import subprocess


class Command:
    def __init__(self, window):
        self.window = window
        self.project_root = window.extract_variables()['folder']

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