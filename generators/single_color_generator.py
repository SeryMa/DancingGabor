from numpy import ones, ndarray

from generators.noise_generator import StaticNoiseGenerator


class SingleColor(StaticNoiseGenerator):
    """ `StaticNoiseGenerator` that generates single color noise.

    The class was designed to be simple, so no there is no normalization.

    Parameters
    ----------
    width : int
        Width of the generated noise

    height : int
        Height of the generated noise

    color:float
        The color the noise will have. It should be within range [0,1].

    """

    def __init__(self, width, height, color=1):
        super(SingleColor, self).__init__(width, height)
        self.arr = ones((self.width, self.height)) * color

    def get_next_frame(self) -> ndarray:
        return self.arr.copy()
