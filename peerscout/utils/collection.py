from itertools import groupby

flatten = lambda l: [item for sublist in l for item in sublist]

iter_flatten = lambda l: (item for sublist in l for item in sublist)

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

def groupby_to_dict(l, kf, vf):
  return {
    k: [vf(v) for v in g]
    for k, g in groupby(sorted(l, key=kf), kf)
  }

def groupby_columns_to_dict(groupby_values, values, vf=None):
  if vf is None:
    vf = lambda x: x
  return groupby_to_dict(
     zip(groupby_values, values),
     lambda item: item[0],
     lambda item: vf(item[1])
  )

def applymap_dict(d, f):
  return {k: f(v) for k, v in d.items()}

def applymap_dict_list(dict_list, f):
  return [applymap_dict(row, f) for row in dict_list]
