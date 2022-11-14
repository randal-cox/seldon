import seldon.core.app

def test_is_interactive():
  assert(not seldon.core.app.is_interactive())
  # can't think of a super-easy way to make sure this works with interactive

def test_app_name():
  assert(seldon.core.app.name() == '__main__')
