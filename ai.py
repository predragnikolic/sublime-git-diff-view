import sublime_plugin 
import sublime
import http.client
import json
import threading
import re
from pathlib import Path
import os
from .core.git_commands import Git

# Ollama server endpoint details
OLLAMA_HOST = "localhost"
OLLAMA_PORT = 11434
OLLAMA_PATH = "/api/generate"
OLLAMA_MODEL = "qwen2.5-coder"

# Event to signal stopping the stream
stop_event = threading.Event()

prompt = """
You are a pro at generating git commit messages.
The commit message correctly explains the diff. 
Use as from 3 to 10 words to describe the diff.
The  message should be short, concise, human readable, and correctly describe the diff. 
Don't generate text that is not true.
Put no quotes around.
If you see a mistake, write a short text to explain the error and stop.
"""


class GitDiffViewGenerateMessageCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        global stop_event, prompt
        w = self.view.window()
        if not w:
            return
        git = Git(w)
        staged_diff = git.diff_staged() or git.diff_all_changes()
        final_prompt = prompt + f"Here is the diff\n```{staged_diff}\n```\nHere is the commit message text:\n"
        print('final_prompt', final_prompt)
        # If a previous request is running, stop it
        if stop_event.is_set() == False:
            stop_event.set()
        self.view.replace(edit, sublime.Region(0, self.view.size()), '')
        stop_event=threading.Event()
        t = threading.Thread(target=stream_response, args=(self.view,final_prompt, stop_event))
        t.start()


def stream_response(view: sublime.View, prompt: str, stop_event: threading.Event):
    connection = http.client.HTTPConnection(OLLAMA_HOST, OLLAMA_PORT)
    headers = {
        "Content-Type": "application/json",
    }

    # Request payload as JSON string
    payload = json.dumps({
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        # "options": {
        #     "stop": [],
        # },
        "stream": True,
        # "raw": True,
    })

    # Send POST request
    print('OLLAMA_PATH', OLLAMA_PATH)
    print('payload', payload)
    connection.request("POST", OLLAMA_PATH, body=payload, headers=headers)

    # Get response and ensure status is OK
    response = connection.getresponse()
    if response.status != 200:
        print("Failed to connect to Ollama API:", response.status)
        print(response)
        return

    # Read and decode the response in chunks
    text_result = ""
    while not stop_event.is_set():
        # Read a chunk of data
        chunk = response.readline()
        
        # Break if no more data
        if not chunk:
            break

        # Decode and parse JSON response if chunk is not empty
        chunk_text = chunk.decode("utf-8").strip()
        if chunk_text:
            try:
                chunk_json = json.loads(chunk_text)
                text_chunk = chunk_json.get("response", "")
                text_result += text_chunk
                view.run_command("append", {
                    'characters': text_chunk,
                    'force': False,
                    'scroll_to_end': True
                })
            except json.JSONDecodeError:
                print("Failed to decode JSON chunk:", chunk_text)

    # Close the connection
    connection.close()

def get_point(view: sublime.View):
    sel = view.sel()
    region = sel[0] if sel else None
    if region is None:
        return
    return region.b


