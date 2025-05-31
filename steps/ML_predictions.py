from pyspark.sql import SparkSession
from pyspark.ml.feature import StringIndexer, OneHotEncoder, VectorAssembler
from pyspark.ml.regression import LinearRegression, GBTRegressor
from pyspark.ml import Pipeline
from pyspark.ml.evaluation import RegressionEvaluator

spark = SparkSession.builder.appName("EntrenamientoModelosMultiples").getOrCreate()

#datasets a procesar
datasets = {
    "WDI": "s3://emr-project3/trusted/WB_WDI/",
    "ESG": "s3://emr-project3/trusted/WB_ESG/",
    "SE4ALL": "s3://emr-project3/trusted/WB_SE4ALL/"
}

output_base = "s3://emr-project3/refined/ml_predictions/"

for name, path in datasets.items():
    
    df = spark.read.csv(path, header=True, inferSchema=True)

    #indexar y codificar
    indexer = StringIndexer(inputCol="REF_AREA", outputCol="REF_AREA_INDEX")
    encoder = OneHotEncoder(inputCols=["REF_AREA_INDEX"], outputCols=["REF_AREA_VEC"])
    assembler = VectorAssembler(inputCols=["REF_AREA_VEC", "TIME_PERIOD"], outputCol="features")

    #modelos
    if name == "SE4ALL":
        model = GBTRegressor(featuresCol="features", labelCol="OBS_VALUE", maxIter=100)
    else:
        model = LinearRegression(featuresCol="features", labelCol="OBS_VALUE")

    pipeline = Pipeline(stages=[indexer, encoder, assembler, model])

    #entrenamiento
    pipeline_model = pipeline.fit(df)
    predictions = pipeline_model.transform(df)

    #evaluacion
    evaluator = RegressionEvaluator(labelCol="OBS_VALUE", predictionCol="prediction", metricName="r2")
    r2 = evaluator.evaluate(predictions)

    #guardar predicciones
    output_path = f"{output_base}{name}/predictions"
    predictions.select("REF_AREA", "TIME_PERIOD", "OBS_VALUE", "prediction") \
        .write.mode("overwrite").csv(output_path, header=True)

spark.stop()
