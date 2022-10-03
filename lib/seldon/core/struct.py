import pprint

def to_s(*args):
  """Convert some structs to a stringified pretty print version"""
  if len(args) == 1: args = args[0]
  return pprint.pformat(args, indent=2, width=120)

def pp(*args):
  """Just pretty print"""
  if len(args) == 1: args = args[0]
  pprint.pformat(args, indent=2, width=120).pprint(args)
