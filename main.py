from typing import List, Optional
import sublime
import sublime_plugin

from .dismiss_changes import GitDiffViewDismissChangesCommand
from .goto_file import GitDiffViewGotoFileCommand
from .stage_unstage_file import GitDiffViewStageUnstageCommand

from .core.git_commands import Git, GitStatus
from .core.event_bus import Event
from .core.diff_view import get_diff_view, DIFF_VIEW_NAME
from .core.status_view import format_git_statuses, get_status_view, STATUS_VIEW_NAME
from .core.git_view import GitView
from .core.layout import Layout
from .core.view_manager import ViewsManager

STOP_INTERVAL = False

def set_interval(fn):
    def interval():
        fn()
        if not STOP_INTERVAL:
            sublime.set_timeout(interval, 800)
    sublime.set_timeout(interval, 800)


def refresh_list():
    ''' Refresh git status view content'''
    window = sublime.active_window()
    view = window.active_view()
    if view is None:
        return
    git_statuses = Git(window).git_statuses()
    view.run_command('update_status_view', {
        'git_statuses': git_statuses,
    })


# command: update_status_view
class UpdateStatusViewCommand(sublime_plugin.TextCommand):
    prev_formatted_git_statuses = ""
    def run(self, edit, git_statuses: List[GitStatus]):
        window = self.view.window()
        if not window:
            return
        status_view = get_status_view(window.views())
        if status_view is None:
            return
        formatted_git_statuses = format_git_statuses(git_statuses)
        if UpdateStatusViewCommand.prev_formatted_git_statuses == formatted_git_statuses:
            # dont trigger render, because it is the same content
            return
        UpdateStatusViewCommand.prev_formatted_git_statuses = formatted_git_statuses
        new_content = formatted_git_statuses
        # update diff view if necessary
        if len(git_statuses) < 1:
            new_content = "No changes"
            status_view.run_command("clear_git_diff_view")
        # update status view
        status_view.set_read_only(False)
        status_view.replace(edit, sublime.Region(0, status_view.size()), new_content)
        status_view.set_read_only(True)


# command: clear_git_diff_view
class ClearGitDiffView(sublime_plugin.TextCommand):
    def run(self, edit):
        w = self.view.window()
        if not w:
            return
        diff_view = get_diff_view(w.views())
        if diff_view is None:
            return
        diff_view.set_read_only(False)
        diff_view.replace(edit, sublime.Region(0, diff_view.size()), "")
        diff_view.set_read_only(True)


class ToggleGitDiffViewCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        global STOP_INTERVAL

        window = sublime.active_window()
        self.git = Git(window)

        layout = Layout(window)
        views_manager = ViewsManager(window)
        git_view = GitView(window, layout)

        # STATE: GitView is open, will be closed
        if ViewsManager.is_git_view_open():
            git_view.close()
            layout.one_column()
            views_manager.restore()

            STOP_INTERVAL = True
        # STATE: GitView is closed, will be opended
        else:
            # array of dict that holds information about
            # the file, type of modification, and if the file is staged
            git_statuses = self.git.git_statuses()
            if self._no_git_output(git_statuses):
                window.status_message('No git changes to show.')
                return

            views_manager.prepare()
            layout.two_columns()
            git_view.open(git_statuses)

            STOP_INTERVAL = False
            set_interval(refresh_list)

    def _no_git_output(self, git_statuses):
        return len(git_statuses) < 1


class SelectionChangedEvent(sublime_plugin.EventListener):
    previus_line = None
    listener = None

    def on_activated_async(self, view):
        if view.name() != STATUS_VIEW_NAME:
            return

        self.listener = Event.listen(
            'git_status.update_diff_view',
            lambda line: GitView.update_diff_view(view, line))

        Event.listen('git_view.close', self.remove_listener)
        ViewsManager.is_open = True

    def on_deactivated_async(self, view):
        if view.name() != STATUS_VIEW_NAME:
            return

        Event.fire('git_view.close')

    def on_close(self, view):
        if view.name() in [STATUS_VIEW_NAME, DIFF_VIEW_NAME]:
            ViewsManager.is_open = True
            view.run_command('toggle_git_diff_view')
            Event.fire('git_view.close')

    def on_selection_modified_async(self, view):
        if not self._is_git_status_view_in_focus(view):
            return

        if not self._have_selection_in(view):
            return

        cursor_pos = view.sel()[0].begin()
        current_line = view.rowcol(cursor_pos)[0]
        on_same_line = current_line == self.previus_line

        if on_same_line:
            return

        self.previus_line = current_line
        Event.fire('git_status.update_diff_view', current_line)

    def _is_git_status_view_in_focus(self, view):
        return view.name() == STATUS_VIEW_NAME

    def _have_selection_in(self, view):
        return len(view.sel()) > 0

    def remove_listener(self):
        if self.listener is not None:
            self.listener()
            self.listener = None


class UpdateGitDiffViewCommand(sublime_plugin.TextCommand):
    def run(self, edit, diff_output, modification_type, file_name):
        window = sublime.active_window()
        views = window.views()
        diff_view = get_diff_view(views)
        if not diff_view:
            return

        # enable editing the file for editing
        diff_view.set_read_only(False)

        if 'M' in modification_type:
            diff_view.set_syntax_file('Packages/Diff/Diff.sublime-syntax')

        elif 'U' in modification_type:
            diff_view.set_syntax_file('Packages/Diff/Diff.sublime-syntax')

        elif 'A' in modification_type:
            diff_view.set_syntax_file('Packages/Diff/Diff.sublime-syntax')

        elif 'R' in modification_type:
            diff_view.set_syntax_file('Packages/Diff/Diff.sublime-syntax')

        elif 'C' in modification_type:
            diff_view.set_syntax_file('Packages/Diff/Diff.sublime-syntax')

        elif '?' in modification_type:
            syntax = get_syntax(file_name, self.view)
            diff_view.set_syntax_file(syntax or 'Packages/GitDiffView/syntax/GitUntracked.sublime-syntax')

        elif 'D' in modification_type:
            diff_view.set_syntax_file(
                'Packages/GitDiffView/syntax/GitRemoved.sublime-syntax')

        diff_view.replace(edit, sublime.Region(0, diff_view.size()), diff_output)
        sel = diff_view.sel()
        if sel:
            sel.clear()

        # disable editing the file for showing
        diff_view.set_read_only(True)

        status_view = get_status_view(views)
        if not status_view:
            return
        window.focus_view(status_view)



def plugin_loaded():
    status_view = get_status_view(sublime.active_window().views())

    # If status view is open when sublime starts, 
    # setup listener for refreshing the list
    if status_view is not None:
        set_interval(refresh_list)


def get_syntax(file_name: str, view: sublime.View) -> Optional[str]:
    window = view.window()
    if not window:
        return
    tmp_buffer = window.open_file(file_name, sublime.TRANSIENT)
    # Even if is_loading() is true the view's settings can be
    # retrieved; settings assigned before open_file() returns.
    syntax = str(tmp_buffer.settings().get("syntax", ""))
    window.run_command("close")
    window.focus_view(view)
    return syntax

