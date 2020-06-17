from numpy import ndarray

from generators.noise_generator import StaticNoiseGenerator
from generators.pink_noise_generator import PinkNoise


class CircularNoiseGenerator(StaticNoiseGenerator):
    """ Class that is used to generated repeated cyclic patterns.

    The `CircularNoiseGenerator` takes `StaticNoiseGenerator` and pre-generates a sequence of frames.
    Every call to `get_next_frame` takes next frame in the sequence. Based on `reverse_return` variable
    different cyclic strategies are used.

    Parameters
    ----------
    width : int
        Width of the generated noise

    height : int
        Height of the generated noise
    generator : StaticNoiseGenerator, optional
        Generator that is used to pre-generate the frame sequence
    sequence_length : int, optional
        Length of the frame sequence
    reverse_return : bool, optional
        Defines how is the sequence re-iterated. Either by starting the iteration over (`False` value) or going through the sequence in reversed order (`False` value).

    Methods
    -------
    get_next_frame:
        Gets next frame in the sequence.
    """

    def __init__(self, width: int, height: int, generator: StaticNoiseGenerator = None, sequence_length=2,
                 reverse_return=True):
        super(CircularNoiseGenerator, self).__init__(width, height)

        generator = generator if generator is not None else PinkNoise(width, height)
        self.frame_sequence = [generator.get_next_frame() for _ in range(sequence_length)]

        self.seq_index = 0
        self.direction = +1
        self.start_over = reverse_return

    def get_next_frame(self) -> ndarray:
        frame = self.frame_sequence[self.seq_index].copy()

        self.seq_index += self.direction

        if self.seq_index + 1 == len(self.frame_sequence) or self.seq_index == 0:
            if self.start_over:
                self.seq_index = 0
            else:
                self.direction *= -1

        return frame
