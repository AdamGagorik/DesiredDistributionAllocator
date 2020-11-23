"""
Methods for loading input into a DataFrame.
"""
import pandas as pd
import logging
import typing
import yaml
import os
import re

import allocate.network.attributes


def load(path: str) -> pd.DataFrame:
    """
    Load the configuration.
    """
    ext = os.path.splitext(path)[-1].lower()
    if ext in ['.yaml', '.yml']:
        return load_yml(path)
    elif ext in ['.csv']:
        return load_csv(path)
    else:
        raise ValueError(f'unknown input extension! {ext}')


def load_yml(path: str) -> pd.DataFrame:
    """
    Load the configuration from YAML.
    """
    with open(path, 'r') as stream:
        data: list = yaml.load(stream, yaml.SafeLoader)
        return _reformat_input(data)


def load_csv(path: str) -> pd.DataFrame:
    """
    Load the configuration.
    """
    with open(path, 'r') as stream:
        data: pd.DataFrame = pd.read_csv(stream)
        return _reformat_input(data)


def _reformat_input(data: typing.Union[list, pd.DataFrame]) -> pd.DataFrame:
    """
    Transform the input so that it is a DataFrame with the correct data types.
    """
    if isinstance(data, list):
        data: pd.DataFrame = pd.DataFrame(data)

    valid = True
    for col in data.columns:
        if col not in ['children'] and col not in allocate.network.attributes.node_attrs.columns(input_only=True):
            logging.error('unknown column in input! %s', col)
            valid = False

    if not valid:
        raise ValueError('unknown column in input!')

    data['children'] = data['children'].apply(_tokenize_children)
    # noinspection PyTypeChecker
    data['children'] = data.apply(_expand_regex_patterns, frame=data, axis=1)
    data = data.astype(allocate.network.attributes.node_attrs.dtypes(input_only=True))

    return data


def _expand_regex_patterns(row: pd.Series, frame: pd.DataFrame) -> typing.Tuple[str]:
    """
    Look for regular expressions in child node lists and expand them.
    """
    def it() -> typing.Generator[str, None, None]:
        excluded = [
            row[allocate.network.attributes.node_attrs.label.column]
        ]
        values = row['children']
        for value in values:
            if value.startswith('regex::'):
                pattern = re.compile(value[len('regex::'):])
                for node in frame[allocate.network.attributes.node_attrs.label.column]:
                    if node not in excluded and pattern.match(node):
                        yield node
            else:
                yield value
    return tuple(it())


def _tokenize_children(value: typing.Union[str, tuple]) -> tuple:
    """
    Turn the string A;B;C into the list [A, B, C] instead.
    """
    if isinstance(value, list):
        return tuple(value)

    if isinstance(value, tuple):
        return value

    if value is None or pd.isna(value):
        return ()

    value = value.strip()
    if value:
        return tuple(t.strip() for t in value.split(';'))
    else:
        return ()
