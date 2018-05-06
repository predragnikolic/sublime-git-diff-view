import subprocess


class Command:
    def __init__(self, window):
        self.window = window
        self.project_root = window.extract_variables()['folder']

    def git_status_dict(self):
        files = []

        # array of staged files
        staged_files = self.git_staged_files().splitlines()
        git_status_output = self.git_status_output()
        
        files_changed = git_status_output.splitlines()
        files_changed = list(map(lambda file: file.strip(), files_changed))
        for file in files_changed:
            modification_type, file = file.split()
            # append space to modification type, looks prettier
            if len(modification_type) < 2:
                modification_type = ' {}'.format(modification_type)

            files.append({
                "file_name": file,
                "modification_type": modification_type,
                "is_staged": file in staged_files
            })

        return files

    def git_status_output(self):
        cmd = ['git status --porcelain']
        return self.run(cmd)

    def git_staged_files(self):
        cmd = ['git diff --name-only --cached']
        return self.run(cmd)

    def git_diff_file(self, file):
        cmd = ['git diff --no-color HEAD^ {}'.format(file)]
        return self.run(cmd)

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
        return output.decode('utf-8')