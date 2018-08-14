import sublime

from .GitStatusView import GitStatusView
from .GitDiffView import GitDiffView
from .Command import Command
from .Event import Event


class GitView:
    ''' Shows the git status and git diff. '''
    listener = None

    def __init__(self, window, layout):
        self.window = window
        self.layout = layout
        self.git_status_view = GitStatusView(window)
        self.git_diff_view = GitDiffView(window)
        self.command = Command(window)

    def close(self):
        ''' Closes the git status view and git diff view. '''

        for view in self.window.views():
            if view.name() in [GitStatusView.view_name, GitDiffView.view_name]:
                self.window.focus_view(view)
                self.window.run_command('close_file')
                Event.fire('git_view.close')

    def open(self, git_statuses):
        ''' Opens the git status view, and git diff view. '''

        git_status_view = self.git_status_view.generate(git_statuses)
        self.layout.insert_into_first_column(git_status_view)

        git_diff_view = self.git_diff_view.generate()
        self.layout.insert_into_second_column(git_diff_view)

        # call --> UPDATE_DIFF_VIEW <-- after registering
        # the 'git_status.update_diff_view' listener
        # so it nows how to remove it
        self.update_diff_view(git_diff_view, 0)

        sel = git_status_view.sel()
        sel.clear()
        sel.add(sublime.Region(0, 0))

    @staticmethod
    def update_diff_view(view, line):
        command = Command(sublime.active_window())
        git_statuses = command.git_statuses()

        if not GitView._have_a_diff_to_show(line, git_statuses):
            return

        file_name = git_statuses[line]['file_name']
        modification_type = git_statuses[line]['modification_type']
        diff_output = ''

        if 'M' in modification_type:
            diff_output = command.git_diff_file(file_name)

        elif 'U' in modification_type:
            diff_output = command.git_diff_file(file_name)

        elif 'A' in modification_type:
            diff_output = command.git_diff_file(file_name)

        elif 'R' in modification_type:
            diff_output = command.git_diff_file(file_name)

        elif 'C' in modification_type:
            diff_output = command.git_diff_file(file_name)

        elif '?' in modification_type:
            diff_output = command.show_added_file(file_name)

        elif 'D' in modification_type:
            diff_output = command.show_deleted_file(file_name)

        data = {
            'diff_output': diff_output,
            'modification_type': modification_type
        }

        view.run_command("update_git_diff_view", data)

    @staticmethod
    def _have_a_diff_to_show(line, git_statuses):
        return line < len(git_statuses)
    def _have_a_diff_to_show(line, git_statuses):
        return line < len(git_statuses)
