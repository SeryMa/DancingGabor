import cv2
from cv2 import VideoCapture, waitKey, CAP_PROP_FRAME_WIDTH, CAP_PROP_FRAME_HEIGHT
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

    def __init__(self, file_name, live=True, fps=30):
        self.capture = VideoCapture(file_name)

        width = int(self.capture.get(CAP_PROP_FRAME_WIDTH))
        height = int(self.capture.get(CAP_PROP_FRAME_HEIGHT))

        self.live = live

        self.capture.set(cv2.CAP_PROP_FPS, fps)

        super(VideoParsingGenerator, self).__init__(width, height)
        waitKey(0)

    def get_next_frame(self, dt=1) -> ndarray:
        if self.live:
            waitKey(int(dt * 1000))
        if not self.capture.isOpened():
            raise ValueError

        _, all_channels_frame = self.capture.read()

        # TODO: this part relies on greyscale images
        frame = all_channels_frame[:, :, 0]
        return frame / frame.max()

    def __del__(self):
        self.capture.release()
