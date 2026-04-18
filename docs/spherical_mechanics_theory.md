# Spherical Mechanics Theory

This document is the deep technical reference for the mathematics and physics behind the SCIAN EVL SpherSIM simulator. It is intended as a standalone reference: each section defines the problem, derives the relevant equation, explains each variable, and states its physical or numerical interpretation. For higher-level biology see [biological_model.md](biological_model.md) and [epiboly_biology.md](epiboly_biology.md); for the software architecture see [architecture.md](architecture.md).

---

## 1. Coordinate System (AER)

All cell positions are stored in **AER** (Azimuth, Elevation, Radius) spherical coordinates. For a sphere of radius `R`:

```
x = R * cos(el) * cos(az)
y = R * cos(el) * sin(az)
z = R * sin(el)
```

| Symbol | Meaning | Range | Unit |
|---|---|---|---|
| `az` | Longitude around the vertical (Z) axis | `[-pi, pi]` | rad |
| `el` | Latitude from the equatorial plane | `[-pi/2, +pi/2]` | rad |
| `R` | Distance from sphere center | `R_embryo` | spatial units |

**Why AER?** The DFC cluster is a narrow patch on the dorsal side. Azimuth/elevation map naturally to "east-west" and "north-south" displacements that match how experimentalists describe epiboly. Radius is a nuisance coordinate held constant.

**Periodic boundary.** Azimuth wraps: after each integration step we renormalize `az <- ((az + pi) mod 2*pi) - pi` so the seam at the anti-meridian is invisible to the dynamics.

**Clamped boundary.** Elevation is clamped to `[-pi/2 + eps, +pi/2 - eps]`. Cells do not pass through the poles because the azimuthal coordinate becomes singular there.

---

## 2. The Spherical Metric and Why Flat Geometry Fails

On a sphere of radius `R`, the infinitesimal arc length is

```
ds^2 = R^2 * (d_el^2 + cos^2(el) * d_az^2)
```

| Symbol | Meaning |
|---|---|
| `ds` | Physical arc length on the surface |
| `d_el`, `d_az` | Small coordinate increments |
| `cos^2(el)` | Metric coefficient that shrinks azimuthal distances near the poles |

**Interpretation.** An azimuth increment `d_az` covers a physical distance `R * cos(el) * d_az`, which varies with latitude:

| Latitude `el` | `cos(el)` | Physical length of `d_az = 0.1` |
|---|---|---|
| 0 (equator) | 1.0 | `0.1 * R` |
| 60 degrees | 0.5 | `0.05 * R` |
| 80 degrees | 0.17 | `0.017 * R` |
| 90 degrees (pole) | 0.0 | 0 (singular) |

**Consequence for collisions.** A naive resolver that pushes two overlapping cells by equal `d_az` increments separates them by **half the physical distance** at 60 degrees latitude compared to the equator. Near the poles, they barely move apart at all. This is the bug that motivated the v2.2 Cartesian tangent-plane push (section 5).

---

## 3. Great-Circle (Haversine) Distance

The true geodesic distance between two points `(az_1, el_1)` and `(az_2, el_2)` on a unit sphere is

```
d_hav = 2 * arcsin( sqrt( sin^2((el_2 - el_1)/2)
                        + cos(el_1) * cos(el_2) * sin^2((az_2 - az_1)/2) ) )
```

| Symbol | Meaning | Unit |
|---|---|---|
| `d_hav` | Angular great-circle distance | rad |
| `el_i, az_i` | Cell centers in AER | rad |

**Physical distance** on a sphere of radius `R` is `R * d_hav`.

**Why not just `sqrt(d_az^2 + d_el^2)`?** The flat-space Pythagoras approximation:
- Over-estimates distance near the poles (because it ignores the `cos(el)` metric factor).
- Fails entirely for points on opposite sides of the sphere.
- Produces direction-dependent errors for cells separated by more than ~0.3 rad.

**Haversine is numerically stable** for small AND large separations because the outer `arcsin` avoids the `arccos(1 - small)` cancellation error that plagues the spherical law of cosines.

**Used in**: collision detection, cluster spread computation, EVL distance for elastic coupling.

---

## 4. EVL Kinematic Boundary

The EVL margin is not simulated as individual cells. It is a **kinematic line of latitude** moving toward the vegetal pole:

```
el_EVL(t) = el_EVL(0) + v_evl * t
```

with `v_evl > 0` in the standard convention where elevation decreases vegetalward; the sign flip is handled by the velocity vector `[0, -(pi/2) * evl_speed, 0]` applied to cells.

| Symbol | Meaning | Unit | Typical |
|---|---|---|---|
| `el_EVL(t)` | EVL margin latitude at time `t` | rad | starts near +0.8, moves toward 0 |
| `v_evl` | Angular migration speed of the EVL | rad/step | `0.005` |

**Why kinematic?** The EVL in real embryos is a large epithelial sheet with roughly uniform margin velocity at the time scale of DFC migration. Modelling it as thousands of individual cells would be wasteful for this study, and its bulk advance is the only force the DFCs actually feel from it. The simplification is a common choice in morphogenesis modelling.

