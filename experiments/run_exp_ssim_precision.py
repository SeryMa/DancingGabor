from experiments.base_experiment_settings import *
from experiments.run_single_experiment import run_experiment

ch_dir()
ch_dir('ssim_precision')

for x_position_update in position_updates:
    for y_position_update in position_updates:
        run_experiment(
            size=base_size,
            patch_shift_x=position_updates[x_position_update],
            patch_shift_y=position_updates[y_position_update],
            exp_name=f'ssim_precision_x_{x_position_update}_y_{y_position_update}',
            length=length,
            live=False,
        )
        experiment_end()
