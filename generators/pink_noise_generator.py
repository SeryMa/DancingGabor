import numpy as np
from numpy import fft

from generators.noise_generator import StaticNoiseGenerator
from generators.white_noise_generator import WhiteNoise


class PinkNoise(StaticNoiseGenerator):
    def __init__(self, width, height, degrees=4):
        self.whiteNoise = WhiteNoise(width, height)
        super(PinkNoise, self).__init__(width, height)

        w = fft.fftshift(fft.fftfreq(self.width))
        w = w / degrees

        h = fft.fftshift(fft.fftfreq(self.height))
        h = h / degrees

        [mesh_w, mesh_h] = np.meshgrid(h, w)
        self.browner = 1 / np.sqrt(mesh_w ** 2 + mesh_h ** 2)
        self.browner[np.isinf(self.browner)] = 0

    def get_next_frame(self):
        base_noise = self.whiteNoise.get_next_frame()
        fft_noise = fft.fftshift(fft.fft2(base_noise))

        brown_noise = fft_noise * self.browner
        unclipped_noise = fft.ifft2(fft.ifftshift(brown_noise))

        std_un = np.std(unclipped_noise)
        clipped_noise = np.clip(unclipped_noise, -2 * std_un, 2 * std_un)
        clipped_noise = np.real(clipped_noise)

        return clipped_noise / clipped_noise.max()
