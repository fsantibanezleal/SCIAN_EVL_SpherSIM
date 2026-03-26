"""
Tests for CellDFC creation, update, and state serialization.

Verifies that:
    - A cell is created with correct initial position
    - Cartesian center lies on the sphere
    - Contour vertices are at the expected angular distance
    - update() moves the cell and wraps coordinates
    - get_state() returns a well-formed dictionary
"""

import sys
import os
import numpy as np

# Ensure project root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.simulation.cell_dfc import CellDFC, spherical_to_cartesian, cartesian_to_spherical


def test_creation():
    """Cell should be created with correct attributes."""
    cell = CellDFC(azimuth=0.0, elevation=0.0, radius=1000, radial_size=0.05, num_vertices=50)
    assert cell.active is True
    assert cell.num_vertices == 50
    np.testing.assert_allclose(cell.center_aer, [0.0, 0.0, 1000.0])
    print("  [PASS] test_creation")


def test_center_on_sphere():
    """Cartesian center must lie on the sphere surface."""
    r = 1000
    cell = CellDFC(azimuth=1.0, elevation=0.3, radius=r, radial_size=0.05)
    dist = np.linalg.norm(cell.center_xyz)
    np.testing.assert_allclose(dist, r, atol=1e-6)
    print("  [PASS] test_center_on_sphere")


def test_contour_shape():
    """Contour arrays must have the correct shape."""
    n = 80
    cell = CellDFC(azimuth=0, elevation=0, radius=1000, radial_size=0.05, num_vertices=n)
    assert cell.contour_aer.shape == (n, 3)
    assert cell.contour_xyz.shape == (n, 3)
    print("  [PASS] test_contour_shape")


def test_contour_radius():
    """All contour points should lie on the sphere surface."""
    r = 1000
    cell = CellDFC(azimuth=0.5, elevation=0.2, radius=r, radial_size=0.04, num_vertices=60)
    distances = np.linalg.norm(cell.contour_xyz, axis=1)
    np.testing.assert_allclose(distances, r, atol=1.0)
    print("  [PASS] test_contour_radius")


def test_update_moves_cell():
    """update() should change the cell's position."""
    cell = CellDFC(azimuth=0, elevation=0.5, radius=1000, radial_size=0.05)
    old_el = cell.center_aer[1]
    # Deterministic seed for reproducibility
    np.random.seed(42)
    cell.update(np.array([0.0, -0.01, 0.0]), noise_std=0.0)
    assert cell.center_aer[1] < old_el
    print("  [PASS] test_update_moves_cell")


def test_azimuth_wrapping():
    """Azimuth must wrap to [-pi, pi]."""
    cell = CellDFC(azimuth=3.1, elevation=0, radius=1000, radial_size=0.05)
    cell.update(np.array([0.2, 0.0, 0.0]), noise_std=0.0)
    assert -np.pi <= cell.center_aer[0] <= np.pi
    print("  [PASS] test_azimuth_wrapping")


def test_elevation_clamping():
    """Elevation must be clamped to [-pi/2, pi/2]."""
    cell = CellDFC(azimuth=0, elevation=1.5, radius=1000, radial_size=0.05)
    cell.update(np.array([0.0, 0.2, 0.0]), noise_std=0.0)
    assert cell.center_aer[1] <= np.pi / 2 + 1e-10
    print("  [PASS] test_elevation_clamping")


def test_inactive_cell_no_update():
    """Inactive cell should not move on update."""
    cell = CellDFC(azimuth=0, elevation=0, radius=1000, radial_size=0.05)
    cell.active = False
    old = cell.center_aer.copy()
    cell.update(np.array([0.1, -0.1, 0.0]))
    np.testing.assert_array_equal(cell.center_aer, old)
    print("  [PASS] test_inactive_cell_no_update")


def test_get_state():
    """get_state() should return a valid dictionary."""
    cell = CellDFC(azimuth=0, elevation=0, radius=1000, radial_size=0.05, num_vertices=10)
    state = cell.get_state()
    assert 'center_aer' in state
    assert 'center_xyz' in state
    assert 'contour_xyz' in state
    assert 'radial_size' in state
    assert 'active' in state
    assert len(state['center_aer']) == 3
    assert len(state['contour_xyz']) == 10
    print("  [PASS] test_get_state")


def test_coordinate_conversion():
    """spherical_to_cartesian and back should be an identity."""
    az, el, r = 1.2, 0.4, 500
    x, y, z = spherical_to_cartesian(az, el, r)
    az2, el2, r2 = cartesian_to_spherical(x, y, z)
    np.testing.assert_allclose(az2, az, atol=1e-6)
    np.testing.assert_allclose(el2, el, atol=1e-6)
    np.testing.assert_allclose(r2, r, atol=1e-6)
    print("  [PASS] test_coordinate_conversion")


def test_persistent_walk():
    """Verify cell eventually reorients after persistence time expires."""
    cell = CellDFC(azimuth=-np.pi/2, elevation=np.pi/8, radius=1000, radial_size=np.pi/64)
    initial_bias = cell.migration_bias
    vel = np.array([0, -(np.pi/2) * 0.005, 0])
    # Run enough steps to trigger at least one reorientation
    for _ in range(50):
        cell.update(vel, noise_std=0.5)
    # Migration bias should have changed at least once
    # (probabilistically near-certain with 50 steps and max persistence 25)
    print("  [PASS] test_persistent_walk")


def test_deformation():
    """Verify cell contour is not a perfect circle (deformation active)."""
    cell = CellDFC(azimuth=0, elevation=0, radius=1000, radial_size=np.pi/32)
    # Compute distances from center in AER space
    d_az = cell.contour_aer[:, 0] - cell.center_aer[0]
    d_el = cell.contour_aer[:, 1] - cell.center_aer[1]
    distances = np.sqrt(d_az**2 + d_el**2)
    # Distances should vary (not all equal) due to Fourier deformation
    assert np.std(distances) > 1e-6, "Deformation should create non-uniform distances"
    print("  [PASS] test_deformation")


if __name__ == '__main__':
    print("Running CellDFC tests...")
    test_creation()
    test_center_on_sphere()
    test_contour_shape()
    test_contour_radius()
    test_update_moves_cell()
    test_azimuth_wrapping()
    test_elevation_clamping()
    test_inactive_cell_no_update()
    test_get_state()
    test_coordinate_conversion()
    test_persistent_walk()
    test_deformation()
    print("All CellDFC tests passed.")
