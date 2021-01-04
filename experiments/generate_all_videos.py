import experiments.run_exp_1_simple_poc
import experiments.run_exp_2_ssim_precision
import experiments.run_exp_3_changing_gabor_adv_detection
import experiments.run_exp_4_moving_gabor_adv_detection

from base_experiment_settings import ch_dir, results_folder

if __name__ == '__main__':
    ch_dir(results_folder)

    experiments.run_exp_1_simple_poc.main()
    experiments.run_exp_2_ssim_precision.main()
    experiments.run_exp_3_changing_gabor_adv_detection.main()
    experiments.run_exp_4_moving_gabor_adv_detection.main()
