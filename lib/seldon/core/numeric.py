import math

def to_human_time(seconds):
  """Seconds in a human-readable way"""
  close = 0.85
  if seconds < 1e-3 * close:
    return '{:.1f} µs'.format(seconds * 1000 * 1000)
  if seconds < 1 * close:
    return '{:.1f} ms'.format(seconds * 1000)
  if seconds < 60 * close:
    return '{:.1f} s'.format(seconds)
  if seconds < 60 * 60 * close:
    return '{:.1f} m'.format(1.0 * seconds / 60)
  if seconds < 24 * 60 * 60 * close:
    return '{:.1f} h'.format(1.0 * seconds / 60 / 60)
  return '{:.1f} d'.format(1.0 * seconds / 60 / 60 / 24)

def to_human_bytes(bytes, long=False):
  """Bytes in a human-readable format"""
  units = "u k m g t p e z y"
  if long: units = "uni kilo mega giga tera peta exa zetta yatta"
  units = units.strip().split()
  target = [1024 ** v for v in range(len(units))]
  for unit, size in reversed(list(zip(units, target))):
    if bytes >= size:
      if unit in ['u', 'uni'] and int(bytes) == 1: return '1 byte'
      u = unit
      if unit in ['u', 'uni']: u = ''
      u += 'b'
      if long: u += 'ytes'
      if unit in ['u', 'uni']: return ('%d %s' % (1.0 * int(bytes) / size, u)).strip()
      return ('%.1f %s' % (1.0 * int(bytes) / size, u)).strip()

  return ('%d b' % int(bytes)).strip()

def significance(value, digits):
  """Restrict to a number of digits of significance
  e.g., significance(1234, 1) returns 1000
  e.g., significance(3.1415,2) returns 3.1"""

  if not math.isfinite(value): return value
  s = 1
  if value < 0: s, value = -1, -value
  # many digits to use
  d = 0 if value == 0 else math.ceil(math.log10(value))
  return s * round(value, digits - d)
