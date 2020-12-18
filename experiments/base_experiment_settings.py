import winsound
from os import makedirs, chdir
from os.path import exists


def ch_dir(folder='results'):
    exists(folder) or makedirs(folder, exist_ok=True)
    chdir(folder)


def experiment_end():
    winsound.Beep(370, 500)
    winsound.Beep(370, 500)


base_size = 200
length = 10

contrast_settings = {'middle': 0.5, 'low': 0.2, 'high': 0.8}
position_settings = {'full': (0, 0), 'top_half': (base_size // 2, 0), 'right_half': (0, base_size // 2),
                     'quarter': (base_size // 2, base_size // 2)}

phase_settings = {'fast': 1, "middle": 0.1, "slow": 0.01, 'none': None}
theta_settings = {'fast': 10, "middle": 5, "slow": 1, 'none': None}
freq_settings = {'fast': 2, 'middle': 1, 'slow': .5, 'none': None}

patch_updates = {
    'phase': phase_settings,
    'theta': theta_settings,
    'freq': freq_settings,
}

granularity = {'high': 100, 'middle': 50, 'low': 10}

position_updates = {'fast': base_size // (2 * 20 / 2), 'middle': base_size // (2 * 20), 'slow': base_size // (2 * 40),
                    'none': 0}
