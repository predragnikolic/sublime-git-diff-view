from typing import List
import sublime


def get_diff_view(views: List[sublime.View]):
    ''' Return the git diff View '''
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
