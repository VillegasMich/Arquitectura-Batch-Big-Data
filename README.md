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

- Asegurarse de inicial el contenedor con la base de datos Sakila

```bash
docker run -d --publish 3306:3306 --name mysqld restsql/mysql-sakila
```

- Finalmente se ejecuta de la siguiente manera:

```bash
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

El bot automaticamente realizará las respectivas consultas y subirá los archivos a la zona `raw` cada 30 minutos (la cuenta academy de AWS tiene límite de 4 horas)

### Parámetros y configuración

#### API Gateway

El API gateway que se implementó fue el dispuesto por AWS con ayuda de `AWS Lambda` para las fuciones de extraer los datos **refined** del bucket S3. los enpoints disponibles son los siguientes:

**root:** `https://pl4uky6vwj.execute-api.us-east-1.amazonaws.com/prod`
**extract-trusted-info:** `https://pl4uky6vwj.execute-api.us-east-1.amazonaws.com/prod/extract-trusted-info`

##### Funciones Lambda

De esta manera y de acuerdo al endpoint correspondiente, se hace la ejecucion de la siguiente función lambda:

![image](https://github.com/user-attachments/assets/e1bf31ca-251d-4f57-ad24-56231c245a5a)

```python
import json
import boto3

AWS_BUCKET_NAME = "emr-project3"
AWS_TRUSTED_PREFIX = "refined/"
AWS_REGION = "us-east-1"

s3 = boto3.client("s3", region_name=AWS_REGION)

def lambda_handler(event, context):
    try:
        # List objects in the trusted/ prefix
        response = s3.list_objects_v2(Bucket=AWS_BUCKET_NAME, Prefix=AWS_TRUSTED_PREFIX)

        if "Contents" not in response:
            return {
                "statusCode": 200,
                "body": json.dumps({})
            }

        files = [obj["Key"] for obj in response["Contents"] if obj["Key"].endswith(".csv")]

        result = {}

        # Read the contents of each CSV file
        for file_key in files:
            obj = s3.get_object(Bucket=AWS_BUCKET_NAME, Key=file_key)
            content = obj["Body"].read().decode("utf-8")
            result[file_key] = content

        return {
            "statusCode": 200,
            "body": json.dumps(result),
            "headers": {
                "Content-Type": "application/json"
            }
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)}),
            "headers": {
                "Content-Type": "application/json"
            }
        }
```

#### Python Bot

Toda la configuracion del bot se puede reailzar desde el archivo `main.py`, `s3_upload_files.py` y `data_pool.py`

### Organización del proyecto

#### Python Bot

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

#### Consumo de API Gateway y Gráficas

```bash
.
├── results/
│   └── <file>.png # resultados de la analítica
├── main.py # punto de entrada de ejecución
├── api_requester.py # clase encargada de peticiones a la API Gateway
```

## 4. Descripción del ambiente de EJECUCIÓN

- Lenguaje: Python 3.\*, Spark 3.3.0
- Librerías:
  - `pyspark`, `boto3`, `matplotlib`, `pandas`
- Infraestructura:
  - AWS EMR Cluster (Spark)
  - Buckets S3 (zonas Raw, Trusted, Refined)
  - API Gateway

### Cómo usar la aplicación

## 5. Otra información relevante

### Gráficas
![observation_statis_country_global](https://github.com/user-attachments/assets/58cce1d3-b155-4e9f-a884-e8597b7299b2)
![observation_summary_stats_ESG](https://github.com/user-attachments/assets/68cefa6b-ed9f-47be-b17d-db4fe228c919)
![observation_summary_stats_SE4ALL](https://github.com/user-attachments/assets/2c8fa13f-b56c-4315-ba63-a0fd16806423)
![observation_summary_stats_WDI](https://github.com/user-attachments/assets/149bae8e-5f3d-48d6-b3df-bbf7df227503)

## Referencias

- [Caso base en GitHub y video YouTube](https://github.com/airscholar/EMR-for-data-engineers/tree/main)
- [Documentación oficial AWS EMR](https://docs.aws.amazon.com/emr/latest/ManagementGuide/emr-what-is-emr.html)

```

```
