import subprocess


class Command:
    def __init__(self, window):
        self.window = window
        self.project_root = window.extract_variables()['folder']

    def git_status_output(self):
        cmd = ['git status --porcelain']
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
        return output.decode('ascii')
