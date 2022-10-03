import os
import sys
import time
import types
from contextlib import contextmanager
import traceback
import builtins
import logging

#import core.utils

import pandas as pd

# the default logger
global_logger = None

"""
Useful additions to logging to
For an example on how to use this, call 'logging_demo'. It gets you output somewhat like this
    program |     INFO | 2020-12-20 12:44:45,299 | start this is timed
    program |     INFO | 2020-12-20 12:44:46,403 | end   this is timed - finished in 1.1 seconds
    program |     INFO | 2020-12-20 12:44:46,403 | start this is progressed
    program |     INFO | 2020-12-20 12:44:46,907 |   Step 1 of 5 [ 20.0%] -- done in   2.0  s
    program |     INFO | 2020-12-20 12:44:47,410 |   Step 2 of 5 [ 40.0%] -- done in   1.5  s
    program |     INFO | 2020-12-20 12:44:47,913 |   Step 3 of 5 [ 60.0%] -- done in   1.0  s
    program |     INFO | 2020-12-20 12:44:48,416 |   Step 4 of 5 [ 80.0%] -- done in 503.1 ms
    program |     INFO | 2020-12-20 12:44:48,919 |   Step 5 of 5 [100.0%] -- done in   0.0 µs
    program |     INFO | 2020-12-20 12:44:48,919 | end   this is progressed - finished in 2.5  s   [503.1 ms per step]
    program |  WARNING | 2020-12-20 12:44:48,920 | TODO: remove code near lib/rippleshot/logging.py:225 | We should remove the following exit
    program | CRITICAL | 2020-12-20 12:44:48,920 | EXIT: from lib/rippleshot/logging.py:226 | That's all folks
"""


def logger(level=logging.INFO, path=None, add_std_err=True):
  global global_logger
  if global_logger is None: global_logger = create(level, path, add_std_err)
  return global_logger


