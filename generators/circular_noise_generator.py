from numpy import ndarray

from generators.noise_generator import StaticNoiseGenerator
from generators.pink_noise_generator import PinkNoise


class CircularNoiseGenerator(StaticNoiseGenerator):
    def __init__(self, width: int, height: int, generator: StaticNoiseGenerator = None, sequence_length=2):
        super(CircularNoiseGenerator, self).__init__(width, height)

        generator = generator if generator is not None else PinkNoise(width, height)
        self.frame_sequence = [generator.get_next_frame() for _ in range(sequence_length)]

        self.seq_index = 0
        self.direction = +1

    def get_next_frame(self) -> ndarray:
        frame = self.frame_sequence[self.seq_index].copy()

        self.seq_index += self.direction

        if self.seq_index == 0 or self.seq_index + 1 == len(self.frame_sequence):
            self.direction *= -1

        return frame
