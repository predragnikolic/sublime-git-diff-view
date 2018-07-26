from os import path

import sublime
import sublime_plugin
from GitDiffView.status_commands.DismissChangesCommand import \
    GitDiffViewDismissChangesCommand
from GitDiffView.status_commands.GotoFileCommand import \
    GitDiffViewGotoFileCommand
from GitDiffView.status_commands.StageUnstageCommand import \
    GitDiffViewStageUnstageCommand

from .core.Command import Command
from .core.Event import Event
from .core.GitDiffView import GitDiffView
from .core.GitStatusView import GitStatusView
from .core.GitTextCommand import GitTextCommand
from .core.GitView import GitView
from .core.Layout import Layout
from .core.ViewsManager import ViewsManager


class ToggleGitDiffViewCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        window = sublime.active_window()
        self.command = Command(window)

        views_manager = ViewsManager(window)
        layout = Layout(window)
        git_view = GitView(window, layout)

        # STATE: GitView is open, will be closed
        if ViewsManager.is_git_view_open():
            git_view.close()
            layout.one_column()
            views_manager.reopen()

        # STATE: GitView is closed, will be opended
        else:
            # array of dict that holds information about
            # the file, type of modification, and if the file is staged
            git_statuses = self.command.git_status_dict()
            if self._no_git_output(git_statuses):
                window.status_message('No git changes to show.')
                return
            views_manager.save_views_for_later()
            layout.two_columns()
            git_view.open(git_statuses)

    def _no_git_output(self, git_statuses):
        return len(git_statuses) < 1


class SelectionChangedEvent(sublime_plugin.EventListener):
    previus_line = None
    listener = None

    def on_activated_async(self, view):
        if view.name() != GitStatusView.view_name:
            return

        self.listener = Event.listen(
            'git_status.update_diff_view',
            lambda line: GitView.update_diff_view(view, line))

        Event.listen('git_view.close', self.remove_listener)
        ViewsManager.is_open = True

    def on_deactivated_async(self, view):
        if view.name() != GitStatusView.view_name:
            return

        Event.fire('git_view.close')

    def on_close(self, view):
        if view.name() in [GitStatusView.view_name, GitDiffView.view_name]:
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
        return view.name() == GitStatusView.view_name

    def _have_selection_in(self, view):
        return len(view.sel()) > 0

    def remove_listener(self):
        if self.listener is not None:
            self.listener()
            self.listener = None


class UpdateDiffViewCommand(sublime_plugin.TextCommand):
    def run(self, edit, line, diff_output, modification_type):
        window = sublime.active_window()
        views = window.views()
        git_diff_view = self.get_view(views, GitDiffView.view_name)

        # enable editing the file for editing
        git_diff_view.set_read_only(False)

        if 'M' in modification_type:
            git_diff_view.set_syntax_file('Packages/Diff/Diff.sublime-syntax')

        elif 'U' in modification_type:
            git_diff_view.set_syntax_file('Packages/Diff/Diff.sublime-syntax')

        elif 'A' in modification_type:
            git_diff_view.set_syntax_file('Packages/Diff/Diff.sublime-syntax')

        elif 'R' in modification_type:
            git_diff_view.set_syntax_file('Packages/Diff/Diff.sublime-syntax')

        elif 'C' in modification_type:
            git_diff_view.set_syntax_file('Packages/Diff/Diff.sublime-syntax')

        elif '?' in modification_type:
            git_diff_view.set_syntax_file(
                'Packages/GitDiffView/syntax/GitUntracked.sublime-syntax')

        elif 'D' in modification_type:
            git_diff_view.set_syntax_file(
                'Packages/GitDiffView/syntax/GitRemoved.sublime-syntax')

        self.delete_content(git_diff_view)
        git_diff_view.insert(edit, 0, diff_output)
        # disable editing the file for showing
        git_diff_view.set_read_only(True)

        git_status_view = self.get_view(views, GitStatusView.view_name)
        window.focus_view(git_status_view)

    def delete_content(self, view):
        view.run_command("select_all")
        view.run_command("right_delete")

    def get_view(self, views, view_name):
        return list(
            filter(lambda view: view.name() == view_name, views)
        )[0]

