flatten = lambda l: [item for sublist in l for item in sublist]

filter_none = lambda l: [item for item in l if item is not None]

def deep_get(dictionary, keys, defaultValue=None):
  result = dictionary
  for key in keys:
    if result is not None and key in result:
      result = result[key]
    else:
      return defaultValue
  return result

def deep_get_list(dictionary_list, keys, defaultValue=None):
  return [deep_get(d, keys, defaultValue) for d in dictionary_list]

def merge_grouped_dicts(grouped_dicts):
  return {
    k: flatten([d.get(k, []) for d in grouped_dicts])
    for k in set(flatten([d.keys() for d in grouped_dicts]))
  }
