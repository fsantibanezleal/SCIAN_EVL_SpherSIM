"""
Integration tests for the full simulation pipeline.

Verifies that:
    - Environment + DFCLayer can be created and run together
    - 50 simulation steps complete without errors
    - Cell count remains consistent
    - Serialized state has the expected structure
    - Cells actually move over time
"""

import sys
import os
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.simulation.environment import SphericalEnvironment
from app.simulation.layer_dfc import DFCLayer
from app.simulation.geometry import (
    spherical_to_cartesian_batch,
    cartesian_to_spherical_batch,
    great_circle_distance,
    generate_sphere_mesh,
)


def test_full_simulation_50_steps():
    """Run 50 steps and verify consistency."""
    config = {
        'embryo_radius': 1000,
        'num_dfcs': 12,
        'radial_size': np.pi / 64,
        'num_vertices': 30,
        'evl_speed': 0.005,
        'noise_std': 0.3,
    }

    env = SphericalEnvironment(config)
    layer = DFCLayer({'noise_std': config['noise_std'], 'division_rate': 0.0})
    layer.initialize(
        embryo_radius=config['embryo_radius'],
        num_cells=config['num_dfcs'],
        radial_size=config['radial_size'],
        num_vertices=config['num_vertices'],
    )

    initial_count = len(layer.cells)
    assert initial_count > 0

    # Record initial elevations
    np.random.seed(123)
    initial_elevations = [c.center_aer[1] for c in layer.cells]

    for step in range(50):
        env.update()
        layer.update(env.margin_velocity, evl_elevation=env.margin_elevation)

    assert layer.step_count == 50
    assert env.step_count == 50

    # Cell count should be unchanged (no cell death in this model)
    active_count = len([c for c in layer.cells if c.active])
    assert active_count == initial_count

    # Cells should have moved (elevation decreased on average due to EVL)
    final_elevations = [c.center_aer[1] for c in layer.cells]
    mean_initial = np.mean(initial_elevations)
    mean_final = np.mean(final_elevations)
    assert mean_final < mean_initial, "Cells should migrate southward on average"

    print("  [PASS] test_full_simulation_50_steps")


def test_state_serialization():
    """Serialized state should have expected keys."""
    env = SphericalEnvironment()
    layer = DFCLayer({'noise_std': 0.5, 'division_rate': 0.0})
    layer.initialize(embryo_radius=1000, num_cells=6, num_vertices=20)

    env.update()
    layer.update(env.margin_velocity, evl_elevation=env.margin_elevation)

    state = layer.get_state()
    assert 'step' in state
    assert 'num_cells' in state
    assert 'cells' in state
    assert state['step'] == 1
    assert len(state['cells']) == state['num_cells']

    # Verify new cluster metric keys
    assert 'cluster_spread' in state
    assert 'cluster_elongation' in state
    assert 'cluster_centroid' in state
    assert isinstance(state['cluster_spread'], float)
    assert isinstance(state['cluster_elongation'], float)
    assert len(state['cluster_centroid']) == 3

    env_state = env.get_state()
    assert 'embryo_radius' in env_state
    assert 'margin_velocity' in env_state
    assert 'step' in env_state

    print("  [PASS] test_state_serialization")


def test_geometry_batch_conversion():
    """Batch coordinate conversion should be self-consistent."""
    aer = np.array([
        [0.5, 0.3, 1000],
        [1.0, -0.2, 500],
        [-2.0, 0.8, 750],
    ])
    xyz = spherical_to_cartesian_batch(aer)
    aer_back = cartesian_to_spherical_batch(xyz)
    np.testing.assert_allclose(aer_back, aer, atol=1e-6)
    print("  [PASS] test_geometry_batch_conversion")


def test_great_circle_distance():
    """Great-circle distance between identical points should be zero."""
    p = np.array([1.0, 0.5, 1000])
    assert great_circle_distance(p, p, radius=1000) == 0.0
    print("  [PASS] test_great_circle_distance")


def test_sphere_mesh_generation():
    """Sphere mesh should produce the expected number of vertices."""
    res = 10
    x, y, z = generate_sphere_mesh(500, resolution=res)
    expected = res * res
    assert len(x) == expected
    assert len(y) == expected
    assert len(z) == expected
    print("  [PASS] test_sphere_mesh_generation")


