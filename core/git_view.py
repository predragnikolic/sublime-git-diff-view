import sublime

from .git_status_view import GitStatusView
from .diff_view import create_diff_view, DIFF_VIEW_NAME
from .git_commands import Git
from .event_bus import Event


class GitView:
    ''' Shows the git status and git diff. '''
    listener = None

    def __init__(self, window, layout):
        self.window = window
        self.layout = layout
        self.git_status_view = GitStatusView(window)

    def close(self):
        ''' Closes the git status view and git diff view. '''

        for view in self.window.views():
            if view.name() in [GitStatusView.view_name, DIFF_VIEW_NAME]:
                self.window.focus_view(view)
                self.window.run_command('close_file')
                Event.fire('git_view.close')

    def open(self, git_statuses):
        ''' Opens the git status view, and git diff view. '''

        git_status_view = self.git_status_view.create(git_statuses)
        self.layout.insert_into_first_column(git_status_view)

        git_diff_view = create_diff_view(self.window)
        self.layout.insert_into_second_column(git_diff_view)

        # call --> UPDATE_DIFF_VIEW <-- after registering
        # the 'git_status.update_diff_view' listener
        # so it nows how to remove it
        self.update_diff_view(git_diff_view, 0)

        sel = git_status_view.sel()
        sel.clear()
        sel.add(0)
        git_status_view.show(0)

    @staticmethod
    def update_diff_view(view, line):
        git = Git(sublime.active_window())
        git_statuses = git.git_statuses()

        if not GitView._have_a_diff_to_show(line, git_statuses):
            view.run_command("clear_git_diff_view")
            return

        file_name = git_statuses[line]['file_name']
        modification_type = git_statuses[line]['modification_type']
        diff_output = ''

        if 'MM' == modification_type:
            diff_output = (
                "Staged\n" +
                "======\n" +
                git.diff_file_staged(file_name) +
                "Unstaged\n" +
                "========\n" +
                git.diff_file_unstaged(file_name)
            )

        elif 'M' in modification_type:
            diff_output = git.diff_file(file_name)

        elif 'U' in modification_type:
            diff_output = git.diff_file(file_name)

        elif 'A' in modification_type:
            diff_output = git.diff_file(file_name)

        elif 'R' in modification_type:
            diff_output = git.diff_file(file_name)

        elif 'C' in modification_type:
            diff_output = git.diff_file(file_name)

        elif '?' in modification_type:
            diff_output = git.show_added_file(file_name)

        elif 'D' in modification_type:
            diff_output = git.show_deleted_file(file_name)

        data = {
            'diff_output': diff_output,
            'modification_type': modification_type,
            'file_name': file_name
        }

        view.run_command("update_git_diff_view", data)

    @staticmethod
    def _have_a_diff_to_show(line, git_statuses):
        return line < len(git_statuses)
