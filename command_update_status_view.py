from typing import List
from .core.git_commands import GitStatus
from .core.status_view import get_status_view
import sublime_plugin
import sublime


# command: update_status_view
class UpdateStatusViewCommand(sublime_plugin.TextCommand):
    def __init__(self, view):
        super().__init__(view)
        self.phantom_set = sublime.PhantomSet(view, "status_view_phantoms")

    def run(self, edit, git_statuses: List[GitStatus]):
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
            # self.phantom_set.update([])
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
            elif 'M' in modification_type:
                primary_color = changed
            elif 'U' in modification_type:
                primary_color = changed
            elif 'A' in modification_type:
                primary_color = inserted
            elif 'R' in modification_type:
                primary_color = renamed
            elif 'C' in modification_type:
                primary_color = changed
            elif '?' in modification_type:
                primary_color = untracked
            elif 'D' in modification_type:
                primary_color = deleted

            unstaged_styles = f"color: {primary_color}; border: 1px solid {primary_color};"
            staged_styles = f"color: #333333; background-color: {primary_color}; border: 1px solid {primary_color};"
            styles = staged_styles if git_status['is_staged'] else unstaged_styles
            phantom = sublime.Phantom(sublime.Region(point), f'''<div style="font-weight: bold; text-align: center; border-radius: 4px; width: 2em; padding:0 0.1rem; margin-right: 0.4em; {styles}">
                <div>{git_status['modification_type'].strip()}</div>
            </div>''', sublime.LAYOUT_INLINE)

            phantoms.append(phantom)
        help_phantom = sublime.Phantom(sublime.Region(status_view.size(), 0), f'''<div style="border-top: 1px solid #77777720; color: {comment}">
            <div style="margin-top: 0.4rem">a - stage/unstage a file</div>
            <div style="margin-top: 0.4rem">d - dismiss changes to a file</div>
            <div style="margin-top: 0.4rem">g - go to a file</div>
        </div>''', sublime.LAYOUT_BELOW)
        phantoms.append(help_phantom)
        self.phantom_set.update(phantoms)

        if active_view:
            window.focus_view(active_view)


