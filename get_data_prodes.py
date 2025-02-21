# -*- coding: utf-8 -*-
"""
Created on Thu Feb 20 21:31:17 2025

@author: Edson Matias
"""
import requests
import time


def build_query_params(year_start, year_end, date_field="image_date", output_format="application/json"):
    """
    Constrói os parâmetros da query para a requisição WFS.
    
    Parâmetros:
      start_date, end_date: intervalo de datas (formato 'YYYY-MM-DD').
      date_field: nome do campo de data a ser filtrado.
      uf: (opcional) filtro adicional por unidade federativa.
      output_format: formato de saída (fixado para GeoJSON).
    """
    # Monta o filtro CQL usando o campo informado
    cql_filter = f"year BETWEEN {year_start} AND {year_end}"
    
    params = {
        "service": "WFS",
        "version": "2.0.0",
        "request": "GetFeature",
        "typename": None,  # Será definido em get_paginated_geojson
        "outputFormat": output_format,
        "srsName": "EPSG:4674",
        "CQL_FILTER": cql_filter
    }
    return params

def get_paginated_geojson(workspace, layer, year_start, year_end, date_field="view_date", page_size=10000):
    """
    Realiza requisições paginadas ao WFS, acumulando os dados em uma lista.
    
    Se o download de uma página falhar, ele tenta novamente a cada 10 segundos, por até 10 tentativas.
    
    Parâmetros:
      workspace: Nome do workspace.
      layer: Nome da camada.
      start_date, end_date: Intervalo de datas (formato 'YYYY-MM-DD').
      date_field: Nome do campo de data (ex.: "view_date").
      uf: (opcional) filtro por UF.
      page_size: Número de registros por página.
    
    Retorna:
      Uma lista com todas as features obtidas.
    """
    base_url = f"https://terrabrasilis.dpi.inpe.br/geoserver/{workspace}/{layer}/wfs"
    all_features = []
    start_index = 0

    while True:
        params = build_query_params(year_start, year_end, date_field)
        params["typename"] = f"{workspace}:{layer}"
        params["startIndex"] = start_index
        params["count"] = page_size

        # Tentativas para o download da página atual
        attempts = 0
        success = False
        while attempts < 10:
            #print(f"Tentando baixar a página com startIndex={start_index} (tentativa {attempts + 1}/10)...")
            response = requests.get(base_url, params=params)
            if response.ok:
                success = True
                break
            else:
                attempts += 1
                print(f"Falha na requisição (HTTP {response.status_code}). Tentando novamente em 10 segundos...")
                time.sleep(60)
        
        if not success:
            print(f"Falha após 10 tentativas para a página com startIndex={start_index}. Encerrando a paginação.")
            return response
            break

        data = response.json()
        features = data.get("features", [])
        #print(f"Página com startIndex={start_index} retornou {len(features)} features.")

        if not features:
            break  # Se não houver mais features, encerra a iteração
        
        all_features.extend(features)
        
        # Se o número de features retornadas for menor que o page_size, chegamos ao final
        if len(features) < page_size:
            break
        
        start_index += page_size

    return all_features
