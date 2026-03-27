# Epiboly Biology

This document provides detailed biological context for the zebrafish epiboly process simulated by SCIAN EVL SpherSIM. It covers the developmental stages, tissue layer mechanics, DFC specification, and Kupffer's vesicle formation.

---

## Epiboly Stages

Epiboly is the process by which the blastoderm (the cap of cells sitting on top of the yolk cell) spreads to envelop the entire yolk. It is conventionally described by the percentage of the yolk cell surface covered by the advancing blastoderm margin.

| Stage         | Timing (hpf)  | Description                                                                                                |
|---------------|---------------|------------------------------------------------------------------------------------------------------------|
| **30% epiboly** | ~4.7 hpf    | The blastoderm has thinned and begun spreading. The EVL margin has moved past the equator-equivalent of the animal hemisphere. DFCs are first identifiable at the dorsal margin. |
| **50% epiboly** | ~5.3 hpf    | The blastoderm margin reaches the equator of the yolk cell. The EVL and deep cell layers are spreading in coordination. DFCs maintain strong apical contacts with the EVL. |
| **75% epiboly** | ~8.0 hpf    | Three-quarters of the yolk is covered. The EVL margin has accelerated. DFCs begin to lose apical contacts (partial delamination). The DFC cluster starts to compact along the dorsal midline. |
| **90% epiboly** | ~9.0 hpf    | Nearly complete coverage. DFCs have largely delaminated from the EVL and are migrating as a cohesive cluster toward the vegetal pole. Convergence toward the midline is pronounced. |
| **100% epiboly** | ~10.3 hpf  | The yolk cell is fully enclosed. The blastoderm margin has closed at the vegetal pole. DFCs coalesce into a compact rosette and begin forming the lumen of Kupffer's vesicle. |

> **Diagram 1 (see svg/epiboly_stages.svg):** Side-view cross-sections of the embryo at each of the five stages, showing the progressive spreading of tissue layers and the migration of the DFC cluster.

---

## Tissue Layers

Three tissue layers participate in epiboly, each with distinct structural and mechanical roles.

### EVL (Enveloping Layer)

The EVL is the outermost single-cell-thick epithelial sheet. It forms a tight, mechanically coherent barrier.

- **Structure:** Flattened squamous epithelial cells connected by tight junctions and adherens junctions. The EVL acts as a permeability barrier covering the embryo.
- **Mechanical role:** The EVL margin is the leading front of epiboly. Its steady advancement toward the vegetal pole provides the primary driving force for DFC vegetal migration. The EVL margin is connected to the YSL through a continuous actomyosin belt, and the combined tension of this belt helps pull the entire tissue sheet vegetalward.
- **In the simulation:** Modeled as a kinematic boundary (a latitude line on the sphere) that moves at constant angular velocity toward the vegetal pole. DFCs are coupled to this boundary through elastic spring attachments that decay with distance.

### DEL (Deep Cell Layer)

The DEL consists of the bulk of the blastoderm cells lying between the EVL and the yolk cell surface.

- **Structure:** Loosely packed, round cells that will later give rise to all embryonic tissues (ectoderm, mesoderm, endoderm) through gastrulation.
- **Mechanical role:** Deep cells undergo radial intercalation -- they rearrange from a multi-layered stack into fewer layers, effectively thinning the blastoderm and providing a force contribution to epiboly. Deep cells do not have strong cell-cell junctions and move relatively independently.
- **In the simulation:** Not explicitly modeled. The simulation focuses on the DFC subpopulation and treats the surrounding deep cell environment as passive.

### YSL (Yolk Syncytial Layer)

The YSL is a multinucleated cytoplasmic layer that lies directly on the yolk cell surface, beneath the EVL.

- **Structure:** Formed by the fusion of marginal blastomeres with the yolk cell. Contains hundreds of nuclei but no cell membranes -- it is a syncytium. Rich in actin and myosin.
- **Mechanical role:** The external YSL (e-YSL) at the margin contains a circumferential actomyosin ring that generates contractile tension pulling the EVL margin vegetalward. The internal YSL (i-YSL) beneath the blastoderm facilitates deep cell spreading through friction-like interactions. The YSL is thought to be the primary motor of epiboly.
- **In the simulation:** Not explicitly modeled as a separate entity. Its mechanical contribution is implicitly captured by the constant EVL margin velocity, which represents the net effect of YSL-driven pulling forces.

> **Diagram 2 (see svg/spherical_model.svg):** The existing spherical model diagram shows the overall embryo geometry, including the relative positions of the tissue layers.

---

## DFC Specification

Dorsal Forerunner Cells (DFCs) are specified from EVL cells at the dorsal margin of the embryo during early epiboly.

### Incomplete Delamination Model

DFCs do not fully detach from the EVL when they are specified. Instead, they undergo **incomplete delamination**:

1. **Apical constriction.** A subset of EVL cells at the dorsal margin constricts their apical surface, reducing their footprint within the EVL sheet.
2. **Basal extrusion.** These cells begin to move basally (inward), away from the embryo surface and toward the yolk cell.
3. **Retained apical contacts.** Critically, the delaminating cells do not fully sever their apical membrane connections to neighboring EVL cells. Thin cytoplasmic threads (apical contacts) persist, physically tethering the DFCs to the advancing EVL margin.
4. **Progressive severance.** As epiboly continues and the EVL margin moves farther from the DFC cluster, these apical contacts are progressively stretched and severed. By approximately 75-90% epiboly, most DFCs have lost their EVL attachments entirely.

