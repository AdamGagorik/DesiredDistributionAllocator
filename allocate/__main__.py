"""
A script to allocate items to reach the desired distribution.
"""
import networkx as nx
import pandas as pd
import argparse
import logging
import os

import allocate.configure
import allocate.load_inputs
import allocate.network.visualize
import allocate.network.algorithms


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
    frame: pd.DataFrame = allocate.load_inputs.load(path=config)
    logging.debug('frame:\n%s\n', frame)
    graph: nx.DiGraph = allocate.network.algorithms.create(frame)
    logging.debug('graph:\n%s', allocate.network.visualize.text(graph, **allocate.network.visualize.formats))


if __name__ == '__main__':
    # noinspection PyBroadException
    try:
        allocate.configure.pandas()
        allocate.configure.logging()
        opts = get_arguments()
        main(**opts.__dict__)
    except Exception:
        logging.exception('caught unhandled exception!')
        exit(-1)
    exit(0)
