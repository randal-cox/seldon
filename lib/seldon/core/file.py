import os, contextlib, builtins, gzip, time, re, types

import seldon.core.path
import seldon.core.app

@contextlib.contextmanager
def open(*path_parts, mode='r'):
  """Open a file for reading or writing, supporting
  - file paths on s3
  - gzip formats for read or write
  - atomic writing so that the file is not present until the entire operation is completed
  """
  if path_parts[-1] in ['r', 'w']:
    raise ValueError("specify mode as mode=r|w, not as the last argument")

  path = seldon.core.path.join(*path_parts)

  if seldon.core.path.to_s3(path).startswith('s3://'):
    raise ValueError('s3 paths not currently implemented')
  else:
    if mode == 'w':
      # make sure there is a dir to put the file in and that we remove any temporary or previous versions
      if not os.path.exists(os.path.dirname(path)):
        if os.path.dirname(path) != '': os.makedirs(os.path.dirname(path))

      path_tmp = path + '.tmp'
      if os.path.exists(path): os.remove(path)
      if os.path.exists(path_tmp): os.remove(path_tmp)

      if path.endswith('.gz'):
        file = fix_gzip_writer(gzip.open(path_tmp, mode))
      else:
        file = builtins.open(path_tmp, mode)
      yield file
      file.close()
      os.rename(path_tmp, path)
    elif mode == 'r':
      if path.endswith('.gz'):
        file = fix_gzip_reader(gzip.open(path, mode))
      else:
        file = builtins.open(path, mode)
      yield file
      file.close()
    else:
      raise ValueError("mode must be r or w only")

wc_cache_path = None
wc_cache_db = None
wc_cache_last = None

def wc_cache_default_path():
  return seldon.core.path.join('~/logs', seldon.core.app.name)

def wc_cache(*path_parts):
  global wc_cache_path
  global wc_cache_db
  global wc_cache_last
  p = seldon.core.path.join(*path_parts)
  if wc_cache_path == p: return

  # nuke any old one
  if seldon.core.path.exists(wc_cache_path): os.remove(wc_cache_path)
  wc_cache_db = {}
  wc_cache_last = time.time()

def wc(*path_parts):
  """Get the lines, words, and characters of a file, supporting
  - file paths on S3
  - gzip formats
  - cache results so you don't have to spend the time to compute it again
  """
  wc_cache(wc_cache_default_path())
  global wc_cache_db, wc_cache_last
  path = seldon.core.path.join(*path_parts)
  if path in wc_cache_db: return wc_cache_db[path]

  with seldon.core.file.open(path, mode='r') as f: content = f.read()
  lines = len(content.split("\n"))
  chars = len(content)
  words = len(re.findall(r'\w+', content))
  wc_cache_db[path] = types.SimpleNamespace(lines=lines, chars=chars, characters=chars, words=words)
  return wc_cache_db[path]

def stale(inputs, outputs, remove=False):
  """Determine is a set of output paths is out-of-date relative to a list of inputs, supporting
  - file paths on S3
  - inputs and outputs can be grouped into dictonaries, so you can cluster related items together
    like inputs could be
      'set1': [path1, path2, path3],
      'set2': [path4, path5, path6],
    Or it could just be a list
      [path1, path2, path3, path4, path5, path6]
    Also note that paths can be arrays that are joined
  - remove stale files if remove==True
  """

  if isinstance(inputs, str): inputs = [inputs]
  if isinstance(outputs, str): outputs = [outputs]
  if isinstance(inputs, dict):
    inputs = list(inputs.values())
    inputs = seldon.core.list.flatten(inputs)
  if isinstance(outputs, dict):
    outputs = list(outputs.values())
    outputs = seldon.core.list.flatten(outputs)
  inputs = list(inputs)
  outputs = list(outputs)
  common = list(set(inputs) & set(outputs))
  if len(common) > 0: raise (ValueError, "Overlapping inputs and outputs: {} vs {}".format(inputs, outputs))
  res = _stale(inputs, outputs)
  if res and remove:
    for p in outputs:
      seldon.core.path.rm(p)
  return res

def _stale(inputs, outputs):
  # just get the stale or not so that it's easier to handle the reset request
  if len(inputs) == 0: return False
  if len(outputs) == 0: return False
  if not all([seldon.core.path.exists(path) for path in outputs]): return True
  if not all([seldon.core.path.exists(path) for path in inputs]): return True

  max_t_inputs = max([seldon.core.path.mtime(path) for path in inputs])
  min_t_outputs = min([seldon.core.path.mtime(path) for path in outputs])
  return max_t_inputs > min_t_outputs


class UpdateException(Exception): pass

@contextlib.contextmanager
def update(inputs, outputs, reset=False):
  """Update a set of outputs given inputs if the outputs are stale or reset==True, supporting
  - file paths on S3
  - inputs and outputs can be grouped in dictionaries, so you can cluster related items together
  Call this like
    with update(['path1'], ['path2']) as sources, targets:
      with open(targets[0]) as t:
        with open(sources[0]) as s:
          t.write(s.read())
  """
  if not stale(inputs, outputs) and not reset: return
  yield [inputs, outputs]
  if stale(inputs, outputs): raise UpdateException("Not updated after calls to update")

#########################################
# some utilty functions for open to modify
# the file objects so they handle decoding and encoding
#########################################
# Monkey patching the gzipreader and writer so I don't have to encode or decode
def new_gzip_write(self, s):
  s = s.encode()
  # try: s = s.encode()
  # except AttributeError: pass
  self._old_write(s)

def new_gzip_read(self): return self._old_read().decode()

def fix_gzip_writer(file):
  file._old_write = file.write
  file.write = lambda s: new_gzip_write(file, s)
  return file

def fix_gzip_reader(file):
  gzip.GzipFile._old_read = gzip.GzipFile.read
  file.read = lambda: new_gzip_read(file)
  return file