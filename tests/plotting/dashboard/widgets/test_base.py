"""
Unit tests for module.
"""
import unittest.mock
import panel as pn

from allocate.plotting.dashboard.widgets.base import Widget


def test_empty_view_on_create():
    w0 = Widget()
    assert not w0.view


def test_setup_called_on_create():
    with unittest.mock.patch.object(Widget, '__setup__') as m0:
        w0 = Widget()
        m0.assert_called_once()


def test_layout_created_and_cached():
    w0 = Widget()
    assert not w0.view
    layout = w0.layout
    assert id(next(iter(w0.view.values()))) == id(layout)
    assert id(next(iter(w0.view.values()))) == id(layout)


def test_connect_calls_children():
    w0 = Widget(parent=None)
    w1 = Widget(parent=w0)
    w2 = Widget(parent=w1)
    w3 = Widget(parent=w1)
    with unittest.mock.patch.object(w0, '__connect__') as m0:
        with unittest.mock.patch.object(w1, '__connect__') as m1:
            with unittest.mock.patch.object(w2, '__connect__') as m2:
                with unittest.mock.patch.object(w3, '__connect__') as m3:
                    w0.connect()
                    m0.assert_called_once()
                    m1.assert_called_once()
                    m2.assert_called_once()
                    m3.assert_called_once()


def test_serve_calls_layout_method():
    with unittest.mock.patch.object(pn, 'serve') as m0:
        w0 = Widget()
        w0.serve()
        m0.assert_called_once_with(w0.layout)
