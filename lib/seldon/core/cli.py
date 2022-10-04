import sys, os.path, re, datetime, argparse

import seldon.core.logging

import seldon.core.spark
import seldon.core.struct
import seldon.core.stdio
import seldon.core.path
import seldon.core.commands.demo

class CLI:
  """Command line interface to the qualia project"""
  def command_class(self):
    """Override this with a class containing the commands that need running"""
    return seldon.core.commands.demo.DemoCommands

  def __init__(self):
    logger = self.logger = seldon.core.logging.logger()

    # Overall command
    self.parser = argparse.ArgumentParser(description="Project Seldon commands")
    self.subparsers = self.parser.add_subparsers(help='{command} --help for additional help', dest='command')
    self.unpathed = []

    # add in all the cmd_ methods in alpha order (junk last)
    for cmd in sorted(dir(self)):
      if cmd.startswith('add_'):
        getattr(self, cmd)()

    # parse the command line args and do a little post-processing on the results
    args = self.parser.parse_args(None if sys.argv[1:] else ['-h'])
    # should make a pass at standardizing some fields like dates, times, etc
    args.logger = self.logger
    command_class = self.command_class()(args)

    # display our args to the logger
    with logger.section('command-line arguments'):
      for k, v in vars(args).items():
        if k.startswith('_'): continue
        if k in ['func', 'command', 'logger', 'spark']: continue
        if isinstance(v, list):
          logger.info('{:<30s}: {}'.format(k, ', '.join([str(v1) for v1 in v])))
        else:
          logger.info('{:<30s}: {}'.format(k, v))
    args.logger = logger

    # iterate over all the paths we have
    paths = args.paths
    delattr(args, 'paths')

    if args.command in self.unpathed:
      # these need no paths as arguments
      with args.logger.timer(args.command):
        args.func(command_class)
    else:
      # these need no paths as arguments
      with logger.progress(title=args.command, steps=len(paths)) as progress:
        for path in paths:
          args.path = path
          with args.logger.timer("path " + path):
            args.func(command_class, path)
          progress.next(command_class, path)

  @staticmethod
  def cmd_standard(cmd, func):
    """Add in standard arguments shared by all commands"""
    # main argument which is a path
    cmd.add_argument(
      'paths',
      nargs='*',
      help="paths to parse"
    )
    cmd.add_argument(
      "-j", "--jobs",
      help="force job status re-evaluation (default: %(default)s)",
      default=False,
      action="store_true"
    )
    cmd.add_argument(
      "-f", "--reset",
      help="force reset of all files (default: %(default)s)",
      default=False,
      action="store_true"
    )

    ###############################################################################
    # Mostly debugging tools, though potentially generally useful, too
    ###############################################################################
    # be more chatty
    cmd.add_argument(
      "-v", "--verbose",
      help="output to stdout (default: %(default)s)",
      default=False,
      action="store_true"
    )

    # test can default to True if a special signal file is present in the cwd
    def_test = False
    if os.path.exists('.test_always_on'):
      self.logger.warn('file ".test_always_on" is present, so forcing the test switch')
      def_test = True
    cmd.add_argument(
      "-t", "--test",
      help="run with test data and test output (default: %(default)s)",
      default=def_test,
      action="store_true"
    )

    # supress exit on errors
    cmd.add_argument(
      "--nofail",
      help="suppress exit on errors (default: %(default)s)",
      default=True,
      action="store_false"
    )

    cmd.set_defaults(func=func)

  ###################################################
  # commands
  ###################################################
  def add_demo(self):
    name = 'demo'
    defs = {}
    self.unpathed.append(name)
    sub = self.subparsers.add_parser(name, help="show off some logger and spark commands")
    self.cmd_standard(sub, func=lambda command_class: command_class.command_demo())

