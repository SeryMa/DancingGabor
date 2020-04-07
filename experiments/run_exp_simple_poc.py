from experiments.base_experiment_settings import *

ch_dir()
ch_dir('simple_poc')

for contrast_setting in contrast_settings:
    for position_setting in position_settings:
        run_experiment(
            contrast=contrast_settings[contrast_setting],
            patch_position=position_settings[position_setting],
            size=base_size,
            exp_name=f'{contrast_setting}_{position_setting}_patch',
            length=length,
            live=False,
        )
        experiment_end()
