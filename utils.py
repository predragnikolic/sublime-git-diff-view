from typing import List
from .core.git_commands import GitStatus
import sublime


def get_line(view: sublime.View):
    point = get_point(view)
    if point is None:
        return
    return view.rowcol(point)[0]


def get_point(view: sublime.View):
    sel = view.sel()
    if not sel:
        return
    return sel[0].b


def format_git_statuses(git_statuses: List[GitStatus]) -> str:
    result = []
    settings = sublime.load_settings("GitDiffView.sublime-settings")
    staged = '■'
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