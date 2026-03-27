# Development History

## v2.2.0 (2026-03-26) -- Spherical Mechanics Rewrite

### Critical Fix: Cartesian Collision Resolution

**Problem**: v2.1 resolved collisions in AER (azimuth, elevation) space by pushing cells with equal angular increments. The AER metric is non-uniform:

```
ds² = R²(dθ² + cos²(θ)·dφ²)
```

An azimuth increment Δφ produces physical arc length R·cos(θ)·Δφ, which varies with latitude:
- Equator (θ=0): full arc length
- 60 latitude: half arc length
- Pole (θ=90): zero arc length (singularity)

This caused cells near the poles to barely separate during collision resolution.

**Solution**: Collisions are now resolved in Cartesian 3D space:

```
1. direction = normalize(xyz_i - xyz_j)     [3D push direction]
2. tangent = direction - (direction·n_hat)·n_hat    [project to tangent plane]
3. xyz_new = xyz + push · tangent/|tangent|  [move in tangent plane]
4. xyz_new = R · normalize(xyz_new)          [project back to sphere]
5. (phi,theta,R) = cart2sph(xyz_new)         [convert to AER]
```

Compact form:
```
xyz_new = R · normalize(xyz + push · tangent)
```

This gives physically correct, latitude-independent separation distances.

**Also applied to**: Differential adhesion forces, which suffered from the same metric distortion.

> See `docs/diagrams/architecture.svg` for visual reference.

### New: EVL-DFC Elastic Spring Coupling

**Problem**: v2.1 gave all DFC cells the same constant EVL velocity, regardless of their distance from the EVL margin. This doesn't match the biological mechanism where DFCs maintain elastic apical attachments to the EVL.

**Solution**: Per-cell elastic coupling with exponential distance decay:

```
F = k · d · exp(-d/λ)
```

where:
- k = spring constant (stiffness of the attachment)
- d = el_cell - el_EVL (elevation difference)
- λ = 0.3 rad (attachment decay length)

This creates a biologically realistic gradient where:
- **Leader cells** (closest to EVL margin): strong pull, fast migration
- **Follower cells** (further from EVL): weak pull, lag behind
- **Detached cells** (below EVL margin): no pull

**Physical basis**: DFCs maintain TJ-enriched apical attachments to the EVL (Ablooglu et al., eLife 2021). The elastic tether transmits epiboly forces, with attachment probability decreasing with distance.

### New: Cluster Cohesion Metrics

Added real-time quantification of DFC cluster state:

**Centroid**: Mean position of all active cells
```
C = (1/N) Σᵢ (φᵢ, θᵢ)
```

**Spread**: RMS angular distance from centroid (compactness)
```
σ = √(mean(d²)) = √[(1/N) Σᵢ ((φᵢ-C_φ)² + (θᵢ-C_θ)²)]
```

**Elongation**: Ratio of principal axes from covariance eigenvalues
```
e = √(λ_max / λ_min)    where λ = eigenvalues of Cov(φ,θ)
```

- Isotropic cluster: e ~ 1
- Elongated cluster: e >> 1 (indicates streaming migration)
- Increasing spread: cluster fragmenting
- Decreasing spread: cluster converging

### Architecture (v2.2)

```
Per-cell update:
  1. Compute EVL coupling force F = k·d·exp(-d/λ)
  2. Combine: v_eff = v_EVL + F_coupling
  3. Persistent random walk: v += bias + noise
  4. Advance deformation phases

Collective interactions:
  5. Collision resolution (Cartesian tangent push)
  6. Differential adhesion (Cartesian tangent pull)
  7. Compute cluster metrics (centroid, spread, elongation)
```

---

## v2.1.0 (2026-03-26)

### Algorithmic Improvements

#### Great-Circle Collision Detection (Bug Fix)
Replaced flat angular distance approximation with the Haversine formula:

```
d = 2·arcsin(√(sin²(Δφ/2) + cos(φ₁)·cos(φ₂)·sin²(Δλ/2)))
```

This provides exact geodesic distance on the sphere, correcting errors
near poles and at large angular separations.

#### Persistent Random Walk Migration
Cells maintain directional bias for τ ∈ [8, 25] steps before stochastic
reorientation, modeling filopodial persistence:

```
v = v_EVL + α · (cos(θ_bias), sin(θ_bias)) + σ · ξ
```

Compact form:
```
v = v_EVL + α · bias + σ · ξ
```

where α = 0.3 * |v_EVL| and ξ ~ N(0, 1).

#### Differential Adhesion (Steinberg, 1963)
Cell-cell adhesion follows:

