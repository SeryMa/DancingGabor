from base_experiment_settings import *

from generators.continuous_noise_generator import ContinuousNoiseGenerator
from generators.gabor_generator import GaborGenerator
from generators.patched_noise_generator import PatchedNoiseGenerator
from generators.pink_noise_generator import PinkNoise
from utils.image import luminance_comparison, contrast_comparison, structural_similarity, phase_invariant_similarity
from utils.simple_functions import construct_file_name


def main():
    ch_dir('1_simple_poc')

    for contrast_setting, contrast in contrast_settings.items():
        for position_setting, patch_position in position_settings.items():
            exp_name = f'{contrast_setting}_{position_setting}_patch'

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
                              f'Contrast: {contrast:.2f}\n',
                              f'Patch position: {patch_position}\n',
                              ])

            base_noise = ContinuousNoiseGenerator(base_size, base_size, PinkNoise(base_size, base_size),
                                                  period=base_period)

            patch_generator = GaborGenerator(patch_size_deg=patch_size_deg, ppd=ppd)
            noise_with_gabor = PatchedNoiseGenerator(base_size, base_size, base_noise,
                                                     [(patch_generator, lambda dt: patch_position)],
                                                     contrast=contrast)

            field_names = []
            output_generators = []

            field_names.extend([
                'compare_lum_gabor_noise_vs_gabor',
                'compare_lum_noise_vs_gabor',
                'compare_lum_gabor_noise_vs_noise'
            ])
            output_generators.extend([
                lambda: luminance_comparison(noise_with_gabor.get_next_frame(0),
                                             patch_generator.get_normalized_patch()),
                lambda: luminance_comparison(base_noise.get_next_frame(0),
                                             patch_generator.get_normalized_patch()),
                lambda: luminance_comparison(noise_with_gabor.get_next_frame(0),
                                             base_noise.get_next_frame(0)),
            ])

            field_names.extend([
                'compare_con_gabor_noise_vs_gabor',
                'compare_con_noise_vs_gabor',
                'compare_con_gabor_noise_vs_noise'
            ])
            output_generators.extend([
                lambda: contrast_comparison(noise_with_gabor.get_next_frame(0),
                                            patch_generator.get_normalized_patch()),
                lambda: contrast_comparison(base_noise.get_next_frame(0),
                                            patch_generator.get_normalized_patch()),
                lambda: contrast_comparison(noise_with_gabor.get_next_frame(0),
                                            base_noise.get_next_frame(0)),
            ])

            field_names.extend([
                'compare_str_gabor_noise_vs_gabor',
                'compare_str_noise_vs_gabor',
                'compare_str_gabor_noise_vs_noise'
            ])
            output_generators.extend([
                lambda: structural_similarity(noise_with_gabor.get_next_frame(0),
                                              patch_generator.get_normalized_patch()),
                lambda: structural_similarity(base_noise.get_next_frame(0),
                                              patch_generator.get_normalized_patch()),
                lambda: structural_similarity(noise_with_gabor.get_next_frame(0),
                                              base_noise.get_next_frame(0)),
            ])

            field_names.extend([
                'compare_cw_str_gabor_noise_vs_gabor',
                'compare_cw_str_noise_vs_gabor',
                'compare_cw_str_gabor_noise_vs_noise'
            ])
            output_generators.extend([
                lambda: phase_invariant_similarity(noise_with_gabor.get_next_frame(0),
                                                   patch_generator.get_normalized_patch()),
                lambda: phase_invariant_similarity(base_noise.get_next_frame(0),
                                                   patch_generator.get_normalized_patch()),
                lambda: phase_invariant_similarity(noise_with_gabor.get_next_frame(0),
                                                   base_noise.get_next_frame(0)),
            ])

            generate_experiment_output(output_name=output_name,
                                       generator=noise_with_gabor,
                                       fields=field_names,
                                       outputs=output_generators)


if __name__ == '__main__':
    main()
