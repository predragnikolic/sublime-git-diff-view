import sublime
import sublime_plugin

from .core.ViewsManager import ViewsManager
from .core.Layout import Layout
from .core.GitView import GitView
from .core.GitStatusView import GitStatusView
from .core.Event import Event
from .core.Command import Command


class GitDiffToggleViewCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        window = sublime.active_window()

        views_manager = ViewsManager(window)
        layout = Layout(window)
        git_view = GitView(window, layout, edit)
        command = Command(window)

        git_statuses = command.git_status_dict()
        if len(git_statuses) < 1:
            window.status_message('No git changes to show.')
            return

        # STATE: GitView is open, will be closed
        if ViewsManager.toggle_view():
            git_view.close()
            layout.one_column()
            views_manager.reopen()

        # STATE: GitView is closed, will be opended
        else:
            views_manager.save_views_for_later()
            layout.two_columns()
            git_view.open()


class SelectionChangedEvent(sublime_plugin.EventListener):
    previus_line = None

    def on_selection_modified_async(self, view):

        if len(view.sel()) < 1:
            return
        cursor_pos = view.sel()[0].begin()

        if not cursor_pos:
            return
        current_line = view.rowcol(cursor_pos)[0]
        on_same_line = current_line == self.previus_line

        if self._is_git_status_view(view) or on_same_line:
            return

        self.previus_line = current_line
        Event.fire('git_status.update_diff_view', current_line)

    def _is_git_status_view(self, view):
        return view.name() != GitStatusView.view_name


class UpdateDiffViewCommand(sublime_plugin.TextCommand):
    def run(self, edit, line, diff_output):
        window = sublime.active_window()
        views = window.views_in_group(1)
        git_diff_view = list(filter(lambda view: view.name() == "Git Diff View", views))[0]
        git_diff_view.set_read_only(False)
        git_diff_view.run_command("select_all")
        git_diff_view.run_command("right_delete")
        git_diff_view.insert(edit, 0, diff_output)
        git_diff_view.set_read_only(True)

        views = sublime.active_window().views_in_group(0)
        git_status_view = list(filter(lambda view: view.name() == GitStatusView.view_name, views))[0]

        window.focus_view(git_status_view)
