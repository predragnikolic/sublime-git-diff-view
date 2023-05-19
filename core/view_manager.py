from typing import List
from .diff_view import DIFF_VIEW_NAME
from .status_view import STATUS_VIEW_NAME
import sublime


class ViewsManager:
    ''' Responsible for storing views and reopening them later. '''

    # {'window_id' : [ views.file_names ]}
    previous_views = {}
    # {'window_id' : view.file_name }
    last_active_view = {}
    # {'window_id': pos}
    last_cursor_pos = {}
    # {'window_id': bool }
    last_sidebar_state = {}
    # {'window_id': str }
    last_active_panel = {}

    is_open = False

    def __init__(self, window):
        self.window = window

    @staticmethod
    def is_git_view_open(views: List[sublime.View]):
        for view in views:
            if view.name() in [STATUS_VIEW_NAME, DIFF_VIEW_NAME]:
                return True
        return False

    def prepare(self):
        self.save_views_for_later()
        self.window.set_sidebar_visible(False)
        self.window.run_command('hide_panel')

    def restore(self):
        print('called')
        views = self.get_views() or []
        print('views', views)
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

        last_sidebar_state = self.last_sidebar_state.get(self.window.id())
        if last_sidebar_state:
            self.window.set_sidebar_visible(True)

        last_active_panel = self.last_active_panel.get(self.window.id())
        if last_active_panel:
            self.window.run_command("show_panel", { "panel": last_active_panel })

        self._clear_state()

    def save_views_for_later(self):
        view = self.window.active_view()
        self._save_last_active_view(view)
        self._save_last_cursor_pos(view)
        self._save_sidebar_state()
        self._save_active_panel()
        self._save_views(self.window.views())

    def get_views(self):
        return self.previous_views.get(self.window.id(), [])

    def _get_last_active_view(self):
        return self.last_active_view.get(self.window.id())

    def _restore_cursor_pos(self, view):
        cursor_pos = self.last_cursor_pos.get(self.window.id())

        # put the cursor there
        sel = view.sel()
        sel.clear()
        sel.add(cursor_pos)

        # show the position at center
        # if the row is greater then the last visible row
        row = view.rowcol(cursor_pos)[0]
        last_visible_row = 18
        if row > last_visible_row:
            view.show_at_center(cursor_pos)

    def _save_last_active_view(self, view):
        self.last_active_view[self.window.id()] = view.file_name()

    def _save_last_cursor_pos(self, view):
        self.last_cursor_pos[self.window.id()] = view.sel()[0].begin()

    def _save_active_panel(self):
        self.last_active_panel[self.window.id()] = self.window.active_panel()

    def _save_sidebar_state(self):
        self.last_sidebar_state[self.window.id()] = self.window.is_sidebar_visible()

    def _save_views(self, views):
        self.previous_views[self.window.id()] = []
        for view in views:
            self.previous_views[self.window.id()].append(view.file_name())
            view.close()

    def _clear_state(self):
        self.previous_views[self.window.id()] = []
        self.last_active_panel[self.window.id()] = None
