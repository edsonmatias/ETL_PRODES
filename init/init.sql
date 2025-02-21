-- Habilita o PostGIS no banco de dados
CREATE EXTENSION IF NOT EXISTS postgis;

-- Cria o schema raw_data
CREATE SCHEMA IF NOT EXISTS raw_data;

-- Cria a tabela desmatamentos
CREATE TABLE raw_data.desmatamento(
	id VARCHAR PRIMARY KEY,
    uid VARCHAR,
    state TEXT NOT NULL,
    path_row TEXT,
    def_cloud TEXT,
    julian_day INT,
    year INT NOT NULL,
    area_km FLOAT,
    scene_id INT,
    publish_year DATE,
    source TEXT NOT NULL,
    satellite TEXT,
    sensor TEXT,
    image_date DATE,
    geom GEOMETRY(Geometry, 4326) NOT NULL
);


-- Cria índices para otimizar consultas
CREATE INDEX idx_desmatamento_year ON raw_data.desmatamento (year);
CREATE INDEX idx_desmatamento_state ON raw_data.desmatamento (state);
CREATE INDEX idx_desmatamento_source ON raw_data.desmatamento (source);
CREATE INDEX idx_desmatamento_geom ON raw_data.desmatamento USING GIST (geom);