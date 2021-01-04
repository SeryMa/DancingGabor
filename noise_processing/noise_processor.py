from numpy import ndarray

from generators.noise_generator import NoiseGenerator


class NoiseProcessor(NoiseGenerator):
    """ Abstract class which is used to transform and process given noise.

    On top of regular methods of NoiseGenerator class there is one new step in the update part. There is a new

    Parameters
    ----------
    generator : NoiseGenerator
        NoiseGenerator used to generate underlying noise.

    Attributes
    ----------
    frame : ndarray

    Methods
    -------
    get_next_frame()
        Gets next frame.
    """

    def __init__(self, generator: NoiseGenerator):
        self.noise_generator = generator
        super(NoiseProcessor, self).__init__(self.noise_generator.width, self.noise_generator.height)

    def __process__(self, dt=1) -> None:
        pass

    def __update__(self, dt=1) -> None:
        self.frame = self.noise_generator.get_next_frame(dt)
        self.__process__(dt)


class PersistentNoiseProcessor(NoiseProcessor):
    """ Abstract class which is used to transform and process given noise.

    On top of regular methods of NoiseGenerator class there is one new step in the update part.

    The update of the underlying noise MUST be done elsewhere. This class won't update the underlying noise by itself.
    This class is created to allow easier chaining of several NoiseProcessors

    Attributes
    ----------
    frame : ndarray

    Methods
    -------
    get_next_frame()
        Gets next frame.
    """

    def __update__(self, dt=1) -> None:
        # This is the change from NoiseProcessor which also updates the noise_generator
        self.frame = self.noise_generator.get_next_frame(0)
        self.__process__(dt)
