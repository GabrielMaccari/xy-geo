# -*- coding: utf-8 -*-
"""
Created on Mon Sep 26 18:31:49 2022

@author: gabri
"""
from PyQt6.QtWidgets import QMainWindow, QApplication, QInputDialog, QPushButton, QLabel, QTableWidget, QTableWidgetItem, QComboBox, QFileDialog, QMessageBox, QFrame
from PyQt6.QtGui import QIcon, QFont
from pyproj.database import query_crs_info
from sys import argv as sys_argv
from os import getcwd as os_getcwd
import pandas
import numpy
import re
from pyproj import Transformer

class XYConverterApp(QMainWindow):
    def __init__(self):
        
        super().__init__()
        
        self.setWindowTitle('XY Converter')
        self.setWindowIcon(QIcon('icons/globe.ico'))
        
        #Variáveis gerais
        self.folder = os_getcwd()
        self.fileOpened = False
        self.fileDF = None
        self.interfaceDF = None
        self.UTM_CRS_dt = {}
        self.geographic_CRS_dt = {}
        self.format_options = {}
        
        #Coleta dois dicionários de sistemas de referência de coordenadas (uma de SRCs projetados e outra de SRCs geográficos)
        #Cada dicionário contém o nome do SRC e seu código EPSG ('SRC_name':EPSG)
        utm_crs_data = query_crs_info(pj_types='PROJECTED_CRS')  #pyproj.database.query_crs_info()
        geo_crs_data = query_crs_info(pj_types='GEOGRAPHIC_2D_CRS')
        for info in utm_crs_data:
            if info.auth_name=='EPSG':
                self.UTM_CRS_dt[info.name] = int(info.code)
        for info in geo_crs_data:
            if info.auth_name=='EPSG':
                self.geographic_CRS_dt[info.name] = int(info.code)
                
        #Opções de formatos de coordenadas
        self.format_options = {'Projetado (UTM)': 
                                   {'headings':['Northing','Easting'], 
                                    'example':'720366', 
                                    'crs_dict':self.UTM_CRS_dt},
                               'Geográfico (GD)': 
                                   {'headings':['Latitude','Longitude'], 
                                    'example':'-27,1952', 
                                    'crs_dict':self.geographic_CRS_dt},
                               'Geográfico (GMS)':
                                   {'headings':['Latitude','Longitude'], 
                                    'example':'27°11\'42,556"S', 
                                    'crs_dict':self.geographic_CRS_dt}}
            
        #Limites das coordenadas
        self.coordinate_ranges = {
            'Projetado (UTM)': {'y_max':10000000, 'y_min':1099000, 'x_max':835000, 'x_min':165000},
            'Geográfico (GD)': {'y_max':90, 'y_min':-90, 'x_max':180, 'x_min':-180},
            'Geográfico (GMS)': {'y_max':None, 'y_min':None, 'x_max':None, 'x_min':None}
            }
        
        #Interface
        x, y, h = 5, 5, 22
        self.file_lbl = QLabel('Selecione uma tabela contendo os dados de entrada.', self)
        self.file_lbl.setGeometry(x, y, 310, h)
        self.file_btn = QPushButton('Selecionar', self)
        self.file_btn.setGeometry(x+310, y, 95, h)
        self.file_btn.clicked.connect(self.open_file_button_clicked)
        
        y+=30
        self.line1 = QFrame(self)
        self.line1.setGeometry(5, y, 405, 3)
        self.line1.setLineWidth(1)
        self.line1.setFrameShape(QFrame.Shape.HLine)
        self.line1.setFrameShadow(QFrame.Shadow.Sunken)
        
        y, h, w1, w2, w3 = y+10, 22, 85, 120, 190
        self.inputCRS_lbl = QLabel('SRC de entrada:', self)
        self.inputCRS_lbl.setGeometry(x, y, w1, h)
        
        self.inputCRStype_cbx = QComboBox(self)
        self.inputCRStype_cbx.setGeometry(x+w1+5, y, w2, h)
        self.inputCRStype_cbx.addItems(self.format_options.keys())
        self.inputCRStype_cbx.setCurrentText('Geográfico (GD)')
        self.inputCRStype_cbx.currentTextChanged.connect(lambda: self.CRS_type_selected('input'))
        
        self.inputCRS_cbx = QComboBox(self)
        self.inputCRS_cbx.setGeometry(x+w1+5+w2+5, y, w3, h)
        self.inputCRS_cbx.addItems(sorted(self.geographic_CRS_dt.keys()))
        self.inputCRS_cbx.setCurrentText('SIRGAS 2000')
        
        y, h = y+h+1, 15
        self.inputFormatExample_lbl = QLabel('Ex:  '+self.format_options['Geográfico (GD)']['example'], self)
        self.inputFormatExample_lbl.setGeometry(x+w1+5+w2+10, y, 100, h)
        
        y, h, w1, w2, w3 = y+h+5, 22, 85, 120, 190
        self.outputCRS_lbl = QLabel('SRC de saída:', self)
        self.outputCRS_lbl.setGeometry(x, y, w1, h)
        
        self.outputCRStype_cbx = QComboBox(self)
        self.outputCRStype_cbx.setGeometry(x+w1+5, y, w2, h)
        self.outputCRStype_cbx.addItems(self.format_options.keys())
        self.outputCRStype_cbx.setCurrentText('Projetado (UTM)')
        self.outputCRStype_cbx.currentTextChanged.connect(lambda: self.CRS_type_selected('output'))
        
        self.outputCRS_cbx = QComboBox(self)
        self.outputCRS_cbx.setGeometry(x+w1+5+w2+5, y, w3, h)
        self.outputCRS_cbx.addItems(sorted(self.UTM_CRS_dt.keys()))
        self.outputCRS_cbx.setCurrentText('SIRGAS 2000 / UTM zone 22S')
        
        y, h = y+h+1, 15
        self.outputFormatExample_lbl = QLabel('Ex:  '+self.format_options['Projetado (UTM)']['example'], self)
        self.outputFormatExample_lbl.setGeometry(x+w1+5+w2+10, y, 100, h)
        
        y = y+h+5
        self.line2 = QFrame(self)
        self.line2.setGeometry(5, y, 405, 3)
        self.line2.setLineWidth(1)
        self.line2.setFrameShape(QFrame.Shape.HLine)
        self.line2.setFrameShadow(QFrame.Shadow.Sunken)
        
        w1, w2 = 60, 340
        y, h = y+10, 22
        self.yColumn_lbl = QLabel('Latitude:', self)
        self.yColumn_lbl.setGeometry(x, y, w1, h)
        self.yColumn_lbl.setEnabled(False)
        
        self.yColumn_cbx = QComboBox(self)
        self.yColumn_cbx.setGeometry(x+w1+5, y, w2, h)
        self.yColumn_cbx.setEnabled(False)
        self.yColumn_cbx.currentTextChanged.connect(lambda: self.yx_column_selected('y'))
        
        y, h = y+h+5, 22
        self.xColumn_lbl = QLabel('Longitude:', self)
        self.xColumn_lbl.setGeometry(x, y, w1, h)
        self.xColumn_lbl.setEnabled(False)
        
        self.xColumn_cbx = QComboBox(self)
        self.xColumn_cbx.setGeometry(x+w1+5, y, w2, h)
        self.xColumn_cbx.setEnabled(False)
        self.xColumn_cbx.currentTextChanged.connect(lambda: self.yx_column_selected('x'))
        
        y, h, w = y+h+10, 250, 370
        
        self.coordinates_tbl = QTableWidget(self)
        self.coordinates_tbl.setGeometry(x, y, w, h)
        self.coordinates_tbl.setColumnCount(2)
        self.coordinates_tbl.setColumnWidth(0, 183)
        self.coordinates_tbl.setColumnWidth(1, 183)
        self.coordinates_tbl.setHorizontalHeaderLabels(self.format_options['Geográfico (GD)']['headings'])
        self.coordinates_tbl.itemChanged.connect(self.check_table_data)
        
        y2, wh = y, 30
        self.addRow_btn = QPushButton('', self)
        self.addRow_btn.setGeometry(w+10, y-1, wh, wh)
        self.addRow_btn.setIcon(QIcon('icons/add.png'))
        self.addRow_btn.setToolTip('Adicionar uma linha')
        self.addRow_btn.clicked.connect(self.add_row)
        
        y2+=35
        self.deleteRow_btn = QPushButton('', self)
        self.deleteRow_btn.setGeometry(w+10, y2, wh, wh)
        self.deleteRow_btn.setIcon(QIcon('icons/delete.png'))
        self.deleteRow_btn.setToolTip('Remover linha selecionada')
        self.deleteRow_btn.clicked.connect(self.delete_row)
        
        y2+=35
        self.clear_btn = QPushButton('', self)
        self.clear_btn.setGeometry(w+10, y2, wh, wh)
        self.clear_btn.setIcon(QIcon('icons/clear.png'))
        self.clear_btn.setToolTip('Remover todas as linhas')
        self.clear_btn.clicked.connect(self.clear_table)
        
        y2+=35
        self.reset_btn = QPushButton('', self)
        self.reset_btn.setGeometry(w+10, y2, wh, wh)
        self.reset_btn.setIcon(QIcon('icons/refresh.png'))
        self.reset_btn.setToolTip('Reiniciar a tabela com os dados do arquivo carregado')
        self.reset_btn.clicked.connect(self.refresh_table)
        self.reset_btn.setEnabled(False)
        
        y, h = y+h+5, 40
        self.convert_btn = QPushButton('Converter', self)
        self.convert_btn.setGeometry(x, y, 405, h)
        self.convert_btn.setEnabled(False)
        self.convert_btn.clicked.connect(self.manage_conversion)
        
        y, h = y+h, 20
        self.copyrightLabel = QLabel('© 2022 Gabriel Maccari <gabriel.maccari@hotmail.com>', self)
        self.copyrightLabel.setGeometry(5, y, 340, h)
        self.copyrightLabel.setFont(QFont('Sans Serif', 8))
        
        y+=h
        self.setMinimumSize(415, y)
        self.setMaximumSize(415, y)
    
    
    def open_file_button_clicked(self):
        """Exibe um diálogo para seleção de um arquivo (xlsx, xlsm, csv, ods) e cria um DataFrame (StereographerApp.file) para conter os dados de entrada. Elimina linhas e colunas em branco no DataFrame."""
        
        self.fileOpened = False
        #Abre um diálogo para seleção do arquivo. Os formatos suportados são xlsx, xlsm, csv e ods
        try:
            inFile = QFileDialog.getOpenFileName(self, caption='Selecione uma tabela contendo os dados de entrada.', directory=self.folder, filter='Formatos suportados (*.xlsx *.xlsm *.csv *.ods);;Pasta de Trabalho do Excel (*.xlsx);;Pasta de Trabalho Habilitada para Macro do Excel (*.xlsm);;CSV (*.csv);; OpenDocument Spreadsheet (*.ods)')
        #Se não der para abrir o arquivo, mostra uma mensagem com o erro
        except Exception as e:
            msg = QMessageBox(parent=self, text='Não foi possível abrir o arquivo selecionado.\n\nERRO: %s' % (str(e)))
            msg.setWindowTitle('Erro')
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.exec()
        
        path = inFile[0]
        
        #Se algum arquivo tiver sido selecionado com sucesso
        if path != '':
            try:
                #Cria um dataframe a partir de um arquivo csv
                if path.endswith('.csv'):
                    file = pandas.read_csv(path, decimal=',', delimiter=';')
                    self.fileOpened = True
                #Cria um dataframe a partir de um arquivo xlsx, xlsm ou ods
                else:
                    #Engine odf para arquivos ods e openpyxl para arquivos do excel
                    eng=('odf' if path.endswith('.ods') else 'openpyxl')
                    wholeFile = pandas.ExcelFile(path, engine=eng)
                    sheetNames = wholeFile.sheet_names
                    #Caso o arquivo tenha mais de uma planilha, mostra um diálogo com uma comboBox para selecionar a planilha dos dados
                    if len(sheetNames) > 1:
                        sheet, ok = QInputDialog.getItem(self, 'Selecionar aba', 'Planilha:', sheetNames)
                        #Se o usuário apertar ok no diálogo, cria o dataframe a partir da planilha selecionada
                        if ok:
                            file = wholeFile.parse(sheet_name=sheet)
                        #Caso o usuário aperte em cancelar ou fechar o diálogo, cancela a leitura do arquivo
                        else:
                            return
                    #Se o arquivo tiver apenas uma planilha, cria o dataframe com ela
                    else:
                        file = pandas.read_excel(path, engine=eng)
                    
                    file.columns = file.columns.astype(str)
                    
                    #Remove colunas e linhas em branco
                    remove_cols = [col for col in file.columns if 'Unnamed' in col]
                    file.drop(remove_cols, axis='columns', inplace=True)
                    file.replace(r'^\s*$', numpy.nan, inplace=True, regex=True)
                    file.dropna(how='all', axis='index', inplace=True)
                    
                    self.fileOpened = True
                    
            #Caso ocorra algum erro na leitura do arquivo, exibe uma mensagem com o erro e esvazia as combo boxes
            except Exception as e:
                self.fileOpened = False
                msg = QMessageBox(parent=self, text='Não foi possível abrir o arquivo.\n\n'+str(e))
                msg.setWindowTitle('Erro')
                msg.setIcon(QMessageBox.Icon.Critical)
                msg.exec()
                self.file_lbl.setText('Não foi possível abrir o arquivo.')
                self.file_lbl.setStyleSheet('QLabel {color: red}')
                self.yColumn_lbl.setEnabled(False)
                self.yColumn_cbx.setEnabled(False)
                self.xColumn_lbl.setEnabled(False)
                self.xColumn_cbx.setEnabled(False)
                self.reset_btn.setEnabled(False)
        
        #Instruções a serem seguidas quando um arquivo é aberto e o DataFrame é criado com sucesso
        if self.fileOpened:
            self.fileDF = file
            self.file_lbl.setText('Arquivo carregado com sucesso.')
            self.file_lbl.setStyleSheet('QLabel {color: green}')
            
            self.yColumn_lbl.setEnabled(True)
            self.yColumn_cbx.setEnabled(True)
            self.xColumn_lbl.setEnabled(True)
            self.xColumn_cbx.setEnabled(True)
            
            self.reset_btn.setEnabled(True)
            
            self.update_coordinate_column_boxes()


    def CRS_type_selected(self, in_or_out):
        try:
            if in_or_out=='input':
                CRStype_cbx = self.inputCRStype_cbx
                CRS_cbx = self.inputCRS_cbx
                example_lbl = self.inputFormatExample_lbl
            elif in_or_out=='output':
                CRStype_cbx = self.outputCRStype_cbx
                CRS_cbx = self.outputCRS_cbx
                example_lbl = self.outputFormatExample_lbl
            else:
                return
            
            crs_type = CRStype_cbx.currentText()
            selected_crs = CRS_cbx.currentText()
            
            #Atualiza as combo boxes de SRC com os SRCs do tipo selecionado
            crs_dict = self.UTM_CRS_dt if crs_type=='Projetado (UTM)' else self.geographic_CRS_dt
            CRS_cbx.clear()
            CRS_cbx.addItems(sorted(crs_dict.keys()))
            if selected_crs in crs_dict.keys(): CRS_cbx.setCurrentText(selected_crs)
            
            #Atualiza os exemplos de formato das coordenadas
            example_lbl.setText('Ex:  ' + self.format_options[crs_type]['example'])
            
            #Atualiza as labels da seleção de colunas
            self.yColumn_lbl.setText(self.format_options[crs_type]['headings'][0]+':')
            self.xColumn_lbl.setText(self.format_options[crs_type]['headings'][1]+':')
            
            #Atualiza os cabeçalhos da tabela com o tipo de coordenada do tipo de SRC selecionado
            if in_or_out=='input':
                self.coordinates_tbl.setHorizontalHeaderLabels(self.format_options[crs_type]['headings'])
            
            #Se houver um arquivo aberto, atualiza as combo boxes de colunas das coordenadas
            if self.fileOpened and crs_type:
                self.update_coordinate_column_boxes()
        except Exception as e:
            msg = QMessageBox(parent=self, text='Ocorreu um erro ao atualizar a interface.\n\n'+str(e))
            msg.setWindowTitle('Erro')
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.exec()
          
            
    def update_coordinate_column_boxes(self):
        try:
            y_columns, x_columns = self.filter_coordinate_columns(self.fileDF, self.inputCRStype_cbx.currentText())
            
            self.yColumn_cbx.clear()
            self.xColumn_cbx.clear()
            self.yColumn_cbx.addItems(y_columns)
            self.xColumn_cbx.addItems(x_columns)
            
            #Troca a coluna selecionada na combo box de X para o segundo item da lista (só para não ficar com as 2 combo boxes iguais ao filtrar as colunas)
            if len(x_columns)>1: 
                self.xColumn_cbx.setCurrentIndex(1)
        except Exception as e:
            msg = QMessageBox(parent=self, text='Ocorreu um erro ao atualizar os campos de coordenadas na interface.\n\n'+str(e))
            msg.setWindowTitle('Erro')
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.exec()
    
    
    def filter_coordinate_columns(self, DF, crs_type):
        try:
            y_columns, x_columns = [], []
            
            if crs_type=='Geográfico (GMS)':
                NS_pattern = re.compile('[0-9]{1,2}°[0-9]{1,2}\'[0-9]{1,2},[0-9]{0,20}"[NS]')
                WE_pattern = re.compile('[0-9]{1,2}°[0-9]{1,2}\'[0-9]{1,2},[0-9]{0,20}"[WEOL]')
                
                for c in DF.columns:
                    rows = DF[c].values
                    N_ok, E_ok = True, True
                    
                    for i in rows:
                        if NS_pattern.match(str(i)) == None:
                            N_ok = False
                        if WE_pattern.match(str(i)) == None:
                            E_ok = False
                    
                    if N_ok: y_columns.append(c)
                    if E_ok: x_columns.append(c)
                
                return y_columns, x_columns
                    
            else:
                y_max, y_min, x_max, x_min = self.coordinate_ranges[crs_type]['y_max'], self.coordinate_ranges[crs_type]['y_min'], self.coordinate_ranges[crs_type]['x_max'], self.coordinate_ranges[crs_type]['x_min']
                
                for c in DF.columns:
                    try:
                        DF[c] = DF[c].astype(float, errors='raise')
                        if DF[c].dropna().between(y_min, y_max).all() and not DF[c].dropna().empty:
                            y_columns.append(c)
                        if DF[c].dropna().between(x_min, x_max).all() and not DF[c].dropna().empty:
                            x_columns.append(c)
                    except:
                        pass
                return y_columns, x_columns
        except Exception as e:
            msg = QMessageBox(parent=self, text='Ocorreu um erro ao filtrar os campos de coordenadas.\n\n'+str(e))
            msg.setWindowTitle('Erro')
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.exec()
    
    
    def yx_column_selected(self, axis):
        try:
            self.coordinates_tbl.disconnect()
            
            column = 0 if axis=='y' else 1
            column2 = 1 if axis=='y' else 0
            field = self.yColumn_cbx.currentText() if axis=='y' else self.xColumn_cbx.currentText()
            
            if field!='':
                data = self.fileDF[field]
                
                rows = len(data)
                self.coordinates_tbl.setRowCount(rows)
                
                for row, i in enumerate(data):
                    value = QTableWidgetItem(str(i))
                    self.coordinates_tbl.setItem(row, column, value)
            
            else:
                other_column = []
                for row in range(self.coordinates_tbl.rowCount()):
                    value = QTableWidgetItem(None)
                    self.coordinates_tbl.setItem(row, column, value)
                    
                    other_column_item = self.coordinates_tbl.item(row, column2).text()
                    if other_column_item != '': other_column.append(other_column_item)
                
                if not other_column:
                    self.coordinates_tbl.setRowCount(0)
                    
            self.coordinates_tbl.setColumnWidth(0, 164)
            self.coordinates_tbl.setColumnWidth(1, 164)
            self.coordinates_tbl.itemChanged.connect(self.check_table_data)
            self.check_table_data()
        except Exception as e:
            msg = QMessageBox(parent=self, text='Ocorreu um erro ao atualizar a tabela.\n\n'+str(e))
            msg.setWindowTitle('Erro')
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.exec()
        
    
    def add_row(self):
        try:
            rows = self.coordinates_tbl.rowCount()
            self.coordinates_tbl.insertRow(rows)
            
            self.coordinates_tbl.setColumnWidth(0, 164)
            self.coordinates_tbl.setColumnWidth(1, 164)
        
            self.check_table_data()
        except:
            pass
        
        
    def delete_row(self):
        try:
            self.coordinates_tbl.removeRow(self.coordinates_tbl.currentRow())
            self.check_table_data()
        except:
            pass
        
        
    def clear_table(self):
        try:
            self.coordinates_tbl.setRowCount(0)
            self.check_table_data()
        except:
            pass
        
        
    def refresh_table(self):
        try:
            self.clear_table()
            self.yx_column_selected('y')
            self.yx_column_selected('x')
        except:
            pass
        
        
    def get_table_data(self):
        try:
            rows = self.coordinates_tbl.rowCount()
            columns = self.coordinates_tbl.columnCount()
            
            crs_type = self.inputCRStype_cbx.currentText()
            
            DF = pandas.DataFrame()
            
            for c in range(columns):
                h = self.format_options[crs_type]['headings'][c]
                column_data = []
                for r in range(rows):
                    item = self.coordinates_tbl.item(r,c)
                    try:
                        column_data.append(item.text())
                    except AttributeError:
                        column_data.append(numpy.nan)
                DF[h] = column_data
            
            if len(DF.columns)<2: DF['fill'] = numpy.nan
        
            return DF
        except Exception as e:
            msg = QMessageBox(parent=self, text='Ocorreu um erro ao recuperar os dados da tabela.\n\n'+str(e))
            msg.setWindowTitle('Erro')
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.exec()
            return self.fileDF
        
        
    def check_table_data(self):
        try:
            self.interfaceDF = self.get_table_data()
            fields = self.interfaceDF.columns.to_list()
            
            crs_type = self.inputCRStype_cbx.currentText()
            
            y_columns, x_columns = self.filter_coordinate_columns(self.interfaceDF, crs_type)  
            
            columns_ok = True if (fields[0] in y_columns and fields[1] in x_columns) else False
            rows_ok = True if (self.interfaceDF[fields[0]].dropna().size == self.interfaceDF[fields[1]].dropna().size) else False
            
            self.convert_btn.setEnabled(columns_ok and rows_ok)
        except Exception as e:
            msg = QMessageBox(parent=self, text='Ocorreu um erro ao checar os dados da tabela.\n\n'+str(e))
            msg.setWindowTitle('Erro')
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.exec()
        
        
    def manage_conversion(self):
        
        try:
            input_CRS_type = self.inputCRStype_cbx.currentText()
            output_CRS_type = self.outputCRStype_cbx.currentText()
            
            input_CRS = self.inputCRS_cbx.currentText()
            output_CRS = self.outputCRS_cbx.currentText()
            
            input_EPSG = self.geographic_CRS_dt[input_CRS] if input_CRS_type.startswith('Geográfico') else self.UTM_CRS_dt[input_CRS]
            output_EPSG = self.geographic_CRS_dt[output_CRS] if output_CRS_type.startswith('Geográfico') else self.UTM_CRS_dt[output_CRS]
            
            fields = self.interfaceDF.columns.to_list()
            input_y = self.interfaceDF[fields[0]].values
            input_x = self.interfaceDF[fields[1]].values
                
            if input_CRS_type=='Projetado (UTM)' and output_CRS_type=='Geográfico (GD)':
                self.output_y, self.output_x = self.convert_coordinates(input_y, input_x, input_EPSG, output_EPSG, input_CRS_type, output_CRS_type)
            
            elif input_CRS_type=='Projetado (UTM)' and output_CRS_type=='Geográfico (GMS)':
                output_y_DD, output_x_DD = self.convert_coordinates(input_y, input_x, input_EPSG, output_EPSG, input_CRS_type, 'Geográfico (GD)')
                self.output_y = self.reformat_DD_to_DMS(output_y_DD, 'y')
                self.output_x = self.reformat_DD_to_DMS(output_x_DD, 'x')
            
            elif input_CRS_type=='Projetado (UTM)' and output_CRS_type=='Projetado (UTM)':
                self.output_y, self.output_x = self.convert_coordinates(input_y, input_x, input_EPSG, output_EPSG, input_CRS_type, output_CRS_type)
            
            elif input_CRS_type=='Geográfico (GD)' and output_CRS_type=='Geográfico (GMS)':
                output_y_DD, output_x_DD = self.convert_coordinates(input_y, input_x, input_EPSG, output_EPSG, input_CRS_type, 'Geográfico (GD)')
                self.output_y = self.reformat_DD_to_DMS(output_y_DD, 'y')
                self.output_x = self.reformat_DD_to_DMS(output_x_DD, 'x')
           
            elif input_CRS_type=='Geográfico (GD)' and output_CRS_type=='Projetado (UTM)':
                self.output_y, self.output_x = self.convert_coordinates(input_y, input_x, input_EPSG, output_EPSG, input_CRS_type, output_CRS_type)
            
            elif input_CRS_type=='Geográfico (GD)' and output_CRS_type=='Projetado (GD)':
                self.output_y, self.output_x = self.convert_coordinates(input_y, input_x, input_EPSG, output_EPSG, input_CRS_type, output_CRS_type)
            
            elif input_CRS_type=='Geográfico (GMS)' and output_CRS_type=='Geográfico (GD)':
                input_y_DD = self.reformat_DMS_to_DD(input_y)
                input_x_DD = self.reformat_DMS_to_DD(input_x)
                self.output_y, self.output_x = self.convert_coordinates(input_y_DD, input_x_DD, input_EPSG, output_EPSG, 'Geográfico (GD)', output_CRS_type)
            
            elif input_CRS_type=='Geográfico (GMS)' and output_CRS_type=='Projetado (UTM)':
                input_y_DD = self.reformat_DMS_to_DD(input_y)
                input_x_DD = self.reformat_DMS_to_DD(input_x)
                self.output_y, self.output_x = self.convert_coordinates(input_y_DD, input_x_DD, input_EPSG, output_EPSG, 'Geográfico (GD)', output_CRS_type)
           
            elif input_CRS_type=='Geográfico (GMS)' and output_CRS_type=='Geográfico (GMS)':
                input_y_DD = self.reformat_DMS_to_DD(input_y)
                input_x_DD = self.reformat_DMS_to_DD(input_x)
                output_y_DD, output_x_DD = self.convert_coordinates(input_y_DD, input_x_DD, input_EPSG, output_EPSG, 'Geográfico (GD)', 'Geográfico (GD)')
                self.output_y = self.reformat_DD_to_DMS(output_y_DD, 'y')
                self.output_x = self.reformat_DD_to_DMS(output_x_DD, 'x')
        
        except Exception as e:
            msg = QMessageBox(parent=self, text='Ocorreu um erro durante a conversão.\n\n'+str(e))
            msg.setWindowTitle('Erro')
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.exec()
        
        self.export_results(output_CRS_type)
        
        
    def convert_coordinates(self, input_y, input_x, input_EPSG, output_EPSG, input_CRS_type, output_CRS_type):
        
        if len(input_y)==len(input_x): n = len(input_y)
        else: raise Exception('There\'s an uneven number of Y and X coordinates')
        
        transformer = Transformer.from_crs(input_EPSG, output_EPSG)
        
        output_y, output_x = [], []
        
        for i in range(0, n):
            a,b = input_y[i], input_x[i]
            
            if input_CRS_type=='Projetado (UTM)' and output_CRS_type=='Geográfico (GD)':
                y,x = transformer.transform(b,a)
            elif input_CRS_type=='Projetado (UTM)' and output_CRS_type=='Projetado (UTM)':
                x,y = transformer.transform(b,a)
            elif input_CRS_type=='Geográfico (GD)' and output_CRS_type=='Projetado (UTM)':
                x,y = transformer.transform(a,b)
            elif input_CRS_type=='Geográfico (GD)' and output_CRS_type=='Geográfico (GD)':
                y,x = transformer.transform(a,b)
            
            output_y.append(y)
            output_x.append(x)
        
        return output_y, output_x
    
    
    def reformat_DD_to_DMS(self, DD_coordinates, axis):
        DMS_coordinates = []
        for i in DD_coordinates:
            if i<0:
                if axis=='y':
                    pole='S'
                elif axis=='x':
                    pole='W'
            else: 
                if axis=='y':
                    pole='N'
                elif axis=='x':
                    pole='E'
            
            mnt, sec = divmod(abs(i)*3600,60)
            deg, mnt = divmod(mnt,60)
            DMS = ('%02.0f°%02.0f\'%07.4f\"%s' % (deg,mnt,sec,pole)).replace('.',',')
            DMS_coordinates.append(DMS)
        
        return DMS_coordinates
    
    
    def reformat_DMS_to_DD(self, DMS_coordinates):
        DD_coordinates = []
        for i in DMS_coordinates:
            coordinate = i.replace(',','.')
            deg, mnt, sec, suffix = re.split('[°\'"]', coordinate)
            DD = (float(deg) + float(mnt)/60 + float(sec)/(60*60)) * (-1 if suffix in ['W', 'O', 'S'] else 1)
            DD_coordinates.append(DD)
        
        return DD_coordinates
    
    def export_results(self, output_CRS_type):
        try:
            DF = pandas.DataFrame()
            if output_CRS_type=='Projetado (UTM)':
                DF['Easting'] = self.output_x
                DF['Northing'] = self.output_y
            else:
                DF['Latitude'] = self.output_y
                DF['Longitude'] = self.output_x
                
            output_file = QFileDialog.getSaveFileName(self, caption='Salvar arquivo', directory=self.folder, filter='Pasta de trabalho do excel (*.xlsx);;Texto separado por delimitador (*.csv)')
            filePath = output_file[0]
            if filePath!='':
                if filePath.endswith('.csv'):
                    DF.to_csv(filePath, sep=',', decimal='.', index=False)
                else:
                    DF.to_excel(filePath, index=False, engine='openpyxl')
                
                msg = QMessageBox(parent=self, text='Arquivo salvo com sucesso!')
                msg.setWindowTitle('Sucesso')
                msg.exec()
        except Exception as e:
            msg = QMessageBox(parent=self, text='Ocorreu um erro ao exportar os resultados.\n\n'+str(e))
            msg.setWindowTitle('Erro')
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.exec()

if __name__ == '__main__':
    app = QApplication(sys_argv)
    window = XYConverterApp()
    window.show()
    app.exec()