import pytest

import seldon.core.boolean

def test_to_b():
  for b in 'true t yes y + 1'.split(): assert seldon.core.boolean.to_b(b)
  for b in 'false f no n - 0'.split(): assert not seldon.core.boolean.to_b(b)
  for b in 'nil Nil na NA n/a ?'.split(): assert seldon.core.boolean.to_b(b) is None
  assert seldon.core.boolean.to_b(None) is None
  assert seldon.core.boolean.to_b(True)
  assert not seldon.core.boolean.to_b(False)
  assert seldon.core.boolean.to_b(1)
  assert not seldon.core.boolean.to_b(0)
  assert seldon.core.boolean.to_b(float("NaN")) is None
  assert seldon.core.boolean.to_b(1.0)
  assert not seldon.core.boolean.to_b(0.0)
  for b in 'junk nuts a b c'.split():
    with pytest.raises(ValueError):
      seldon.core.boolean.to_b(b)
  with pytest.raises(ValueError):
    seldon.core.boolean.to_b([])

def test_is_b():
  assert seldon.core.boolean.is_b('f')
  assert seldon.core.boolean.is_b('t')
  assert seldon.core.boolean.is_b(False)
  assert seldon.core.boolean.is_b(True)
  assert(not seldon.core.boolean.is_b([]))

def test_to_i():
  assert seldon.core.boolean.to_i('f') == 0
  assert seldon.core.boolean.to_i('t') == 1
  assert seldon.core.boolean.to_i(False) == 0
  assert seldon.core.boolean.to_i(True) == 1
  assert seldon.core.boolean.to_i(None) is None
