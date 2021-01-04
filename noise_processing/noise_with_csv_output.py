import csv

from generators.noise_generator import NoiseGenerator
from noise_processing.noise_processor import NoiseProcessor
from utils.simple_functions import construct_file_name


class NoiseGeneratorWithCSVOutput(NoiseProcessor):
    def __init__(self, generator: NoiseGenerator, file_name=None, delimiter=';', output_generators=None,
                 field_names=None):
        super(NoiseGeneratorWithCSVOutput, self).__init__(generator)

        self.output_values = output_generators or []

        # It's required to add empty newline to not add empty lines between rows
        # see: https://docs.python.org/3/library/csv.html#id3
        self.output_file = open(file_name or construct_file_name(file_name, extension='csv'), mode='w', newline='')

        self.output_file_writer = csv.writer(self.output_file,
                                             delimiter=delimiter,
                                             # We do not expect to write down many strings
                                             # so there is no need to escape anything
                                             # but using this trick we can record
                                             # several values from one output function
                                             escapechar=' ', quoting=csv.QUOTE_NONE)

        self.output_file_writer.writerow(['time'] + field_names or [])

        self.time = 0

    def __process__(self, dt=1) -> None:
        self.time += dt
        self.output_file_writer.writerow([self.time] + [fun() for fun in self.output_values])

    def __del__(self):
        self.output_file.close()
