# Development History

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
