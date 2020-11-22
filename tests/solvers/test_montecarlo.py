"""
Unit tests for module.
"""
import pandas as pd
import numpy as np
import logging

import allocate.solvers.bucketdata
import allocate.solvers.montecarlo

from pandas.testing import assert_series_equal


# noinspection DuplicatedCode
def test_solver_solve_simple():
    system = allocate.solvers.bucketdata.BucketSystem.create(
        amount_to_add=10, current_values=[0, 0], optimal_ratios=[0.5, 0.5])
    logging.debug('\n%s', system)

    solver = allocate.solvers.montecarlo.BucketSolverConstrainedMonteCarlo.solve(system, step_size=1, max_steps=100)
    logging.debug('\n%s', solver)

    totals = pd.Series(solver.result_total.values)
    assert_series_equal(totals, pd.Series([5.0, 5.0]))


# noinspection DuplicatedCode
def test_solver_solve_all_positive():
    system = allocate.solvers.bucketdata.BucketSystem.create(
        amount_to_add=10, current_values=[10, 90], optimal_ratios=[0.5, 0.5])
    logging.debug('\n%s', system)

    solver = allocate.solvers.montecarlo.BucketSolverConstrainedMonteCarlo.solve(system, step_size=1, max_steps=100)
    logging.debug('\n%s', solver)

    assert np.all(solver.result_delta.values >= 0)
