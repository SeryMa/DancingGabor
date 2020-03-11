import argparse

from generators.continuous_noise_generator import ContinuousNoiseGenerator
from generators.gabor_generator import GaborGenerator
from generators.patched_noise_generator import PatchedNoiseGenerator
from generators.pink_noise_generator import PinkNoise
from noise_processing.heat_map_generator import HeatMapGenerator
from outputs.pyglet_app import PygletOutput
from utils.updater import LinUpdater


def get_command_line_args():
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--size", default=500, type=int, help="Size")
    parser.add_argument("--len", default=1, type=int, help="Length of observation")

    parser.add_argument("--seed", default=42, type=int, help="Seed for the random generator")
    return parser.parse_args().__dict__


args = get_command_line_args()
width = height = args['size']
length = args['len']

pink_noise_generator = ContinuousNoiseGenerator(width, height, PinkNoise(width, height))

ppd = 80
gabor_generator = GaborGenerator(patch_size_deg=width / ppd, ppd=ppd, update_list=[
    ('phase', LinUpdater(initial_value=0.00, time_step=1).update)
    #  ('patch_size_deg', LinUpdater(initial_value=1, time_step=1).update)
])

noise_with_gabor = PatchedNoiseGenerator(width, height, pink_noise_generator, [(gabor_generator, lambda dt: (0, 0))])

# noise_generator = NoiseGeneratorWithCSVOutput(generator=noise_with_gabor, output_values=[
#     lambda: get_luminance(noise_with_gabor.get_next_frame(0)),
#     lambda: get_rms_contrast(noise_with_gabor.get_next_frame(0)),
#     lambda: get_luminance(gabor_generator.get_next_frame(0)),
#     lambda: get_rms_contrast(gabor_generator.get_next_frame(0)),
# ])

noise_generator = HeatMapGenerator(noise_with_gabor)

output = PygletOutput(noise_generator.get_next_frame, width, height)
output.run()
