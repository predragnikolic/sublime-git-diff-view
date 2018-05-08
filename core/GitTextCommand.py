import sublime_plugin
import sublime

from .GitStatusView import GitStatusView
from .Command import Command


class GitTextCommand(sublime_plugin.TextCommand):
    def have_a_diff_to_show(self):
        self._setup()
        return self.current_line < len(self.git_statuses)

    def get_file(self):
        return self.git_statuses[self.current_line]

    def rerender_git_status_view(self):
        git_statuses = self.command.git_status_dict()
        git_status_view = GitStatusView(self.window)
        git_status_view.update(self.view, git_statuses, self._get_cursor_pos())

    def _setup(self):
        self.window = sublime.active_window()
        self.command = Command(self.window)
        self.current_line = self._get_line(self._get_cursor_pos())
        self.git_statuses = self.command.git_status_dict()

    def _get_cursor_pos(self):
        return self.view.sel()[0].begin()

    def _get_line(self, point):
        return self.view.rowcol(point)[0]