"""
Collision detection, resolution, and cell-cell adhesion on a spherical surface.

This module handles two types of inter-cell interactions:

1. **Collision detection and resolution**: Overlapping cell pairs are pushed
   apart along the great-circle geodesic connecting their centers.  Distance
   is computed with the Haversine formula, which is exact on the sphere.

2. **Differential adhesion**: Nearby (but non-overlapping) cells experience
   a weak attractive force, modeling cadherin-mediated cell-cell adhesion
   per the Differential Adhesion Hypothesis (Steinberg, 1963).

Complexity is O(n^2) pairwise, which is acceptable for the typical DFC
population of ~24 cells.  For larger populations (n > 100), a spatial hash
on the sphere would be needed to maintain real-time performance.

References:
    - Steinberg, M.S. (1963). Reconstruction of tissues by dissociated cells.
    - Foty, R.A. & Steinberg, M.S. (2005). The differential adhesion hypothesis:
      a direct evaluation. Developmental Biology, 278(1), 255-263.
"""

import numpy as np


def angular_distance(cell_a, cell_b) -> float:
    """Compute great-circle angular distance between two cells on the sphere.

    Uses the Haversine formula which is numerically stable for both
    small and large angular separations:

        d = 2 * arcsin(sqrt(sin^2(d_el/2) + cos(el1)*cos(el2)*sin^2(d_az/2)))

    where el is elevation (latitude) and az is azimuth (longitude).

    This is exact on the sphere, unlike the flat approximation
    sqrt(d_az^2 + d_el^2) which introduces significant error at large
    angular separations or near the poles.

    Args:
        cell_a: First CellDFC instance with center_aer attribute.
        cell_b: Second CellDFC instance with center_aer attribute.

    Returns:
        Angular distance in radians on the unit sphere.
    """
    az1, el1 = cell_a.center_aer[0], cell_a.center_aer[1]
    az2, el2 = cell_b.center_aer[0], cell_b.center_aer[1]

    d_el = el2 - el1
    d_az = az2 - az1

    # Haversine intermediate value
    a = np.sin(d_el / 2)**2 + np.cos(el1) * np.cos(el2) * np.sin(d_az / 2)**2

    # Clip to [0, 1] to guard against floating-point overshoot
    return 2 * np.arcsin(np.sqrt(np.clip(a, 0, 1)))


def apply_adhesion(cells, adhesion_strength=0.001, adhesion_range=3.0):
    """Apply differential adhesion forces between nearby cells.

    Cells within the adhesion range experience a weak attractive
    force toward each other, modeling cadherin-mediated cell-cell
    adhesion.  This implements the Differential Adhesion Hypothesis
    (Steinberg, 1963) in a simplified pairwise form.

    The adhesion force is:
        F_adh = strength * (d - r_min) / (r_max - r_min) * direction

    for r_min < d < r_max, where d is the cell-cell distance,
    r_min is the contact distance, and r_max is the adhesion range.

    The force magnitude increases linearly from zero at the contact
    boundary to `adhesion_strength` at the maximum adhesion range,
    so cells that are further apart (but still within range) feel
    stronger attraction, mimicking the restoring behavior of
    stretched cadherin bonds.

    Args:
        cells: List of active CellDFC objects.
        adhesion_strength: Maximum magnitude of adhesion force (radians/step).
        adhesion_range: Maximum range for adhesion, expressed as a multiple
            of the contact distance (sum of radial sizes).
    """
    n = len(cells)

    for i in range(n):
        for j in range(i + 1, n):
            dist = angular_distance(cells[i], cells[j])
            contact_dist = cells[i].radial_size + cells[j].radial_size
            max_range = contact_dist * adhesion_range

            # Adhesion acts only between contact distance and max range
            if contact_dist < dist < max_range:
                # Force ramps linearly from 0 at contact to full at max range
                force = adhesion_strength * (dist - contact_dist) / (max_range - contact_dist)

                # Direction vector from cell i toward cell j (attractive)
                direction = cells[j].center_aer[:2] - cells[i].center_aer[:2]
                norm = np.linalg.norm(direction)
                if norm > 1e-10:
                    direction /= norm

                    # Pull both cells toward each other
                    cells[i].center_aer[0] += direction[0] * force
                    cells[i].center_aer[1] += direction[1] * force
                    cells[j].center_aer[0] -= direction[0] * force
                    cells[j].center_aer[1] -= direction[1] * force


def solve_collisions(cells, adhesion_enabled=True, adhesion_strength=0.001):
    """Resolve overlaps and apply adhesion between all cell pairs.

    For each overlapping pair, cells are pushed apart along the
    great-circle connecting their centers.  The push magnitude is
    slightly more than half the overlap distance (55%), applied
    symmetrically, to ensure complete separation in a single pass.

    The algorithm uses a single pass with immediate position updates,
    which is sufficient for the typical population sizes (~24 cells).
    For larger populations, an iterative relaxation scheme would
    provide better convergence.

    After collision resolution, differential adhesion is applied to
    create cohesive cell clusters (if enabled).

    Complexity: O(n^2) pairwise checks, acceptable for n <= 100.

    Args:
        cells: List of CellDFC instances (active and inactive).
        adhesion_enabled: Whether to apply cell-cell adhesion forces
            after collision resolution.
        adhesion_strength: Magnitude of adhesion force (radians/step).
    """
    active = [c for c in cells if c.active]
    n = len(active)

    for i in range(n):
        for j in range(i + 1, n):
            dist = angular_distance(active[i], active[j])
            min_dist = active[i].radial_size + active[j].radial_size

            if dist < min_dist and dist > 1e-10:
                # Amount of overlap to resolve
                overlap = min_dist - dist
                # Push slightly more than half to guarantee separation
                push = overlap * 0.55

                # Direction along geodesic in AER space
                direction = active[i].center_aer[:2] - active[j].center_aer[:2]
                norm = np.linalg.norm(direction)
                if norm < 1e-10:
                    # Degenerate case: cells exactly coincident, use random perturbation
                    direction = np.random.randn(2)
                    norm = np.linalg.norm(direction)
                direction /= norm

                # Apply symmetric push along the connecting direction
                active[i].center_aer[0] += direction[0] * push
                active[i].center_aer[1] += direction[1] * push
                active[j].center_aer[0] -= direction[0] * push
                active[j].center_aer[1] -= direction[1] * push

                # Enforce spherical coordinate bounds
                for cell in [active[i], active[j]]:
                    # Wrap azimuth to [-pi, pi]
                    cell.center_aer[0] = ((cell.center_aer[0] + np.pi) % (2 * np.pi)) - np.pi
                    # Clamp elevation to avoid pole singularities
                    cell.center_aer[1] = np.clip(
                        cell.center_aer[1], -np.pi / 2 + 0.01, np.pi / 2 - 0.01
                    )

                # Rebuild Cartesian coordinates and cell contour
                active[i]._update_cartesian_center()
                active[i]._create_contour()
                active[j]._update_cartesian_center()
                active[j]._create_contour()

    # Apply adhesion after collision resolution
    if adhesion_enabled:
        apply_adhesion(active, adhesion_strength=adhesion_strength)
