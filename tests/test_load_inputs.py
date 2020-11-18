"""
Unit tests for io module.
"""
import unittest.mock
import pandas as pd
import textwrap
import builtins
import pytest
import io

from pandas.testing import assert_frame_equal
from _pytest.monkeypatch import MonkeyPatch

import allocate.load_inputs


def make_input_stream_mock_function(contents: str):
    """
    Create a mock method to replace the open builtin function.
    """
    stream = io.StringIO(textwrap.dedent(contents))

    # noinspection PyUnusedLocal
    def mock(*args, **kwargs):
        stream.seek(0)
        return stream

    return mock


@pytest.fixture()
def input_yml_stream():
    """
    Example input for YAML.
    """
    yield make_input_stream_mock_function(r"""
        - { name: 0, desired: 100, current: 5500, distribute: 4000, children: A;B;C }
        - { name: A, desired:  45, current: 1000, distribute:    0, children: [] }
        - { name: B, desired:  20, current: 1500, distribute:    0, children: [] }
        - { name: C, desired:  35, current: 3000, distribute:    0, children: [] }
    """)


@pytest.fixture()
def input_csv_stream():
    """
    Example input for CSV.
    """
    yield make_input_stream_mock_function(r"""
        name,desired,current,distribute,children
        0,100,5500,4000,A;B;C
        A,45,1000,0,
        B,20,1500,0,
        C,35,3000,0,
    """)


@pytest.fixture()
def expected_load_results():
    """
    Expected result for examples.
    """
    yield pd.DataFrame([
        dict(name='0', desired=100, current=5500, distribute=4000, children=('A', 'B', 'C')),
        dict(name='A', desired=45, current=1000, distribute=0, children=()),
        dict(name='B', desired=20, current=1500, distribute=0, children=()),
        dict(name='C', desired=35, current=3000, distribute=0, children=()),
    ])


def test_load():
    with unittest.mock.patch.object(allocate.load_inputs, 'load_yml') as mock_load_yml:
        with unittest.mock.patch.object(allocate.load_inputs, 'load_csv') as mock_load_csv:
            allocate.load_inputs.load('input.yaml')
            mock_load_yml.assert_called_once()
            mock_load_csv.assert_not_called()

    with unittest.mock.patch.object(allocate.load_inputs, 'load_yml') as mock_load_yml:
        with unittest.mock.patch.object(allocate.load_inputs, 'load_csv') as mock_load_csv:
            allocate.load_inputs.load('input.csv')
            mock_load_csv.assert_called_once()
            mock_load_yml.assert_not_called()

    with pytest.raises(ValueError, match='unknown .* extension!'):
        allocate.load_inputs.load('input.jpeg')


def test_load_yml(monkeypatch: MonkeyPatch, input_yml_stream, expected_load_results):
    with monkeypatch.context() as m:
        m.setattr(builtins, 'open', input_yml_stream)
        observed_load_results = allocate.load_inputs.load_yml('input.yaml')
        assert_frame_equal(observed_load_results, expected_load_results)


def test_load_csv(monkeypatch: MonkeyPatch, input_csv_stream, expected_load_results):
    with monkeypatch.context() as m:
        m.setattr(builtins, 'open', input_csv_stream)
        observed_load_results = allocate.load_inputs.load_csv('input.csv')
        assert_frame_equal(observed_load_results, expected_load_results)
