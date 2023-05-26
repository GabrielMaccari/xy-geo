from PyQt6.QtWidgets import *
from PyQt6.QtGui import *

from View.main_window import AppMainWindow
from Controller.operations_controller import geographic_crs_dict, projected_crs_dict

CRS_FORMATS = ("GD", "UTM", "GMS")
CRS_FORMATS_TOOLTIP = ("GD: Graus decimais (latitude e longitude)\n"
                       "UTM: Projeção Universal de Mercator (northing e easting)\n"
                       "GMS: Graus, minutos e segundos (latitude e longitude)")
DEFAULT_UTM_CRS = "SIRGAS 2000 / UTM zone 22S (EPSG:31982)"
DEFAULT_GEO_CRS = "SIRGAS 2000 (EPSG:4674)"


class UIController(AppMainWindow):
    def __init__(self, operations_controller):
        super().__init__()

        self.op_controller = operations_controller
        self.valid_x_columns, self.valid_y_columns = [], []
        self.columns_ok = [False, False]

        self.utm_crs_list = sorted(list(projected_crs_dict.keys()), key=lambda x: projected_crs_dict[x]['name'])
        self.geo_crs_list = sorted(list(geographic_crs_dict.keys()), key=lambda x: geographic_crs_dict[x]['name'])

        self.input_format_combo.addItems(CRS_FORMATS)
        self.input_format_combo.setCurrentText("GD")
        self.input_format_combo.setToolTip(CRS_FORMATS_TOOLTIP)

        self.input_crs_combo.addItems(self.geo_crs_list)
        self.input_crs_combo.setCurrentText(DEFAULT_GEO_CRS)

        self.output_format_combo.addItems(CRS_FORMATS)
        self.output_format_combo.setCurrentText("UTM")
        self.output_format_combo.setToolTip(CRS_FORMATS_TOOLTIP)

        self.output_crs_combo.addItems(self.utm_crs_list)
        self.output_crs_combo.setCurrentText(DEFAULT_UTM_CRS)

        self.open_file_button.clicked.connect(self.open_file_button_clicked)
        self.input_format_combo.currentTextChanged.connect(lambda: self.coord_format_selected("input"))
        self.output_format_combo.currentTextChanged.connect(lambda: self.coord_format_selected("output"))
        self.labels_field_combo.currentTextChanged.connect(lambda: self.field_selected("labels"))
        self.x_field_combo.currentTextChanged.connect(lambda: self.field_selected("x"))
        self.y_field_combo.currentTextChanged.connect(lambda: self.field_selected("y"))
        self.reproject_button.clicked.connect(self.reproject_button_clicked)

        self.enable_widgets(["settings", "reproject"], False)

    def enable_widgets(self, sections: list[str], enable: bool = True):
        if "settings" in sections:
            self.input_crs_label.setEnabled(enable)
            self.input_format_combo.setEnabled(enable)
            self.input_crs_combo.setEnabled(enable)

            self.output_crs_label.setEnabled(enable)
            self.output_format_combo.setEnabled(enable)
            self.output_crs_combo.setEnabled(enable)

            self.labels_field_label.setEnabled(enable)
            self.labels_field_combo.setEnabled(enable)
            self.labels_field_icon.setEnabled(enable)

            self.x_field_label.setEnabled(enable)
            self.x_field_combo.setEnabled(enable)
            self.x_field_icon.setEnabled(enable)

            self.y_field_label.setEnabled(enable)
            self.y_field_combo.setEnabled(enable)
            self.y_field_icon.setEnabled(enable)

        if "reproject" in sections:
            self.reproject_button.setEnabled(enable)

    def open_file_button_clicked(self):
        try:
            # Abre uma janela de seleção de arquivo
            path = show_file_dialog(
                caption="Selecione uma tabela contendo os dados de entrada.",
                extension_filter=("Pasta de trabalho do Excel (*.xlsx);;"
                                  "Pasta de trabalho habilitada para macro do Excel (*.xlsm);;"
                                  "Open Document Spreadsheet (*.ods);;"
                                  "CSV (*.csv)"),
                mode="open", parent=self
            )

            # Se nenhum arquivo foi selecionado, retorna
            if path == "":
                return

            # Lê o arquivo
            new_file_opened = self.op_controller.read_file(path)

            # Se o arquivo não pôde ser lido, retorna
            if not new_file_opened:
                return

            # Atualiza a label de arquivo com o nome do arquivo selecionado
            path_parts = path.split("/")
            self.file_label.setText(path_parts[-1])

            # Preenche as comboboxes de campos com as colunas da tabela
            column_list = self.op_controller.get_column_list()
            combo_boxes = [self.labels_field_combo, self.x_field_combo, self.y_field_combo]
            for box in combo_boxes:
                box.clear()
                box.addItems(column_list)

            # Habilita os widgets da interface
            self.enable_widgets(["settings"], True)

            # Chama o slot de seleção de formato para atualizar toda a interface
            self.coord_format_selected("input")

        except Exception as exception:
            show_popup(f"ERRO: {exception}", "error", self)

    def coord_format_selected(self, input_or_output: str):
        try:
            # Seleciona as combo boxes
            format_combo = self.input_format_combo if input_or_output == "input" else self.output_format_combo
            crs_combo = self.input_crs_combo if input_or_output == "input" else self.output_crs_combo

            # Limpa as opções de CRS e insere novas
            crs_options = self.utm_crs_list if format_combo.currentText() == "UTM" else self.geo_crs_list
            if crs_combo.currentText() not in crs_options:
                crs_combo.clear()
                crs_combo.addItems(crs_options)
                crs_combo.setCurrentText(DEFAULT_UTM_CRS if format_combo.currentText() == "UTM" else DEFAULT_GEO_CRS)

            if input_or_output == "input":
                # Muda as labels dos campos de coordenadas
                x_label = "Easting" if self.input_format_combo.currentText() == "UTM" else "Longitude"
                y_label = "Northing" if self.input_format_combo.currentText() == "UTM" else "Latitude"
                self.x_field_label.setText(x_label)
                self.y_field_label.setText(y_label)

                # Obtém uma lista das colunas válidas para coordenadas
                coord_format = self.input_format_combo.currentText()
                self.valid_x_columns, self.valid_y_columns = self.op_controller.filter_valid_coord_columns(coord_format)

                # Seleciona as prováveis colunas de coordenadas nas combo boxes com base no nome
                self.select_probable_coord_columns()
                for f in ["labels","x","y"]:
                    self.field_selected(f)
        except Exception as exception:
            show_popup(f"ERRO: {exception}", "error", self)

    def field_selected(self, field: str):
        try:
            combo_boxes = {
                "labels": self.labels_field_combo,
                "x": self.x_field_combo,
                "y": self.y_field_combo
            }
            status_icons = {
                "labels": self.labels_field_icon,
                "x": self.x_field_icon,
                "y": self.y_field_icon
            }

            # Seleciona os widgets relativos ao campo selecionado
            field_box = combo_boxes[field]
            status_icon = status_icons[field]

            # Caso seja o campo das labels, vale qualquer coisa
            if field == "labels":
                status_icon.setIcon(QIcon("icons/ok.png"))
                return

            # Se a coluna selecionada estiver na lista de colunas válidas, ícone verde, senão ícone vermelho
            valid_cols = self.valid_x_columns if field == "x" else self.valid_y_columns
            status_icon.setIcon(QIcon("icons/ok.png" if field_box.currentText() in valid_cols else "icons/not_ok.png"))

            i = 0 if field == "x" else 1
            self.columns_ok[i] = field_box.currentText() in valid_cols

            self.enable_widgets(["reproject"], self.columns_ok[0] and self.columns_ok[1])
        except Exception as exception:
            show_popup(f"ERRO: {exception}", "error", self)

    def reproject_button_clicked(self):
        try:
            input_format = self.input_format_combo.currentText()
            output_format = self.output_format_combo.currentText()
            input_crs_key = self.input_crs_combo.currentText()
            output_crs_key = self.output_crs_combo.currentText()
            label_field = self.labels_field_combo.currentText()
            y_field = self.y_field_combo.currentText()
            x_field = self.x_field_combo.currentText()

            self.op_controller.manage_conversion(input_format, output_format, input_crs_key, output_crs_key,
                                                 label_field, y_field, x_field)

            save_path = show_file_dialog(caption="Salvar tabela",
                                         extension_filter=("Pasta de trabalho do Excel (*.xlsx);;"
                                                           "Pasta de trabalho habilitada para macro do Excel (*.xlsm);;"
                                                           "Open Document Spreadsheet (*.ods);;"
                                                           "CSV (*.csv)"),
                                         mode="save", parent=self)

            if save_path == "":
                return

            self.op_controller.save_file(save_path)

            show_popup("Arquivo salvo com sucesso!", parent=self)

        except Exception as exception:
            show_popup(f"ERRO: {exception}", "error", self)

    def select_probable_coord_columns(self):
        probable_x_column = self.op_controller.select_coord_column("x")
        probable_y_column = self.op_controller.select_coord_column("y")
        self.x_field_combo.setCurrentText(probable_x_column)
        self.y_field_combo.setCurrentText(probable_y_column)


