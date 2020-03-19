import winsound

from experiments.graphs import *
from generators.continuous_noise_generator import ContinuousNoiseGenerator
from generators.gabor_generator import GaborGenerator
from generators.patched_noise_generator import PatchedNoiseGenerator
from generators.pink_noise_generator import PinkNoise
from noise_processing.noise_with_csv_output import NoiseGeneratorWithCSVOutput
from outputs.pyglet_app import PygletOutput
from outputs.video_output import VideoOutput
from utils.image import get_rms_contrast, get_luminance, ssim
from utils.simple_functions import construct_file_name
from utils.updater import LinUpdater


def get_command_line_args():
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--exp_name", default="high_contrast_20s_period_full_gabor", type=str,
                        help="Name of the output files")

    parser.add_argument("--size", default=500, type=int, help="Size")
    parser.add_argument("--len", default=10, type=int, help="Length of observation")

    parser.add_argument("--gabor_x", default=0, type=int, help="X position of the gabor patch")
    parser.add_argument("--gabor_y", default=0, type=int, help="Y position of the gabor patch")

    parser.add_argument("--contrast", default=0.5, type=float, help="Contrast used to display patch")

    parser.add_argument("--seed", default=42, type=int, help="Seed for the random generator")
    parser.add_argument("--live", default=False, type=bool, help="Should live preview be shown")
    parser.add_argument("--delimiter", default=';', type=str, help="CSV value delimiter")
    return parser.parse_args().__dict__


def main(args=None):
    args = args or get_command_line_args()
    width = height = args['size']
    length = args['len']

    base_noise = ContinuousNoiseGenerator(width, height, PinkNoise(width, height), period=1)

    ppd = 80
    gabor_generator = GaborGenerator(patch_size_deg=width / ppd, ppd=ppd, update_list=[
        ('phase', LinUpdater(initial_value=0.00, time_step=args['phase_speed']).update)
        # ('theta', LinUpdater(initial_value=0, time_step=10).update)
    ])

    gabor_position = (args['gabor_x'], args['gabor_y'])
    noise_with_gabor = PatchedNoiseGenerator(width, height, base_noise, [(gabor_generator, lambda dt: gabor_position)],
                                             contrast=args['contrast'])

    output_name = construct_file_name(args['exp_name'])
    noise_generator = NoiseGeneratorWithCSVOutput(generator=noise_with_gabor,
                                                  file_name=output_name + ".csv",
                                                  fieldnames=[
                                                      'luminance_with_gabor',
                                                      'contrast_with_gabor',
                                                      'luminance_without_gabor',
                                                      'contrast_without_gabor',
                                                      'luminance_gabor',
                                                      'contrast_gabor',

                                                      'ssim_noise_vs_gabor',
                                                      'ssim_gabor_noise_vs_gabor',
                                                  ],

                                                  output_values=[
                                                      lambda: get_luminance(noise_with_gabor.get_next_frame(0)),
                                                      lambda: get_rms_contrast(noise_with_gabor.get_next_frame(0)),
                                                      lambda: get_luminance(base_noise.get_next_frame(0)),
                                                      lambda: get_rms_contrast(base_noise.get_next_frame(0)),
                                                      lambda: get_luminance(gabor_generator.get_next_frame(0)),
                                                      lambda: get_rms_contrast(gabor_generator.get_next_frame(0)),

                                                      lambda: ssim(base_noise.get_next_frame(0),
                                                                   gabor_generator.get_next_frame(0)),
                                                      lambda: ssim(noise_with_gabor.get_next_frame(0),
                                                                   gabor_generator.get_next_frame(0)),
                                                  ])

    if args['live']:
        output = PygletOutput(noise_generator.get_next_frame, width, height)
    else:
        output = VideoOutput(noise_generator.get_next_frame, width, height, FPS=50, length=length,
                             video_name=output_name + ".avi")

    output.run()
    output.__del__()
    noise_generator.__del__()

    # GRAPHS part starts here!

    delimiter = args['delimiter']

    data = get_data(output_name + '.csv', delimiter)

    fig, (ax1, ax2, ax3) = get_axes()

    # luminance plot:
    plot(ax1, data[0], [data[1], data[3], data[5]], labels=['Noise with gabor', 'Noise without gabor', 'Gabor'],
         title='Luminance values')

    # contrast plot
    plot(ax2, data[0], [data[2], data[4], data[6]], labels=['Noise with gabor', 'Noise without gabor', 'Gabor'],
         title='Contrast values')

    # SSIM
    plot(ax3, data[0], [data[7], data[8]], labels=['noise vs gabor', 'gabor noise vs gabor'],
         title='SSIM values')

    if args["live"]:
        plt.show()
    else:
        plt.savefig(output_name + '.pdf')
        plt.savefig(output_name + '.png')

    winsound.Beep(370, 500)
    winsound.Beep(370, 500)
    winsound.Beep(370, 500)
    winsound.Beep(370, 500)
    winsound.Beep(370, 500)


if __name__ == '__main__':
    main()
