import pytest, os.path, inspect, tempfile, glob, subprocess

import seldon.core.path

def test_exists():
	p = inspect.stack()[0].filename
	assert(seldon.core.path.exists(p))
	p += 'junk'
	assert(not seldon.core.path.exists(p))

def test_join():
	assert(seldon.core.path.join('this', 'is', 'a', 'path') =='this/is/a/path')
	assert(seldon.core.path.join('this/is/a', 'path') == 'this/is/a/path')
	assert(seldon.core.path.join('~', 'this', 'is', 'a', 'path') == os.path.expanduser('~') + '/this/is/a/path')
	r = os.path.dirname(inspect.stack()[0].filename)
	assert(seldon.core.path.join('*', 'this', 'is', 'a', 'path') == r + '/this/is/a/path')
	assert(seldon.core.path.join(['this', 'is', 'a', 'path']) == 'this/is/a/path')

def test_to_s3():
	assert(seldon.core.path.to_s3('this') == 'this')
	assert(seldon.core.path.to_s3('s3://this') == 's3://this')
	assert(seldon.core.path.to_s3('s3a://this') == 's3://this')

def test_to_s3a():
	assert(seldon.core.path.to_s3a('this') == 'this')
	assert(seldon.core.path.to_s3a('s3://this') == 's3a://this')
	assert(seldon.core.path.to_s3a('s3a://this') == 's3a://this')

def test_to_a():
	assert(seldon.core.path.to_a('this/is/a/path') == 'this/is/a/path'.split('/'))

def test_slice():
	assert(seldon.core.path.slice('this/is/a/path') == 'this/is/a/path')
	assert(seldon.core.path.slice('this/is/a/path', stop=-1) == 'this/is/a')
	assert(seldon.core.path.slice('this/is/a/path', start=-1) == 'path')
	assert(seldon.core.path.slice('this/is/a/path', start=-3, stop=-1) == 'is/a')

def test_is_dir():
	p = inspect.stack()[0].filename
	assert(not seldon.core.path.is_dir(p))
	p = os.path.dirname(p)
	assert(seldon.core.path.is_dir(p))

def test_mtime():
	p = inspect.stack()[0].filename
	assert(os.path.getmtime(p) == seldon.core.path.mtime(p))

def test_size():
	p = inspect.stack()[0].filename
	assert(os.path.getsize(p) == seldon.core.path.size(p))

def test_glob():
	p = os.path.join(inspect.stack()[0].filename.replace('.py',''),'*')
	hits = sorted([os.path.basename(h) for h in seldon.core.path.glob(p)])
	assert(['a.txt', 'b.txt', 'c.txt'] == hits)

def test_glob_last():
	p = os.path.join(inspect.stack()[0].filename.replace('.py',''),'*')
	assert('c.txt' == os.path.basename(seldon.core.path.glob_last(p)))

def test_glob_first():
	p = os.path.join(inspect.stack()[0].filename.replace('.py',''),'*')
	assert('a.txt' == os.path.basename(seldon.core.path.glob_first(p)))

def test_rm():
	with tempfile.TemporaryDirectory() as d:
		p1 = os.path.join(d, 'j')
		d1 = os.path.join(d, 'd')
		p2 = os.path.join(d1, 'k')
		assert(not os.path.exists(p1))
		assert(not os.path.exists(p2))
		assert(not os.path.exists(d1))

		with open(p1, 'w') as f: f.write('')
		assert(os.path.exists(p1))

		os.mkdir(d1)
		assert(os.path.exists(d1))

		with open(p2, 'w') as f: f.write('')
		assert(os.path.exists(p2))

		seldon.core.path.rm(p1)
		seldon.core.path.rm(d1)
		assert(not os.path.exists(p1))
		assert(not os.path.exists(p2))
		assert(not os.path.exists(d1))


