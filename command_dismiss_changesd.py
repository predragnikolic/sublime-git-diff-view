from .core.git_commands import Git
from .core.git_diff_view import GitDiffView
from .utils import get_line
import sublime
import sublime_plugin


# command: git_diff_view_dismiss_changes
class GitDiffViewDismissChangesCommand(sublime_plugin.TextCommand):
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

        def done(option):
            if option == -1:
                return
            # 0 -> Discard changes
            if git_status["is_staged"]:
                git.reset_head(git_status["file_name"])
            if git_status["modification_type"] == '??':
                git.clean(git_status["file_name"])
            else:
                git.checkout(git_status["file_name"])
            git_statuses = git.git_statuses()
            self.view.run_command('update_status_view', {
                'git_statuses': git_statuses,
            })
            self.view.run_command("update_diff_view", {
                'git_status': git_status,
            })

        self.view.show_popup_menu([
            'Confirm Discard'
        ], done)
