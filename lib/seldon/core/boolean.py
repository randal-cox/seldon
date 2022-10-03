import re, math

def to_b(v):
  """Convert a string or number of boolean to a boolean value"""
  if v is None: return None
  if v is True: return True
  if v is False: return False

  if isinstance(v, float):
    if math.isnan(v): return None
    return v != 0

  if isinstance(v, int):  return v != 0

  if callable(getattr(v, "strip", None)):
    v = v.strip().lower()
    if len(v) == 0: return None
    if re.search(r'^(nil|null|na|n/a|\?)$', v): return None
    if re.search(r'^(true|t|yes|y|on|1|\+)$', v): return True
    if re.search(r'^(false|f|no|n|off|0|-)$', v): return False
    raise ValueError(
      "type {}, value {}: not a parsable boolean".format(type(v), str(v))
    )

  raise ValueError(
    "value {} of type {} is not parseable as a boolean".format(
      str(v),
      type(v)
    )
  )

def is_b(v):
  """check if an object is parsable as a boolean"""
  try:
    to_b(v)
    return True
  except ValueError:
    return False

def to_i(v):
  """Convert a boolean/string representation to 0 for True, 1 for False"""
  v = to_b(v)
  if v is True: return 1
  if v is False: return 0
  return v

