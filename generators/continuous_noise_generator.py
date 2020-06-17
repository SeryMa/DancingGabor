from typing import Callable

from numpy import ndarray

from generators.noise_generator import NoiseGenerator, StaticNoiseGenerator
from generators.pink_noise_generator import PinkNoise
from utils.simple_functions import interpolate


class ContinuousNoiseGenerator(NoiseGenerator):
    """ `NoiseGenerator` that takes `StaticNoiseGenerator` and creates a continuous time stream of noise images

    After `period` time units new image from `generator` is generated. Using function `interpolate` a new image noise
    is generated for given time. That way we can create a continuous stream of noise images.

    Parameters
    ----------
    width : int
        Width of the generated noise

    height : int
        Height of the generated noise

    generator : StaticNoiseGenerator, optional
        The base StaticNoiseGenerator that is used to generate the list of defined frames.
        If not set the generator defaults to `PinkNoise`

    interpolate : Callable[[ndarray, ndarray, float], ndarray], optional
        Function that is used to interpolate between two consecutive noise images. The function accepts two noise parameters.
        The starting noise and it's eventual goal noise. Third argument denotes the percentage of similarity (0 being the starting noise, 1 being the goal noise).
        Defaults to linear interpolation of the noises.

    period : int
        Time period after which new frame from `generator` is generated.

    Attributes
    ----------
    width : int
        Width of the generated noise

    height : int
        Height of the generated noise
    """

    def __init__(self, width: int, height: int, generator: StaticNoiseGenerator = None,
                 interpolation: Callable[[ndarray, ndarray, float], ndarray] = interpolate, period=1, **kwargs):
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

        self.frame = self.interpolation(self.origin, self.goal, perc)
