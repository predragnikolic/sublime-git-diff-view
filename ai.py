from __future__ import annotations
from typing import Iterator, Literal
import sublime_plugin 
import sublime
import json
import threading
from .core.git_commands import Git
import requests

# Event to signal stopping the stream
stop_event = threading.Event()

class Ollama:
    base_url= "http://localhost:11434"
    model="qwen2.5-coder"
    is_installed= False


class IsOllamaInstalled(sublime_plugin.EventListener):
    def on_init(self, views):
        def is_ollama_installed():
            res = requests.get(Ollama.base_url)
            Ollama.is_installed = res.status_code == 200
            print('Ollama.is_installed', Ollama.is_installed)
        t = threading.Thread(target=is_ollama_installed)
        t.start()


class GitDiffViewGenerateMessageCancelCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        global stop_event
        # If a previous request is running, stop it
        if not stop_event.is_set():
            stop_event.set()


last_generated_text = ''
class GitDiffViewGenerateMessageCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        global stop_event, last_generated_text
        w = self.view.window()
        if not w:
            return
        git = Git(w)
        staged_diff = git.diff_staged() or git.diff_all_changes()
        final_prompt = f"Generate short concise correct git commit message.\nThe diff is\n```{staged_diff}\n```\nHere is the commit message text:\n"
        # If a previous request is running, stop it
        if not stop_event.is_set():
            stop_event.set()
        text_region = self.view.find(last_generated_text, 0)
        if text_region:
            self.view.replace(edit, text_region, '')
        stop_event=threading.Event()
        t = threading.Thread(target=stream_response, args=(self.view, final_prompt, stop_event))
        t.start()


def stream_response(view:sublime.View, prompt: str, stop_event: threading.Event):
    global last_generated_text
    payload = {
        "model": Ollama.model,
        "prompt": prompt,
        "stream": True,
    }
    try:
        last_generated_text = ''
        for text_chunk in stream('post', f"{Ollama.base_url}/api/generate", payload, stop_event):
            last_generated_text+=text_chunk
            view.run_command("insert", {
                'characters': text_chunk,
                'force': False,
                'scroll_to_end': True
            })
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Ollama API: {e}")
        return


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
