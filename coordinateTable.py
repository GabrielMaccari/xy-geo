# -*- coding: utf-8 -*-
"""
Created on Tue Jun 21 13:44:14 2022

@author: gabri
"""

import pandas
from pyproj import Transformer
import re

class CoordinateTable:
    #Inicialização dos atributos da classe
    def __init__(self, path):
        self.file = path
        self.dataframe = pandas.read_excel(self.file)
        self.columns = self.dataframe.columns.to_list()
        self.dTypes = self.dataframe.dtypes.to_list()
    
    #Função que retorna os nomes das colunas da tabela
    def getHeadings(self):
        return list(self.dataframe.columns.values)
    
    def getCoordinateColumns(self, input_format):
        
        if input_format=='Graus decimais':
            allowed_dTypes = ['float64']
            y_range_min, y_range_max = -90, 90
            x_range_min, x_range_max = -180, 180
        elif input_format=='UTM':
            allowed_dTypes = ['float64', 'int64']
            y_range_min, y_range_max = 1099000, 10000000
            x_range_min, x_range_max = 165000, 835000
        else:
            return self.columns, self.columns
        
        y_columns_list, x_columns_list = [], []
        for i in range(len(self.columns)):
            if self.dTypes[i] in allowed_dTypes:
                c = self.columns[i]
                if self.dataframe[c].dropna().between(y_range_min, y_range_max).all() and not self.dataframe[c].dropna().empty:
                    y_columns_list.append(c)
                if self.dataframe[c].dropna().between(x_range_min, x_range_max).all() and not self.dataframe[c].dropna().empty:
                    x_columns_list.append(c)
        
        return y_columns_list, x_columns_list
    
    #Função que retorna pares de coordenadas para compor a tabela de visuaização do programa
    def getPairs(self, N, E):
        #Lista onde serão armazenados os pares
        pair_list = []
        
        #Listas com todos os valores das colunas
        N_values, E_values = self.dataframe[N].values, self.dataframe[E].values
        
        #Passa os valores em pares para a lista de pares, substituindo os pontos por vírgulas para separação decimal
        for i in range(len(N_values)):
            pair_list.append([str(N_values[i]).replace('.',','), str(E_values[i]).replace('.',',')])
        
        #Retorna a lista de pares
        return pair_list
    
    #Função que checa se uma coluna do dataframe contém apenas valores numéricos
    def checkNumericInput(self, N, E, input_format):
        
        try:
            self.dataframe[N] = self.dataframe[N].astype('float64')
            self.dataframe[E] = self.dataframe[E].astype('float64')
        except:
            return False

        if input_format=='UTM':
            y_range_min, y_range_max = 1099000, 10000000
            x_range_min, x_range_max = 165000, 835000
        else:
            y_range_min, y_range_max = -90, 90
            x_range_min, x_range_max = -180, 180
        
        N_ok, E_ok = [], []
        
        if self.dataframe[N].dropna().between(y_range_min, y_range_max).all() and not self.dataframe[N].dropna().empty:
            N_ok = True
        else:
            N_ok = False
        
        if self.dataframe[E].dropna().between(x_range_min, x_range_max).all() and not self.dataframe[E].dropna().empty:
            E_ok = True
        else:
            E_ok = False 
        
        return (N_ok and E_ok)
                  
    #Função que checa se uma coluna do dataframe contém apenas valores numéricos
    def checkDMSInput(self, N_column, E_column):
        NS_pattern = re.compile('[0-9]{1,2}°[0-9]{1,2}\'[0-9]{1,2},[0-9]{0,20}"[NS]')
        WE_pattern = re.compile('[0-9]{1,2}°[0-9]{1,2}\'[0-9]{1,2},[0-9]{0,20}"[WEOL]')
        
        N = self.dataframe[N_column].values
        E = self.dataframe[E_column].values
        
        if N.all()==E.all():
            return False
        
        N_ok, E_ok = True, True
        
        for i in N:
            if NS_pattern.match(str(i)) == None:
                N_ok = False
        for j in E:
            if WE_pattern.match(str(j)) == None:
                E_ok = False

        return (N_ok and E_ok)
    
    def reproject(self, E_column, N_column, input_CRS, input_type, output_CRS, output_type):
        #Armazena as coordenadas em uma lista para poder iterar nelas (é mais fácil do que iterar nas colunas do dataframe)
        listaCoordenadas = self.dataframe[[E_column, N_column]].values.tolist()
        #Define os parâmetros de conversão
        transformer = Transformer.from_crs(input_CRS, output_CRS)
        #Listas vazias para armazenar as coordenadas geográficas após a conversão
        y_list, x_list = [], []
        
        #Converte as coordenadas e armazena nas listas
        for i in range(0, len(listaCoordenadas)):
            a,b = self.dataframe[N_column][i], (self.dataframe[E_column][i])
            
            if input_type=='UTM' and output_type=='Geographic':
                y,x = transformer.transform(b,a)
            elif input_type=='UTM' and output_type=='UTM':
                x,y = transformer.transform(b,a)
            elif input_type=='Geographic' and output_type=='UTM':
                x,y = transformer.transform(a,b)
            elif input_type=='Geographic' and output_type=='Geographic':
                y,x = transformer.transform(a,b)
            
            y_list.append(y)
            x_list.append(x)
            
        if output_type=='Geographic':
            #Adiciona os resultados ao dataframe
            self.dataframe['lat_'+str(output_CRS)] = y_list
            self.dataframe['lon_'+str(output_CRS)] = x_list
            
            #Retorna os nomes das colunas de resultados
            return 'lat_'+str(output_CRS), 'lon_'+str(output_CRS)
        
        elif output_type=='UTM':
            #Adiciona os resultados ao dataframe
            self.dataframe['E_'+str(output_CRS)] = x_list
            self.dataframe['N_'+str(output_CRS)] = y_list
            
            #Retorna os nomes das colunas de resultados
            return 'E_'+str(output_CRS), 'N_'+str(output_CRS)
    
    #Função que formata coordenadas geográficas decimais para graus, minutos e segundos
    def format_DD_to_DMS(self, column, axis):
        DD_coordinates = self.dataframe[column].values.tolist()
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
            DMS = ('%02.0f°%02.0f\'%07.7f\"%s' % (deg,mnt,sec,pole)).replace('.',',')
            DMS_coordinates.append(DMS)
        
        self.dataframe[column+'_GMS'] = DMS_coordinates
        
        return column+'_GMS'
    
    #Função que formata coordenadas geográficas decimais para graus, minutos e segundos
    def format_DMS_to_DD(self, column):
        DMS_coordinates = self.dataframe[column].values.tolist()
        DD_coordinates = []
        
        for i in DMS_coordinates:
            coordinate = i.replace(',','.')
            deg, mnt, sec, suffix = re.split('[°\'"]', coordinate)
            DD = (float(deg) + float(mnt)/60 + float(sec)/(60*60)) * (-1 if suffix in ['W', 'O', 'S'] else 1)
            DD_coordinates.append(DD)
        
        self.dataframe[column+'_DD'] = DD_coordinates
        
        return column+'_DD'
    
    #Função que deleta colunas do dataframe
    def deleteDataframeColumns(self, columns):
        self.dataframe.drop(columns, axis=1, inplace=True)
        return
    
    #Função que exporta o dataframe para um arquivo
    def exportDataframe(self, output_path, output_name, output_extension):
        if output_extension=='.csv':
            self.dataframe.to_csv(output_path+'\\'+output_name+'.csv', sep=';', decimal=',', index=False)
        elif output_extension=='.xlsx':
            self.dataframe.to_excel(output_path+'\\'+output_name+'.xlsx', index=False)
        elif output_extension=='.html':
            self.dataframe.to_html(output_path+'\\'+output_name+'.html', decimal=',', index=False)
        
        return
