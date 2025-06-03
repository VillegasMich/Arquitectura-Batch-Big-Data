# info de la materia: ST0263 Tópicos Especiales en Telemática

# Estudiante(s):

- Manuela Castaño - mcastanof1@eafit.edu.co
- Miguel Vásquez - mvasquezb@eafit.edu.co
- Manuel Villegas - mvillegas6@eafit.edu.co

# Profesor:

- Edwin Montoya - emontoya@eafit.edu.co

# Automatización del proceso de Captura, Ingesta, Procesamiento y Salida de datos accionables (Arquitectura Batch para Big Data)

## 1. Breve descripción de la actividad

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
- Consumo de los resultados via API Gateway para su visualización.
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

- Las credenciales se pueden adquirir desde la terminal del laboratorio con el siguiente comando:

```bash
cat .aws/credentials
```

- Asegurarse de iniciar el contenedor con la base de datos Sakila:

```bash
docker run -d --publish 3306:3306 --name mysqld restsql/mysql-sakila
```

- Finalmente, se ejecuta de la siguiente manera:

```bash
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

El bot automáticamente realizará las respectivas consultas y subirá los archivos a la zona `raw` cada 30 minutos (la cuenta academy de AWS tiene límite de 4 horas).

### Parámetros y configuración

#### API Gateway

El API gateway que se implementó fue el dispuesto por AWS con ayuda de `AWS Lambda` para las funciones de extraer los datos **refined** del bucket S3. Los endpoints disponibles son los siguientes:

**root:** `https://pl4uky6vwj.execute-api.us-east-1.amazonaws.com/prod`
**extract-trusted-info:** `https://pl4uky6vwj.execute-api.us-east-1.amazonaws.com/prod/extract-trusted-info`

##### Funciones Lambda

De esta manera y de acuerdo al endpoint correspondiente, se hace la ejecución de la siguiente función lambda:

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

Toda la configuración del bot se puede realizar desde el archivo `main.py`, `s3_upload_files.py` y `data_pool.py`

### Preparación del Cluster y Steps

#### Inicialización

En primer lugar, es necesario que todos los archivos originales provenientes de la fuente de datos, se encuentren en la zona `raw` del bucket S3.

También, es importante que el bucket S3 tenga una carpeta llamada `steps` que contenga todos los scripts de Python que se ejecutarán como steps en el cluster. 

Adicionalmente, dentro del bucket también, se debe crear una carpeta `dependencies` , y adentro, cargar un `script.sh` con todas las librerías y módulos que el EMR necesite, pues estos clusters sólo traen ciertas dependencias instaladas por defecto, pero para la realización de este proyecto se necesitan específicamente las librerías de `numpy` y `pandas` para la correcta ejecución del step de predicciones con sparkML. Un ejemplo de este script puede ser uno que contenga los siguientes comandos:

```
#!/bin/bash
sudo pip3 install numpy pandas
```

El siguiente paso es clonar un cluster EMR pre-configurado que contenga todas las herramientas y programas requeridos. Durante el formulario de creación o clonación, en la sección de **Bootstrap**, es necesario agregar un **Bootstrap Action** que apunte a la URL de S3 donde se encuentre el `script.sh` de instalación de librerías descrito anteriormente. 

Una vez que el cluster esté completamente inicializado, dirígete a la sección de `steps` en la interfaz de EMR. Aquí deberás agregar los scripts de Python en orden. Estos scripts están diseñados para realizar las tareas de preparación y análisis de datos. A continuación, se describen cada uno de ellos:

#### SCRIPT DE PREPARACIÓN DE DATOS
**Nombre del step:** EDSTATS-step.py

El script de preparación de datos es genérico y puede utilizarse para todos los archivos. Este recibe el nombre de un archivo como parámetro al ejecutarse y realiza las siguientes operaciones sobre el archivo especificado en la zona de parámetros:

1. Localiza y extrae el archivo desde la zona `raw` del bucket S3.
2. Rellena los valores nulos en la columna `OBS_VALUE` con 0.0 para no afectar el análisis.
3. Elimina las columnas constantes que no aportan valor al análisis planeado.
4. Reordena las columnas para asegurar que todos los conjuntos de datos sigan el mismo esquema.
5. Guarda el conjunto de datos procesado en la zona `Trusted` de S3.