---

## 5. Cartesian Tangent-Plane Collision Resolution

**Problem.** Section 2 showed that pushing cells apart in AER space produces latitude-dependent physical separations. The fix is to push in 3D Cartesian space along the local tangent plane.

**Algorithm.** For two overlapping cells `i` and `j` with 3D positions `p_i`, `p_j` on a sphere of radius `R`:

```
1. n_i     = p_i / R                                # outward normal at cell i
2. d_vec   = p_i - p_j                              # direction from j to i in 3D
3. d_tan   = d_vec - (d_vec . n_i) * n_i            # remove radial component
4. d_hat   = d_tan / ||d_tan||                      # unit tangent direction
5. p_i'    = p_i + (overlap/2) * d_hat              # push i outward
6. p_i''   = R * (p_i' / ||p_i'||)                  # re-project onto sphere
7. (az_i, el_i, R) = cart2sph(p_i'')                # return to AER
```

Cell `j` is pushed by the opposite direction with symmetric magnitude.

| Symbol | Meaning |
|---|---|
| `n_i` | Outward unit normal at cell `i` |
| `d_tan` | Separation vector projected onto the tangent plane at `i` |
| `overlap` | `(r_i + r_j) - d_hav` , the amount of penetration |
| `R` | Embryo radius, preserved by the final re-projection |

**Compact form**

```
p_i_new = R * normalize( p_i + (overlap/2) * d_tan / ||d_tan|| )
```

**Properties.**
- **Latitude-independent.** The push magnitude is measured in real 3D space, not in coordinate space.
- **Symmetry-preserving.** Equal-and-opposite displacements conserve the midpoint of the pair.
- **Manifold-preserving.** The final re-projection onto the sphere eliminates the tiny out-of-surface error from the tangential step.

This same projection pattern is used for differential adhesion forces, which suffered from the same metric distortion before v2.2.

---

## 6. EVL Elastic Coupling Force

Experiments (Ablooglu et al., 2021) show DFCs maintain **apical tight-junction attachments** to the EVL, acting as elastic tethers. Pull strength decays with distance from the EVL margin:

```
F_EVL = k * d * exp( -d / lambda )
```

| Symbol | Meaning | Unit | Default |
|---|---|---|---|
| `F_EVL` | Force magnitude on a DFC | same as `k * rad` | — |
| `k` | Spring constant | 1/step | tuned per run |
| `d` | `el_cell - el_EVL`, the elevation separation | rad | — |
| `lambda` | Attachment decay length | rad | `0.3` |

**Interpretation.**
- `d = 0` (cell at margin): force = 0 (no tether stretch).
- `d = lambda`: force = `k * lambda / e` ≈ 37% of peak, the characteristic attachment scale.
- `d >> lambda`: force → 0 (cells that have fallen behind detach from the EVL).
- `d < 0` (cell below margin): clipped to zero in the implementation (cells cannot be pushed backward by a downstream EVL).

**Biological consequence.** This generates the observed leader-follower pattern: cells closest to the EVL (small `d`) get pulled hardest and migrate fastest, while cells further from the margin (large `d`) lag — exactly matching live-imaging observations.

---

## 7. Persistent Random Walk

DFCs exhibit filopodial persistence: they commit to a direction for several steps before reorienting. The velocity update is

```
v = v_EVL + alpha * ( cos(theta_bias), sin(theta_bias) ) + sigma * xi
```

| Symbol | Meaning |
|---|---|
| `v_EVL` | Elastic coupling velocity (section 6) |
| `alpha` | Persistence amplitude, `0.3 * ||v_EVL||` |
| `theta_bias` | Current directional bias, held for `tau` steps |
| `tau` | Persistence time, drawn from `Uniform(8, 25)` |
| `sigma` | Gaussian noise standard deviation, user parameter |
| `xi ~ N(0, I_2)` | Uncorrelated 2D Gaussian |

Each time the persistence counter expires, a new `theta_bias` is drawn uniformly in `[0, 2*pi)` and a new `tau` is drawn. This produces trajectories with short-time ballistic motion and long-time diffusive motion — a Langevin-like process on the sphere.

---

## 8. Differential Adhesion

Following Steinberg (1963), cell-cell contact forces are modeled with a smooth attractive potential:

```
F_adh = s * (d - d_contact) / (d_max - d_contact) * d_hat    for d_contact < d < d_max
F_adh = 0                                                    otherwise
```

| Symbol | Meaning |
|---|---|
| `s` | Adhesion strength |
| `d` | Haversine distance between cell centers |
| `d_contact` | Distance below which collision repulsion takes over |
| `d_max` | Distance beyond which adhesion vanishes |
| `d_hat` | Unit vector from cell `i` to cell `j` on the tangent plane |

