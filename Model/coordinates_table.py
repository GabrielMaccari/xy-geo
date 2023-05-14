# -*- coding: utf-8 -*-
"""
@author: Gabriel Maccari
"""


class CoordinatesTable:
    def __init__(self, df, y_column=None, x_column=None, crs=None, crs_type=None):
        self.df = df

        self.y_column = y_column
        self.x_column = x_column

        self.crs = crs
        self.crs_type = crs_type
