import sublime


class ViewsManager:
    ''' Responsible for storing views and reopening them later. '''

    # {'window_id' : [ views.file_names ]}
    previous_views = {}
    # {'window_id' : view.file_name }
    last_active_view = {}
    # {'window_id': pos}
    last_cursor_pos = {}

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
            view = self.window.open_file(last_active_view)

            def trying_restoring_the_cursor(view):
                if not view.is_loading():
                    self._restore_cursor_pos(view)
                else:
                    # cant put the cursor if the view is not loaded
                    # so try it again
                    sublime.set_timeout(lambda:
                                        trying_restoring_the_cursor(view), 20)

            trying_restoring_the_cursor(view)
        self._clear_state()

    def save_views_for_later(self):
        view = self.window.active_view()
        self._save_last_active_view(view)
        self._save_last_cursor_pos(view)
        self._save_views(self.window.views())

    def get_views(self):
        return self.previous_views.get(self.window.id())

    def _get_last_active_view(self):
        return self.last_active_view.get(self.window.id())

    def _restore_cursor_pos(self, view):
        cursor_pos = self.last_cursor_pos.get(self.window.id())

        # put the cursor there
        sel = view.sel()
        sel.clear()
        sel.add(cursor_pos)

        # show the position at center
        view.show_at_center(cursor_pos)

    def _save_last_active_view(self, view):
        self.last_active_view[self.window.id()] = view.file_name()

    def _save_last_cursor_pos(self, view):
        self.last_cursor_pos[self.window.id()] = view.sel()[0].begin()

    def _save_views(self, views):
        self.previous_views[self.window.id()] = []

        for view in views:
                self.previous_views[self.window.id()].append(view.file_name())
                self.window.focus_view(view)
                self.window.run_command('close_file')

    def _clear_state(self):
        self.previous_views[self.window.id()] = []
