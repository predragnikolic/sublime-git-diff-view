from typing import List, Literal, Optional, Tuple, TypedDict, cast
import re
import subprocess
import sublime


ModificationType = Literal[
     "??", # Untracked
     " A", # Added
     "AM", # Added and Staged
     " M", # Modified
     "MM", # Modified and Staged
     " D", # Deleted
     " R", # Renamed
     " C", # Copied
     "UU", # Unmerged(Conflict)
]

GitStatus = TypedDict('GitStatus', {
    "file_name": str,
    "modification_type": ModificationType,
    "is_staged": bool,
    "old_file_name": Optional[str]
})


class Git:
    ''' Responsible for running git commands throughout `subprocess`
    and returning it's output. '''

    def __init__(self, window: sublime.Window) -> None:
        self.window = window
        self.git_root_dir = None
        self.git_root_dir = str(self.run(['git rev-parse --show-toplevel']).strip())

    def git_statuses(self) -> List[GitStatus]:
        statuses: List[GitStatus] = []
        # array of staged statuses
        staged_files = self.diff().splitlines()
        git_status_output = self.status_untracked_files()
        # normalize git status output
        files_changed = git_status_output.splitlines()
        files_changed = list(map(lambda file: file.strip(), files_changed))
        for file in files_changed:
            reg_result = re.search(
                r"(.{0,2})\s+(.+)",
                file
            )
            if not reg_result:
                return []
            modification_type, file = reg_result.groups()
            # if file contains spaces the name will
            # be warped with quotes, so we strip them
            file = file.strip("\"")
            # strip spaces from type if left
            modification_type = modification_type.strip()
            old_file_name = None
            if 'R' in modification_type:
                old_file_name, file = self.split_filename_at_arrow(file)
            if 'C' in modification_type:
                old_file_name, file = self.split_filename_at_arrow(file)
            # append space to modification type, looks prettier
            if len(modification_type) < 2:
                modification_type = ' {}'.format(modification_type)
            statuses.append({
                "file_name": file,
                "modification_type": cast(ModificationType, modification_type),
                "is_staged": file in staged_files,
                "old_file_name": old_file_name
            })
        statuses = sorted(statuses, key=lambda k: k['file_name'])
        # bad code, fix circular imports (:
        from .git_diff_view import GitDiffView
        GitDiffView.git_statuses[self.window.id()] = statuses # store
        return statuses

    def split_filename_at_arrow(self, file: str) -> Tuple[str, str]:
        ''' If the file has a `->` than split it in two files.
        Returns the `old_file_name`, than the `new_file`. '''
        old_file_name, new_file = file.split("->")
        file = new_file.replace("\"", "")
        file = file.strip()
        old_file_name = old_file_name.replace("\"", "")
        old_file_name = old_file_name.strip()
        return old_file_name, file

    def status_untracked_files(self) -> str:
        cmd = ['git status --porcelain --untracked-files']
        return self.run(cmd)

    def diff(self) -> str:
        cmd = ['git diff --name-only --cached']
        return self.run(cmd)

    def diff_file(self, file_name: str) -> str:
        file_name = escape_special_characters(file_name)
        cmd = ['git diff --no-color HEAD -- {}'.format(file_name)]
        output = ''
        try:
            output = remove_diff_head(self.run(cmd))
        except Exception:
            output = self.show_added_file(file_name)
        return output

    def diff_head(self, file_name: str) -> str:
        file_name = escape_special_characters(file_name)
        cmd = ['git diff --no-color HEAD -- {}'.format(file_name)]
        output = ''
        try:
            output = diff_head(self.run(cmd))
        except Exception:
            output = ''
        return output

    def diff_file_staged(self, file_name: str) -> str:
        file_name = escape_special_characters(file_name)
        cmd = ['git diff --no-color --staged -- {}'.format(file_name)]
        output = remove_diff_head(self.run(cmd))
        return output

    def diff_file_unstaged(self, file_name: str) -> str:
        file_name = escape_special_characters(file_name)
        cmd = ['git diff --no-color -- {}'.format(file_name)]
        output = remove_diff_head(self.run(cmd))
        return output

    def show_added_file(self, file_name: str) -> str:
        file_name = escape_special_characters(file_name)
        cmd = ['cat {}'.format(file_name)]
        return self.run(cmd)

    def show_deleted_file(self, file_name: str) -> str:
        file_name = escape_special_characters(file_name)
        cmd = ['git show HEAD:{}'.format(file_name)]
        return self.run(cmd)

    def stage_file(self, file_name: str) -> str:
        """ stage file """
        file_name = escape_special_characters(file_name)
        cmd = ['git add {}'.format(file_name)]
        return self.run(cmd)

    def unstage_file(self, file_name: str) -> str:
        """ unstage file """
        file_name = escape_special_characters(file_name)
        cmd = ['git reset HEAD -- {}'.format(file_name)]
        return self.run(cmd)

    def checkout(self, file_name: str) -> str:
        """ dismiss changes """
        file_name = escape_special_characters(file_name)
        cmd = ['git checkout {}'.format(file_name)]
        return self.run(cmd)

    def clean(self, file_name: str) -> str:
        file_name = escape_special_characters(file_name)
        cmd = ['git clean -f {}'.format(file_name)]
        return self.run(cmd)

    def stage_patch(self, file_name: str) -> str:
        file_name = escape_special_characters(file_name)
        cmd = [f'git apply --cache {file_name}']
        return self.run(cmd)

    def discard_patch(self, file_name: str) -> str:
        file_name = escape_special_characters(file_name)
        cmd = [f'git apply --reverse {file_name}']
        return self.run(cmd)

    def unstage_patch(self, file_name: str) -> str:
        file_name = escape_special_characters(file_name)
        cmd = [f'git apply -R --cache {file_name}']
        return self.run(cmd)

    def run(self, cmd: List[str]) -> str:
        cwd = self.git_root_dir if self.git_root_dir else self.window.extract_variables()['folder']
        p = subprocess.Popen(cmd,
                             bufsize=-1,
                             cwd=cwd,
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             shell=True)
        output, stderr = p.communicate()
        if (stderr):
            print(f'GitDiffView: An error happened while running this command "{cmd}".', stderr)
            raise Exception(f'GitDiffView: An error happened while running this command "{cmd}". {stderr}')
        return output.decode('utf-8')


def escape_special_characters(file_name: str) -> str:
    file_name = file_name.replace('(', '\\(')
    file_name = file_name.replace(')', '\\)')
    return file_name.replace(' ', '\\ ')


def remove_diff_head(diff: str) -> str:
    return diff.split("\n", 4)[4]


def diff_head(diff: str) -> str:
    return "\n".join(diff.split("\n", 4)[:4])
