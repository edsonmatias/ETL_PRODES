# -*- coding: utf-8 -*-
"""
Created on Thu Feb 20 23:39:58 2025

@author: Edson Matias
"""


from sqlalchemy import create_engine, text

# Configuração de Conexão com o BD
db_connection_string = "postgresql+psycopg2://admin:admin2k25@localhost:15432/geodb"

def upload_gdf_to_post(gdf, table_name, schema="raw_data"):
    """
    Envia um GeoDataFrame para uma tabela no PostgreSQL/PostGIS, evitando duplicatas.
    """
    
    # Converter a geometria para WKT (Well-Known Text)
    gdf["geom"] = gdf["geometry"].apply(lambda geom: geom.wkt)
    gdf = gdf.drop(columns=["geometry"])
    
    # Transformar em dicionário de registros
    data = gdf.to_dict(orient='records')
    
    # Query de inserção ignorando duplicatas
    insert_query = text(f"""
        INSERT INTO {schema}.{table_name} (id, uid, state, path_row, def_cloud, julian_day, image_date, year, area_km, scene_id, source, satellite, sensor, publish_year, geom)
        SELECT 
            :id, 
            :uid, 
            :state, 
            :path_row, 
            :def_cloud, 
            :julian_day, 
            :image_date, 
            :year, 
            :area_km, 
            :scene_id, 
            :source, 
            :satellite, 
            :sensor, 
            :publish_year, 
            ST_GeomFromText(:geom, 4326)
        WHERE NOT EXISTS (
            SELECT 1 FROM {schema}.{table_name} 
            WHERE id = :id
        )
    """)
    
    # Conectar e executar inserções
    engine = create_engine(db_connection_string)
    with engine.begin() as conn:
        conn.execute(insert_query, data)


