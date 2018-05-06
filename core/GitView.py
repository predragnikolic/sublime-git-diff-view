from .GitStatusView import GitStatusView

class GitView:
    ''' Shows the git status and git diff'''

    def __init__(self, window, layout):
        self.window = window
        self.layout = layout
        self.git_status_view = GitStatusView(self.window)

    def close(self):
        for view in self.window.views():
            if view.name() in [GitStatusView.view_name, "Git Diff View"]:
                self.window.focus_view(view)
                self.window.run_command('close_file')

    def open(self):
        git_status_view = self.git_status_view.generate()
        self.layout.insert_into_first_column(git_status_view)

        view2 = self.window.new_file()
        view2.set_name("Git Diff View")
        view2.settings().set("line_numbers", False)
        view2.set_scratch(True)

        self.layout.insert_into_second_column(view2)
