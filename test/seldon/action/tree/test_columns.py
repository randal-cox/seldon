import tempfile

import seldon.action.tree.columns


def test_path():
  with tempfile.TemporaryDirectory() as d:
    c = seldon.action.tree.columns.Column('feature1', d, 'categorical')
    # assert(c.path() == )

  assert (not seldon.core.app.is_interactive())
  # can't think of a super-easy way to make sure this works with interactive


def test_app_name():
  assert (seldon.core.app.name() == '__main__')


def test_junk():
  pass

# test data set
# A 7
# A 8

# B 1
# B 2
# B 3
# B 4
# B 5

# C 12
# C 13
# C 14

# D 9
# E 10

# if max_categories=2, and min_records = 0.2, then
# - we will choose B and C
# - B will be 3
# - C will be 13
# the OTHERS will average to 8.5

# PROBLEM: what is two categories get marked to the same effective value? THis might mean less features than expected
# fixing this is possible in that keep loop, though a bit of a p
