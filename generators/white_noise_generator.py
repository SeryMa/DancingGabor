from numpy.random import rand

from generators.noise_generator import StaticNoiseGenerator


class WhiteNoise(StaticNoiseGenerator):
    def get_next_frame(self):
        return (rand(self.width, self.height) * 2) - 1
