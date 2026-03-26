"""
Geometric utilities for spherical computations.

Provides coordinate conversion functions (both single-point and batched),
great-circle distance calculations, and sphere mesh generation for the
Three.js frontend.
"""

import numpy as np


def spherical_to_cartesian_batch(aer: np.ndarray) -> np.ndarray:
    """Convert an Nx3 array of [azimuth, elevation, radius] to [x, y, z].

    Args:
        aer: Array of shape (N, 3) with columns (azimuth, elevation, radius).

    Returns:
        Array of shape (N, 3) with columns (x, y, z).
    """
    az, el, r = aer[:, 0], aer[:, 1], aer[:, 2]
    x = r * np.cos(el) * np.cos(az)
    y = r * np.cos(el) * np.sin(az)
    z = r * np.sin(el)
    return np.column_stack([x, y, z])


def cartesian_to_spherical_batch(xyz: np.ndarray) -> np.ndarray:
    """Convert an Nx3 array of [x, y, z] to [azimuth, elevation, radius].

    Args:
        xyz: Array of shape (N, 3) with columns (x, y, z).

    Returns:
        Array of shape (N, 3) with columns (azimuth, elevation, radius).
    """
    x, y, z = xyz[:, 0], xyz[:, 1], xyz[:, 2]
    r = np.sqrt(x**2 + y**2 + z**2)
    el = np.arcsin(np.clip(z / (r + 1e-10), -1, 1))
    az = np.arctan2(y, x)
    return np.column_stack([az, el, r])


def great_circle_distance(
    aer1: np.ndarray, aer2: np.ndarray, radius: float = 1.0
) -> float:
    """Compute the great-circle distance between two points on a sphere.

    Uses the Haversine formula for numerical stability at small
    distances.

    Args:
        aer1: First point as [azimuth, elevation, radius].
        aer2: Second point as [azimuth, elevation, radius].
        radius: Sphere radius for arc-length conversion.

    Returns:
        Arc-length distance on the sphere surface.
    """
    lat1, lon1 = aer1[1], aer1[0]
    lat2, lon2 = aer2[1], aer2[0]
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    c = 2 * np.arcsin(np.sqrt(np.clip(a, 0, 1)))
    return radius * c


def generate_sphere_mesh(
    radius: float, resolution: int = 50
) -> tuple[list[float], list[float], list[float]]:
    """Generate sphere mesh vertices for Three.js rendering.

    Produces a latitude-longitude grid of 3D points on the sphere
    surface.

    Args:
        radius: Sphere radius.
        resolution: Number of subdivisions along each angular axis.

    Returns:
        Tuple of (x_list, y_list, z_list) flattened vertex coordinates.
    """
    phi = np.linspace(0, np.pi, resolution)
    theta = np.linspace(0, 2 * np.pi, resolution)
    phi, theta = np.meshgrid(phi, theta)

    x = radius * np.sin(phi) * np.cos(theta)
    y = radius * np.sin(phi) * np.sin(theta)
    z = radius * np.cos(phi)

    return x.flatten().tolist(), y.flatten().tolist(), z.flatten().tolist()
