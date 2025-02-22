# -*- coding: utf-8 -*-
"""
Created on Thu Feb 20 23:12:48 2025

@author: Edson Matias
"""

from get_data_prodes import get_paginated_geojson as gd  # Função para baixar os dados GeoJSON paginados
from geom_transf_valid import convert_feature_to_gdf, validate_and_fix_geometry  # Funções para converter e validar geometria
from tqdm import tqdm  
from data_up import upload_gdf_to_post  # Função para upload do GeoDataFrame para o banco de dados
import pandas as pd


class DeforestationProcessor:
    def __init__(self, workspace, layer, year_start, year_end, source_none):
        """
        Inicializa o processador de dados de desmatamento.

        :param workspace: Nome do workspace no WFS
        :param layer: Nome da camada a ser consultada
        :param year_start: Ano inicial do intervalo de consulta
        :param year_end: Ano final do intervalo de consulta
        :param source_none: Valor padrão para preencher o campo 'source' quando estiver ausente
        """
        self.workspace = workspace
        self.layer = layer
        self.year_start = year_start
        self.year_end = year_end
        self.source_none = source_none

    def process_years(self):
        """
        Processa os dados em intervalos de dois anos e faz o upload para o banco de dados.
        """
        for ystart in range(self.year_start, self.year_end + 1, 2):
            yend = min(ystart + 1, self.year_end)

            print(f'Filtrando Ano: {ystart} até {yend}')
            print('Fazendo Download...')
            dict_geo = gd(self.workspace, self.layer, str(ystart), str(yend))  # Obtém os dados GeoJSON
            print('Download Concluído!')

            gdfs_validos = self._process_features(dict_geo)  # Processa as features

            if gdfs_validos:
                print('Subindo dado no BD...')
                gdf_final = pd.concat(gdfs_validos, ignore_index=True)
                upload_gdf_to_post(gdf_final, 'desmatamento', schema="raw_data")  # Upload único das features validadas
                print('Upload completo!')
            else:
                print('Nenhum dado válido para upload.')

    def _process_features(self, dict_geo):
        """
        Processa as features do GeoJSON, convertendo e validando as geometrias.
        """
        gdfs_validos = []
        for feat in tqdm(dict_geo, desc="Convertendo e Validando Geometrias"):
            gdf = convert_feature_to_gdf(feat)  # Converte a feature para um GeoDataFrame

            if gdf is not None:  # Verifica se a conversão foi bem-sucedida
                gdf = validate_and_fix_geometry(gdf)  # Valida e tenta corrigir a geometria

                if gdf is not None:  # Se a validação e correção funcionaram
                    gdf["source"] = source_none  # Preenche valores com o source correspondente
                    gdfs_validos.append(gdf)  # Adiciona à lista de GDFs válidos
                else:
                    print('Geometria inválida, não foi possível a correção')
            else:
                print('Não foi possível a conversão')

        return gdfs_validos

#%%
# Configurações iniciais/Filtros
workspace = "prodes-cerrado-nb"
layer = "yearly_deforestation"
year_start = 2000
year_end = 2024
source_none = 'cerrado' #Para evitar despadronização e categorizar os dados

# Cria uma instância
processor = DeforestationProcessor(workspace, layer, year_start, year_end, source_none)

# Processa os dados e faz o upload
processor.process_years()