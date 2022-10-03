"""logging the way I like to see it"""

import os, sys, time, datetime, types, traceback, logging, io, contextlib

import seldon.core.app, seldon.core.path, seldon.core.numeric

global_logger = None

def unset_logger():
  global global_logger
  global_logger = None

def logger(level=logging.INFO, handlers=['log', 'stderr'], reset=False):
  """
      Set up the logger the way I like it and add some extra methods
      - exit     - log and exit
      - remove   - a standard way to note the following code should be removed
      - section  - indent the stuff in the context manager
      - timer    - start a timer as a context manager
      - progress - start a progress meter as a context manager
      - pp       - pretty print something
      - df       - display a spark data frame

      level is the log level filter, default to INFO
      handlers are the output streams, special strings denoting handlers, or actual io objects
        - 'stderr'      - gets sys.stderr
        - 'stdout'      - gets sys.stdout
        - 'log'         - gets the standard log file location
        - other strings - saves to the file specified in the string
        - all others    - should be an io thing like stderr or stdout
  """
  if reset: unset_logger()
  global global_logger
  if global_logger is not None: return global_logger

  # Set up the basic logger with formatting the way I like
  name = seldon.core.app.name()
  log_path = seldon.core.path.join('~/logs', name + '.txt')

  print(handlers)

  if not isinstance(handlers, list): handlers = [handlers]
  if len(handlers) == 0: handlers = ['log', 'stderr']
  handlers = [logger_handler(h) for h in handlers]
  print(handlers)

  logging.basicConfig(
    level=level,
    format="{ts:s} | {dt0:<12s} | {levelname:<8s} | {indenter:<{indent}s}{message:s}",
    style='{',
    handlers=handlers
  )
  logging.indent = 0
  logging.start = logging.last = datetime.datetime.now()

  # add in our extra indent variables
  old_factory = logging.getLogRecordFactory()

  def record_factory(*args, **kwargs):
    """Update the factory used in creating a new log line"""
    r = old_factory(*args, **kwargs)
    r.indent = logging.indent
    r.indenter = ''
    r.now = time.time()
    r.dt0 = seldon.core.numeric.to_human_time(
      (datetime.datetime.now() - logging.start).total_seconds()
    )
    r.ts = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return r
  logging.setLogRecordFactory(record_factory)

  # add in the indentation and de-indentation
  def add(): logging.indent += 2
  def sub(): logging.indent -= 2
  old_getLogger = logging.getLogger
  def updatedGetLogger(name=None):
    name = name or sys.argv[0]
    ret = old_getLogger(name)
    ret.add = add
    ret.sub = sub
    return ret
  logging.getLogger = updatedGetLogger

  # log where the log file is as well as add in some standard methods
  ret = logging.getLogger(seldon.core.app.name())
  display_path = log_path
  ret.info('log at ' + display_path)

  # noinspection PyUnusedLocal
  def _from(target):
    """the right way to say where the caller was"""
    fi = traceback.extract_stack()[-3]
    root = os.path.dirname(os.path.dirname(os.path.abspath(os.path.expanduser(sys.argv[0]))))
    return fi.filename.replace(root, '').lstrip('/') + ':' + str(fi.lineno)
  ret.source = types.MethodType(_from, ret)

  # Add a bunch of methods to the logger item
  def _exit(target, message=None):
    """log that we are exiting"""
    msg = "EXIT: from " + target.source()
    if message is not None: msg += ' | ' + message
    target.critical(msg)
    sys.exit()
  ret.exit = types.MethodType(_exit, ret)

  def _remove(target, message=None):
    """Log that we should remove some lines of code"""
    m = 'ALERT!!! drop code near ' + target.source()
    if message is not None: m += ' | ' + message
    target.warning(m)
  ret.remove = types.MethodType(_remove, ret)

  @contextlib.contextmanager
  def _section(target, title=None):
    """create a section with a title. use as a context manager"""
    target.info(title)
    target.add()
    yield
    target.sub()
  ret.section = types.MethodType(_section, ret)

  @contextlib.contextmanager
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
    if dt > 1: msg += ' - finished in ' + seldon.core.numeric.to_human_time(dt)
    target.info(msg)
  ret.timer = types.MethodType(_timer, ret)

  @contextlib.contextmanager
  def _progress(target, title=None, steps=None, update=0):
    """create a progress in the logger as a context manager"""
    if steps == 0:
      # don't set up anything here or do any cleanup
      yield None
    else:
      # noinspection PyProtectedMember,PyUnresolvedReferences
      title = title or sys._getframe(2).f_code.co_name
      lp = Progress(target, title, steps, update)
      yield lp
      lp.stop()
  ret.progress = types.MethodType(_progress, ret)

  def _pp(target, obj):
    """put pretty print to the logger."""
    for line in seldon.core.struct.to_s(obj).split("\n"):
      target.info(line)
  ret.pp = types.MethodType(_pp, ret)

  def _df(target, df, rows=None, indent=0):
    #def _df_show(target, df, n=None, truncate=200, vertical=False, indent=0):
    """Run show on a dataframe, but output to the logger."""
    if rows is None: rows = df.count()
    # noinspection PyProtectedMember
    ind = ' ' * indent
    for line in df._jdf.showString(rows, 200, False).split("\n"):
      if line.strip() != '':
        target.info(ind + line)
  ret.df = types.MethodType(_df, ret)

  # add and remove output handlers beyond the default
  # def _add_handler(target, handler):
  #   target.logger.parent.handlers = list(set(ret.logger.parent.handlers + [handler]))
  # ret.add_handler = types.MethodType(_add_handler, ret)
  #
  # def _remove_handler(target, handler):
  #   try:
  #     target.logger.parent.handlers.remove(handler)
  #   except ValueError:
  #     target.warn("tried to remove handler '{}' when it was not in the current handlers".format(str(handler)))
  # ret.remove_handler = types.MethodType(_remove_handler, ret)

  # save the global
  global_logger = ret

  return ret

