from collections import defaultdict
from itertools import groupby


def flatten(l):
    return [item for sublist in l for item in sublist]


def iter_flatten(l):
    return (item for sublist in l for item in sublist)


def filter_none(l):
    return [item for item in l if item is not None]


def force_list(x):
    if x is None:
        return []
    if isinstance(x, list):
        return x
    return [x]


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


def _IDENTIFY_FN(x):
    return x


def groupby_columns_to_dict(groupby_values, values, vf=None):
    if vf is None:
        vf = _IDENTIFY_FN
    return groupby_to_dict(
        zip(groupby_values, values),
        lambda item: item[0],
        lambda item: vf(item[1])
    )


def applymap_dict(d, f):
    return {k: f(v) for k, v in d.items()}


def applymap_dict_list(dict_list, f):
    return [applymap_dict(row, f) for row in dict_list]


def parse_list(s, sep=','):
    s = s.strip()
    if not s:
        return []
    return [item.strip() for item in s.split(sep)]


def invert_set_dict(d: dict) -> dict:
    """Inverts a dict like:

      {'a': {1, 2}, 'b': {1, 3}}

      to:

      {1: {'a', 'b'}, 2: {'a'}, 3: {'b'}}
    """
    result = defaultdict(set)
    for k, v in d.items():
        for x in v:
            result[x].add(k)
    return result
