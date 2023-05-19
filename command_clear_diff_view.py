from .core.diff_view import get_diff_view
import sublime
import sublime_plugin


# command: clear_diff_view
class ClearDiffView(sublime_plugin.TextCommand):
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