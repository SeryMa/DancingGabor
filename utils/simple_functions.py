import collections


def interpolate(val_a, val_b, percent):
    return val_a + (val_b - val_a) * percent


def get_perc(min_value, max_value, val):
    return (val - min_value) / (max_value - min_value)


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


def nested_clear_override(original, update, override_keys):
    original_override = next(filter(lambda key: key in override_keys, original), '')
    update_override = next(filter(lambda key: key in override_keys, update), '')

    if original_override:
        if update_override and original_override == update_override:
            nested_clear_override(original[original_override], update[update_override], override_keys)
        else:
            original.pop(original_override)


def id(x):
    return x


def identity(*args):
    return args
