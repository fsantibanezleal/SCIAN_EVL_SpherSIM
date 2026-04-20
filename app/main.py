"""
SCIAN EVL SpherSIM -- Spherical Embryo Simulation.

FastAPI web application for 3D simulation of DFC cell migration on a
spherical embryo surface during zebrafish epiboly.

Usage:
    uvicorn app.main:app --reload --port 8002

The server exposes:
    GET  /                          -- Single-page application (index.html)
    POST /api/simulation/init       -- Initialize simulation with config
    POST /api/simulation/start      -- Begin continuous stepping
    POST /api/simulation/stop       -- Pause continuous stepping
    POST /api/simulation/step       -- Advance one time step
    GET  /api/simulation/state      -- Query current state snapshot
    WS   /ws/simulation             -- Real-time state streaming
"""

import asyncio
import json
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel

from . import __version__
from .simulation.layer_dfc import DFCLayer
from .simulation.environment import SphericalEnvironment

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

APP_TITLE = "SCIAN EVL SpherSIM"

app = FastAPI(
    title=APP_TITLE,
    description="3D spherical simulation of embryonic cell migration",
    version=__version__,
)

static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Mutable simulation state shared by endpoints and the WebSocket loop.
sim_state: dict = {
    "env": None,
    "dfc_layer": None,
    "running": False,
    "speed": 50,
    "metrics_history": [],
}

# ---------------------------------------------------------------------------
# Configuration schema
# ---------------------------------------------------------------------------


class SimConfig(BaseModel):
    """Simulation configuration received from the frontend."""

    embryo_radius: float = 1000
    num_dfcs: int = 24
    radial_size: float = 0.049  # approximately pi/64
    num_vertices: int = 100
    evl_speed: float = 0.005
    noise_std: float = 0.5
    ring_strength: float = 0.005
    speed_ms: int = 50


# ---------------------------------------------------------------------------
# REST endpoints
# ---------------------------------------------------------------------------


@app.get("/")
async def root():
    """Serve the single-page application."""
    return FileResponse(str(static_dir / "index.html"))


@app.get("/api/health")
async def health():
    """Lightweight liveness probe.

    Returns a stable ``{"status": "ok"}`` payload with HTTP 200. Intended
    for uptime monitors, cPanel health-checks, and local smoke tests.
    """
    return {"status": "ok"}


@app.get("/api/version")
async def version():
    """Expose the deployed application version.

    Sources the version string from :data:`app.__version__` (single source
    of truth) and the service name from the FastAPI ``title``. Useful for
    verifying which build is running in a given environment.
    """
    return {"version": __version__, "name": APP_TITLE}


@app.post("/api/simulation/init")
async def init_sim(config: SimConfig):
    """Initialize (or re-initialize) the simulation."""
    env_config = {
        "embryo_radius": config.embryo_radius,
        "num_dfcs": config.num_dfcs,
        "radial_size": config.radial_size,
        "num_vertices": config.num_vertices,
        "evl_speed": config.evl_speed,
        "noise_std": config.noise_std,
    }

    sim_state["env"] = SphericalEnvironment(env_config)
    sim_state["dfc_layer"] = DFCLayer({
        "noise_std": config.noise_std,
        "ring_strength": config.ring_strength,
    })
    sim_state["dfc_layer"].initialize(
        embryo_radius=config.embryo_radius,
        num_cells=config.num_dfcs,
        radial_size=config.radial_size,
        num_vertices=config.num_vertices,
    )
    sim_state["speed"] = config.speed_ms
    sim_state["running"] = False
    sim_state["metrics_history"] = []

    return {
        "status": "initialized",
        "num_cells": len(sim_state["dfc_layer"].cells),
    }


@app.post("/api/simulation/start")
async def start():
    """Resume continuous simulation stepping."""
    sim_state["running"] = True
    return {"status": "running"}


@app.post("/api/simulation/stop")
async def stop():
    """Pause continuous simulation stepping."""
    sim_state["running"] = False
    return {"status": "stopped"}


@app.post("/api/simulation/step")
async def step():
    """Advance the simulation by a single time step."""
    if sim_state["dfc_layer"] is None:
        return {"error": "Not initialized"}

    env = sim_state["env"]
    env.update()
    sim_state["dfc_layer"].update(env.margin_velocity, evl_elevation=env.margin_elevation)

    # Accumulate metrics for CSV export
    metrics = sim_state["dfc_layer"].compute_cluster_metrics()
    sim_state["metrics_history"].append(metrics)

    return {
        "dfc_layer": sim_state["dfc_layer"].get_state(),
        "environment": env.get_state(),
    }


@app.get("/api/simulation/state")
async def get_state():
    """Return the current simulation state without advancing it."""
    if sim_state["dfc_layer"] is None:
        return {"error": "Not initialized"}

    return {
        "dfc_layer": sim_state["dfc_layer"].get_state(),
        "environment": sim_state["env"].get_state(),
    }


@app.get("/api/simulation/export-csv")
async def export_csv():
    """Export accumulated simulation metrics as CSV download."""
    import io
    import csv

    history = sim_state.get("metrics_history", [])
    if not history:
        return {"error": "No simulation history. Run the simulation first."}

    output = io.StringIO()
    keys = list(history[0].keys())
    writer = csv.DictWriter(output, fieldnames=['step'] + keys)
    writer.writeheader()
    for i, row in enumerate(history):
        writer.writerow({'step': i, **{k: row.get(k, '') for k in keys}})

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=simulation_metrics.csv"}
    )


# ---------------------------------------------------------------------------
# WebSocket endpoint
# ---------------------------------------------------------------------------


@app.websocket("/ws/simulation")
async def ws_sim(websocket: WebSocket):
    """Stream simulation state in real time.

    Accepts JSON messages with an ``action`` field:
        ``start``  -- begin continuous stepping
        ``stop``   -- pause stepping
        ``speed``  -- change step interval (``value`` in ms)
    """
    await websocket.accept()
    try:
        while True:
            # Non-blocking check for incoming commands
            try:
                data = await asyncio.wait_for(
                    websocket.receive_text(), timeout=0.01
                )
                msg = json.loads(data)
                action = msg.get("action")
                if action == "start":
                    sim_state["running"] = True
                elif action == "stop":
                    sim_state["running"] = False
                elif action == "speed":
                    sim_state["speed"] = msg.get("value", 50)
            except asyncio.TimeoutError:
                pass

            # Step and broadcast if running
            if sim_state["running"] and sim_state["dfc_layer"]:
                sim_state["env"].update()
                sim_state["dfc_layer"].update(sim_state["env"].margin_velocity, evl_elevation=sim_state["env"].margin_elevation)

                # Accumulate metrics for CSV export
                metrics = sim_state["dfc_layer"].compute_cluster_metrics()
                sim_state["metrics_history"].append(metrics)

                state = {
                    "dfc_layer": sim_state["dfc_layer"].get_state(),
                    "environment": sim_state["env"].get_state(),
                }
                await websocket.send_json(state)

            await asyncio.sleep(sim_state["speed"] / 1000.0)

    except WebSocketDisconnect:
        pass
