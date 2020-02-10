
import matplotlib.cm as cmaps

import numpy as np
import pyglet
import pyglet.gl
from matplotlib.colors import Normalize


class ArrayImage:
    """Dynamic pyglet image of a 2d numpy array using matplotlib colormaps."""
    def __init__(self, array, cmap=cmaps.binary, norm=None, rescale=True):
        self.array = array
        self.cmap = cmap
        self.norm = Normalize() if norm is None else norm
        self.rescale = rescale

        self._array_normed = np.zeros(array.shape+(4,), dtype=np.uint8)
        # self._array_normed = np.zeros(array.shape, dtype=np.uint8)

        self._tex_data = (pyglet.gl.GLubyte * self._array_normed.size).from_buffer(self._array_normed)
        # self._tex_data = (pyglet.gl.GLubyte * self._array_normed.size).from_buffer(self._array_normed)
        self._update_array()

        format_size = 4
        # format_size = 1
        bytes_per_channel = 1
        self.pitch = array.shape[1] * format_size * bytes_per_channel
        self.image = pyglet.image.ImageData(array.shape[0], array.shape[1], "RGBA", self._tex_data)
        # self.image = pyglet.image.ImageData(array.shape[0], array.shape[1], "L", self._tex_data)
        self._update_image()

    def set_array(self, data):
        self.array = data
        self.update()

    def _update_array(self):
        if self.rescale:
            self.norm.autoscale(self.array)

        self._array_normed[:] = self.cmap(self.norm(self.array), bytes=True)
        # self._array_normed[:] = self.cmap(self.norm(self.array), bytes=True)[:,:,0]

    def _update_image(self):
        self.image.set_data("RGBA", self.pitch, self._tex_data)
        # self.image.set_data("L", self.pitch, self._tex_data)

    def update(self):
        self._update_array()
        self._update_image()


def normalize(array, min=None, max=None):
    """
    Works in place!
    :param array: Array to normalize - after normalization the array will be within the [0, 1] interval
    :param min: Expected min of the GIVEN array
    :param max: Expected max of the GIVEN array
    """
    array -= np.min(array) if min is None else min
    array /= np.max(array) if max is None else max


def cast_to_uint8(array, min=None, max=None, clip_min=None, clip_max=None):
    if clip_min or clip_max:
        array = np.clip(array,
                        np.min(array) if clip_min is None else clip_min,
                        np.max(array) if clip_max is None else clip_max)

    normalize(array, min, max)
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

    trimmed_patch = contrast * patch[max(0, -x): min(-x + max_top, patch_max_top), max(0, -y): min(-y + max_right, patch_max_right)]

    if overwrite:
        source[bottom:top, left:right] = trimmed_patch
    else:
        source[bottom:top, left:right] += trimmed_patch

    # In order for this function to work in place we have to rewrite
    # elements of the `source` instead of rewriting the `source` variable itself
    source[:] = np.clip(source, 0, 1)[:]