Deberás de crear un step con este script para cada uno de los archivos que vayas a analizar.

#### SCRIPT DE ANÁLISIS DE DATOS
**Nombre del step:** indicator-analysis.py

Una vez que los datos se encuentran en la zona `Trusted`, el siguiente paso se encargará de analizarlos mediante PySpark SQL para extraer métricas que facilitarán el estudio de los indicadores. Este proceso incluye:

1. Localizar y extraer de forma recursiva los archivos desde la zona `Trusted` del bucket S3.
2. Realizar un análisis de los datos por país y por indicador, identificando los países con mejor desempeño en cada indicador individual.
3. Escribir los resultados en la zona `Refined` por indicador dentro de la carpeta `stats_country_indicator`, organizados por `DATABASE_ID` que identifica el indicador analizado.
4. Realizar un análisis global de todos los indicadores por país, evaluando el desempeño general de cada país considerando todos los indicadores en conjunto.
5. Escribir los resultados globales en la zona `Refined` dentro de la carpeta `stats_country_global`.

Es importante destacar que este script debe ejecutarse en un único paso, ya que realiza el análisis de todos los archivos de manera simultánea.

#### SCRIPT DE PREDICCIÓN DE DATOS
**Nombre del step:** ML_predictions.py

Este script implementa un proceso automatizado de predicción mediante técnicas de aprendizaje automático utilizando SparkML. Está diseñado para ejecutarse sobre los datos previamente limpiados (ubicados en la zona `Trusted` del bucket S3) y generar predicciones que se almacenan organizadamente en la zona Refined. El script ha sido diseñado para ser reutilizable y adaptable a diferentes conjuntos de datos siempre que cumplan con la estructura de entrada esperada.

Las principales tareas que realiza el script son:

1. Accede a los conjuntos de datos almacenados en la zona `Trusted` de S3, aplicando las transformaciones necesarias para preparar los datos para el entrenamiento del modelo.
    
2. Identifica las columnas relevantes para la predicción y construye un vector de características. También realiza transformaciones como la estandarización de valores o la codificación de variables categóricas, si es necesario.

3. Aplica un algoritmo de regresión lineal de SparkML para ajustar un modelo predictivo, dependiendo del tipo de dato de entrada. Este modelo aprende patrones a partir de las variables independientes para predecir la variable objetivo.
    
4. Calcula métricas de desempeño como el error cuadrático medio (RMSE) para evaluar la precisión del modelo sobre los datos de prueba. Esto permite valorar la calidad de las predicciones generadas.
    
5. Aplica el modelo entrenado a los datos nuevos o no vistos, generando predicciones para la variable objetivo.
    
6. Guarda las predicciones junto con las columnas clave del conjunto original en la zona Refined del bucket S3, permitiendo su análisis posterior o visualización en herramientas externas.

Algunas consideraciones importantes son:
- Este step depende de algunas librerías. Por eso es necesario seguir los pasos de la creación de un Bootstrap Action durante el lanzamiento del cluster.
- El script está preparado para funcionar como parte de un pipeline de análisis más amplio. Por tanto, se asume que los datos de entrada han sido previamente limpiados y estructurados correctamente.
- A diferencia de otros scripts que operan archivo por archivo, este script puede configurarse para ejecutarse sobre múltiples conjuntos de datos si se adapta la lógica de carga y filtrado inicial.


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
### Consumo por medio de AWS Athena
Athena nos permite acceder a nuestros datos almacenados en S3 mediante consultas SQL, lo cual facilita la creación de tablas para el análisis y manipulación de los datos. Los scripts para crear las tablas:

> Nota: Es necesario configurar previamente un objeto de salida en S3 para que las consultas puedan ejecutarse correctamente.

1. Creación de las tablas de paises por indicador.

      ```sql
      CREATE EXTERNAL TABLE IF NOT EXISTS refined.stats_country_indicator_${filename} (
        REF_AREA string,
        avg_val double,
        median_val double,
        min_val double,
        max_val double,
        count_obs int
      )
      ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
      WITH SERDEPROPERTIES (
        "separatorChar" = ",",
        "quoteChar"     = "\""
      )
      LOCATION 's3://emr-project3/refined/stats_country_indicator/DATABASE_ID=${filename}/'
      TBLPROPERTIES ('skip.header.line.count'='1');
      ```
