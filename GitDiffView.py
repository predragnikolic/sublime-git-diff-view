import sublime
import sublime_plugin

from .core.ViewsManager import ViewsManager
from .core.Layout import Layout
from .core.Command import Command

class GitDiffView:
    def __init__(self, window, layout):
        self.window = window
        self.layout = layout
        self.command = Command(window)

    def close(self):
        for view in self.window.views():
            if view.name() in ["Git Status", "Git Diff View"]:
                self.window.focus_view(view)
                self.window.run_command('close_file')

    def open(self):
        view = self.window.new_file()
        view.settings().set("plist.interface", 'plist')
        view.settings().set('highlight_line', True)
        view.settings().set("line_numbers", False)
        # view.settings().set("font_size", 12)
        view.settings().set("scroll_past_end", False)
        view.settings().set("draw_centered", False)
        view.settings().set("tab_size", 4)
        view.settings().set("show_minimap", False)
        view.settings().set("word_wrap", False)
        view.set_name("Git Status")
        view.set_scratch(True)

        self.layout.insert_into_first_column(view)

        view2 = self.window.new_file()
        view2.set_name("Git Diff View")
        view2.settings().set("line_numbers", False)
        view2.set_scratch(True)

        self.layout.insert_into_second_column(view2)
        git_status = self.command.git_status_output()

        view.run_command("insert", {"characters": git_status})


class GitDiffToggleViewCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        window = sublime.active_window()

        views_manager = ViewsManager(window)
        layout = Layout(window)
        git_diff_view = GitDiffView(window, layout)

        # STATE: GitDiffView is open, will be closed
        if ViewsManager.toggle_view():
            git_diff_view.close()
            layout.one_column()
            views_manager.reopen()

        # STATE: GitDiffView is closed, will be opended
        else:
            views_manager.save_views_for_later()
            layout.two_columns()
            git_diff_view.open()

            # print(views_manager.previous_views[window.id()])
            # print(views_manager.last_active_view[window.id()])
