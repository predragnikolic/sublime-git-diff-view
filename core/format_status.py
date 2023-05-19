from core.git_commands import GitStatus
from typing import List
import sublime


def format_git_statuses(git_statuses: List[GitStatus]) -> str:
    # type of modification, and if the file is staged
    # will be rendered to git status view
    result = []

    settings = sublime.load_settings("GitDiffView.sublime-settings")
    staged = settings.get('staged_symbol', '■')
    unstaged = ' '

    for status in git_statuses:
        staged_status = staged if status['is_staged'] else unstaged

        file_name = status['file_name']

        if status['old_file_name']:
            file_name = status['old_file_name'] \
                        + ' -> ' + status['file_name']

        result.append("{} {} {}".format(
            staged_status,
            status['modification_type'],
            file_name
        ))

    help = [
        "-------------------------------",
        "[a] stage/unstage file",
        "[d] dismiss changes to file",
        "[g] go to file"
    ]
    for option in help:
        result.append(option)

    return '\n'.join(result)

