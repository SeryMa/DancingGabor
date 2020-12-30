import numpy as np
from numpy import fft

from generators.noise_generator import StaticNoiseGenerator
from generators.white_noise_generator import WhiteNoise
from utils.array import normalize


class PinkNoise(StaticNoiseGenerator):
    """ `StaticNoiseGenerator` that generates pink noise images

    Parameters
    ----------
    width : int
        Width of the generated noise

    height : int
        Height of the generated noise

    """

    def __init__(self, width, height):
        self.whiteNoise = WhiteNoise(width, height)
        super(PinkNoise, self).__init__(width, height)

        w = fft.fftshift(fft.fftfreq(self.width))
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

        # inf_browner = np.isposinf(self.browner)
        # self.browner[inf_browner] = self.browner[~inf_browner].max()

    def get_next_frame(self) -> np.ndarray:
        base_noise = self.whiteNoise.get_next_frame()
        fft_noise = fft.fftshift(fft.fft2(base_noise))

        brown_noise = fft_noise * self.browner
        unclipped_noise = fft.ifft2(fft.ifftshift(brown_noise))

        std_un = np.std(unclipped_noise)
        clipped_noise = np.clip(unclipped_noise, -2 * std_un, 2 * std_un)
        clipped_noise = np.real(clipped_noise)

        normalize(clipped_noise)
        return clipped_noise
