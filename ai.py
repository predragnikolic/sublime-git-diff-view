from __future__ import annotations
import sublime_plugin 
import sublime
import http.client
import json
import threading
from .core.git_commands import Git
import requests

# Ollama server endpoint details
OLLAMA_HOST = "localhost"
OLLAMA_PORT = 11434
OLLAMA_PATH = "/api/generate"
OLLAMA_MODEL = "qwen2.5-coder"

# Event to signal stopping the stream
stop_event = threading.Event()


class GitDiffViewGenerateMessageCancelCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        global stop_event
        # If a previous request is running, stop it
        if not stop_event.is_set():
            stop_event.set()




class GitDiffViewGenerateMessageCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        global stop_event
        w = self.view.window()
        if not w:
            return
        git = Git(w)
        staged_diff = git.diff_staged() or git.diff_all_changes()
        final_prompt = f"You are a pro at generating short concise correct git commit messages subjects text.\nHere is the diff\n```{staged_diff}\n```\nHere is the commit message text:\n"
        # If a previous request is running, stop it
        if not stop_event.is_set():
            stop_event.set()
        self.view.replace(edit, sublime.Region(0, self.view.size()), '')
        stop_event=threading.Event()
        t = threading.Thread(target=stream_response, args=(self.view,final_prompt, stop_event))
        t.start()


def stream_response(view: sublime.View, prompt: str, stop_event: threading.Event):
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": True,
    }

    try:
        with requests.post(OLLAMA_PATH, json=payload, headers=headers, stream=True) as response:
            response.raise_for_status()  # Raise an exception for bad status codes

            text_result = ""
            for chunk in response.iter_lines():
                if stop_event.is_set():
                    break

                if chunk:
                    try:
                        chunk_text = chunk.decode("utf-8")
                        chunk_json = json.loads(chunk_text)
                        text_chunk = chunk_json.get("response", "")
                        text_result += text_chunk

                        # Use Sublime Text API on the main thread.
                        def append_to_view():
                            view.run_command("append", {
                                'characters': text_chunk,
                                'force': False,
                                'scroll_to_end': True
                            })

                        sublime.set_timeout_async(append_to_view, 0)


                    except json.JSONDecodeError:
                        print("Failed to decode JSON chunk:", chunk)
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Ollama API: {e}")
        return

def get_point(view: sublime.View):
    sel = view.sel()
    region = sel[0] if sel else None
    if region is None:
        return
    return region.b


def fetch(method: str, path: str, headers: dict[str, str], payload: dict | None = None, ) -> http.client.HTTPResponse:
    connection = http.client.HTTPConnection(host, port)
    try:
        if payload:
            connection.request(method, path, body=payload, headers=headers)
        else:
            connection.request(method, path, headers=headers)
        return connection.getresponse()
    except Exception as e:
        print(f"Error during HTTP request: {e}")
        connection.close()  # Ensure connection is closed on error.
        return None  # Explicitly return None on error
