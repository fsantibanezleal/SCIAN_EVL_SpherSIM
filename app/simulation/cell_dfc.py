"""
Deep Forming Cell (DFC) on a spherical embryo surface.

DFCs are represented as circular contours in spherical coordinates.
Each cell has a center (azimuth, elevation, radius) and a discretized
boundary of N vertices distributed uniformly around the center.

The cell contour in spherical coordinates:
    vertex[i].azimuth   = center.azimuth   + radialSize * cos(2*pi*i / N)
    vertex[i].elevation = center.elevation  + radialSize * sin(2*pi*i / N)
    vertex[i].radius    = center.radius     (constant on sphere)

References:
    - Oteiza et al. (2015), Cell collectivity during KV formation
    - Ablooglu et al. (eLife 2021), DFC apical contacts and dragging
"""

import numpy as np


def spherical_to_cartesian(azimuth: float, elevation: float, radius: float):
    """Convert spherical coordinates (AER) to Cartesian (XYZ).

    Uses the convention where azimuth is the longitude angle around the
    vertical axis, elevation is the latitude measured from the equator,
    and radius is the distance from the origin.

    Args:
        azimuth: Angle around vertical axis (radians).
        elevation: Angle from equator (radians), positive toward north pole.
        radius: Distance from center.

    Returns:
        Tuple (x, y, z) in Cartesian coordinates.
    """
    x = radius * np.cos(elevation) * np.cos(azimuth)
    y = radius * np.cos(elevation) * np.sin(azimuth)
    z = radius * np.sin(elevation)
    return x, y, z


def cartesian_to_spherical(x: float, y: float, z: float):
    """Convert Cartesian coordinates to spherical (AER).

    Args:
        x: Cartesian x coordinate.
        y: Cartesian y coordinate.
        z: Cartesian z coordinate.

    Returns:
        Tuple (azimuth, elevation, radius).
    """
    r = np.sqrt(x**2 + y**2 + z**2)
    elevation = np.arcsin(np.clip(z / (r + 1e-10), -1, 1))
    azimuth = np.arctan2(y, x)
    return azimuth, elevation, r


class CellDFC:
    """Deep Forming Cell on a spherical embryo surface.

    A DFC is modeled as a circular contour on the sphere, defined by a
    center position in spherical coordinates and an angular radius
    (``radial_size``).  The contour is discretized into ``num_vertices``
    evenly spaced points.

    Attributes:
        center_aer: numpy array [azimuth, elevation, radius].
        radial_size: Angular half-width of the cell (radians).
        num_vertices: Number of vertices in the discretized contour.
        active: Whether the cell participates in the simulation.
        contour_aer: Nx3 array of contour vertices in spherical coords.
        contour_xyz: Nx3 array of contour vertices in Cartesian coords.
        center_xyz: 1D array of center position in Cartesian coords.
    """

    def __init__(
        self,
        azimuth: float,
        elevation: float,
        radius: float,
        radial_size: float,
        num_vertices: int = 100,
    ):
        """Initialize a DFC cell.

        Args:
            azimuth: Angular position around vertical axis (radians).
            elevation: Elevation angle from equator (radians).
            radius: Embryo radius (spatial units).
            radial_size: Cell angular radius (radians).
            num_vertices: Number of points in contour discretization.
        """
        self.center_aer = np.array([azimuth, elevation, radius], dtype=np.float64)
        self.radial_size = radial_size
        self.num_vertices = num_vertices
        self.active = True

        # Contour storage
        self.contour_aer = np.zeros((num_vertices, 3), dtype=np.float64)
        self.contour_xyz = np.zeros((num_vertices, 3), dtype=np.float64)
        self.center_xyz = np.zeros(3, dtype=np.float64)

        self._update_cartesian_center()
        self._create_contour()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _update_cartesian_center(self):
        """Recompute the Cartesian center from the current spherical center."""
        x, y, z = spherical_to_cartesian(*self.center_aer)
        self.center_xyz = np.array([x, y, z])

    def _create_contour(self):
        """Generate a circular contour on the sphere surface.

        Each vertex is placed at a fixed angular offset from the center,
        sampled uniformly around the full circle.
        """
        angles = np.linspace(0, 2 * np.pi, self.num_vertices, endpoint=False)

        for i, angle in enumerate(angles):
            az = self.center_aer[0] + self.radial_size * np.cos(angle)
            el = self.center_aer[1] + self.radial_size * np.sin(angle)
            r = self.center_aer[2]

            self.contour_aer[i] = [az, el, r]
            x, y, z = spherical_to_cartesian(az, el, r)
            self.contour_xyz[i] = [x, y, z]

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def update(self, velocity_aer: np.ndarray, noise_std: float = 0.5):
        """Advance the cell by one time step.

        Applies a deterministic velocity plus a stochastic Gaussian
        perturbation.  The noise amplitude scales with the absolute
        elevation component of the velocity so that faster-moving cells
        experience proportionally larger fluctuations.

        After updating the center position the azimuth is wrapped to
        [-pi, pi] and the elevation is clamped to [-pi/2, pi/2].

        Args:
            velocity_aer: Base velocity vector [dAz, dEl, dR].
            noise_std: Standard deviation of noise relative to velocity
                       magnitude.
        """
        if not self.active:
            return

        # Stochastic perturbation
        noise = noise_std * np.abs(velocity_aer[1]) * np.random.randn(2)
        actual_velocity = velocity_aer.copy()
        actual_velocity[0] += noise[0]
        actual_velocity[1] += noise[1]

        # Integrate position
        self.center_aer += actual_velocity

        # Wrap azimuth to [-pi, pi]
        self.center_aer[0] = ((self.center_aer[0] + np.pi) % (2 * np.pi)) - np.pi
        # Clamp elevation to [-pi/2, pi/2]
        self.center_aer[1] = np.clip(self.center_aer[1], -np.pi / 2, np.pi / 2)

        self._update_cartesian_center()
        self._create_contour()

    def get_state(self) -> dict:
        """Return a JSON-serializable snapshot of the cell state.

        Used for WebSocket streaming to the browser client.

        Returns:
            Dictionary with center, contour, size, and activity flag.
        """
        return {
            "center_aer": self.center_aer.tolist(),
            "center_xyz": self.center_xyz.tolist(),
            "contour_xyz": self.contour_xyz.tolist(),
            "radial_size": self.radial_size,
            "active": self.active,
        }
