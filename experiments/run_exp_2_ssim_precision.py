from experiments.base_experiment_settings import *
from experiments.run_single_experiment import run_experiment

ch_dir()
ch_dir('2_ssim_precision')

for x_position_update in position_updates:
    for y_position_update in position_updates:
        run_experiment(
            size=base_size,
            patch_shift_x=position_updates[x_position_update],
            patch_shift_y=position_updates[y_position_update],
            exp_name=f'ssim_precision_x_{x_position_update}_y_{y_position_update}',
            output_values=['ssim', 'cw_ssim'],
            alpha=0, beta=-0.5, gamma=0.5,
            length=length,
            live=False,
        )
        experiment_end()
