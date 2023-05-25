from os import path
from .diff_view import DIFF_VIEW_NAME
from .status_view import STATUS_VIEW_NAME
from typing import Any, Dict, List, Optional
import sublime
import json
from pathlib import Path

SESSION_DIR = path.join(sublime.cache_path(), 'GitDiffView')

WindowId = int
FileName = str
Layout = Dict[str, Any]

RootDirPath = str

class ViewsManager:
    ''' Responsible for storing views and reopening them later. '''


    def __init__(self, window: sublime.Window, root_dir: RootDirPath) -> None:
        self.window: sublime.Window = window
        self.root_dir = root_dir
        self.session_file_path = path.join(SESSION_DIR, 'session.json')
        self.previous_file_names: List[FileName] = []
        self.last_active_file_name: Optional[FileName] = None
        self.last_cursor_pos:  Optional[int] = None
        self.last_sidebar_state:  Optional[bool] = None
        self.last_active_panel:  Optional[str] = None
        self.last_layout:  Optional[Layout] = None
        self.view_to_group: Dict[FileName, int] = {}

    @staticmethod
    def is_git_view_open(views: List[sublime.View]) -> bool:
        for view in views:
            if view.name() in [STATUS_VIEW_NAME, DIFF_VIEW_NAME]:
                return True
        return False

    def prepare(self) -> None:
        # save layout
        self.last_layout = self.window.layout()
        self.save_views_for_later()
        self.window.set_sidebar_visible(False)
        self.window.run_command('hide_panel')

        self.save_to_session_file()

    def load_session_file(self) -> None:
        if not path.exists(self.session_file_path):
            return
        saved_file = open(self.session_file_path, "r")
        dict = json.loads(saved_file.read()) or {}
        saved_file.close()
        saved_settings = dict.pop(self.root_dir, {})
        self.previous_file_names = saved_settings.get('previous_file_names', [])
        self.last_active_file_name = saved_settings.get('last_active_file_name', None)
        self.last_cursor_pos = saved_settings.get('last_cursor_pos', None)
        self.last_sidebar_state = saved_settings.get('last_sidebar_state', None)
        self.last_active_panel = saved_settings.get('last_active_panel', None)
        self.last_layout = saved_settings.get('last_layout', None)
        self.view_to_group = saved_settings.get('view_to_group', {})
        file_path = Path(self.session_file_path)
        file_path.touch(exist_ok=True)
        file = open(file_path, "w+")
        file.write(json.dumps(dict))
        file.close()

    def save_to_session_file(self) -> None:
        saved_file = open(self.session_file_path, "r")
        dict = json.loads(saved_file.read()) or {}
        saved_file.close()
        dict[self.root_dir] = {}
        dict[self.root_dir]['previous_file_names'] = self.previous_file_names
        dict[self.root_dir]['last_active_file_name'] = self.last_active_file_name
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


    def restore(self) -> None:
        self.load_session_file()
        # restore layout
        last_layout = self.last_layout
        if last_layout:
            self.window.set_layout(last_layout)
        # restore views
        views = self.previous_file_names
        for file_name in views:
            if file_name:
                group = self.view_to_group.get(file_name, -1)
                self.window.open_file(file_name, group=group)
        # restore last active view
        last_active_file_name = self.last_active_file_name
        if last_active_file_name is not None:
            view = self.window.open_file(last_active_file_name)

            def trying_restoring_the_cursor(view: sublime.View) -> None:
                if not view.is_loading():
                    self._restore_cursor_pos(view)
                else:
                    # cant put the cursor if the view is not loaded
                    # so try it again
                    sublime.set_timeout(lambda:
                                        trying_restoring_the_cursor(view), 20)

            trying_restoring_the_cursor(view)
        # restore sidebar
        last_sidebar_state = self.last_sidebar_state
        if last_sidebar_state is not None:
            self.window.set_sidebar_visible(True)
        # restore panel
        last_active_panel = self.last_active_panel
        if last_active_panel:
            self.window.run_command("show_panel", { "panel": last_active_panel })

    def save_views_for_later(self) -> None:
        view = self.window.active_view()
        if view:
            file_name = view.file_name()
            # save active view
            if file_name:
                self.last_active_file_name = file_name
            # save cursor
            self.last_cursor_pos = view.sel()[0].begin()
        # save sidebar
        self.last_sidebar_state = self.window.is_sidebar_visible()
        # save panel
        active_panel = self.window.active_panel()
        if active_panel:
            self.last_active_panel = active_panel
        # save open views
        self._save_open_file_names(self.window)

    def _restore_cursor_pos(self, view: sublime.View) -> None:
        cursor_pos = self.last_cursor_pos
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

    def _save_open_file_names(self, window: sublime.Window) -> None:
        self.previous_file_names = []
        num_groups = window.num_groups()
        for group in range(num_groups):
            for view in window.views_in_group(group):
                file_name = view.file_name()
                if file_name:
                    self.view_to_group[file_name] = group
                    self.previous_file_names.append(file_name)
                    view.close()
