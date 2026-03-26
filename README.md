# SCIAN EVL SpherSIM

3D simulation of Deep Forming Cell (DFC) collective migration on a spherical zebrafish embryo surface during epiboly. Built with Python/FastAPI on the backend and Three.js for interactive browser-based 3D visualization.

DFCs are the precursor cells of Kupffer's vesicle, the zebrafish organ responsible for establishing left-right body asymmetry. This simulation models how DFCs are carried vegetalward by the advancing EVL (Enveloping Layer) margin, subject to stochastic noise and inter-cell collision constraints. The project is a complete rewrite of a legacy MATLAB implementation, designed for accessibility, real-time interactivity, and modularity.

## Architecture

![Architecture](docs/svg/architecture.svg)

The system consists of a FastAPI server that runs the simulation engine and a Three.js frontend that renders the results in real time. Communication happens over REST (for initialization and control) and WebSocket (for continuous state streaming during playback).

## Spherical Embryo Model

![Spherical Model](docs/svg/spherical_model.svg)

The embryo is modeled as a sphere. DFC cells are represented as circular contours on the sphere surface, tracked in AER (Azimuth-Elevation-Radius) coordinates. The EVL margin is a latitude line that moves steadily toward the vegetal pole, dragging the DFC cluster along with it.

## Application

![App](docs/svg/app_screenshot.svg)

The browser interface provides a 3D viewport with orbit controls (rotate, pan, zoom) and a right-side panel for simulation parameters and playback controls.

## Quick Start

```bash
cd SCIAN_EVL_SpherSIM
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt

# Run tests
python tests/test_cell.py
python tests/test_collision.py
python tests/test_simulation.py

# Start application
python -m uvicorn app.main:app --reload --port 8002
# Open http://localhost:8002
```

## Features

- Interactive 3D visualization of the embryo sphere and DFC cells using Three.js with WebGL
- Real-time simulation streaming via WebSocket at configurable tick intervals
- Configurable parameters: cell count, radial size, EVL speed, noise amplitude, and more
- Orbit controls for rotation, pan, and zoom with mouse or touch
- Play / Pause / Step controls for continuous or frame-by-frame simulation
- Wireframe overlay, axes helper, and cell center markers as toggleable view options
- Dark theme UI with blue accent color scheme
- Pairwise collision detection and symmetric resolution to prevent cell overlap
- AER coordinate system with automatic wrapping (azimuth) and clamping (elevation)
- 23 automated tests covering cells, collisions, geometry, and full simulation pipeline

## Project Structure

```
SCIAN_EVL_SpherSIM/
  app/
    main.py                   FastAPI application, REST + WebSocket endpoints
    simulation/
      cell_dfc.py             Individual DFC cell model (AER position, contour, update)
      layer_dfc.py            DFC population management (grid init, collective update)
      layer_evl.py            EVL margin kinematic model (latitude moves vegetalward)
      environment.py          Global parameters (radius, speed, bounds, noise)
      collision.py            Pairwise collision detection and resolution
      geometry.py             Coordinate conversions, great-circle distance, mesh generation
    api/
      routes.py               Reserved for future endpoint expansion
    static/
      index.html              Single-page application shell
      css/style.css           Dark theme stylesheet
      js/
        app.js                Orchestration: binds controls, renderer, WebSocket
        renderer3d.js         Three.js scene: sphere, contours, orbit controls
        controls.js           Parameter panel and status display
        websocket.js          WebSocket client with auto-reconnect
  tests/
    test_cell.py              10 tests: cell creation, update, wrapping, serialization
    test_collision.py         7 tests: distance, overlap, resolution, symmetry
    test_simulation.py        6 tests: pipeline, serialization, geometry, bounds
  docs/
    architecture.md           System design and API reference
    biological_model.md       Zebrafish biology and simulation model
    development_history.md    Changelog from MATLAB v1.x to Python v2.0
    references.md             Academic papers and software libraries
    user_guide.md             Installation, usage, and troubleshooting
    svg/                      Diagrams (architecture, model, flow, coordinates, app)
  legacy/                     Original MATLAB code and GUIDE files
  requirements.txt            Pinned Python dependencies
```

## API Summary

### REST Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/` | Serve the single-page application |
| `POST` | `/api/simulation/init` | Initialize simulation with config JSON |
| `POST` | `/api/simulation/start` | Begin continuous stepping |
| `POST` | `/api/simulation/stop` | Pause stepping |
| `POST` | `/api/simulation/step` | Advance one time step |
| `GET` | `/api/simulation/state` | Query current state snapshot |

### WebSocket

| Endpoint | Direction | Message |
|---|---|---|
| `ws://localhost:8002/ws/simulation` | Client to Server | `{ "action": "start" }`, `{ "action": "stop" }`, `{ "action": "speed", "value": 100 }` |
| | Server to Client | JSON with `dfc_layer` (cells, step count) and `environment` (radius, velocity, bounds) |

## Documentation

- [Architecture](docs/architecture.md) -- System design, API endpoints, WebSocket protocol, data flow
- [Biological Model](docs/biological_model.md) -- Zebrafish biology, DFC migration, collision model
- [Development History](docs/development_history.md) -- Changelog from MATLAB to Python/Web
- [References](docs/references.md) -- Academic papers and software libraries
- [User Guide](docs/user_guide.md) -- Installation, usage, parameters, troubleshooting

## Tech Stack

- **Backend:** Python 3.11+, FastAPI, Uvicorn, NumPy, SciPy, Pydantic
- **Frontend:** Three.js r128 (CDN), vanilla JavaScript, HTML5, CSS3
- **Communication:** REST API (JSON) + WebSocket (JSON streaming)
- **Testing:** 23 tests across 3 test files, run with plain Python (no framework required)

## License

Academic use. See institutional guidelines.
