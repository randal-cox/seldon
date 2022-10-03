import pytest, io

import seldon.core.stdio

def test_redirect():
  s = io.StringIO('')
  with seldon.core.stdio.RedirectStdStreams(stdout=s): print("hello")
  assert(s.getvalue() == 'hello\n')
