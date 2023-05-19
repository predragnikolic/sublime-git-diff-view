import sublime_plugin
from .utils import get_line
from .core.git_commands import Git


class GitDiffViewStageUnstageCommand(sublime_plugin.TextCommand):
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
        if git_status["is_staged"]:
            git.reset_head(git_status["file_name"])
        else:
            git.add(git_status["file_name"])
        self.view.run_command('update_status_view', {
            'git_statuses': git_statuses,
        })
        self.view.run_command("update_diff_view", {
            'git_status': git_status,
        })
