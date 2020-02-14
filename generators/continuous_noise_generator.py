from generators.noise_generator import NoiseGenerator, StaticNoiseGenerator
from generators.pink_noise_generator import PinkNoise

from utils.simple_functions import interpolate


class ContinuousNoiseGenerator(NoiseGenerator):
    def __init__(self, width, height, generator: StaticNoiseGenerator = None, interpolation=interpolate, period=1,
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

    def get_next_frame(self, dt=1):
        self.currentTime += dt

        while self.currentTime >= self.period:
            self.__set_new_goal__()

        perc = self.currentTime / self.period
        frame = self.interpolation(self.origin, self.goal, perc)

        return frame
