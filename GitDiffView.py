import sublime
import sublime_plugin

class Views:
    previous_views = {} 
    last_active_view = {}

    @staticmethod
    def get_views(window_id):
        return Views.previous_views.get(window_id)

    @staticmethod
    def get_last_active_view(window_id):
        return Views.last_active_view.get(window_id)

    @staticmethod
    def set_last_active_view(window, file_name):
        Views.last_active_view[window.id()] = file_name

    @staticmethod
    def set_views(window, views):
        Views.previous_views[window.id()] = []

        for view in views:
                Views.previous_views[window.id()].append(view.file_name())
                window.focus_view(view)
                window.run_command('close_file')

    @staticmethod
    def clear_views(window):
        Views.previous_views[window.id()] = []
        Views.last_active_view[window.id()] = ''


class GitDiffToggleViewCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        active_window = sublime.active_window()

        # If we retrive views from our state
        # assume that the GitDiffView is open
        views = Views.get_views(active_window.id())
        if views:
            for file_name in views:
                active_window.open_file(file_name)

            active_window.open_file(
                Views.get_last_active_view(active_window.id())
            )

            Views.clear_views(active_window)

        # We dont have any views from our state
        # so we assume that the GitDiffView is closed
        else:
            last_active_view = active_window.active_view().file_name()
            Views.set_last_active_view(active_window, last_active_view)
            Views.set_views(active_window, active_window.views())
            
            print('test')
            print(Views.state[active_window.id()])
            print(Views.last_active_view[active_window.id()])






