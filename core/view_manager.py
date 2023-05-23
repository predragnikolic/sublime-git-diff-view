from os import path
from .diff_view import DIFF_VIEW_NAME
from .status_view import STATUS_VIEW_NAME
from typing import Any, Dict, List
import sublime
import json
from pathlib import Path

WindowId = int
FileName = str
Layout = Dict[str, Any]

RootDirPath = str

class ViewsManager:
    ''' Responsible for storing views and reopening them later. '''

    previous_views: Dict[RootDirPath, List[FileName]] = {}
    last_active_view: Dict[RootDirPath, FileName] = {}
    last_cursor_pos: Dict[RootDirPath, int] = {}
    last_sidebar_state: Dict[RootDirPath, bool] = {}
    last_active_panel: Dict[RootDirPath, str] = {}
    last_layout: Dict[RootDirPath, Layout] = {}
    view_to_group: Dict[FileName, int] = {}

    def __init__(self, window: sublime.Window, root_dir: RootDirPath):
        self.window: sublime.Window = window
        self.root_dir = root_dir
        self.session_file_path = path.join(sublime.cache_path(), 'GitDiffView', 'session.json')

    @staticmethod
    def is_git_view_open(views: List[sublime.View]):
        for view in views:
            if view.name() in [STATUS_VIEW_NAME, DIFF_VIEW_NAME]:
                return True
        return False

    def prepare(self):
        # save layout
        self.last_layout[self.root_dir] = self.window.layout()
        self.save_views_for_later()
        self.window.set_sidebar_visible(False)
        self.window.run_command('hide_panel')

        self.save_to_session_file()

    def load_session_file(self):
        if not path.exists(self.session_file_path):
            return
        file = open(self.session_file_path, "r")
        dict = json.loads(file.read())
        file.close()
        self.previous_views = dict.get(self.root_dir, {}).get('previous_views', {})
        self.last_active_view = dict.get(self.root_dir, {}).get('last_active_view', {})
        self.last_cursor_pos = dict.get(self.root_dir, {}).get('last_cursor_pos', {})
        self.last_sidebar_state = dict.get(self.root_dir, {}).get('last_sidebar_state', {})
        self.last_active_panel = dict.get(self.root_dir, {}).get('last_active_panel', {})
        self.last_layout = dict.get(self.root_dir, {}).get('last_layout', {})
        self.view_to_group = dict.get(self.root_dir, {}).get('view_to_group', {})
        file.close()

    def save_to_session_file(self):
        dict = {}
        dict[self.root_dir] = {}
        dict[self.root_dir]['previous_views'] = self.previous_views
        dict[self.root_dir]['last_active_view'] = self.last_active_view
        dict[self.root_dir]['last_cursor_pos'] = self.last_cursor_pos
        dict[self.root_dir]['last_sidebar_state'] = self.last_sidebar_state
        dict[self.root_dir]['last_active_panel'] = self.last_active_panel
        dict[self.root_dir]['last_layout'] = self.last_layout
        dict[self.root_dir]['view_to_group'] = self.view_to_group
        file_path = Path(self.session_file_path)
        file_path.touch(exist_ok=True)
        file = open(file_path, "w+")
        file.write(json.dumps(dict))
        file.close()

    def restore(self):
        self.load_session_file()
        # restore layout
        last_layout = self.last_layout[self.root_dir]
        if last_layout:
            self.window.set_layout(last_layout)
        # restore views
        views = self.get_views() or []
        for file_name in views:
            if file_name:
                group = self.view_to_group.get(file_name, -1)
                self.window.open_file(file_name, group=group)
        # restore last active view
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
        # restore sidebar
        last_sidebar_state = self.last_sidebar_state.get(self.root_dir)
        if last_sidebar_state:
            self.window.set_sidebar_visible(True)
        # restore panel
        last_active_panel = self.last_active_panel.get(self.root_dir)
        if last_active_panel:
            self.window.run_command("show_panel", { "panel": last_active_panel })

    def save_views_for_later(self):
        view = self.window.active_view()
        if view:
            self._save_last_active_view(view)
            self._save_last_cursor_pos(view)
        self._save_sidebar_state()
        self._save_active_panel()
        self._save_views(self.window)

    def get_views(self):
        return self.previous_views.get(self.root_dir, [])

    def _get_last_active_view(self):
        return self.last_active_view.get(self.root_dir)

    def _restore_cursor_pos(self, view: sublime.View):
        cursor_pos = self.last_cursor_pos.get(self.root_dir)
        if not cursor_pos:
            return
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

    def _save_last_active_view(self, view: sublime.View):
        file_name = view.file_name()
        if file_name:
            self.last_active_view[self.root_dir] = file_name

    def _save_last_cursor_pos(self, view: sublime.View):
        self.last_cursor_pos[self.root_dir] = view.sel()[0].begin()

    def _save_active_panel(self):
        active_panel = self.window.active_panel()
        if active_panel:
            self.last_active_panel[self.root_dir] = active_panel

    def _save_sidebar_state(self):
        self.last_sidebar_state[self.root_dir] = self.window.is_sidebar_visible()

    def _save_views(self, window: sublime.Window):
        self.previous_views[self.root_dir] = []
        num_groups = window.num_groups()
        for group in range(num_groups):
            for view in window.views_in_group(group):
                file_name = view.file_name()
                if file_name:
                    self.view_to_group[file_name] = group
                    self.previous_views[self.root_dir].append(file_name)
                    view.close()
