import os, os.path, re, builtins, shutil
import glob as glob_base
import seldon.core.caller, seldon.core.list

def exists(*args):
  """Check if file exists, allowing for paths on s3"""
  path = join(*args)
  if to_s3(path).startwith('s3://'):
    raise Exception("Have to write exists for s3")
  return os.path.exists(path)

def join(*args):
  """Like os.path.join but it takes care of ~ and *
  ~ is the user's home directory
  * is the directory of the file containing the method that called this function
  """
  args = seldon.core.list.flatten(args)
  ret = os.path.join(*[str(a) for a in args])
  ret = os.path.expanduser(ret)
  if ret.startswith('*/'): ret = os.path.dirname(seldon.core.caller.file(2)) + '/' + ret[2:]
  return ret

def to_s3(*args):
  """Join and convert the parth to s3 notation"""
  path = join(*args)
  return re.sub(r'^s3a://', 's3://', path)

def to_s3a(*args):
  """Join and convert the parth to s3a notation"""
  path = join(*args)
  return re.sub(r'^s3://', 's3a://', path)

def to_a(path):
  """Convert a path to a list of elements in that path"""
  if isinstance(path, list): return path
  return path.split(os.sep)

def slice(*args, start=None, stop=None):
  """Slice a path so you can get some part of it
  For e.g., slice("1/2/3/4", stop=-1) => "1/2/3"""
  path = to_a(*args)
  if start is None and stop is None: return join(*path)
  if start is None and stop is not None: join(*path[:stop])
  if start is not None and stop is None: return join(*path[start:])
  return join(*path[start:stop])

def glob(*args):
  """A glob that handles the niceties like join and expanduser"""
  path = join(*args)
  if to_s3(path).startswith('s3://'):
    raise ValueError("Have not done exists for s3")
  else:
    return glob_base.glob(path)

def glob_last(*args, maximum_date=None):
  """ the alphabetically last one"""
  path = join(*args)
  if to_s3(path).startswith('s3://'):
    raise ValueError("Have not done exists for s3")
  else:
    return sorted(glob_base.glob(path))[-1]

def glob_first(*args, maximum_date=None):
  """ the alphabetically last one"""
  path = join(*args)
  if to_s3(path).startswith('s3://'):
    raise ValueError("Have not done exists for s3")
  else:
    return sorted(glob_base.glob(path))[0]

def exists(*args):
  """Returns true if the path exists, supporitng
  - file paths on S3
  """
  path = join(*args)
  if to_s3(path).startswith('s3://'):
    raise ValueError("Have not done exists for s3")
  else:
    return os.path.exists(path)

def rm(*args):
  path = join(*args)
  if to_s3(path).startswith('s3://'): raise ValueError("Have not done is_dir for s3")
  if os.path.isdir(path): shutil.rmtree(path)
  else: os.remove(path)

def mtime(*args):
  path = join(*args)
  if to_s3(path).startswith('s3://'):
    raise ValueError("Have not done is_dir for s3")
  else:
    return os.path.getmtime(path)

def size(*args):
  path = join(*args)
  if to_s3(path).startswith('s3://'):
    raise ValueError("Have not done is_dir for s3")
  else:
    return os.path.getsize(path)

def is_dir(*args):
  path = join(*args)
  if to_s3(path).startswith('s3://'):
    raise ValueError("Have not done is_dir for s3")
  else:
    return os.path.isdir(path)