def logger_path():
  # Set up the basic logger with formatting the way I like
  name = seldon.core.app.name()
  log_path = seldon.core.path.join('~/logs', name + '.txt')
  return log_path

def logger_handler(v):
  if v == 'stderr': return logging.StreamHandler(sys.stderr)
  if v == 'stdout': return logging.StreamHandler(sys.stdout)
  import io
  if isinstance(v, io.StringIO): return logging.StreamHandler(v)

  if v == 'log': return logging.FileHandler(logger_path())
  if isinstance(v, str):
    print(f"adding handler for path {v}")
    return logging.FileHandler(v)
  raise ValueError(f'Illegal io: {v}')

class Progress:
  """add progress to logger calls"""

  def __init__(self, this_logger, title, steps=None, update=30):
    """create the progress
    this_logger - the one to send messages to
    title - what to call the progress
    steps - how many steps in the task
    update - how long between updating the progress
    """
    if steps is not None and (steps != int(steps) or steps < 0):
      msg = "Steps must be positive integer or None, not '{}'".format(steps)
      raise Exception(msg)
    self.logger = this_logger
    self.title = title
    self.steps = steps
    self.update = update
    self.fmt = "{:" + str(len(str(self.steps or 0))) + ",}"

    # kick it off
    self.t0 = self.t_last = time.time()
    self.pos = 0
    self.start()

  def start(self):
    """Crete the opening of the progress"""
    out = 'BEGIN'
    if self.title is not None: out += ' ' + self.title
    self.logger.info(out)
    self.logger.add()

  def goto(self, pos, message=None, force=False):
    """Move to a new location in progress. You can force the display"""
    self.pos = pos
    if time.time() - self.t_last < self.update and not force: return
    elapsed = time.time() - self.t0
    if self.steps is None:
      out = "step {:,}".format(self.pos)
      if message is not None: out += " | " + str(message)
    else:
      eta = seldon.core.numeric.to_human_time((self.steps - self.pos) / self.pos * elapsed)
      fmt = "step {} of {}".format(self.fmt, self.fmt) + " [{:5.1f}%] -- done in {:>8s}"
      out = fmt.format(
        self.pos,
        self.steps,
        100.0 * self.pos / self.steps,
        eta
      )
      if message is not None:
        out += " | " + str(message)
    self.logger.info(out)
    self.t_last = time.time()

  def step(self, message=None, force=False):
    """Move one position up in the progress, can force the message if needed"""
    self.goto(self.pos + 1, message, force)

  def stop(self):
    """Finish the progress"""
    self.logger.sub()

    out = 'FINISH '
    if self.title is not None: out += self.title

    dt = time.time() - self.t0
    if dt > 1: out += ' - finished in {:8s}'.format(seldon.core.numeric.to_human_time(dt))

    if self.steps is not None and self.steps > 0:
      rate = dt / self.steps
      out += " [{:8s} per step]".format(seldon.core.numeric.to_human_time(rate))

    self.logger.info(out)
