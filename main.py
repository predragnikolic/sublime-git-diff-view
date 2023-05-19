from typing import List, Optional
import sublime
import sublime_plugin
from .utils import get_line

from .dismiss_changes import GitDiffViewDismissChangesCommand
from .goto_file import GitDiffViewGotoFileCommand
from .stage_unstage_file import GitDiffViewStageUnstageCommand

from .core.git_commands import Git, GitStatus
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
            sublime.set_timeout(interval, 2000)
    sublime.set_timeout(interval, 2000)


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


# command: toggle_git_diff_view
class ToggleGitDiffViewCommand(sublime_plugin.TextCommand):
    def run(self, _):
        global STOP_INTERVAL
        window = sublime.active_window()
        if not window:
            return

        layout = Layout(window)
        views_manager = ViewsManager(window)
        git_view = GitView(window, layout)

        if ViewsManager.is_git_view_open(window.views()):
            git_view.close()
            layout.one_column()
            views_manager.restore()

            STOP_INTERVAL = True
        else:
            git = Git(window)
            # open GitView
            # array of dict that holds information about
            # the file, type of modification, and if the file is staged
            git_statuses = git.git_statuses()
            if not git_statuses:
                window.status_message('No git changes to show.')
                return

            views_manager.prepare()
            layout.two_columns()
            git_view.open()

            STOP_INTERVAL = False
            set_interval(refresh_list)


class SelectionChangedEvent(sublime_plugin.EventListener):
    previous_line = None
    listener = None

    def on_close(self, view):
        if view.name() in [STATUS_VIEW_NAME, DIFF_VIEW_NAME]:
            view.run_command('toggle_git_diff_view')

    def on_selection_modified(self, view):
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
        git_statuses = GitView.git_statuses[window.id()]
        try:
            git_status = git_statuses[line]
            view.run_command("update_diff_view", {
                'git_status': git_status,
            })
        except:
            status_view.run_command("clear_git_diff_view")


# command: update_diff_view
class UpdateDiffViewCommand(sublime_plugin.TextCommand):
    def run(self, edit, git_status: GitStatus):
        modification_type = git_status['modification_type']
        file_name = git_status['file_name']
        window = self.view.window()
        if not window:
            return
        git = Git(window)
        views = window.views()
        diff_view = get_diff_view(views)
        if not diff_view:
            return
        # enable editing the file for editing
        diff_view.set_read_only(False)
        diff_output = ''
        if 'MM' == modification_type:
            diff_output = (
                "Staged\n" +
                "======\n" +
                git.diff_file_staged(file_name) +
                "Unstaged\n" +
                "========\n" +
                git.diff_file_unstaged(file_name)
            )
        elif 'M' in modification_type:
            diff_view.set_syntax_file('Packages/Diff/Diff.sublime-syntax')
            diff_output = git.diff_file(file_name)
        elif 'U' in modification_type:
            diff_view.set_syntax_file('Packages/Diff/Diff.sublime-syntax')
            diff_output = git.diff_file(file_name)
        elif 'A' in modification_type:
            diff_view.set_syntax_file('Packages/Diff/Diff.sublime-syntax')
            diff_output = git.diff_file(file_name)
        elif 'R' in modification_type:
            diff_view.set_syntax_file('Packages/Diff/Diff.sublime-syntax')
            diff_output = git.diff_file(file_name)
        elif 'C' in modification_type:
            diff_view.set_syntax_file('Packages/Diff/Diff.sublime-syntax')
            diff_output = git.diff_file(file_name)
        elif '?' in modification_type:
            syntax = get_syntax(file_name, self.view)
            diff_view.set_syntax_file(syntax or 'Packages/GitDiffView/syntax/GitUntracked.sublime-syntax')
            diff_output = git.show_added_file(file_name)
        elif 'D' in modification_type:
            diff_view.set_syntax_file(
                'Packages/GitDiffView/syntax/GitRemoved.sublime-syntax')
            diff_output = git.show_deleted_file(file_name)
        diff_view.replace(edit, sublime.Region(0, diff_view.size()), diff_output)

        sel = diff_view.sel()
        if sel:
            sel.clear()

        # disable editing the file for showing
        diff_view.set_read_only(True)

        status_view = get_status_view(views)
        if status_view:
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

