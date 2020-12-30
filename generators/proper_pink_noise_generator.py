import numpy as np
from numpy import fft

from generators.noise_generator import NoiseGenerator
from utils.array import normalize


class PinkNoise(NoiseGenerator):
    """ `NoiseGenerator` that generates pink noise in time

    Parameters
    ----------
    width : int
        Width of the generated noise

    height : int
        Height of the generated noise

    """

    def __init__(self, width, height, length=5, fps=30, deg=1 / 100):
        super(PinkNoise, self).__init__(width, height)

        self.length = length
        self.frames_count = fps * length

        w = fft.fftshift(fft.fftfreq(self.width))
        # w = w / degrees

        h = fft.fftshift(fft.fftfreq(self.height))
        # h = h / degrees

        t = fft.fftshift(fft.fftfreq(self.frames_count))
        t /= deg

        # In the 3-D case with inputs of length M, N and P,
        # outputs are of shape (N, M, P) for 'xy' indexing
        [mesh_w, mesh_t, mesh_h] = np.meshgrid(h, w, t)
        omega = np.sqrt(mesh_w ** 2 + mesh_h ** 2 + mesh_t ** 2)

        # This part deals with zero frequencies. There is only one present
        # and is replaced with next closest value
        zero_freq = omega == 0
        omega[zero_freq] = omega[~zero_freq].min()

        self.browner = 1 / omega

        self.__set_new_goal__()
        self.currentTime = 0

    def __set_new_goal__(self):
        base_noise = (np.random.rand(*self.browner.shape) * 2) - 1
        fft_noise = fft.fftshift(fft.fftn(base_noise))

        brown_noise = fft_noise * self.browner
        unclipped_noise = fft.ifftn(fft.ifftshift(brown_noise))

        std_un = np.std(unclipped_noise)
        clipped_noise = np.clip(unclipped_noise, -2 * std_un, 2 * std_un)
        clipped_noise = np.real(clipped_noise)

        normalize(clipped_noise)

        self.noise = clipped_noise

    def __update__(self, dt=1) -> None:
        self.currentTime += dt

        i = int((self.currentTime / self.length) * self.frames_count)

        self.frame = self.noise[:, :, i]