```
F_adh = s · (d - d_contact) / (d_max - d_contact) · d_hat
```

for d_contact < d < d_max, creating cohesive cell clusters.

#### Dynamic Cell Deformation (Fourier Modes)
Cell contours are perturbed by low-frequency Fourier modes k = 2,3,4,5:

```
R(θ) = R_base · (1 + ε · Σ_k cos(k·θ + φ_k(t)))
```

with time-varying phases φ_k(t) creating membrane fluctuations.

### Frontend Improvements
- Help modal with interactive usage guide
- Tooltips on all parameter controls
- Section-level expandable help text

---

## v2.0.0 (2026-03-26) -- Python/Web Rewrite

Complete rewrite of the simulation platform from MATLAB to a modern Python web stack.

### Major Changes

- **Backend:** Rebuilt in Python using FastAPI as the web framework and NumPy for numerical computation. The simulation engine runs server-side and exposes both REST endpoints and a WebSocket interface.
- **Frontend:** Replaced MATLAB's GUIDE-based GUI with a browser-based single-page application using Three.js for hardware-accelerated 3D rendering. OrbitControls provide intuitive mouse-based rotation, panning, and zooming.
- **Real-time streaming:** Introduced WebSocket-based state streaming. The server pushes simulation snapshots at configurable intervals, enabling smooth animation of cell migration.
- **Dark theme UI:** Designed a modern dark interface with a blue accent color scheme, a right-side parameter panel, and a full-width 3D viewport.
- **Comprehensive test suite:** Added 23 unit and integration tests covering cell creation, coordinate conversion, collision detection and resolution, simulation stepping, state serialization, geometry utilities, and boundary conditions.
- **Modular architecture:** Separated concerns into distinct modules: cell model, population layer, EVL kinematic model, environment parameters, collision solver, and geometry utilities. This makes it straightforward to extend or replace individual components.
- **Configurable parameters:** All simulation parameters (embryo radius, cell count, radial size, EVL speed, noise amplitude, step interval) are exposed through both the REST API and the browser UI.
- **Coordinate system formalized:** Adopted an explicit AER (Azimuth-Elevation-Radius) convention with documented conversion formulas and batch-processing utilities.

### Technical Stack

- Python 3.11+, FastAPI, Uvicorn, NumPy, SciPy, Pydantic
- Three.js r128 (loaded from CDN), vanilla JavaScript, HTML5, CSS3
- Communication via REST (JSON) and WebSocket (JSON streaming)

> See `docs/diagrams/architecture.svg` and `docs/diagrams/cell_model.svg` for visual reference.

---

## v1.x (2013-2014) -- Original MATLAB Implementation [Legacy]

The first version of this simulation was developed as a MATLAB project at the SCIAN laboratory. It was used for exploratory research on DFC collective migration patterns.

### Features

- Simulation of DFC cells as circular contours on a spherical surface using MATLAB arrays.
- 3D visualization using MATLAB's `surf` and `plot3` functions for rendering the embryo sphere and cell positions.
- Graphical user interface built with MATLAB GUIDE, providing sliders and buttons for parameter control.
- Basic collision detection between cell pairs.
- Manual stepping and plotting -- no real-time animation.

### Limitations That Motivated the Rewrite

- **License dependency.** Running the simulation required a MATLAB license, limiting accessibility for collaborators and students.
- **Rendering constraints.** MATLAB's 3D plotting is not designed for real-time interactive visualization. Rotating the view or updating cell positions required explicit redraws that were slow and visually jarring.
- **No network interface.** The MATLAB GUI was purely local. There was no way to share a running simulation or build alternative clients.
- **Monolithic code.** The original implementation mixed simulation logic, GUI callbacks, and plotting code in a small number of large files, making it difficult to test or extend.
- **No automated tests.** The MATLAB version had no test suite; correctness was verified visually.

### Preserved Legacy Code

The original MATLAB scripts and GUIDE `.fig`/`.m` files are preserved in the `legacy/` directory for reference. They are not required to run the current version of the application.

---

## Roadmap

Potential future enhancements under consideration:

- **Cell adhesion model.** Add attractive forces between neighboring DFCs to better capture cluster cohesion.
- **Variable EVL speed.** Model epiboly deceleration as the margin approaches the vegetal pole.
- **Cell fate tracking.** Record migration trajectories and export them for quantitative analysis.
- **Parameter sweeps.** Batch mode for running many simulations with different parameter combinations and collecting statistics.
- **Comparison with experimental data.** Overlay tracked DFC positions from live-imaging experiments onto the simulated sphere for visual comparison.
