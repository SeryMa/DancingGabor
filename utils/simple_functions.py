import collections
from datetime import datetime
from os import makedirs, chdir
from os.path import exists, sep

import numpy as np


def interpolate(val_a, val_b, percent):
    return val_a + (val_b - val_a) * percent


def get_perc(min_value, max_value, val):
    return (val - min_value) / (max_value - min_value)


def simple_difference(a, b):
    return np.abs(a - b)


def any_lambda(i, predicate):
    return any(predicate(e) for e in i)


def all_lambda(i, predicate):
    return all(predicate(e) for e in i)


def nested_update(original, update):
    for key, value in update.items():
        if key in original and isinstance(value, collections.Mapping):
            nested_update(original[key], value)
        else:
            original[key] = update[key]


def nested_replace(original: {}, update: {}, replace_key: str = None):
    for key, value in update.items():
        if key == replace_key:
            update.pop(key)
            update.update(original)
            return True
        elif isinstance(value, collections.Mapping):
            nested_replace(original, value, replace_key)

    return False


def nested_clear_override(original: {}, update: {}, override_keys: [str]):
    original_override = next(filter(lambda key: key in override_keys, original), '')
    update_override = next(filter(lambda key: key in override_keys, update), '')

    if not original_override:
        return

    if update_override and original_override == update_override:
        nested_clear_override(original[original_override], update[update_override], override_keys)
    else:
        original.pop(original_override)


def construct_file_name(base_name: str, extension='', folder='', change_dir=False):
    if sep in base_name:
        tmp = base_name.split(sep)
        base_name = tmp[-1]

        folder = folder + sep + sep.join(tmp[:-1])

    if folder:
        exists(folder) or makedirs(folder, exist_ok=True)
        change_dir and chdir(folder)

    return f'{base_name}_{datetime.now().microsecond}{("." + extension) if extension else ""}'
