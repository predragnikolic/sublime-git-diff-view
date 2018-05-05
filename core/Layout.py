class Layout:
    '''Resposible for the layout'''
    def __init__(self, window):
        self.window = window

    def one_column(self):
        grid = {
                "cols": [0.0, 1.0],
                "rows": [0.0, 1.0],
                "cells": [[0, 0, 1, 1]]
            }
        self.window.run_command('set_layout', grid)

    def two_columns(self):
        grid = {
                "cols": [0.0, 0.3, 1.0],
                "rows": [0.0, 1.0],
                "cells": [[0, 0, 1, 1], [1, 0, 2, 1]]
            }
        self.window.run_command('set_layout', grid)
