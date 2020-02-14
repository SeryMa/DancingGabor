import numpy as np
import numpy.fft as fft

from generators.noise_generator import NoiseGenerator


class GaborGenerator(NoiseGenerator):
    TRIM = 0.005

    def __init__(self, patch_size_deg=2, ppd=60, update_list=None,
                 contr=1, freq=6, bandwidth=4, theta=45, phase=0.25, **kwargs):
        self.__ppd__ = ppd
        self.patch_size_px = int(patch_size_deg * ppd)
        width = height = np.sqrt(self.patch_size_px)

        super(GaborGenerator, self).__init__(width, height)

        self.update_list = update_list or []

        self.contr = contr  # doesn't react to any change...
        self.freq = freq  # lambda
        self.bandwidth = bandwidth  # doesn't react to any change...
        self.theta = theta  # changes orientation
        self.phase = phase

        # TODO: try to think about a different approach to double initialized values
        self.__update__(0)

    def __update__(self, dt):
        for name, update_function in self.update_list:
            self.__dict__[name] = update_function(dt)

    def get_next_frame(self, dt=1):
        self.__update__(dt)

        sigmadeg = (np.sqrt(np.log(4)) / (2 * np.pi * 6)) * ((2 ** (self.bandwidth + 1)) / (2 ** (self.bandwidth - 1)))
        sigma = sigmadeg * self.__ppd__

        phase_rad = (self.phase * 2 * np.pi)

        w = fft.fftshift(fft.fftfreq(self.patch_size_px))
        [meshw, meshh] = np.meshgrid(w, w)

        theta_rad = (self.theta / 360) * 2 * np.pi

        x_t = meshw * np.cos(theta_rad)
        y_t = meshh * np.sin(theta_rad)

        xyt = x_t + y_t
        xyf = xyt * self.freq * 2 * np.pi
        grating = self.contr * np.sin((xyf + phase_rad))

        s = sigma / self.patch_size_px
        gauss = np.exp(-(((meshw ** 2) + (meshh ** 2)) / (2 * s ** 2)))

        gauss = np.clip(gauss, self.TRIM, gauss.max()) - self.TRIM
        return grating * gauss


class PlaidGenerator(GaborGenerator):
    def __init__(self, **kwargs):
        self.second_generator = GaborGenerator(**kwargs)

        super(PlaidGenerator, self).__init__(**kwargs)

    def __update__(self, dt):
        super(PlaidGenerator, self).__update__(dt)
        self.theta = self.second_generator.theta + 90

    def get_next_frame(self, dt=1):
        gabor_a = self.second_generator.get_next_frame(dt)
        gabor_b = super(PlaidGenerator, self).get_next_frame(dt)

        return gabor_b + gabor_a
