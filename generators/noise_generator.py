class NoiseGenerator:
    def __init__(self, width, height, **kwargs):
        self.width = width
        self.height = height

        self.should_run = True

    def get_next_frame(self, dt=1):
        pass

    def __del__(self):
        self.should_run = False

    def stop(self):
        self.should_run = False

    def __iter__(self):
        while self.should_run:
            yield self.get_next_frame()


class StaticNoiseGenerator:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def get_next_frame(self):
        pass
