from core.git_commands import GitStatus
from typing import List
import sublime

prev_formatted_git_status = ''

def get_git_status_view():
    ''' Return the git status View '''
    window = sublime.active_window()
    views = window.views()
    for view in views:
        if view.name() == 'Git Status':
            return view
    return None

class GitStatusView:
    view_name = "Git Status"

    def __init__(self, window):
        self.window = window

    def create(self, git_statuses):
        view = self.window.new_file()

        formatted_git_status = format_git_statuses(git_statuses)
        view.run_command("append", {"characters": formatted_git_status})
        self._configure_view(view)
        return view

    def update(self, view, git_statuses):
        global prev_formatted_git_status

        if isinstance(git_statuses, str):
            formatted_git_status = git_statuses
        else:
            formatted_git_status = format_git_statuses(git_statuses)

        if prev_formatted_git_status == formatted_git_status:
            # dont trigger render, because it is the same content
            return

        prev_formatted_git_status = formatted_git_status

        view.run_command('update_status_view', {
                'content': formatted_git_status,
            })

    def _configure_view(self, view):
        settings = sublime.load_settings("GitDiffView.sublime-settings")

        default_sytnax = "Packages/GitDiffView/syntax/GitStatus.sublime-syntax"
        fancy_sytnax = "Packages/GitDiffView/syntax/GitStatusFancy.sublime-syntax"

        highlight_file_names = settings.get("highlight_file_names", False)
        syntax = fancy_sytnax if highlight_file_names else default_sytnax

        view.set_syntax_file(syntax)

        view.settings().set('highlight_line', True)
        view.settings().set("line_numbers", False)
        view.settings().set("scroll_past_end", False)
        view.settings().set("draw_centered", False)
        view.settings().set("tab_size", 4)
        view.settings().set("show_minimap", False)
        view.settings().set("word_wrap", False)
        view.settings().set("draw_indent_guides", False)
        view.set_name(self.view_name)
        view.set_scratch(True)
        # disable editing of the view
        view.set_read_only(True)


def format_git_statuses(git_statuses: List[GitStatus]) -> str:
    result = []
    settings = sublime.load_settings("GitDiffView.sublime-settings")
    staged = settings.get('staged_symbol', '■')
    unstaged = ' '
    for status in git_statuses:
        staged_status = staged if status['is_staged'] else unstaged
        file_name = status['file_name']
        if status['old_file_name']:
            file_name = f"{status['old_file_name']} -> {status['file_name']}"
        result.append(f"{staged_status} {status['modification_type']} {file_name}")
    help = [
        "-------------------------------",
        "[a] stage/unstage file",
        "[d] dismiss changes to file",
        "[g] go to file"
    ]
    for option in help:
        result.append(option)
    return '\n'.join(result)
