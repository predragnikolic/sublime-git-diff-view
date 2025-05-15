import sublime
from .core.git_commands import Git
from .core.git_diff_view import GitDiffView
from .utils import get_selected_lines, get_line
import sublime_plugin
from .command_update_diff_view import update_diff_view

# command: git_diff_view_stage_unstage
class GitDiffViewStageUnstageCommand(sublime_plugin.TextCommand):
    def run(self, _: sublime.Edit) -> None:
        window = self.view.window()
        if not window:
            return
        selected_lines = get_selected_lines(self.view)
        line = get_line(self.view)
        if line is None:
            return
        git = Git(window)
        git_statuses = GitDiffView.git_statuses[window.id()]
        git_status = git_statuses[line]
        if not git_status:
            return

        file_names = [git_statuses[line]['file_name'] for line in selected_lines]
        if git_status["is_staged"]:
            git.unstage_files(file_names)
        else:
            git.stage_files(file_names)
        git_statuses = git.git_statuses()
        self.view.run_command('update_status_view', {
            'git_statuses': git_statuses,
        })
        update_diff_view(self.view, git_status)
