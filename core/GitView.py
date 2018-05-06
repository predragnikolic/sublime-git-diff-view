from .GitStatusView import GitStatusView
from .Command import Command
class GitView:
    ''' Shows the git status and git diff'''

    def __init__(self, window, layout, edit):
        self.window = window
        self.layout = layout
        self.git_status_view = GitStatusView(self.window)
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
        print('ovo je novo')
        print(git_statuses)
        git_status_view = self.git_status_view.generate(git_statuses)
        self.layout.insert_into_first_column(git_status_view)

        diff_output = ''
        if len(git_statuses) > 0:
            if 'D' not in git_statuses[0]['modification_type']:
                diff_output = self.command.git_diff_file(git_statuses[0]['file_name'])
            else: 
                print('ipak je d')
        view2 = self.window.new_file()
        view2.set_name("Git Diff View")
        view2.settings().set("line_numbers", False)
        view2.set_scratch(True)
        print('diff output')
        print(diff_output)
        view2.insert(self.edit, 0, diff_output)
        # view2.run_command("insert", {"characters": diff_output})
        view2.set_syntax_file('Packages/Diff/Diff.sublime-syntax')
        self.layout.insert_into_second_column(view2)
