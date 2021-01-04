from enum import Enum

from numpy import fft, real, imag, sqrt

from generators.continuous_noise_generator import ContinuousNoiseGenerator
from generators.pink_noise_generator import PinkNoise
from generators.proper_pink_noise_generator import PinkNoise as PinkNoise2
from generators.running_pink_noise_generator import RunningPinkNoise
from generators.white_noise_generator import WhiteNoise
from utils.array import get_normalized
from utils.base_experiment_settings import *


class Noises(Enum):
    Inter = 'interpolated'
    Pink = 'pink'
    Run = 'running'
    White = 'white'


if __name__ == '__main__':
    # parser = argparse.ArgumentParser()
    # parser.add_argument("--noise", default=Noises.Inter.value, type=str)
    # noise_type = parser.parse_args().noise

    ch_dir('spectra')
    # for noise_type in [Noises.Run.value]:
    for noise_type in (noise.value for noise in Noises):
        if noise_type == Noises.Inter.value:
            noise = ContinuousNoiseGenerator(base_size, base_size, PinkNoise(base_size, base_size), period=base_period)
        elif noise_type == Noises.Pink.value:
            # Beware! PinkNoise2 is fixed in time length so running it for for longer than 5 s will crash the app
            noise = PinkNoise2(base_size, base_size, length=length)
        elif noise_type == Noises.Run.value:
            noise = RunningPinkNoise(base_size, base_size, base_period * 5)
        elif noise_type == Noises.White.value:
            noise = ContinuousNoiseGenerator(base_size, base_size, WhiteNoise(base_size, base_size), period=base_period)
        else:
            raise ValueError(f'{noise_type} is not a recognized noise type')


        def get_spectra(dt):
            frame = noise.get_next_frame(dt) - .5
            # frame = (np.ones((base_size, base_size))-0.5)

            f_frame = fft.fftshift(fft.fft2(frame))
            spectra = sqrt(real(f_frame) ** 2 + imag(f_frame) ** 2)
            # spectra = real(f_frame)
            # spectra = imag(f_frame)
            out = get_normalized(spectra)
            return out


        # output = PygletOutput(get_spectra, base_size, base_size)
        # output = PygletOutput(noise.get_next_frame, base_size, base_size)

        output = VideoOutput(noise.get_next_frame, base_size, base_size, length=length,
                             video_name=f'simple_{noise_type}.avi',
                             secondary_outputs=[('spectra', get_spectra)])
        output.run()
