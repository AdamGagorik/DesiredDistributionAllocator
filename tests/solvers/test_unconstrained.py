"""
Unit tests for module.
"""
import pandas as pd
import logging

import allocate.solvers.bucketdata
import allocate.solvers.unconstrained

from pandas.testing import assert_series_equal


# noinspection DuplicatedCode
def test_solver_solve_simple():
    system = allocate.solvers.bucketdata.BucketSystem.create(
        amount_to_add=10, current_values=[0, 0], optimal_ratios=[0.5, 0.5])
    logging.debug('\n%s', system)

    solver = allocate.solvers.unconstrained.BucketSolverSimple.solve(system)
    logging.debug('\n%s', solver)

    totals = pd.Series(solver.result_total.values)
    assert_series_equal(totals, pd.Series([5.0, 5.0]))


# noinspection DuplicatedCode
def test_solver_solve_negative_values():
    system = allocate.solvers.bucketdata.BucketSystem.create(
        amount_to_add=10, current_values=[100, 0], optimal_ratios=[0.5, 0.5])
    logging.debug('\n%s', system)

    solver = allocate.solvers.unconstrained.BucketSolverSimple.solve(system)
    logging.debug('\n%s', solver)

    assert solver.result_delta.values[0] < 0
    assert solver.result_delta.values[1] > 0
