"""
A script to allocate items to reach the desired distribution.
"""
import argparse
import logging
import os

from . import configure


# noinspection DuplicatedCode
def get_arguments(args=None) -> argparse.Namespace:
    """
    Get the command line arguments.
    """
    # noinspection PyTypeChecker
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--config', default='allocate.yaml', type=os.path.abspath, help='The config file to load')
    return parser.parse_args(args=args)


def main(config: str):
    """
    The main logic of the script.
    """
    logging.debug('config: %s', config)


if __name__ == '__main__':
    # noinspection PyBroadException
    try:
        configure.pandas()
        configure.logging()
        opts = get_arguments()
        main(**opts.__dict__)
    except Exception:
        logging.exception('caught unhandled exception!')
        exit(-1)
    exit(0)
