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

        views = window.views()
        print('views')
        print(views)
        if len(views) > 0:
            print('uslo')
            for view in views:
                print('ime')
                print(view.name())
                print(view.name() in ["Git Status", "Git Diff View"])
                if view.name() in ["Git Status", "Git Diff View"]:
                    window.focus_view(view)
                    window.run_command('close_file')

        
        if ViewsManager.toggle_view():
            views_manager.reopen()

        # We dont have any views
        # than we assume that the GitDiffView is closed
        else:
            views_manager.save_for_later()
            grid = {
                "cols": [0.0, 0.2, 1.0],
                "rows": [0.0, 1.0],
                "cells": [[0, 0, 1, 1], [1, 0, 2, 1]]
            }

            window.run_command('set_layout', grid)


            group = window.active_group()
            print('grupa')
            print(group)

            view = window.new_file()
            view.settings().set("plist.interface", 'plist')
            view.settings().set('highlight_line', True)
            view.settings().set("line_numbers", False)
            view.settings().set("font_size", 12)
            view.settings().set("scroll_past_end", False)
            view.settings().set("draw_centered", False)
            view.settings().set("line_padding_bottom", 2)
            view.settings().set("line_padding_top", 2)
            view.settings().set("tab_size", 4)
            view.settings().set("show_minimap", False)
            view.settings().set("word_wrap", False)
            view.set_name("Git Status")
            view.set_scratch(True)

            window.set_view_index(view, 0, 0)
            print(window.views_in_group(group))

            view2 = window.new_file()
            view2.set_name("Git Diff View")
            view2.settings().set("line_numbers", False)
            view2.set_scratch(True)

            window.set_view_index(view2, 1, 0)

            # print('test', 'delete')
            # print(views_manager.previous_views[window.id()])
            # print(views_manager.last_active_view[window.id()])
