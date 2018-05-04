import sublime
import sublime_plugin
from .core.ViewsManager import ViewsManager


class GitDiffToggleViewCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        window = sublime.active_window()

        # If we have views
        # than assume that the GitDiffView is open
        views_manager = ViewsManager(window)
        views = views_manager.get_views()

        if views:
            views_manager.reopen(views)

        # We dont have any views
        # than we assume that the GitDiffView is closed
        else:
            views_manager.save_for_later()

            print('test', 'delete')
            print(views_manager.previous_views[window.id()])
            print(views_manager.last_active_view[window.id()])
         
            






