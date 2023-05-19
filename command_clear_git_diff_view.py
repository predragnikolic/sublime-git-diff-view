from core.diff_view import get_diff_view
import sublime_plugin
import sublime


# command: clear_git_diff_view
class ClearGitDiffView(sublime_plugin.TextCommand):
    def run(self, edit):
        w = self.view.window()
        if not w:
            return
        diff_view = get_diff_view(w.views())
        if diff_view is None:
            return
        diff_view.set_read_only(False)
        diff_view.replace(edit, sublime.Region(0, diff_view.size()), "")
        diff_view.set_read_only(True)