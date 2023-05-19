from .core.event_bus import Event
from .git_text import GitTextCommand
from sublime import ok_cancel_dialog


class GitDiffViewDismissChangesCommand(GitTextCommand):
    warning_text = "Warning: this will dismiss all changes to the file \"{}.\""

    def run(self, edit):
        if self.have_a_diff_to_show():
            file = self.get_file()
            message = self._get_message(file)

            if self.should_dismiss_dialog(message):
                if file["is_staged"]:
                    self.command.git_unstage(file["file_name"])

                if file["modification_type"] == '??':
                    self.command.git_clean(file["file_name"])
                else:
                    self.command.git_dismis_changes(file["file_name"])

                self.rerender_git_status_view()
                Event.fire('git_status.update_diff_view', self.current_line)

    def should_dismiss_dialog(self, message):
        return ok_cancel_dialog(message, 'Dismiss')

    def _get_message(self, file):
        return self.warning_text.format(file["file_name"])