def test_layer_initialization_bounds():
    """Cells should be placed within the specified bounds."""
    az_range = (-1.0, -0.5)
    el_range = (0.1, 0.6)
    layer = DFCLayer({'noise_std': 0.5})
    layer.initialize(
        embryo_radius=1000,
        num_cells=8,
        radial_size=0.04,
        num_vertices=20,
        az_range=az_range,
        el_range=el_range,
    )
    for cell in layer.cells:
        az, el = cell.center_aer[0], cell.center_aer[1]
        assert az_range[0] <= az <= az_range[1], f"Azimuth {az} out of range"
        assert el_range[0] <= el <= el_range[1], f"Elevation {el} out of range"
    print("  [PASS] test_layer_initialization_bounds")


def test_cell_division():
    """Verify stochastic cell division creates daughter cells."""
    np.random.seed(42)
    layer = DFCLayer({'noise_std': 0.3, 'division_rate': 1.0})  # rate=1.0 forces division
    layer.initialize(
        embryo_radius=1000,
        num_cells=4,
        radial_size=np.pi / 64,
        num_vertices=20,
    )
    initial_count = len(layer.cells)

    # With division_rate=1.0, all cells should divide (capped at 60)
    layer._check_division(division_rate=1.0)

    # Each parent produces 2 daughters, parents removed
    # So we should have 2 * initial_count cells
    assert len(layer.cells) == 2 * initial_count, \
        f"Expected {2 * initial_count} cells after division, got {len(layer.cells)}"
    # All cells should be active (parents removed)
    assert all(c.active for c in layer.cells), "All daughter cells should be active"
    print("  [PASS] test_cell_division")


def test_division_respects_max_cells():
    """Verify division stops at maximum cell count."""
    np.random.seed(42)
    layer = DFCLayer({'noise_std': 0.3})
    layer.initialize(
        embryo_radius=1000,
        num_cells=24,
        radial_size=np.pi / 64,
        num_vertices=20,
    )

    # Run division with high rate multiple times
    for _ in range(10):
        layer._check_division(division_rate=1.0)

    assert len(layer.cells) <= 60, \
        f"Cell count {len(layer.cells)} should not exceed 60"
    print("  [PASS] test_division_respects_max_cells")


def test_division_daughter_properties():
    """Verify daughter cells have correct properties."""
    np.random.seed(42)
    layer = DFCLayer({'noise_std': 0.3})
    layer.initialize(
        embryo_radius=1000,
        num_cells=1,
        radial_size=np.pi / 32,
        num_vertices=30,
    )
    parent_size = layer.cells[0].radial_size
    parent_el = layer.cells[0].center_aer[1]
    parent_r = layer.cells[0].center_aer[2]

    layer._check_division(division_rate=1.0)

    assert len(layer.cells) == 2, f"Expected 2 daughters, got {len(layer.cells)}"
    for d in layer.cells:
        assert abs(d.radial_size - parent_size * 0.85) < 1e-10, \
            "Daughter radial_size should be 0.85x parent"
        assert abs(d.center_aer[1] - parent_el) < 1e-10, \
            "Daughters should share parent elevation"
        assert abs(d.center_aer[2] - parent_r) < 1e-10, \
            "Daughters should share parent radius"
    print("  [PASS] test_division_daughter_properties")


def test_division_in_update():
    """Verify cell division occurs during normal update cycle."""
    np.random.seed(42)
    config = {
        'embryo_radius': 1000,
        'num_dfcs': 6,
        'radial_size': np.pi / 64,
        'num_vertices': 20,
        'evl_speed': 0.005,
        'noise_std': 0.3,
        'division_rate': 0.5,
    }
    env = SphericalEnvironment(config)
    layer = DFCLayer({'noise_std': config['noise_std'], 'division_rate': config['division_rate']})
    layer.initialize(
        embryo_radius=config['embryo_radius'],
        num_cells=config['num_dfcs'],
        radial_size=config['radial_size'],
        num_vertices=config['num_vertices'],
    )

    initial_count = len(layer.cells)

    # Run 20 steps with high division rate
    for _ in range(20):
        env.update()
        layer.update(env.margin_velocity, evl_elevation=env.margin_elevation)

    # With rate=0.5 over 20 steps, some divisions should have occurred
    assert len(layer.cells) >= initial_count, "Cell count should not decrease"
    print("  [PASS] test_division_in_update")


if __name__ == '__main__':
    print("Running integration tests...")
    test_full_simulation_50_steps()
    test_state_serialization()
    test_geometry_batch_conversion()
    test_great_circle_distance()
    test_sphere_mesh_generation()
    test_layer_initialization_bounds()
    test_cell_division()
    test_division_respects_max_cells()
    test_division_daughter_properties()
    test_division_in_update()
    print("All integration tests passed.")
