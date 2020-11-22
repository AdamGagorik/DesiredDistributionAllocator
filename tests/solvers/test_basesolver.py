"""
Unit tests for module.
"""
import pytest

import allocate.solvers.bucketdata
import allocate.solvers.basesolver


def test_base_not_implemented():
    with pytest.raises(NotImplementedError):
        system = allocate.solvers.bucketdata.BucketSystem.create(1, [1, 1], [1, 1])
        allocate.solvers.basesolver.BucketSolver.solve(system)