This incomplete delamination mechanism is directly modeled in the simulator through the elastic spring coupling between DFC cells and the EVL boundary:

```
F = k * d * exp(-d / lambda)
```

The exponential decay with distance (`lambda = 0.3 rad`) captures the progressive stretching and weakening of apical contacts. Cells close to the EVL margin (small `d`) feel a strong pull; cells far from the margin (large `d`) are effectively detached.

### DFC Population

- **Number:** Approximately 20-30 cells per embryo at the time of specification.
- **Location:** Dorsal margin, spanning a limited azimuthal range along the shield/organizer region.
- **Variability:** The exact number and spatial arrangement of DFCs varies between embryos, contributing to natural variability in Kupffer's vesicle size and function.

---

## Kupffer's Vesicle Formation

Kupffer's vesicle (KV) is the transient organ responsible for establishing left-right asymmetry in the zebrafish embryo. Its formation is the ultimate biological outcome of the DFC migration process modeled by this simulator.

### Formation Sequence

1. **DFC cluster convergence.** As the DFCs detach from the EVL and lose their apical contacts, they rely on cell-cell adhesion (E-cadherin) to maintain cluster cohesion. The cluster progressively compacts through a combination of EVL-driven migration, stochastic motility, and differential adhesion.

2. **Rosette formation.** At or near the vegetal pole (100% epiboly), the DFC cluster forms a compact rosette with cells arranged around a central point. Apical surfaces of the cells point inward.

3. **Lumen formation.** The apical surfaces of the rosette cells secrete fluid into the central space, inflating a fluid-filled lumen. Ion channels and transporters (notably CFTR chloride channels) drive osmotic water flow into the lumen, expanding it.

4. **Ciliogenesis.** Each DFC cell extends a single motile cilium from its apical surface into the KV lumen. These cilia are approximately 5-7 um long.

5. **Cilia-driven flow.** The motile cilia beat in a coordinated, posteriorly tilted rotational pattern, generating a counterclockwise (when viewed from the dorsal side) fluid flow inside the KV lumen.

6. **Left-right symmetry breaking.** The asymmetric fluid flow creates a concentration gradient of signaling molecules (possibly Nodal pathway ligands) across the left-right axis of the KV. Sensory cilia on the KV wall detect this asymmetry and relay the signal to adjacent tissues, initiating a cascade that specifies left-right organ placement.

### Consequences of KV Failure

When the DFC migration or KV formation process is disrupted, the embryo develops **laterality defects**:

- **Situs inversus:** Complete mirror reversal of organ placement (heart, liver, gut looping all reversed).
- **Heterotaxia:** Randomized or discordant organ placement, with some organs on the correct side and others reversed.
- **Bilateral symmetry retention:** Organs that should be asymmetric remain symmetric.

These defects arise from insufficient DFC number (too few cells to form a functional vesicle), disrupted DFC migration (cluster fragmentation), or faulty cilia function.

> **Diagram 3 (see svg/coordinate_system.svg):** The existing coordinate system diagram shows the AER convention used to track DFC positions during migration from the animal hemisphere toward the vegetal pole.

---

## Mechanical Forces in Epiboly

Epiboly is driven by the coordinated action of multiple mechanical forces:

### EVL Tension

The EVL sheet is under tension due to active spreading at the margin and passive resistance from the tissue ahead of the margin. This tension:
- Drives the margin vegetalward at approximately constant velocity during mid-epiboly.
- Transmits force to DFCs through apical contacts, dragging them along.
- Creates a mechanical boundary that confines deep cells beneath it.

### Yolk Cell Contraction

The yolk cell is not passive during epiboly. Actin and myosin networks within the YSL generate contractile forces:
- The e-YSL actomyosin ring contracts, pulling the EVL margin vegetalward.
- The yolk cell surface undergoes slow, bulk contraction that assists tissue spreading.
- Laser ablation experiments show that disrupting YSL actomyosin halts epiboly.

### Actomyosin Ring

A circumferential actomyosin band at the EVL margin and e-YSL interface acts as a purse-string:
- Its contraction constricts the blastoderm margin, pulling it over the yolk cell.
- The ring generates tension of approximately 1-10 nN (estimated from laser ablation recoil measurements).
- Pharmacological disruption of the ring (e.g., blebbistatin treatment) stalls epiboly at approximately 50%.

### Deep Cell Intercalation

Deep cells rearrange by moving between each other (intercalation), effectively thinning the blastoderm from multiple cell layers to fewer layers. This contributes a secondary spreading force that complements EVL margin advancement.

---

## References

- Ablooglu, A.J. et al. (2021). Apical contacts stemming from incomplete delamination guide progenitor cell allocation through a dragging mechanism. *eLife*, 10:e66495.
- Solnica-Krezel, L. (2005). Conserved patterns of cell movements during vertebrate gastrulation. *Current Biology*, 15(6), R213-R228.
- Bruce, A.E.E. (2016). Zebrafish epiboly: Spreading thin over the yolk. *Developmental Dynamics*, 245(3), 244-258.
- Keller, P.J. et al. (2025). Modeling Epithelial Morphogenesis during Zebrafish Epiboly. *bioRxiv*.
- Chal, J. et al. (2025). Mechanical coupling between DFCs and the EVL during epiboly. *bioRxiv*.
- Oteiza, P. et al. (2008). Origin and shaping of the laterality organ in zebrafish. *Development*, 135(16), 2807-2813.
