from typing import Tuple

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
    """RMS contrast is defined as the standard deviation of the pixel intensities"""
    # With `axis=None` the array should be flattened before computing deviation, so only a single value is returned
    return float(np.std(image, axis=None))


def get_dynamic_range(image: np.ndarray) -> float:
    # noinspection PyArgumentList
    return image.max() - image.min()


K1 = 0.01
K2 = 0.03


def __luminance_comparison(lum_a: float, lum_b: float, c: float) -> float:
    return (2 * lum_a * lum_b + c) / (lum_a ** 2 + lum_b ** 2 + c)


def luminance_comparison(image_a: np.ndarray, image_b: np.ndarray) -> float:
    dynamic_range = max(
        get_dynamic_range(image_a),
        get_dynamic_range(image_b),
        1
    )

    stabilize_1 = (K1 * dynamic_range) ** 2

    lum_a = get_luminance(image_a)
    lum_b = get_luminance(image_b)
    return __luminance_comparison(lum_a, lum_b, stabilize_1)


def __contrast_comparison(con_a: float, con_b: float, c: float) -> float:
    return (2 * con_a * con_b + c) / (con_a ** 2 + con_b ** 2 + c)


def contrast_comparison(image_a: np.ndarray, image_b: np.ndarray) -> float:
    dynamic_range = max(
        get_dynamic_range(image_a),
        get_dynamic_range(image_b),
        1
    )

    stabilize_2 = (K2 * dynamic_range) ** 2

    con_a = get_rms_contrast(image_a)
    con_b = get_rms_contrast(image_b)

    return __contrast_comparison(con_a, con_b, stabilize_2)


def covariance(image_a: np.ndarray, image_b: np.ndarray) -> float:
    return np.cov(image_a.flat, image_b.flat)[0][1]


def __structural_similarity(cov: float, con_a: float, con_b: float, c: float) -> float:
    return (cov + c) / ((con_a * con_b) + c)


def structural_similarity(image_a: np.ndarray, image_b: np.ndarray) -> [float]:
    dynamic_range = max(
        get_dynamic_range(image_a),
        get_dynamic_range(image_b),
        1
    )

    stabilize = ((K2 * dynamic_range) ** 2) / 2

    con_a = get_rms_contrast(image_a)
    con_b = get_rms_contrast(image_b)

    return __structural_similarity(covariance(image_a, image_b), con_a, con_b, stabilize)


def fourier_amplitude_spectrum(image: np.ndarray) -> np.ndarray:
    return np.absolute(np.fft.fft(image - get_luminance(image)))


def __phase_invariant_similarity(image_a: np.ndarray, image_b: np.ndarray, c=K2 ** 2 / 2) -> float:
    amplitude_a = fourier_amplitude_spectrum(image_a).flat
    amplitude_b = fourier_amplitude_spectrum(image_b).flat

    return (np.inner(amplitude_a, amplitude_b) + c) / (np.linalg.norm(amplitude_a) * np.linalg.norm(amplitude_b) + c)


def phase_invariant_similarity(image_a: np.ndarray, image_b: np.ndarray) -> float:
    dynamic_range = max(
        get_dynamic_range(image_a),
        get_dynamic_range(image_b),
        1
    )

    stabilize = ((K2 * dynamic_range) ** 2) / 2
    return __phase_invariant_similarity(image_a, image_b, stabilize)


def compare_images(image_a: np.ndarray, image_b: np.ndarray, simple=True) -> [float]:
    dynamic_range = max(
        get_dynamic_range(image_a),
        get_dynamic_range(image_b),
        1
    )

    stabilize_1 = (K1 * dynamic_range) ** 2
    stabilize_2 = (K2 * dynamic_range) ** 2

    lum_a = get_luminance(image_a)
    lum_b = get_luminance(image_b)

    con_a = get_rms_contrast(image_a)
    con_b = get_rms_contrast(image_b)

    luminance = __luminance_comparison(lum_a, lum_b, stabilize_1)
    contrast = __contrast_comparison(con_a, con_b, stabilize_2)

    structure = __structural_similarity(covariance(image_a, image_b), con_a, con_b, stabilize_2 / 2) \
        if simple else __phase_invariant_similarity(image_a, image_b, stabilize_2 / 2)

    return [luminance, contrast, structure]


def simple_combine(properties: [Tuple[float, float]]) -> float:
    # Weird hack to prevent `runtimewarning: invalid value encountered`
    # numpy has issue when powering high precision low number to power that's less than 1
    # see: https://stackoverflow.com/a/45384691
    return np.product([np.sign(prop) * (np.abs(prop)) ** weight for prop, weight in properties])


def __ssim(image_a: np.ndarray, image_b: np.ndarray,
           alpha=1, beta=1, gamma=1,
           simple=True, combine=simple_combine) -> float:
    luminance, contrast, structure = compare_images(image_a, image_b, simple)
    return combine([(luminance, alpha), (contrast, beta), (structure, gamma)])


def ssim(image_a: np.ndarray, image_b: np.ndarray, alpha=1, beta=1, gamma=1) -> float:
    return __ssim(image_a, image_b, alpha=alpha, beta=beta, gamma=gamma)


def dssim(image_a: np.ndarray, image_b: np.ndarray) -> float:
    return (1 - ssim(image_a, image_b)) / 2


def cw_ssim(image_a: np.ndarray, image_b: np.ndarray, alpha=1, beta=1, gamma=1) -> float:
    return __ssim(image_a, image_b, simple=False, alpha=alpha, beta=beta, gamma=gamma)
