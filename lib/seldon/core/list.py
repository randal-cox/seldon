def flatten(list_of_lists):
  if len(list_of_lists) == 0:
    return list_of_lists
  if isinstance(list_of_lists[0], list):
    return list(flatten(list_of_lists[0])) + list(flatten(list_of_lists[1:]))
  return list(list_of_lists[:1]) + list(flatten(list_of_lists[1:]))
