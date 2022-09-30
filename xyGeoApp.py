# -*- coding: utf-8 -*-
"""
Created on Fri Jun 24 12:16:32 2022

@author: gabri
"""

import PySimpleGUI as sg
from coordinateTable import CoordinateTable
from pyproj.database import query_crs_info
from os import getcwd

sg.theme('BrownBlue')

utm_crs_data = query_crs_info(pj_types='PROJECTED_CRS')  #pyproj.database.query_crs_info()
geo_crs_data = query_crs_info(pj_types='GEOGRAPHIC_2D_CRS')
utm_crs_dict, geo_crs_dict = {}, {}

for info in utm_crs_data:
    if info.auth_name=='EPSG':
        utm_crs_dict[info.name] = int(info.code)
for info in geo_crs_data:
    if info.auth_name=='EPSG':
        geo_crs_dict[info.name] = int(info.code)
        
#Exemplos de formato de coordenadas
format_options = {'UTM':'720366',
                  'Graus decimais':'-27,1952',
                  'Graus, minutos e segundos':'27°11\'42,556"S'}

#Opções de formatos de arquivo de saída
extension_options = ['.csv','.html','.xlsx']

tooltips = {'Arquivo_entrada':'Selecione uma tabela .csv contendo as coordenadas a serem convertidas.O separador decimal utilizado deve ser a vírgula, e não o ponto.',
            'Northing':'Selecione a coluna da tabela que contém as coordenadas do eixo Norte-Sul.',
            'Easting':'Selecione a coluna da tabela que contém as coordenadas do eixo Leste-Oeste.',
            'Formato_saída':'Selecione o formato de saída desejado para as coordenadas.',
            'SRC_origem':'Selecione o sistema de referência das coordenadas de entrada.',
            'SRC_destino':'Selecione o sistema de referência para o qual você quer converter as coordenadas.',
            'Arquivo_saída':'Insira o nome do arquivo (sem extensão) para o qual os resultados da conversão serão exportados e selecione o formato do arquivo dentre as opções disponíveis.',
            'Formato_entrada':'Selecione o formato de entrada das coordenadas.',
            'Latitude':'Selecione a coluna da tabela que contém as coordenadas de latitude.',
            'Longitude':'Selecione a coluna da tabela que contém as coordenadas de longitude.'}

#Elementos do layout
layout = [[sg.Text('Arquivo: ', size=(8,1)),
           sg.Input('', key='file_path', readonly=True, size=(47,1), enable_events=True, disabled=True, tooltip=tooltips['Arquivo_entrada']),
           sg.FileBrowse('Procurar', key='file_select', target='file_path', auto_size_button=False, size=(7,1))],
          [sg.Text('Formato de entrada:', size=(15,1)),
           sg.Combo(list(format_options.keys()), default_value='UTM', key='input_format', size=(30,1), enable_events=True, disabled=True, readonly=True, tooltip=tooltips['Formato_entrada']),
           sg.Text('Ex: 720336', key='input_format_example')],
          [sg.Text('Northing:', key='N_or_lat', size=(8,1)),
           sg.Combo((), key='Y_column', disabled=True, readonly=True, size=(12,1), tooltip=tooltips['Northing']),
           sg.Text('', size=(4,1)),
           sg.Text('Easting:', key='E_or_lon', size=(8,1)),
           sg.Combo((), key='X_column', disabled=True, readonly=True, size=(12,1), tooltip=tooltips['Easting']),
           sg.Button('OK', key='confirm_columns', disabled=True)],
          [sg.Table(values=[], headings=['Y','X'], key='table', num_rows=10, def_col_width=26, auto_size_columns=False, justification='center')],
          [sg.Text('Formato de saída:', size=(13,1)), 
           sg.Combo(list(format_options.keys()), default_value='Graus decimais', key='output_format', size=(30,1), enable_events=True, disabled=True, readonly=True, tooltip=tooltips['Formato_saída']),
           sg.Text('Ex: -27,1952', key='output_format_example')],
          [sg.Text('SRC de origem:', size=(13,1)),
           sg.Combo(values=sorted(list(utm_crs_dict.keys())), default_value='SIRGAS 2000 / UTM zone 22S', key='fromCRS', disabled=True, readonly=True, enable_events=True, size=(50,1), tooltip=tooltips['SRC_origem'])],
          [sg.Text('SRC de destino:', size=(13,1)),
           sg.Combo(values=sorted(list(geo_crs_dict.keys())), default_value='SIRGAS 2000', key='toCRS', disabled=True, readonly=True, enable_events=True, size=(50,1), tooltip=tooltips['SRC_destino'])],
          [sg.Text('Arquivo de saída: ', size=(13,1)),
           sg.Input(default_text='resultados_conversao', key='output_name', size=(32,1), tooltip=tooltips['Arquivo_saída'], disabled=True), 
           sg.Combo(extension_options, default_value='.xlsx', key='output_extension', readonly=True, disabled=True), 
           sg.Button('Converter', key='convert', disabled=True)],
          [sg.Text('© 2022 Gabriel Maccari <gabriel.maccari@hotmail.com>')]]

