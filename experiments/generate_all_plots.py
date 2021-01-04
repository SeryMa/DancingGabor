from base_experiment_settings import ch_dir, results_folder
from experiments.generate_plots_for_experiment import generate_graphs

if __name__ == '__main__':
    ch_dir(results_folder)
    generate_graphs(folder='1_simple_poc',
                    output_values=['Luminance', 'Contrast', 'Structure', 'CW_Structure'],
                    live=False)

    generate_graphs(folder='2_ssim_precision',
                    output_values=['ssim', 'cw_ssim'],
                    live=False)

    generate_graphs(folder='3_changing_gabor_adv_detection',
                    output_values=['ssim', 'pattern_search_ssim', 'cw_ssim', 'pattern_search_cw_ssim'],
                    live=False)

    generate_graphs(folder='4_moving_gabor_adv_detection',
                    output_values=['ssim', 'pattern_search_ssim', 'cw_ssim', 'pattern_search_cw_ssim'],
                    live=False)
