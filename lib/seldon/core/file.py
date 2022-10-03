import seldon.core.path

@contextmanager
def open(*path_parts, mode='r'):
  """Open a file for reading or writing, supporting
  - file paths on s3
  - gzip formats for read or write
  - atomic writing so that the file is not present until the entire operation is completed
  """

  path = seldon.core.path.join(path_parts)
  if path.startswith('s3'):
    pass
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
      raise (ValueError, "mode must be r or w only")

def wc(*path_parts):
  """Get the lines, words, and characters of a file, supporting
  - file paths on S3
  - gzip formats
  - cache results so you don't have to spend the time to compute it again
  """
  pass

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
  if isinstance(inputs, dict): inputs = seldon.core.list.flatten(inputs.values)
  if isinstance(outputs, dict): outputs = seldon.core.list.flatten(outputs.values)
  inputs = list(inputs)
  outputs = list(outputs)

  common = list(set(inputs) & set(targets))
  if len(common) > 0: raise (ValueError, "Overlapping inputs and outputs: {} vs {}".format(sources, targets))
  if len(sources) == 0: return False
  if len(outputs) == 0: return False
  if not all([seldon.core.path.exists(path) for path in outputs]): return True
  if not all([seldon.core.path.exists(path) for path in inputs]): return True
  max_t_inputs = min([seldon.core.path.mtime(path) for path in inputs])
  min_t_outputs = min([seldon.core.path.mtime(path) for path in outputs])
  return max_t_inputs > min_t_outputs

@contextmanager
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
  pass

