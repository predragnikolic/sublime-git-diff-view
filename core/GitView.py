from .GitStatusView import GitStatusView
from .GitDiffView import GitDiffView
from .Command import Command
from .Event import Event
import sublime


class GitView:
    ''' Shows the git status and git diff'''
    listener = None
    instance = None

    @staticmethod
    def singleton(window, layout):
        if GitView.instance is None:
            GitView.instance = GitView(window, layout)
        return GitView.instance

    def __init__(self, window, layout):
        self.window = window
        self.layout = layout
        self.git_status_view = GitStatusView(window)
        self.git_diff_view = GitDiffView(window)
        self.command = Command.singleton(window)

    def close(self):
        for view in self.window.views():
            if view.name() in [GitStatusView.view_name, GitDiffView.view_name]:
                self.window.focus_view(view)
                self.window.run_command('close_file')
                Event.fire('git_view.close')

    def open(self, git_statuses):
        git_status_view = self.git_status_view.generate(git_statuses)
        self.layout.insert_into_first_column(git_status_view)

        git_diff_view = self.git_diff_view.generate()
        self.layout.insert_into_second_column(git_diff_view)

        self.listener = Event.listen(
            'git_status.update_diff_view',
            lambda line: self.update_diff_view(git_diff_view, line))

        # call --> UPDATE_DIFF_VIEW <-- after registering
        # the 'git_status.update_diff_view' listener
        # so it nows how to remove it
        self.update_diff_view(git_diff_view, 0)

        sel = git_status_view.sel()
        sel.clear()
        sel.add(sublime.Region(0, 0))

    def update_diff_view(self, view, line):
        git_statuses = self.command.git_status_dict()
        if not self._have_a_diff_to_show(line, git_statuses):
            return

        file_name = git_statuses[line]['file_name']
        modification_type = git_statuses[line]['modification_type']
        diff_output = ''

        if 'M' or 'A' in modification_type:
            # view.set_syntax_file('Packages/Diff/Diff.sublime-syntax')
            diff_output = self.command.git_diff_file(file_name)

        elif '?' in modification_type:
            diff_output = self.command.show_added_file(file_name)

        elif 'D' in modification_type:
            diff_output = self.command.show_deleted_file(file_name)

        data = {
            'line': line,
            'diff_output': diff_output,
            'modification_type': modification_type
        }

        Event.listen('git_view.close', self.remove_listener)
        view.run_command("update_diff_view", data)

    def remove_listener(self):
        if self.listener is not None:
            self.listener()
            self.listener = None

    def _have_a_diff_to_show(self, line, git_statuses):
        return line < len(git_statuses)
