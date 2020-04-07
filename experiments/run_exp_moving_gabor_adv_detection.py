from experiments.base_experiment_settings import *
from experiments.run_single_experiment import run_experiment

ch_dir()
ch_dir('moving_gabor_adv_detection')

for patch_update in patch_updates:
    for granularity in granularities:
        settings = {
            f'{patch_update}_speed': patch_updates[patch_update]['fast'],
        }

        run_experiment(size=base_size,
                       length=length,
                       live=False,
                       exp_name=f'patch_{patch_update}_granularity_{granularity}',
                       output_values=['full_ssim'],
                       granularity=granularities[granularity],
                       **settings)

        experiment_end()