def show_popup(message: str, msg_type: str = "notification", parent: QMainWindow = None):
    """
    Exibe uma mensagem em popup.
    :param message: Conteúdo da popup.
    :param msg_type: "notification" ou "error". Define o ícone a ser exibido.
    :param parent: A janela pai.
    :return: Nada.
    """
    popup_types = {
        "notification": {"title": "Notificação", "icon": "icons/info.png"},
        "error":        {"title": "Erro",        "icon": "icons/error.png"}
    }
    title = popup_types[msg_type]["title"]
    icon = QIcon(popup_types[msg_type]["icon"])

    popup = QMessageBox(parent)
    popup.setText(message)
    popup.setWindowTitle(title)
    popup.setWindowIcon(icon)

    popup.exec()


def show_file_dialog(caption: str, extension_filter: str, mode: str = "open", parent: QMainWindow = None) -> str:
    """
    Exibe um diálogo de abertura/salvamento de arquivo.
    :param caption: Título do diálogo.
    :param extension_filter: Filtro de extensões de arquivo.
    :param mode: "open" ou "save".
    :param parent: Janela pai.
    :return: Caminho completo do arquivo (str).
    """
    if mode == "open":
        file_name, file_type = QFileDialog.getOpenFileName(parent, caption=caption, filter=extension_filter)
    else:
        file_name, file_type = QFileDialog.getSaveFileName(parent, caption=caption, filter=extension_filter)

    return file_name
