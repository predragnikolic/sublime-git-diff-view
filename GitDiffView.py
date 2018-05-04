import sublime
import sublime_plugin


class ViewsManager:
    # {'window_id' : [ views ]}
    previous_views = {}
    # { 'window_id' : view }
    last_active_view = {}

    def __init__(self, window):
        self.window = window

    def reopen(self, views):
        for file_name in views:
                self.window.open_file(file_name)

        self.window.open_file(self._get_last_active_view())
        self._clear_state()

    def save_for_later(self):
        last_active_view = self.window.active_view().file_name()
        self._save_last_active_view(last_active_view)
        self._save_views(self.window.views())

    def get_views(self):
        return self.previous_views.get(self.window.id())

    def _get_last_active_view(self):
        return self.last_active_view.get(self.window.id())

    def _save_last_active_view(self, file_name):
        self.last_active_view[self.window.id()] = file_name

    def _save_views(self, views):
        self.previous_views[self.window.id()] = []

        for view in views:
                self.previous_views[self.window.id()].append(view.file_name())
                self.window.focus_view(view)
                self.window.run_command('close_file')

    def _clear_state(self):
        self.previous_views[self.window.id()] = []
        self.last_active_view[self.window.id()] = ''


class GitDiffToggleViewCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        window = sublime.active_window()

        # If we have views
        # than assume that the GitDiffView is open
        views_manager = ViewsManager(window)
        views = views_manager.get_views()

        if views:
            views_manager.reopen(views)

        # We dont have any views
        # than we assume that the GitDiffView is closed
        else:
            views_manager.save_for_later()

            print('test', 'delete')
            print(views_manager.previous_views[window.id()])
            print(views_manager.last_active_view[window.id()])
         
            






