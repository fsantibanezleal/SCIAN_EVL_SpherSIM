"""
Collision detection, resolution, and adhesion on a spherical surface.

===== GEODESIC-CORRECT COLLISION RESOLUTION =====

The key challenge on a sphere is that the AER coordinate system
(azimuth, elevation) has a NON-UNIFORM metric:

    ds^2 = R^2(dtheta^2 + cos^2(theta)*dphi^2)

This means equal azimuth increments (dphi) produce different physical
arc lengths at different latitudes. At elevation theta:

    arc_length = R * cos(theta) * dphi

Consequence: pushing cells apart by equal dphi amounts is WRONG because:
- Near the equator (theta~0): cos(0)=1, full arc length
- At 60 deg latitude: cos(60 deg)=0.5, half the arc length
- At the pole (theta=90 deg): cos(90 deg)=0, zero arc length (singularity!)

===== SOLUTION: CARTESIAN PUSH =====

We resolve collisions in Cartesian 3D space where the metric is
uniform (ds^2 = dx^2 + dy^2 + dz^2):

1. Compute push direction as 3D vector between cell centers
2. Project onto the tangent plane at each cell's position
3. Move cell along the tangent direction by the required arc length
4. Renormalize to the sphere surface: x_new = R * x/|x|
5. Convert back to AER coordinates

This gives physically correct, latitude-independent collision resolution.

===== DIFFERENTIAL ADHESION =====

Cell-cell adhesion follows the Differential Adhesion Hypothesis
(Steinberg, 1963): cells with matching surface receptors attract
each other via cadherin-mediated bonds.

Force model:
    F = s * (d - d_contact) / (d_max - d_contact) * d_hat
for d_contact < d < d_max

References:
    - Steinberg (1963), Reconstruction of tissues by dissociated cells
    - Foty & Steinberg (2005), The differential adhesion hypothesis
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

    Uses Cartesian 3D space for the same reason as collision resolution:
    the AER metric is non-uniform, so equal angular displacements in
    azimuth produce different physical distances at different latitudes.

    Cells within the adhesion range experience a weak attractive
    force toward each other, modeling cadherin-mediated cell-cell
    adhesion per the Differential Adhesion Hypothesis (Steinberg, 1963).

    The adhesion force is:
        F_adh = strength * (d - r_min) / (r_max - r_min) * direction

    for r_min < d < r_max, where d is the angular cell-cell distance,
    r_min is the contact distance, and r_max is the adhesion range.

    The direction is computed in Cartesian 3D, projected onto each
    cell's tangent plane, then the cell is moved and renormalized
    back to the sphere surface.

    Args:
        cells: List of active CellDFC objects.
        adhesion_strength: Maximum magnitude of adhesion force (radians/step).
        adhesion_range: Maximum range for adhesion, expressed as a multiple
            of the contact distance (sum of radial sizes).
    """
    from .cell_dfc import cartesian_to_spherical

    n = len(cells)

    for i in range(n):
        for j in range(i + 1, n):
            dist = angular_distance(cells[i], cells[j])
            contact_dist = cells[i].radial_size + cells[j].radial_size
            max_range = contact_dist * adhesion_range

            # Adhesion acts only between contact distance and max range
            if contact_dist < dist < max_range:
                # Force ramps linearly from 0 at contact to full at max range
                force_angle = adhesion_strength * (dist - contact_dist) / (max_range - contact_dist)

                # --- CARTESIAN ADHESION ---
                # Direction from cell i toward cell j in 3D (attractive)
                xyz_i = cells[i].center_xyz.copy()
                xyz_j = cells[j].center_xyz.copy()
                R = cells[i].center_aer[2]

                diff = xyz_j - xyz_i  # points from i toward j
                diff_norm = np.linalg.norm(diff)
                if diff_norm < 1e-10:
                    continue
                direction_3d = diff / diff_norm

                # Convert angular force to arc length
                arc_force = force_angle * R

                # Apply to both cells: i pulled toward j, j pulled toward i
                for cell, sign in [(cells[i], +1), (cells[j], -1)]:
                    pos = cell.center_xyz.copy()
                    normal = pos / np.linalg.norm(pos)

                    # Project direction onto tangent plane
                    tangent_dir = direction_3d - np.dot(direction_3d, normal) * normal
                    tangent_norm = np.linalg.norm(tangent_dir)
                    if tangent_norm > 1e-10:
                        tangent_dir /= tangent_norm
                    else:
                        continue

                    # Move along tangent and project back to sphere
                    new_pos = pos + sign * arc_force * tangent_dir
                    new_pos = R * new_pos / np.linalg.norm(new_pos)

                    # Convert back to AER
                    az, el, r = cartesian_to_spherical(new_pos[0], new_pos[1], new_pos[2])
                    cell.center_aer[0] = az
                    cell.center_aer[1] = np.clip(el, -np.pi/2 + 0.01, np.pi/2 - 0.01)
                    cell.center_aer[2] = R
                    cell._update_cartesian_center()
                    cell._create_contour()


