"""
Classroom web app: Bishop earthfill/rockfill slope stability and gravity-dam checks.

Run locally:
    pip install -r requirements.txt
    streamlit run app.py
"""

from __future__ import annotations

import contextlib
import io
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import streamlit as st

import earthfill_dam_bishop as b
import gravity_dam as gd


st.set_page_config(
    page_title="Dam Stability Calculator",
    page_icon="△",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
      [data-testid="stMainBlockContainer"] {
        padding-top: 1.25rem;
      }
      .st-key-options_panel {
        padding: 0.35rem 0.8rem 0.4rem 0.8rem !important;
      }
      .st-key-options_panel [data-testid="stVerticalBlock"] {
        gap: 0.2rem !important;
      }
      .st-key-options_panel [data-testid="stHorizontalBlock"] {
        gap: 0.35rem !important;
      }
      .st-key-options_panel h3 {
        font-size: 1.05rem !important;
        margin: 0 !important;
        padding: 0 !important;
      }
      .st-key-options_panel [data-testid="stMarkdownContainer"] p,
      .st-key-options_panel [data-testid="stWidgetLabel"] p,
      .st-key-options_panel [data-testid="stCaptionContainer"] p {
        margin: 0 !important;
        padding: 0 !important;
      }
      .st-key-options_panel [data-testid="stRadio"],
      .st-key-options_panel [data-testid="stCheckbox"],
      .st-key-options_panel [data-testid="stNumberInput"] {
        margin-bottom: 0 !important;
        padding-top: 0 !important;
        padding-bottom: 0 !important;
      }
      .st-key-options_panel [data-testid="stRadio"] > div {
        gap: 0.4rem !important;
      }
      .st-key-options_panel label {
        min-height: 0 !important;
        padding-top: 0.05rem !important;
        padding-bottom: 0.05rem !important;
      }
      [data-testid="stHorizontalBlock"]:has(.st-key-inputs_panel) {
        align-items: start !important;
      }
      .st-key-plot_panel [data-testid="stImage"] {
        width: 100%;
      }
      .st-key-plot_panel img {
        width: 100% !important;
        max-width: 100% !important;
        height: auto !important;
        object-fit: contain !important;
        object-position: top left !important;
      }
    </style>
    """,
    unsafe_allow_html=True,
)


def points_to_text(points):
    return "\n".join(f"{x}, {y}" for x, y in points)


def text_to_points(text, fallback):
    pts = []
    for raw in text.strip().splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        line = line.replace(";", ",")
        parts = [p.strip() for p in line.split(",") if p.strip()]
        if len(parts) != 2:
            continue
        pts.append((float(parts[0]), float(parts[1])))
    return pts if len(pts) >= 2 else list(fallback)


def seed_100m_defaults():
    """Apply the 100 m geometry once so an existing Streamlit session picks it up."""
    if st.session_state.get("_defaults_v") == "h100":
        return
    st.session_state["_defaults_v"] = "h100"
    hom = b.HOMOGENEOUS_DAM
    core = b.CLAY_CORE_DAM
    cfrd = b.ROCKFILL_CFRD_DAM
    g = b.GRID_CONFIG
    r = b.RADIUS_CONFIG
    circ = hom["slip_circle"]
    gd_d = gd.DEFAULTS
    updates = {
        "homg_h": hom["geometry"]["height"],
        "homg_cw": hom["geometry"]["crest_width"],
        "coreg_h": core["geometry"]["height"],
        "coreg_cw": core["geometry"]["crest_width"],
        "cfrdg_h": cfrd["geometry"]["height"],
        "cfrdg_cw": cfrd["geometry"]["crest_width"],
        "cg_cw": core["core_geometry"]["crest_width"],
        "cg_bw": core["core_geometry"]["base_width"],
        "cfrd_cg_cw": cfrd["core_geometry"]["crest_width"],
        "cfrd_cg_bw": cfrd["core_geometry"]["base_width"],
        "trial_cx": circ["center_x"],
        "trial_cy": circ["center_y"],
        "trial_r": circ["radius"],
        "llx": g["lower_left_x"],
        "lly": g["lower_left_y"],
        "gw": g["grid_width"],
        "gh": g["grid_height"],
        "sx": g["grid_spacing_x"],
        "sy": g["grid_spacing_y"],
        "rmin": r["min_radius"],
        "rmax": r["max_radius"],
        "fth": b.FOUNDATION["thickness"],
        "few": b.FOUNDATION["extra_width"],
        "ft": cfrd["concrete_face"]["thickness"],
        "ph_hom": points_to_text(b.PHREATIC_LINE_HOMOGENEOUS),
        "ph_core": points_to_text(b.PHREATIC_LINE_CLAY_CORE),
        "ph_cfrd": points_to_text(b.PHREATIC_LINE_CFRD),
        "pxmin": b.PLOT_X_MIN,
        "pxmax": b.PLOT_X_MAX,
        "pymin": b.PLOT_Y_MIN,
        "pymax": b.PLOT_Y_MAX,
        "grav_H": gd_d["H"],
        "grav_B": gd_d["B"],
        "grav_hc": gd_d["h_C"],
        "grav_hw": gd_d["hw"],
        "grav_tb": gd_d["t_base"],
    }
    for key, value in updates.items():
        if key in st.session_state:
            st.session_state[key] = value


def number(label, value, key, step=0.1, fmt="%.2f", help_text=None):
    kwargs = {"step": float(step), "format": fmt, "key": key}
    if help_text:
        kwargs["help"] = help_text
    if key not in st.session_state:
        kwargs["value"] = float(value)
    return st.number_input(label, **kwargs)


def geometry_inputs(prefix, geom):
    c1, c2 = st.columns(2)
    with c1:
        height = number("Height (m)", geom["height"], f"{prefix}_h")
        crest = number("Crest width (m)", geom["crest_width"], f"{prefix}_cw")
        left = number("Left toe x (m)", geom["left_toe_x"], f"{prefix}_x0")
    with c2:
        up = number("Upstream slope H:V", geom["upstream_slope"], f"{prefix}_up")
        down = number("Downstream slope H:V", geom["downstream_slope"], f"{prefix}_dn")
        base = number("Base y (m)", geom["base_y"], f"{prefix}_by")
    return {
        "height": height,
        "crest_width": crest,
        "upstream_slope": up,
        "downstream_slope": down,
        "left_toe_x": left,
        "base_y": base,
    }


def material_inputs(prefix, props, cohesion=True):
    c1, c2 = st.columns(2)
    with c1:
        name = st.text_input("Name", value=props["name"], key=f"{prefix}_name")
        c = number("Cohesion c′ (kPa)", props["cohesion"], f"{prefix}_c") if cohesion else 0.0
        if not cohesion:
            st.caption("Rockfill: cohesion fixed at 0 kPa.")
        phi = number("Friction φ′ (deg)", props["friction_angle"], f"{prefix}_phi")
    with c2:
        g = number("Unit weight (kN/m³)", props["unit_weight"], f"{prefix}_g")
        gs = number(
            "Saturated unit weight (kN/m³)",
            props["saturated_unit_weight"],
            f"{prefix}_gs",
        )
    out = dict(props)
    out.update({
        "name": name,
        "cohesion": 0.0 if not cohesion else c,
        "friction_angle": phi,
        "unit_weight": g,
        "saturated_unit_weight": gs,
    })
    return out


def circle_inputs(prefix, circle):
    c1, c2, c3 = st.columns(3)
    with c1:
        cx = number("Centre x (m)", circle["center_x"], f"{prefix}_cx")
    with c2:
        cy = number("Centre y (m)", circle["center_y"], f"{prefix}_cy")
    with c3:
        r = number("Radius (m)", circle["radius"], f"{prefix}_r")
    return {"center_x": cx, "center_y": cy, "radius": r}


def _state_float(key, fallback):
    val = st.session_state.get(key, fallback)
    return float(val)


def _state_int(key, fallback):
    val = st.session_state.get(key, fallback)
    return int(val)


INNER_SLOPE = "Inner slope analysis"
RAPID_DRAWDOWN_ANALYSIS = "Rapid drawdown analysis"


def dam_mid_x():
    """Dam centreline x from the homogeneous geometry (widgets if present)."""
    g = b.HOMOGENEOUS_DAM["geometry"]
    h = float(st.session_state.get("homg_h", g["height"]))
    cw = float(st.session_state.get("homg_cw", g["crest_width"]))
    up = float(st.session_state.get("homg_up", g["upstream_slope"]))
    dn = float(st.session_state.get("homg_dn", g["downstream_slope"]))
    x0 = float(st.session_state.get("homg_x0", g["left_toe_x"]))
    return x0 + 0.5 * (cw + h * (up + dn))


def place_circle_and_grid_on_face(rapid):
    """Put the trial centre (and search grid) on the slope for this analysis."""
    xmid = dam_mid_x()
    d = b.HOMOGENEOUS_DAM["slip_circle"]
    cx = float(st.session_state.get("trial_cx", d["center_x"]))
    if rapid and cx > xmid:
        st.session_state["trial_cx"] = 2.0 * xmid - cx
    elif (not rapid) and cx < xmid:
        st.session_state["trial_cx"] = 2.0 * xmid - cx
    if "llx" in st.session_state and "gw" in st.session_state:
        llx = float(st.session_state["llx"])
        gw = float(st.session_state["gw"])
        gcx = llx + 0.5 * gw
        if rapid and gcx > xmid:
            st.session_state["llx"] = 2.0 * xmid - (llx + gw)
        elif (not rapid) and gcx < xmid:
            st.session_state["llx"] = 2.0 * xmid - (llx + gw)


def grid_fields():
    g = b.GRID_CONFIG
    gx1, gx2 = st.columns(2)
    with gx1:
        llx = number("Grid lower-left x (m)", g["lower_left_x"], "llx")
        w = number("Grid width (m)", g["grid_width"], "gw")
        sx = number("Spacing x (m)", g["grid_spacing_x"], "sx", step=1.0)
    with gx2:
        lly = number("Grid lower-left y (m)", g["lower_left_y"], "lly")
        h = number("Grid height (m)", g["grid_height"], "gh")
        sy = number("Spacing y (m)", g["grid_spacing_y"], "sy", step=1.0)
    r1, r2, r3 = st.columns(3)
    with r1:
        rmin = number("Min radius (m)", b.RADIUS_CONFIG["min_radius"], "rmin")
    with r2:
        rmax = number("Max radius (m)", b.RADIUS_CONFIG["max_radius"], "rmax")
    with r3:
        nr = st.number_input(
            "Number of radii", min_value=2, max_value=20,
            value=int(b.RADIUS_CONFIG["num_radii"]), step=1, key="nr",
        )
    search_slices = st.number_input(
        "Slices during search", min_value=8, max_value=50,
        value=int(b.SEARCH_NUM_SLICES), step=1, key="ss",
    )
    max_fs = number("Heatmap FS colour cap", b.MAX_DISPLAY_FS, "maxfs", step=0.5)
    num_slices = reported_slices_input()
    return {
        "grid": {
            "lower_left_x": llx,
            "lower_left_y": lly,
            "grid_width": w,
            "grid_height": h,
            "grid_spacing_x": sx,
            "grid_spacing_y": sy,
        },
        "radii": {"min_radius": rmin, "max_radius": rmax, "num_radii": int(nr)},
        "search_slices": search_slices,
        "max_fs": max_fs,
        "num_slices": num_slices,
    }


def grid_fields_from_state():
    g = b.GRID_CONFIG
    r = b.RADIUS_CONFIG
    return {
        "grid": {
            "lower_left_x": _state_float("llx", g["lower_left_x"]),
            "lower_left_y": _state_float("lly", g["lower_left_y"]),
            "grid_width": _state_float("gw", g["grid_width"]),
            "grid_height": _state_float("gh", g["grid_height"]),
            "grid_spacing_x": _state_float("sx", g["grid_spacing_x"]),
            "grid_spacing_y": _state_float("sy", g["grid_spacing_y"]),
        },
        "radii": {
            "min_radius": _state_float("rmin", r["min_radius"]),
            "max_radius": _state_float("rmax", r["max_radius"]),
            "num_radii": _state_int("nr", r["num_radii"]),
        },
        "search_slices": _state_int("ss", b.SEARCH_NUM_SLICES),
        "max_fs": _state_float("maxfs", b.MAX_DISPLAY_FS),
    }


def centerpoint_fields():
    st.caption(
        "One trial circle for every ticked earthfill/rockfill dam. "
        "Switching **Inner slope analysis** / **Rapid drawdown analysis** "
        "moves the centre onto that face and updates Centre x to match. "
        "The plotted circle uses these numbers."
    )
    circ = circle_inputs("trial", b.HOMOGENEOUS_DAM["slip_circle"])
    num_slices = reported_slices_input()
    return circ, num_slices


def centerpoint_from_state():
    d = b.HOMOGENEOUS_DAM["slip_circle"]
    return {
        "center_x": _state_float("trial_cx", d["center_x"]),
        "center_y": _state_float("trial_cy", d["center_y"]),
        "radius": _state_float("trial_r", d["radius"]),
    }


def reported_slices_input():
    return st.number_input(
        "Slices for the reported circle",
        min_value=10, max_value=80,
        value=int(b.NUM_SLICES), step=1, key="ns",
        help="Vertical slices used for the printed factor of safety. "
             "After a grid search the critical circle is re-run with this count.",
    )


def safety_factor_fields():
    st.caption(
        "Minimum factor of safety for a PASS. After Run analysis, each check is "
        "PASS if the calculated FS is at least this value."
    )
    st.markdown("Earthfill / rockfill (Bishop)")
    c1, c2 = st.columns(2)
    with c1:
        fs_inner = number(
            "Inner slope analysis", 1.5, "fs_inner", step=0.05, fmt="%.2f",
            help_text="Usual classroom static check is 1.5.",
        )
    with c2:
        fs_dd = number(
            "Rapid drawdown analysis", 1.3, "fs_dd", step=0.05, fmt="%.2f",
            help_text="Often lower than the inner-slope (steady) requirement.",
        )
    st.markdown("Concrete gravity dam")
    g1, g2 = st.columns(2)
    with g1:
        fos_static = number(
            "Static loading", 1.5, "fos_static", step=0.05, fmt="%.2f",
        )
    with g2:
        fos_seismic = number(
            "Seismic loading", 1.3, "fos_seismic", step=0.05, fmt="%.2f",
        )
    return {
        "fs_inner": fs_inner,
        "fs_dd": fs_dd,
        "fos_static": fos_static,
        "fos_seismic": fos_seismic,
    }


def plot_extent_fields():
    st.caption(
        "x and y window for every earthfill/rockfill panel. "
        "The gravity-dam panel keeps its own scale."
    )
    c1, c2 = st.columns(2)
    with c1:
        x_min = number("x min (m)", b.PLOT_X_MIN, "pxmin", step=5.0)
        y_min = number("y min (m)", b.PLOT_Y_MIN, "pymin", step=5.0)
    with c2:
        x_max = number("x max (m)", b.PLOT_X_MAX, "pxmax", step=5.0)
        y_max = number("y max (m)", b.PLOT_Y_MAX, "pymax", step=5.0)
    return {
        "x_min": x_min,
        "x_max": x_max,
        "y_min": y_min,
        "y_max": y_max,
    }


def apply_to_engine(ui):
    b.RAPID_DRAWDOWN = ui["rapid"]
    if ui["ph_hom"]:
        b.NORMAL_RESERVOIR_LEVEL = float(ui["ph_hom"][0][1])
    b.PHREATIC_LINE_HOMOGENEOUS = ui["ph_hom"]
    b.PHREATIC_LINE_CLAY_CORE = ui["ph_core"]
    b.PHREATIC_LINE_CFRD = ui["ph_cfrd"]
    b.FIND_CRITICAL_CIRCLE = ui["grid_search"]
    b.GRID_CONFIG.update(ui["grid"])
    b.RADIUS_CONFIG.update(ui["radii"])
    b.SEARCH_NUM_SLICES = int(ui["search_slices"])
    b.MAX_DISPLAY_FS = ui["max_fs"]
    b.NUM_SLICES = int(ui["num_slices"])
    b.DRAW_SLICES = ui["draw_slices"]
    b.REQUIRED_FS_INNER = float(ui["fs_inner"])
    b.REQUIRED_FS_DRAWDOWN = float(ui["fs_dd"])
    x0, x1 = ui["x_min"], ui["x_max"]
    y0, y1 = ui["y_min"], ui["y_max"]
    if x1 < x0:
        x0, x1 = x1, x0
    if y1 < y0:
        y0, y1 = y1, y0
    b.PLOT_X_MIN = x0
    b.PLOT_X_MAX = x1
    b.PLOT_Y_MIN = y0
    b.PLOT_Y_MAX = y1
    b.Y_AXIS_MAX = y1
    b.SHOW_PLOT = False
    b.SAVE_FIGURE = False

    foundation = dict(b.FOUNDATION)
    foundation.update(ui["foundation"])
    b.FOUNDATION.clear()
    b.FOUNDATION.update(foundation)

    def attach_foundation(dam):
        dam["foundation"] = dict(b.FOUNDATION) if ui["use_foundation"] else None

    h = b.HOMOGENEOUS_DAM
    h["enabled"] = ui["en_hom"]
    h["geometry"] = ui["geom_hom"]
    h["fill"] = ui["fill_hom"]
    h["slip_circle"] = ui["circ_hom"]
    h["include_reservoir_water_weight"] = ui["water_weight"]
    attach_foundation(h)

    c = b.CLAY_CORE_DAM
    c["enabled"] = ui["en_core"]
    c["geometry"] = ui["geom_core"]
    c["fill"] = ui["fill_core"]
    c["core"] = ui["core_mat"]
    c["core_geometry"] = ui["core_geom"]
    c["slip_circle"] = ui["circ_core"]
    c["include_reservoir_water_weight"] = ui["water_weight"]
    attach_foundation(c)

    r = b.ROCKFILL_CFRD_DAM
    r["enabled"] = ui["en_cfrd"]
    r["geometry"] = ui["geom_cfrd"]
    r["fill"] = ui["fill_cfrd"]
    r["core"] = ui["core_mat_cfrd"]
    r["core_geometry"] = ui["core_geom_cfrd"]
    r["concrete_face"] = ui["face"]
    r["slip_circle"] = ui["circ_cfrd"]
    r["include_reservoir_water_weight"] = ui["water_weight"]
    attach_foundation(r)


def bishop_required_fs(ui):
    return float(ui["fs_dd"] if ui.get("rapid") else ui["fs_inner"])


def gravity_target_fs(ui, seismic=None):
    if seismic is None:
        seismic = ui.get("loading") == "Seismic"
    return float(ui["fos_seismic"] if seismic else ui["fos_static"])


def apply_gravity_targets(r, ui):
    if not r:
        return r
    target = gravity_target_fs(ui, r.get("seismic"))
    r["target_FoS"] = target
    r["pass_O"] = r["FoS_O"] >= target
    r["pass_S"] = r["FoS_S"] >= target
    return r


def format_results(cases, required):
    lines = []
    for case in cases:
        result = case.get("result")
        lines.append(case["title"])
        if result is None:
            lines.append("  No valid slip surface for this setting.")
            lines.append("  Verdict: FAIL")
        else:
            cx, cy = result["center"]
            fos = result["fos"]
            verdict = "PASS" if fos >= required else "FAIL"
            lines.append(f"  FS = {fos:.3f}   required ≥ {required:.2f}   [{verdict}]")
            lines.append(f"  Centre ({cx:.1f}, {cy:.1f}) m   R = {result['radius']:.1f} m")
            lines.append(f"  Slices = {len(result['slices'])}")
        lines.append("")
    return "\n".join(lines).strip()


def figure_to_png(fig):
    png = io.BytesIO()
    fig.savefig(png, format="png", dpi=140, bbox_inches="tight")
    plt.close(fig)
    return png.getvalue()


def show_plot(png):
    with st.container(key="plot_panel"):
        st.image(png, width="stretch")


def format_gravity(r):
    def mark(ok):
        return "PASS" if ok else "FAIL"

    loading = "seismic" if r["seismic"] else "static"
    heel = "compression" if r["pass_C"] else "TENSION"
    return "\n".join([
        f"Concrete gravity dam  H = {r['H']:.1f} m   B = {r['B']:.1f} m   hw = {r['hw']:.1f} m",
        f"Crest = {r['crest']:.2f} m   break C at {r['h_C']:.1f} m   area = {r['area']:.0f} m²/m",
        f"Centroid ({r['cx']:.2f}, {r['cy']:.2f}) m from heel A",
        f"Loading: {loading}   target FoS = {r['target_FoS']:.1f}",
        "",
        f"Overturning   FoS = {r['FoS_O']:.3f}   [{mark(r['pass_O'])}]",
        f"Sliding       FoS = {r['FoS_S']:.3f}   [{mark(r['pass_S'])}]",
        f"Toe stress    {r['q_toe']:.0f} kPa  (allowable {r['q_all']:g} kPa)  [{mark(r['pass_B'])}]",
        f"Heel stress   {r['q_heel']:.0f} kPa  ({heel})  [{mark(r['pass_C'])}]",
        f"Eccentricity  e = {r['e']:.2f} m   middle-third limit B/6 = {r['e_max']:.2f} m",
        "",
        f"W = {r['W']:.0f} kN/m    U = {r['U']:.0f} kN/m    Fw = {r['Fw']:.0f} kN/m   Fw,v = {r['Fw_v']:.0f} kN/m",
        f"ΣV = {r['sum_V']:.0f} kN/m    ΣH = {r['sum_H']:.0f} kN/m",
        f"F_Eh = {r['F_Eh']:.0f} kN/m    F_Ev = {r['F_Ev']:.0f} kN/m    F_wd = {r['F_wd']:.0f} kN/m",
    ])


def show_bishop_metrics(cases, required):
    if not cases:
        return
    cols = st.columns(len(cases))
    for col, case in zip(cols, cases):
        title = case["title"].split("—")[0].strip()
        result = case.get("result")
        with col:
            if result is None:
                st.metric(title, "—", "FAIL")
            else:
                fos = result["fos"]
                ok = fos >= required
                st.metric(
                    title, f"{fos:.2f}",
                    f"{'PASS' if ok else 'FAIL'}  (≥ {required:.2f})",
                    delta_color="off",
                    help="Bishop factor of safety versus the Safety factors tab.",
                )


def show_gravity_metrics(r):
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Overturning FoS", f"{r['FoS_O']:.2f}", "PASS" if r["pass_O"] else "FAIL")
    c2.metric("Sliding FoS", f"{r['FoS_S']:.2f}", "PASS" if r["pass_S"] else "FAIL")
    c3.metric("Toe stress (kPa)", f"{r['q_toe']:.0f}", "PASS" if r["pass_B"] else "FAIL")
    c4.metric("Heel", "Compression" if r["pass_C"] else "Tension", "PASS" if r["pass_C"] else "FAIL")


def bishop_options():
    c1, c2 = st.columns([1.15, 1.55], gap="small")
    with c1:
        water = st.radio(
            "Slope analysis",
            (INNER_SLOPE, RAPID_DRAWDOWN_ANALYSIS),
            horizontal=True,
            key="analysis_mode",
            help="Inner slope analysis: reservoir at the first phreatic-line elevation, "
                 "slip circle on the downstream face. "
                 "Rapid drawdown analysis: empty reservoir, slip circle on the upstream face, "
                 "phreatic held from that first point.",
        )
        rapid_mode = water == RAPID_DRAWDOWN_ANALYSIS
        if st.session_state.get("_analysis_mode") != water:
            place_circle_and_grid_on_face(rapid_mode)
            st.session_state["_analysis_mode"] = water
    with c2:
        mode = st.radio(
            "Slip surface",
            ("Single trial circle", "Grid search for critical circle"),
            index=0,
            horizontal=True,
            help="Grid search tests many centres and radii. It is slower (often 1–3 minutes).",
        )
    st.caption("Dams and extras")
    d1, d2, d3, d4 = st.columns(4, gap="small")
    with d1:
        en_hom = st.checkbox("Homogeneous earthfill", value=True)
    with d2:
        en_core = st.checkbox("Earthfill with clay core", value=True)
    with d3:
        en_cfrd = st.checkbox("Rockfill with concrete face", value=True)
    with d4:
        en_grav = st.checkbox("Concrete gravity dam", value=True)
    e1, e2, e3 = st.columns(3, gap="small")
    with e1:
        use_foundation = st.checkbox("Include foundation (deeper circles)", value=True)
    with e2:
        water_weight = st.checkbox("Reservoir water weight on upstream face", value=True)
    with e3:
        draw_slices = st.checkbox(
            "Draw slices on the plot", value=True, key="draw_slices",
            help="Vertical Bishop slices on the trial circle, and on the reported circle after Run analysis.",
        )
    gravity_opt = {"loading": "Static", "k_h": 0.0, "k_v": 0.0}
    if en_grav:
        gravity_opt = gravity_options()
    return {
        "rapid": water == RAPID_DRAWDOWN_ANALYSIS,
        "grid_search": mode == "Grid search for critical circle",
        "en_hom": en_hom,
        "en_core": en_core,
        "en_cfrd": en_cfrd,
        "en_grav": en_grav,
        "use_foundation": use_foundation,
        "water_weight": water_weight,
        "draw_slices": draw_slices,
        **gravity_opt,
    }


def bishop_input_tabs(grid_search):
    if grid_search:
        tab_names = ["Grid", "Safety factors", "Foundation", "Homogeneous", "Clay core", "CFRD", "Gravity", "Plot extent"]
    else:
        tab_names = ["Centerpoint", "Safety factors", "Foundation", "Homogeneous", "Clay core", "CFRD", "Gravity", "Plot extent"]
    tabs = st.tabs(tab_names)
    tab_mode, tab_fs, tab_found, tab_hom, tab_core, tab_cfrd, tab_grav, tab_extent = tabs
    if grid_search:
        with tab_mode:
            grid_vals = grid_fields()
        circ = centerpoint_from_state()
        num_slices = grid_vals.pop("num_slices")
    else:
        with tab_mode:
            circ, num_slices = centerpoint_fields()
        grid_vals = grid_fields_from_state()
    with tab_fs:
        fs_vals = safety_factor_fields()
    with tab_found:
        f = b.FOUNDATION
        foundation = material_inputs("found", f)
        ft1, ft2 = st.columns(2)
        with ft1:
            foundation["thickness"] = number("Thickness (m)", f["thickness"], "fth")
        with ft2:
            foundation["extra_width"] = number("Extra width beyond toes (m)", f["extra_width"], "few")
    with tab_hom:
        geom_hom = geometry_inputs("homg", b.HOMOGENEOUS_DAM["geometry"])
        fill_hom = material_inputs("homf", b.HOMOGENEOUS_DAM["fill"])
        ph_hom = text_to_points(
            st.text_area(
                "Phreatic line (x, y per line, m)",
                value=points_to_text(b.PHREATIC_LINE_HOMOGENEOUS),
                key="ph_hom",
                height=90,
            ),
            b.PHREATIC_LINE_HOMOGENEOUS,
        )
    with tab_core:
        geom_core = geometry_inputs("coreg", b.CLAY_CORE_DAM["geometry"])
        fill_core = material_inputs("coref", b.CLAY_CORE_DAM["fill"])
        core_mat = material_inputs("corem", b.CLAY_CORE_DAM["core"])
        cg = b.CLAY_CORE_DAM["core_geometry"]
        cc1, cc2 = st.columns(2)
        with cc1:
            core_cw = number("Core crest width (m)", cg["crest_width"], "cg_cw")
        with cc2:
            core_bw = number("Core base width (m)", cg["base_width"], "cg_bw")
        core_geom = {"crest_width": core_cw, "base_width": core_bw, "center_x": None}
        ph_core = text_to_points(
            st.text_area(
                "Phreatic line (x, y per line, m)",
                value=points_to_text(b.PHREATIC_LINE_CLAY_CORE),
                key="ph_core",
                height=90,
            ),
            b.PHREATIC_LINE_CLAY_CORE,
        )
    with tab_cfrd:
        geom_cfrd = geometry_inputs("cfrdg", b.ROCKFILL_CFRD_DAM["geometry"])
        fill_cfrd = material_inputs("cfrdf", b.ROCKFILL_CFRD_DAM["fill"], cohesion=False)
        core_mat_cfrd = material_inputs("cfrdcore", b.ROCKFILL_CFRD_DAM["core"])
        cg_r = b.ROCKFILL_CFRD_DAM["core_geometry"]
        rc1, rc2 = st.columns(2)
        with rc1:
            r_core_cw = number("Core crest width (m)", cg_r["crest_width"], "cfrd_cg_cw")
        with rc2:
            r_core_bw = number("Core base width (m)", cg_r["base_width"], "cfrd_cg_bw")
        core_geom_cfrd = {
            "crest_width": r_core_cw, "base_width": r_core_bw, "center_x": None,
        }
        face0 = b.ROCKFILL_CFRD_DAM["concrete_face"]
        fc1, fc2 = st.columns(2)
        with fc1:
            ft = number("Slab thickness (m)", face0["thickness"], "ft")
        with fc2:
            fg = number("Slab unit weight (kN/m³)", face0["unit_weight"], "fg")
        face = {"name": "Concrete face", "thickness": ft, "unit_weight": fg}
        ph_cfrd = text_to_points(
            st.text_area(
                "Phreatic line (x, y per line, m)",
                value=points_to_text(b.PHREATIC_LINE_CFRD),
                key="ph_cfrd",
                height=90,
            ),
            b.PHREATIC_LINE_CFRD,
        )
    with tab_grav:
        grav = gravity_fields()
    with tab_extent:
        plot_lims = plot_extent_fields()
    return {
        **grid_vals,
        "foundation": foundation,
        "geom_hom": geom_hom,
        "fill_hom": fill_hom,
        "circ_hom": circ,
        "ph_hom": ph_hom,
        "geom_core": geom_core,
        "fill_core": fill_core,
        "core_mat": core_mat,
        "core_geom": core_geom,
        "circ_core": circ,
        "ph_core": ph_core,
        "geom_cfrd": geom_cfrd,
        "fill_cfrd": fill_cfrd,
        "core_mat_cfrd": core_mat_cfrd,
        "core_geom_cfrd": core_geom_cfrd,
        "face": face,
        "circ_cfrd": circ,
        "ph_cfrd": ph_cfrd,
        "num_slices": num_slices,
        **fs_vals,
        **plot_lims,
        **grav,
    }


HELP_DIR = Path(__file__).resolve().parent


def show_help():
    with st.expander("Help — how to use this tool"):
        st.markdown((HELP_DIR / "help_bishop.md").read_text(encoding="utf-8"))
        st.markdown("---")
        st.markdown((HELP_DIR / "help_gravity.md").read_text(encoding="utf-8"))


def title_with_actions(title, refresh_key, run_key):
    left, mid, right = st.columns([0.56, 0.22, 0.22], vertical_alignment="bottom")
    with left:
        st.title(title)
    with mid:
        refresh = st.button("Geometry refresh", width="stretch", key=refresh_key)
    with right:
        run = st.button("Run analysis", type="primary", width="stretch", key=run_key)
    return refresh, run


def dam_key(case):
    title = case["title"].lower()
    if "clay" in title:
        return "core"
    if "concrete" in title or "rockfill" in title:
        return "cfrd"
    return "hom"


def current_bishop_cases(ui):
    stored = st.session_state.get("bishop_cases") or []
    preview = st.session_state.get("is_preview", True)
    stored_map = {}
    if stored and not preview:
        for case in stored:
            stored_map[dam_key(case)] = case
    out = []
    for flag, cfg, key in (
        ("en_hom", b.HOMOGENEOUS_DAM, "hom"),
        ("en_core", b.CLAY_CORE_DAM, "core"),
        ("en_cfrd", b.ROCKFILL_CFRD_DAM, "cfrd"),
    ):
        if not ui[flag]:
            continue
        if key in stored_map:
            out.append(stored_map[key])
        else:
            out.append(b.geometry_case(cfg))
    return out


def draw_bishop_case(ax, fig, case, ui, grid_cfg):
    if case.get("fos_grid") is not None:
        b.draw_search_panel(ax, fig, case, grid_cfg)
    elif case.get("result") is not None:
        b.draw_analysis_panel(ax, case, grid_cfg)
    else:
        b.draw_geometry_panel(
            ax, case, show_grid=bool(ui.get("grid_search")), grid_cfg=grid_cfg,
        )


def combined_figure(bishop_cases, ui, gravity_result=None):
    n_b = len(bishop_cases)
    n_g = 1 if ui.get("en_grav") else 0
    n = n_b + n_g
    fig, axes = b.grid_figure(n)
    if n == 0:
        return fig
    grid_cfg = None
    if n_b:
        grid_cfg = b.placed_grid_config(bishop_cases[0]["dam"])
    i = 0
    for case in bishop_cases:
        draw_bishop_case(axes[i], fig, case, ui, grid_cfg)
        i += 1
    if n_g:
        try:
            gd.draw_section(
                axes[i],
                result=gravity_result,
                **{k: ui[k] for k in gd.GEOM_KEYS},
            )
        except Exception:
            axes[i].text(0.5, 0.5, "Invalid gravity geometry",
                         ha="center", va="center", transform=axes[i].transAxes)
            axes[i].set_axis_off()
    fig.tight_layout()
    return fig


def gravity_analyse_kwargs(ui):
    keys = list(gd.GEOM_KEYS) + [
        "gamma_c", "gamma_w", "mu", "c", "q_all", "k_h", "k_v",
    ]
    out = {k: ui[k] for k in keys}
    out["target_static"] = ui["fos_static"]
    out["target_seismic"] = ui["fos_seismic"]
    return out


def rebuild_plot(ui):
    apply_to_engine(ui)
    cases = current_bishop_cases(ui)
    grav = None
    if ui.get("en_grav") and not st.session_state.get("is_preview", True):
        grav = st.session_state.get("gravity_result")
    fig = combined_figure(cases, ui, gravity_result=grav)
    st.session_state["plot_png"] = figure_to_png(fig)


def combined_results(ui, refresh, run):
    any_bishop = ui["en_hom"] or ui["en_core"] or ui["en_cfrd"]
    any_dam = any_bishop or ui["en_grav"]
    dam_sig = (ui["en_hom"], ui["en_core"], ui["en_cfrd"], ui["en_grav"], "face-follow-v1")
    sig_changed = st.session_state.get("dam_sig") != dam_sig
    st.session_state["dam_sig"] = dam_sig
    extent_sig = (ui["x_min"], ui["x_max"], ui["y_min"], ui["y_max"])
    extent_changed = st.session_state.get("extent_sig") != extent_sig
    st.session_state["extent_sig"] = extent_sig
    water_sig = (
        ui["rapid"],
        tuple(ui["ph_hom"]),
        tuple(ui["ph_core"]),
        tuple(ui["ph_cfrd"]),
    )
    water_changed = st.session_state.get("water_sig") != water_sig
    st.session_state["water_sig"] = water_sig
    circ = ui.get("circ_hom") or {}
    circ_sig = (
        circ.get("center_x"),
        circ.get("center_y"),
        circ.get("radius"),
        ui.get("grid_search"),
    )
    circ_changed = st.session_state.get("circ_sig") != circ_sig
    st.session_state["circ_sig"] = circ_sig
    slice_sig = (bool(ui.get("draw_slices")), int(ui.get("num_slices") or 0))
    slice_changed = st.session_state.get("slice_sig") != slice_sig
    st.session_state["slice_sig"] = slice_sig
    fs_sig = (
        ui.get("fs_inner"), ui.get("fs_dd"),
        ui.get("fos_static"), ui.get("fos_seismic"),
    )
    fs_changed = st.session_state.get("fs_sig") != fs_sig
    st.session_state["fs_sig"] = fs_sig

    if run:
        if not any_dam:
            st.error("Select at least one dam type.")
        elif ui["en_grav"] and ui["hw"] > ui["H"]:
            st.error("Water depth hw cannot exceed dam height H.")
        elif ui["en_grav"] and (ui["B"] <= 0 or ui["H"] <= 0):
            st.error("Gravity-dam height and base width must be positive.")
        else:
            apply_to_engine(ui)
            spinner = (
                "Searching the grid. This can take a couple of minutes…"
                if ui["grid_search"] and any_bishop
                else "Evaluating the selected dams…"
            )
            with st.spinner(spinner):
                try:
                    if any_bishop:
                        buf = io.StringIO()
                        with contextlib.redirect_stdout(buf):
                            cases, fig_b = b.run(return_figure=True)
                        plt.close(fig_b)
                        st.session_state["bishop_cases"] = cases
                        st.session_state["bishop_summary"] = format_results(
                            cases, bishop_required_fs(ui),
                        )
                        st.session_state["bishop_log"] = buf.getvalue()
                    else:
                        st.session_state.pop("bishop_cases", None)
                        st.session_state.pop("bishop_summary", None)
                        st.session_state.pop("bishop_log", None)
                    if ui["en_grav"]:
                        results = gd.analyse(**gravity_analyse_kwargs(ui))
                        st.session_state["gravity_result"] = results
                        st.session_state["gravity_summary"] = format_gravity(results)
                    else:
                        st.session_state.pop("gravity_result", None)
                        st.session_state.pop("gravity_summary", None)
                    st.session_state["is_preview"] = False
                    rebuild_plot(ui)
                except Exception as exc:
                    st.exception(exc)
                else:
                    st.rerun()
    elif refresh or sig_changed or extent_changed or water_changed or circ_changed or slice_changed or fs_changed or "plot_png" not in st.session_state:
        if not any_dam:
            st.error("Select at least one dam type.")
            st.session_state.pop("plot_png", None)
        else:
            drop_bishop = refresh or (circ_changed and not ui.get("grid_search"))
            if drop_bishop:
                st.session_state["is_preview"] = True
                st.session_state.pop("bishop_cases", None)
                st.session_state.pop("bishop_summary", None)
                st.session_state.pop("bishop_log", None)
            if refresh:
                st.session_state.pop("gravity_result", None)
                st.session_state.pop("gravity_summary", None)
            elif fs_changed and st.session_state.get("gravity_result"):
                apply_gravity_targets(st.session_state["gravity_result"], ui)
                st.session_state["gravity_summary"] = format_gravity(
                    st.session_state["gravity_result"]
                )
            if fs_changed and st.session_state.get("bishop_cases"):
                st.session_state["bishop_summary"] = format_results(
                    st.session_state["bishop_cases"], bishop_required_fs(ui),
                )
            try:
                apply_to_engine(ui)
                rebuild_plot(ui)
            except Exception as exc:
                st.exception(exc)

    preview = st.session_state.get("is_preview", True)
    shown_cases = [
        c for c in (st.session_state.get("bishop_cases") or [])
        if (dam_key(c) == "hom" and ui["en_hom"])
        or (dam_key(c) == "core" and ui["en_core"])
        or (dam_key(c) == "cfrd" and ui["en_cfrd"])
    ]
    if shown_cases and not preview:
        show_bishop_metrics(shown_cases, bishop_required_fs(ui))
    if ui.get("en_grav") and st.session_state.get("gravity_result") and not preview:
        show_gravity_metrics(st.session_state["gravity_result"])

    if "plot_png" in st.session_state:
        show_plot(st.session_state["plot_png"])
    else:
        st.info("Set the options and press Geometry refresh or Run analysis.")

    if st.session_state.get("bishop_summary") and shown_cases and not preview:
        with st.expander("Bishop detailed results", expanded=True):
            st.code(st.session_state["bishop_summary"], language=None)
    if ui.get("en_grav") and st.session_state.get("gravity_summary") and not preview:
        with st.expander("Gravity-dam detailed results", expanded=True):
            st.code(st.session_state["gravity_summary"], language=None)
    if st.session_state.get("bishop_log") and shown_cases and not preview:
        with st.expander("Calculation log"):
            st.text(st.session_state["bishop_log"])


def gravity_options():
    d = gd.DEFAULTS
    c1, c2, c3 = st.columns(3, gap="small")
    with c1:
        loading = st.radio(
            "Loading",
            ("Static", "Seismic"),
            index=1 if (d["k_h"] or d["k_v"]) else 0,
            horizontal=True,
            help="Static / seismic target FoS are set on the Safety factors tab. "
                 "Seismic adds inertia plus Westergaard hydrodynamic force.",
        )
    k_h = 0.0
    k_v = 0.0
    if loading == "Seismic":
        with c2:
            k_h = number("Horizontal seismic k_h", d["k_h"], "gd_kh", step=0.01, fmt="%.3f")
        with c3:
            k_v = number("Vertical seismic k_v", d["k_v"], "gd_kv", step=0.01, fmt="%.3f")
    return {"loading": loading, "k_h": k_h, "k_v": k_v}


def gravity_fields():
    d = gd.DEFAULTS
    st.markdown("Section (as in the typical monolith: crest, batter, two-slope downstream)")
    H = number("Height H (m)", d["H"], "grav_H", step=1.0)
    B = number("Base width B, A to B (m)", d["B"], "grav_B", step=0.1)
    h_C = number("Slope-break height C (m)", d["h_C"], "grav_hc", step=0.5)
    n_up = number("Upstream batter 1/n", d["n_up"], "grav_nup", step=0.5)
    n_dn_u = number("Downstream upper 1/n", d["n_dn_u"], "grav_ndu", step=0.01)
    n_dn_l = number("Downstream lower 1/n", d["n_dn_l"], "grav_ndl", step=0.01)
    hw = number("Upstream water hw (m)", d["hw"], "grav_hw", step=1.0)
    t_base = number("Foundation block thickness (m)", d["t_base"], "grav_tb", step=0.5)
    try:
        g = gd.make_geometry(
            H=H, B=B, h_C=h_C, n_up=n_up, n_dn_u=n_dn_u, n_dn_l=n_dn_l,
            hw=hw, t_base=t_base,
        )
        st.caption(
            f"Crest width = {g['crest']:.2f} m   "
            f"concrete area = {g['area']:.0f} m²/m   "
            f"centroid x = {g['cx']:.2f} m from heel A."
        )
    except ValueError as exc:
        st.warning(str(exc))
    st.markdown("Materials")
    gamma_c = number("Concrete unit weight (kN/m³)", d["gamma_c"], "gd_gc")
    gamma_w = number("Water unit weight (kN/m³)", d["gamma_w"], "gd_gw")
    mu = number("Base friction μ", d["mu"], "gd_mu", step=0.05)
    cohesion = number("Base cohesion c (kPa)", d["c"], "gd_c")
    q_all = number("Allowable bearing (kPa)", d["q_all"], "gd_qall", step=50.0)
    return {
        "H": H, "B": B, "h_C": h_C,
        "n_up": n_up, "n_dn_u": n_dn_u, "n_dn_l": n_dn_l,
        "hw": hw, "t_base": t_base,
        "gamma_c": gamma_c, "gamma_w": gamma_w,
        "mu": mu, "c": cohesion, "q_all": q_all,
    }


seed_100m_defaults()
refresh, run = title_with_actions("Dam Stability Calculator", "geo_all", "run_all")
st.caption(
    "Bishop simplified method for earthfill/rockfill and limit-equilibrium checks for a gravity dam. "
    "Units: lengths in m, unit weights in kN/m³, cohesion in kPa. "
    "Tick a dam under **Dams and extras** to show it on the 2×2 plot. "
    "Use **Geometry refresh** to update sections without calculating FS."
)

with st.container(border=True, key="options_panel"):
    st.subheader("Options")
    bishop_opt = bishop_options()

inp_col, plot_col = st.columns([0.38, 0.62], gap="large")
with inp_col:
    with st.container(border=True, key="inputs_panel"):
        st.subheader("Inputs")
        ui = {**bishop_opt, **bishop_input_tabs(bishop_opt["grid_search"])}

with plot_col:
    combined_results(ui, refresh, run)

show_help()

