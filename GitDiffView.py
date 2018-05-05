import sublime
import sublime_plugin
import subprocess

from .core.ViewsManager import ViewsManager
from .core.Layout import Layout


class GitDiffToggleViewCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        window = sublime.active_window()

        views_manager = ViewsManager(window)
        layout = Layout(window)

        # STATE: GitDiffView is open, will be closed
        if ViewsManager.toggle_view():
            layout.one_column()

            for view in window.views():
                if view.name() in ["Git Status", "Git Diff View"]:
                    window.focus_view(view)
                    window.run_command('close_file')

            views_manager.reopen()

        # STATE: GitDiffView is closed, will be opended
        else:

            views_manager.save_views_for_later()
            layout.two_columns()


            group = window.active_group()

            view = window.new_file()
            view.settings().set("plist.interface", 'plist')
            view.settings().set('highlight_line', True)
            view.settings().set("line_numbers", False)
            # view.settings().set("font_size", 12)
            view.settings().set("scroll_past_end", False)
            view.settings().set("draw_centered", False)
            view.settings().set("tab_size", 4)
            view.settings().set("show_minimap", False)
            view.settings().set("word_wrap", False)
            view.set_name("Git Status")
            view.set_scratch(True)

            window.set_view_index(view, 0, 0)
            print(window.views_in_group(group))

            view2 = window.new_file()
            view2.set_name("Git Diff View")
            view2.settings().set("line_numbers", False)
            view2.set_scratch(True)

            window.set_view_index(view2, 1, 0)

            # git 
            root = window.extract_variables()['folder']
            print('root')
            print(root)
            cmd = ['git status --porcelain']
            p = subprocess.Popen(cmd,
                                 bufsize = -1,
                                 cwd = root,
                                 stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 shell=True)
            output, stderr = p.communicate()
            if (stderr):
                print(stderr)
            git_status = (output)
            print(git_status)

            view.run_command("insert",{"characters": git_status.decode('ascii')})

            # print(views_manager.previous_views[window.id()])
            # print(views_manager.last_active_view[window.id()])
