from outputs.pyglet_app import PygletOutput
from outputs.video_output import VideoOutput
from utils.argument_parser import prepare_app

noise_generator, args = prepare_app()

if args['live']:
    output = PygletOutput(noise_generator.get_next_frame, **args)
    # output = PygletDiffOutput(noise_generator.get_next_frame, **args)
else:
    output = VideoOutput(noise_generator.get_next_frame, video_name=args['file_name'], **args)

output.run()
