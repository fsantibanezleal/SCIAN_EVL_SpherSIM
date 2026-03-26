"""
DFC Layer -- population of Deep Forming Cells on the embryo sphere.

Manages a collection of DFC cells, handling initialization in a grid
pattern, collective migration with persistent random walks, inter-cell
collision detection and resolution, and differential adhesion.

The DFC population migrates collectively during zebrafish epiboly,
eventually converging to form Kupffer's vesicle (the left-right
organizer).  The layer model captures three key biological behaviors:

1. **Collective drift**: All cells are dragged by the EVL margin
2. **Individual exploration**: Each cell performs a persistent random walk
3. **Cohesion**: Adhesion forces keep the cluster from dispersing

References:
    - Oteiza et al. (2015), Cell collectivity regulation
    - Keller et al. (bioRxiv 2025), Modeling epithelial morphogenesis
    - Steinberg, M.S. (1963), Differential adhesion hypothesis
"""

import numpy as np

from .cell_dfc import CellDFC
from .collision import solve_collisions


class DFCLayer:
    """Manages the full population of DFC cells.

    Provides methods to initialize a grid arrangement, advance the
    simulation by one time step (with noise, collisions, and adhesion),
    and serialize the current state for the frontend.

    Attributes:
        config: Dictionary of simulation parameters.
        cells: List of CellDFC instances.
        step_count: Number of simulation steps completed.
        adhesion_enabled: Whether cell-cell adhesion forces are active.
        adhesion_strength: Magnitude of adhesion force (radians/step).
    """

    def __init__(self, config: dict):
        """Create a DFC layer from a configuration dictionary.

        Args:
            config: Dictionary with recognized keys:
                ``noise_std`` -- Noise amplitude for cell migration.
                ``adhesion_enabled`` -- Enable/disable adhesion (default True).
                ``adhesion_strength`` -- Adhesion force magnitude (default 0.001).
        """
        self.config = config
        self.cells: list[CellDFC] = []
        self.step_count = 0

        # Adhesion parameters with sensible defaults
        self.adhesion_enabled = config.get("adhesion_enabled", True)
        self.adhesion_strength = config.get("adhesion_strength", 0.001)

    def initialize(
        self,
        embryo_radius: float,
        num_cells: int = 24,
        radial_size: float | None = None,
        num_vertices: int = 100,
        az_range: tuple[float, float] | None = None,
        el_range: tuple[float, float] | None = None,
    ):
        """Initialize DFC cells in a grid pattern on the sphere.

        Cells are placed on a rectangular grid in (azimuth, elevation)
        space, packed as tightly as possible given their angular size.
        The grid dimensions are computed to fill the placement region
        as uniformly as possible.

        Args:
            embryo_radius: Radius of the embryo sphere (spatial units).
            num_cells: Total number of cells to create.
            radial_size: Angular radius of each cell (radians).  Defaults
                to pi/64 (~0.049 rad).
            num_vertices: Contour discretization per cell.
            az_range: (min_az, max_az) azimuth bounds for placement.
            el_range: (min_el, max_el) elevation bounds for placement.
        """
        if radial_size is None:
            radial_size = np.pi / 64
        if az_range is None:
            az_range = (-3 * np.pi / 4, -np.pi / 2)
        if el_range is None:
            el_range = (0, np.pi / 4)

        self.cells = []
        spacing = 2 * radial_size  # minimum center-to-center distance

        # Determine grid dimensions to approximately fill the region
        az_span = az_range[1] - az_range[0]
        el_span = el_range[1] - el_range[0]
        cols = max(1, int(np.sqrt(num_cells * az_span / (el_span + 1e-10))))
        rows = int(np.ceil(num_cells / cols))

        count = 0
        for row in range(rows):
            for col in range(cols):
                if count >= num_cells:
                    break

                # Place cell at grid position with offset from boundary
                az = az_range[0] + radial_size + col * spacing
                el = el_range[1] - radial_size - row * spacing

                # Only place if within bounds
                if az_range[0] <= az <= az_range[1] and el_range[0] <= el <= el_range[1]:
                    cell = CellDFC(
                        azimuth=az,
                        elevation=el,
                        radius=embryo_radius,
                        radial_size=radial_size,
                        num_vertices=num_vertices,
                    )
                    self.cells.append(cell)
                    count += 1

    def update(self, margin_velocity: np.ndarray):
        """Advance all cells by one time step.

        The update sequence is:
        1. Each active cell integrates the base margin velocity plus its
           persistent random walk and noise components.
        2. Pairwise collisions are resolved (cells pushed apart).
        3. Differential adhesion is applied (cells pulled together if
           within adhesion range but not overlapping).

        Args:
            margin_velocity: Base velocity [dAz, dEl, dR] from the EVL
                margin model.
        """
        noise_std = self.config.get("noise_std", 0.5)

        # Step 1: Individual cell updates (persistent random walk)
        for cell in self.cells:
            if cell.active:
                cell.update(margin_velocity, noise_std=noise_std)

        # Step 2 & 3: Collision resolution and adhesion
        solve_collisions(
            self.cells,
            adhesion_enabled=self.adhesion_enabled,
            adhesion_strength=self.adhesion_strength,
        )
        self.step_count += 1

    def get_state(self) -> dict:
        """Return a JSON-serializable snapshot of the layer.

        Includes aggregate statistics and per-cell state dictionaries
        for the frontend renderer.

        Returns:
            Dictionary with step count, number of active cells, and a
            list of per-cell state dictionaries.
        """
        return {
            "step": self.step_count,
            "num_cells": len([c for c in self.cells if c.active]),
            "cells": [c.get_state() for c in self.cells if c.active],
        }
