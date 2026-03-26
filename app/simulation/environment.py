"""
Spherical embryo environment for EVL / DFC simulation.

Models the zebrafish embryo as a sphere with configurable radius.
The EVL (Enveloping Layer) provides a migrating margin that drives
DFC convergence movements during epiboly.

The environment acts as the central parameter store and computes the
global EVL margin velocity that is broadcast to all DFC cells each
time step.  It does not hold references to the cells themselves;
instead, it exposes the velocity vector which the DFCLayer consumes.

Configuration hierarchy:
    User UI -> REST API -> SimConfig -> SphericalEnvironment

References:
    - Compagnon & Bhatt (2019), Mechanisms of zebrafish epiboly
    - Rho et al. (2009), Zebrafish epiboly: mechanics and mechanisms
"""

import numpy as np


class SphericalEnvironment:
    """Spherical embryo environment holding global simulation parameters.

    Holds global parameters such as the embryo radius, EVL margin speed,
    DFC placement bounds, and noise level.  Exposes the margin velocity
    vector consumed by :class:`DFCLayer.update`.

    The margin velocity has the form [0, -(pi/2)*speed, 0], which drives
    all DFC cells southward (decreasing elevation) at a rate proportional
    to the EVL speed parameter.

    Attributes:
        embryo_radius: Radius of the embryo sphere (spatial units).
        num_dfcs: Default number of DFC cells.
        radial_size: Default angular cell radius (radians).
        num_vertices: Default contour discretization.
        margin_velocity: Current EVL velocity [dAz, dEl, dR].
        az_range: Azimuth bounds for DFC placement.
        el_range: Elevation bounds for DFC placement.
        noise_std: Noise amplitude parameter for cell migration.
        step_count: Number of simulation steps completed.
    """

    def __init__(self, config: dict | None = None):
        """Create the environment from a configuration dictionary.

        All parameters have sensible defaults for zebrafish embryo
        simulation.  The EVL speed of 1/200 produces ~300 steps of
        migration from the animal to vegetal pole.

        Args:
            config: Optional dictionary.  Recognized keys:
                ``embryo_radius`` -- Sphere radius in spatial units (default 1000).
                ``num_dfcs`` -- Number of DFC cells to initialize (default 24).
                ``radial_size`` -- Angular radius per cell in radians (default pi/64).
                ``num_vertices`` -- Contour discretization per cell (default 100).
                ``evl_speed`` -- EVL margin angular velocity (default 1/200).
                ``min_azimuth``, ``max_azimuth`` -- Azimuth placement bounds.
                ``min_elevation``, ``max_elevation`` -- Elevation placement bounds.
                ``noise_std`` -- Migration noise standard deviation (default 0.5).
        """
        config = config or {}

        # Embryo geometry
        self.embryo_radius: float = config.get("embryo_radius", 1000)

        # Cell population defaults
        self.num_dfcs: int = config.get("num_dfcs", 24)
        self.radial_size: float = config.get("radial_size", np.pi / 64)
        self.num_vertices: int = config.get("num_vertices", 100)

        # EVL margin velocity [azimuth, elevation, radius]
        # The pi/2 scaling converts the speed parameter to radians per step
        evl_speed = config.get("evl_speed", 1.0 / 200.0)
        self.margin_velocity = np.array([0, -(np.pi / 2) * evl_speed, 0])

        # DFC placement region on the sphere
        self.az_range = (
            config.get("min_azimuth", -3 * np.pi / 4),
            config.get("max_azimuth", -np.pi / 2),
        )
        self.el_range = (
            config.get("min_elevation", 0),
            config.get("max_elevation", np.pi / 4),
        )

        # Noise amplitude for stochastic cell migration
        self.noise_std: float = config.get("noise_std", 0.5)

        # Simulation clock
        self.step_count: int = 0

    def update(self):
        """Advance the environment by one time step.

        Currently only increments the step counter.  Future extensions
        could model time-varying EVL speed or environmental gradients.
        """
        self.step_count += 1

    def get_state(self) -> dict:
        """Return a JSON-serializable snapshot of the environment.

        Used by the REST API and WebSocket to communicate current
        environment parameters to the frontend.

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
