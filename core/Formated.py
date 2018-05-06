from .Command import Command

class Formated:
    def __init__ (self, window):
        self.window = window
        self.command = Command(window)

    def git_status(self, git_statuses):
        # holds dict with every file, type of modification, and if the file is staged 

        formated_output = []
        staged = '✔'
        unstaged = '☐'
        
        for status in git_statuses:
            staged_status = staged if status['is_staged'] else unstaged

            formated_output.append("{} {} {}".format(
                staged_status,
                status['modification_type'],
                status['file_name']
            ))

        return '\n'.join(formated_output)
