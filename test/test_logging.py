import pytest, os.path, io, time, tempfile

import seldon.core.logging

def test_one():
  #seldon.core.logging.unset_logger()
  #with tempfile.TemporaryDirectory() as d:
  p = os.path.join('junk.txt')
  l = seldon.core.logging.logger(handlers=[p, 'stderr'])
  l.info('oooooo')
  print(p)

  # l = seldon.core.logging.logger() #ios=[s, 'stderr'])
  # with l.section('section'):
  #   l.info('inside section')
  #   l.remove('should remove some stuff')
  # with l.progress("some progress", 10) as p:
  #   for i in range(10):
  #     p.step()
  # with l.timer('name'):
  #   time.sleep(1)
  #
  # # l.warning("this")
  # #print(s.getvalue())
  # print("================")
  #assert(False)

test_one()