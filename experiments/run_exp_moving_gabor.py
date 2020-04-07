from experiments.base_experiment_settings import *
from experiments.run_single_experiment import run_experiment

ch_dir()
ch_dir('moving_gabor')

for patch_update in patch_updates:
    for value_change in patch_updates[patch_update]:
        settings = {
            f'{patch_update}_speed': patch_updates[patch_update][value_change],
        }

        run_experiment(size=base_size,
                       length=length,
                       live=False,
                       output_diff=True,
                       exp_name=f'patch_{patch_update}_{value_change}',
                       output_values=['Luminance', 'Contrast', 'SSIM', 'diff'],
                       **settings)

        experiment_end()
