from generators.noise_generator import NoiseGenerator, StaticNoiseGenerator
from generators.pink_noise_generator import PinkNoise


class SingleNoiseGenerator(NoiseGenerator):
    """ `NoiseGenerator` that creates a continuous time stream of a single noise instance of given `StaticNoiseGenerator`


    Parameters
    ----------
    width : int
        Width of the generated noise

    height : int
        Height of the generated noise

    generator : StaticNoiseGenerator, optional
        The base StaticNoiseGenerator that is used to generate the list of defined frames.
        If not set the generator defaults to `PinkNoise`

    Attributes
    ----------
    width : int
        Width of the generated noise

    height : int
        Height of the generated noise
    """

    def __init__(self, width: int, height: int, generator: StaticNoiseGenerator = None):
        super(SingleNoiseGenerator, self).__init__(width, height)

        generator = generator if generator is not None else PinkNoise(width, height)

        self.frame = generator.get_next_frame()