#Definição da janela
window = sg.Window('Ferramenta de Conversão de Tabela de Coordenadas', layout)

#Função que checa se a extensão do arquivo de entrada é CSV
def checkFileExtension(path):
    if path.lower().endswith('.xlsx'): return True
    else: return False
    
#Função que habilita ou desabilita as caixas de seleção de colunas
def enableColumnSelection(state):
    state = not state
    window['input_format'].update(disabled=state)
    window['Y_column'].update('', disabled=state)
    window['X_column'].update('', disabled=state)
    window['confirm_columns'].update(disabled=state)
    return

#Função que habilita ou desabilita as caixas de definição do SRC
def enableCRSSelection(state):
    state = not state
    window['output_format'].update(disabled=state)
    window['fromCRS'].update(disabled=state)
    window['toCRS'].update(disabled=state)
    window['output_name'].update(disabled=state)
    window['output_extension'].update(disabled=state)
    return

#Função que habilita ou desabilita o botão de conversão    
def enableConvertButton(state):
    state = not state
    window['convert'].update(disabled=state)
    return

#Loop de leitura de eventos
while True:
    event, values = window.read()
    
    #Ao fechar a janela
    if event == sg.WIN_CLOSED:
        break
    
    #Ao selecionar um arquivo
    if event == 'file_path':
        file = values['file_path']
        window['table'].update(values=[])
        #Checa se o arquivo é uma tabela .csv
        if checkFileExtension(file):
            #Cria um dataframe a partir da tabela e obtém os nomes das colunas dentro dela
            coordinates_DF = CoordinateTable(file)
            DF_columns = coordinates_DF.getHeadings()
            #Habilita os campos de seleção de colunas e preenche as opções com as colunas da tabela
            enableColumnSelection(True)
            y_columns, x_columns = coordinates_DF.getCoordinateColumns(values['input_format'])
            if len(y_columns)==0 or len(x_columns)==0:
                sg.popup('Não foi possível encontrar as colunas de coordenadas da tabela. Verifique se essas colunas estão no formato adequado e tente novamente.')
                enableCRSSelection(False)
                enableConvertButton(False)
            else:
                window['Y_column'].update(y_columns[0], values=y_columns)
                window['X_column'].update(x_columns[0], values=x_columns)
        else:
            sg.popup('O arquivo deve ser uma tabela em formato ".xlsx".')
            window['file_path'].update('')
            enableColumnSelection(False)
            enableCRSSelection(False)
            enableConvertButton(False)
    
    #Ao selecionar um formato de entrada das coordenadas
    if event == 'input_format':
        input_format = values['input_format']
        window['input_format_example'].update('Ex: '+format_options[input_format])
        if input_format=='UTM':
            window['N_or_lat'].update('Northing:')
            window['E_or_lon'].update('Easting:')
            window['fromCRS'].update(values=sorted(list(utm_crs_dict.keys())), value='SIRGAS 2000 / UTM zone 22S')
        else:
            window['N_or_lat'].update('Latitude:')
            window['E_or_lon'].update('Longitude:')
            window['fromCRS'].update(values=sorted(list(geo_crs_dict.keys())), value='SIRGAS 2000')
        y_columns, x_columns = coordinates_DF.getCoordinateColumns(input_format)
        if len(y_columns)==0 or len(x_columns)==0:
            sg.popup('Não foi possível encontrar as colunas de coordenadas da tabela. Verifique se essas colunas estão no formato adequado e tente novamente.')
            enableCRSSelection(False)
            enableConvertButton(False)
        else:
            window['Y_column'].update(y_columns[0], values=y_columns)
            window['X_column'].update(x_columns[0], values=x_columns)
        
    #Ao confirmar as colunas
    if event == 'confirm_columns':
        N_column, E_column = values['Y_column'], values['X_column']
        input_format = values['input_format']
                
        if input_format == 'Graus, minutos e segundos':
            columns_ok = coordinates_DF.checkDMSInput(N_column, E_column)
        else:
            columns_ok = coordinates_DF.checkNumericInput(N_column, E_column, input_format)
        
        if columns_ok:
            pairs = coordinates_DF.getPairs(N_column, E_column)
            window['table'].update(values=pairs)
                
            enableCRSSelection(True)
            enableConvertButton(True)
        else:
            window['table'].update(values=[])
            enableCRSSelection(False)
            enableConvertButton(False)
            sg.popup('As colunas selecionadas incluem coordenadas fora do formato selecionado ou contêm os mesmos valores. Corrija os dados de entrada conforme os exemplos da interface e tente novamente.\n-Utilize vírgula (,) como separador decimal.\n-Verifique se não existem dados não-numéricos dentro das colunas de coordenadas.\n-Confira se as colunas de coordenadas não se encontram invertidas ou duplicadas.')
    
    #Ao selecionar o formato de saída das coordenadas
    if event == 'output_format':
        window['output_format_example'].update('Ex: '+format_options[values['output_format']])
        if values['output_format']=='UTM':
            window['toCRS'].update(values=sorted(list(utm_crs_dict.keys())), value='SIRGAS 2000 / UTM zone 22S')
        else:
            window['toCRS'].update(values=sorted(list(geo_crs_dict.keys())), value='SIRGAS 2000')
    
    if event == 'convert':
        y, x = values['Y_column'], values['X_column']
        input_format, output_format = values['input_format'], values['output_format']
        
        crs_ok = False
        
        try:
            if input_format=='UTM':
                input_CRS = utm_crs_dict[values['fromCRS']]
            else:
                input_CRS = geo_crs_dict[values['fromCRS']]
            crs_ok = True
        except:
            sg.popup('Selecione um sistema de referência de coordenadas de entrada.')
            
        try:
            if output_format=='UTM':
                output_CRS = utm_crs_dict[values['toCRS']]
            else:
                output_CRS = geo_crs_dict[values['toCRS']]
            crs_ok = True
        except:
            sg.popup('Selecione um sistema de referência de coordenadas de saída.')
            
        output_folder = getcwd() #os.getcwd()
        output_name = values['output_name']
        output_extension = values['output_extension']
        
        try: 
            #Conversão de UTM para graus decimais
            if input_format=='UTM' and output_format=='Graus decimais':
                y_out, x_out = coordinates_DF.reproject(x, y, input_CRS, 'UTM', output_CRS, 'Geographic')
                
            #Conversão de UTM para graus, minutos e segundos
            elif input_format=='UTM' and output_format=='Graus, minutos e segundos':
                y_DD, x_DD = coordinates_DF.reproject(x, y, input_CRS, 'UTM', output_CRS, 'Geographic')
                y_out, x_out = coordinates_DF.format_DD_to_DMS(y_DD, 'y'), coordinates_DF.format_DD_to_DMS(x_DD, 'x')
                coordinates_DF.deleteDataframeColumns([y_DD, x_DD])
            
            #Conversão de UTM para UTM
            elif input_format=='UTM' and output_format=='UTM':
                x_out, y_out = coordinates_DF.reproject(x, y, input_CRS, 'UTM', output_CRS, 'UTM')
            
            #Conversão de graus decimais para UTM
            elif input_format=='Graus decimais' and output_format=='UTM':
                x_out, y_out = coordinates_DF.reproject(x, y, input_CRS, 'Geographic', output_CRS, 'UTM')
            
            #Conversão de graus decimais para graus decimais
            elif input_format=='Graus decimais' and output_format=='Graus decimais':
                x_out, y_out = coordinates_DF.reproject(x, y, input_CRS, 'Geographic', output_CRS, 'Geographic')
            
            #Conversão de graus decimais para graus, minutos e segundos
            elif input_format=='Graus decimais' and output_format=='Graus, minutos e segundos':
                y_DD, x_DD = coordinates_DF.reproject(x, y, input_CRS, 'Geographic', output_CRS, 'Geographic')
                y_out, x_out = coordinates_DF.format_DD_to_DMS(y_DD, 'y'), coordinates_DF.format_DD_to_DMS(x_DD, 'x')
                coordinates_DF.deleteDataframeColumns([y_DD, x_DD])
            
            #Conversão de graus,minutos e segundos para graus decimais
            elif input_format=='Graus, minutos e segundos' and output_format=='Graus decimais':
                y_DD, x_DD = coordinates_DF.format_DMS_to_DD(y), coordinates_DF.format_DMS_to_DD(x)
                y_out, x_out = coordinates_DF.reproject(x_DD, y_DD, input_CRS, 'Geographic', output_CRS, 'Geographic')
                coordinates_DF.deleteDataframeColumns([y_DD, x_DD])
            
            #Conversão de graus, minutos e segundos para UTM
            elif input_format=='Graus, minutos e segundos' and output_format=='UTM':
                y_DD, x_DD = coordinates_DF.format_DMS_to_DD(y), coordinates_DF.format_DMS_to_DD(x)
                x_out, y_out = coordinates_DF.reproject(x_DD, y_DD, input_CRS, 'Geographic', output_CRS, 'UTM')
                coordinates_DF.deleteDataframeColumns([y_DD, x_DD])
            
            #Conversão de graus, minutos e segundos para graus, minutos e segundos
            elif input_format=='Graus, minutos e segundos' and output_format=='Graus, minutos e segundos':
                y_DD, x_DD = coordinates_DF.format_DMS_to_DD(y), coordinates_DF.format_DMS_to_DD(x)
                y_DD2, x_DD2 = coordinates_DF.reproject(x_DD, y_DD, input_CRS, 'Geographic', output_CRS, 'Geographic')
                y_out, x_out = coordinates_DF.format_DD_to_DMS(y_DD2, 'y'), coordinates_DF.format_DD_to_DMS(x_DD2, 'x')
                coordinates_DF.deleteDataframeColumns([y_DD, x_DD, y_DD2, x_DD2])
            
            conversion_ok = True
                
        except Exception as e:
            conversion_ok = False
            sg.popup('Ocorreu um erro durante a conversão das coordenadas. Verifique os dados de entrada e tente novamente.\n\nDescrição do erro:\n'+str(e))
    
        if conversion_ok:
            try:
                coordinates_DF.exportDataframe(output_folder, output_name, output_extension)
                sg.popup('Conversão finalizada com sucesso! Os resultados foram exportados para %s\\%s%s. Foram criadas as colunas "%s" e "%s" para conter os valores de saída.' % (output_folder, output_name, output_extension, y_out, x_out))
            except Exception as e:
                sg.popup('Ocorreu um erro durante a exportação dos resultados. Verifique se o arquivo de saída não está aberto em outro programa e tente novamente.\n\nDescrição do erro:\n'+str(e))