# Pipeline ETL - Dados de Desmatamento do PRODES/Cerrado

Pipeline para extração, transformação e carga (ETL) de dados geoespaciais de desmatamento do TerraBrasilis.

## 📋 Pré-requisitos
- **Docker e Docker Compose** (para o banco de dados).
- **Python 3.8+** (para execução do script).
- **Bibliotecas Python**: Instaladas via `requirements.txt`.

## 🚀 Configuração

### 1. Banco de Dados (PostgreSQL/PostGIS)
```bash
# Subir o contêiner
docker-compose up -d

# Verificar status
docker ps -a | grep postgis_container
```
### 2. Instalar dependências
pip install -r requirements.txt

### 3. execução
python main.py