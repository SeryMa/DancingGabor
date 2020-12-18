from experiments.base_experiment_settings import *
from experiments.run_single_experiment import run_experiment

ch_dir()
ch_dir('1_simple_poc')

for contrast_setting in contrast_settings:
    for position_setting in position_settings:
        run_experiment(
            contrast=contrast_settings[contrast_setting],
            patch_position=position_settings[position_setting],
            size=base_size,
            exp_name=f'{contrast_setting}_{position_setting}_patch',
            output_values=['Luminance', 'Contrast', 'Structure'],
            length=length,
            live=False,
        )
        experiment_end()
