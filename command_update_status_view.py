from typing import List
from .utils import format_git_statuses
from .core.git_commands import GitStatus
from .core.status_view import get_status_view
import sublime_plugin
import sublime


# command: update_status_view
class UpdateStatusViewCommand(sublime_plugin.TextCommand):
    def run(self, edit, git_statuses: List[GitStatus]):
        window = self.view.window()
        if not window:
            return
        active_view = window.active_view()
        status_view = get_status_view(window.views())
        if status_view is None:
            return
        formatted_git_statuses = format_git_statuses(git_statuses)
        new_content = formatted_git_statuses
        # update diff view if necessary
        if len(git_statuses) < 1:
            new_content = "No changes"
        # update status view
        status_view.set_read_only(False)
        status_view.replace(edit, sublime.Region(0, status_view.size()), new_content)
        status_view.set_read_only(True)
        window.focus_view(active_view)
