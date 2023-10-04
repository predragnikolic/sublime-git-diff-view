import sublime
from .core.git_commands import Git
from .core.status_view import get_status_view
from .core.git_diff_view import GitDiffView
from .utils import get_line
import sublime_plugin
import os

# command: git_diff_view_stage_unstage_chunk
class GitDiffViewStageUnstageChunkCommand(sublime_plugin.TextCommand):
    def run(self, _: sublime.Edit) -> None:
        window = self.view.window()
        if not window:
            return
        diff_view = self.view
        sel = diff_view.sel()
        if not sel:
            return
        cursor = sel[0].b
        status_view = get_status_view(window.views())
        if not status_view:
            return
        line = get_line(status_view)
        if line is None:
            return
        git = Git(window)
        git_statuses = GitDiffView.git_statuses[window.id()]
        git_status = git_statuses[line]
        if not git_status:
            return
        head = git.diff_head(git_status['file_name'])

        start_patch = diff_view.find('^@@', cursor, sublime.REVERSE)
        if not start_patch:
            return

        end_patch = diff_view.find('^@@', cursor)
        if not end_patch:
            end_patch = sublime.Region(diff_view.size())
        hunk_content = diff_view.substr(sublime.Region(start_patch.begin(), end_patch.begin()))
        patch_content = f"{head}\n{hunk_content}"

        not_staged = not git_status['is_staged'] or diff_view.find('^Unstaged', cursor, sublime.REVERSE)
        temp_patch_file = os.path.join(sublime.cache_path(), 'temp_patch_file.patch')
        patch_file = open(temp_patch_file, 'w', encoding='utf-8')
        try:
            patch_file.write(patch_content)
            patch_file.close()
            if not_staged:
                git.apply_patch(temp_patch_file)
            else:
                git.undo_patch(temp_patch_file)
        finally:
            patch_file.close()
            os.remove(patch_file.name)

        new_git_statuses = git.git_statuses()
        new_git_status = new_git_statuses[line]
        status_view.run_command('update_status_view', {
            'git_statuses': new_git_statuses,
        })
        diff_view.run_command("update_diff_view", {
            'git_status': new_git_status,
        })

# command: git_diff_view_stage_unstage
class GitDiffViewStageUnstageCommand(sublime_plugin.TextCommand):
    def run(self, _: sublime.Edit) -> None:
        window = self.view.window()
        if not window:
            return
        line = get_line(self.view)
        if line is None:
            return
        git = Git(window)
        git_statuses = GitDiffView.git_statuses[window.id()]
        git_status = git_statuses[line]
        if not git_status:
            return
        if git_status["is_staged"]:
            git.reset_head(git_status["file_name"])
        else:
            git.add(git_status["file_name"])
        git_statuses = git.git_statuses()
        self.view.run_command('update_status_view', {
            'git_statuses': git_statuses,
        })
        self.view.run_command("update_diff_view", {
            'git_status': git_status,
        })
