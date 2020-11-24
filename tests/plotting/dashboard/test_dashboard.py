"""
Unit tests for module.
"""
import unittest.mock

from allocate.plotting.dashboard.dashboard import Dashboard


def test_setup_called_on_create():
    with unittest.mock.patch.object(Dashboard, '__setup__') as m0:
        w0 = Dashboard()
        m0.assert_called_once()
