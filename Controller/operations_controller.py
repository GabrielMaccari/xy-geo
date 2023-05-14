# -*- coding: utf-8 -*-
"""
@author: Gabriel Maccari
"""

import pandas
import numpy
import re
import pyproj
from csv import Sniffer
from PyQt6.QtWidgets import QInputDialog

geographic_crs_dict = {}
for crs in pyproj.database.query_crs_info(pj_types='GEOGRAPHIC_2D_CRS'):
    key = f"{crs.name} ({crs.auth_name}:{crs.code})"
    geographic_crs_dict[key] = {
        "name": crs.name,
        "auth_name": crs.auth_name,
        "code": crs.code
    }

projected_crs_dict = {}
for crs in pyproj.database.query_crs_info(pj_types='PROJECTED_CRS'):
    key = f"{crs.name} ({crs.auth_name}:{crs.code})"
    projected_crs_dict[key] = {
        "name": crs.name,
        "auth_name": crs.auth_name,
        "code": crs.code
    }


class OperationsController:
    def __init__(self, model_class):
        self.table_class = model_class
        self.input_table = None
        self.output_table = None

    def read_file(self, path: str):
        # Arquivo csv
        if path.endswith(".csv"):
            data = open(path, "r").read(4096)
            sep = str(Sniffer().sniff(data).delimiter)
            df = pandas.read_csv(path, delimiter=sep)
        # Arquivo xlsx, xlsm ou ods
        else:
            engine = ("odf" if path.endswith(".ods") else "openpyxl")
            excel_file = pandas.ExcelFile(path, engine=engine)
            sheets = excel_file.sheet_names
            # Se houver mais de 1 aba, o usuário seleciona uma delas
            if len(sheets) > 1:
                sheet, ok = QInputDialog.getItem(None, "Selecionar aba",
                                                 "Selecione a planilha que contém as coordenadas dos pontos:", sheets,
                                                 editable=False)
                if not ok:
                    return False
            else:
                sheet = 0
            df = excel_file.parse(sheet_name=sheet)

        df.columns = df.columns.astype(str)

        self.create_model_instance(df)

        return True

    def create_model_instance(self, df, io = "input"):
        if io == "input":
            self.input_table = None
            self.input_table = self.table_class(df)
        else:
            self.output_table = None
            self.output_table = self.table_class(df)

    def get_column_list(self):
        return self.input_table.df.columns.to_list()

    def select_coord_column(self, axis: str) -> str | None:
        options = self.get_column_list()
        if axis == "y":
            common_names = ("latitude", "lat", "northing", "utm_n", "utmn", "n", "y", "utmn (m)")
        elif axis == "x":
            common_names = ("longitude", "lon", "easting", "utm_e", "utme", "e", "x", "utme (m)")
        else:
            raise Exception('Expected "y" or "x" for axis')

        for col in options:
            if str(col).lower() in common_names:
                return col

        return None

    def filter_valid_coord_columns(self, coord_format):
        df = self.input_table.df

        y_columns, x_columns = [], []

        if coord_format == "GMS":
            y_pattern = re.compile(r"^(\d{1,2})([°º])(\d{1,2})(['’])(\d{1,2}([.,]\d+)?)([\"”])([NS])$")
            x_pattern = re.compile(r"^(\d{1,3})([°º])(\d{1,2})(['’])(\d{1,2}([.,]\d+)?)([\"”])([EWOL])$")

            for c in df.columns:
                rows = df[c].values
                y_ok, x_ok = True, True

                for value in rows:
                    if y_pattern.match(str(value)) is None:
                        y_ok = False
                    if x_pattern.match(str(value)) is None:
                        x_ok = False

                    if not y_ok and not x_ok:
                        continue

                    parts = re.split(r'[^\d\w]+', value)
                    degrees = int(parts[0])
                    minutes = int(parts[1])
                    seconds = float(f"{parts[2]}.{parts[3]}" if parts[3].isdigit() else parts[2])

                    if degrees > 180:
                        x_ok = False
                    elif degrees > 90:
                        y_ok = False

                    if minutes > 60 or seconds > 60:
                        x_ok, y_ok = False, False

                if y_ok:
                    y_columns.append(c)
                if x_ok:
                    x_columns.append(c)

        else:
            if coord_format == 'GD':
                y_min, y_max, x_min, x_max = -90, 90, -180, 180
                # x_min, y_min, x_max, y_max = crs.area_of_use.bounds
            else:
                y_min, y_max, x_min, x_max = 1099000, 10000000, 165000, 835000

            for c in df.columns:
                y_ok, x_ok = True, True

                try:
                    df[c] = df[c].replace(",", ".", regex=True).astype(float, errors='raise')
                except (ValueError, TypeError):
                    continue

                if not df[c].dropna().between(y_min, y_max).all() or df[c].dropna().empty:
                    y_ok = False
                if not df[c].dropna().between(x_min, x_max).all() or df[c].dropna().empty:
                    x_ok = False

                if y_ok:
                    y_columns.append(c)
                if x_ok:
                    x_columns.append(c)

        return x_columns, y_columns

    def manage_conversion(self, input_format, output_format, input_crs_key, output_crs_key,
                          label_field, y_field, x_field):
        input_df = self.input_table.df

        # Cria o DataFrame e preenche o campo de identificação dos pontos
        output_df = pandas.DataFrame()
        output_df["rotulo"] = input_df[label_field]
        output_df = output_df.set_index("rotulo")

        # Seleciona o nome das colunas de coordenadas conforme o formato de entrada
        column_names = {"GD": ["latitude", "longitude"],
                        "GMS": ["latitude", "longitude"],
                        "UTM": ["northing", "easting"]}
        y_col = column_names[output_format][0]
        x_col = column_names[output_format][1]

        # Obtém a autoridade e código dos SRCs de entrada e saída
        crs_dt = projected_crs_dict if input_format == "UTM" else geographic_crs_dict
        input_auth = crs_dt[input_crs_key]["auth_name"]
        input_code = crs_dt[input_crs_key]["code"]

        crs_dt = projected_crs_dict if output_format == "UTM" else geographic_crs_dict
        output_auth = crs_dt[output_crs_key]["auth_name"]
        output_code = crs_dt[output_crs_key]["code"]

        # Define os SRCs
        input_crs = pyproj.CRS.from_authority(input_auth, input_code)
        output_crs = pyproj.CRS.from_authority(output_auth, output_code)

        # Caso as coordenadas de entrada estejam em GMS, converte elas para DD
        if input_format == "GMS":
            input_df[y_field], input_df[x_field] = self.reformat_dms_to_dd(input_df[y_field], input_df[x_field])

        # Reprojeta as coordenadas entre SRCs
        output_df[y_col], output_df[x_col] = self.reproject(input_df[y_field], input_df[x_field],
                                                            input_crs, output_crs,
                                                            input_format, output_format)

        # Caso a saída seja em GMS, converte os DD reprojetados para GMS
        if output_format == "GMS":
            output_df[y_col], output_df[x_col] = self.reformat_DD_to_DMS(output_df[y_col], output_df[x_col])

        # Anexa uma coluna com o nome do SRC de saída
        output_df["src"] = output_crs.name

        # Salva o DataFrame em um atributo
        self.create_model_instance(output_df, "output")
        self.output_table.crs = output_crs_key
        self.output_table.x_column = x_col
        self.output_table.y_column = y_col

    def reformat_dms_to_dd(self, y, x):
        def dms_to_decimal(dms):
            parts = re.split(r"°|º|'|’|\"|”", dms)
            d, m, s = int(parts[0]), int(parts[1]), float(parts[2].replace(",","."))
            direction = parts[3]

            dd = d + (m / 60) + (s / 3600)

            if direction in ["S", "W", "O"]:
                dd *= -1

            return dd

        y_dd = y.apply(dms_to_decimal)
        x_dd = x.apply(dms_to_decimal)

        return y_dd, x_dd

    def reproject(self, input_y, input_x, input_crs, output_crs, input_format, output_format):
        transformer = pyproj.Transformer.from_crs(input_crs, output_crs)

        output_y, output_x = [], []
        for old_y, old_x in zip(input_y, input_x):
            try:
                if input_format in ["GD","GMS"] and output_format == "UTM":
                    new_x, new_y = transformer.transform(old_y, old_x)
                elif input_format in ["GD","GMS"] and output_format in ["GD","GMS"]:
                    new_y, new_x = transformer.transform(old_y, old_x)
                elif input_format == "UTM" and output_format in ["GD","GMS"]:
                    new_y, new_x = transformer.transform(old_x, old_y)
                elif input_format == "UTM" and output_format == "UTM":
                    new_x, new_y = transformer.transform(old_x, old_y)
                else:
                    raise Exception("Unknown input/output combination for reprojection")

                if new_x == numpy.inf or new_y == numpy.inf:
                    raise TypeError(f"Invalid coordinate output (X: {new_x} / Y: {new_y})")

                output_y.append(new_y)
                output_x.append(new_x)

            except TypeError:
                output_y.append(pandas.NA)
                output_x.append(pandas.NA)

        return output_y, output_x

    def reformat_DD_to_DMS(self, y, x):
        def decimal_to_dms(dd, axis="y"):
            d = int(abs(dd))
            md = (abs(dd) - d) * 60
            m = int(md)
            s = (md - m) * 60
            if dd >= 0:
                direction = "N" if axis == "y" else "E"
            else:
                direction = "S" if axis == "y" else "W"

            return f"{d:0>2}°{m:0>2}'{s:07.4f}\"{direction}".replace(".",",")

        y_dms = y.apply(decimal_to_dms, axis="y")
        x_dms = x.apply(decimal_to_dms, axis="x")

        return y_dms, x_dms

    def save_file(self, path):
        df = self.output_table.df
        if path.endswith(".csv"):
            df.to_csv(path, decimal=",", sep=";")
        elif path.endswith(".ods"):
            df.to_excel(path, engine="odf")
        else:
            df.to_excel(path, engine="openpyxl")
