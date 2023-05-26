from typing import Callable
from .core.diff_view import DIFF_VIEW_NAME
from .core.git_commands import Git
from .core.git_diff_view import GitDiffView
from .core.status_view import get_status_view, STATUS_VIEW_NAME
from .core.view_manager import SESSION_DIR, ViewsManager
from .utils import get_line
import sublime
import sublime_plugin
import os


STOP_INTERVAL = False
def set_interval(fn: Callable) -> None:
    def interval() -> None:
        fn()
        if not STOP_INTERVAL:
            sublime.set_timeout(interval, 2000)
    sublime.set_timeout(interval, 2000)


def refresh_list() -> None:
    ''' Refresh git status view content'''
    window = sublime.active_window()
    view = get_status_view(window.views())
    if view is None:
        return
    git_statuses = Git(window).git_statuses()
    view.run_command('update_status_view', {
        'git_statuses': git_statuses,
    })


def plugin_loaded() -> None:
    # create session dir where the session file will be stored
    if not os.path.exists(SESSION_DIR):
       os.makedirs(SESSION_DIR)
    status_view = get_status_view(sublime.active_window().views())
    # If status view is open when sublime starts,
    if status_view is not None:
        set_interval(refresh_list)


# command: close_git_diff_view
class CloseGitDiffViewCommand(sublime_plugin.TextCommand):
    def run(self, _: sublime.Edit) -> None:
        global STOP_INTERVAL
        window = self.view.window()
        if not window:
            return
        git_diff_view = GitDiffView(window)
        git_diff_view.close()

        git = Git(window)
        views_manager = ViewsManager(window, git.git_root_dir or "")
        views_manager.restore()

        STOP_INTERVAL = True


# command: open_git_diff_view
class OpenGitDiffViewCommand(sublime_plugin.TextCommand):
    def run(self, _: sublime.Edit) -> None:
        global STOP_INTERVAL
        window = self.view.window()
        if not window:
            return
        git = Git(window)
        # open GitView
        # array of dict that holds information about
        # the file, type of modification, and if the file is staged
        git_statuses = git.git_statuses()
        if not git_statuses:
            window.status_message('No git changes to show.')
            return
        views_manager = ViewsManager(window, git.git_root_dir or "")
        views_manager.prepare()

        git_diff_view = GitDiffView(window)
        git_diff_view.open()

        STOP_INTERVAL = False
        set_interval(refresh_list)


# command: toggle_git_diff_view
class ToggleGitDiffViewCommand(sublime_plugin.TextCommand):
    def run(self, _: sublime.Edit) -> None:
        global STOP_INTERVAL
        window = self.view.window()
        if not window:
            return
        if ViewsManager.is_git_view_open(window.views()):
            self.view.run_command('close_git_diff_view')
        else:
            self.view.run_command('open_git_diff_view')


class SelectionChangedEvent(sublime_plugin.EventListener):
    previous_line = None

    def on_pre_close(self, view: sublime.View) -> None:
        window = view.window()
        if not window:
            return
        if not ViewsManager.is_git_view_open(window.views()):
            return
        if view.name() in [STATUS_VIEW_NAME, DIFF_VIEW_NAME]:
            sublime.set_timeout(lambda: window.run_command('close_git_diff_view'))


    def on_selection_modified(self, view: sublime.View) -> None:
        if view.name() != STATUS_VIEW_NAME:
            return
        window = view.window()
        if not window:
            return
        status_view = view
        line = get_line(status_view)
        on_same_line = line == self.previous_line
        if on_same_line or line is None:
            return
        git_statuses = GitDiffView.git_statuses[window.id()]
        try:
            git_status = git_statuses[line]
            view.run_command("update_diff_view", {
                'git_status': git_status,
            })
        except:
            status_view.run_command("clear_diff_view")


