import sublime


def get_git_diff_view():
    ''' Return the git diff View '''
    window = sublime.active_window()
    views = window.views()
    for view in views:
        if view.name() == 'Git Diff View':
            return view
    return None


class GitDiffView:
    view_name = "Git Diff View"

    def __init__(self, window):
        self.window = window

    def generate(self):
        view = self.window.new_file()
        view.set_name(GitDiffView.view_name)
        view.settings().set("line_numbers", False)
        view.set_scratch(True)
        return view
