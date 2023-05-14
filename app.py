# -*- coding: utf-8 -*-
"""
@author: Gabriel Maccari
"""

from PyQt6.QtWidgets import QApplication
import sys

from Model.coordinates_table import CoordinatesTable
from View.main_window import AppMainWindow
from Controller.operations_controller import OperationsController
from Controller.ui_controller import UIController

if __name__ == "__main__":
    app = QApplication(sys.argv)

    with open('style/app_style.qss', 'r') as f:
        style = f.read()
    app.setStyleSheet(style)

    op_controller = OperationsController(CoordinatesTable)

    ui_controller = UIController(op_controller)
    ui_controller.show()

    app.exec()
