# Help: Earthfill and rockfill (Bishop)

This tool estimates the **factor of safety (FS)** of a circular slip using the **Bishop simplified method**. Forces are for a **1 m** thick slice of the dam (plane strain).

**Units:** length in m, unit weight in kN/m³, cohesion in kPa (= kN/m²). FS is dimensionless. A classroom static check is often **FS ≥ 1.5**; use the value given in the course notes.

**Buttons (top right)**

- **Geometry refresh** — redraws the cross-section, water, phreatic line, search grid and plot window. No FS is calculated. Use this after changing sizes, slopes, water or **Plot extent**. Changing **Centre x**, **Centre y** or **Radius** also redraws the circle.
- **Run analysis** — computes FS (one trial circle, or a grid search). Grid search is slower (often 1–3 minutes).

---

## Options (full-width bar)

**Slope analysis**

| Choice | Reservoir plotted | Slip circle | Phreatic line |
|---|---|---|---|
| **Inner slope analysis** | Pool at the **first y** of that dam’s phreatic line | Downstream face | Starts at the pool |
| **Rapid drawdown analysis** | Empty (no blue water) | Upstream face | Held from the **first y** of that dam’s phreatic line (the old pool) |

Switching the choice moves the trial **centre** onto that face and updates **Centre x** so the numbers match the plot.

**Slip surface**

- **Single trial circle** — one centre and radius from the **Centerpoint** tab, shared by every ticked earthfill/rockfill dam. Fast. Use it to see how FS changes with materials or water. The **Grid** tab is hidden in this mode.
- **Grid search for critical circle** — many centres and radii from the **Grid** tab. The lowest valid FS is reported. Grey cells are centres with no valid circle. The **Centerpoint** tab is hidden in this mode.

The earthfill/rockfill **reservoir elevation** is the **y** of the first point of that dam’s phreatic line (Homogeneous, Clay core or CFRD tab). There is no separate global pool input.

**Dams and extras** — tick a dam to show it on the **2×2 plot**. Untick it and that panel disappears.

