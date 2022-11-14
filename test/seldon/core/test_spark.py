import os.path
import tempfile

import pytest
import seldon.core.spark


@pytest.mark.slow
def test_spark():
  seldon.core.spark.spark()


@pytest.mark.slow
def test_data_frames():
  rows = [
      ("Finance",10),
      ("Marketing",20),
      ("Sales",30),
      ("IT",40)
  ]
  columns = ["dept_name","dept_id"]
  spark = seldon.core.spark.spark()
  df1 = spark.createDataFrame(data=rows, schema=columns).orderBy('dept_name')
  with tempfile.TemporaryDirectory() as d:
    p1 = os.path.join(d, 'junk.parquet')
    df1.write.mode('overwrite').parquet(p1)
    df2 = spark.read.parquet(p1)
    for row in zip(df1.collect(), df2.collect()):
      assert(row[0] == row[1])
