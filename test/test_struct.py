import pytest

import seldon.core.struct

def test_to_s():
  s = [1,2,3]
  assert(seldon.core.struct.to_s(s) == '[1, 2, 3]')

