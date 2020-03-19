from functools import reduce

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

        self._array_normed = np.zeros(array.shape + (4,), dtype=np.uint8)
        # self._array_normed = np.zeros(array.shape, dtype=np.uint8)

        # noinspection PyTypeChecker
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


def get_luminance(image: np.ndarray) -> float:
    return image.mean()


def get_rms_contrast(image: np.ndarray) -> float:
    lum = get_luminance(image)

    return np.sqrt(np.sum(
        reduce(lambda acc, x: acc + (lum - x) ** 2, np.nditer(image), 0)
    ) / image.size)


def get_dynamic_range(image: np.ndarray) -> float:
    return image.max() - image.min()


K1 = 0.01
K2 = 0.03


def ssim(image_a: np.ndarray, image_b: np.ndarray) -> float:
    dynamic_range = max(
        get_dynamic_range(image_a),
        get_dynamic_range(image_b),
        1
    )

    stabilize_1 = (K1 * dynamic_range) ** 2
    stabilize_2 = (K2 * dynamic_range) ** 2

    lum_a = get_luminance(image_a)
    lum_b = get_luminance(image_b)

    numerator = (2 * lum_a * lum_b + stabilize_1) * (2 * covariance(image_a, image_b) + stabilize_2)
    denominator = (lum_a ** 2 + lum_b ** 2 + stabilize_1) * (np.var(image_a) + np.var(image_b) + stabilize_2)

    return numerator / denominator


def dssim(image_a: np.ndarray, image_b: np.ndarray) -> float:
    return (1 - ssim(image_a, image_b)) / 2


def covariance(image_a: np.ndarray, image_b: np.ndarray) -> float:
    return np.cov(image_a.flat, image_b.flat, bias=True)[0][1]
    # if image_a.size != image_b.size:
    #     raise ValueError('Cannot compute covariance of two arrays of different sizes')
    #
    # mean_a = image_a.mean()
    # mean_b = image_b.mean()
    # s = np.sum([(a - mean_a)*(b - mean_b) for a, b in zip(image_a.flat, image_b.flat)])
    #
    # return s / image_a.size
