# info de la materia: ST0263 Tópicos Especiales en Telemática

# Estudiante(s):

- Manuela Castaño - mcastanof1@eafit.edu.co
- Miguel Vásquez - mvasquezb@eafit.edu.co
- Manuel Villegas - mvillegas6@eafit.edu.co

# Profesor:

- Edwin Montoya - emontoya@eafit.edu.co

# Automatización del proceso de Captura, Ingesta, Procesamiento y Salida de datos accionables (Arquitectura Batch para Big Data)

## 1. breve descripción de la actividad

Este proyecto implementa una arquitectura tipo batch en la nube para la captura, ingesta, procesamiento y análisis de datos a gran escala, automatizando cada etapa sin intervención humana. El objetivo es simular un proceso de ingeniería de datos real utilizando servicios cloud (AWS EMR, S3, Athena, API Gateway, entre otros) y fuentes de datos externas (APIs públicas, archivos en línea y bases de datos relacionales).

### 1.1. Qué aspectos cumplió o desarrolló de la actividad propuesta por el profesor

- Captura automática de datos desde:
  - API externa (ej: data-360).
  - Base de datos relacional (MySQL - Sakila) simulada.
- Ingesta de los datos capturados en buckets S3, zona `Raw`.
- Creación automatizada del clúster EMR (mediante scripts).
- Ejecución de procesos ETL automáticos con Apache Spark (Steps de EMR).
- Almacenamiento del resultado en zona `Trusted`.
- Análisis descriptivo y analítica con SparkSQL y SparkML.
- Resultados enviados automáticamente a la zona `Refined` en S3.
- Documentación del proceso en este archivo README.
- Video de sustentación y scripts completos en el repositorio.

### 1.2. Qué aspectos NO cumplió o desarrolló de la actividad propuesta por el profesor

- El clúster EMR fue probado manualmente en etapas intermedias antes de automatizar.
- No se exploraron todas las fuentes de datos opcionales por tiempo y alcance.

## 2. Información general de diseño de alto nivel

- Arquitectura batch sobre AWS:
  - Captura y almacenamiento en S3 (zona Raw).
  - Procesamiento ETL con Spark sobre EMR (zona Trusted).
  - Análisis y resultados en S3 (zona Refined).
- Automatización con scripts en Bash y Python.
- Uso de buenas prácticas:
  - Estructura por módulos.
  - Logging y manejo de errores.

## 3. Descripción del ambiente de desarrollo y técnico

- Lenguaje principal: Python 3.\*
- Scripts: PySpark
- Librerías:
  - `boto3`, `requests`, `pyspark`
- Plataforma cloud: AWS Academy
- Base de datos: MySQL 5 (docker image `restsql/mysql-sakila`)

### Compilación y ejecución

#### Ejecución del bot python para ingesta automática de datos

- Completar las credenciales en el archivo `s3_upload_files.py`

```python
AWS_ACCESS_KEY = ""
AWS_SECRET_KEY = ""
AWS_SESSION_TOKEN = ""
```

- Las credenciales se pueden adquirir desde la terminar del laboratorio con el siguiente comando

```bash
cat .aws/credentials
```

- Finalmente se ejecuta de la siguiente manera:

```bash
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

El bot automaticamente realizará las respectivas consultas y subirá los archivos a la zona `raw` cada 30 minutos (la cuenta academy de AWS tiene límite de 4 horas)

### Parámetros y configuración

#### Python Bot

Toda la configuracion del bot se puede reailzar desde el archivo `main.py`, `s3_upload_files.py` y `data_pool.py`

### Organización del proyecto (Python Bot)

```bash
.
├── csv_outputs/
│   └── <file>.csv # resultados de la consulta en csv
├── json_outputs/
│   └── <file>.json # resultados de la consulta en json
├── main.py # punto de entrada de ejecución
├── s3_upload_files.py # clase encargada de montar los archivos a S3
├── json_csv_converter.py # clase encargada de convertir el json en archivos csv
├── data_pool.py # arreglos de id de bases de datos y nombres de tablas
├── api_requester.py # clase encargada de peticiones a la API
├── db_requester.py # clase encargada de peticiones a la BD
├── yf_requester.py # clase encargada de peticiones a Yahoo Finance (No utilizada)
├── README.md # Documentación
```

## 4. Descripción del ambiente de EJECUCIÓN

- Lenguaje: Python 3.\*, Spark 3.3.0
- Librerías:
  - `pyspark`, `boto3`
- Infraestructura:
  - AWS EMR Cluster (Spark)
  - Buckets S3 (zonas Raw, Trusted, Refined)

### Cómo usar la aplicación

## 5. Otra información relevante

## Referencias

- [Caso base en GitHub y video YouTube](https://github.com/airscholar/EMR-for-data-engineers/tree/main)
- [Documentación oficial AWS EMR](https://docs.aws.amazon.com/emr/latest/ManagementGuide/emr-what-is-emr.html)
