#!/usr/bin/env python3.8
import os.path
import sys

import findspark

import seldon.core.logging
import seldon.core.utils

findspark.init()
from pyspark.sql import SparkSession

logger = None

# global settings
settings = {
  'name': seldon.core.app.name(),
  'driver_memory': '16g',
  'executor_memory': '52g',
  'max_result_size': '32g',
  'spark': None,
}

def spark(**args):
  """Get/create a spark object"""

  global settings, logger
  if logger is None: logger = seldon.core.logging.logger()

  # return the one already in place if it's already present
  if settings['spark'] is not None: return settings['spark']

  # take care of defaults
  settings.update(args)

  with logger.timer('getting spark'):
    # I can't seem to turn off all this initial logging to stdout, so at least wall it off with some *****
    sys.stderr.write('#' * 100 + "\n")
    sys.stderr.write("messy spark logging I cannot remove- just ignore it\n")

    # noinspection PyTypeChecker,PyTypedDict
    spark = settings['spark'] = SparkSession.builder.appName(
      str(settings['name'])
    ).config(
      'spark.ui.killEnabled', 'false'
    ).config(
      'spark.driver.memory', settings['driver_memory']
    ).config(
      'spark.executor.memory', settings['executor_memory']
    ).config(
      'spark.driver.maxResultSize', settings['max_result_size']
    ).getOrCreate()
    sys.stderr.write('#' * 100 + "\n")
    return spark
