from generators.noise_generator import NoiseGenerator, StaticNoiseGenerator
from generators.pink_noise_generator import PinkNoise

from utils.simple_functions import interpolate


class ContinuousNoiseGenerator(NoiseGenerator):
    """ContinuousNoiseGenerator that iterates over a pre-defined list of noise frames.

    This ContinuousNoiseGenerator first generates a set list of noise frames.
    The list is iterated over back and forth to get edge frames for the underlying ContinuousNoiseGenerator


    Parameters
    ----------
    width : int
        Width of the generated noise

    height : int
        Height of the generated noise

    generator: StaticNoiseGenerator, optional
        The base StaticNoiseGenerator that is used to generate the list of defined frames.
        If not set the generator defaults to PinkNoise

    interpolate, optional


    Attributes
    ----------
    width : int
        Width of the generated noise

    height : int
        Height of the generated noise

    Methods
    -------
    get_next_frame(dt=1)
        Gets next frame. `dt` denotes the time that has passed between two consecutive generations.
    """

    def __init__(self, width: int, height: int, generator: StaticNoiseGenerator = None, interpolation=interpolate,
                 period=1,
                 **kwargs):
        super(ContinuousNoiseGenerator, self).__init__(width, height)

        self.generator = generator if generator is not None else PinkNoise(width, height)
        self.interpolation = interpolation

        self.origin = self.generator.get_next_frame()
        self.goal = self.generator.get_next_frame()

        self.period = period
        self.currentTime = 0.0

    def __set_new_goal__(self):
        self.origin = self.goal
        self.goal = self.generator.get_next_frame()

        self.currentTime -= self.period

    def __update__(self, dt=1) -> None:
        self.currentTime += dt

        while self.currentTime >= self.period:
            self.__set_new_goal__()

        perc = self.currentTime / self.period

        self.last_frame = self.interpolation(self.origin, self.goal, perc)
