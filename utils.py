from typing import Optional
import sublime


def get_line(view: sublime.View) -> Optional[int]:
    point = get_point(view)
    if point is None:
        return None
    return view.rowcol(view.line(point).begin())[0]


def get_point(view: sublime.View) -> Optional[int]:
    sel = view.sel()
    if not sel:
        return None
    return sel[0].b
