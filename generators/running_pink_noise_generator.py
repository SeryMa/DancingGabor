import numpy as np
from numpy import fft

from generators.noise_generator import NoiseGenerator
from generators.white_noise_generator import WhiteNoise
from utils.array import normalize


class RunningPinkNoise(NoiseGenerator):
    """ `StaticNoiseGenerator` that generates pink noise images

    Parameters
    ----------
    width : int
        Width of the generated noise

    height : int
        Height of the generated noise

    """

    def __init__(self, width, height, period):
        super(RunningPinkNoise, self).__init__(width, height)

        self.offset_width = width // 20
        self.whiteNoise = WhiteNoise(width + self.offset_width * 2, height)

        w = fft.fftshift(fft.fftfreq(self.width + self.offset_width * 2))
        # w = w / degrees

        h = fft.fftshift(fft.fftfreq(self.height))
        # h = h / degrees

        [mesh_w, mesh_h] = np.meshgrid(h, w)
        omega = np.sqrt(mesh_w ** 2 + mesh_h ** 2)

        # This part deals with zero frequencies. There is only one present
        # and is replaced with next closest value
        zero_freq = omega == 0
        omega[zero_freq] = omega[~zero_freq].min()

        self.browner = 1 / omega
        self.currentTime = 0.0
        self.period = period

        self.base_noise = np.concatenate((self.whiteNoise.get_next_frame(), self.whiteNoise.get_next_frame()))

    def __set_new_goal__(self):
        self.base_noise[0:self.width + self.offset_width * 2, 0:] = \
            self.base_noise[self.width + self.offset_width * 2:, 0:]
        self.base_noise[self.width + self.offset_width * 2:, 0:] = \
            self.whiteNoise.get_next_frame()

        self.currentTime -= self.period

    def __update__(self, dt=1) -> None:
        self.currentTime += dt

        while self.currentTime >= self.period:
            self.__set_new_goal__()

        i = int((self.currentTime / self.period) * (self.width + self.offset_width * 2))

        base_noise = self.base_noise[i:i + self.width + self.offset_width * 2, 0:]
        fft_noise = fft.fftshift(fft.fft2(base_noise))

        brown_noise = fft_noise * self.browner
        unclipped_noise = fft.ifft2(fft.ifftshift(brown_noise))

        std_un = np.std(unclipped_noise)
        clipped_noise = np.clip(unclipped_noise, -2 * std_un, 2 * std_un)
        clipped_noise = np.real(clipped_noise)

        normalize(clipped_noise)

        self.frame = clipped_noise[self.offset_width:self.offset_width + self.width, 0:]
