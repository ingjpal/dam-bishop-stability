"""
Concrete gravity-dam stability: overturning, sliding, bearing and heel tension.

Formulas follow the classroom Gravity_Stability.py script (triangular section,
vertical upstream face). Forces are per metre of dam length.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import matplotlib.patches as patches


DEFAULTS = {
    "H": 100.0,
    "B": 10.0,
    "hw": 45.0,
    "gamma_c": 24.0,
    "gamma_w": 9.81,
    "mu": 0.75,
    "c": 0.0,
    "q_all": 3000.0,
    "k_h": 0.10,
    "k_v": 0.05,
}


def analyse(
    H=None,
    B=None,
    hw=None,
    gamma_c=None,
    gamma_w=None,
    mu=None,
    c=None,
    q_all=None,
    k_h=None,
    k_v=None,
):
    H = DEFAULTS["H"] if H is None else float(H)
    B = DEFAULTS["B"] if B is None else float(B)
    hw = DEFAULTS["hw"] if hw is None else float(hw)
    gamma_c = DEFAULTS["gamma_c"] if gamma_c is None else float(gamma_c)
    gamma_w = DEFAULTS["gamma_w"] if gamma_w is None else float(gamma_w)
    mu = DEFAULTS["mu"] if mu is None else float(mu)
    c = DEFAULTS["c"] if c is None else float(c)
    q_all = DEFAULTS["q_all"] if q_all is None else float(q_all)
    k_h = DEFAULTS["k_h"] if k_h is None else float(k_h)
    k_v = DEFAULTS["k_v"] if k_v is None else float(k_v)

    W = 0.5 * B * H * gamma_c
    Fw = 0.5 * gamma_w * hw ** 2
    U = 0.5 * gamma_w * hw * B

    F_Eh = W * k_h
    F_Ev = W * k_v
    F_wd = 0.583 * k_h * gamma_w * hw ** 2

    sum_V = W - U - F_Ev
    sum_H = Fw + F_Eh + F_wd

    M_resisting = (W * (2.0 / 3.0 * B)) - (F_Ev * (2.0 / 3.0 * B))
    M_overturning = (
        (Fw * (hw / 3.0))
        + (U * (2.0 / 3.0 * B))
        + (F_Eh * (H / 3.0))
        + (F_wd * (0.4 * hw))
    )

    x_bar = (M_resisting - M_overturning) / sum_V if sum_V != 0 else float("nan")
    x_resultant = B - x_bar
    e = (B / 2.0) - x_bar
    e_max = B / 6.0

    q_toe = (sum_V / B) * (1 + (6 * e) / B)
    q_heel = (sum_V / B) * (1 - (6 * e) / B)

    seismic = not (k_h == 0 and k_v == 0)
    target_FoS = 1.3 if seismic else 1.5
    FoS_O = M_resisting / M_overturning if M_overturning != 0 else float("inf")
    resisting_H = mu * sum_V + c * B
    FoS_S = resisting_H / sum_H if sum_H != 0 else float("inf")

    pass_O = FoS_O >= target_FoS
    pass_S = FoS_S >= target_FoS
    pass_B = q_toe <= q_all
    pass_C = q_heel >= 0

    return {
        "H": H,
        "B": B,
        "hw": hw,
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
    }


def _verdict(ok):
    return "PASS" if ok else "FAIL"


def plot_mechanisms(r):
    H, B, hw = r["H"], r["B"], r["hw"]
    W, Fw, U = r["W"], r["Fw"], r["U"]
    F_Eh, sum_H, sum_V = r["F_Eh"], r["sum_H"], r["sum_V"]
    resisting_H = r["resisting_H"]
    q_toe, q_heel, q_all = r["q_toe"], r["q_heel"], r["q_all"]
    k_h = r["k_h"]
    x_resultant, e, e_max = r["x_resultant"], r["e"], r["e_max"]
    FoS_O, FoS_S = r["FoS_O"], r["FoS_S"]

    fig, axs = plt.subplots(2, 2, figsize=(14, 12))
    fig.suptitle("Visualizing Forces per Failure Mechanism", fontsize=16, fontweight="bold")

    def draw_base_geometry(ax, title):
        dam = patches.Polygon(
            [(0, H), (0, 0), (B, 0)],
            facecolor="lightgray",
            edgecolor="black",
            lw=2,
        )
        water = patches.Polygon(
            [(-B / 1.5, hw), (0, hw), (0, 0), (-B / 1.5, 0)],
            facecolor="dodgerblue",
            alpha=0.3,
        )
        ax.add_patch(dam)
        ax.add_patch(water)
        ax.plot([-B / 1.5, B * 1.4], [0, 0], "k-", lw=3)
        ax.set_aspect("equal")
        ax.set_xlim(-B / 1.5, B * 1.4)
        ax.set_ylim(-H * 0.4, H * 1.1)
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
        xy=(B / 3, H / 3),
        xytext=(B / 3, H / 3 + W * scale_f),
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
            xy=(B / 3, H / 3),
            xytext=(B / 3 - F_Eh * scale_f, H / 3),
            arrowprops=dict(facecolor="crimson", width=3, headwidth=10),
            va="center",
            color="crimson",
        )
    ax_O.text(
        B * 0.5,
        H * 0.9,
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
        B * 0.5,
        H * 0.9,
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
        B,
        -q_toe * scale_q - 3,
        f"Max Compressive Stress\n{q_toe:.0f} kPa",
        ha="center",
        va="top",
        color="darkred",
        fontweight="bold",
    )
    ax_B.text(
        B * 0.5,
        H * 0.9,
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
        B * 0.5,
        H * 0.9,
        f"Eccentricity: {e:.2f}m (Max {e_max:.2f}m) [{_verdict(r['pass_C'])}]",
        bbox=dict(facecolor="white", edgecolor="black"),
    )

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
