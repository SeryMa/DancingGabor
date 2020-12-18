from PIL import Image
from PIL.ImageOps import colorize

from outputs.output import Output
from utils.array import cast_to_uint8


class ImageOutput(Output):
    def __init__(self, get_next_frame, file_name, fps=30, length=10, secondary_outputs=None,
                 **kwargs):
        super(ImageOutput, self).__init__(get_next_frame, **kwargs)

        self.FPS = fps
        self.length = length

        self.file_name = file_name
        self.color_palette = kwargs

        self.secondary_outputs = [] if secondary_outputs is None else secondary_outputs

    def run(self):
        for frame_no in range(self.FPS * self.length):
            frame = cast_to_uint8(self.get_next_frame(dt=1. / self.FPS))
            img = Image.fromarray(frame, 'L')
            if self.color_palette:
                img = colorize(img, **self.color_palette)
            img.save(f'{self.file_name}_{frame_no}.png')

            for secondary_output_name, secondary_output_generator in self.secondary_outputs:
                secondary_frame = cast_to_uint8(secondary_output_generator(0))
                Image.fromarray(secondary_frame, 'L').save(f'{self.file_name}_{secondary_output_name}_{frame_no}.png')
