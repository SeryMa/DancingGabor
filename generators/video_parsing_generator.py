from cv2 import VideoCapture, waitKey
from numpy import ndarray

from generators.noise_generator import NoiseGenerator


class VideoParsingGenerator(NoiseGenerator):
    """ `NoiseGenerator` that parses a video stream into `ndarray`.

    Width and Height of the noise is derived from the video file.

    Parameters
    ----------
    file_name : str
        Name of the video file.
    """

    def __init__(self, file_name):
        self.capture = VideoCapture(file_name)

        width = int(self.capture.get(3))
        height = int(self.capture.get(4))

        super(VideoParsingGenerator, self).__init__(width, height)
        waitKey(0)

    def get_next_frame(self, dt=1) -> ndarray:
        waitKey(int(dt * 1000))
        if not self.capture.isOpened():
            raise ValueError

        _, all_chanels_frame = self.capture.read()

        # TODO: this part relies on greyscale images
        frame = all_chanels_frame[:, :, 0]
        return frame / frame.max()

    def __del__(self):
        self.capture.release()
