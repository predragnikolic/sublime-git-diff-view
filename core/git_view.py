from typing import Dict, List
from .git_commands import GitStatus
import sublime

from .status_view import STATUS_VIEW_NAME, create_status_view
from .diff_view import create_diff_view, DIFF_VIEW_NAME

WindowId = int

class GitView:
    ''' Shows the git status and git diff. '''
    listener = None
    git_statuses: Dict[WindowId, List[GitStatus]] = {}

    def __init__(self, window, layout):
        self.window: sublime.Window = window
        self.layout = layout

    def close(self):
        ''' Closes the git status view and git diff view. '''
        for view in self.window.views():
            if view.name() in [STATUS_VIEW_NAME, DIFF_VIEW_NAME]:
                view.close()

    def open(self):
        ''' Opens the git status view, and git diff view. '''
        git_statuses = GitView.git_statuses[self.window.id()]
        status_view = create_status_view(self.window, git_statuses)
        self.layout.insert_into_first_column(status_view)
        diff_view = create_diff_view(self.window)
        self.layout.insert_into_second_column(diff_view)
        # select first line, Status View
        sel = status_view.sel()
        sel.clear()
        sel.add(0)
        status_view.show(0)
        # display first line , Git View
        git_status = git_statuses[0]
        if not git_status:
            return
        diff_view.run_command("update_diff_view", {
            'git_status': git_status,
        })
