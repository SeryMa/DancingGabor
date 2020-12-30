from base_experiment_settings import *
from experiments.run_single_experiment import run_experiment

if __name__ == '__main__':
    ch_dir('0_test_running')

    for contrast_setting in contrast_settings:
        for position_setting in position_settings:
            run_experiment(
                contrast=contrast_settings[contrast_setting],
                patch_position=position_settings[position_setting],
                size=base_size,
                exp_name=f'run_{contrast_setting}_{position_setting}_patch',
                output_values=['Luminance', 'Contrast', 'Structure', 'CW_Structure'],
                length=length,
                live=False,
            )
            experiment_end()

    for contrast_setting in contrast_settings:
        for position_setting in position_settings:
            run_experiment(
                contrast=contrast_settings[contrast_setting],
                patch_position=position_settings[position_setting],
                size=base_size,
                exp_name=f'v2_{contrast_setting}_{position_setting}_patch',
                output_values=['Luminance', 'Contrast', 'Structure', 'CW_Structure'],
                length=length,
                live=False,
            )
            experiment_end()
