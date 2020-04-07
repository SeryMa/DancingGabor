import numpy as np
import numpy.fft as fft

from generators.noise_generator import NoiseGenerator
from utils.array import get_normalized


# TODO: create a `StaticGaborGenerator` which would not compute a new gabor every iteration
#  but rather return a copy of precomputed array.
#  Possibly create a new function that would actually return gabor with given parameters.


class GaborGenerator(NoiseGenerator):
    TRIM = 0.005
    SIGMA = 0.32

    def __init__(self, patch_size_deg=2, ppd=60, update_list=None,
                 freq=6, theta=45, phase=0.25, **kwargs):
        patch_size_px = int(patch_size_deg * ppd)
        super(GaborGenerator, self).__init__(width=patch_size_px, height=patch_size_px)

        self.update_list = update_list or []

        self.freq = freq  # lambda
        self.theta = theta  # changes orientation
        self.phase = phase

        w = fft.fftshift(fft.fftfreq(patch_size_px))
        self.mesh = np.meshgrid(w, w)

        self.gauss = self.get_gauss_cutout()

        self.__should_update_normalized = True
        self.__normalized_patch = None

        # TODO: try to think about a different approach to double initialized values
        self.__update__(0)

    def get_normalized_patch(self):
        if self.__should_update_normalized:
            self.__normalized_patch = get_normalized(self.last_frame)
            self.__should_update_normalized = False

        return self.__normalized_patch

    def __update_values__(self, dt=1) -> None:
        for name, update_function in self.update_list:
            self.__dict__[name] = update_function(dt)

        self.__should_update_normalized = True
        self.__normalized_patch = None

    def __update__(self, dt=1) -> None:
        self.__update_values__(dt)

        grating = self.get_grating()
        gabor = grating * self.gauss
        self.last_frame = gabor / gabor.max()

    def get_grating(self):
        phase_rad = (self.phase * 2 * np.pi)
        theta_rad = (self.theta / 360) * 2 * np.pi

        [meshw, meshh] = self.mesh
        x_t = meshw * np.cos(theta_rad)
        y_t = meshh * np.sin(theta_rad)

        xyt = x_t + y_t
        xyf = xyt * self.freq * 2 * np.pi
        return np.sin((xyf + phase_rad))

    def get_gauss_cutout(self):
        [meshw, meshh] = self.mesh
        gauss = np.exp(-(((meshw ** 2) + (meshh ** 2)) / (self.SIGMA ** 2)))

        return np.clip(gauss, self.TRIM, gauss.max()) - self.TRIM


class PlaidGenerator(GaborGenerator):
    def __init__(self, **kwargs):
        super(PlaidGenerator, self).__init__(**kwargs)
        self.gauss /= 2

    def __update__(self, dt=1) -> None:
        self.__update_values__(dt)

        grating_a = self.get_grating()
        self.theta += 90
        grating_b = self.get_grating()
        self.theta -= 90

        grating = grating_a + grating_b
        gabor = grating * self.gauss

        self.last_frame = gabor / gabor.max()
