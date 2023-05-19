import sublime


def get_syntax(file_name: str, view: sublime.View):
    window = view.window()
    if not window:
        return
    tmp_buffer = window.open_file(file_name, sublime.TRANSIENT)
    # Even if is_loading() is true the view's settings can be
    # retrieved; settings assigned before open_file() returns.
    syntax = str(tmp_buffer.settings().get("syntax", ""))
    window.run_command("close")
    window.focus_view(view)
    return syntax

