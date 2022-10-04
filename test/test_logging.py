import pytest, os.path, io, time, tempfile, logging

import seldon.core.logging

# pytest is really annoying because it intercepts almost all the logging and formatting, so it is super hard
# to test any time stamps, formatting, indentation, and so on. Until I figure out a way to supress this, I will
# merely run all these calls and make sure nothing crashes

def test_fast(caplog):
  with tempfile.TemporaryDirectory() as d:
    p = os.path.join(d, 'log.txt')
    seldon.core.logging.unset_logger()
    l = seldon.core.logging.logger(handlers=['stderr', 'stdout', 'log', io.StringIO(), p])
    caplog.clear()
    caplog.set_level(logging.INFO)
    l.warning('1')
    with l.section('section'):
      l.warning('2')
    assert([r.message for r in caplog.records] == ['1', '2'])
    try: l.exit('hello')
    except SystemExit: pass
    l.remove('')
    with l.timer(''): pass
    with l.progress('', steps=2) as prog: prog.step('-')
    with l.progress('') as prog: prog.step('-')
    with pytest.raises(ValueError):
      with l.progress('', steps=-2) as prog: prog.step()
    with pytest.raises(ValueError):
      with l.progress('', steps=0.5) as prog: prog.step()
    l.pp([])

def test_fail():
  seldon.core.logging.unset_logger()
  with pytest.raises(ValueError):
    seldon.core.logging.logger(handlers=[[]])

@pytest.mark.slow
def test_slow():
  rows = [
    ("Finance", 10),
    ("Marketing", 20),
    ("Sales", 30),
    ("IT", 40)
  ]
  columns = ["dept_name", "dept_id"]
  spark = seldon.core.spark.spark()
  df = spark.createDataFrame(data=rows, schema=columns).orderBy('dept_name')
  seldon.core.logging.unset_logger()
  l = seldon.core.logging.logger(handlers=['stderr'])
  l.df(df)