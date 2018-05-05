from .Command import Command


class GitView:
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