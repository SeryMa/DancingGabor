from numpy import ones

from generators.noise_generator import StaticNoiseGenerator


class SingleColor(StaticNoiseGenerator):
    def __init__(self, width, height, color=1):
        super(SingleColor, self).__init__(width, height)
        self.arr = ones((self.width, self.height)) * color

    def get_next_frame(self):
        return self.arr.copy()
