from generators.noise_generator import NoiseGenerator


class NoiseProcessor(NoiseGenerator):
    def __init__(self, generator: NoiseGenerator):
        self.noise_generator = generator
        super(NoiseProcessor, self).__init__(self.noise_generator.width, self.noise_generator.height)

    def __process__(self, dt=1) -> None:
        pass

    def __update__(self, dt=1) -> None:
        self.last_frame = self.noise_generator.get_next_frame(dt)

        self.__process__(dt)
