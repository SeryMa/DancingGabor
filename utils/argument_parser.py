import argparse
import json
from os import sep as separator
from sys import argv

from utils.input_parser import get_noise
from utils.simple_functions import nested_clear_override, nested_update, nested_replace


def get_command_line_args() -> dict:
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--noise", default="pink", type=str, help="Noise color")
    parser.add_argument("--deg", default=4, type=int, help="Degress used for pink noise generation")
    parser.add_argument("--width", default=500, type=int, help="Width")
    parser.add_argument("--height", default=500, type=int, help="Height")
    parser.add_argument("--time_span", default=1, type=int, help="Time [ms] between separate noise generations")

    # This one should be in production set to False. True is for debugging.
    parser.add_argument("--live", default=True, type=bool,
                        help="Should the live preview be played instead of creating video file")

    # Video specific
    parser.add_argument("--FPS", default=60, type=int, help="Frames per second")
    parser.add_argument("--len", default=10, type=int, help="Video length")

    return vars(parser.parse_args())


NOISES = [
    'white',
    'pink',
    'single',

    'continuous',
    'patched',
    'circular',

    'plaid',
    'gabor',

    'diff',
    'heat',
    'process'
]


def get_json_config_args() -> (dict, dict):
    data = {
        'continuous': {'pink': {}}
    }

    output_data = {
        'live': True,
        'width': 50,
        'height': 50,
        'file_name': ''
    }

    # TODO: Check which approach is more UX friendly. Either the later argument overrides former
    #       or the other way around (former overrides later)
    # for file in argv[:0:-1]:
    for file in argv[1:]:
        with open(file) as config_file:
            new_dict = json.load(config_file)  # type: dict

            if 'output' in new_dict:
                new_dict_output = new_dict['output']
                new_dict.pop('output')

                nested_update(output_data, new_dict_output)

            if not nested_replace(data, new_dict, 'noise'):
                # TODO: this one might be unnecessarily complicated after separating `output` to different dictionary
                nested_clear_override(data, new_dict, NOISES)
                nested_update(data, new_dict)

            stripped = file[:file.rfind('.')]
            stripped = stripped[stripped.rfind(separator) + len(separator):]

            output_data["file_name"] = stripped

    return output_data, data


def prepare_app(args_source='json'):
    if 'json' in args_source:
        output_args, args = get_json_config_args()
    elif 'command' in args_source:
        args = get_command_line_args()
        output_args = args['output']
        args.pop('output')
    else:
        raise ValueError(
            f"Invalid value '{args_source}' for 'args_source' variable. Try 'json' or 'command line' instead.")

    noise_generator, _ = get_noise(output_args['width'], output_args['height'], **args)

    if not noise_generator:
        raise ValueError(f"Any noise type wasn't recognized.")

    return noise_generator, output_args
