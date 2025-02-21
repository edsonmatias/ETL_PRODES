# -*- coding: utf-8 -*-
"""
Created on Thu Feb 20 23:39:58 2025

@author: Edson Matias
"""


from sqlalchemy import create_engine

db_connection_string = "postgresql+psycopg2://admin:admin2k25@localhost:15432/geodb"

def upload_gdf_to_post(gdf, table_name, schema="public"):
    """
    Envia um GeoDataFrame para uma tabela no PostgreSQL/PostGIS.

    :param gdf: GeoDataFrame contendo as informações a serem inseridas
    :param table_name: Nome da tabela no PostgreSQL
    :param db_connection_string: String de conexão com o banco de dados
    :param schema: Schema onde a tabela será criada (padrão: public)
    """

    # Converter a geometria para WKT (Well-Known Text)
    gdf["geom"] = gdf["geometry"].apply(lambda geom: geom.wkt)

    # Remover a coluna original de geometria
    gdf = gdf.drop(columns=["geometry"])

    # Criar conexão com o banco
    engine = create_engine(db_connection_string)

    # Subir para o banco de dados via to_sql
    with engine.begin() as connection:
        # Subir para o banco de dados via to_sql
        gdf.to_sql(
            table_name,
            con=connection,
            schema=schema,
            if_exists="append",
            index=False
        )
    


