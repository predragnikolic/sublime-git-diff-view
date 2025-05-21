from ..command_update_diff_view import update_diff_view
from .view_manager import ViewsManager
from .layout import insert_into_first_column, insert_into_second_column, two_columns
from .diff_view import create_diff_view, DIFF_VIEW_NAME
from .git_commands import GitStatus
from .status_view import STATUS_VIEW_NAME, create_status_view
from typing import Dict, List
import sublime


WindowId = int


class GitDiffView:
    ''' Shows the git status and git diff. '''
    git_statuses: Dict[WindowId, List[GitStatus]] = {}
    ''' stores the last result of the `git.git_statuses()` call for fast reads'''

    def __init__(self, window: sublime.Window) -> None:
        self.window: sublime.Window = window

    def close(self) -> None:
        ''' Closes the git status view and git diff view. '''
        for view in self.window.views():
            if view.name() in [STATUS_VIEW_NAME, DIFF_VIEW_NAME]:
                view.close()

    def open(self) -> None:
        ''' Opens the git status view, and git diff view. '''
        git_statuses = GitDiffView.git_statuses[self.window.id()]
        status_view = create_status_view(self.window)
        status_view.run_command('update_status_view', {
            'git_statuses': git_statuses,
        })
        two_columns(self.window)
        insert_into_first_column(self.window, status_view)
        diff_view = create_diff_view(self.window)
        insert_into_second_column(self.window, diff_view)
        # select first line, Status View
        cursor_position = ViewsManager.status_view_last_position.get(self.window.id(), 0)
        sel = status_view.sel()
        sel.clear()
        sel.add(cursor_position)
        status_view.show(cursor_position)
        line_index, _ = status_view.rowcol(cursor_position)
        # display first line , Git View
        git_status = git_statuses[line_index]
        if not git_status:
            return
        update_diff_view(diff_view, git_status)
        self.window.focus_view(status_view)
