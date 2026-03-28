"""
DFC Layer -- population of Deep Forming Cells on the embryo sphere.

Manages a collection of DFC cells, handling initialization in a grid
pattern, collective migration with persistent random walks, inter-cell
collision detection and resolution, and differential adhesion.

The DFC population migrates collectively during zebrafish epiboly,
eventually converging to form Kupffer's vesicle (the left-right
organizer).  The layer model captures four key biological behaviors:

1. **EVL elastic coupling**: Each DFC maintains apical attachments to
   the EVL margin via tight junctions, creating spring-like tethers
   whose strength decays with distance (Ablooglu et al., eLife 2021).
2. **Collective drift**: The EVL margin drags the cluster vegetalward.
3. **Individual exploration**: Each cell performs a persistent random walk.
4. **Cohesion**: Adhesion forces keep the cluster from dispersing.

References:
    - Oteiza et al. (2015), Cell collectivity regulation
    - Ablooglu et al. (eLife 2021), DFC apical contacts and dragging
    - Keller et al. (bioRxiv 2025), Modeling epithelial morphogenesis
    - Steinberg, M.S. (1963), Differential adhesion hypothesis
"""

import numpy as np

from .cell_dfc import CellDFC
from .collision import solve_collisions


class DFCLayer:
    """Manages the full population of DFC cells.

    Provides methods to initialize a grid arrangement, advance the
    simulation by one time step (with noise, collisions, adhesion,
    and EVL coupling), and serialize the current state for the frontend.

    Attributes:
        config: Dictionary of simulation parameters.
        cells: List of CellDFC instances.
        step_count: Number of simulation steps completed.
        adhesion_enabled: Whether cell-cell adhesion forces are active.
        adhesion_strength: Magnitude of adhesion force (radians/step).
        spring_constant: Elastic coupling strength to EVL margin.
    """

    def __init__(self, config: dict):
        """Create a DFC layer from a configuration dictionary.

        Args:
            config: Dictionary with recognized keys:
                ``noise_std`` -- Noise amplitude for cell migration.
                ``adhesion_enabled`` -- Enable/disable adhesion (default True).
                ``adhesion_strength`` -- Adhesion force magnitude (default 0.001).
                ``spring_constant`` -- EVL coupling spring stiffness (default 0.01).
        """
        self.config = config
        self.cells: list[CellDFC] = []
        self.step_count = 0

        # Adhesion parameters with sensible defaults
        self.adhesion_enabled = config.get("adhesion_enabled", True)
        self.adhesion_strength = config.get("adhesion_strength", 0.001)
        self.spring_constant = config.get("spring_constant", 0.01)

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

    def _compute_evl_coupling_force(self, cell, evl_elevation, spring_constant=0.01):
        """Compute elastic coupling force between a DFC and the EVL margin.

        ===== BIOLOGICAL MODEL =====

        DFCs maintain tight junction-enriched apical attachments to the EVL
        (Ablooglu et al., eLife 2021). These act as elastic tethers:

            F_EVL = k * (el_EVL - el_cell)    (when el_cell > el_EVL)

        where:
            k       = spring constant (stiffness of the attachment)
            el_EVL  = current EVL margin elevation
            el_cell = cell elevation

        The force is attractive (pulls cell toward EVL) and proportional
        to the distance. Cells far from the EVL feel weaker coupling,
        modeling the observation that leader cells at the cluster front
        have stronger attachments than follower cells.

        Cells below the EVL margin (el_cell < el_EVL) are not pulled
        upward -- the EVL only drags, it doesn't push.

        Args:
            cell: CellDFC instance.
            evl_elevation: Current EVL margin elevation (radians).
            spring_constant: Elastic coupling strength.

        Returns:
            Velocity contribution [dAz, dEl, dR] from EVL coupling.
        """
        vel = np.zeros(3)

        # Distance from cell to EVL margin (in elevation)
        distance_to_evl = cell.center_aer[1] - evl_elevation

        if distance_to_evl > 0:
            # Cell is above EVL margin: pull downward (toward EVL)
            # Force decays with distance (exponential attachment probability)
            coupling = spring_constant * distance_to_evl * np.exp(-distance_to_evl / 0.3)
            vel[1] = -coupling

        return vel

    def _check_division(self, division_rate=0.005):
        """Stochastic cell division on the sphere surface.

        Each cell has a small probability per step of dividing.
        Division axis is perpendicular to the cluster migration
        direction (approximated by the EVL velocity direction).

        Daughter cells are placed along the division axis at
        +/-0.6*radial_size from the parent, with slightly smaller
        radial size (0.85x) to conserve approximate area.
        """
        new_cells = []
        for cell in self.cells:
            if not cell.active:
                continue
            if np.random.random() > division_rate:
                continue
            if len(self.cells) + len(new_cells) >= 60:  # max cells
                break

            # Division axis: perpendicular to elevation (along azimuth)
            div_offset = cell.radial_size * 0.6
            daughter_size = cell.radial_size * 0.85

            # Daughter 1: offset in +azimuth
            d1 = CellDFC(
                azimuth=cell.center_aer[0] + div_offset,
                elevation=cell.center_aer[1],
                radius=cell.center_aer[2],
                radial_size=daughter_size,
                num_vertices=cell.num_vertices,
            )
            # Daughter 2: offset in -azimuth
            d2 = CellDFC(
                azimuth=cell.center_aer[0] - div_offset,
                elevation=cell.center_aer[1],
                radius=cell.center_aer[2],
                radial_size=daughter_size,
                num_vertices=cell.num_vertices,
            )

            cell.active = False  # Parent deactivated
            new_cells.extend([d1, d2])

        self.cells.extend(new_cells)
        # Remove inactive
        self.cells = [c for c in self.cells if c.active]

    def update(self, margin_velocity: np.ndarray, evl_elevation: float | None = None):
        """Update all DFC cells with EVL coupling and collective dynamics.

        ===== SIMULATION PIPELINE (PER STEP) =====

        For each active cell:
        1. Compute EVL coupling force (elastic spring to margin)
        2. Add collective velocity component (cluster cohesion)
        3. Apply persistent random walk + noise
        4. Resolve collisions and adhesion

        Args:
            margin_velocity: Base EVL margin velocity [dAz, dEl, dR].
            evl_elevation: Current EVL margin elevation (radians).
                If None, coupling forces are not applied (backward
                compatible with callers that do not track EVL position).
        """
        noise_std = self.config.get("noise_std", 0.5)

        for cell in self.cells:
            if not cell.active:
                continue

            # Base EVL drag (diminishing with distance)
            if evl_elevation is not None:
                evl_force = self._compute_evl_coupling_force(
                    cell, evl_elevation, spring_constant=self.spring_constant
                )
                effective_vel = margin_velocity.copy() + evl_force
            else:
                effective_vel = margin_velocity.copy()

            cell.update(effective_vel, noise_std=noise_std)

        # Collision resolution and adhesion
        solve_collisions(
            self.cells,
            adhesion_enabled=self.adhesion_enabled,
            adhesion_strength=self.adhesion_strength,
        )

        # Stochastic cell division (low probability per step)
        self._check_division(division_rate=self.config.get("division_rate", 0.005))

        self.step_count += 1

    def compute_cluster_metrics(self) -> dict:
        """Compute metrics characterizing the DFC cluster state.

        ===== METRICS =====

        Centroid: Mean position of all active cells in AER space.
            Indicates the cluster's bulk position on the embryo.

        Spread: RMS angular distance from the centroid.
            Measures cluster compactness. Increasing spread indicates
            fragmentation; decreasing spread indicates convergence.

        Elongation: Ratio of maximum to minimum spread along principal axes.
            Isotropic cluster -> elongation ~ 1
            Elongated cluster -> elongation >> 1

        Returns:
            Dictionary with 'centroid_aer', 'spread', 'elongation', 'num_active'.
        """
        active = [c for c in self.cells if c.active]
        if len(active) == 0:
            return {'centroid_aer': [0, 0, 0], 'spread': 0, 'elongation': 1, 'num_active': 0}

        # Centroid in AER
        positions = np.array([c.center_aer for c in active])
        centroid = np.mean(positions, axis=0)

        # Spread: RMS angular distance from centroid
        deltas = positions[:, :2] - centroid[:2]
        distances_sq = deltas[:, 0]**2 + deltas[:, 1]**2
        spread = float(np.sqrt(np.mean(distances_sq)))

        # Elongation via eigenvalues of covariance matrix
        if len(active) > 2:
            cov = np.cov(deltas.T)
            eigenvalues = np.linalg.eigvalsh(cov)
            eigenvalues = np.maximum(eigenvalues, 1e-10)
            elongation = float(np.sqrt(eigenvalues[-1] / eigenvalues[0]))
        else:
            elongation = 1.0

        return {
            'centroid_aer': centroid.tolist(),
            'spread': spread,
            'elongation': elongation,
            'num_active': len(active),
        }

    def get_state(self) -> dict:
        """Return a JSON-serializable snapshot of the layer.

        Includes aggregate statistics, cluster metrics, and per-cell
        state dictionaries for the frontend renderer.

        Returns:
            Dictionary with step count, cluster metrics, and a list
            of per-cell state dictionaries.
        """
        metrics = self.compute_cluster_metrics()
        return {
            "cells": [c.get_state() for c in self.cells if c.active],
            "step": self.step_count,
            "num_cells": metrics['num_active'],
            "cluster_spread": metrics['spread'],
            "cluster_elongation": metrics['elongation'],
            "cluster_centroid": metrics['centroid_aer'],
        }
