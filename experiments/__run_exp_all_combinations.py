from experiments.base_experiment_settings import *
from experiments.run_single_experiment import run_experiment

ch_dir()

for contrast_setting in contrast_settings:
    for position_setting in position_settings:
        for x_position_update in position_updates:
            for y_position_update in position_updates:
                for patch_update in patch_updates:
                    for value_change in patch_updates[patch_update]:
                        settings = {
                            'contrast': contrast_settings[contrast_setting],
                            'gabor_position': position_settings[position_setting],
                            'gabor_shift_x': position_updates[x_position_update],
                            'gabor_shift_y': position_updates[y_position_update],
                            f'{patch_update}_speed': patch_updates[patch_update][value_change],
                            'size': base_size,
                            'exp_name': f'{contrast_setting}_{position_setting}_patch_{patch_update}_{value_change}_{x_position_update}_{y_position_update}',
                            'len': 20,
                            'live': False,
                        }

                        run_experiment(**settings)

                        experiment_end()
