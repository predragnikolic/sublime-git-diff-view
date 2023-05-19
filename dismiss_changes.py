from .core.event_bus import Event
from .git_text import GitTextCommand
import sublime


class GitDiffViewDismissChangesCommand(GitTextCommand):
    def run(self, _):
        if not self.have_a_diff_to_show():
            return
        file = self.get_file()
        message = f'Warning: Dismiss all changes to the file "{file["file_name"]}?"'
        if not sublime.ok_cancel_dialog(message, 'Dismiss'):
            return
        if file["is_staged"]:
            self.git.reset_head(file["file_name"])
        if file["modification_type"] == '??':
            self.git.clean(file["file_name"])
        else:
            self.git.checkout(file["file_name"])
        self.rerender_git_status_view()
        Event.fire('git_status.update_diff_view', self.current_line)
