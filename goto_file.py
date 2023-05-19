from os import path
from .git_text import GitTextCommand
from .core.git_commands import Command


class GitDiffViewGotoFileCommand(GitTextCommand):
    def run(self, edit):
        if self.have_a_diff_to_show():
            file = self.get_file()

            if 'D' in file["modification_type"]:
                print('cant go to a deleted file')
                return

            command = Command(self.window)
            absolute_path_to_file = path.join(command.project_root,
                                              file["file_name"])
            self.window.run_command('toggle_git_diff_view')
            view = self.window.open_file(absolute_path_to_file)
            self.window.focus_view(view)
