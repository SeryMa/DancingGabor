import csv

from generators.noise_generator import NoiseGenerator
from noise_processing.noise_processor import NoiseProcessor


class NoiseGeneratorWithCSVOutput(NoiseProcessor):
    def __init__(self, generator: NoiseGenerator, file="output.csv", delimiter=';', output_values=None, **kwargs):
        super(NoiseGeneratorWithCSVOutput, self).__init__(generator)

        self.output_values = output_values or []

        self.output_file = open(file, mode='w')
        self.output_file_writer = csv.writer(self.output_file, delimiter=delimiter)

        self.time = 0

    def __process__(self, dt=1) -> None:
        self.time += dt
        self.output_file_writer.writerow([self.time] + [fun() for fun in self.output_values])

    def __del__(self):
        self.output_file.close()
