from .core.status_view import get_status_view
from .core.git_commands import Git
from .core.git_diff_view import GitDiffView
from .utils import get_line
from os import path
import sublime
import sublime_plugin


# command: git_diff_view_goto_file
class GitDiffViewGotoHunkCommand(sublime_plugin.TextCommand):
    def run(self, _: sublime.Edit) -> None:
        diff_view = self.view
        window = self.view.window()
        if not window:
            return
        status_view = get_status_view(window.views())
        if not status_view:
            return
        line = get_line(status_view)
        if line is None:
            return
        git = Git(window)
        git_statuses = GitDiffView.git_statuses[window.id()]
        git_status = git_statuses[line]
        if not git_status:
            return
        if 'D' in git_status["modification_type"]:
            window.status_message("GitDiffVIew: Can't go to a deleted file")
            return
        file_name = git_status["file_name"]
        if not git.git_root_dir or not file_name:
            return
        absolute_path_to_file = path.join(git.git_root_dir,
                                          git_status["file_name"])
        sel = diff_view.sel()
        if not sel:
            return
        cursor = sel[0].b
        start_patch = diff_view.find('^@@.+@@', cursor, sublime.REVERSE)
        row = 0
        if start_patch:
            header = diff_view.substr(start_patch).split(' ')  #  ['@@', '-23,5', '+23,10', '@@']
            row = header[2].replace('-', '').replace('+', '').split(',')[0]  # row = 23
        window.run_command('toggle_git_diff_view')
        view = window.open_file(f"{absolute_path_to_file}:{row}", sublime.ENCODED_POSITION)
        sublime.set_timeout(lambda: window.focus_view(view))
