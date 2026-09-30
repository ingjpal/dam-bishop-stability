"""
Concrete gravity-dam stability: overturning, sliding, bearing and heel tension.

The section matches a typical non-overflow monolith (crest, upstream batter,
two-slope downstream face, foundation block). Weight is the concrete polygon
times γc, per metre of dam length. Stability is evaluated on contact A–B.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import matplotlib.patches as patches


DEFAULTS = {
    "H": 100.0,
    "B": 68.16,
    "h_C": 64.56,
    "n_up": 24.0,
    "n_dn_u": 6.54,
    "n_dn_l": 1.38,
    "hw": 37.86,
    "t_base": 11.65,
    "gamma_c": 24.0,
    "gamma_w": 9.81,
    "mu": 0.75,
    "c": 0.0,
    "q_all": 3000.0,
    "k_h": 0.10,
    "k_v": 0.05,
}

GEOM_KEYS = ("H", "B", "h_C", "n_up", "n_dn_u", "n_dn_l", "hw", "t_base")


def _num(name, value):
    return DEFAULTS[name] if value is None else float(value)


def _shoelace(pts):
    n = len(pts)
    acc = 0.0
    cx = 0.0
    cy = 0.0
    for i in range(n):
        x0, y0 = pts[i]
        x1, y1 = pts[(i + 1) % n]
        cross = x0 * y1 - x1 * y0
        acc += cross
        cx += (x0 + x1) * cross
        cy += (y0 + y1) * cross
    area = 0.5 * acc
    if abs(area) < 1e-12:
        return 0.0, 0.0, 0.0
    return abs(area), cx / (6.0 * area), cy / (6.0 * area)


def make_geometry(
    H=None,
    B=None,
    h_C=None,
    n_up=None,
    n_dn_u=None,
    n_dn_l=None,
    hw=None,
    t_base=None,
):
    """Dam polygon, crest width and centroid. Origin at heel A, x downstream."""
    H = _num("H", H)
    B = _num("B", B)
    h_C = _num("h_C", h_C)
    n_up = _num("n_up", n_up)
    n_dn_u = _num("n_dn_u", n_dn_u)
    n_dn_l = _num("n_dn_l", n_dn_l)
    hw = _num("hw", hw)
    t_base = _num("t_base", t_base)

    if H <= 0 or B <= 0:
        raise ValueError("Height H and base width B must be positive.")
    if not (0.0 < h_C < H):
        raise ValueError("Slope-break height C must lie between 0 and H.")
    if min(n_up, n_dn_u, n_dn_l) <= 0:
        raise ValueError("Slope 1/n values must be positive.")
    if hw < 0 or hw > H:
        raise ValueError("Water depth hw must satisfy 0 ≤ hw ≤ H.")

    s_up = 1.0 / n_up
    s_du = 1.0 / n_dn_u
    s_dl = 1.0 / n_dn_l

    x_cu = H * s_up
    x_C = B - h_C * s_dl
    x_cd = x_C - (H - h_C) * s_du
    crest = x_cd - x_cu
    if crest < 0.5:
        raise ValueError(
            "Crest width is too small (or negative). Increase B or steepen a slope."
        )

    vertices = [
        (0.0, 0.0),
        (B, 0.0),
        (x_C, h_C),
        (x_cd, H),
        (x_cu, H),
    ]
    area, cx, cy = _shoelace(vertices)
    return {
        "H": H,
        "B": B,
        "h_C": h_C,
        "n_up": n_up,
        "n_dn_u": n_dn_u,
        "n_dn_l": n_dn_l,
        "hw": hw,
        "t_base": t_base,
        "s_up": s_up,
        "x_cu": x_cu,
        "x_cd": x_cd,
        "x_C": x_C,
        "crest": crest,
        "vertices": vertices,
        "area": area,
        "cx": cx,
        "cy": cy,
    }


def analyse(
    H=None,
    B=None,
    h_C=None,
    n_up=None,
    n_dn_u=None,
    n_dn_l=None,
    hw=None,
    t_base=None,
    gamma_c=None,
    gamma_w=None,
    mu=None,
    c=None,
    q_all=None,
    k_h=None,
    k_v=None,
    target_static=None,
    target_seismic=None,
):
    g = make_geometry(
        H=H, B=B, h_C=h_C, n_up=n_up, n_dn_u=n_dn_u, n_dn_l=n_dn_l,
        hw=hw, t_base=t_base,
    )
    gamma_c = _num("gamma_c", gamma_c)
    gamma_w = _num("gamma_w", gamma_w)
    mu = _num("mu", mu)
    c = _num("c", c)
    q_all = _num("q_all", q_all)
    k_h = _num("k_h", k_h)
    k_v = _num("k_v", k_v)

    H, B, hw = g["H"], g["B"], g["hw"]
    cx, cy, area = g["cx"], g["cy"], g["area"]
    s_up = g["s_up"]

    W = area * gamma_c
    Fw = 0.5 * gamma_w * hw ** 2
    Fw_v = Fw * s_up
    U = 0.5 * gamma_w * hw * B

    F_Eh = W * k_h
    F_Ev = W * k_v
    F_wd = 0.583 * k_h * gamma_w * hw ** 2

    sum_V = W - U - F_Ev - Fw_v
    sum_H = Fw + F_Eh + F_wd

    lever_W = B - cx
    x_Fv = s_up * hw / 3.0
    M_resisting = (W * lever_W) - (F_Ev * lever_W) - (Fw_v * (B - x_Fv))
    M_overturning = (
        (Fw * (hw / 3.0))
        + (U * (2.0 / 3.0 * B))
        + (F_Eh * cy)
        + (F_wd * (0.4 * hw))
    )

    x_bar = (M_resisting - M_overturning) / sum_V if sum_V != 0 else float("nan")
    x_resultant = B - x_bar
    e = (B / 2.0) - x_bar
    e_max = B / 6.0

    q_toe = (sum_V / B) * (1 + (6 * e) / B)
    q_heel = (sum_V / B) * (1 - (6 * e) / B)

    seismic = not (k_h == 0 and k_v == 0)
    t_static = 1.5 if target_static is None else float(target_static)
    t_seismic = 1.3 if target_seismic is None else float(target_seismic)
    target_FoS = t_seismic if seismic else t_static
    FoS_O = M_resisting / M_overturning if M_overturning != 0 else float("inf")
    resisting_H = mu * sum_V + c * B
    FoS_S = resisting_H / sum_H if sum_H != 0 else float("inf")

    pass_O = FoS_O >= target_FoS
    pass_S = FoS_S >= target_FoS
    pass_B = q_toe <= q_all
    pass_C = q_heel >= 0

    out = dict(g)
    out.update({
        "gamma_c": gamma_c,
        "gamma_w": gamma_w,
        "mu": mu,
        "c": c,
        "q_all": q_all,
        "k_h": k_h,
        "k_v": k_v,
        "seismic": seismic,
        "W": W,
        "Fw": Fw,
        "Fw_v": Fw_v,
        "U": U,
        "F_Eh": F_Eh,
        "F_Ev": F_Ev,
        "F_wd": F_wd,
        "sum_V": sum_V,
        "sum_H": sum_H,
        "M_resisting": M_resisting,
        "M_overturning": M_overturning,
        "x_bar": x_bar,
        "x_resultant": x_resultant,
        "e": e,
        "e_max": e_max,
        "q_toe": q_toe,
        "q_heel": q_heel,
        "target_FoS": target_FoS,
        "FoS_O": FoS_O,
        "FoS_S": FoS_S,
        "resisting_H": resisting_H,
        "pass_O": pass_O,
        "pass_S": pass_S,
        "pass_B": pass_B,
        "pass_C": pass_C,
    })
    return out


def _verdict(ok):
    return "PASS" if ok else "FAIL"


def _draw_body(ax, g, with_labels=True):
    H, B, hw = g["H"], g["B"], g["hw"]
    t_base = g["t_base"]
    verts = g["vertices"]
    x_C, h_C = g["x_C"], g["h_C"]
    x_cu, x_cd = g["x_cu"], g["x_cd"]

    ground_x0 = -0.22 * B
    ground_x1 = B + 0.22 * B
    ax.add_patch(patches.Polygon(
        [(ground_x0, -1.65 * t_base), (ground_x1, -1.65 * t_base),
         (ground_x1, 0.0), (ground_x0, 0.0)],
        facecolor="#c5d6e8", edgecolor="none", zorder=0, label="Ground",
    ))
    ax.add_patch(patches.Rectangle(
        (0.0, -t_base), B, t_base,
        facecolor="#8b5a2b", edgecolor="black", lw=1.4, zorder=1, label="Base",
    ))
    ax.add_patch(patches.Polygon(
        verts, facecolor="#d9d4cc", edgecolor="black", lw=1.8, zorder=2,
        label="Dam",
    ))

    if hw > 0:
        x_int = min(hw * g["s_up"], x_cu)
        ax.add_patch(patches.Polygon(
            [(ground_x0, 0.0), (0.0, 0.0), (x_int, hw), (ground_x0, hw)],
            facecolor="dodgerblue", alpha=0.35, edgecolor="none", zorder=1,
            label="Reservoir",
        ))
        ax.axhline(hw, color="dodgerblue", ls=":", lw=1, zorder=3)

    ax.plot([ground_x0, ground_x1], [0, 0], "k-", lw=2.2, zorder=3)

    if with_labels:
        ax.plot(0, 0, "k.", ms=7, zorder=5)
        ax.plot(B, 0, "k.", ms=7, zorder=5)
        ax.plot(x_C, h_C, "k.", ms=7, zorder=5)
        ax.text(0, -0.04 * H, "A", ha="center", va="top", fontsize=8, fontweight="bold")
        ax.text(B, -0.04 * H, "B", ha="center", va="top", fontsize=8, fontweight="bold")
        ax.text(x_C + 0.02 * B, h_C, "C", ha="left", va="bottom", fontsize=8, fontweight="bold")
        ax.text(B * 0.5, -0.55 * t_base, f"Base {B:.1f} m", ha="center", va="center",
                fontsize=7, color="white", fontweight="bold", zorder=4)
        mid_up = 0.45 * H
        ax.annotate(
            f"1/{g['n_up']:g}",
            xy=(mid_up * g["s_up"], mid_up),
            xytext=(-0.12 * B, mid_up),
            fontsize=7, ha="right", va="center", color="#1b6b2a",
            arrowprops=dict(arrowstyle="->", color="#1b6b2a", lw=1),
        )
        mid_du_y = 0.5 * (h_C + H)
        mid_du_x = 0.5 * (x_C + x_cd)
        ax.annotate(
            f"1/{g['n_dn_u']:g}",
            xy=(mid_du_x, mid_du_y),
            xytext=(mid_du_x + 0.12 * B, mid_du_y + 0.04 * H),
            fontsize=7, color="#1b6b2a",
            arrowprops=dict(arrowstyle="->", color="#1b6b2a", lw=1),
        )
        mid_dl_y = 0.5 * h_C
        mid_dl_x = 0.5 * (B + x_C)
        ax.text(mid_dl_x + 0.02 * B, mid_dl_y, f"1/{g['n_dn_l']:g}",
                fontsize=7, color="#1b6b2a")

    ax.set_aspect("equal", adjustable="box")
    ax.set_xlim(ground_x0, ground_x1)
    ax.set_ylim(-1.75 * t_base, H * 1.14)


def plot_mechanisms(r):
    H, B, hw = r["H"], r["B"], r["hw"]
    W, Fw, U = r["W"], r["Fw"], r["U"]
    F_Eh, sum_H, sum_V = r["F_Eh"], r["sum_H"], r["sum_V"]
    resisting_H = r["resisting_H"]
    q_toe, q_heel, q_all = r["q_toe"], r["q_heel"], r["q_all"]
    k_h = r["k_h"]
    cx, cy = r["cx"], r["cy"]
    x_resultant, e, e_max = r["x_resultant"], r["e"], r["e_max"]
    FoS_O, FoS_S = r["FoS_O"], r["FoS_S"]

    fig, axs = plt.subplots(2, 2, figsize=(11.2, 9.6))
    fig.suptitle("Visualizing Forces per Failure Mechanism", fontsize=16, fontweight="bold")

    def draw_base_geometry(ax, title):
        _draw_body(ax, r, with_labels=False)
        ax.set_title(title, fontweight="bold")
        ax.axis("off")

    scale_f = (H * 0.3) / max(abs(W), abs(Fw), 1.0)
    scale_q = (H * 0.3) / max(abs(q_toe), abs(q_heel), 1.0)

    ax_O = axs[0, 0]
    draw_base_geometry(ax_O, "1. Overturning (Tipping) Mechanics")
    ax_O.plot(B, 0, marker="o", color="black", ms=12)
    ax_O.text(B + 2, 2, "Pivot (Toe)", fontweight="bold")
    ax_O.annotate(
        "Weight (Resisting)",
        xy=(cx, cy),
        xytext=(cx, cy + W * scale_f),
        arrowprops=dict(facecolor="forestgreen", width=3, headwidth=10),
        ha="center",
        color="forestgreen",
    )
    ax_O.annotate(
        "Hydro (Driving)",
        xy=(0, hw / 3),
        xytext=(-Fw * scale_f, hw / 3),
        arrowprops=dict(facecolor="crimson", width=3, headwidth=10),
        va="center",
        color="crimson",
    )
    ax_O.annotate(
        "Uplift (Driving)",
        xy=(B / 3, 0),
        xytext=(B / 3, -U * scale_f),
        arrowprops=dict(facecolor="crimson", width=3, headwidth=10),
        ha="center",
        color="crimson",
    )
    if k_h > 0:
        ax_O.annotate(
            "Seismic (Driving)",
            xy=(cx, cy),
            xytext=(cx - F_Eh * scale_f, cy),
            arrowprops=dict(facecolor="crimson", width=3, headwidth=10),
            va="center",
            color="crimson",
        )
    ax_O.text(
        B * 0.5, H * 0.92,
        f"FoS: {FoS_O:.2f} [{_verdict(r['pass_O'])}]",
        bbox=dict(facecolor="white", edgecolor="black"),
    )

    ax_S = axs[0, 1]
    draw_base_geometry(ax_S, "2. Sliding (Shear) Mechanics")
    ax_S.annotate(
        f"Total Driving:\n{sum_H:.0f} kN",
        xy=(B / 2, H / 4),
        xytext=(-sum_H * scale_f, H / 4),
        arrowprops=dict(facecolor="crimson", width=5, headwidth=12),
        va="center",
        ha="right",
        color="crimson",
        fontweight="bold",
    )
    ax_S.annotate(
        f"Friction Resisting:\n{resisting_H:.0f} kN",
        xy=(B / 2, 0),
        xytext=(B / 2 + resisting_H * scale_f, 0),
        arrowprops=dict(facecolor="forestgreen", width=5, headwidth=12),
        va="center",
        color="forestgreen",
        fontweight="bold",
    )
    ax_S.text(
        B * 0.5, H * 0.92,
        f"FoS: {FoS_S:.2f} [{_verdict(r['pass_S'])}]",
        bbox=dict(facecolor="white", edgecolor="black"),
    )

    ax_B = axs[1, 0]
    draw_base_geometry(ax_B, "3. Foundation Bearing (Toe Crushing)")
    stress_verts = [(0, 0), (B, 0), (B, -q_toe * scale_q), (0, -q_heel * scale_q)]
    ax_B.add_patch(
        patches.Polygon(
            stress_verts, facecolor="orange", alpha=0.5, edgecolor="darkorange", lw=2
        )
    )
    ax_B.annotate(
        f"Total Vertical Load\n{sum_V:.0f} kN",
        xy=(B / 2, 0),
        xytext=(B / 2, H * 0.4),
        arrowprops=dict(facecolor="purple", width=4, headwidth=12),
        ha="center",
        color="purple",
        fontweight="bold",
    )
    ax_B.text(
        B, -q_toe * scale_q - 3,
        f"Max Compressive Stress\n{q_toe:.0f} kPa",
        ha="center", va="top", color="darkred", fontweight="bold",
    )
    ax_B.text(
        B * 0.5, H * 0.92,
        f"Toe Stress vs Allowable ({q_all:g} kPa) [{_verdict(r['pass_B'])}]",
        bbox=dict(facecolor="white", edgecolor="black"),
    )

    ax_C = axs[1, 1]
    draw_base_geometry(ax_C, "4. Tensile Cracking (Middle Third Rule)")
    ax_C.plot([B / 3, 2 * B / 3], [0, 0], color="forestgreen", lw=8)
    ax_C.text(B / 2, 2, "Safe Middle Third", ha="center", color="forestgreen", fontweight="bold")
    ax_C.annotate(
        "Resultant Force",
        xy=(x_resultant, 0),
        xytext=(x_resultant, H * 0.3),
        arrowprops=dict(facecolor="darkorange", width=3, headwidth=10),
        ha="center",
        color="darkorange",
        fontweight="bold",
    )
    if r["pass_C"]:
        ax_C.text(0, 5, "Compression\n(Safe)", ha="center", color="forestgreen", fontweight="bold")
    else:
        ax_C.text(0, 5, "TENSION ZONE\nCracking Risk!", ha="center", color="crimson", fontweight="bold")
        ax_C.plot(0, 0, marker="X", color="crimson", ms=15)
    ax_C.text(
        B * 0.5, H * 0.92,
        f"Eccentricity: {e:.2f}m (Max {e_max:.2f}m) [{_verdict(r['pass_C'])}]",
        bbox=dict(facecolor="white", edgecolor="black"),
    )

    fig.tight_layout()
    return fig


def draw_section(ax, H=None, B=None, hw=None, result=None, **kwargs):
    """Draw the gravity section onto an existing axis."""
    if result is not None:
        g = result
    else:
        g = make_geometry(H=H, B=B, hw=hw, **kwargs)
    _draw_body(ax, g, with_labels=True)
    ax.set_xlabel("x (m)")
    ax.set_ylabel("y (m)")
    ax.set_title("Gravity dam", fontsize=12, fontweight="bold")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper right", fontsize=7, framealpha=0.92)
    if result is not None and "FoS_O" in result:
        mark = lambda ok: "PASS" if ok else "FAIL"
        ax.text(
            0.02, 0.98,
            f"Overturning {result['FoS_O']:.2f} [{mark(result['pass_O'])}]\n"
            f"Sliding {result['FoS_S']:.2f} [{mark(result['pass_S'])}]\n"
            f"Toe {result['q_toe']:.0f} kPa [{mark(result['pass_B'])}]\n"
            f"Heel {'compr.' if result['pass_C'] else 'TENSION'} [{mark(result['pass_C'])}]",
            transform=ax.transAxes, ha="left", va="top",
            fontsize=8, fontweight="bold", zorder=12,
            bbox=dict(boxstyle="round,pad=0.35", facecolor="#fff6b0",
                      edgecolor="#c0392b", linewidth=1.2),
        )


def plot_section(H=None, B=None, hw=None, **kwargs):
    """Single-panel cross-section for geometry preview (no safety checks)."""
    fig, ax = plt.subplots(figsize=(8.4, 5.6))
    draw_section(ax, H=H, B=B, hw=hw, **kwargs)
    fig.tight_layout()
    return fig


def run(return_figure=False, **kwargs):
    results = analyse(**kwargs)
    fig = plot_mechanisms(results)
    if return_figure:
        return results, fig
    plt.show()
    return results


if __name__ == "__main__":
    run()
