import seldon.core.numeric

def test_to_human_time():
  assert(seldon.core.numeric.to_human_time(0) == '0.0 µs')
  assert(seldon.core.numeric.to_human_time(.2) == '200.0 ms')
  assert(seldon.core.numeric.to_human_time(10) == '10.0 s')
  assert(seldon.core.numeric.to_human_time(40) == '40.0 s')
  assert(seldon.core.numeric.to_human_time(59) == '1.0 m')
  assert(seldon.core.numeric.to_human_time(60*60*2) == '2.0 h')
  assert(seldon.core.numeric.to_human_time(60*60*24*2) == '2.0 d')

def test_to_human_bytes():
  assert(seldon.core.numeric.to_human_bytes(0) == '0 b')
  assert(seldon.core.numeric.to_human_bytes(1024) == '1.0 kb')
  assert(seldon.core.numeric.to_human_bytes(1024, True) == '1.0 kilobytes')
  assert(seldon.core.numeric.to_human_bytes(1024**4) == '1.0 tb')

def test_significance():
  assert(seldon.core.numeric.significance(1234, 1) == 1000)
  assert(seldon.core.numeric.significance(3.1415, 2) == 3.1)
