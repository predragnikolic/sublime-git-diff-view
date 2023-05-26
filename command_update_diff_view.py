from .core.diff_view import get_diff_view
from .core.git_commands import Git, GitStatus
from .core.status_view import get_status_view
from typing import List, Optional
import sublime
import sublime_plugin
import difflib as dl
import re

# command: update_diff_view
class UpdateDiffViewCommand(sublime_plugin.TextCommand):
    def run(self, edit: sublime.Edit, git_status: GitStatus) -> None:
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
            diff_view.set_syntax_file('Packages/Diff/Diff.sublime-syntax')
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

        self.add_diff_highlights(diff_view, git_status)

        status_view = get_status_view(views)
        if status_view:
            window.focus_view(status_view)

    def add_diff_highlights(self, diff_view: sublime.View, git_status: GitStatus) -> None:
        st_bug_first_call_to_find_all_will_not_work_correctly = diff_view.find_all('') # haha, one new ST bug :D, without this line, the bellow diff_view.find_all will not work. Looks like the first call to diff_view.find_all will not work correctly.
        added_lines = diff_view.find_all('^\\+.*')
        removed_lines = diff_view.find_all('^\\-.*')

        add_changes: List[sublime.Region] = []
        remove_changes: List[sublime.Region] = []
        plus_minus_sign_offset = 1
        # TODO: The way diffs are found is probably not the best... PRs to improve this are welcome
        diffs = list(dl.ndiff(
                [diff_view.substr(sublime.Region(r.begin() + plus_minus_sign_offset, r.end())) for r in removed_lines],
                [diff_view.substr(sublime.Region(r.begin() + plus_minus_sign_offset, r.end())) for r in added_lines]))
        start_find_pt = 0
        for i, diff in enumerate(diffs):
            is_change = diff.startswith('?')
            if is_change:
                look_text = diffs[i-1][2:]  #+ +    font-size: 0.9em dsa;
                diff_text = diff[2:]        #? ^                    ++++
                look_region = diff_view.find(re.escape(look_text), start_find_pt)
                row, _ = diff_view.rowcol(look_region.begin())
                # for debugging
                # print('look text', look_text)
                # print('diff text', diff_text)
                addition_matches = re.finditer(r'\++', diff_text)
                for i in addition_matches:
                    start, end = i.span(0)
                    start_point = diff_view.text_point(row, start + plus_minus_sign_offset)
                    end_point = diff_view.text_point(row, end + plus_minus_sign_offset)
                    start_find_pt = end_point
                    add_changes.append(sublime.Region(start_point, end_point))

                removal_matches = re.finditer(r'\-+', diff_text)
                for i in removal_matches:
                    start, end = i.span(0)
                    start_point = diff_view.text_point(row, start + plus_minus_sign_offset)
                    end_point = diff_view.text_point(row, end + plus_minus_sign_offset)
                    start_find_pt = end_point
                    remove_changes.append(sublime.Region(start_point, end_point))

                diff_text_without_leading_tilde = ' ' + diff_text[1:] # diff_text
                modification_matches = re.finditer('\\^+', diff_text_without_leading_tilde)
                for i in modification_matches:
                    start, end = i.span(0)
                    start_point = diff_view.text_point(row, start + plus_minus_sign_offset)
                    end_point = diff_view.text_point(row, end + plus_minus_sign_offset)
                    start_find_pt = end_point

                    if diff_view.match_selector(start_point, 'markup.deleted.diff'):
                        remove_changes.append(sublime.Region(start_point, end_point))
                    else:
                        add_changes.append(sublime.Region(start_point, end_point))

        diff_view.add_regions('git_diff_view.add_bg', added_lines, "diff.inserted")
        diff_view.add_regions('git_diff_view.removed_bg', removed_lines, "diff.deleted")
        diff_view.add_regions('git_diff_view.add_char', add_changes, "diff.inserted.char")
        diff_view.add_regions('git_diff_view.remove_char', remove_changes, "diff.deleted.char")

        if git_status['modification_type'] == ' D':
             diff_view.add_regions('git_diff_view.removed_bg', [sublime.Region(0, diff_view.size())], "diff.deleted")


def get_syntax(file_name: str, view: sublime.View) -> Optional[str]:
    window = view.window()
    if not window:
        return None
    tmp_buffer = window.open_file(file_name, sublime.TRANSIENT)
    # Even if is_loading() is true the view's settings can be
    # retrieved; settings assigned before open_file() returns.
    syntax = str(tmp_buffer.settings().get("syntax", ""))
    window.run_command("close")
    window.focus_view(view)
    return syntax
