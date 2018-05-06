from .Formated import Formated


class GitStatusView:
    view_name = "Git Status"

    def __init__(self, window):
        self.window = window
        self.formated = Formated(window)

    def generate(self):
        view = self.window.new_file()

        formated_git_status = self.formated.git_status()
        print('dictornary')
        print(formated_git_status)
        self._insert_text(view, formated_git_status)
        self._configure_view(view)
        return view

    def _insert_text(self, view, output):
        view.run_command("insert", {"characters": output})

    def _configure_view(self, view):
        view.settings().set('highlight_line', True)
        view.settings().set("line_numbers", False)
        view.settings().set("scroll_past_end", False)
        view.settings().set("draw_centered", False)
        view.settings().set("tab_size", 4)
        view.settings().set("show_minimap", False)
        view.settings().set("word_wrap", False)
        view.set_name(self.view_name)
        view.set_scratch(True)
        # disable editing of the view
        view.set_read_only(True)