- **Homogeneous earthfill** — one fill material.
- **Earthfill with clay core** — shell plus a central clay core.
- **Rockfill with concrete face (CFRD)** — rockfill with \(c' = 0\), a central clay core, an upstream concrete slab, and a phreatic line that drops just behind the face.
- **Concrete gravity dam** — crest, upstream batter and two-slope downstream face (inputs on the **Gravity** tab). Untick to hide it.
- **Include foundation** — a soil layer under the dam so deep circles can pass below the base. Untick to keep circles inside the dam body.
- **Reservoir water weight on upstream face** — extra downward force from the pool on the upstream slope (**Inner slope analysis**). After **Rapid drawdown analysis** the pool is gone, so this force is zero.
- **Draw slices on the plot** — vertical Bishop slices from the slip arc up to the dam surface. Shown on the trial circle and, after **Run analysis**, on the reported circle. The count is **Slices for the reported circle**.

Tick at least one dam type.

---

## Inputs — Safety factors

Minimum FS for **PASS**. After **Run analysis**, each Bishop dam and each gravity check is judged against these numbers.

| Input | Default | Used when |
|---|---|---|
| **Inner slope analysis** | 1.5 | Slope analysis = Inner slope analysis. Bishop FS must be ≥ this. |
| **Rapid drawdown analysis** | 1.3 | Slope analysis = Rapid drawdown analysis. Bishop FS must be ≥ this. |
| **Static loading** | 1.5 | Gravity dam, Loading = Static. Overturning and sliding FoS must be ≥ this. |
| **Seismic loading** | 1.3 | Gravity dam, Loading = Seismic. Overturning and sliding FoS must be ≥ this. |

Bearing and heel compression on the gravity dam still use **Allowable bearing** and no tension at the heel (Gravity tab). Changing a required FS after a run updates PASS/FAIL without re-running the calculation.

---

## Inputs — Centerpoint

Shown only when **Slip surface** is **Single trial circle**. Hidden during a grid search. One circle is used for every ticked earthfill/rockfill dam. Switching **Inner slope analysis** / **Rapid drawdown analysis** moves the centre onto that face and writes the new **Centre x**. **Centre x**, **Centre y** and **Radius** are then the plotted circle.

| Input | Meaning |
|---|---|
| **Centre x (m)** | Horizontal coordinate of the circle centre. |
| **Centre y (m)** | Vertical coordinate of the circle centre. |
| **Radius (m)** | Circle radius. Must be large enough to cut the slope in two points. |
| **Slices for the reported circle** | Number of vertical slices used for the FS that is printed. More slices = smoother result, slightly slower. |

---

## Inputs — Grid

Shown only when **Slip surface** is **Grid search**. Hidden during a single trial circle. The rectangle is the cloud of trial **centres**.

| Input | Meaning |
|---|---|
| **Grid lower-left x (m)** | Left edge of the centre grid. Increase it to shift the grid downstream (useful for the outer slope). |
| **Grid lower-left y (m)** | Bottom edge of the centre grid. Centres sit **above** the slip, so this is usually above the crest. |
| **Grid width (m)** | Horizontal size of the rectangle of centres. |
| **Grid height (m)** | Vertical size of the rectangle of centres. |
| **Spacing x (m)** | Distance between centres horizontally. Smaller spacing = more trials and a longer run. |
| **Spacing y (m)** | Distance between centres vertically. |
| **Min radius (m)** | Smallest circle radius tried at every centre. |
| **Max radius (m)** | Largest circle radius tried at every centre. |
| **Number of radii** | How many radii between min and max (inclusive). |
| **Slices during search** | Vertical slices per trial while sweeping. Fewer slices are faster; the reported circle is re-analysed with **Slices for the reported circle**. |
| **Heatmap FS colour cap** | Colour scale upper limit. Centres with FS above this look the same (saturated colour). Does not change the calculated FS. |
| **Slices for the reported circle** | Number of vertical slices used for the FS that is printed (the critical circle is re-run with this count). More slices = smoother result, slightly slower. |

A valid circle must cut the dam (or foundation) in two points and stay geometrically possible. Invalid trials are skipped (grey).

---

## Inputs — Foundation

Active when **Include foundation** is ticked. Deep circles may pass through this layer.

| Input | Meaning |
|---|---|
| **Name** | Label on the plot legend. |
| **Cohesion c′ (kPa)** | Effective cohesion of the foundation. |
| **Friction φ′ (deg)** | Effective friction angle of the foundation. |
| **Unit weight (kN/m³)** | Bulk unit weight above the phreatic line. |
| **Saturated unit weight (kN/m³)** | Unit weight below the phreatic line. |
| **Thickness (m)** | Depth of the foundation **below the dam base**. |
| **Extra width beyond toes (m)** | How far the foundation extends left of the upstream toe and right of the downstream toe. Needed so a deep circle can exit in the foundation. |

---

## Shared geometry (Homogeneous, Clay core, CFRD)

Each dam is a trapezoid built from these six numbers (unless you later replace it with a custom polygon in the Python script).

| Input | Meaning |
|---|---|
| **Height (m)** | Crest elevation minus **Base y**. |
| **Crest width (m)** | Width of the flat crest. |
| **Left toe x (m)** | x-coordinate of the upstream (left) toe. |
| **Upstream slope H:V** | Horizontal : vertical on the inner face. **2.5** means 2.5 m horizontal for 1 m vertical (a 1V:2.5H slope). Larger = flatter. |
| **Downstream slope H:V** | Same definition on the outer face. |
| **Base y (m)** | Elevation of the dam base (usually 0). |

---

## Shared materials

Mohr–Coulomb effective-stress parameters. Slices below the phreatic line use the **saturated** unit weight; slices above it use the bulk unit weight. Pore pressure is \(\gamma_w \times\) depth under the phreatic line.

| Input | Meaning |
|---|---|
| **Name** | Legend label. |
| **Cohesion c′ (kPa)** | Effective cohesion. Rockfill (CFRD) is fixed at **0**. |
| **Friction φ′ (deg)** | Effective friction angle. |
| **Unit weight (kN/m³)** | Bulk (moist) unit weight above the phreatic line. |
| **Saturated unit weight (kN/m³)** | Unit weight of the same material when submerged. |

---

## Shared phreatic line

Type **x, y** in metres, **one pair per line**, for example:

```
200.0, 80.0
265.0, 36.0
530.0, 0.0
```

Points run from the upstream face toward the downstream toe. The **first point’s y** is the reservoir waterline for that dam. Lines starting with `#` are ignored.

- **Homogeneous** — seepage through the fill; typically a smooth drop from the pool to the downstream toe.
- **Clay core** — a flatter path through the core (higher head drop across the clay).
- **CFRD** — first point at the **reservoir waterline on the slab**, then an immediate drop **behind the face** so the rockfill stays nearly dry.

---

## Inputs — Homogeneous

Fill geometry, one fill material, and the homogeneous phreatic line (see tables above). The trial circle lives on **Centerpoint**, not here.

---

## Inputs — Clay core

Everything in **Homogeneous**, plus a second material and the core sizes. The trial circle is still the shared one on **Centerpoint**.

| Extra input | Meaning |
|---|---|
| **Core** material block | \(c'\), \(\varphi'\), unit weights of the **clay**, not the shell. |
| **Core crest width (m)** | Width of the core at crest level. The core is centred on the dam centreline. |
| **Core base width (m)** | Width of the core at the dam base. Larger than the crest width gives a tapered core. |

A slice that crosses the core uses clay strength inside the core polygon and shell strength outside it.

---

## Inputs — CFRD (rockfill with concrete face)

Rockfill has **no cohesion**. The central clay core uses the same strength model as the earthfill-with-core dam. The upstream slab is impervious: it adds weight on the inner face (important after drawdown, when the reservoir no longer supports that face) and the phreatic line drops behind the slab.

| Extra input | Meaning |
|---|---|
| **Core** material block | \(c'\), \(\varphi'\), unit weights of the **clay**, not the rockfill. |
| **Core crest width (m)** | Width of the core at crest level. The core is centred on the dam centreline. |
| **Core base width (m)** | Width of the core at the dam base. |
| **Slab thickness (m)** | Concrete thickness **normal to the upstream face**. |
| **Slab unit weight (kN/m³)** | Typically ~24 kN/m³. |

---

## Inputs — Plot extent

Same **x** and **y** window for every earthfill/rockfill panel (homogeneous, clay core, CFRD). The gravity-dam panel keeps its own scale. The figure updates when these numbers change.

| Input | Meaning |
|---|---|
| **x min (m)** | Left edge of the plot. |
| **x max (m)** | Right edge of the plot. |
| **y min (m)** | Bottom edge of the plot (often below the foundation). |
| **y max (m)** | Top edge of the plot. Increase it if the grid or circle centres are cut off. |

If min and max are swapped, the app orders them.

---

## How to read the result

FS = resisting shear / driving shear along the circular surface.

- **FS < 1** — that trial surface is not in equilibrium (unsafe).
- **FS ≈ 1** — limiting equilibrium.
- Compare dam types on the **same** circle or the **same** grid: a clay core and a CFRD are **not** expected to match a homogeneous fill.

After **Run analysis**, the number above the plot is Bishop FS with **PASS** or **FAIL** versus the **Safety factors** tab. Open **Detailed results** for centre, radius and slice count, and **Calculation log** for the full printout.
