import os.path

import seldon.core.caller


def test_line():
  # this is super fragile since it can move around. Keep it HERE
  assert (seldon.core.caller.line() == 8)

def test_file():
  assert(os.path.basename(seldon.core.caller.file()) == 'test_caller.py')

def test_function():
  assert(seldon.core.caller.function() == 'test_function')

