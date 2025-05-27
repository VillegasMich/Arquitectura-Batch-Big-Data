from pyspark.sql import SparkSession
from pyspark.sql.functions import col, countDistinct
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--file', required=True, help='S3 URI del CSV de entrada')
args = parser.parse_args()

#Spark session
spark = (SparkSession.builder
         .appName("EDSTATS-step")
         .getOrCreate())

#Read data  
df=spark.read.csv(f's3://emr-project3/raw/{args.file}.csv',inferSchema=True,header=True)

#Fill null values with 0.0
df = df.fillna({'OBS_VALUE':0.0})

#Remove constant columns
const_cols = []
for c in df.columns:
    distinct_vals = df.agg(countDistinct(col(c)).alias("n")).collect()[0].n
    if distinct_vals <= 1:  
        const_cols.append(c)

const_cols = [c for c in const_cols if c != "DATABASE_ID"]

#Drop columns
drop_cols = set(const_cols)
df = df.drop(*drop_cols)

# Order columns to match the expected schema
ordered_cols = ["DATABASE_ID", "TIME_PERIOD", "OBS_VALUE", "REF_AREA"]
df = df.select(ordered_cols)

#Write data
df_clean_coal = df.coalesce(1)
output_path = f"s3://emr-project3/trusted/{args.file}/"

if len(df_clean_coal.columns) > 0:
    df_clean_coal.write \
        .option("header","true") \
        .mode("overwrite") \
        .csv(output_path)
else:
    print("No columns left after dropping constant columns. Skipping write.")
