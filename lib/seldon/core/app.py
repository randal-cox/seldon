import os.path, sys, re

def is_interactive():
  """Determine if the environment is interactive (via jupyter notebooks) or from the command line"""
  import __main__ as main
  return not hasattr(main, '__file__')

def name():
  """Get the name of the app, handling the case of jupyter notebooks"""
  name = os.path.basename(re.sub(r'\.[^\.]+$', '', os.path.basename(sys.argv[0])))
  if name == 'ipykernel_launcher': name = 'jupyter'
  return name
