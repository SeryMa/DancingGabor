from experiments.base_experiment_settings import *
from experiments.run_single_experiment import run_experiment

ch_dir()
ch_dir('4_moving_gabor_adv_detection')

for x_position_update in position_updates:
    for y_position_update in position_updates:
        run_experiment(size=base_size,
                       patch_shift_x=position_updates[x_position_update],
                       patch_shift_y=position_updates[y_position_update],
                       length=length,
                       live=False,
                       exp_name=f'adv_detection_precision_x_{x_position_update}_y_{y_position_update}',
                       output_values=['pattern_search_ssim', 'ssim', 'pattern_search_cw_ssim', 'cw_ssim'],
                       alpha=0, beta=-0.5, gamma=0.5,
                       granularity=granularity['middle'],
                       )

        experiment_end()
