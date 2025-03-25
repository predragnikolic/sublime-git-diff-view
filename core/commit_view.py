from typing import List, Optional
import sublime

COMMIT_VIEW_NAME = "Commit Message"
prev_formatted_git_status = ''


def get_commit_view(views: List[sublime.View]) -> Optional[sublime.View]:
    ''' Return the git status View '''
    for view in views:
        if view.name() == COMMIT_VIEW_NAME:
            return view
    return None


def create_commit_view(window: sublime.Window) -> sublime.View:
    view = window.new_file()
    # configure view
    view.set_syntax_file("Packages/Markdown/Markdown.sublime-syntax")
    view.settings().set('highlight_line', False)
    view.settings().set("line_numbers", False)
    view.settings().set("scroll_past_end", False)
    view.settings().set("draw_centered", False)
    view.settings().set("tab_size", 4)
    view.settings().set("show_minimap", False)
    view.settings().set("draw_indent_guides", False)
    view.set_name(COMMIT_VIEW_NAME)
    view.set_scratch(True)
    return view
