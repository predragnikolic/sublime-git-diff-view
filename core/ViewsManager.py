class ViewsManager:
    '''Responsible for storing views and reopening them later'''

    # {'window_id' : [ views ]}
    previous_views = {}
    # { 'window_id' : view }
    last_active_view = {}

    is_open = False

    def __init__(self, window):
        self.window = window

    @staticmethod
    def is_git_view_open():
        is_open = ViewsManager.is_open
        ViewsManager.is_open = not ViewsManager.is_open
        return is_open

    def reopen(self):
        views = self.get_views() or []
        for file_name in views:
                if file_name:
                    self.window.open_file(file_name)

        last_active_view = self._get_last_active_view()
        if last_active_view:
            self.window.open_file(last_active_view)
        self._clear_state()

    def save_views_for_later(self):
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
