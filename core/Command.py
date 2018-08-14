import subprocess
import re


class Command:
    ''' Responsible for running git comands throught `subprocess`
    and returning it's output. '''

    # for testing testing
    # called_times = 1
    # def called(self):
    #     print('called ', self.called_times)
    #     self.called_times += 1

    def __init__(self, window):
        self.window = window
        self.project_root = window.extract_variables()['folder']

    def git_statuses(self):
        ''' Return a list of git statuses.
        Example:
        [{
            "file_name",
            "modification_type",
            "is_staged",
            "old_file_name"
        }] '''
        statuses = []

        # array of staged statuses
        staged_files = self.git_staged_files().splitlines()
        git_status_output = self.git_status_output()

        # normalize git status output
        files_changed = git_status_output.splitlines()
        files_changed = list(map(lambda file: file.strip(), files_changed))
        for file in files_changed:
            modification_type, file = re.search(
                r"(.{0,2})\s+(.+)",
                file
            ).groups()
            # if file contains spaces the name will
            # be wraped with quotes, so we strip them
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
                "modification_type": modification_type,
                "is_staged": file in staged_files,
                "old_file_name": old_file_name
            })

        return statuses

    def split_filename_at_arrow(self, file):
        ''' If the file has a `->` than split it in two files.
        Returns the `old_file_name`, than the `new_file`. '''
        old_file_name, new_file = file.split("->")
        file = new_file.replace("\"", "")
        file = file.strip()
        old_file_name = old_file_name.replace("\"", "")
        old_file_name = old_file_name.strip()
        return old_file_name, file

    def git_status_output(self):
        cmd = ['git status --porcelain --untracked-files']
        return self.run(cmd)

    def git_staged_files(self):
        cmd = ['git diff --name-only --cached']
        return self.run(cmd)

    def git_diff_file(self, file_name):
        file_name = self.escape_special_characters(file_name)
        cmd = ['git diff --no-color HEAD -- {}'.format(file_name)]
        output = ''
        try:
            output = self.run(cmd)
        except Exception:
            output = self.show_added_file(file_name)
        return output

    def show_added_file(self, file_name):
        file_name = self.escape_special_characters(file_name)
        cmd = ['cat {}'.format(file_name)]
        return self.run(cmd)

    def show_deleted_file(self, file_name):
        file_name = self.escape_special_characters(file_name)
        cmd = ['git show HEAD:{}'.format(file_name)]
        return self.run(cmd)

    def git_stage(self, file_name):
        file_name = self.escape_special_characters(file_name)
        cmd = ['git add {}'.format(file_name)]
        return self.run(cmd)

    def git_unstage(self, file_name):
        file_name = self.escape_special_characters(file_name)
        cmd = ['git reset HEAD -- {}'.format(file_name)]
        return self.run(cmd)

    def git_dismis_changes(self, file_name):
        file_name = self.escape_special_characters(file_name)
        cmd = ['git checkout {}'.format(file_name)]
        return self.run(cmd)

    def escape_special_characters(self, file_name):
        file_name = file_name.replace('(', '\\(');
        file_name = file_name.replace(')', '\\)');
        return file_name.replace(' ', '\\ ')

    def run(self, cmd):
        p = subprocess.Popen(cmd,
                             bufsize=-1,
                             cwd=self.project_root,
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             shell=True)
        output, stderr = p.communicate()
        if (stderr):
            print('Error in Command.py:', stderr)
            raise Exception('Error in Command.py: {}'.format(stderr))
        return output.decode('utf-8')
