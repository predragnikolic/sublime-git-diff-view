from .GitStatusView import GitStatusView
from .GitDiffView import GitDiffView
from .Command import Command
from .Event import Event
import sublime


class GitView:
    ''' Shows the git status and git diff'''

    def __init__(self, window, layout, edit):
        self.window = window
        self.layout = layout
        self.git_status_view = GitStatusView(window)
        self.git_diff_view = GitDiffView(window)
        self.command = Command(window)
        self.edit = edit

    def close(self):
        for view in self.window.views():
            if view.name() in [GitStatusView.view_name, "Git Diff View"]:
                self.window.focus_view(view)
                self.window.run_command('close_file')

    def open(self):
        # array of dict that holds information about
        # the file, type of modification, and if the file is staged
        git_statuses = self.command.git_status_dict()
        # git status view
        git_status_view = self.git_status_view.generate(git_statuses)
        self.layout.insert_into_first_column(git_status_view)

        git_diff_view = self.git_diff_view.generate()
        self.layout.insert_into_second_column(git_diff_view)
        self.update_diff_view(git_diff_view, 0)

        Event.listen('git_status.update_diff_view', lambda line:
                     self.update_diff_view(git_diff_view, line))

        sel = git_status_view.sel()
        sel.clear()
        sel.add(sublime.Region(0, 0))


    def update_diff_view(self, view, line):
        git_statuses = self.command.git_status_dict()
        file_name = git_statuses[line]['file_name']
        diff_output = ''

        if 'D' not in git_statuses[line]['modification_type']:
            diff_output = self.command.git_diff_file(file_name)

        if self._have_a_diff_to_show(line, git_statuses):
            view.run_command("update_diff_view", {"line": line, 'diff_output': diff_output})

    def _have_a_diff_to_show(self, line, git_statuses):
        return line <= len(git_statuses)

        