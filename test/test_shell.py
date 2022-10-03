import pytest, os.path, inspect

import seldon.core.shell

def test_system_call():
  d = os.path.join(os.path.dirname(inspect.stack()[0].filename),"test_path")
  assert(
    seldon.core.shell.call(f'ls -1 {d}').strip().split("\n") ==
    ['a.txt', 'b.txt', 'c.txt']
  )

