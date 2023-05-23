import sublime


def two_columns(window: sublime.Window):
    ''' Set two column layout. '''
    grid = {
            "cols": [0.0, 0.3, 1.0],
            "rows": [0.0, 1.0],
            "cells": [[0, 0, 1, 1], [1, 0, 2, 1]]
        }
    window.run_command('set_layout', grid)


def insert_into_first_column(window: sublime.Window, view: sublime.View):
    ''' Insert into first column a view. '''
    insert_into_column(window, 0, view)


def insert_into_second_column(window: sublime.Window, view: sublime.View):
    ''' Insert into second column a view. '''
    insert_into_column(window, 1, view)


def insert_into_column(window: sublime.Window, column: int, view: sublime.View):
    ''' Insert into a given column a view.
    Where column index starts at `0`. '''
    window.set_view_index(view, column, 0)
