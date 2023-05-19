from ..utils import format_git_statuses
from .git_commands import GitStatus
from typing import List, Optional
import sublime

STATUS_VIEW_NAME = "Git Status"
prev_formatted_git_status = ''


def get_status_view(views: List[sublime.View]) -> Optional[sublime.View]:
    ''' Return the git status View '''
    for view in views:
        if view.name() == STATUS_VIEW_NAME:
            return view
    return None


def create_status_view(window: sublime.Window, git_statuses: List[GitStatus]) -> sublime.View:
    view = window.new_file()
    formatted_git_status = format_git_statuses(git_statuses)
    view.run_command("append", {"characters": formatted_git_status})
    # configure view
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
    view.set_name(STATUS_VIEW_NAME)
    view.set_scratch(True)
    # disable editing of the view
    view.set_read_only(True)
    return view
