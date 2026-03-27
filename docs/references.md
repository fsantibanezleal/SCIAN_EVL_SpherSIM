# References

## Biological Background

### DFC Migration and Kupffer's Vesicle

1. **Oteiza P, Koppen M, Krieg M, et al.** (2008). Planar cell polarity signalling regulates cell adhesion properties in progenitors of the zebrafish laterality organ. *Development*, 135(20), 3459-3468.
   - Investigates how planar cell polarity pathways influence adhesion among DFC progenitors during Kupffer's vesicle formation.

2. **Oteiza P, Koppen M, Concha ML, Heisenberg CP.** (2008). Origin and shaping of the laterality organ in zebrafish. *Development*, 135(16), 2807-2813.
   - Describes how DFCs originate at the dorsal margin and collectively shape into the vesicle that establishes left-right asymmetry.

3. **Ablooglu AJ, et al.** (2021). DFC apical contacts and dragging during Kupffer's vesicle formation. *eLife*.
   - Demonstrates that DFCs maintain apical membrane attachments to the EVL and are physically dragged vegetalward by the advancing margin.

### Zebrafish Epiboly Mechanics

4. **Compagnon J, Bhatt DK.** (2019). Mechanisms of zebrafish epiboly. In *Cell Polarity in Development and Disease*. Elsevier.
   - Reviews the cellular and molecular mechanisms driving EVL spreading, deep cell intercalation, and yolk cell contractility during epiboly.

5. **Rho HK, et al.** (2009). Zebrafish epiboly: mechanics and mechanisms. *Int J Dev Biol*, 53(8-10), 1187-1193.
   - Provides a mechanical perspective on how tissue-level forces coordinate the three layers (EVL, deep cells, YSL) during epiboly.

### Computational Modeling

6. **Keller R, et al.** (2025). Modeling epithelial morphogenesis on curved surfaces. *bioRxiv*.
   - Presents computational approaches for simulating cell sheet dynamics on curved geometries, relevant to the spherical surface model used here.

## Software and Libraries

| Library | Role in this project | URL |
|---|---|---|
| **FastAPI** | Asynchronous Python web framework used for REST and WebSocket endpoints. | https://fastapi.tiangolo.com/ |
| **Uvicorn** | ASGI server that runs the FastAPI application. | https://www.uvicorn.org/ |
| **NumPy** | Numerical array operations for coordinate conversions, contour generation, and collision math. | https://numpy.org/ |
| **SciPy** | Scientific computing library; available for extended analysis and spatial routines. | https://scipy.org/ |
| **Pydantic** | Data validation for the simulation configuration schema (`SimConfig`). | https://docs.pydantic.dev/ |
| **Three.js** | JavaScript 3D rendering library used for the browser-based visualization (loaded from CDN, version r128). | https://threejs.org/ |
| **WebSockets** | Python library supporting the WebSocket protocol for real-time state streaming. | https://websockets.readthedocs.io/ |

## Related Projects

| Project | Description |
|---|---|
| **SCIAN_LEO_CPM** | Cellular Potts Model simulation for studying cell sorting and tissue patterning. Companion project in the SCIAN laboratory. |
| **CEFOP_DinHot** | Dynamic holography tools for optical manipulation and measurement. |
| **FASL_Coding_DualFotography** | Dual photography application exploring light transport and computational imaging. |

## Epiboly and Gastrulation

7. **Keller PJ, et al.** (2025). Modeling epithelial morphogenesis during zebrafish epiboly. *bioRxiv*.
   - Presents computational models for EVL tissue mechanics on curved surfaces, providing quantitative measurements of tissue tension and migration speed that inform the EVL velocity parameters used in this simulation.

8. **Chal J, et al.** (2025). Mechanical coupling between DFCs and the EVL during epiboly. *bioRxiv*.
   - Investigates the elastic mechanical coupling between DFC cells and the EVL margin, demonstrating that apical contacts act as spring-like tethers. This finding directly motivated the elastic spring coupling model (`F = k * d * exp(-d/lambda)`) implemented in v2.2.

9. **Solnica-Krezel L.** (2005). Conserved patterns of cell movements during vertebrate gastrulation. *Current Biology*, 15(6), R213-R228.
   - A comprehensive review of gastrulation movements across vertebrate species, placing zebrafish epiboly in the context of conserved morphogenetic programs. Describes how convergence, extension, and epiboly are coordinated to shape the embryo.

10. **Bruce AEE.** (2016). Zebrafish epiboly: Spreading thin over the yolk. *Developmental Dynamics*, 245(3), 244-258.
    - A detailed review focused specifically on zebrafish epiboly mechanisms, covering the roles of EVL tension, YSL actomyosin contractility, deep cell intercalation, and E-cadherin adhesion. Provides the mechanical framework that motivates treating the EVL as a kinematic boundary in this simulation.
