import sublime


def get_line(view: sublime.View):
    point = get_point(view)
    if point is None:
        return
    return view.rowcol(point)[0]


def get_point(view: sublime.View):
    sel = view.sel()
    if not sel:
        return
    return sel[0].b
