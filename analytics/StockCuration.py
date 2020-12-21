from pyspark.sql import SparkSession
from pyspark.sql import SQLContext
import numpy as np

spark = SparkSession.builder.appName('StockCuration').getOrCreate()
ctx = SQLContext(spark)

quotes = ctx.read.load('s3n://nbachmei.finsurf.data-us-west-2/data/csv/L2_stockquotes*.csv', header='true',inferSchema='true',format='csv')

import pyspark.sql.functions as F
@F.udf
def fix_date(dt):    
    if dt is None:
        return dt
    parts = dt.split('/')
    return "{}-{}-{}".format(parts[2],parts[0],parts[1])

curated = quotes.withColumn('dt',fix_date(F.col('quotedate')))
curated = curated.withColumn('year', F.year(F.col('dt')))
curated = curated.withColumn('quarter', F.quarter(F.col('dt')))

curated.show()

joined = curated.alias('alpha').join(curated.alias('beta'), ['year','quarter','dt']).select(
    F.col('alpha.year').alias('year'),
    F.col('alpha.quarter').alias('quarter'),
    F.col('alpha.dt').alias('dt'),
    
    F.col('alpha.symbol').alias('alpha_symbol'),
    F.col('alpha.dt').alias('alpha_dt'),
    F.col('alpha.open').alias('alpha_open'),
    F.col('alpha.high').alias('alpha_high'),
    F.col('alpha.low').alias('alpha_low'),
    F.col('alpha.close').alias('alpha_close'),
    F.col('alpha.volume').alias('alpha_volume'),
    
    F.col('beta.symbol').alias('beta_symbol'),
    F.col('beta.open').alias('beta_open'),
    F.col('beta.high').alias('beta_high'),
    F.col('beta.low').alias('beta_low'),
    F.col('beta.close').alias('beta_close'),
    F.col('beta.volume').alias('beta_volume'),
)

# Remove joinedicate mappings
joined = joined.filter(F.col('alpha_symbol') < F.col('beta_symbol'))
joined.write.parquet("s3n://nbachmei.finsurf.data-us-west-2/spark/Quotes/joined")