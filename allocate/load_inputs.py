"""
Methods for loading input into a DataFrame.
"""
import pandas as pd
import logging
import typing
import yaml
import os

from .network.attributes import node_attrs


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
        if col not in ['children'] and col not in node_attrs.columns():
            logging.error('unknown column in input! %s', col)
            valid = False

    if not valid:
        raise ValueError('unknown column in input!')

    data['children'] = data['children'].apply(_tokenize_children)
    data = data.astype(node_attrs.dtypes(input_only=True))

    return data


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
