import sublime
import sublime_plugin

from .core.ViewsManager import ViewsManager
from .core.Layout import Layout
from .core.GitView import GitView
from .core.GitStatusView import GitStatusView
from .core.GitDiffView import GitDiffView
from .core.Event import Event
from .core.Command import Command


class GitDiffToggleViewCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        window = sublime.active_window()
        self.command = Command(window)

        views_manager = ViewsManager(window)
        layout = Layout(window)
        git_view = GitView(window, layout, edit)

        # STATE: GitView is open, will be closed
        if ViewsManager.toggle_view():
            git_view.close()            
            layout.one_column()
            views_manager.reopen()

        # STATE: GitView is closed, will be opended
        else:
            if self._no_git_output():
                window.status_message('No git changes to show.')
                return
            views_manager.save_views_for_later()
            layout.two_columns()
            git_view.open()

    def _no_git_output(self):
        git_statuses = self.command.git_status_dict()
        return len(git_statuses) < 1


class SelectionChangedEvent(sublime_plugin.EventListener):
    previus_line = None

    def on_selection_modified_async(self, view):
        if not self._have_selection_in(view):
            return

        cursor_pos = view.sel()[0].begin()
        current_line = view.rowcol(cursor_pos)[0]
        on_same_line = current_line == self.previus_line

        # return if the git status view is not in focus
        if not self._is_git_status_view_in_focus(view) or on_same_line:
            return

        self.previus_line = current_line
        Event.fire('git_status.update_diff_view', current_line)

    def _is_git_status_view_in_focus(self, view):
        return view.name() == GitStatusView.view_name

    def _have_selection_in(self, view):
        return len(view.sel()) > 0


class UpdateDiffViewCommand(sublime_plugin.TextCommand):
    def run(self, edit, line, diff_output):
        window = sublime.active_window()
        views = window.views()
        git_diff_view = self.get_view(views, GitDiffView.view_name)

        # enable editing the file for editing
        git_diff_view.set_read_only(False)
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
