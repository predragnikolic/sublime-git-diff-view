class Layout:
    '''Responsible for the layout'''

    def __init__(self, window):
        self.window = window

    def two_columns(self):
        ''' Set two column layout. '''

        grid = {
                "cols": [0.0, 0.3, 1.0],
                "rows": [0.0, 1.0],
                "cells": [[0, 0, 1, 1], [1, 0, 2, 1]]
            }
        self.window.run_command('set_layout', grid)

    def insert_into_first_column(self, view):
        ''' Insert into first column a view. '''
        self._insert_into_column(0, view)

    def insert_into_second_column(self, view):
        ''' Insert into second column a view. '''
        self._insert_into_column(1, view)

    def _insert_into_column(self, column, view):
        ''' Insert into a given column a view.
        Where column index starts at `0`. '''
        self.window.set_view_index(view, column, 0)
