from datetime import datetime
from os import makedirs, chdir
from os.path import exists

from cv2 import VideoWriter, VideoWriter_fourcc

from outputs.output import Output
from utils.array import cast_to_uint8


class VideoOutput(Output):
    def __init__(self, get_next_frame, width, height, video_name="tst", folder=None, fps=30, length=10, **kwargs):
        super(VideoOutput, self).__init__(get_next_frame, **kwargs)

        self.FPS = fps
        self.length = length

        if folder:
            exists(folder) or makedirs(folder)
            chdir(folder)

        fourcc = VideoWriter_fourcc(*'MP42')
        file_name = f'{video_name}_{width}_{height}_{datetime.now().microsecond}.avi'
        self.video = VideoWriter(file_name, fourcc, float(fps), (width, height), 0)

    def run(self):
        for _ in range(self.FPS * self.length):
            frame = cast_to_uint8(self.get_next_frame(dt=1 / self.FPS))
            self.video.write(frame)

    def __del__(self):
        self.video.release()
