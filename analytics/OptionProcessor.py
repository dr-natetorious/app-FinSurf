"""
This is a Spark script for curating the historical options
"""

sc.install_pypi_package('scipy')

from pyspark.sql import SparkSession
from pyspark.sql import SQLContext
import numpy as np

spark = SparkSession.builder.appName('MapRedBook').getOrCreate()
ctx = SQLContext(spark)

options = ctx.read.load('s3n://nbachmei.finsurf.data-us-west-2/data/csv/L2_options_*.csv', 
  header="true",
  inferSchema="true",
  format="csv")

import pyspark.sql.functions as F
import datetime
import numpy as np
import scipy.stats as si

@F.udf
def fix_date(dt):    
    if dt is None:
        return dt
    parts = dt.split('/')
    return "{}-{}-{}".format(parts[2],parts[0],parts[1])
    
@F.udf
def dte(date,expiration):
    date = datetime.datetime.strptime(date,'%m/%d/%Y')
    expiration = datetime.datetime.strptime(expiration,'%m/%d/%Y')
    return (expiration - date).days / 365.0

@F.udf
def euro_vanilla(S, K, T, sigma, option):
    import numpy as np
    import scipy.stats as si
    import math
    
    #S: spot price
    #K: strike price
    #T: time to maturity
    #r: interest rate
    #sigma: volatility of underlying asset
    
    print("S={}, K={}, T={}, sigma={}, option={}".format(S, K, T, sigma, option))
    
    r= 0.01
    
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = (np.log(S / K) + (r - 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    print('d1={}, d2={}'.format(d1,d2))
    
    if option == 'call':                
        result = S * si.norm.cdf(d1, 0.0, 1.0) - K * np.exp(-r * T) * si.norm.cdf(d2, 0.0, 1.0)
    if option == 'put':
        result = K * np.exp(-r * T) * si.norm.cdf(-d2, 0.0, 1.0) - S * si.norm.cdf(-d1, 0.0, 1.0)
    return str(round(result,4))

curated = options.drop('OptionExt','AKA','Exchange')
curated = curated.withColumn('dt', fix_date(F.col('DataDate')))
curated = curated.withColumn('exp', fix_date(F.col('Expiration')))
curated = curated.withColumn('year', F.year(F.col('dt')))
curated = curated.withColumn('dte', dte(F.col('DataDate'), F.col('Expiration')).cast('double'))
curated = curated.withColumn('theo', euro_vanilla(
    F.col('UnderlyingPrice'), # S
    F.col('Strike'), # K
    F.col('dte'), # T
    F.col('IV'), #sigma
    F.col('Type') #option
).cast('double'))

curated.show(20,False)
#euro_vanilla(75.91)
curated.printSchema()
curated.write.parquet("s3n://nbachmei.finsurf.data-us-west-2/spark/OptionPrices/")
