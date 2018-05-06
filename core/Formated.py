from .Command import Command

class Formated:
    def __init__ (self, window):
        self.window = window
        self.command = Command(window)

    def git_status(self):
        # holds dict with every file, type of modification, and if the file is staged 
        files = []

        # array of staged files
        staged_files = self.command.git_staged_files().splitlines()
        git_status_output = self.command.git_status_output()
        
        files_changed = git_status_output.splitlines()
        files_changed = list(map(lambda file: file.strip(), files_changed))
        for file in files_changed:
            modification_type, file = file.split()
            # append space to modification type, looks prettier
            if len(modification_type) < 2:
                modification_type = ' {}'.format(modification_type)

            files.append({
                "name": file,
                "modification_type": modification_type,
                "is_staged": file in staged_files
            })

        formated_output = []
        staged = '✔'
        unstaged = '☐'
        
        for file in files:
            staged_status = staged if file['is_staged'] else unstaged

            formated_output.append("{} {} {}".format(
                staged_status,
                file['modification_type'],
                file['name']
            ))

        print('first diff')
        if len(files) > 0:
            if 'D' not in files[0]['modification_type']:
                print(self.command.git_diff_file(files[0]['name']))
            else: 
                print('ipak je d')

        return '\n'.join(formated_output)
