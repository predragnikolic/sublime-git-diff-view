import subprocess


class Command:
    def __init__(self, window):
        self.window = window

    def git_status_output(self):
        root = self.window.extract_variables()['folder']
        cmd = ['git status --porcelain']
        p = subprocess.Popen(cmd,
                             bufsize=-1,
                             cwd=root,
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             shell=True)
        output, stderr = p.communicate()
        if (stderr):
            print('Error in Command.py:', stderr)
        return output.decode('ascii')