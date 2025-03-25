from __future__ import annotations
from typing import Callable


from .command_update_diff_view import update_diff_view
from .core.diff_view import DIFF_VIEW_NAME
from .core.git_commands import Git
from .core.git_diff_view import GitDiffView
from .core.status_view import get_status_view, STATUS_VIEW_NAME
from .core.commit_view import COMMIT_VIEW_NAME
from .core.view_manager import SESSION_DIR, ViewsManager
from .utils import get_line, get_point
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
        Git.reset_command_cache()
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
    def on_pre_close(self, view: sublime.View) -> None:
        window = view.window()
        if not window:
            return
        if not ViewsManager.is_git_view_open(window.views()):
            return
        if view.name() in [STATUS_VIEW_NAME, DIFF_VIEW_NAME, COMMIT_VIEW_NAME]:
            point = get_point(view)
            if view.name() == STATUS_VIEW_NAME and point:
                ViewsManager.status_view_last_position[window.id()] = point

            def deffer_close_diff_view() -> None:
                if window:
                    window.run_command('close_git_diff_view')

            sublime.set_timeout(deffer_close_diff_view)

    def on_selection_modified(self, view: sublime.View) -> None:
        if view.name() != STATUS_VIEW_NAME:
            return
        window = view.window()
        if not window:
            return
        status_view = view
        line = get_line(status_view)
        if line is None:
            return
        _, y =status_view.viewport_position()
        status_view.set_viewport_position((0, y)) # make sure that the labels are always visible
        git_statuses = GitDiffView.git_statuses[window.id()]
        try:
            git_status = git_statuses[line]
            update_diff_view(view, git_status)
        except Exception:
            update_diff_view(view, None)


class CommitViewListener(sublime_plugin.ViewEventListener):
    def on_query_completions(self, prefix: str, locations: list[int]):
        w = self.view.window()
        if self.view.name() != COMMIT_VIEW_NAME or not w:
            return None
        cl = sublime.CompletionList()
        cl.set_completions([
            sublime.CompletionItem.command_completion("Generate Message", "git_diff_view_generate_message", {}, kind=(sublime.KindId.SNIPPET, "AI", ""))
        ], flags=sublime.AutoCompleteFlags.INHIBIT_WORD_COMPLETIONS)
        return cl


class GitDiffViewOpenCommitModal(sublime_plugin.TextCommand):
    def run(self, edit: sublime.Edit):
        items = ['Commit', 'Commit - Amend']
        def on_done(i):
            if i < 0:
                return
            window = self.view.window()
            if not window:
                return
            git = Git(window)
            selected = items[i]
            commit_message = self.view.substr(sublime.Region(0, self.view.size()))
            if selected == 'Commit':
                error_message = ''
                if not commit_message.strip():
                    error_message = 'Message Required'
                git_statuses = GitDiffView.git_statuses[window.id()]
                if not git_statuses:
                    error_message = 'Nothing to commit'
                if error_message:
                    self.view.show_popup(f'<p>{error_message}</p>', flags=sublime.PopupFlags.HIDE_ON_MOUSE_MOVE_AWAY | sublime.PopupFlags.HIDE_ON_CHARACTER_EVENT)
                    return
                output = ''
                try:
                    output = git.commit(commit_message)
                    panel = window.create_output_panel('git_diff_view_commit', unlisted=False)
                    panel.run_command('append', {
                        "characters": output
                    })
                    window.run_command("show_panel", {"panel": "output.git_diff_view_commit"})
                except Exception as e:
                    output = str(e)
                    panel = window.create_output_panel('git_diff_view_commit', unlisted=False)
                    panel.run_command('append', {
                        "characters": output
                    })
                    window.run_command("show_panel", {"panel": "output.git_diff_view_commit"})
                    return
                # everything is ok close the diff view
                window.run_command('close_git_diff_view')
            if selected == 'Commit - Amend':
                output = ''
                try:
                    output = git.commit_amend()
                    panel = window.create_output_panel('git_diff_view_commit', unlisted=False)
                    panel.run_command('append', {
                        "characters": output
                    })
                    window.run_command("show_panel", {"panel": "output.git_diff_view_commit"})
                except Exception as e:
                    output = str(e)
                    panel = window.create_output_panel('git_diff_view_commit', unlisted=False)
                    panel.run_command('append', {
                        "characters": output
                    })
                    window.run_command("show_panel", {"panel": "output.git_diff_view_commit"})
                    return
                # everything is ok close the diff view
                window.run_command('close_git_diff_view')

        self.view.show_popup_menu(items, on_done=on_done)
