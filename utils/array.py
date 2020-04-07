import numpy as np
from numpy import fft


def normalize(array: np.ndarray, min_value=None, max_value=None):
    """ In place normalizes given array.

    Given array is normalized. After normalization the array will be within the [0, 1] interval.
    Works in place!

    Parameters
    ----------
    array : np.ndarray
        Array to be normalized.

    min_value : None or number
        Expected min of the GIVEN array - before normalization

    max_value : None or number
        Expected max of the GIVEN array - before normalization
    """
    min_value = np.min(array) if min_value is None else min_value
    max_value = (np.max(array) if max_value is None else max_value)

    if min_value == max_value:
        if max_value > 1:
            array /= max_value

        return

    array -= min_value
    array /= max_value - min_value


def get_normalized(array: np.ndarray, min_value=None, max_value=None):
    """ Creates a normalized array which is then returned.

    The normalized array will be within the [0, 1] interval.

    Parameters
    ----------
    array : np.ndarray
        Array to get normalized form of.

    min_value : None or number
        Expected min of the GIVEN array - before normalization

    max_value : None or number
        Expected max of the GIVEN array - before normalization
    """
    ret = array.copy()
    normalize(ret, min_value, max_value)

    return ret


def cast_to_uint8(array, min_value=None, max_value=None, clip_min=None, clip_max=None):
    if clip_min or clip_max:
        array = np.clip(array,
                        np.min(array) if clip_min is None else clip_min,
                        np.max(array) if clip_max is None else clip_max)

    normalize(array, min_value, max_value)
    array *= 255

    array = array.astype('uint8')

    return array


# TODO: make the patch be applied centered
def apply_patch(source, patch, x, y, contrast=0.5, overwrite=False):
    max_right = source.shape[1]
    max_top = source.shape[0]

    patch_max_top = patch.shape[0]
    patch_max_right = patch.shape[1]

    bottom = max(x, 0)
    left = max(y, 0)

    right = max(0, min(max_right, y + patch_max_right))
    top = max(0, min(max_top, x + patch_max_top))

    trimmed_patch = contrast * patch[max(0, -x): min(-x + max_top, patch_max_top),
                               max(0, -y): min(-y + max_right, patch_max_right)]

    if overwrite:
        source[bottom:top, left:right] = trimmed_patch
    else:
        source[bottom:top, left:right] += trimmed_patch

    # In order for this function to work in place we have to rewrite
    # elements of the `source` instead of rewriting the `source` variable itself
    source[:] = np.clip(source, 0, 1)[:]


def get_windows(array, window_size_height=1, window_size_width=1, step=1):
    for x in range(-window_size_height + step, array.shape[0], step):
        for y in range(-window_size_width + step, array.shape[1], step):
            yield array[max(0, x):x + window_size_height, max(0, y):y + window_size_width]


# TODO: The phase invariant similarity S was defined as the cosine of the angle between the Fourier amplitude
#  spectrum of the patch (minus its mean) and the Fourier amplitude spectrum of the target, where the two spectra are
#  regarded as vectors.
def get_similarity(image_a: np.ndarray, image_b: np.ndarray) -> np.ndarray:
    return np.dot(
        fft.rfft2(image_a),
        fft.rfft2(image_b)
    )


def read_file(filename, delimiter=';') -> dict:
    with open(filename, 'r') as file:
        headers = file.readline().split(delimiter)

    all_values = np.loadtxt(filename, delimiter=delimiter, skiprows=1)

    ret = {}
    for header, values in zip(headers, all_values):
        ret[header] = values

    return ret
