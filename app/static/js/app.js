/**
 * Main application orchestration for SpherSIM.
 *
 * Connects the UI controls, Three.js renderer, and WebSocket client
 * into a cohesive application.
 */

(function () {
    'use strict';

    // ---- Globals ----
    let controls, renderer, wsClient;
    let isRunning = false;

    // ---- Build WebSocket URL ----
    function wsUrl() {
        const proto = location.protocol === 'https:' ? 'wss:' : 'ws:';
        return proto + '//' + location.host + '/ws/simulation';
    }

    // ---- Initialize ----
    function init() {
        controls = new SimControls();
        renderer = new Renderer3D(document.getElementById('three-canvas'));

        // WebSocket
        wsClient = new SimWebSocket(
            wsUrl(),
            onSimState,
            (status) => controls.setWsStatus(status),
        );
        wsClient.connect();

        // ---- Button handlers ----
        controls.btnInit.addEventListener('click', async () => {
            const config = controls.getConfig();
            try {
                const resp = await fetch('/api/simulation/init', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(config),
                });
                const data = await resp.json();
                controls.updateStatus(0, data.num_cells || 0);

                // Fetch initial state to render
                const stateResp = await fetch('/api/simulation/state');
                const state = await stateResp.json();
                onSimState(state);

                // Update sphere if radius changed
                renderer.updateSphere(config.embryo_radius);
            } catch (err) {
                console.error('Init failed:', err);
            }
        });

        controls.btnPlay.addEventListener('click', () => {
            isRunning = true;
            controls.setRunning(true);
            wsClient.send({ action: 'start' });
        });

        controls.btnPause.addEventListener('click', () => {
            isRunning = false;
            controls.setRunning(false);
            wsClient.send({ action: 'stop' });
        });

        controls.btnStep.addEventListener('click', async () => {
            try {
                const resp = await fetch('/api/simulation/step', { method: 'POST' });
                const data = await resp.json();
                onSimState(data);
            } catch (err) {
                console.error('Step failed:', err);
            }
        });

        // ---- Speed change ----
        controls.inputs.speed.addEventListener('change', () => {
            const ms = parseInt(controls.inputs.speed.value, 10);
            wsClient.send({ action: 'speed', value: ms });
        });

        // ---- View toggles ----
        controls.chkWireframe.addEventListener('change', (e) => {
            renderer.setWireframe(e.target.checked);
        });
        controls.chkAxes.addEventListener('change', (e) => {
            renderer.setAxes(e.target.checked);
        });
        controls.chkCenters.addEventListener('change', (e) => {
            renderer.setCenters(e.target.checked);
        });
    }

    // ---- Handle incoming simulation state ----
    function onSimState(state) {
        if (!state || state.error) return;

        const dfc = state.dfc_layer;
        if (dfc) {
            controls.updateStatus(dfc.step, dfc.num_cells);
            renderer.updateCells(dfc.cells);
        }
    }

    // ---- Boot ----
    document.addEventListener('DOMContentLoaded', init);
})();
