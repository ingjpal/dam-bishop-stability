# Help: Concrete gravity dam

This tool checks a **concrete gravity monolith** (crest, upstream batter, two-slope downstream face, foundation block) for four limit states. Self-weight is the **polygon area** times \(\gamma_c\). All forces and moments are **per metre of dam length** (plane strain).

The default section is the classroom figure scaled to \(H = 100\) m (originally 103 m): base \(B = 68.16\) m (A to B), slope break **C** at 64.56 m, upstream batter \(1/24\), downstream \(1/6.54\) above C and \(1/1.38\) below C.

**Units:** length in m, unit weight in kN/m³, stress and cohesion in kPa. Factors of safety are dimensionless.

**Buttons (top right)**

- **Geometry refresh** — redraws the section and the reservoir. No factors of safety are calculated.
- **Run analysis** — computes the four checks.

Classroom targets default to **FoS = 1.5** (static) and **FoS = 1.3** (seismic). Change them on the **Safety factors** tab.

---

## Options (full-width bar)

Tick **Concrete gravity dam** under Dams and extras to show it on the 2×2 plot; untick to hide it. Inputs are on the **Gravity** tab.

**Loading**

| Choice | What is included | Target FoS |
|---|---|---|
| **Static** | Self-weight, hydrostatic water, uplift. \(k_h = k_v = 0\). | **Safety factors** tab, **Static loading** (default 1.5) |
| **Seismic** | Static loads plus dam inertia and a Westergaard-type hydrodynamic force on the upstream face. | **Safety factors** tab, **Seismic loading** (default 1.3) |

**Horizontal seismic \(k_h\)** (seismic only) — fraction of the dam weight applied as a **horizontal** inertia force toward downstream: \(F_{Eh} = k_h W\). Typical classroom values are 0.05–0.15. Larger \(k_h\) increases overturning and sliding demand.

**Vertical seismic \(k_v\)** (seismic only) — fraction of the dam weight applied **upward** (reduces the effective vertical load): \(F_{Ev} = k_v W\). That lowers \(\sum V\), which hurts sliding and can raise toe stress. Typical classroom values are about half of \(k_h\).

Uplift is a **triangle**: full reservoir head at the **heel A**, zero at the **toe B** (no drains modelled).

---

## Inputs — Gravity tab (geometry)

Slope \(1/n\) means **1 horizontal : n vertical** (as labelled on the figure).

| Input | Meaning |
|---|---|
| **Height H (m)** | Crest elevation above contact A–B. Default **100**. |
| **Base width B (m)** | Heel **A** to toe **B**. Default **68.16**. Sliding and bearing use this width. |
| **Slope-break height C (m)** | Height of point **C** on the downstream face, where the slope changes. Default **64.56**. |
| **Upstream batter 1/n** | Upstream face. Default **24** (\(1/24\)). |
| **Downstream upper 1/n** | Face from crest to C. Default **6.54**. |
| **Downstream lower 1/n** | Face from C to toe B. Default **1.38**. |
| **Upstream water hw (m)** | Reservoir depth. Must satisfy \(h_w \le H\). Default **37.86**. |
| **Foundation block thickness (m)** | Brown base drawn under A–B. For plotting only; it is **not** added to the dam weight. Default **11.65**. |

The crest width is computed from H, B, C and the three slopes so the polygon closes. A caption under the inputs shows crest width, concrete area and the centroid.

Self-weight \(W = A_\text{polygon}\,\gamma_c\) acts at the polygon centroid \((c_x, c_y)\) measured from heel A. Overturning moments are taken about the **toe B**, so the weight lever arm is \(B - c_x\).

Hydrostatic force on the battered upstream face: horizontal \(F_w = \tfrac12 \gamma_w h_w^2\) at \(h_w/3\) above the base, plus a small vertical component \(F_{w,v} = F_w / n_\text{up}\).

---

## Inputs — Materials

| Input | Meaning |
|---|---|
| **Concrete unit weight (kN/m³)** | \(\gamma_c\). Controls \(W\). Typical mass concrete is about **24 kN/m³**. |
| **Water unit weight (kN/m³)** | \(\gamma_w\). Use **9.81** unless the course specifies otherwise. |
| **Base friction μ** | Coefficient of friction on contact A–B. Sliding resistance includes \(\mu \sum V\). |
| **Base cohesion c (kPa)** | Extra sliding resistance \(c B\). Leave at **0** unless the course allows a bonded contact. |
| **Allowable bearing (kPa)** | Maximum permitted **toe** normal stress. |

---

## The four checks

After **Run analysis**, the gravity panel (and the metrics above the plot) report:

1. **Overturning** — moments about the **toe B**. Weight resists; water, uplift, inertia and hydrodynamic force drive.  
   \(F_O = M_\text{resisting} / M_\text{overturning}\). Pass if \(F_O \ge\) target FoS.

2. **Sliding** — horizontal shear on A–B.  
   Resistance \(= \mu \sum V + c B\).  
   \(\sum V = W - U - F_{Ev} - F_{w,v}\) and \(\sum H = F_w + F_{Eh} + F_{wd}\).

3. **Foundation bearing** — trapezoidal normal stress on A–B. The **toe** stress \(q_\text{toe}\) must stay \(\le q_\text{all}\).

4. **Heel tension (middle third)** — the resultant of \(\sum V\) should fall in the **middle third** of the base: \(e \le B/6\). Pass requires compression at the heel.

Seismic extras (only when Loading = Seismic):

- \(F_{Eh} = k_h W\) — horizontal inertia at the centroid height \(c_y\).
- \(F_{Ev} = k_v W\) — vertical inertia (upward) at \(c_x\).
- \(F_{wd} = 0.583\, k_h\, \gamma_w\, h_w^2\) — Westergaard-type hydrodynamic force, lever arm \(0.4\, h_w\).

---

## How to run

1. Tick **Concrete gravity dam** and choose **Static** or **Seismic**.
2. Check H, B, C, the three \(1/n\) slopes and \(h_w\) on the Gravity tab.
3. Press **Geometry refresh**, then **Run analysis**.
4. **PASS** / **FAIL** uses the target FoS, allowable bearing, and no tension at the heel.

---

## How to read the result

All four checks should pass for a first design. With the default 100 m / 68.16 m section, \(B/H \approx 0.68\), which is a usual gravity-dam proportion.

| If this fails | Typical classroom fix |
|---|---|
| Overturning | Increase **B**, lower **hw**, or reduce \(k_h\). |
| Sliding | Increase **B** or **μ**. Add **c** only if the course allows a bonded base. |
| Toe bearing | Increase **B** or raise **allowable bearing** only if the foundation data support it. |
| Heel tension | Increase **B** or lower **hw** so the resultant moves back into the middle third. |

**Gravity-dam detailed results** lists area, centroid, every force (\(W\), \(U\), \(F_w\), \(F_{w,v}\), \(F_{Eh}\), \(F_{Ev}\), \(F_{wd}\)) and \(e\) versus \(B/6\).
