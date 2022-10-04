import time, os, sys, tempfile

import seldon.core.logging
import seldon.core.spark
import seldon.core.struct
import seldon.core.stdio
import seldon.core.path

class DemoCommands:
  def __init__(self, args):
    self.args = args

  def command_demo(self):
    l = seldon.core.logging.logger()
    spark = seldon.core.spark.spark()

    with tempfile.TemporaryDirectory() as d:
      p = os.path.join(d, 'd.parquet')

      with l.timer("creating a data frame"):
        rows = [ ("Finance", 10), ("Marketing", 20), ("Sales", 30), ("IT", 40)]
        columns = ["dept_name", "dept_id"]
        df = spark.createDataFrame(data=rows, schema=columns)
        l.df(df)
        df.write.mode('overwrite').parquet(p)

      with l.timer("reading data frame"): spark.read.parquet(p)

    with l.section('section'):
      l.info('inside section')
      l.remove('should remove some stuff')

    with l.progress("some progress", 10) as p:
      for i in range(10):
        p.step()

    with l.timer('name'):
      time.sleep(0.1)

    l.exit()
