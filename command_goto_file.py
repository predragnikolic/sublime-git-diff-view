from .core.git_commands import Git
from .core.git_diff_view import GitDiffView
from .utils import get_line
from os import path
import sublime
import sublime_plugin


# command: git_diff_view_goto_file
class GitDiffViewGotoFileCommand(sublime_plugin.TextCommand):
    def run(self, _: sublime.Edit) -> None:
        window = self.view.window()
        if not window:
            return
        line = get_line(self.view)
        if line is None:
            return
        git = Git(window)
        git_statuses = GitDiffView.git_statuses[window.id()]
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

        def deffer_focus_view() -> None:
            if window:
                window.focus_view(view)

        sublime.set_timeout(deffer_focus_view)