def create(level=logging.INFO, path=None, add_std_err=True):
  """
      Set up logger and adda bunch of methods to it

      Extra methods
      exit - log that we are doing a sys.exit (plus actually call that)
      remove - log a future request to remove some code
      progress - start a progress as a context manager
      timer - start a timer as a context manager
  """
  # Set up the basic logger with formatting the way I like
  def_path = os.path.join(os.path.dirname(os.path.abspath('')), 'log')
  log_path = os.path.expanduser(path or def_path)
  name = os.path.basename(sys.argv[0]).replace('.py', '')

  handlers = [logging.FileHandler(log_path)]
  if add_std_err: handlers.append(logging.StreamHandler(sys.stderr))

  logging.basicConfig(
    level=level,
    # format=name + " | {levelname:<8s} | {asctime:s} | {indent_string:{indent_fill}{indent}}{message:s}",
    format=name + " | {levelname:<8s} | {asctime:s} | {indent_string:<{indent}s}{message:s}",
    # format=name + " | %(levelname)8s | %(asctime)s | %(message)s",
    style='{',
    handlers=handlers
  )
  logging.indent = 0

  # add in our extra indent variables
  old_factory = logging.getLogRecordFactory()

  def record_factory(*args, **kwargs):
    record = old_factory(*args, **kwargs)
    record.indent = logging.indent
    record.indent_fill = '.'
    record.indent_string = ''
    return record

  logging.setLogRecordFactory(record_factory)

  def add():
    logging.indent += 2

  def sub():
    logging.indent -= 2

  old_getLogger = logging.getLogger

  def newGetLogger(name=None):
    name = name or sys.argv[0]
    ret = old_getLogger(name)
    ret.add = add
    ret.sub = sub
    return ret

  logging.getLogger = newGetLogger

  ret = logging.getLogger(name)
  ret.info(name + ' logging - log saved at ' + log_path)

  # noinspection PyUnusedLocal
  def _from(target):
    """Standard way to say where the log call was made from"""
    fi = traceback.extract_stack()[-3]
    root = os.path.dirname(
      os.path.dirname(
        os.path.abspath(
          os.path.expanduser(
            sys.argv[0]
          )
        )
      )
    )
    return fi.filename.replace(root, '').lstrip('/') + ':' + str(fi.lineno)
  ret.source = types.MethodType(_from, ret)

  # Add a bunch of methods to the logger item
  def _exit(target, message=None):
    """Log that we are calling sys.exit"""
    msg = "EXIT: from " + target.source()
    if message is not None: msg += ' | ' + message
    target.critical(msg)
    sys.exit()
  ret.exit = types.MethodType(_exit, ret)

  def _remove(target, message=None):
    """Log that we should remove some lines of code"""
    msg = 'TODO: remove code near: ' + target.source()
    if message is not None: msg += ' | ' + message
    target.warn(msg)
  ret.remove = types.MethodType(_remove, ret)

  def _here(target, message=None):
    """Log where the call was"""
    msg = 'HERE: ' + target.source()
    if message is not None: msg += ' | ' + message
    target.debug(msg)
  ret.here = types.MethodType(_here, ret)

  @contextmanager
  def _section(target, title=None):
    """launch a progress inside the logger"""
    target.info(title)
    target.add()
    yield
    target.sub()
  ret.section = types.MethodType(_section, ret)

  @contextmanager
  def _progress(target, title=None, length=None, update_dt=0):
    """launch a progress inside the logger"""
    if length == 0:
      # don't set up anything here or do any cleanup
      yield None
    else:
      # logging_progress(target, title=name, length=length, update_dt=update_dt)
      # noinspection PyProtectedMember,PyUnresolvedReferences
      title = title or sys._getframe(2).f_code.co_name
      lp = LoggingProgress(target, length, update_dt, title)
      yield lp
      lp.stop()
  ret.progress = types.MethodType(_progress, ret)

  @contextmanager
  def _timer(target, title=None):
    """Launch a timer in the logger"""
    # noinspection PyProtectedMember,PyUnresolvedReferences
    title = title or sys._getframe(2).f_code.co_name
    t0 = time.time()
    target.info('START ' + title)
    target.add()
    yield
    target.sub()
    dt = time.time() - t0
    msg = ('ENDED ' + title)
    if dt > 1: msg += ' - finished in ' + LoggingProgress.human_time(dt)
    target.info(msg)
  ret.timer = types.MethodType(_timer, ret)

  def _pp(target, obj):
    """put pretty print to the logger."""
    for line in jom.utils.pp(obj, as_string=True).split("\n"):
      target.info(line)
  ret.pp = types.MethodType(_pp, ret)

  def _df_describe(target, df):
    """Run describe on a dataframe, but transpose it and send to the logger. Cool for lots of described columns."""
    pd.set_option('display.width', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    for line in str(df.describe().toPandas().transpose()).split("\n"):
      target.info(line)
  ret.df_describe = types.MethodType(_df_describe, ret)

  def _df_show(target, df, n=None, truncate=200, vertical=False, indent=0):
    """Run show on a dataframe, but output to the logger."""
    if n is None: n = df.count()
    # noinspection PyProtectedMember
    ind = ' ' * indent
    show = df._jdf.showString(n, truncate, vertical)
    for line in show.split("\n"):
      if line.strip() != '':
        target.info(ind + line)

  ret.df_show = types.MethodType(_df_show, ret)

  def _multi(target, multi, n=None, truncate=200, vertical=False, indent=0):
    """show a multi-line behemoth"""
    multi = multi.split("\n")
    if n is None: n = len(multi)
    # noinspection PyProtectedMember
    ind = ' ' * indent
    i = 0
    for line in multi:
      if line.strip() != '':
        target.info(ind + line)
        i += 1
        if i > n: break

  ret.multi = types.MethodType(_multi, ret)

  # TODO: does not get any formatting!
  def _add_handler(target, handler):
    target.logger.parent.handlers = list(set(ret.logger.parent.handlers + [handler]))

  ret.add_handler = types.MethodType(_add_handler, ret)

  def _remove_handler(target, handler):
    try:
      target.logger.parent.handlers.remove(handler)
    except ValueError:
      target.warn("tried to remove handler '{}' when it was not in the current handlers".format(str(handler)))

  ret.remove_handler = types.MethodType(_remove_handler, ret)

  # Finally, pass back our beefed-up logger
  global global_logger
  if global_logger is None: global_logger = ret

  return ret


class LoggingProgress:
  """
  Progress in the context of logging. Used by logging_logger
  """

  def __init__(self, this_logger, length=None, update_dt=30, title=None):
    """
        Start a logging process
        logger - a logging item
        length - the total steps in this porgress, None if indeterminate
        update_dt - how often to print lines on the logger, 0 for every time next is called
    """
    if length is not None and (length != int(length) or length < 0):
      msg = "Bad length (must be positive integer): {}".format(length)
      print([length])
      raise Exception(msg)
    self.logger = this_logger
    self.length = length
    self.update_dt = update_dt
    flen = str(len(str(self.length or 0)))
    self.fmt = "{:" + flen + ",}"

    # kick it off
    self.t0 = time.time()
    self.t_last = self.t0
    self.pos = 0
    self.name = title
    out = 'START'
    if title is not None: out += ' ' + title
    self.logger.info(out)
    self.logger.add()

  @staticmethod
  def human_time(seconds):
    # TODO: move to numeric
    """
        Human-style formatting of elapsed seconds
        seconds - elapsed seonds
        returns a formatted string humans can read
    """
    if seconds < 1e-3 * 0.8:
      return '{:.1f} µs'.format(seconds * 1000 * 1000)
    if seconds < 1 * 0.8:
      return '{:.1f} ms'.format(seconds * 1000)
    if seconds < 60 * 0.8:
      return '{:.1f}  s'.format(seconds)
    if seconds < 60 * 60 * 0.8:
      return '{:.1f}  m'.format(1.0 * seconds / 60)
    if seconds < 24 * 60 * 60 * 0.8:
      return '{:.1f}  h'.format(1.0 * seconds / 60 / 60)
    return '{:.1f} days'.format(1.0 * seconds / 60 / 60 / 24)

  def goto(self, position, message=None, force=False, warn=False):
    """
        Move to a specific step in the progress
        message - the message to display or None if no message
        force - force the display
        warn - True if we MUST print this messsage (to display as a warning)
    """
    self.pos = position
    if time.time() - self.t_last < self.update_dt and not force and not warn: return
    elapsed = time.time() - self.t0
    if self.length is None:
      out = "Step {:,}".format(self.pos)
      if message is not None: out += " | " + str(message)
    else:
      eta = self.human_time((self.length - self.pos) / self.pos * elapsed)
      fmt = "Step {} of {}".format(self.fmt, self.fmt) + " [{:5.1f}%] -- done in {:>8s}"
      out = fmt.format(
        self.pos,
        self.length,
        100.0 * self.pos / self.length,
        eta
      )
      if message is not None:
        out += " | " + str(message)
    if warn:
      self.logger.warn(out)
    else:
      self.logger.info(out)
    self.t_last = time.time()

  def next(self, message=None, force=False, warn=False):
    """
        Next step in the progress
        message - the message to display or None if no message
        force - force the display
        warn - True if we MUST print this messsage (to display as a warning)
    """
    self.goto(self.pos + 1, message, force, warn)

  def stop(self):
    """
        Finish the progress
    """
    self.logger.sub()

    out = 'ENDED '
    if self.name is not None: out += self.name

    dt = time.time() - self.t0
    if dt > 1: out += ' - finished in {:8s}'.format(self.human_time(dt))

    if self.length is not None and self.length > 0:
      rate = dt / self.length
      out += " [{:8s} per step]".format(self.human_time(rate))

    self.logger.info(out)

  def position(self):
    """Convenience access to the current position in the progress"""
    return self.pos


def demo():
  this_logger = create()
  with this_logger.timer("this is timed"): time.sleep(1.1)
  todo = range(0, 5)
  with this_logger.progress("this is progressed", length=len(todo)) as progress:
    for i in todo:
      time.sleep(0.5)
      progress.next(i)
  this_logger.remove("We should remove the following exit")
  this_logger.exit("That's all folks")
