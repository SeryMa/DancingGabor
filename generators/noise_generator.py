from numpy import ndarray


# TODO: Think about making this class abstract - is there a way how to do that in Pytohn? It should be...
# TODO: generalize this class to be able to return nD arrays instead of fixed 2D
class NoiseGenerator:
    """
    Abstract class which is used to generate a 2D noise, which changes in time.
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

    Methods
    -------
    get_next_frame(dt=1)
        Gets next frame. `dt` denotes the time that has passed between two consecutive generations.
    """

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height

    def get_next_frame(self, dt=1) -> ndarray:
        """Generates next frame.

        Parameters
        ----------
        dt : int
            The time that has passed after generating last frame.

        Returns
        ----------
        ndarray
        """
        pass


class StaticNoiseGenerator:
    """
    Abstract class which is used to generate a 2D noise, which changes in time.
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
        """Generates next frame.

        Returns
        ----------
        ndarray
        """
        pass
