"""
Deep Forming Cell (DFC) on a spherical embryo surface.

DFCs are represented as deformable contours in spherical coordinates.
Each cell has a center (azimuth, elevation, radius) and a discretized
boundary of N vertices distributed around the center with Fourier-mode
perturbations for biological realism.

The migration model uses a persistent random walk where cells maintain
a directional bias for several steps before stochastic reorientation,
modeling filopodial persistence observed in migrating cells.

Cell contour with deformation:
    R(theta) = R_base * (1 + eps * sum_k cos(k*theta + phi_k(t)))

where eps is the deformation amplitude and phi_k(t) are time-varying
phases that create dynamic membrane fluctuations.

References:
    - Oteiza et al. (2015), Cell collectivity during KV formation
    - Ablooglu et al. (eLife 2021), DFC apical contacts and dragging
    - Selmeczi et al. (2005), Cell motility as persistent random motion
"""

import numpy as np


def spherical_to_cartesian(azimuth: float, elevation: float, radius: float):
    """Convert spherical coordinates (AER) to Cartesian (XYZ).

    Uses the geographic convention where azimuth is the longitude angle
    around the vertical axis, elevation is the latitude measured from
    the equator, and radius is the distance from the origin.

    The mapping is:
        x = r * cos(el) * cos(az)
        y = r * cos(el) * sin(az)
        z = r * sin(el)

    Args:
        azimuth: Angle around vertical axis (radians), positive eastward.
        elevation: Angle from equator (radians), positive toward north pole.
        radius: Distance from center (spatial units).

    Returns:
        Tuple (x, y, z) in Cartesian coordinates.
    """
    x = radius * np.cos(elevation) * np.cos(azimuth)
    y = radius * np.cos(elevation) * np.sin(azimuth)
    z = radius * np.sin(elevation)
    return x, y, z


def cartesian_to_spherical(x: float, y: float, z: float):
    """Convert Cartesian coordinates to spherical (AER).

    Inverse of :func:`spherical_to_cartesian`.  The radius is recovered
    as the Euclidean norm, elevation via arcsin(z/r), and azimuth via
    arctan2(y, x).

    Args:
        x: Cartesian x coordinate.
        y: Cartesian y coordinate.
        z: Cartesian z coordinate.

    Returns:
        Tuple (azimuth, elevation, radius) in spherical coordinates.
    """
    r = np.sqrt(x**2 + y**2 + z**2)
    # Clip to handle numerical noise in z/r
    elevation = np.arcsin(np.clip(z / (r + 1e-10), -1, 1))
    azimuth = np.arctan2(y, x)
    return azimuth, elevation, r


