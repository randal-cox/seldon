import io
import sys

import seldon.core.struct


def test_to_s():
  s = [1, 2, 3]
  assert (seldon.core.struct.to_s(s) == '[1, 2, 3]')


def test_pp():
  s = [1, 2, 3]
  old_out = sys.stdout
  new_out = sys.stdout = io.StringIO()
  seldon.core.struct.pp(s)
  sys.stdout = old_out
  assert (new_out.getvalue() == '[1, 2, 3]\n')
