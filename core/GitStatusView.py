import sublime
from .Formated import Formated

prev_formated_git_stauts = ''


def get_git_status_view():
    ''' Return the git status View '''
    window = sublime.active_window()
    views = window.views()
    for view in views:
        if view.name() == 'Git Status':
            return view
    return None


class GitStatusView:
    view_name = "Git Status"

    def __init__(self, window):
        self.window = window
        self.formated = Formated(window)

    def generate(self, git_statuses):
        view = self.window.new_file()

        formated_git_status = self.formated.git_status(git_statuses)
        view.run_command("append", {"characters": formated_git_status})
        self._configure_view(view)
        return view

    def update(self, view, git_statuses):
        global prev_formated_git_stauts

        if isinstance(git_statuses, str):
            formated_git_status = git_statuses
        else:
            formated_git_status = self.formated.git_status(git_statuses)

        if prev_formated_git_stauts == formated_git_status:
            # dont trigger render, because it is the same content
            return

        prev_formated_git_stauts = formated_git_status

        view.run_command('update_status_view', {
                'content': formated_git_status,
            })

    def _configure_view(self, view):
        view.set_syntax_file(
            'Packages/GitDiffView/syntax/GitStatus.sublime-syntax')
        view.settings().set('highlight_line', True)
        view.settings().set("line_numbers", False)
        view.settings().set("scroll_past_end", False)
        view.settings().set("draw_centered", False)
        view.settings().set("tab_size", 4)
        view.settings().set("show_minimap", False)
        view.settings().set("word_wrap", False)
        view.set_name(self.view_name)
        view.set_scratch(True)
        # disable editing of the view
        view.set_read_only(True)
