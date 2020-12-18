from numpy import ones, ndarray

from generators.noise_generator import StaticNoiseGenerator


class SingleColor(StaticNoiseGenerator):
    """ `StaticNoiseGenerator` that generates single color noise.

    Parameters
    ----------
    width : int
        Width of the generated noise

    height : int
        Height of the generated noise

    color:float
        The color the noise will have. It's automatically clipped to be within range [0,1].

    """

    def __init__(self, width, height, color=1):
        super(SingleColor, self).__init__(width, height)
        self.arr = ones((self.width, self.height)) * min(max(color, 0), 1)

    def get_next_frame(self) -> ndarray:
        return self.arr.copy()
