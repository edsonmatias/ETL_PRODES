# -*- coding: utf-8 -*-
"""
Created on Thu Feb 20 23:13:04 2025

@author: Edson Matias
"""

import geopandas as gpd
from shapely import make_valid
from shapely.geometry import shape
import numpy as np

def convert_feature_to_gdf(feature):
    """
    Converte uma feature WFS para um GeoDataFrame, garantindo que contenha apenas as colunas especificadas.

    :param feature: Dicionário contendo a feature com geometria e atributos.
    :return: GeoDataFrame contendo a feature convertida e padronizada.
    """
    # Colunas esperadas no GeoDataFrame
    expected_columns = [
        'uid', 'state', 'path_row', 'def_cloud', 'julian_day', 'image_date',
        'year', 'area_km', 'scene_id', 'source', 'satellite', 'sensor',
        'publish_year', 'geometry'
    ]

    try:
        # Copiar as propriedades da feature
        properties = feature["properties"].copy()

        # Remover campos indesejados
        fields_to_remove = ["main_class", "class_name"]
        for field in fields_to_remove:
            properties.pop(field, None)

        # Verificar e renomear colunas existentes
        for col in list(properties.keys()):  # Usar list() para evitar RuntimeError ao modificar o dicionário
            if col not in expected_columns:
                # Verificar se o nome da coluna contém uma substring esperada
                for expected in expected_columns:
                    if expected in col:
                        properties[expected] = properties.pop(col)  # Renomeia a coluna
                        break

        # Adicionar colunas faltantes com valores padrão
        for col in expected_columns:
            if col not in properties:
                if col in ['uid', 'julian_day', 'year', 'scene_id']:  # Colunas numéricas
                    properties[col] = None
                elif col in ['area_km']:  # Colunas de float
                    properties[col] = np.nan
                elif col in ['publish_year', 'image_date']:  # Colunas de data
                    properties[col] = None
                else:  # Colunas de texto
                    properties[col] = None

        # Converter geometria usando shapely
        geometry = shape(feature["geometry"])

        # Criar o GeoDataFrame
        gdf = gpd.GeoDataFrame(
            [properties],
            geometry=[geometry],
            crs="EPSG:4326"
        )
        
        gdf['id'] = feature["id"]

        # Garantir que a coluna 'geom' seja uma cópia de 'geometry'
        if 'geometry' in gdf.columns and 'geom' not in gdf.columns:
            gdf['geom'] = gdf['geometry']


        return gdf
    except Exception as e:
        print(f"Erro ao converter a feature: {e}")
        return None


def validate_and_fix_geometry(gdf):
    """
    Valida e corrige geometrias inválidas em um GeoDataFrame.
    
    :param gdf: GeoDataFrame contendo a geometria a ser validada.
    :return: GeoDataFrame corrigido ou None se a geometria continuar inválida.
    """
    try:
        # Aplicar make_valid para corrigir geometrias inválidas
        gdf["geometry"] = gdf["geometry"].apply(make_valid)

        # Se ainda houver geometria inválida, retorna None
        if not gdf.is_valid.all():
            print("Geometria inválida mesmo após correção.")
            return None

        return gdf
    except Exception as e:
        print(f"Erro ao validar/corrigir geometria: {e}")
        return None
