from base_experiment_settings import *

from generators.continuous_noise_generator import ContinuousNoiseGenerator
from generators.gabor_generator import GaborGenerator
from generators.patched_noise_generator import PatchedNoiseGenerator
from generators.pink_noise_generator import PinkNoise
from utils.image import cw_ssim, ssim
from utils.patch_compare import PatchComparator
from utils.simple_functions import construct_file_name


def main():
    ch_dir('3_changing_gabor_adv_detection')

    for update_type, update_options in patch_updates.items():
        for granularity, granularity_value in granularities.items():
            update_speed = update_options['middle']
            exp_name = f'patch_{update_type}_granularity_{granularity}'

            output_name = construct_file_name(exp_name)
            with open(output_name + '.log', 'w') as f:
                f.writelines([f'Log file for experiment {output_name}\n',
                              'The experiment presents one big gabor patch in pink noise scene.\n'
                              f'New pink noise is generated every {base_period:.2f} s\n',

                              f'\nExperiment settings:\n',
                              f'Scene dimensions: {base_size}\n',
                              f'Length [s]: {length}\n',
                              f'FPS: {fps}\n',
                              f'PPD: {ppd}\n',
                              f'Contrast: {base_contrast:.2f}\n',
                              f'{update_type} update [s^-1]: {update_speed}\n',
                              ])

            base_noise = ContinuousNoiseGenerator(base_size, base_size, PinkNoise(base_size, base_size),
                                                  period=base_period)

            patch_generator = GaborGenerator(patch_size_deg=patch_size_deg, ppd=ppd,
                                             update_list=get_patch_value_updates(update_type, update_speed,
                                                                                 initial_value=6
                                                                                 if update_type == 'freq'
                                                                                 else 0))
            noise_with_gabor = PatchedNoiseGenerator(base_size, base_size, base_noise,
                                                     [(patch_generator, lambda dt: base_position)],
                                                     contrast=base_contrast)

            field_names = []
            output_generators = []

            field_names.extend([
                'ssim_gabor_noise_vs_gabor',
                'ssim_noise_vs_gabor',
                'ssim_gabor_noise_vs_noise'
            ])
            output_generators.extend([
                lambda: ssim(noise_with_gabor.get_next_frame(0),
                             patch_generator.get_normalized_patch(),
                             alpha, beta, gamma),
                lambda: ssim(base_noise.get_next_frame(0),
                             patch_generator.get_normalized_patch(),
                             alpha, beta, gamma),
                lambda: ssim(noise_with_gabor.get_next_frame(0),
                             base_noise.get_next_frame(0),
                             alpha, beta, gamma),
            ])

            field_names.extend([
                'simple_ssim_gabor_noise_vs_patch_search',
                'simple_ssim_noise_vs_patch_search',
                'simple_ssim_gabor_noise_vs_noise',
            ])
            simple_patch_comparator = PatchComparator(patch_size_deg, ppd, granularity=granularity_value,
                                                      alpha=alpha, beta=beta, gamma=gamma)
            output_generators.extend([
                lambda: simple_patch_comparator.get_best_ssim_match(noise_with_gabor.get_next_frame(0)),
                lambda: simple_patch_comparator.get_best_ssim_match(base_noise.get_next_frame(0)),
                lambda: ssim(noise_with_gabor.get_next_frame(0),
                             base_noise.get_next_frame(0),
                             alpha, beta, gamma)
            ])

            field_names.extend([
                'cw_ssim_gabor_noise_vs_gabor',
                'cw_ssim_noise_vs_gabor',
                'cw_ssim_gabor_noise_vs_noise'
            ])
            output_generators.extend([
                lambda: cw_ssim(noise_with_gabor.get_next_frame(0),
                                patch_generator.get_normalized_patch(),
                                alpha, beta, gamma),
                lambda: cw_ssim(base_noise.get_next_frame(0),
                                patch_generator.get_normalized_patch(),
                                alpha, beta, gamma),
                lambda: cw_ssim(noise_with_gabor.get_next_frame(0),
                                base_noise.get_next_frame(0),
                                alpha, beta, gamma),
            ])

            field_names.extend([
                'cw_ssim_gabor_noise_vs_patch_search',
                'cw_ssim_noise_vs_patch_search',
                'cw_ssim_gabor_noise_vs_noise',
            ])
            complex_patch_comparator = PatchComparator(patch_size_deg, ppd, granularity=granularity_value,
                                                       alpha=alpha, beta=beta, gamma=gamma, simple=False)
            output_generators.extend([
                lambda: complex_patch_comparator.get_best_ssim_match(noise_with_gabor.get_next_frame(0)),
                lambda: complex_patch_comparator.get_best_ssim_match(base_noise.get_next_frame(0)),
                lambda: cw_ssim(noise_with_gabor.get_next_frame(0),
                                base_noise.get_next_frame(0),
                                alpha, beta, gamma),
            ])

            generate_experiment_output(output_name=output_name,
                                       generator=noise_with_gabor,
                                       fields=field_names,
                                       outputs=output_generators)


if __name__ == '__main__':
    main()
