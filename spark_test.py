from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .master("local[*]") \
    .appName("Test") \
    .getOrCreate()

df = spark.createDataFrame([(1, "A"), (2, "B")], ["id", "value"])
df.show()
