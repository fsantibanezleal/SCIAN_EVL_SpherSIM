/**
 * Three.js 3D renderer for SpherSIM.
 *
 * Renders the embryo sphere and DFC cell contours using Three.js
 * with OrbitControls for interactive rotation and zoom.
 */

class Renderer3D {
    /**
     * @param {HTMLCanvasElement} canvas - Target canvas element.
     */
    constructor(canvas) {
        this.canvas = canvas;
        this.cellLines = [];
        this.cellCenters = [];
        this.showWireframe = false;
        this.showAxes = true;
        this.showCenters = true;
        this.embryoRadius = 1000;

        // Color palette for cells
        this.palette = [
            0x58a6ff, 0x3fb950, 0xd29922, 0xf85149, 0xbc8cff,
            0x79c0ff, 0x56d364, 0xe3b341, 0xffa198, 0xd2a8ff,
            0x39d353, 0xf0883e, 0xff7b72, 0xa371f7, 0x6cb6ff,
            0x7ee787, 0xf2cc60, 0xffa657, 0xcea5fb, 0x9ecbff,
            0x2ea043, 0xdb6d28, 0xda3633, 0x8957e5, 0x388bfd,
        ];

        this._initScene();
        this._initLights();
        this._initSphere();
        this._initAxes();
        this._initControls();
        this._onResize();

        window.addEventListener('resize', () => this._onResize());
        this._animate();
    }

    // ------------------------------------------------------------------
    // Initialization
    // ------------------------------------------------------------------

    _initScene() {
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x0d1117);

        this.camera = new THREE.PerspectiveCamera(50, 1, 1, 50000);
        this.camera.position.set(2200, 1200, 2200);
        this.camera.lookAt(0, 0, 0);

        this.renderer = new THREE.WebGLRenderer({
            canvas: this.canvas,
            antialias: true,
        });
        this.renderer.setPixelRatio(window.devicePixelRatio);
    }

    _initLights() {
        const ambient = new THREE.AmbientLight(0xffffff, 0.4);
        this.scene.add(ambient);

        const dir = new THREE.DirectionalLight(0xffffff, 0.8);
        dir.position.set(3000, 3000, 3000);
        this.scene.add(dir);

        const dir2 = new THREE.DirectionalLight(0x388bfd, 0.3);
        dir2.position.set(-2000, -1000, 1000);
        this.scene.add(dir2);
    }

    _initSphere() {
        // Solid semi-transparent sphere
        const geom = new THREE.SphereGeometry(this.embryoRadius, 64, 48);
        const mat = new THREE.MeshPhongMaterial({
            color: 0x1a3a1a,
            transparent: true,
            opacity: 0.25,
            side: THREE.DoubleSide,
            depthWrite: false,
        });
        this.sphereMesh = new THREE.Mesh(geom, mat);
        this.scene.add(this.sphereMesh);

        // Wireframe overlay
        const wireMat = new THREE.MeshBasicMaterial({
            color: 0x2ea043,
            wireframe: true,
            transparent: true,
            opacity: 0.08,
        });
        this.sphereWire = new THREE.Mesh(geom.clone(), wireMat);
        this.sphereWire.visible = this.showWireframe;
        this.scene.add(this.sphereWire);
    }

    _initAxes() {
        this.axesHelper = new THREE.AxesHelper(this.embryoRadius * 1.4);
        this.axesHelper.visible = this.showAxes;
        this.scene.add(this.axesHelper);
    }

    _initControls() {
        this.controls = new THREE.OrbitControls(this.camera, this.canvas);
        this.controls.enableDamping = true;
        this.controls.dampingFactor = 0.08;
        this.controls.minDistance = 500;
        this.controls.maxDistance = 15000;
    }

    // ------------------------------------------------------------------
    // Resize
    // ------------------------------------------------------------------

    _onResize() {
        const parent = this.canvas.parentElement;
        if (!parent) return;
        const w = parent.clientWidth;
        const h = parent.clientHeight;
        this.renderer.setSize(w, h);
        this.camera.aspect = w / h;
        this.camera.updateProjectionMatrix();
    }

    // ------------------------------------------------------------------
    // Animation loop
    // ------------------------------------------------------------------

    _animate() {
        requestAnimationFrame(() => this._animate());
        this.controls.update();
        this.renderer.render(this.scene, this.camera);
    }

    // ------------------------------------------------------------------
    // Update embryo
    // ------------------------------------------------------------------

    /** Recreate the sphere if the radius changed. */
    updateSphere(radius) {
        if (Math.abs(radius - this.embryoRadius) < 0.01) return;
        this.embryoRadius = radius;

        // Remove old meshes
        this.scene.remove(this.sphereMesh);
        this.scene.remove(this.sphereWire);
        this.scene.remove(this.axesHelper);

        this._initSphere();
        this._initAxes();
    }

    // ------------------------------------------------------------------
    // Update cells
    // ------------------------------------------------------------------

    /**
     * Update all DFC cell visuals from simulation state.
     * @param {Array} cells - Array of cell state objects from the server.
     */
    updateCells(cells) {
        // Remove old cell objects
        for (const line of this.cellLines) {
            this.scene.remove(line);
            line.geometry.dispose();
            line.material.dispose();
        }
        for (const pt of this.cellCenters) {
            this.scene.remove(pt);
            pt.geometry.dispose();
            pt.material.dispose();
        }
        this.cellLines = [];
        this.cellCenters = [];

        if (!cells) return;

        for (let idx = 0; idx < cells.length; idx++) {
            const cell = cells[idx];
            const color = this.palette[idx % this.palette.length];

            // --- Contour line ---
            const contour = cell.contour_xyz;
            const points = [];
            for (let i = 0; i < contour.length; i++) {
                points.push(new THREE.Vector3(contour[i][0], contour[i][2], -contour[i][1]));
            }
            // Close the loop
            if (contour.length > 0) {
                points.push(new THREE.Vector3(contour[0][0], contour[0][2], -contour[0][1]));
            }

            const lineGeom = new THREE.BufferGeometry().setFromPoints(points);
            const lineMat = new THREE.LineBasicMaterial({ color: color, linewidth: 2 });
            const line = new THREE.Line(lineGeom, lineMat);
            this.scene.add(line);
            this.cellLines.push(line);

            // --- Center sphere ---
            if (this.showCenters) {
                const cx = cell.center_xyz[0];
                const cy = cell.center_xyz[2];    // swap Y/Z for Three.js
                const cz = -cell.center_xyz[1];
                const dotGeom = new THREE.SphereGeometry(12, 8, 6);
                const dotMat = new THREE.MeshBasicMaterial({ color: color });
                const dot = new THREE.Mesh(dotGeom, dotMat);
                dot.position.set(cx, cy, cz);
                this.scene.add(dot);
                this.cellCenters.push(dot);
            }
        }
    }

    // ------------------------------------------------------------------
    // View toggles
    // ------------------------------------------------------------------

    setWireframe(visible) {
        this.showWireframe = visible;
        if (this.sphereWire) this.sphereWire.visible = visible;
    }

    setAxes(visible) {
        this.showAxes = visible;
        if (this.axesHelper) this.axesHelper.visible = visible;
    }

    setCenters(visible) {
        this.showCenters = visible;
    }
}
