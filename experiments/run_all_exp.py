from os import makedirs, chdir
from os.path import exists

from experiments.experiment_base import main

folder = 'results'
exists(folder) or makedirs(folder, exist_ok=True)
chdir(folder)

base_size = 500
contrast_settings = {'middle': 0.5, 'low': 0.2, 'high': 0.8}
position_settings = {'full': (0, 0), 'top_half': (base_size // 2, 0), 'right_half': (0, base_size // 2),
                     'quarter': (base_size // 2, base_size // 2)}
phase_settings = {'fast': 10, "middle": 5, "slow": 1}

for contrast_setting in contrast_settings:
    for position_setting in position_settings:
        for phase_setting in phase_settings:
            settings = {
                'contrast': contrast_settings[contrast_setting],
                'gabor_x': position_settings[position_setting][0],
                'gabor_y': position_settings[position_setting][1],
                'phase_speed': phase_settings[phase_setting],
                'size': base_size,
                'exp_name': f'{contrast_setting}_{position_setting}_gabor_phase_{phase_setting}',
                'len': 20,
                'delimiter': ';',
                'live': False,
            }

            main(settings)
