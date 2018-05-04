import sublime
import sublime_plugin
from .core.ViewsManager import ViewsManager


class GitDiffToggleViewCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        window = sublime.active_window()

        # If we have views
        # than assume that the GitDiffView is open
        views_manager = ViewsManager(window)

        grid = {
            "cols": [0.0, 1.0],
            "rows": [0.0, 1.0],
            "cells": [[0, 0, 1, 1]]
        }

        window.run_command('set_layout', grid)

        print('niz')
        print(window.num_groups())

        if ViewsManager.toggle_view():
            views_manager.reopen()

        # We dont have any views
        # than we assume that the GitDiffView is closed
        else:
            views_manager.save_for_later()
            grid = {
                "cols": [0.0, 0.35, 1.0],
                "rows": [0.0, 1.0],
                "cells": [[0, 0, 1, 1], [1, 0, 2, 1]]
            }

            window.run_command('set_layout', grid)

            print('niz')
            print(window.num_groups())

            # print('test', 'delete')
            # print(views_manager.previous_views[window.id()])
            # print(views_manager.last_active_view[window.id()])
