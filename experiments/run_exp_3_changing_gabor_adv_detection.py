from experiments.base_experiment_settings import *
from experiments.run_single_experiment import run_experiment

ch_dir()
ch_dir('3_changing_gabor_adv_detection')

for patch_update in patch_updates:
    for gran in granularity:
        settings = {
            f'{patch_update}_speed': patch_updates[patch_update]['middle'],
        }

        run_experiment(size=base_size,
                       length=length,
                       live=False,
                       exp_name=f'patch_{patch_update}_granularity_{gran}',
                       output_values=['pattern_search_ssim', 'ssim', 'pattern_search_cw_ssim', 'cw_ssim'],
                       alpha=0, beta=-0.5, gamma=0.5,
                       granularity=granularity[gran],
                       **settings)

        experiment_end()
