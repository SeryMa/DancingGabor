from numpy import ndarray


# TODO: Think about making this class abstract - is there a way how to do that in Pytohn? It should be...
# TODO: generalize this class to be able to return nD arrays instead of fixed 2D
class NoiseGenerator:
    """ Abstract class which is used to generate a 2D noise, which changes in time.

    The consecutive generations are dependent on each other.

    Parameters
    ----------
    width : int
        Width of the generated noise

    height : int
        Height of the generated noise

    Attributes
    ----------
    width : int
        Width of the generated noise

    height : int
        Height of the generated noise

    frame : ndarray
        The last frame that has been generated

    Methods
    -------
    get_next_frame(dt=1)
        Gets next frame. `dt` denotes the time that has passed between two consecutive generations.

        Should always returns a copy of `frame` to prevent unwanted modifications.
    """

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height

        self.frame = None

    def __update__(self, dt=1) -> None:
        """Updates inner variables.

        Gets called in `get_next_frame` if positive `dt` is passed (or if it's the very first call)
        This method should always update the `frame` so `get_next_frame` can return the most recent one.

        Parameters
        ----------
        dt : int
            The time that has passed since last update.
        """
        pass

    def get_next_frame(self, dt=1) -> ndarray:
        if dt > 0 or self.frame is None:
            self.__update__(dt)

        return self.frame.copy()


class StaticNoiseGenerator:
    """ Abstract class which is used to generate a 2D noise, which changes in time.

    Several consecutive generations are independent of each others.

    Parameters
    ----------
    width : int
        Width of the generated noise

    height : int
        Height of the generated noise

    Attributes
    ----------
    width : int
        Width of the generated noise

    height : int
        Height of the generated noise

    Methods
    -------
    get_next_frame()
        Gets next frame.
    """

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height

    def get_next_frame(self) -> ndarray:
        pass
