"""
Spherical embryo environment for EVL / DFC simulation.

Models the zebrafish embryo as a sphere with configurable radius.
The EVL (Enveloping Layer) provides a migrating margin that drives
DFC convergence movements during epiboly.

References:
    - Compagnon & Bhatt (2019), Mechanisms of zebrafish epiboly
    - Rho et al. (2009), Zebrafish epiboly: mechanics and mechanisms
"""

import numpy as np


class SphericalEnvironment:
    """Spherical embryo environment.

    Holds global parameters such as the embryo radius, EVL margin speed,
    DFC placement bounds, and noise level.  Exposes the margin velocity
    vector consumed by :class:`DFCLayer.update`.

    Attributes:
        embryo_radius: Radius of the embryo sphere (spatial units).
        num_dfcs: Default number of DFC cells.
        radial_size: Default angular cell radius (radians).
        num_vertices: Default contour discretization.
        margin_velocity: Current EVL velocity [dAz, dEl, dR].
        az_range: Azimuth bounds for DFC placement.
        el_range: Elevation bounds for DFC placement.
        noise_std: Noise amplitude parameter.
        step_count: Number of simulation steps completed.
    """

    def __init__(self, config: dict | None = None):
        """Create the environment from a configuration dictionary.

        Args:
            config: Optional dictionary.  Recognized keys:
                ``embryo_radius``, ``num_dfcs``, ``radial_size``,
                ``num_vertices``, ``evl_speed``, ``min_azimuth``,
                ``max_azimuth``, ``min_elevation``, ``max_elevation``,
                ``noise_std``.
        """
        config = config or {}
        self.embryo_radius: float = config.get("embryo_radius", 1000)
        self.num_dfcs: int = config.get("num_dfcs", 24)
        self.radial_size: float = config.get("radial_size", np.pi / 64)
        self.num_vertices: int = config.get("num_vertices", 100)

        # EVL margin velocity [azimuth, elevation, radius]
        evl_speed = config.get("evl_speed", 1.0 / 200.0)
        self.margin_velocity = np.array([0, -(np.pi / 2) * evl_speed, 0])

        # DFC region bounds
        self.az_range = (
            config.get("min_azimuth", -3 * np.pi / 4),
            config.get("max_azimuth", -np.pi / 2),
        )
        self.el_range = (
            config.get("min_elevation", 0),
            config.get("max_elevation", np.pi / 4),
        )

        # Noise
        self.noise_std: float = config.get("noise_std", 0.5)

        self.step_count: int = 0

    def update(self):
        """Advance the environment by one time step."""
        self.step_count += 1

    def get_state(self) -> dict:
        """Return a JSON-serializable snapshot of the environment.

        Returns:
            Dictionary with radius, velocity, step count, and bounds.
        """
        return {
            "embryo_radius": self.embryo_radius,
            "margin_velocity": self.margin_velocity.tolist(),
            "step": self.step_count,
            "az_range": list(self.az_range),
            "el_range": list(self.el_range),
        }
