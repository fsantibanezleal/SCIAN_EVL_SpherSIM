/**
 * UI Controls for SpherSIM.
 *
 * Reads parameter values from the control panel inputs and provides
 * them to the application layer.
 */

class SimControls {
    constructor() {
        // Parameter inputs
        this.inputs = {
            radius:     document.getElementById('param-radius'),
            numDfcs:    document.getElementById('param-num-dfcs'),
            radialSize: document.getElementById('param-radial-size'),
            vertices:   document.getElementById('param-vertices'),
            evlSpeed:   document.getElementById('param-evl-speed'),
            noise:      document.getElementById('param-noise'),
            speed:      document.getElementById('param-speed'),
        };

        // Buttons
        this.btnInit  = document.getElementById('btn-init');
        this.btnPlay  = document.getElementById('btn-play');
        this.btnPause = document.getElementById('btn-pause');
        this.btnStep  = document.getElementById('btn-step');

        // View toggles
        this.chkWireframe = document.getElementById('chk-wireframe');
        this.chkAxes      = document.getElementById('chk-axes');
        this.chkCenters   = document.getElementById('chk-centers');

        // Status displays
        this.statStep  = document.getElementById('stat-step');
        this.statCells = document.getElementById('stat-cells');
        this.statWs    = document.getElementById('stat-ws');
    }

    /** Collect current parameter values into a config object. */
    getConfig() {
        return {
            embryo_radius: parseFloat(this.inputs.radius.value),
            num_dfcs:      parseInt(this.inputs.numDfcs.value, 10),
            radial_size:   parseFloat(this.inputs.radialSize.value),
            num_vertices:  parseInt(this.inputs.vertices.value, 10),
            evl_speed:     parseFloat(this.inputs.evlSpeed.value),
            noise_std:     parseFloat(this.inputs.noise.value),
            speed_ms:      parseInt(this.inputs.speed.value, 10),
        };
    }

    /** Update displayed status information. */
    updateStatus(step, numCells) {
        this.statStep.textContent  = step;
        this.statCells.textContent = numCells;
    }

    /** Update WebSocket status indicator. */
    setWsStatus(status) {
        this.statWs.textContent = status;
        this.statWs.style.color =
            status === 'connected'    ? 'var(--success)' :
            status === 'disconnected' ? 'var(--danger)'  :
            status === 'error'        ? 'var(--danger)'  :
            'var(--text-primary)';
    }

    /** Set button states for running mode. */
    setRunning(running) {
        this.btnPlay.disabled  = running;
        this.btnPause.disabled = !running;
    }
}
