# -*- coding: utf-8 -*-
"""
Created on Thu Feb 20 21:31:17 2025

@author: Edson Matias
"""
import requests
import time


def build_query_params(year_start, year_end, output_format="application/json"):
    """
    Constrói os parâmetros da query para a requisição WFS.
    """
    # Monta o filtro CQL usando o campo informado
    cql_filter = f"year BETWEEN {year_start} AND {year_end}"
    
    params = {
        "service": "WFS",
        "version": "2.0.0",
        "request": "GetFeature",
        "typename": None,  
        "outputFormat": output_format,
        "srsName": "EPSG:4674",
        "CQL_FILTER": cql_filter,
        "sortBy": "year A"
    }
    return params

def get_paginated_geojson(workspace, layer, year_start, year_end, page_size=10000):
    """
    Realiza requisições paginadas ao WFS, acumulando os dados em uma lista.
    
    Se o download de uma página falhar, ele tenta novamente a cada X segundos, por até X tentativas.
    Retorna:
      Uma lista com todas as features obtidas.
    """
    base_url = f"https://terrabrasilis.dpi.inpe.br/geoserver/{workspace}/{layer}/wfs"
    all_features = []
    start_index = 0

    while True:
        params = build_query_params(year_start, year_end,)
        params["typename"] = f"{workspace}:{layer}"
        params["startIndex"] = start_index
        params["count"] = page_size

        # Tentativas para o download da página atual
        attempts = 0
        success = False
        while attempts < 10:
            print(f"Tentando baixar a página com startIndex={start_index} (tentativa {attempts + 1}/10)...")
            response = requests.get(base_url, params=params)
            if response.ok:
                success = True
                break
            else:
                attempts += 1
                print(f"Falha na requisição (HTTP {response.text}). Tentando novamente em 60 segundos...")
                time.sleep(60)
        
        if not success:
            print(f"Falha após 10 tentativas para a página com startIndex={start_index}. Encerrando a paginação.")
            return response
            break

        data = response.json()
        features = data.get("features", [])
        print(f"Página com startIndex={start_index} retornou {len(features)} features.")

        if not features:
            break  # Se não houver mais features, encerra a iteração
        
        all_features.extend(features)
        
        # Se o número de features retornadas for menor que o page_size, chegamos ao final
        if len(features) < page_size:
            break
        
        start_index += page_size

    return all_features
