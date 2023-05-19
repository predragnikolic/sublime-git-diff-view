from .core.event_bus import Event
from .git_text import GitTextCommand


class GitDiffViewStageUnstageCommand(GitTextCommand):
    def run(self, edit):
        if self.have_a_diff_to_show():
            file = self.get_file()
            if file["is_staged"]:
                self.command.git_unstage(file["file_name"])
            else:
                self.command.git_stage(file["file_name"])
            self.rerender_git_status_view()
            Event.fire('git_status.update_diff_view', self.current_line)
