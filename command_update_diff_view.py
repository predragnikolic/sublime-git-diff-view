from .core.diff_view import get_diff_view
from .core.git_commands import Git, GitStatus
from .core.status_view import get_status_view
from typing import Optional
import sublime
import sublime_plugin


# command: update_diff_view
class UpdateDiffViewCommand(sublime_plugin.TextCommand):
    def run(self, edit, git_status: GitStatus):
        modification_type = git_status['modification_type']
        file_name = git_status['file_name']
        window = self.view.window()
        if not window:
            return
        git = Git(window)
        views = window.views()
        diff_view = get_diff_view(views)
        if not diff_view:
            return
        # enable editing the file for editing
        diff_view.set_read_only(False)
        diff_output = ''
        if 'MM' == modification_type:
            diff_output = (
                "Staged\n" +
                "======\n" +
                git.diff_file_staged(file_name) +
                "Unstaged\n" +
                "========\n" +
                git.diff_file_unstaged(file_name)
            )
        elif 'M' in modification_type:
            diff_view.set_syntax_file('Packages/Diff/Diff.sublime-syntax')
            diff_output = git.diff_file(file_name)
        elif 'U' in modification_type:
            diff_view.set_syntax_file('Packages/Diff/Diff.sublime-syntax')
            diff_output = git.diff_file(file_name)
        elif 'A' in modification_type:
            diff_view.set_syntax_file('Packages/Diff/Diff.sublime-syntax')
            diff_output = git.diff_file(file_name)
        elif 'R' in modification_type:
            diff_view.set_syntax_file('Packages/Diff/Diff.sublime-syntax')
            diff_output = git.diff_file(file_name)
        elif 'C' in modification_type:
            diff_view.set_syntax_file('Packages/Diff/Diff.sublime-syntax')
            diff_output = git.diff_file(file_name)
        elif '?' in modification_type:
            syntax = get_syntax(file_name, self.view)
            diff_view.set_syntax_file(syntax or 'Packages/GitDiffView/syntax/GitUntracked.sublime-syntax')
            diff_output = git.show_added_file(file_name)
        elif 'D' in modification_type:
            diff_view.set_syntax_file(
                'Packages/GitDiffView/syntax/GitRemoved.sublime-syntax')
            diff_output = git.show_deleted_file(file_name)
        diff_view.replace(edit, sublime.Region(0, diff_view.size()), diff_output)

        sel = diff_view.sel()
        if sel:
            sel.clear()

        # disable editing the file for showing
        diff_view.set_read_only(True)

        status_view = get_status_view(views)
        if status_view:
            window.focus_view(status_view)


def get_syntax(file_name: str, view: sublime.View) -> Optional[str]:
    window = view.window()
    if not window:
        return
    tmp_buffer = window.open_file(file_name, sublime.TRANSIENT)
    # Even if is_loading() is true the view's settings can be
    # retrieved; settings assigned before open_file() returns.
    syntax = str(tmp_buffer.settings().get("syntax", ""))
    window.run_command("close")
    window.focus_view(view)
    return syntax