**Interpretation.** Cells in the interaction band `(d_contact, d_max)` feel a mild pull toward each other that is zero at `d_contact` and maximal at `d_max`. The effect is cluster cohesion: isolated cells drift back into the cluster instead of dispersing under stochastic noise.

Like collisions, adhesion forces are applied on the tangent plane (Cartesian, section 5) and re-projected, so the magnitude is latitude-independent.

---

## 9. Dynamic Contour Deformation (Fourier Modes)

To make the visualization biologically plausible, cell contours are perturbed by low-frequency Fourier modes:

```
R(theta, t) = R_base * ( 1 + epsilon * sum_{k=2..5} cos( k*theta + phi_k(t) ) )
```

| Symbol | Meaning |
|---|---|
| `R(theta, t)` | Instantaneous angular radius at contour parameter `theta` |
| `R_base` | Nominal cell radius (user parameter) |
| `epsilon` | Deformation amplitude (~0.05) |
| `k` | Mode number (2 = elliptic, 3 = triangular, 4 = quadrupolar, 5 = pentagonal) |
| `phi_k(t)` | Time-varying phase, `phi_k(t) = phi_k(0) + omega_k * t` |

**Purpose.** Purely cosmetic: rigid-circle cells look computer-generated. Fourier perturbation mimics membrane fluctuations without affecting the centroid dynamics (the deformation is volume-preserving to leading order in `epsilon`).

---

## 10. Cluster Cohesion Metrics

Real-time quantification of the DFC cluster state during simulation.

### 10.1 Centroid

```
C = (1/N) * sum_i (az_i, el_i)
```

where `N` is the number of active cells. This is a mean in coordinate space, which is a good approximation while the cluster is small compared to the embryo (the usual case for DFCs).

### 10.2 Spread (compactness)

```
sigma = sqrt( (1/N) * sum_i d_i^2 )
```

where `d_i` is the Haversine distance from cell `i` to the centroid `C`. Low `sigma` means a tight cluster; rising `sigma` signals fragmentation.

### 10.3 Elongation

```
elongation = sqrt( lambda_max / lambda_min )
```

where `lambda_max`, `lambda_min` are the two eigenvalues of the 2D covariance matrix of cell positions (projected onto the tangent plane at `C`):

```
Cov = (1/N) * sum_i (p_i - C)(p_i - C)^T
```

| Elongation | Shape |
|---|---|
| ≈ 1 | Isotropic (circular) cluster |
| ≈ 2 | Mildly stretched |
| > 3 | Strong streaming migration |

These metrics are exported in the CSV download and drive the right-panel status display.

---

## 11. Numerical Integration

The simulator uses **forward Euler integration** with a fixed tick `dt = 1 step`:

```
az(t+1) = az(t) + v_az(t)
el(t+1) = el(t) + v_el(t)
```

followed by wrap/clamp and collision/adhesion correction.

**Accuracy.** Forward Euler has `O(dt)` local error. Because `dt` is small relative to `lambda` (the slowest timescale in the EVL coupling) and because all forces are bounded, the global error over a typical 500-step run stays well below the cell radius. Higher-order integrators (RK4, symplectic) were considered and rejected: the stochastic term dominates the residual, so additional deterministic accuracy is wasted.

**Stability.** The combination of clamped elevation and bounded spring forces ensures no cell velocity can exceed `~2 * v_evl` per step under reasonable parameter choices.

---

## 12. Summary Table

| Equation | Purpose | Section |
|---|---|---|
| `ds^2 = R^2 (d_el^2 + cos^2(el) d_az^2)` | Spherical metric | 2 |
| `d_hav = 2 arcsin(sqrt(...))` | Great-circle distance | 3 |
| `p_new = R * normalize(p + push * tangent)` | Cartesian push | 5 |
| `F_EVL = k * d * exp(-d/lambda)` | EVL elastic coupling | 6 |
| `v = v_EVL + alpha*bias + sigma*xi` | Persistent random walk | 7 |
| `F_adh = s * (d - d_contact) / (d_max - d_contact)` | Differential adhesion | 8 |
| `R(theta,t) = R_base (1 + eps sum cos(k*theta + phi_k(t)))` | Contour deformation | 9 |
| `sigma = sqrt(mean(d^2))` | Cluster spread | 10 |
| `elongation = sqrt(lambda_max / lambda_min)` | Cluster elongation | 10 |

---

## References

The mathematical formulation here draws on:

- Vincenty, T. (1975). Direct and inverse solutions of geodesics on the ellipsoid. *Survey Review*, 23(176). -- Haversine and geodesic formulas.
- Steinberg, M. (1963). Reconstruction of tissues by dissociated cells. *Science*, 141(3579). -- Differential adhesion.
- Ablooglu et al. (2021). Apical contacts stemming from incomplete delamination. *eLife*, 10:e61495. -- EVL elastic coupling motivation.
- Rieu et al. (2000). Diffusion and deformations of single Hydra cells. *Biophysical Journal*, 79(4). -- Persistent random walk on surfaces.

For the full bibliography see [references.md](references.md).