class CellDFC:
    """Deep Forming Cell on a spherical embryo surface.

    A DFC is modeled as a deformable contour on the sphere, defined by a
    center position in spherical coordinates and an angular radius
    (``radial_size``).  The contour is discretized into ``num_vertices``
    points, perturbed by low-frequency Fourier modes for visual realism.

    The migration model combines deterministic EVL-driven drift, a
    persistent directional bias (random walk with memory), and
    stochastic Gaussian noise.

    Attributes:
        center_aer: numpy array [azimuth, elevation, radius].
        radial_size: Angular half-width of the cell (radians).
        num_vertices: Number of vertices in the discretized contour.
        active: Whether the cell participates in the simulation.
        contour_aer: Nx3 array of contour vertices in spherical coords.
        contour_xyz: Nx3 array of contour vertices in Cartesian coords.
        center_xyz: 1D array of center position in Cartesian coords.
        persistence_time: Steps before random reorientation event.
        steps_since_reorientation: Counter for persistence tracking.
        migration_bias: Current directional bias angle (radians).
        deformation_amplitude: Strength of contour shape perturbation.
        deformation_phases: Phase offsets for each Fourier deformation mode.
        deformation_rates: Angular velocities for time-varying deformation.
    """

    def __init__(
        self,
        azimuth: float,
        elevation: float,
        radius: float,
        radial_size: float,
        num_vertices: int = 100,
    ):
        """Initialize a DFC cell with position, size, and deformation state.

        Args:
            azimuth: Angular position around vertical axis (radians).
            elevation: Elevation angle from equator (radians).
            radius: Embryo radius (spatial units).
            radial_size: Cell angular radius (radians).
            num_vertices: Number of points in contour discretization.
                Higher values give smoother contours but cost more to compute.
        """
        self.center_aer = np.array([azimuth, elevation, radius], dtype=np.float64)
        self.radial_size = radial_size
        self.num_vertices = num_vertices
        self.active = True

        # Persistent random walk: cells maintain direction for several steps,
        # modeling filopodial persistence observed in migrating cells
        self.persistence_time = np.random.randint(8, 25)
        self.steps_since_reorientation = 0
        self.migration_bias = np.random.uniform(-np.pi, np.pi)

        # Deformation parameters: low-frequency Fourier modes create
        # biologically realistic irregular cell boundaries
        self.deformation_amplitude = 0.15  # fraction of radial_size
        self.deformation_phases = np.random.uniform(0, 2 * np.pi, 4)  # 4 modes
        self.deformation_rates = np.random.uniform(-0.05, 0.05, 4)  # rotation speeds

        # Contour storage (pre-allocated for efficiency)
        self.contour_aer = np.zeros((num_vertices, 3), dtype=np.float64)
        self.contour_xyz = np.zeros((num_vertices, 3), dtype=np.float64)
        self.center_xyz = np.zeros(3, dtype=np.float64)

        # Compute initial Cartesian position and contour
        self._update_cartesian_center()
        self._create_contour()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _update_cartesian_center(self):
        """Recompute the Cartesian center from the current spherical center.

        Called after any position update to keep the Cartesian representation
        synchronized with the spherical coordinates.
        """
        x, y, z = spherical_to_cartesian(*self.center_aer)
        self.center_xyz = np.array([x, y, z])

    def _create_contour(self):
        """Generate deformable cell contour on the sphere surface.

        The contour is a circle perturbed by low-frequency Fourier modes
        to create a more biologically realistic irregular cell boundary:

            R(theta) = R_base * (1 + eps * sum_k cos(k*theta + phi_k))

        where eps is the deformation amplitude and phi_k are time-varying
        phases that create dynamic membrane fluctuations.  Using modes
        k = 2, 3, 4, 5 avoids the k=0 (size change) and k=1 (translation)
        modes, preserving the cell's mean size and center position.
        """
        angles = np.linspace(0, 2 * np.pi, self.num_vertices, endpoint=False)

        # Fourier-mode deformation for biological realism
        deformation = np.zeros(self.num_vertices)
        for k in range(len(self.deformation_phases)):
            # Modes k+2 to avoid pure translation (k=1) and size change (k=0)
            deformation += np.cos((k + 2) * angles + self.deformation_phases[k])
        # Normalize by number of modes to keep amplitude controlled
        deformation *= self.deformation_amplitude / len(self.deformation_phases)

        # Perturbed radial size for each vertex
        perturbed_size = self.radial_size * (1.0 + deformation)

        for i, angle in enumerate(angles):
            az = self.center_aer[0] + perturbed_size[i] * np.cos(angle)
            el = self.center_aer[1] + perturbed_size[i] * np.sin(angle)
            r = self.center_aer[2]

            self.contour_aer[i] = [az, el, r]
            x, y, z = spherical_to_cartesian(az, el, r)
            self.contour_xyz[i] = [x, y, z]

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def update(self, velocity_aer: np.ndarray, noise_std: float = 0.5):
        """Update cell position using a persistent random walk model.

        The migration model combines three components:

        1. **Deterministic drift**: Base velocity from EVL margin (v_EVL)
        2. **Persistent bias**: Directional preference maintained for tau steps
        3. **Stochastic noise**: Gaussian perturbation for random exploration

        The effective velocity is:
            v = v_EVL + alpha * bias_direction + sigma * xi

        where alpha is the persistence strength (proportional to the EVL
        velocity magnitude), and xi ~ N(0, sigma^2).

        After tau steps, the cell reorients by choosing a new random
        bias direction, modeling filopodial retraction and re-extension.

        Args:
            velocity_aer: Base velocity [dAz, dEl, dR] from EVL margin.
            noise_std: Standard deviation of stochastic noise, relative
                to the velocity magnitude.
        """
        if not self.active:
            return

        self.steps_since_reorientation += 1

        # Check for reorientation event (filopodial re-extension)
        if self.steps_since_reorientation >= self.persistence_time:
            self.steps_since_reorientation = 0
            self.persistence_time = np.random.randint(8, 25)
            self.migration_bias = np.random.uniform(-np.pi, np.pi)

        # Persistence contribution: directional bias scaled by EVL velocity
        persistence_strength = 0.3 * np.abs(velocity_aer[1])
        bias_az = persistence_strength * np.cos(self.migration_bias)
        bias_el = persistence_strength * np.sin(self.migration_bias)

        # Stochastic noise scaled by velocity magnitude
        noise_scale = noise_std * np.abs(velocity_aer[1])
        noise_az = noise_scale * np.random.randn()
        noise_el = noise_scale * np.random.randn()

        # Combined velocity: deterministic + persistent bias + noise
        actual_velocity = velocity_aer.copy()
        actual_velocity[0] += bias_az + noise_az
        actual_velocity[1] += bias_el + noise_el

        # Integrate position
        self.center_aer += actual_velocity

        # Wrap azimuth to [-pi, pi]
        self.center_aer[0] = ((self.center_aer[0] + np.pi) % (2 * np.pi)) - np.pi
        # Clamp elevation to [-pi/2, pi/2] with small margin for pole safety
        self.center_aer[1] = np.clip(self.center_aer[1], -np.pi / 2 + 0.01, np.pi / 2 - 0.01)

        # Advance deformation phases to animate membrane fluctuations
        self.deformation_phases += self.deformation_rates

        self._update_cartesian_center()
        self._create_contour()

    def get_state(self) -> dict:
        """Return a JSON-serializable snapshot of the cell state.

        Used for WebSocket streaming to the browser client.  Includes
        both spherical and Cartesian representations of the center and
        contour, plus metadata for the frontend renderer.

        Returns:
            Dictionary with keys: center_aer, center_xyz, contour_xyz,
            radial_size, active.
        """
        return {
            "center_aer": self.center_aer.tolist(),
            "center_xyz": self.center_xyz.tolist(),
            "contour_xyz": self.contour_xyz.tolist(),
            "radial_size": self.radial_size,
            "active": self.active,
        }
