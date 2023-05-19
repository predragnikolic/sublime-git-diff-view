import sublime

from .status_view import STATUS_VIEW_NAME, create_status_view
from .diff_view import create_diff_view, DIFF_VIEW_NAME
from .git_commands import Git
from .event_bus import Event


class GitView:
    ''' Shows the git status and git diff. '''
    listener = None

    def __init__(self, window, layout):
        self.window: sublime.Window = window
        self.layout = layout

    def close(self):
        ''' Closes the git status view and git diff view. '''

        for view in self.window.views():
            if view.name() in [STATUS_VIEW_NAME, DIFF_VIEW_NAME]:
                view.close()
                Event.fire('git_view.close')

    def open(self, git_statuses):
        ''' Opens the git status view, and git diff view. '''

        status_view = create_status_view(self.window, git_statuses)
        self.layout.insert_into_first_column(status_view)

        diff_view = create_diff_view(self.window)
        self.layout.insert_into_second_column(diff_view)

        # call --> UPDATE_DIFF_VIEW <-- after registering
        # the 'git_status.update_diff_view' listener
        # so it nows how to remove it
        self.update_diff_view(diff_view, 0)

        sel = status_view.sel()
        sel.clear()
        sel.add(0)
        status_view.show(0)

    @staticmethod
    def update_diff_view(view, line):
        git = Git(sublime.active_window())
        git_statuses = git.git_statuses()

        if not GitView._have_a_diff_to_show(line, git_statuses):
            view.run_command("clear_git_diff_view")
            return

        file_name = git_statuses[line]['file_name']
        modification_type = git_statuses[line]['modification_type']
        data = {
            'modification_type': modification_type,
            'file_name': file_name
        }

        view.run_command("update_git_diff_view", data)

    @staticmethod
    def _have_a_diff_to_show(line, git_statuses):
        return line < len(git_statuses)
