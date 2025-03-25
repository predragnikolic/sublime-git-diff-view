import sublime


def three_columns(window: sublime.Window) -> None:
    ''' Set two column layout. '''
    grid = {
            "cols": [0.0, 0.3, 1.0],
            "rows": [0.0, 0.2, 1.0],
            "cells": [[0, 0, 1, 1], [0, 1, 1, 2], [1, 0, 2, 2]]
        }
    window.run_command('set_layout', grid)

def insert_into_first_column(window: sublime.Window, view: sublime.View) -> None:
    ''' Insert into first column a view. '''
    insert_into_column(window, 0, view)


def insert_into_second_column(window: sublime.Window, view: sublime.View) -> None:
    ''' Insert into second column a view. '''
    insert_into_column(window, 1, view)


def insert_into_third_column(window: sublime.Window, view: sublime.View) -> None:
    ''' Insert into second column a view. '''
    insert_into_column(window, 2, view)


def insert_into_column(window: sublime.Window, column: int, view: sublime.View) -> None:
    ''' Insert into a given column a view.
    Where column index starts at `0`. '''
    window.set_view_index(view, column, 0)
