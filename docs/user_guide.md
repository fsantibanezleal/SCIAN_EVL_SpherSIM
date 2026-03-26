# User Guide

## Prerequisites

Before running the application, ensure you have the following installed:

- **Python 3.11 or later.** You can check your version with `python --version`. Download from https://www.python.org/ if needed.
- **A modern web browser** with WebGL support (Chrome, Firefox, Edge, or Safari). Most browsers released after 2020 work fine.
- **Git** (optional, for cloning the repository).

No MATLAB installation is required. The legacy MATLAB code in `legacy/` is preserved for historical reference only.

## Installation

### 1. Obtain the Source Code

Clone the repository or download and extract the ZIP archive:

```bash
git clone <repository-url> SCIAN_EVL_SpherSIM
cd SCIAN_EVL_SpherSIM
```

### 2. Create a Virtual Environment

It is strongly recommended to use a Python virtual environment to isolate dependencies:

```bash
python -m venv .venv
```

### 3. Activate the Virtual Environment

On **Windows** (Command Prompt or Git Bash):

```bash
source .venv/Scripts/activate
```

On **macOS / Linux**:

```bash
source .venv/bin/activate
```

Your terminal prompt should now show `(.venv)` to confirm the environment is active.

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs FastAPI, Uvicorn, NumPy, SciPy, Pydantic, and their transitive dependencies. The full list is pinned in `requirements.txt` for reproducibility.

## Running the Application

Start the FastAPI server with Uvicorn:

```bash
python -m uvicorn app.main:app --reload --port 8002
```

- `--reload` enables automatic reloading when source files change (useful during development; omit for production).
- `--port 8002` sets the listening port. Change this if 8002 is already in use on your machine.

Once the server starts, open your browser and navigate to:

```
http://localhost:8002
```

You should see the dark-themed interface with a 3D viewport on the left and a controls panel on the right.

## Using the Interface

### Simulation Controls

The top of the right-side panel has four buttons:

| Button | Action |
|---|---|
| **Init** | Creates a new simulation using the current parameter values. Any previous simulation state is discarded. You must click Init before Play or Step. |
| **Play** | Starts continuous simulation stepping. The server advances the simulation at the configured step interval and streams the state to the browser over WebSocket. |
| **Pause** | Stops continuous stepping. The current state is preserved; you can resume with Play or advance manually with Step. |
| **Step** | Advances the simulation by exactly one time step. Useful for frame-by-frame inspection of cell movements. |

### Parameter Panel

Below the control buttons, you can adjust the following parameters before clicking **Init**:

| Parameter | Description | Default | Units |
|---|---|---|---|
| **Embryo Radius** | Radius of the spherical embryo. Larger values spread cells out more in 3D space. | 1000 | spatial units |
| **Number of DFCs** | How many DFC cells to create in the initial grid. | 24 | cells |
| **Cell Radial Size** | Angular half-width of each cell contour. Controls how large cells appear on the sphere surface. | 0.049 (~pi/64) | radians |
| **Contour Vertices** | Number of points used to discretize each cell boundary. Higher values give smoother circles but cost more to render. | 100 | vertices |
| **EVL Speed** | Angular velocity of the EVL margin. Higher values make cells migrate faster toward the vegetal pole. | 0.005 | radians/step |
| **Noise Std** | Amplitude of the Gaussian noise added to cell velocities. Zero means perfectly deterministic motion; higher values produce more scattered trajectories. | 0.5 | dimensionless |
| **Step Interval** | Time between WebSocket updates in milliseconds. Lower values give smoother animation but increase CPU and network load. | 50 | ms |

After changing parameters, you must click **Init** again for the changes to take effect.

### View Options

Below the parameters, three checkboxes control the 3D rendering:

- **Wireframe sphere** -- Toggles a wireframe mesh overlay on the embryo, making it easier to see the sphere's curvature and the cells' positions relative to latitude/longitude lines.
- **Show axes** -- Toggles an XYZ axis helper at the origin. Red = X, Green = Y, Blue = Z.
- **Show cell centers** -- Toggles small white spheres at each cell's center position. Useful for tracking individual cells when contours overlap.

### 3D Navigation

The viewport supports standard Three.js OrbitControls:

| Action | Mouse Gesture |
|---|---|
| **Rotate** | Left-click and drag |
| **Pan** | Right-click and drag |
| **Zoom** | Scroll wheel up/down |

You can also use touch gestures on mobile devices (one finger to rotate, two fingers to pan/pinch to zoom).

## Running the Tests

The project includes 23 tests organized into three test files. Run them from the project root:

```bash
python tests/test_cell.py
python tests/test_collision.py
python tests/test_simulation.py
```

Each file prints `[PASS]` for every passing test and a summary at the end. If any test fails, it will raise an `AssertionError` with a descriptive message.

### What the Tests Cover

- **`test_cell.py`** (10 tests): Cell creation, Cartesian position on sphere, contour shape and radius, position update, azimuth wrapping, elevation clamping, inactive cell behavior, state serialization, and coordinate round-trip conversion.
- **`test_collision.py`** (7 tests): Angular distance computation, overlap detection, push-apart resolution, symmetric displacement, inactive cell exclusion, and multi-cell scenarios.
- **`test_simulation.py`** (6 tests): Full 50-step simulation pipeline, state serialization structure, batch coordinate conversion, great-circle distance, sphere mesh generation, and cell initialization bounds.

## Typical Workflow

1. **Start the server** with `python -m uvicorn app.main:app --reload --port 8002`.
2. **Open the browser** at `http://localhost:8002`.
3. **Adjust parameters** in the right panel (e.g., increase DFC count to 30, reduce noise to 0.2).
4. **Click Init** to create the simulation.
5. **Click Play** to watch cells migrate in real time.
6. **Rotate the view** by dragging with the left mouse button to examine the sphere from different angles.
7. **Click Pause** at any time to freeze the simulation.
8. **Click Step** repeatedly for frame-by-frame analysis of cell positions.
9. **Re-initialize** with different parameters by adjusting values and clicking Init again.

## Troubleshooting

| Problem | Solution |
|---|---|
| **Port 8002 already in use** | Change the port: `--port 8003` or any available port. |
| **Browser shows blank page** | Check the terminal for server errors. Ensure `app/static/index.html` exists. |
| **Cells do not move** | Make sure you clicked **Init** before **Play**. Check that EVL Speed is not zero. |
| **WebSocket disconnects** | The client auto-reconnects. If it keeps disconnecting, check the terminal for Python errors. |
| **Import errors when running tests** | Make sure you are running from the project root directory (`SCIAN_EVL_SpherSIM/`). |
| **`ModuleNotFoundError: No module named 'app'`** | Ensure the virtual environment is activated and dependencies are installed. |

## Stopping the Server

Press `Ctrl+C` in the terminal where Uvicorn is running. The server will shut down gracefully.
