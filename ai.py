from __future__ import annotations
from typing import Iterator, Literal
import sublime_plugin 
import sublime
import json
import threading

from .utils import get_point
from .core.git_commands import Git
import requests

# Event to signal stopping the stream
stop_event = threading.Event()

class Ollama:
    url= "http://localhost:11434"
    model="qwen2.5-coder"
    is_installed= False


class IsOllamaInstalled(sublime_plugin.EventListener):
    def on_init(self, views):
        v = sublime.active_window().active_view()
        if not v:
            return
        ollama_settings: dict = v.settings().get("git_diff_view.ollama", {})
        Ollama.url = ollama_settings.get('url', "http://localhost:11434")
        Ollama.model = ollama_settings.get('model', '')
        res = requests.get(Ollama.url)
        if res.status_code != 200:
            print(f'GitDiffView: Ollama is not running on {Ollama.url}.')
            return
        print(f'GitDiffView: Ollama is running on {Ollama.url}.')
        # list models available locally
        res = requests.get(f"{Ollama.url}/api/tags")

        def strip_after_colon(input_string: str):
            """
             ['deepseek-r1:7b', 'qwen2.5-coder:latest', 'phi3.5:3.8b-mini-instruct-q8_0']
             ->
            ['deepseek-r1', 'qwen2.5-coder', 'phi3.5']
            """
            colon_index = input_string.find(':')
            if colon_index != -1:
                return input_string[:colon_index]
            else:
                return input_string

        available_models = [strip_after_colon(model['name']) for model in res.json()['models']]
        if Ollama.model not in available_models:
            print(f'GitDiffView: Model "{Ollama.model}" not found.\n\tUse one of the available models: {available_models}\n\tand set it in Preferences.sublime-settings: `"git_diff_view.ollama": {{ "model": "MODEL" }}`')
            return
        print(f'GitDiffView: Using model "{Ollama.model}."')
        Ollama.is_installed = True


LAST_GENERATED_TEXT = ''

class GitDiffViewGenerateMessageCancelCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        global stop_event, LAST_GENERATED_TEXT
        # If a previous request is running, stop it
        if not stop_event.is_set():
            stop_event.set()
            text_region = self.view.find(LAST_GENERATED_TEXT, 0)
            if text_region:
                self.view.replace(edit, text_region, '')


class GitDiffViewGenerateMessageCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        global stop_event, LAST_GENERATED_TEXT
        w = self.view.window()
        if not w:
            return
        git = Git(w)
        staged_diff = git.diff_staged() or git.diff_all_changes()
        user_prompt = self.view.settings().get("git_diff_view.commit_message_prompt") or "Generate a short, concise and correct git commit message."
        prompt = f"""{user_prompt}
The git diff is:
{staged_diff}
"""
        # If a previous request is running, stop it
        if not stop_event.is_set():
            stop_event.set()
        text_region = self.view.find(LAST_GENERATED_TEXT, 0)
        if text_region:
            self.view.replace(edit, text_region, '')
        stop_event=threading.Event()
        t = threading.Thread(target=stream_response, args=(self.view, prompt, stop_event))
        t.start()


def stream_response(view:sublime.View, prompt: str, stop_event: threading.Event):
    global LAST_GENERATED_TEXT
    payload = {
        "model": Ollama.model,
        "prompt": prompt,
        "stream": True,
    }
    try:
        LAST_GENERATED_TEXT = ''
        last_point = 0
        for text_chunk in stream('post', f"{Ollama.url}/api/generate", payload, stop_event):
            LAST_GENERATED_TEXT+=text_chunk
            view.run_command("git_diff_view_insert_text", {
                'characters': text_chunk,
                'last_point': last_point,
            })
            last_point += len(text_chunk)

    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Ollama API: {e}")
        return

class GitDiffViewInsertTextCommand(sublime_plugin.TextCommand):
    def run(self, edit, characters: str, last_point: int):
        self.view.insert(edit, last_point, characters)

def stream(method: Literal['get', 'post'], url: str, data: dict, stop_event: threading.Event | None=None) -> Iterator[str]:
    headers = {"Content-Type": "application/json"}
    with requests.request(method, url, json=data, headers=headers, stream=True, timeout=10) as response:
        response.raise_for_status()
        for chunk in response.iter_lines():
            if stop_event and stop_event.is_set():
                break
            if chunk:
                try:
                    chunk_text = chunk.decode("utf-8")
                    chunk_json = json.loads(chunk_text)
                    text = chunk_json.get("response", "")  # Extract the text
                    yield text
                except json.JSONDecodeError:
                    print("Failed to decode JSON chunk:", chunk)
                    break
