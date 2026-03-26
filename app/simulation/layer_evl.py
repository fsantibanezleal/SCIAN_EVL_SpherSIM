"""
EVL (Enveloping Layer) margin model.

The EVL is the outermost cell layer of the zebrafish embryo.  During
epiboly, the EVL margin advances vegetally (toward the south pole),
dragging the DFC cluster with it.

This module provides a simple kinematic model of the EVL margin as a
latitude line that moves at a configurable angular speed.

References:
    - Compagnon & Bhatt (2019), Mechanisms of zebrafish epiboly
    - Rho et al. (2009), Zebrafish epiboly: mechanics and mechanisms
"""

import numpy as np


class EVLMargin:
    """Kinematic model of the EVL margin latitude.

    The margin starts at a given elevation and moves southward at a
    constant angular speed each time step.

    Attributes:
        elevation: Current elevation of the margin (radians).
        speed: Angular velocity of the margin (radians / step).
        min_elevation: Lower bound; margin stops here.
    """

    def __init__(self, config: dict | None = None):
        """Initialize the EVL margin.

        Args:
            config: Optional dictionary with ``evl_start_elevation``,
                ``evl_speed``, and ``evl_min_elevation`` keys.
        """
        config = config or {}
        self.elevation = config.get("evl_start_elevation", np.pi / 4)
        self.speed = config.get("evl_speed", 1.0 / 200.0)
        self.min_elevation = config.get("evl_min_elevation", -np.pi / 2)

    def update(self):
        """Advance the margin by one time step."""
        self.elevation = max(
            self.min_elevation,
            self.elevation - (np.pi / 2) * self.speed,
        )

    def get_velocity(self) -> np.ndarray:
        """Return the velocity vector [dAz, dEl, dR] induced by the margin."""
        return np.array([0.0, -(np.pi / 2) * self.speed, 0.0])

    def get_state(self) -> dict:
        """Return a JSON-serializable snapshot."""
        return {
            "elevation": self.elevation,
            "speed": self.speed,
        }
