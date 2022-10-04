#!/usr/bin/env python3.8

import time, os, sys

import seldon.core.logging
import seldon.core.spark
import seldon.core.struct
import seldon.core.stdio

import io
s= io.StringIO()
print(s)
print(sys.stderr)
l = seldon.core.logging.logger(handlers=[s, 'junk2.txt', 'stderr'])
l.info('wazoo')
print("========================")
print(s.getvalue())
sys.exit()
#spark = core.spark.spark()

# with l.timer("creating spark"):
#   with seldon.core.stdio.RedirectStdStreams(stdout=open('out','w'), stderr=open('err','w')):
#     print("You'll never see me")
#     # from pyspark.sql import SparkSession
#     # spark = SparkSession.builder.appName('SparkApp').getOrCreate()
#     spark = seldon.core.spark.spark()
#
#
# with l.timer("reading data frame"):
#   df = spark.read.parquet('junk.parquet')
#
# with l.timer("creating a data frame"):
#     rows = [
#         ("Finance",10),
#         ("Marketing",20),
#         ("Sales",30),
#         ("IT",40)
#     ]
#     columns = ["dept_name","dept_id"]
#     # spark = SparkSession.builder.appName('SparkApp').getOrCreate()
#     df = spark.createDataFrame(data=rows, schema = columns)
#     l.df(df)
#     df.write.mode('overwrite').parquet('junk.parquet')

with l.section('section'):
  l.info('inside section')
  l.remove('should remove some stuff')
with l.progress("some progress", 10) as p:
  for i in range(10):
    p.step()
with l.timer('name'):
  time.sleep(1)
l.exit()