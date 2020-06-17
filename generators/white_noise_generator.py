from numpy.random import rand

from generators.noise_generator import StaticNoiseGenerator


class WhiteNoise(StaticNoiseGenerator):
    """ `StaticNoiseGenerator` that generates white noise images
    """

    def get_next_frame(self):
        return (rand(self.width, self.height) * 2) - 1
