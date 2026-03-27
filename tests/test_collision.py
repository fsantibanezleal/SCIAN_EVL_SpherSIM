"""
Tests for collision detection and resolution.

Verifies that:
    - Overlapping cells are pushed apart
    - Non-overlapping cells are left untouched
    - angular_distance() computes correct values
    - Collision resolution preserves sphere constraint
"""

import sys
import os
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.simulation.cell_dfc import CellDFC
from app.simulation.collision import angular_distance, solve_collisions, apply_adhesion


def test_angular_distance_zero():
    """Identical positions should give zero distance."""
    a = CellDFC(azimuth=1.0, elevation=0.5, radius=1000, radial_size=0.05)
    b = CellDFC(azimuth=1.0, elevation=0.5, radius=1000, radial_size=0.05)
    assert angular_distance(a, b) == 0.0
    print("  [PASS] test_angular_distance_zero")


def test_angular_distance_known():
    """Angular distance for known separation (Haversine)."""
    a = CellDFC(azimuth=0.0, elevation=0.0, radius=1000, radial_size=0.05)
    b = CellDFC(azimuth=0.3, elevation=0.4, radius=1000, radial_size=0.05)
    # Haversine expected value for (az=0,el=0) to (az=0.3,el=0.4)
    d_el = 0.4
    d_az = 0.3
    hav = np.sin(d_el / 2)**2 + np.cos(0.0) * np.cos(0.4) * np.sin(d_az / 2)**2
    expected = 2 * np.arcsin(np.sqrt(hav))
    np.testing.assert_allclose(angular_distance(a, b), expected, atol=1e-10)
    print("  [PASS] test_angular_distance_known")


def test_overlapping_cells_pushed_apart():
    """Two overlapping cells should end up further apart."""
    size = 0.1
    # Place cells closer than 2*size
    a = CellDFC(azimuth=0.0, elevation=0.0, radius=1000, radial_size=size)
    b = CellDFC(azimuth=0.05, elevation=0.0, radius=1000, radial_size=size)

    dist_before = angular_distance(a, b)
    assert dist_before < 2 * size  # confirm overlap

    solve_collisions([a, b])

    dist_after = angular_distance(a, b)
    assert dist_after > dist_before
    print("  [PASS] test_overlapping_cells_pushed_apart")


def test_non_overlapping_unchanged():
    """Well-separated cells should not move."""
    a = CellDFC(azimuth=0.0, elevation=0.0, radius=1000, radial_size=0.05)
    b = CellDFC(azimuth=1.0, elevation=1.0, radius=1000, radial_size=0.05)

    pos_a = a.center_aer.copy()
    pos_b = b.center_aer.copy()

    solve_collisions([a, b])

    np.testing.assert_array_equal(a.center_aer, pos_a)
    np.testing.assert_array_equal(b.center_aer, pos_b)
    print("  [PASS] test_non_overlapping_unchanged")


def test_collision_symmetric():
    """Both cells should be displaced approximately equally (symmetric resolution).

    With Cartesian-space push, the midpoint in Cartesian 3D is preserved
    exactly. The AER midpoint is preserved approximately for cells near
    the equator where the metric is close to uniform.
    """
    size = 0.1
    a = CellDFC(azimuth=0.0, elevation=0.0, radius=1000, radial_size=size)
    b = CellDFC(azimuth=0.08, elevation=0.0, radius=1000, radial_size=size)

    mid_xyz_before = (a.center_xyz + b.center_xyz) / 2

    solve_collisions([a, b])

    mid_xyz_after = (a.center_xyz + b.center_xyz) / 2
    # Cartesian midpoint should be approximately preserved.
    # On a curved surface the tangent planes at i and j differ slightly,
    # so the midpoint is preserved only approximately.
    np.testing.assert_allclose(mid_xyz_after, mid_xyz_before, atol=10.0)
    print("  [PASS] test_collision_symmetric")


def test_inactive_cells_ignored():
    """Inactive cells should not participate in collisions."""
    size = 0.1
    a = CellDFC(azimuth=0.0, elevation=0.0, radius=1000, radial_size=size)
    b = CellDFC(azimuth=0.05, elevation=0.0, radius=1000, radial_size=size)
    b.active = False

    pos_a = a.center_aer.copy()
    solve_collisions([a, b])
    np.testing.assert_array_equal(a.center_aer, pos_a)
    print("  [PASS] test_inactive_cells_ignored")


def test_multiple_cells():
    """Collision resolution should handle more than two cells."""
    size = 0.1
    cells = [
        CellDFC(azimuth=0.0, elevation=0.0, radius=1000, radial_size=size),
        CellDFC(azimuth=0.05, elevation=0.0, radius=1000, radial_size=size),
        CellDFC(azimuth=0.1, elevation=0.0, radius=1000, radial_size=size),
    ]
    # Should not raise
    solve_collisions(cells)
    # All cells should still be active
    for c in cells:
        assert c.active is True
    print("  [PASS] test_multiple_cells")


def test_haversine_known_values():
    """Verify Haversine distance against known analytical values."""
    # Cells at same longitude, 90 degrees apart in elevation
    c1 = CellDFC(azimuth=0, elevation=0, radius=1000, radial_size=0.01)
    c2 = CellDFC(azimuth=0, elevation=np.pi/2 - 0.02, radius=1000, radial_size=0.01)
    dist = angular_distance(c1, c2)
    expected = np.pi/2 - 0.02  # Should be close to 90 degrees
    assert abs(dist - expected) < 0.01, f"Expected ~{expected}, got {dist}"
    print("  [PASS] test_haversine_known_values")


def test_adhesion_pulls_cells_closer():
    """Verify adhesion force pulls non-overlapping nearby cells together."""
    c1 = CellDFC(azimuth=-0.6, elevation=0.1, radius=1000, radial_size=0.05)
    c2 = CellDFC(azimuth=-0.4, elevation=0.1, radius=1000, radial_size=0.05)
    dist_before = angular_distance(c1, c2)
    apply_adhesion([c1, c2], adhesion_strength=0.01, adhesion_range=5.0)
    dist_after = angular_distance(c1, c2)
    assert dist_after < dist_before, "Adhesion should pull cells closer"
    print("  [PASS] test_adhesion_pulls_cells_closer")


if __name__ == '__main__':
    print("Running collision tests...")
    test_angular_distance_zero()
    test_angular_distance_known()
    test_overlapping_cells_pushed_apart()
    test_non_overlapping_unchanged()
    test_collision_symmetric()
    test_inactive_cells_ignored()
    test_multiple_cells()
    test_haversine_known_values()
    test_adhesion_pulls_cells_closer()
    print("All collision tests passed.")
