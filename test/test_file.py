import pytest, os.path, tempfile

import seldon.core.file
import seldon.core.path
import seldon.core.shell

def test_open():
  with tempfile.TemporaryDirectory() as d:
    p1 = os.path.join(d, 'f1')
    with seldon.core.file.open(p1, mode='w') as f:
      assert(not os.path.exists(p1))
      f.write('1')
    assert(os.path.exists(p1))

    with seldon.core.file.open(p1, mode='r') as f:
      assert(f.read() == '1')
    assert(os.path.exists(p1))

    p2 = os.path.join(d, 'f2.gz')
    with seldon.core.file.open(p2, mode='w') as f:
      assert(not os.path.exists(p2))
      f.write('2')
    assert(os.path.exists(p2))
    assert('gzip' in seldon.core.shell.call(f'file {p2}'))

    with seldon.core.file.open(p2) as f:
      assert(f.read() == '2')
    assert(os.path.exists(p2))

def test_stale():
  with tempfile.TemporaryDirectory() as d:
    p1 = os.path.join(d, 'f1')
    p2 = os.path.join(d, 'f2')
    p3 = os.path.join(d, 'f3')
    assert(seldon.core.file.stale([p1, p2], [p3]))
    with(open(p1, 'w')) as f: f.write('')
    assert(seldon.core.file.stale([p1, p2], [p3]))
    with(open(p2, 'w')) as f: f.write('')
    assert(seldon.core.file.stale([p1, p2], [p3]))
    with(open(p3, 'w')) as f: f.write('')
    assert(not seldon.core.file.stale([p1, p2], [p3]))

    # then break it
    os.remove(p2)
    assert(seldon.core.file.stale([p1, p2], [p3]))

    # see if remove works
    assert(seldon.core.file.stale([p1, p2], [p3], remove=True))
    assert(not seldon.core.path.exists(p3))

    # create the p2 file again, now with no p3 so it is stale
    with(open(p2, 'w')) as f: f.write('')
    assert(seldon.core.file.stale([p1, p2], [p3]))

    # and repair it with a new p3 file
    with(open(p3, 'w')) as f: f.write('')
    assert(not seldon.core.file.stale([p1, p2], [p3]))

    # try the dict version of inputs and outputs
    assert(not seldon.core.file.stale({'p1': p1, 'p2': p2}, {'p3': p3}))
    assert(not seldon.core.file.stale({'set': [p1, p2]}, {'p3': p3}))

def test_update():
  with tempfile.TemporaryDirectory() as d:
    p1 = os.path.join(d, 'f1')
    p2 = os.path.join(d, 'f2')
    p3 = os.path.join(d, 'f3')
    with(open(p1, 'w')) as f: f.write('')
    with(open(p2, 'w')) as f: f.write('')
    with seldon.core.file.update([p1, p2], [p3]) as args:
      inputs, outputs = args
      n = open(inputs[0]).read() + open(inputs[1]).read()
      with seldon.core.file.open(p3, mode='w') as f: f.write(n)
    assert (not seldon.core.file.stale([p1, p2], [p3]))
