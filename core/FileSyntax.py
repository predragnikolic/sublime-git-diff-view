import sublime
import os, tempfile

class FileSyntax:
    def __init__(self, window):
        self.window = window

    def get(self, file_name):
        active_buffer = self.window.active_view()

        tmp_buffer = self.window.open_file(file_name, sublime.TRANSIENT)

        # Even if is_loading() is true the view's settings can be
        # retrieved; settings assigned before open_file() returns.
        syntax = tmp_buffer.settings().get("syntax", None)

        self.window.run_command("close")
        if active_buffer:
            self.window.focus_view(active_buffer)

        return syntax
