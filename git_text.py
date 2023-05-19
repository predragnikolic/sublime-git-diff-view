from typing import List
import sublime_plugin
import sublime

from .core.git_commands import Git, GitStatus
from .core.event_bus import Event


class GitTextCommand(sublime_plugin.TextCommand):
    ''' Acts as an abstract class. All git commands
    that can be triggered from the gits status view can extend it. '''

    def have_a_diff_to_show(self):
        self._setup()
        return self.current_line < len(self.git_statuses)

    def get_file(self):
        return self.git_statuses[self.current_line]

    def _setup(self):
        self.window = sublime.active_window()
        self.git = Git(self.window)
        self.current_line = self._get_line(self._get_cursor_pos())
        self.git_statuses = self.git.git_statuses()

    def _get_cursor_pos(self):
        return self.view.sel()[0].begin()

    def _get_line(self, point):
        return self.view.rowcol(point)[0]
