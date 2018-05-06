from .Command import Command
from .Format import Format

class GitStatusView:
    view_name = "Git Status"

    def __init__(self, window):
        self.window = window
        self.command = Command(window)

    def generate(self):
        view = self.window.new_file()
        staged_files = self.command.git_staged_files()
        print('staged files')
        print(staged_files)
        git_status_output = self.command.git_status_output()

        git_status_dic = Format.git_status(git_status_output)
        print('dictornary')
        print(git_status_dic)
        self._insert_text(view, git_status_output)
        self._configure_view(view)
        return view

    def _insert_text(self, view, output):
        # output = self._format(output)
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