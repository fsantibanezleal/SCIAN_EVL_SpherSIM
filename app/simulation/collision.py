"""
Collision detection and resolution for cells on a spherical surface.

Uses distance-based detection in spherical coordinates and pushes
overlapping cells apart along their connecting geodesic.

For computational efficiency, collisions are detected using the angular
distance between cell centers compared to the sum of their radial sizes.
All active cell pairs are checked each time step (O(n^2)), which is
acceptable for the typical DFC population of ~24 cells.
"""

import numpy as np


def angular_distance(cell_a, cell_b) -> float:
    """Compute the angular distance between two cells on the sphere.

    Uses a flat approximation in (azimuth, elevation) space which is
    accurate for small angular separations typical of neighboring cells.

    Args:
        cell_a: First CellDFC instance.
        cell_b: Second CellDFC instance.

    Returns:
        Angular distance in radians.
    """
    da = cell_a.center_aer[0] - cell_b.center_aer[0]
    de = cell_a.center_aer[1] - cell_b.center_aer[1]
    return np.sqrt(da**2 + de**2)


def solve_collisions(cells: list):
    """Resolve overlaps between all active cell pairs.

    For each pair of cells whose angular distance is less than the sum of
    their radial sizes, the cells are pushed apart symmetrically along the
    line connecting their centers.  Each cell moves by half the overlap
    distance.

    After adjustment, contours are rebuilt to reflect the new positions.

    Args:
        cells: List of CellDFC instances.
    """
    active = [c for c in cells if c.active]
    n = len(active)

    for i in range(n):
        for j in range(i + 1, n):
            dist = angular_distance(active[i], active[j])
            min_dist = active[i].radial_size + active[j].radial_size

            if dist < min_dist and dist > 1e-10:
                # Compute overlap and push direction
                overlap = min_dist - dist
                direction = active[i].center_aer[:2] - active[j].center_aer[:2]
                direction_norm = direction / (np.linalg.norm(direction) + 1e-10)

                push = overlap * 0.5
                active[i].center_aer[0] += direction_norm[0] * push
                active[i].center_aer[1] += direction_norm[1] * push
                active[j].center_aer[0] -= direction_norm[0] * push
                active[j].center_aer[1] -= direction_norm[1] * push

                # Rebuild Cartesian data
                active[i]._update_cartesian_center()
                active[i]._create_contour()
                active[j]._update_cartesian_center()
                active[j]._create_contour()
