from pyspark.sql import SparkSession
from pyspark.sql.functions import col, countDistinct, when

#Spark session
spark = (SparkSession.builder
         .appName("EDSTATS-step")
         .getOrCreate())

# Load csv Dataset
df = (spark.read
  .option("header", "true")
  .option("inferSchema", "true")
  .option("recursiveFileLookup", "true")
  .csv("s3://emr-project3/trusted/"))

# Create temp view from the merged datasets
df.createOrReplaceTempView("trusted_data")

# Create temp view for indicator stats stats by country and indicator
spark.sql("""
  CREATE OR REPLACE TEMP VIEW stats_per_country_indicator AS
  SELECT
    REF_AREA,
    DATABASE_ID,
    AVG(OBS_VALUE)                          AS avg_val,
    percentile_approx(OBS_VALUE, 0.5)       AS median_val,
    MIN(OBS_VALUE)                          AS min_val,
    MAX(OBS_VALUE)                          AS max_val,
    COUNT(*)                                AS count_obs
  FROM trusted_data
  GROUP BY REF_AREA, DATABASE_ID
""")


stats_per_country_indicator = spark.table("stats_per_country_indicator")

# Write the stats_per_country_indicator to s3
(stats_per_country_indicator
  .coalesce(1)                       
  .write
    .option("header", "true")
    .mode("overwrite")
    .partitionBy("DATABASE_ID")
    .csv("s3://emr-project3/refined/stats_country_indicator")
)

# Create temp view for indicator stats stats by country
spark.sql("""
  CREATE OR REPLACE TEMP VIEW stats_per_country AS
  SELECT
    REF_AREA,
    COUNT(OBS_VALUE)                                  AS n_obs,
    AVG(OBS_VALUE)                                    AS mean_obs,
    percentile_approx(OBS_VALUE, 0.5)                  AS median_obs,
    STDDEV(OBS_VALUE)                                 AS stddev_obs,
    MIN(OBS_VALUE)                                    AS min_obs,
    MAX(OBS_VALUE)                                    AS max_obs
  FROM trusted_data
  GROUP BY REF_AREA
  ORDER BY mean_obs DESC
""")

stats_per_country = spark.table("stats_per_country")

# Write the stats_per_country to s3
(stats_per_country
  .coalesce(1)                       
  .write
    .option("header", "true")
    .mode("overwrite")
    .csv("s3://emr-project3/refined/stats_country_global")
)