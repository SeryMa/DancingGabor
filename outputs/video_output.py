from cv2 import VideoWriter, VideoWriter_fourcc

from outputs.output import Output
from utils.array import cast_to_uint8
from utils.simple_functions import construct_file_name


class VideoOutput(Output):
    def __init__(self, get_next_frame, width, height, video_name='', fps=30, length=10, secondary_outputs=None,
                 **kwargs):
        super(VideoOutput, self).__init__(get_next_frame, **kwargs)

        self.FPS = fps
        self.length = length

        fourcc = VideoWriter_fourcc(*'MP42')
        self.file_name = video_name or construct_file_name(video_name, extension='avi')
        self.video = VideoWriter(self.file_name, fourcc, float(fps), (width, height), 0)

        self.secondary_outputs = []
        for secondary_output_name, secondary_output_generator in secondary_outputs or []:
            split_name = self.file_name.split('.')
            split_name[-2] += f'_{secondary_output_name}'
            self.secondary_outputs.append(
                (secondary_output_generator, VideoWriter('.'.join(split_name), fourcc, float(fps), (width, height), 0))
            )

    def run(self):
        for _ in range(self.FPS * self.length):
            frame = cast_to_uint8(self.get_next_frame(dt=1 / self.FPS))
            self.video.write(frame)

            for secondary_output_generator, secondary_output_writer in self.secondary_outputs:
                secondary_frame = cast_to_uint8(secondary_output_generator(0))
                secondary_output_writer.write(secondary_frame)

    def __del__(self):
        self.video.release()

        for _, secondary_output_writer in self.secondary_outputs:
            secondary_output_writer.release()
