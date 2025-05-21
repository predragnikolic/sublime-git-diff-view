from __future__ import annotations
from typing import Optional
import sublime


def get_line(view: sublime.View) -> Optional[int]:
    point = get_point(view)
    if point is None:
        return None
    return view.rowcol(view.line(point).begin())[0]


def get_line_at_point(view: sublime.View, point: int) -> int:
    return view.rowcol(view.line(point).begin())[0]

def get_selected_lines(view: sublime.View) -> list[int]:
    lines = []
    for r in view.sel():
        start_line = get_line_at_point(view, r.begin())
        end_line = get_line_at_point(view, r.end()) +1
        lines.extend([*range(start_line, end_line)])
    return lines

def get_point(view: sublime.View) -> Optional[int]:
    sel = view.sel()
    if not sel:
        return None
    return sel[0].b
