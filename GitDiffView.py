import sublime
import sublime_plugin

from .core.ViewsManager import ViewsManager
from .core.Layout import Layout
from .core.GitView import GitView


class GitDiffToggleViewCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        window = sublime.active_window()

        views_manager = ViewsManager(window)
        layout = Layout(window)
        git_view = GitView(window, layout)

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
