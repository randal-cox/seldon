import inspect

"""Functions to get the file, function, and line of the caller code"""

def file(depth=1):
  """Get the name of the calling file"""
  return inspect.stack()[depth].filename

def function(depth=1):
  """Get the name of the calling function"""
  return inspect.stack()[depth].function

def line(depth=1):
  """Get the name of the calling function"""
  return inspect.stack()[depth].lineno
