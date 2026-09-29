"""
Classroom web app for Bishop dam slope-stability analysis.

Run locally:
    pip install -r requirements.txt
    streamlit run app.py
"""

from __future__ import annotations

import contextlib
import io

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import streamlit as st

import earthfill_dam_bishop as b


st.set_page_config(
    page_title="Dam slope stability (Bishop)",
    page_icon="△",
    layout="wide",
    initial_sidebar_state="collapsed",
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


def number(label, value, key, step=0.1, fmt="%.2f", help_text=None):
    return st.number_input(
        label, value=float(value), step=float(step), format=fmt, key=key,
        help=help_text,
    )


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


def apply_to_engine(ui):
    b.RAPID_DRAWDOWN = ui["rapid"]
    b.NORMAL_RESERVOIR_LEVEL = ui["pool"]
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
    b.Y_AXIS_MAX = ui["y_max"]
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
    r["concrete_face"] = ui["face"]
    r["slip_circle"] = ui["circ_cfrd"]
    r["include_reservoir_water_weight"] = ui["water_weight"]
    attach_foundation(r)


def format_results(cases):
    lines = []
    for case in cases:
        result = case.get("result")
        lines.append(case["title"])
        if result is None:
            lines.append("  No valid slip surface for this setting.")
        else:
            cx, cy = result["center"]
            lines.append(f"  FS = {result['fos']:.3f}")
            lines.append(f"  Centre ({cx:.1f}, {cy:.1f}) m   R = {result['radius']:.1f} m")
            lines.append(f"  Slices = {len(result['slices'])}")
        lines.append("")
    return "\n".join(lines).strip()


# ---------- page -----------------------------------------------------------

st.title("Dam slope stability")
st.caption(
    "Bishop simplified method for earthfill, clay-core and concrete-faced rockfill dams. "
    "Units: lengths in m, unit weights in kN/m³, cohesion in kPa."
)

left, right = st.columns([0.92, 1.25], gap="large")

with left:
    st.subheader("Analysis")
    water = st.radio(
        "Water condition",
        ("Steady seepage", "Rapid drawdown"),
        index=0 if not b.RAPID_DRAWDOWN else 1,
        help="Steady seepage: full reservoir, outer slope. "
             "Rapid drawdown: empty reservoir, inner slope, phreatic held from the old pool.",
    )
    mode = st.radio(
        "Slip surface",
        ("Single trial circle", "Grid search for critical circle"),
        index=0,
        help="Grid search tests many centres and radii. It is slower (often 1–3 minutes).",
    )
    st.markdown("**Dams to include**")
    en_hom = st.checkbox("Homogeneous earthfill", value=True)
    en_core = st.checkbox("Earthfill with clay core", value=True)
    en_cfrd = st.checkbox("Rockfill with concrete face", value=True)
    use_foundation = st.checkbox("Include foundation (deeper circles)", value=True)
    water_weight = st.checkbox("Include reservoir water weight on the upstream face", value=True)
    draw_slices = st.checkbox("Draw slices on the plot", value=True)

    pool = number("Normal reservoir level (m)", b.NORMAL_RESERVOIR_LEVEL, "pool", step=0.5)

    with st.expander("Search grid and radii", expanded=False):
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
            nr = st.number_input("Number of radii", min_value=2, max_value=20,
                                 value=int(b.RADIUS_CONFIG["num_radii"]), step=1, key="nr")
        search_slices = st.number_input(
            "Slices during search", min_value=8, max_value=50,
            value=int(b.SEARCH_NUM_SLICES), step=1, key="ss",
        )
        max_fs = number("Heatmap FS colour cap", b.MAX_DISPLAY_FS, "maxfs", step=0.5)

    with st.expander("Foundation", expanded=False):
        f = b.FOUNDATION
        foundation = material_inputs("found", f)
        ft1, ft2 = st.columns(2)
        with ft1:
            foundation["thickness"] = number("Thickness (m)", f["thickness"], "fth")
        with ft2:
            foundation["extra_width"] = number("Extra width beyond toes (m)", f["extra_width"], "few")

    with st.expander("Homogeneous earthfill", expanded=False):
        geom_hom = geometry_inputs("homg", b.HOMOGENEOUS_DAM["geometry"])
        fill_hom = material_inputs("homf", b.HOMOGENEOUS_DAM["fill"])
        st.markdown("Trial circle (used if slip surface is a single circle)")
        circ_hom = circle_inputs("homc", b.HOMOGENEOUS_DAM["slip_circle"])
        ph_hom = text_to_points(
            st.text_area(
                "Phreatic line (x, y per line, m)",
                value=points_to_text(b.PHREATIC_LINE_HOMOGENEOUS),
                key="ph_hom",
                height=90,
            ),
            b.PHREATIC_LINE_HOMOGENEOUS,
        )

    with st.expander("Clay-core earthfill", expanded=False):
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
        circ_core = circle_inputs("corec", b.CLAY_CORE_DAM["slip_circle"])
        ph_core = text_to_points(
            st.text_area(
                "Phreatic line (x, y per line, m)",
                value=points_to_text(b.PHREATIC_LINE_CLAY_CORE),
                key="ph_core",
                height=90,
            ),
            b.PHREATIC_LINE_CLAY_CORE,
        )

    with st.expander("Rockfill with concrete face", expanded=False):
        geom_cfrd = geometry_inputs("cfrdg", b.ROCKFILL_CFRD_DAM["geometry"])
        fill_cfrd = material_inputs("cfrdf", b.ROCKFILL_CFRD_DAM["fill"], cohesion=False)
        face0 = b.ROCKFILL_CFRD_DAM["concrete_face"]
        fc1, fc2 = st.columns(2)
        with fc1:
            ft = number("Slab thickness (m)", face0["thickness"], "ft")
        with fc2:
            fg = number("Slab unit weight (kN/m³)", face0["unit_weight"], "fg")
        face = {"name": "Concrete face", "thickness": ft, "unit_weight": fg}
        circ_cfrd = circle_inputs("cfrdc", b.ROCKFILL_CFRD_DAM["slip_circle"])
        ph_cfrd = text_to_points(
            st.text_area(
                "Phreatic line (x, y per line, m)",
                value=points_to_text(b.PHREATIC_LINE_CFRD),
                key="ph_cfrd",
                height=90,
            ),
            b.PHREATIC_LINE_CFRD,
        )

    with st.expander("Numerics and plot", expanded=False):
        num_slices = st.number_input(
            "Slices for the reported circle", min_value=10, max_value=80,
            value=int(b.NUM_SLICES), step=1, key="ns",
        )
        y_max = number("Plot y-axis upper limit (m)", b.Y_AXIS_MAX, "ymax", step=5.0)

    run = st.button("Run analysis", type="primary", width="stretch")

ui = {
    "rapid": water == "Rapid drawdown",
    "pool": pool,
    "grid_search": mode == "Grid search for critical circle",
    "en_hom": en_hom,
    "en_core": en_core,
    "en_cfrd": en_cfrd,
    "use_foundation": use_foundation,
    "water_weight": water_weight,
    "draw_slices": draw_slices,
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
    "foundation": foundation,
    "geom_hom": geom_hom,
    "fill_hom": fill_hom,
    "circ_hom": circ_hom,
    "ph_hom": ph_hom,
    "geom_core": geom_core,
    "fill_core": fill_core,
    "core_mat": core_mat,
    "core_geom": core_geom,
    "circ_core": circ_core,
    "ph_core": ph_core,
    "geom_cfrd": geom_cfrd,
    "fill_cfrd": fill_cfrd,
    "face": face,
    "circ_cfrd": circ_cfrd,
    "ph_cfrd": ph_cfrd,
    "num_slices": num_slices,
    "y_max": y_max,
}

with right:
    st.subheader("Results")
    plot_slot = st.empty()
    text_slot = st.empty()
    log_slot = st.empty()

    if "figure_png" in st.session_state:
        plot_slot.image(st.session_state["figure_png"], width="stretch")
    else:
        plot_slot.info("Set the options on the left and press **Run analysis**.")

    if "summary" in st.session_state:
        text_slot.code(st.session_state["summary"], language=None)

    if "log" in st.session_state:
        with log_slot.expander("Calculation log"):
            st.text(st.session_state["log"])

    if run:
        if not (en_hom or en_core or en_cfrd):
            st.error("Select at least one dam type.")
        else:
            apply_to_engine(ui)
            buf = io.StringIO()
            spinner = (
                "Searching the grid. This can take a couple of minutes…"
                if ui["grid_search"]
                else "Evaluating the trial circle…"
            )
            with st.spinner(spinner):
                try:
                    with contextlib.redirect_stdout(buf):
                        cases, fig = b.run(return_figure=True)
                except Exception as exc:
                    st.exception(exc)
                else:
                    png = io.BytesIO()
                    fig.savefig(png, format="png", dpi=140, bbox_inches="tight")
                    plt.close(fig)
                    st.session_state["figure_png"] = png.getvalue()
                    st.session_state["summary"] = format_results(cases)
                    st.session_state["log"] = buf.getvalue()
                    plot_slot.image(st.session_state["figure_png"], width="stretch")
                    text_slot.code(st.session_state["summary"], language=None)
                    with log_slot.expander("Calculation log"):
                        st.text(st.session_state["log"])
