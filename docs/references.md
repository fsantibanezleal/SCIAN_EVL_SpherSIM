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

11. **Solnica-Krezel L.** (2006). Gastrulation in zebrafish — all just about adhesion? *Current Opinion in Genetics & Development*, 16(4), 433-441.
    - Discusses how differential cadherin-mediated adhesion coordinates the large-scale rearrangements of gastrulation, including the interactions between the EVL, YSL, and deep cell populations. Supports the use of differential-adhesion terms in the simulation's collision and cluster-cohesion model.

12. **Kimmel CB, Ballard WW, Kimmel SR, Ullmann B, Schilling TF.** (1995). Stages of embryonic development of the zebrafish. *Developmental Dynamics*, 203(3), 253-310.
    - Canonical staging atlas used throughout the field. Defines the epiboly stages (30%, 50%, 75%, 90%, 100%) referenced by `docs/svg/epiboly_stages.svg` and by the EVL margin elevation schedule in `layer_evl.py`.

13. **Cooper MS, D'Amico LA.** (1996). A cluster of noninvoluting endocytic cells at the margin of the zebrafish blastoderm marks the site of embryonic shield formation. *Developmental Biology*, 180(1), 184-198.
    - Original identification of the dorsal-forerunner cell (DFC) cluster as a distinct, non-involuting population. This is the foundational paper that defines the biological object this simulation models.

14. **Amack JD, Yost HJ.** (2004). The T box transcription factor no tail in ciliated cells controls zebrafish left-right asymmetry. *Current Biology*, 14(8), 685-690.
    - Establishes the functional link between DFCs, Kupffer's vesicle, and left-right asymmetry (situs inversus when DFCs are disrupted). Motivates why correct DFC migration is biomedically relevant and not just a developmental-biology curiosity.

15. **Wang X, Merkel M, Sutter LB, Erdemci-Tandogan G, Manning ML, Kasza KE.** (2024). Anisotropy links cell shapes to tissue flow during convergent extension. *Nature Physics*, 20(1), 127-135.
    - A modern computational-morphogenesis reference showing how anisotropic cell shape drives collective tissue flow on curved substrates. Relevant for extending the current isotropic contour model (`cell_dfc.py`) toward shape-anisotropic cells in future versions.