2. Creación de la tabla de países tomando en cuenta todos los indicadores.

      ```sql
      CREATE EXTERNAL TABLE IF NOT EXISTS refined.stats_per_country (
        REF_AREA string,
        avg_val double,
        median_val double,
        min_val double,
        max_val double,
        count_obs int
      )
      ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
      WITH SERDEPROPERTIES (
        "separatorChar" = ",",
        "quoteChar"     = "\""
      )
      LOCATION 's3://emr-project3/refined/stats_country_global/'
      TBLPROPERTIES ('skip.header.line.count'='1');
      ```



## 4. Descripción del ambiente de EJECUCIÓN

- Lenguaje: Python 3.\*, Spark 3.3.0
- Librerías:
  - `pyspark`, `boto3`, `matplotlib`, `pandas`, `numpy`
- Infraestructura:
  - AWS EMR Cluster (Spark)
  - Buckets S3 (zonas Raw, Trusted, Refined)
  - API Gateway

## 5. Otra información relevante

### Descripción de la fuente de datos utilizada

Los datos usados en este proyecto provienen de [World Bank Open Data](https://data.worldbank.org/), una fuente confiable que ofrece indicadores globales para el análisis del desarrollo socioeconómico y ambiental. Nos enfocamos en tres conjuntos de indicadores: WDI, ESG y SE4ALL, que permiten estudiar diferentes aspectos como salud, emisiones de carbono y acceso a electricidad.

El indicador WDI (World Development Indicators) mide la esperanza de vida al nacer, que representa los años promedio que viviría un recién nacido si las condiciones de mortalidad actuales se mantienen constantes. Este dato es crucial para evaluar la salud y el desarrollo socioeconómico de un país.

El indicador ESG (Environment, Social & Governance) incluye las emisiones de CO2 per cápita, que reflejan el impacto ambiental de la quema de combustibles fósiles y la producción industrial. Este indicador es fundamental para entender la contribución de cada país al cambio climático global.

Finalmente, el indicador SE4ALL (Sustainable Energy For All) mide el porcentaje de la población con acceso a electricidad. Este dato es clave para evaluar el progreso hacia el acceso universal a energía confiable y sostenible, un aspecto esencial para el desarrollo social y económico.

### Gráficas

### De analítica con Spark
![observation_statis_country_global](https://github.com/user-attachments/assets/58cce1d3-b155-4e9f-a884-e8597b7299b2)
![observation_summary_stats_ESG](https://github.com/user-attachments/assets/68cefa6b-ed9f-47be-b17d-db4fe228c919)
![observation_summary_stats_SE4ALL](https://github.com/user-attachments/assets/2c8fa13f-b56c-4315-ba63-a0fd16806423)
![observation_summary_stats_WDI](https://github.com/user-attachments/assets/149bae8e-5f3d-48d6-b3df-bbf7df227503)

### De predicción con Machine Learning usando SparkML

Resultados del modelo implementado para cada indicador

![image](https://github.com/user-attachments/assets/3b94df79-1406-474b-bf9b-1898605912e6)
![image](https://github.com/user-attachments/assets/02f35992-7a15-4136-86ac-173618aac9fc)
![image](https://github.com/user-attachments/assets/d750bf3b-e391-4eea-8a3d-864b94b83ee4)


## Referencias

- [Github de la materia con tutoriales](https://github.com/st0263eafit/st0263-251/tree/main/bigdata/03-spark)
- [Caso base en GitHub y video YouTube](https://github.com/airscholar/EMR-for-data-engineers/tree/main)
- [Documentación oficial AWS EMR](https://docs.aws.amazon.com/emr/latest/ManagementGuide/emr-what-is-emr.html)
- [Tutorial Spark](https://www.databricks.com/spark/getting-started-with-apache-spark/machine-learning)
- [Inteligencia Artificial para mejorar redacción y buenas prácticas en código](https://chatgpt.com/)

### Datos de World Bank Open Data

- [Indicador de WDI](https://data360.worldbank.org/en/indicator/WB_WDI_SP_DYN_LE00_IN)
- [Indicador de ESG](https://data360.worldbank.org/en/indicator/WB_ESG_EN_ATM_CO2E_PC)
- [Indicador de SE4ALL](https://data360.worldbank.org/en/indicator/WB_SE4ALL_EG_ACS_ELEC)
  
