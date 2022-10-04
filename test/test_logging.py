import pytest, os.path, io, time, tempfile, logging

import seldon.core.logging

# pytest is really annoying because it intercepts almost all the logging and formatting, so it is super hard
# to test any time stamps, formatting, indentation, and so on. Until I figure out a way to supress this, I will
# merely check that there are entries within a section

def test_section(caplog):
  seldon.core.logging.unset_logger()
  l = seldon.core.logging.logger(handlers=['stderr'])
  caplog.clear()
  caplog.set_level(logging.INFO)
  l.warning('1')
  with l.section('section'):
    l.warning('2')
  assert([r.message for r in caplog.records] == ['1', '2'])
