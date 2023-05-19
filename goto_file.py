from os import path
import sublime_plugin
import sublime

from .utils import get_line
from .core.git_commands import Git


class GitDiffViewGotoFileCommand(sublime_plugin.TextCommand):
    def run(self, _):
        window = self.view.window()
        if not window:
            return
        line = get_line(self.view)
        if line is None:
            return
        git = Git(window)
        git_statuses = git.git_statuses() or []
        git_status = git_statuses[line]
        if not git_status:
            return
        if 'D' in git_status["modification_type"]:
            window.status_message("GitDiffVIew: Can't go to a deleted file")
            return
        file_name = git_status["file_name"]
        if not git.git_root_dir or not file_name:
            return
        absolute_path_to_file = path.join(git.git_root_dir,
                                          git_status["file_name"])
        window.run_command('toggle_git_diff_view')

        view = window.open_file(absolute_path_to_file)
        sublime.set_timeout(lambda: window.focus_view(view))
