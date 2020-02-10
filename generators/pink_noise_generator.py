import numpy as np
from numpy import fft

from generators.noise_generator import StaticNoiseGenerator
from generators.white_noise_generator import WhiteNoise


class PinkNoise(StaticNoiseGenerator):
    def __init__(self, width, height, degrees=4):
        self.whiteNoise = WhiteNoise(width, height)
        self.degrees = degrees
        super(PinkNoise, self).__init__(width, height)

    def get_next_frame(self):
        base_noise = self.whiteNoise.get_next_frame() - 0.5
        fft_noise = fft.fftshift(fft.fft2(base_noise))

        w = fft.fftshift(fft.fftfreq(self.width))
        h = fft.fftshift(fft.fftfreq(self.height))
        w = w / self.degrees
        h = h / self.degrees
        [meshw, meshh] = np.meshgrid(h, w)
        # browner = np.sqrt(meshw ** 2 + meshh ** 2) ** (-1)
        browner = 1 / np.sqrt(meshw ** 2 + meshh ** 2)
        browner[np.isinf(browner)] = 0
        brown_noise = fft_noise * browner
        unclipped_noise = fft.ifft2(fft.ifftshift(brown_noise))

        std_un = np.std(unclipped_noise)
        clipped_noise = np.clip(unclipped_noise, -2 * std_un, 2 * std_un)
        clipped_noise = np.real(clipped_noise)

        return clipped_noise
