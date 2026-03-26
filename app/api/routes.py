"""
REST API routes for the SpherSIM web application.

Provides endpoints for initializing, starting, stopping, and stepping
the simulation, as well as querying the current state.  These endpoints
are mounted by :mod:`app.main` and complement the WebSocket endpoint
used for real-time streaming.
"""

from fastapi import APIRouter

router = APIRouter(prefix="/api/simulation", tags=["simulation"])


# NOTE: Routes are defined directly in main.py for simplicity.
# This module is reserved for future expansion (e.g., parameter
# presets, file export, snapshot management).
