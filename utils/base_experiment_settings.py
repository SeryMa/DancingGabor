import winsound
from os import makedirs, chdir
from os.path import exists

from noise_processing.noise_with_csv_output import NoiseGeneratorWithCSVOutput
from outputs.video_output import VideoOutput
from utils.updater import LinUpdater


def ch_dir(folder):
    exists(folder) or makedirs(folder, exist_ok=True)
    chdir(folder)


def experiment_end():
    print('Experiment ended!')
    winsound.Beep(370, 500)
    winsound.Beep(370, 500)


def get_position_updater(patch_shift=(0, 0), patch_position=(0, 0)):
    if patch_shift[0] or patch_shift[1]:
        x_updater = LinUpdater(initial_value=patch_position[0], time_step=patch_shift[0])
        y_updater = LinUpdater(initial_value=patch_position[1], time_step=patch_shift[1])

        return lambda dt: (x_updater.update(dt), y_updater.update(dt))
    else:
        return lambda dt: patch_position


def get_patch_value_updates(value, speed_of_change, initial_value=0):
    return [(value, LinUpdater(initial_value=initial_value, time_step=speed_of_change).update)]


def generate_experiment_output(output_name, generator, fields, outputs):
    noise_generator = NoiseGeneratorWithCSVOutput(generator=generator,
                                                  file_name=output_name + ".csv",
                                                  field_names=fields, output_generators=outputs)

    output = VideoOutput(noise_generator.get_next_frame, base_size, base_size,
                         FPS=fps, length=length, video_name=output_name + ".avi")

    output.run()
    hasattr(output, '__del__') and output.__del__()
    noise_generator.__del__()


results_folder = 'results'

base_size = 200
length = 10
base_period = 1

ppd = 30
fps = 30
patch_size_deg = base_size / ppd

alpha = 0
beta = -0.5
gamma = 0.5

contrast_settings = {'middle': 0.5, 'low': 0.2, 'high': 0.8}
base_contrast = contrast_settings['middle']
position_settings = {'full': (0, 0), 'top_half': (base_size // 2, 0), 'right_half': (0, base_size // 2),
                     'quarter': (base_size // 2, base_size // 2)}
base_position = position_settings['full']

phase_settings = {'fast': 1, "middle": 0.1, "slow": 0.01, 'none': None}
theta_settings = {'fast': 10, "middle": 5, "slow": 1, 'none': None}
freq_settings = {'fast': 2, 'middle': 1, 'slow': .5, 'none': None}

patch_updates = {
    'phase': phase_settings,
    'theta': theta_settings,
    'freq': freq_settings,
}

granularities = {'high': 100, 'middle': 50, 'low': 10}
base_granularity = granularities['middle']

position_updates = {'fast': base_size // (2 * 20 / 2),
                    'middle': base_size // (2 * 20),
                    'slow': base_size // (2 * 40),
                    'none': 0}
