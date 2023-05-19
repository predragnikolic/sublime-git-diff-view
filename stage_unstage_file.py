from sublime import windows
from sublime_plugin import sublime
from .core.git_commands import Git
from .core.event_bus import Event
from .git_text import GitTextCommand


class GitDiffViewStageUnstageCommand(GitTextCommand):
    def run(self, _):
        window = self.view.window()
        if not window:
            return
        line = get_line(self.view)
        if line is None:
            return
        git_statuses = Git(self.view.window()).git_statuses()
        if not git_statuses:
            return
        git_status = git_statuses[line]
        if not git_status:
            return
        git = Git(window)
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


def get_line(view: sublime.View):
    point = get_point(view)
    if point is None:
        return
    return view.rowcol(point)[0]

def get_point(view: sublime.View):
    sel = view.sel()
    if not sel:
        return
    return sel[0].b