def solve_collisions(cells, adhesion_enabled=True, adhesion_strength=0.001):
    """Resolve overlaps using geodesic-correct Cartesian repulsion.

    ===== WHY CARTESIAN PUSH IS NECESSARY =====

    The AER coordinate system (azimuth, elevation) has a non-uniform
    metric tensor. An angular displacement daz in azimuth covers
    physical arc length daz*R*cos(el), which vanishes at the poles.

    Pushing cells by equal daz amounts at different latitudes moves
    them unequal physical distances, causing:
    - Cells near poles to barely move (under-correction)
    - Cells near equator to move correctly
    - Asymmetric resolution between north-south and east-west

    The fix: compute push direction in Cartesian 3D (where the metric
    is uniform), apply the push along the tangent plane, then project
    back to the sphere surface by renormalizing to radius R.

    ===== ALGORITHM =====

    For each overlapping pair (i, j):
    1. Compute great-circle distance d via Haversine
    2. If d < r_i + r_j (overlap):
       a. Push vector in 3D: p = normalize(xyz_i - xyz_j)
       b. Tangent projection: project p onto each cell's tangent plane
       c. Move each cell by +/-push in tangent direction
       d. Renormalize to sphere: xyz_new = R * normalize(xyz_new)
       e. Convert back to AER

    Complexity: O(n^2) pairwise checks, acceptable for n <= 100.

    Args:
        cells: List of CellDFC instances (active and inactive).
        adhesion_enabled: Whether to apply cell-cell adhesion forces
            after collision resolution.
        adhesion_strength: Magnitude of adhesion force (radians/step).
    """
    from .cell_dfc import cartesian_to_spherical

    active = [c for c in cells if c.active]
    n = len(active)

    for i in range(n):
        for j in range(i + 1, n):
            dist = angular_distance(active[i], active[j])
            min_dist = active[i].radial_size + active[j].radial_size

            if dist < min_dist and dist > 1e-10:
                overlap = min_dist - dist
                push_angle = overlap * 0.55  # slightly more than half

                # --- CARTESIAN PUSH ---
                # Direction vector between cell centers in 3D
                xyz_i = active[i].center_xyz.copy()
                xyz_j = active[j].center_xyz.copy()
                R = active[i].center_aer[2]  # embryo radius

                diff = xyz_i - xyz_j
                diff_norm = np.linalg.norm(diff)
                if diff_norm < 1e-10:
                    diff = np.random.randn(3)
                    diff_norm = np.linalg.norm(diff)
                direction_3d = diff / diff_norm

                # Convert angular push to arc length, then to Cartesian displacement
                arc_push = push_angle * R

                # Project direction onto tangent plane at each cell's position
                # Tangent plane normal = normalized position vector
                for cell, sign in [(active[i], +1), (active[j], -1)]:
                    pos = cell.center_xyz.copy()
                    normal = pos / np.linalg.norm(pos)

                    # Project push direction onto tangent plane
                    tangent_dir = direction_3d - np.dot(direction_3d, normal) * normal
                    tangent_norm = np.linalg.norm(tangent_dir)
                    if tangent_norm > 1e-10:
                        tangent_dir /= tangent_norm
                    else:
                        # Degenerate: use random tangent direction
                        tangent_dir = np.cross(normal, np.array([0, 0, 1]))
                        tn = np.linalg.norm(tangent_dir)
                        if tn < 1e-10:
                            tangent_dir = np.cross(normal, np.array([1, 0, 0]))
                            tn = np.linalg.norm(tangent_dir)
                        tangent_dir /= tn

                    # Move along tangent and project back to sphere
                    new_pos = pos + sign * arc_push * tangent_dir
                    new_pos = R * new_pos / np.linalg.norm(new_pos)

                    # Convert back to AER
                    az, el, r = cartesian_to_spherical(new_pos[0], new_pos[1], new_pos[2])
                    cell.center_aer[0] = az
                    cell.center_aer[1] = np.clip(el, -np.pi/2 + 0.01, np.pi/2 - 0.01)
                    cell.center_aer[2] = R
                    cell._update_cartesian_center()
                    cell._create_contour()

    if adhesion_enabled:
        apply_adhesion(active, adhesion_strength=adhesion_strength)
