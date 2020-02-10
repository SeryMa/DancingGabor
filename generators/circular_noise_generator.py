from generators.continuous_noise_generator import ContinuousNoiseGenerator
from generators.noise_generator import StaticNoiseGenerator
from utils.simple_functions import interpolate


class CircularNoiseGenerator(ContinuousNoiseGenerator):
    def __init__(self, width, height, generator: StaticNoiseGenerator = None, interpolation=interpolate, period=1,
                 sequence_length=2, **kwargs):
        super(CircularNoiseGenerator, self).__init__(width, height, generator, interpolation, period, **kwargs)

        self.frame_sequence = [generator.get_next_frame() for _ in range(sequence_length)]
        self.seq_index = 0
        self.direction = +1

    def __set_new_goal__(self):
        self.seq_index += self.direction
        self.origin = self.goal
        self.goal = self.frame_sequence[self.seq_index]

        if self.seq_index == 0 or self.seq_index + 1 == len(self.frame_sequence):
            self.direction *= -1

        self.currentTime -= self.period
