import seldon.core.list

def test_flatten():
  assert(seldon.core.list.flatten([1,2,3,[4]]) == [1,2,3,4])
  assert(seldon.core.list.flatten([[1,2],3,[4]]) == [1,2,3,4])
  assert(seldon.core.list.flatten([[[1,2]],3,[4]]) == [1,2,3,4])
