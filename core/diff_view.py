from typing import List
import sublime


DIFF_VIEW_NAME = "Diff View"


def get_diff_view(views: List[sublime.View]):
    ''' Return the diff View '''
    for view in views:
        if view.name() == DIFF_VIEW_NAME:
            return view
    return None


def create_diff_view(window: sublime.Window):
    view = window.new_file()
    view.set_name(DIFF_VIEW_NAME)
    view.settings().set("line_numbers", False)
    view.set_scratch(True)
    return view
