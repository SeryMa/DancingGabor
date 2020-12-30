from typing import Iterable, Tuple, Callable, TypeVar

import numpy as np
import numpy.fft as fft

from generators.noise_generator import NoiseGenerator
from utils.array import get_normalized


# TODO: create a `StaticGaborGenerator` which would not compute a new gabor every iteration
#  but rather return a copy of precomputed array.
# TODO: Possibly create a new function that would actually return gabor with given parameters.


class GaborGenerator(NoiseGenerator):
    """Generator used to generate gabor patches of given size

    The gabor patch can change in time if specified during class initialization.

    Parameters
    ----------
    patch_size_deg : float
        Patch size in degrees.

    ppd : int, optional
        Pixels per one degree. Defaults to 60.

    update_list : Iterable[Tuple[str, Callable[[float], AttributeValue]]], optional
        List of update pairs. First in pair is name of updated parameter. Second in pair the function itself.
        The function accepts only one float parameter denoting time that has passed from last update.

        Setting any value to be updated overrides their initial values.
        The initial value is then set to `update_function(0)`
        Attributes to update are `freq`, `theta` and or `phase`.

    freq : int, optional
        Frequency of generated gabor patch. Defaults to 6.

    theta: int, optional
        Rotation of the patch in degrees. Defaults to 45.

    phase: double, optional
        Phase shift of the gabor patch in radians. Defaults to 0.25.

    Attributes
    ----------
    freq : int, optional
        Frequency of generated gabor patch. With higher frequencies there are more lines and they are narrower

    theta: int, optional
        Rotation of the patch in degrees. The zero value (0 degrees) yields vertical lines,
        90 degrees yields horizontal lines.

    phase: float, optional
        Phase shift of the gabor patch in radians.

    Methods
    ----------
    get_normalized_patch
        Returns current normalized patch - without the usual `dt` update.

    get_grating
        Returns non-cut grating.

    get_get_gauss_cutout
        Returns circular gauss cutout.
    """
    TRIM = 0.005
    SIGMA = - np.pi / (8 ** 2)
    TWO_PI = 2 * np.pi

    AttributeValue = TypeVar('AttributeValue')

    def __init__(self, patch_size_deg, ppd=60,
                 update_list: Iterable[Tuple[str, Callable[[float], AttributeValue]]] = None,
                 freq=6, theta=45, phase=0.25):
        patch_size_px = int(patch_size_deg * ppd)
        super(GaborGenerator, self).__init__(width=patch_size_px, height=patch_size_px)

        self.update_list = update_list or []

        self.freq = freq  # lambda
        self.theta = theta  # changes orientation
        self.phase = phase

        w = fft.fftshift(fft.fftfreq(patch_size_px))
        self.mesh = np.meshgrid(w, w)

        self.gauss = self.get_gauss_cutout()

        self.__should_update_patch = True
        self.__normalized_patch = None

        # TODO: try to think about a different approach to double initialized values
        # Instead of update functions there could be initializer of updater classes passed
        self.__update__(0)

    def get_normalized_patch(self) -> np.ndarray:
        # if self.__should_update_patch:
        #     self.__normalized_patch = get_normalized(self.frame)
        #     self.__should_update_patch = False

        return self.__normalized_patch

    def __update_values__(self, dt=1) -> None:
        for name, update_function in self.update_list:
            self.__dict__[name] = update_function(dt)

            self.__should_update_patch = True
            self.__normalized_patch = None

    def __update__(self, dt=1) -> None:
        self.__update_values__(dt)

        if self.__should_update_patch:
            grating = self.get_grating()
            gabor = grating * self.gauss
            self.frame = gabor / gabor.max()

            self.__normalized_patch = get_normalized(self.frame)
            self.__should_update_patch = False

    def get_grating(self) -> np.ndarray:
        theta_rad = (self.theta / 360) * self.TWO_PI
        freq_rad = self.freq * self.TWO_PI
        phase_rad = self.phase * self.TWO_PI

        [mesh_w, mesh_h] = self.mesh
        x_t = mesh_w * np.cos(theta_rad)
        y_t = mesh_h * np.sin(theta_rad)

        xyt = x_t + y_t
        xyf = xyt * freq_rad
        return np.sin(xyf + phase_rad)

    def get_gauss_cutout(self) -> np.ndarray:
        [mesh_w, mesh_h] = self.mesh
        gauss = np.exp(((mesh_w ** 2) + (mesh_h ** 2)) / self.SIGMA)

        return np.clip(gauss, self.TRIM, gauss.max()) - self.TRIM


class PlaidGenerator(GaborGenerator):
    """Generator used to generate plaid patches of given size

      The patch can change in time if specified during class initialization.
    """

    def __init__(self, **kwargs):
        super(PlaidGenerator, self).__init__(**kwargs)

        self.gauss /= 2
        # We need to recompute the patches once again because we changed the gauss cutout
        self.__update__(0)

    def __update__(self, dt=1) -> None:
        self.__update_values__(dt)

        grating_a = self.get_grating()
        self.theta += 90
        grating_b = self.get_grating()
        self.theta -= 90

        grating = grating_a + grating_b
        gabor = grating * self.gauss

        self.frame = gabor / gabor.max()
