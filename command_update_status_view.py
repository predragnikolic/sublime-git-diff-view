from typing import Dict, List
from .core.git_commands import GitStatus, ModificationType
from .core.status_view import get_status_view
import sublime_plugin
import sublime


# command: update_status_view
class UpdateStatusViewCommand(sublime_plugin.TextCommand):
    def __init__(self, view):
        super().__init__(view)
        self.phantom_set = sublime.PhantomSet(view, "status_view_phantoms")
        self.prev_git_statuses: str = ''

    def _is_same(self, git_statuses: List[GitStatus]):
        return self.prev_git_statuses == str(git_statuses)

    def run(self, edit, git_statuses: List[GitStatus]):
        if self._is_same(git_statuses):
            return
        self.prev_git_statuses = str(git_statuses)
        window = self.view.window()
        if not window:
            return
        active_view = window.active_view()
        status_view = get_status_view(window.views())
        if status_view is None:
            return
        files = []
        phantoms: List[sublime.Phantom] = []
        for git_status in git_statuses:
            file_name = git_status['file_name']
            if git_status['old_file_name']:
                file_name = f"{git_status['old_file_name']} -> {git_status['file_name']}"
            files.append(file_name)
        new_content = '\n'.join(files)
        # update diff view if necessary
        if len(git_statuses) < 1:
            new_content = "No changes"
        # update status view
        status_view.set_read_only(False)
        status_view.replace(edit, sublime.Region(0, status_view.size()), new_content)
        status_view.set_read_only(True)

        style = status_view.style()
        changed = status_view.style_for_scope("markup.changed").get('foreground')
        inserted = status_view.style_for_scope("markup.inserted").get('foreground')
        deleted = status_view.style_for_scope("markup.deleted").get('foreground')
        untracked = status_view.style_for_scope("markup.untracked").get('foreground')
        comment = status_view.style_for_scope("comment").get('foreground')
        renamed = style.get('purplish')

        for i, git_status in enumerate(git_statuses):
            point = status_view.text_point(i, 0)
            modification_type = git_status['modification_type']
            primary_color = "#ff0000"
            if modification_type == 'MM':
                primary_color = changed
            elif 'A' in modification_type:
                primary_color = inserted
            elif 'M' in modification_type:
                primary_color = changed
            elif 'U' in modification_type:
                primary_color = changed
            elif 'R' in modification_type:
                primary_color = renamed
            elif 'C' in modification_type:
                primary_color = changed
            elif '?' in modification_type:
                primary_color = untracked
            elif 'D' in modification_type:
                primary_color = deleted

            is_staged = git_status['is_staged']
            unstaged_styles = f"color: {primary_color}; border: 1px solid {primary_color};"
            staged_styles = f"color: #333333; background-color: {primary_color}; border: 1px solid {primary_color};"
            styles = staged_styles if is_staged else unstaged_styles

            readable_modification_type = modification_type_to_readable(modification_type)
            title = f'{readable_modification_type} and STAGED' if is_staged else f'{readable_modification_type} and UNSTAGED'
            print('title', title)
            phantom = sublime.Phantom(sublime.Region(point), f'''<div title="{title}" style="font-weight: bold; text-align: center; border-radius: 4px; width: 2em; padding:0 0.1rem; margin-right: 0.4em; {styles}">
                <div>{git_status['modification_type'].strip()}</div>
            </div>''', sublime.LAYOUT_INLINE)

            phantoms.append(phantom)
        help_phantom = sublime.Phantom(sublime.Region(status_view.size(), status_view.size()), f'''<div style="border-top: 1px solid #77777720; color: {comment}">
            <div style="margin-top: 0.4rem">a - stage/unstage a file</div>
            <div style="margin-top: 0.4rem">d - dismiss changes to a file</div>
            <div style="margin-top: 0.4rem">g - go to a file</div>
        </div>''', sublime.LAYOUT_BLOCK)
        phantoms.append(help_phantom)
        self.phantom_set.update(phantoms)
        if active_view:
            window.focus_view(active_view)


def modification_type_to_readable(modification_type: ModificationType) -> str:
    title_dict: Dict[ModificationType, str] = {
        "??": "File is UNTRACKED",
        " A": "File is ADDED",
        "AM": "File is ADDED",
        " M": "File is MODIFIED",
        "MM": "File is MODIFIED",
        " D": "File is Deleted",
        " R": "File is Renamed",
        " C": "File is Copied",
        "UU": "File has Conflict/s"
    }
    return title_dict[modification_type]