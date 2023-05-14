# -*- coding: utf-8 -*-
"""
@author: Gabriel Maccari
"""

from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *


class AppMainWindow(QMainWindow):
    def __init__(self):
        super().__init__(None)

        self.setWindowTitle("xyGeo")
        self.setWindowIcon(QIcon("icons/globe.ico"))
        self.setMaximumSize(370, 500)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)

        # FILE SELECTION -------------------------------------------------------

        self.file_label = QLabel("Selecione uma tabela de coordenadas.")
        self.file_label.setMinimumHeight(22)

        self.open_file_button = QPushButton("Selecionar")
        self.open_file_button.setMaximumWidth(75)
        self.open_file_button.setMinimumHeight(22)
        self.open_file_button.setFlat(True)
        self.open_file_button.setStyleSheet("border-radius: 3px")

        self.file_selection_layout = QHBoxLayout()
        self.file_selection_layout.setSpacing(5)

        self.file_selection_layout.addWidget(self.file_label)
        self.file_selection_layout.addWidget(self.open_file_button)

        # ----------------------------------------------------------------------

        self.separator1 = QFrame(None)
        self.separator1.setLineWidth(1)
        self.separator1.setFrameShape(QFrame.Shape.HLine)
        self.separator1.setFrameShadow(QFrame.Shadow.Sunken)

        # INPUT CRS CONFIG -----------------------------------------------------

        self.input_crs_label = QLabel("SRC de entrada")

        self.input_format_combo = QComboBox(None)
        self.input_format_combo.setMinimumHeight(22)

        self.input_crs_combo = QComboBox(None)
        self.input_crs_combo.setMaximumWidth(350)
        self.input_crs_combo.setMinimumHeight(22)

        self.input_crs_layout = QGridLayout(None)
        self.input_crs_layout.setSpacing(3)

        self.input_crs_layout.addWidget(self.input_crs_label, 0, 0, 1, 10)
        self.input_crs_layout.addWidget(self.input_format_combo, 1, 0, 1, 1)
        self.input_crs_layout.addWidget(self.input_crs_combo, 1, 1, 1, 9)

        # ----------------------------------------------------------------------

        self.separator2 = QFrame(None)
        self.separator2.setLineWidth(1)
        self.separator2.setFrameShape(QFrame.Shape.HLine)
        self.separator2.setFrameShadow(QFrame.Shadow.Sunken)

        # OUTPUT CRS CONFIG ----------------------------------------------------

        self.output_crs_label = QLabel("SRC de saída")

        self.output_format_combo = QComboBox(None)
        self.output_format_combo.setMinimumHeight(22)

        self.output_crs_combo = QComboBox(None)
        self.output_crs_combo.setMaximumWidth(350)
        self.output_crs_combo.setMinimumHeight(22)

        self.output_crs_layout = QGridLayout(None)
        self.output_crs_layout.setSpacing(3)

        self.output_crs_layout.addWidget(self.output_crs_label, 0, 0, 1, 10)
        self.output_crs_layout.addWidget(self.output_format_combo, 1, 0, 1, 1)
        self.output_crs_layout.addWidget(self.output_crs_combo, 1, 1, 1, 9)

        # ----------------------------------------------------------------------

        self.separator3 = QFrame(None)
        self.separator3.setLineWidth(1)
        self.separator3.setFrameShape(QFrame.Shape.HLine)
        self.separator3.setFrameShadow(QFrame.Shadow.Sunken)

        # FIELDS CONFIG --------------------------------------------------------

        self.labels_field_label = QLabel("Rótulos")
        self.labels_field_label.setMinimumHeight(22)

        self.labels_field_combo = QComboBox(None)
        self.labels_field_combo.setMinimumHeight(22)

        self.labels_field_icon = QToolButton(None)
        self.labels_field_icon.setIcon(QIcon("icons/circle.png"))

        self.x_field_label = QLabel("Longitude")
        self.x_field_label.setMinimumHeight(22)

        self.x_field_combo = QComboBox(None)
        self.x_field_combo.setMinimumHeight(22)

        self.x_field_icon = QToolButton(None)
        self.x_field_icon.setIcon(QIcon("icons/circle.png"))

        self.y_field_label = QLabel("Latitude")
        self.y_field_label.setMinimumHeight(22)

        self.y_field_combo = QComboBox(None)
        self.y_field_combo.setMinimumHeight(22)

        self.y_field_icon = QToolButton(None)
        self.y_field_icon.setIcon(QIcon("icons/circle.png"))

        self.fields_layout = QGridLayout(None)
        self.fields_layout.setSpacing(3)

        self.fields_layout.addWidget(self.labels_field_label, 0, 0, 1, 1)
        self.fields_layout.addWidget(self.labels_field_combo, 0, 1, 1, 8)
        self.fields_layout.addWidget(self.labels_field_icon, 0, 9, 1, 1)
        self.fields_layout.addWidget(self.x_field_label, 1, 0, 1, 1)
        self.fields_layout.addWidget(self.x_field_combo, 1, 1, 1, 8)
        self.fields_layout.addWidget(self.x_field_icon, 1, 9, 1, 1)
        self.fields_layout.addWidget(self.y_field_label, 2, 0, 1, 1)
        self.fields_layout.addWidget(self.y_field_combo, 2, 1, 1, 8)
        self.fields_layout.addWidget(self.y_field_icon, 2, 9, 1, 1)

        # ----------------------------------------------------------------------

        self.separator4 = QFrame(None)
        self.separator4.setLineWidth(1)
        self.separator4.setFrameShape(QFrame.Shape.HLine)
        self.separator4.setFrameShadow(QFrame.Shadow.Sunken)

        # REPROJECT BUTTON -----------------------------------------------------

        self.reproject_button = QPushButton("Reprojetar coordenadas")
        self.reproject_button.setMinimumHeight(35)
        self.reproject_button.setFlat(True)
        self.reproject_button.setStyleSheet("border-radius: 3px")

        # COPYRIGHT LABEL ------------------------------------------------------

        self.copyright_label = QLabel("© 2023 Gabriel Maccari / Icons by www.icons8.com")
        self.copyright_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.copyright_label.setStyleSheet("font-size: 7.5pt")
        self.copyright_label.setMaximumHeight(15)

        # ----------------------------------------------------------------------

        main_layout.addLayout(self.file_selection_layout)
        main_layout.addWidget(self.separator1)
        main_layout.addLayout(self.input_crs_layout)
        main_layout.addWidget(self.separator2)
        main_layout.addLayout(self.output_crs_layout)
        main_layout.addWidget(self.separator3)
        main_layout.addLayout(self.fields_layout)
        main_layout.addWidget(self.separator4)
        main_layout.addWidget(self.reproject_button)
        main_layout.addWidget(self.copyright_label)

        widget = QWidget(self)
        widget.setLayout(main_layout)
        self.setCentralWidget(widget)
