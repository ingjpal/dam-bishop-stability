"""
Bishop simplified slope-stability analysis for earthfill and rockfill dams.

  - homogeneous earthfill
  - earthfill with a central clay core
  - rockfill with an upstream concrete face (CFRD)

The dam is a closed polygon with a flat base. Strength and unit weight
are assigned by point-in-polygon tests (fill vs core), so a slice that
crosses the core is integrated with the correct material along its height.
The slip surface is a circle defined by a centre and a radius, or a grid
of centres and radii can be searched for the minimum factor of safety.
A concrete face keeps the rockfill nearly dry and adds slab weight on the
upstream slope (important once the reservoir is drawn down).

Units: lengths in m, unit weights in kN/m3, cohesion in kPa (= kN/m2).
"""

# ========================================================================
# CONFIGURATION  (all user inputs are in this first section)
# ========================================================================
#
# Each dam is a self-contained block. Set 'enabled': False to skip it.
# Geometry: if 'polygon' is not None it is used as a closed outline
# (flat base; first vertex need not be repeated), otherwise a trapezoid
# is built from 'geometry'.
# Slip circle: give centre + radius, or point_a / point_b + center_x.
# The circle and search grid are placed on the inner face in rapid
# drawdown and on the outer face in steady seepage.
# A custom seepage surface can still be set per dam with 'phreatic_line'.
#
# ========================================================================
# 1. WATER CONDITION
# ========================================================================
# Rapid drawdown: the reservoir is emptied, the blue water is not drawn,
# and the search grid sits on the inner (upstream) slope. Pore pressures
# still follow a phreatic line that starts at NORMAL_RESERVOIR_LEVEL.
# Steady seepage: pool and phreatic line both start at NORMAL_RESERVOIR_LEVEL,
# and the search grid sits on the outer (downstream) slope.
#
# True  -> empty reservoir (0 m), no blue water, inner-slope search
# False -> pool and phreatic at NORMAL_RESERVOIR_LEVEL, outer-slope search

RAPID_DRAWDOWN = False
NORMAL_RESERVOIR_LEVEL = 20.0    # m  (operating / pre-drawdown pool)

# Phreatic line as (x, y) coordinates in m, from the upstream face to
# the downstream toe. The first point is the start elevation of seepage.
# Used unless a dam block sets its own 'phreatic_line'.
PHREATIC_LINE_HOMOGENEOUS = [
    (40.0, 16.0),
    (53.0,  7.2),
    (106.0, 0.0),
]
PHREATIC_LINE_CLAY_CORE = [
    (40.0, 16.0),
    (48.0, 14.4),
    (58.0,  4.0),
    (106.0, 0.0),
]
# Concrete face: starts at the reservoir waterline on the slab, then
# drops immediately behind the face so the rockfill stays nearly dry.
PHREATIC_LINE_CFRD = [
    (50.0, 20.0),
    (51.0,  2.0),
    (70.0,  1.0),
    (106.0, 0.0),
]

# Foundation below the dam base. Deep slip circles may pass through it.
# Set to None to keep circles inside the dam body.
FOUNDATION = {
    'name': 'Foundation',
    'cohesion': 5.0,             # kPa
    'friction_angle': 25.0,      # degrees
    'unit_weight': 21.0,         # kN/m3
    'saturated_unit_weight': 22.0,
    'thickness': 15.0,           # m  below the dam base
    'extra_width': 15.0,         # m  beyond each toe
}

# ========================================================================
# 2. ANALYSIS MODE
# ========================================================================
# False -> evaluate the slip circle given in each dam block
# True  -> search a grid of centres and radii for the lowest FS

FIND_CRITICAL_CIRCLE = True

# Used only if FIND_CRITICAL_CIRCLE is True.
# lower_left_x / lower_left_y set the left and bottom edges of the grid.
GRID_CONFIG = {
    'lower_left_x': 40.0,        # m  shift this to move the grid horizontally
    'lower_left_y': 22.0,        # m
    'grid_width': 80.0,          # m
    'grid_height': 44.0,         # m
    'grid_spacing_x': 4.0,       # m
    'grid_spacing_y': 4.0,       # m
}

RADIUS_CONFIG = {
    'min_radius': 16.0,          # m
    'max_radius': 26.0,          # m
    'num_radii': 8,
}

SEARCH_NUM_SLICES = 24           # coarser slices during the sweep
SEARCH_WEIGHT_SAMPLES = 8
MAX_DISPLAY_FS = 5.0             # heatmap colour cap

# ========================================================================
# 3. DAM A — HOMOGENEOUS EARTHFILL
# ========================================================================

HOMOGENEOUS_DAM = {
    'enabled': True,
    'title': 'Homogeneous earthfill',

    # 'polygon': [(0, 0), (50, 20), (56, 20), (106, 0)],
    'polygon': None,
    'geometry': {
        'height': 20.0,              # m
        'crest_width': 6.0,          # m
        'upstream_slope': 2.5,       # H:V
        'downstream_slope': 2.5,     # H:V
        'left_toe_x': 0.0,           # m
        'base_y': 0.0,               # m
    },

    'fill': {
        'name': 'Earthfill',
        'cohesion': 3.0,             # kPa
        'friction_angle': 20.0,      # degrees
        'unit_weight': 20.0,         # kN/m3
        'saturated_unit_weight': 21.0,
    },
    'foundation': FOUNDATION,
    'phreatic_line': None,           # None = PHREATIC_LINE_HOMOGENEOUS above
    'include_reservoir_water_weight': True,

    # Circle is mirrored onto the inner face in rapid drawdown and onto
    # the outer face in steady seepage.
    'slip_circle': {
        'center_x': 21.0,            # m  (reference: above the upstream face)
        'center_y': 40.6,            # m
        'radius': 38.9,              # m
    },
}

# ========================================================================
# 4. DAM C — EARTHFILL WITH CENTRAL CLAY CORE
# ========================================================================

CLAY_CORE_DAM = {
    'enabled': True,
    'title': 'Earthfill with clay core',

    # 'polygon': [(0, 0), (50, 20), (56, 20), (106, 0)],
    'polygon': None,
    'geometry': {
        'height': 20.0,              # m
        'crest_width': 6.0,          # m
        'upstream_slope': 2.5,       # H:V
        'downstream_slope': 2.5,     # H:V
        'left_toe_x': 0.0,           # m
        'base_y': 0.0,               # m
    },

    # 'core_polygon': [(48, 0), (51.5, 20), (54.5, 20), (58, 0)],
    'core_polygon': None,
    'core_geometry': {
        'crest_width': 3.0,          # m
        'base_width': 10.0,          # m
        'center_x': None,            # None = dam centreline
    },

    'fill': {
        'name': 'Earthfill',
        'cohesion': 3.0,             # kPa
        'friction_angle': 20.0,      # degrees
        'unit_weight': 20.0,         # kN/m3
        'saturated_unit_weight': 21.0,
    },
    'core': {
        'name': 'Clay core',
        'cohesion': 12.0,            # kPa
        'friction_angle': 14.0,      # degrees
        'unit_weight': 19.0,         # kN/m3
        'saturated_unit_weight': 20.0,
    },
    'foundation': FOUNDATION,
    'phreatic_line': None,           # None = PHREATIC_LINE_CLAY_CORE above
    'include_reservoir_water_weight': True,

    # Circle is mirrored onto the inner face in rapid drawdown and onto
    # the outer face in steady seepage.
    'slip_circle': {
        'center_x': 21.0,            # m  (reference: above the upstream face)
        'center_y': 40.6,            # m
        'radius': 38.9,              # m
    },
}

# ========================================================================
# 5. DAM — ROCKFILL WITH CONCRETE FACE
# ========================================================================

ROCKFILL_CFRD_DAM = {
    'enabled': True,
    'title': 'Rockfill with concrete face',

    'polygon': None,
    'geometry': {
        'height': 20.0,              # m
        'crest_width': 6.0,          # m
        'upstream_slope': 2.5,       # H:V
        'downstream_slope': 2.5,     # H:V
        'left_toe_x': 0.0,           # m
        'base_y': 0.0,               # m
    },

    'fill': {
        'name': 'Rockfill',
        'cohesion': 0.0,             # kPa  (no cohesion)
        'friction_angle': 38.0,      # degrees
        'unit_weight': 21.0,         # kN/m3
        'saturated_unit_weight': 22.0,
    },
    'foundation': FOUNDATION,
    'phreatic_line': None,           # None = PHREATIC_LINE_CFRD above
    'include_reservoir_water_weight': True,

    # Impervious upstream slabs. Weight is applied on the inner face
    # and remains after rapid drawdown, when the reservoir support is gone.
    'concrete_face': {
        'name': 'Concrete face',
        'thickness': 0.40,           # m  (normal to the face)
        'unit_weight': 24.0,         # kN/m3
    },

    'slip_circle': {
        'center_x': 21.0,            # m
        'center_y': 40.6,            # m
        'radius': 38.9,              # m
    },
}

# ========================================================================
# 6. NUMERICS AND PLOTTING
# ========================================================================

GAMMA_W = 9.81                   # kN/m3
NUM_SLICES = 50
MAX_ITERATIONS = 60
FS_TOLERANCE = 1e-6
MIN_SLICE_HEIGHT = 0.05          # m; shallower slices are ignored

SHOW_PLOT = True
SAVE_FIGURE = True
FIGURE_NAME = 'earthfill_dam_bishop.png'
DRAW_SLICES = True
Y_AXIS_MAX = 70.0                # m  upper limit of the plots

# ========================================================================
# IMPLEMENTATION
# ========================================================================

import time

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MplPolygon, Rectangle


# ---------- geometry helpers ------------------------------------------------

def close_polygon(vertices):
    """Return an (N, 2) array whose first and last points coincide."""
    pts = np.asarray(vertices, dtype=float)
    if pts.ndim != 2 or pts.shape[1] != 2:
        raise ValueError('Polygon vertices must be an array of (x, y) pairs.')
    if len(pts) < 3:
        raise ValueError('A closed polygon needs at least 3 vertices.')
    if not np.allclose(pts[0], pts[-1]):
        pts = np.vstack([pts, pts[0]])
    return pts


def unclosed(vertices):
    pts = np.asarray(vertices, dtype=float)
    if np.allclose(pts[0], pts[-1]):
        return pts[:-1]
    return pts


def _point_on_segment(x, y, x1, y1, x2, y2, tol=1e-9):
    cross = (x - x1) * (y2 - y1) - (y - y1) * (x2 - x1)
    if abs(cross) > tol * max(1.0, np.hypot(x2 - x1, y2 - y1)):
        return False
    dot = (x - x1) * (x2 - x1) + (y - y1) * (y2 - y1)
    if dot < -tol:
        return False
    if dot > (x2 - x1) ** 2 + (y2 - y1) ** 2 + tol:
        return False
    return True


def point_in_polygon(x, y, vertices, include_boundary=True):
    """Even-odd ray test. Vertices may be open or closed."""
    pts = close_polygon(vertices)
    if include_boundary:
        for i in range(len(pts) - 1):
            if _point_on_segment(x, y, pts[i, 0], pts[i, 1], pts[i + 1, 0], pts[i + 1, 1]):
                return True
    inside = False
    for i in range(len(pts) - 1):
        x1, y1 = pts[i]
        x2, y2 = pts[i + 1]
        if (y1 > y) != (y2 > y):
            x_int = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
            if x_int >= x:
                inside = not inside
    return inside


def polygon_bounds(vertices):
    pts = np.asarray(vertices, dtype=float)
    return pts[:, 0].min(), pts[:, 0].max(), pts[:, 1].min(), pts[:, 1].max()


def polyline_y(x, points):
    """Linear interpolation of a polyline at x. None if outside range."""
    if points is None or len(points) < 2:
        return None
    pts = np.asarray(points, dtype=float)
    order = np.argsort(pts[:, 0])
    xs, ys = pts[order, 0], pts[order, 1]
    if x < xs[0] - 1e-9 or x > xs[-1] + 1e-9:
        return None
    return float(np.interp(x, xs, ys))


def vertical_hits(vertices, x, tol=1e-12):
    """Y-coordinates where a vertical line at x meets the polygon boundary."""
    pts = close_polygon(vertices)
    ys = []
    for i in range(len(pts) - 1):
        x1, y1 = pts[i]
        x2, y2 = pts[i + 1]
        xmin, xmax = (min(x1, x2), max(x1, x2))
        if x < xmin - tol or x > xmax + tol:
            continue
        if abs(x2 - x1) < tol:
            if abs(x - x1) <= tol:
                ys.extend([y1, y2])
            continue
        t = (x - x1) / (x2 - x1)
        if -1e-10 <= t <= 1.0 + 1e-10:
            ys.append(y1 + t * (y2 - y1))
    return ys


def surface_and_base_at_x(vertices, x):
    """Top and bottom of the dam body on a vertical line at x."""
    ys = vertical_hits(vertices, x)
    if not ys:
        return None, None
    return max(ys), min(ys)


def foundation_box(dam_vertices, foundation_props):
    """Horizontal and vertical extent of the foundation layer, or None."""
    if not foundation_props:
        return None
    thickness = float(foundation_props.get('thickness', 0.0))
    if thickness <= 0:
        return None
    xmin, xmax, ymin, _ = polygon_bounds(dam_vertices)
    extra = float(foundation_props.get('extra_width', 0.0))
    return {
        'xmin': xmin - extra,
        'xmax': xmax + extra,
        'ytop': ymin,
        'ybot': ymin - thickness,
    }


def column_top_and_bottom(x, dam_vertices, box):
    """
    Ground/dam surface and lowest allowed elevation at x.

    With a foundation, the column may stand on the terrace beyond the toes.
    """
    y_top, y_dam_bot = surface_and_base_at_x(dam_vertices, x)
    if box is None:
        return y_top, y_dam_bot
    if x < box['xmin'] - 1e-9 or x > box['xmax'] + 1e-9:
        return None, None
    if y_top is None:
        y_top = box['ytop']
    return y_top, box['ybot']


def circle_segment_intersections(cx, cy, radius, p1, p2):
    """Intersections of a circle with the finite segment p1-p2."""
    x1, y1 = p1
    x2, y2 = p2
    dx, dy = x2 - x1, y2 - y1
    fx, fy = x1 - cx, y1 - cy
    a = dx * dx + dy * dy
    if a < 1e-16:
        return []
    b = 2.0 * (fx * dx + fy * dy)
    c = fx * fx + fy * fy - radius * radius
    disc = b * b - 4.0 * a * c
    if disc < -1e-10:
        return []
    disc = max(disc, 0.0)
    hits = []
    sqrt_disc = np.sqrt(disc)
    for sign in (1.0, -1.0):
        t = (-b + sign * sqrt_disc) / (2.0 * a)
        if -1e-8 <= t <= 1.0 + 1e-8:
            px, py = x1 + t * dx, y1 + t * dy
            if abs(np.hypot(px - cx, py - cy) - radius) < 1e-6 * max(1.0, radius):
                hits.append((float(px), float(py)))
    return hits


def unique_points(points, tol=1e-4):
    unique = []
    for p in points:
        if not any(np.hypot(p[0] - q[0], p[1] - q[1]) < tol for q in unique):
            unique.append(p)
    return unique


def circle_polygon_intersections(cx, cy, radius, vertices):
    pts = close_polygon(vertices)
    hits = []
    for i in range(len(pts) - 1):
        hits.extend(circle_segment_intersections(cx, cy, radius, pts[i], pts[i + 1]))
    return unique_points(hits)


def x_on_upstream_face(dam_vertices, y_level):
    """X on the upstream slope (left face) at a given elevation."""
    xmin, xmax, ymin, ymax = polygon_bounds(dam_vertices)
    # Scan from the left: first x whose surface is at least y_level.
    xs = np.linspace(xmin, (xmin + xmax) / 2.0, 400)
    for x in xs:
        y_top, _ = surface_and_base_at_x(dam_vertices, x)
        if y_top is not None and y_top >= y_level - 1e-6:
            return float(x)
    return float(xmin)


def downstream_toe(dam_vertices):
    pts = unclosed(dam_vertices)
    ymin = pts[:, 1].min()
    on_base = pts[np.abs(pts[:, 1] - ymin) < 1e-8]
    right = on_base[np.argmax(on_base[:, 0])]
    return float(right[0]), float(right[1])


def upstream_toe(dam_vertices):
    pts = unclosed(dam_vertices)
    ymin = pts[:, 1].min()
    on_base = pts[np.abs(pts[:, 1] - ymin) < 1e-8]
    left = on_base[np.argmin(on_base[:, 0])]
    return float(left[0]), float(left[1])


def crest_x_range(dam_vertices, height_frac=0.98):
    """Approximate crest as vertices near the maximum elevation."""
    pts = unclosed(dam_vertices)
    ymax = pts[:, 1].max()
    on_crest = pts[pts[:, 1] >= ymax * height_frac]
    return float(on_crest[:, 0].min()), float(on_crest[:, 0].max())


def upstream_face_ends(dam_vertices):
    """Left-toe and left-crest points of the upstream face."""
    x0, y0 = upstream_toe(dam_vertices)
    x1, _ = crest_x_range(dam_vertices)
    ymax = polygon_bounds(dam_vertices)[3]
    return (x0, y0), (x1, ymax)


def face_slope_length_over_width(dam_vertices):
    """Slope length per unit horizontal width on the upstream face."""
    (x0, y0), (x1, y1) = upstream_face_ends(dam_vertices)
    dx = x1 - x0
    if abs(dx) < 1e-9:
        return 1.0
    return float(np.hypot(x1 - x0, y1 - y0) / abs(dx))


def concrete_slab_surcharge(x, width, dam_vertices, face):
    """Weight of the concrete face slab over one slice (kN/m)."""
    if not face:
        return 0.0
    t = float(face.get('thickness', 0.0))
    gamma = float(face.get('unit_weight', 24.0))
    if t <= 0.0 or gamma <= 0.0:
        return 0.0
    (x0, _), (x1, _) = upstream_face_ends(dam_vertices)
    if x < min(x0, x1) - 1e-6 or x > max(x0, x1) + 1e-6:
        return 0.0
    return gamma * t * width * face_slope_length_over_width(dam_vertices)


# ---------- dam builders ----------------------------------------------------

def build_trapezoid_dam(height, crest_width, upstream_slope, downstream_slope,
                        left_toe_x=0.0, base_y=0.0):
    """
    Closed trapezoidal dam polygon, counter-clockwise from the left toe.

    upstream_slope / downstream_slope are H:V (horizontal:vertical).
    """
    x0 = left_toe_x
    y0 = base_y
    x_left_crest = x0 + upstream_slope * height
    x_right_crest = x_left_crest + crest_width
    x_right_toe = x_right_crest + downstream_slope * height
    return np.array([
        [x0, y0],
        [x_left_crest, y0 + height],
        [x_right_crest, y0 + height],
        [x_right_toe, y0],
    ], dtype=float)


def build_core_polygon(dam_vertices, crest_width, base_width, center_x=None):
    """Trapezoidal core sitting on the dam base and reaching the crest."""
    xmin, xmax, ymin, ymax = polygon_bounds(dam_vertices)
    if center_x is None:
        x_c_left, x_c_right = crest_x_range(dam_vertices)
        center_x = 0.5 * (x_c_left + x_c_right)

    x_base_l = center_x - base_width / 2.0
    x_base_r = center_x + base_width / 2.0
    x_top_l = center_x - crest_width / 2.0
    x_top_r = center_x + crest_width / 2.0

    if x_base_l < xmin or x_base_r > xmax:
        raise ValueError(
            'Clay core base is wider than the dam. Reduce core_geometry["base_width"].'
        )
    if x_top_l < xmin or x_top_r > xmax:
        raise ValueError(
            'Clay core crest is wider than the dam. Reduce core_geometry["crest_width"].'
        )

    # Clip the core top to the actual crest elevation of the dam.
    y_top_l, _ = surface_and_base_at_x(dam_vertices, x_top_l)
    y_top_r, _ = surface_and_base_at_x(dam_vertices, x_top_r)
    if y_top_l is None or y_top_r is None:
        raise ValueError('Core top vertices fall outside the dam polygon.')

    core = np.array([
        [x_base_l, ymin],
        [x_top_l, y_top_l],
        [x_top_r, y_top_r],
        [x_base_r, ymin],
    ], dtype=float)
    return core


def default_phreatic_line(dam_vertices, reservoir_level, core_vertices=None):
    """A simple polyline from the reservoir on the upstream face to the toe."""
    if reservoir_level is None:
        return None
    xmin, xmax, ymin, ymax = polygon_bounds(dam_vertices)
    x_up = x_on_upstream_face(dam_vertices, reservoir_level)
    x_toe, y_toe = downstream_toe(dam_vertices)
    x_crest_l, x_crest_r = crest_x_range(dam_vertices)
    x_mid = 0.5 * (x_crest_l + x_crest_r)

    if core_vertices is None:
        # Homogeneous: gradual drawdown toward the downstream toe.
        return [
            (x_up, reservoir_level),
            (x_mid, ymin + 0.45 * (reservoir_level - ymin)),
            (x_toe, y_toe),
        ]

    cmin, cmax, *_ = polygon_bounds(core_vertices)
    # Impervious core: water stays high upstream, drops across the core.
    return [
        (x_up, reservoir_level),
        (cmin, reservoir_level - 0.10 * (reservoir_level - ymin)),
        (cmax, ymin + 0.25 * (reservoir_level - ymin)),
        (x_toe, y_toe),
    ]


# ---------- materials and slice assembly ------------------------------------

def material_at(x, y, dam_vertices, fill_props, core_vertices=None,
                core_props=None, foundation_props=None, base_y=0.0):
    """Return the material dictionary at (x, y), or None if outside."""
    if core_vertices is not None and core_props is not None:
        if point_in_polygon(x, y, core_vertices):
            return core_props
    if point_in_polygon(x, y, dam_vertices):
        return fill_props
    box = foundation_box(dam_vertices, foundation_props)
    if box is not None:
        if (box['xmin'] - 1e-8 <= x <= box['xmax'] + 1e-8
                and box['ybot'] - 1e-8 <= y <= box['ytop'] + 1e-8):
            return foundation_props
    return None


def slice_weight(x, y_base, y_surface, width, dam_vertices, fill_props,
                 core_vertices, core_props, foundation_props, base_y,
                 phreatic_points, n_samples=40):
    """
    Integrate unit weight from the slip surface up to the dam surface.

    Saturated unit weight is used below the phreatic line.
    """
    height = y_surface - y_base
    if height <= 0:
        return 0.0
    n = max(8, int(n_samples * max(1.0, height / 5.0)))
    ys = np.linspace(y_base + 1e-6, y_surface - 1e-6, n)
    dy = height / n
    y_ph = polyline_y(x, phreatic_points)
    weight = 0.0
    for y in ys:
        mat = material_at(
            x, y, dam_vertices, fill_props, core_vertices, core_props,
            foundation_props, base_y,
        )
        if mat is None:
            continue
        if y_ph is not None and y < y_ph:
            gamma = mat.get('saturated_unit_weight', mat['unit_weight'])
        else:
            gamma = mat.get('unit_weight', 18.0)
        weight += gamma * dy * width
    return weight


def lower_circle_y(cx, cy, radius, x):
    disc = radius ** 2 - (x - cx) ** 2
    if disc < 0:
        return None
    return cy - np.sqrt(disc)


def circle_from_two_points(point_a, point_b, center_x):
    """
    Centre y and radius of the circle that passes through two points and
    has a given centre x-coordinate.
    """
    x1, y1 = map(float, point_a)
    x2, y2 = map(float, point_b)
    cx = float(center_x)
    denom = 2.0 * (y2 - y1)
    if abs(denom) < 1e-10:
        raise ValueError(
            'point_a and point_b have the same elevation; cannot solve for '
            'centre_y. Provide center_y and radius instead.'
        )
    rhs = (x2 ** 2 - x1 ** 2) + (y2 ** 2 - y1 ** 2) + 2.0 * cx * (x1 - x2)
    cy = rhs / denom
    radius = float(np.hypot(x1 - cx, y1 - cy))
    return cy, radius


def resolve_slip_circle(cfg):
    """Return (cx, cy, radius) from the SLIP_CIRCLE configuration."""
    cx = float(cfg['center_x'])
    if cfg.get('point_a') is not None and cfg.get('point_b') is not None:
        cy, radius = circle_from_two_points(cfg['point_a'], cfg['point_b'], cx)
        return cx, cy, radius
    return cx, float(cfg['center_y']), float(cfg['radius'])


def valid_slice_intervals(cx, cy, radius, dam_vertices, foundation_props, base_y,
                          n_probe=600):
    """
    Contiguous x-intervals where the lower arc is below the dam surface
    and inside the analysis domain.
    """
    xmin, xmax, *_ = polygon_bounds(dam_vertices)
    box = foundation_box(dam_vertices, foundation_props)
    if box is not None:
        xmin, xmax = box['xmin'], box['xmax']
    x_left = max(xmin, cx - radius)
    x_right = min(xmax, cx + radius)
    if x_right - x_left < MIN_SLICE_HEIGHT:
        return []

    xs = np.linspace(x_left, x_right, n_probe)
    flags = np.zeros(n_probe, dtype=bool)
    for i, x in enumerate(xs):
        yb = lower_circle_y(cx, cy, radius, x)
        y_top, y_bot = column_top_and_bottom(x, dam_vertices, box)
        if yb is None or y_top is None:
            continue
        if yb >= y_top - MIN_SLICE_HEIGHT:
            continue
        if yb < y_bot - 1e-6:
            continue
        flags[i] = True

    intervals = []
    i = 0
    while i < n_probe:
        if flags[i]:
            j = i
            while j < n_probe and flags[j]:
                j += 1
            if xs[j - 1] - xs[i] >= max(2 * MIN_SLICE_HEIGHT, 3.0):
                intervals.append((float(xs[i]), float(xs[j - 1])))
            i = j
        else:
            i += 1
    return intervals


def assemble_slices(cx, cy, radius, dam_vertices, fill_props,
                    core_vertices=None, core_props=None,
                    foundation_props=None, phreatic_points=None,
                    reservoir_level=None, include_water=True,
                    num_slices=NUM_SLICES, x_range=None,
                    slide_direction='downstream', weight_samples=40,
                    concrete_face=None):
    """Build Bishop slices for one circular slip surface."""
    xmin, xmax, ymin, ymax = polygon_bounds(dam_vertices)
    if x_range is None:
        intervals = valid_slice_intervals(
            cx, cy, radius, dam_vertices, foundation_props, ymin,
        )
        if not intervals:
            return None
        # Prefer the downstream (right-most) interval for a dam slope.
        x_entry, x_exit = max(intervals, key=lambda ab: ab[0])
    else:
        x_entry, x_exit = x_range
    if x_exit - x_entry < 2 * MIN_SLICE_HEIGHT:
        return None

    x_crest_l, x_crest_r = crest_x_range(dam_vertices)
    width = (x_exit - x_entry) / num_slices
    slices = []
    box = foundation_box(dam_vertices, foundation_props)

    for i in range(num_slices):
        x = x_entry + (i + 0.5) * width
        y_base = lower_circle_y(cx, cy, radius, x)
        y_top, y_bot = column_top_and_bottom(x, dam_vertices, box)
        if y_base is None or y_top is None:
            continue
        if y_base > y_top - MIN_SLICE_HEIGHT:
            continue
        if y_base < y_bot - 1e-6:
            continue

        mat_base = material_at(
            x, y_base + 1e-4, dam_vertices, fill_props, core_vertices,
            core_props, foundation_props, ymin,
        )
        if mat_base is None:
            # Base sits exactly on the foundation contact: use fill.
            mat_base = material_at(
                x, min(y_base + 0.05, y_top), dam_vertices, fill_props,
                core_vertices, core_props, foundation_props, ymin,
            )
        if mat_base is None:
            continue

        W = slice_weight(
            x, y_base, y_top, width, dam_vertices, fill_props,
            core_vertices, core_props, foundation_props, ymin,
            phreatic_points, n_samples=weight_samples,
        )

        # Ponded reservoir water above a submerged upstream face.
        if (include_water and reservoir_level is not None
                and x <= x_crest_l and y_top < reservoir_level):
            W += GAMMA_W * (reservoir_level - y_top) * width

        # Concrete face slabs sit on the upstream slope. Their weight remains
        # after rapid drawdown, when the reservoir no longer supports the face.
        W += concrete_slab_surcharge(x, width, dam_vertices, concrete_face)

        y_ph = polyline_y(x, phreatic_points)
        if y_ph is not None and y_base < y_ph:
            u = GAMMA_W * (y_ph - y_base)
        else:
            u = 0.0

        # Inclination of the slice base. Sign is chosen so that a positive
        # W sin(alpha) drives the mass in slide_direction.
        # downstream (+x): active zone is left of the centre (base dips right)
        # upstream   (-x): active zone is right of the centre
        s = (x - cx) / radius
        if slide_direction == 'downstream':
            s = -s
        alpha = np.arcsin(np.clip(s, -1.0, 1.0))

        slices.append({
            'x': x,
            'y_base': y_base,
            'y_top': y_top,
            'width': width,
            'weight': W,
            'cohesion': mat_base['cohesion'],
            'friction_angle': np.deg2rad(mat_base['friction_angle']),
            'pore_pressure': u,
            'angle': alpha,
            'material': mat_base['name'],
        })

    if len(slices) < 5:
        return None
    return slices


def bishop_factor_of_safety(slices, max_iter=MAX_ITERATIONS, tol=FS_TOLERANCE):
    """Iterative Bishop simplified method. Returns FS or None."""
    if not slices:
        return None

    fs = 1.0
    for _ in range(max_iter):
        numer = 0.0
        denom = 0.0
        for sl in slices:
            W = sl['weight']
            c = sl['cohesion']
            phi = sl['friction_angle']
            u = sl['pore_pressure']
            alpha = sl['angle']
            b = sl['width']
            m_alpha = np.cos(alpha) + np.tan(phi) * np.sin(alpha) / fs
            if abs(m_alpha) < 1e-12:
                return None
            numer += (c * b + (W - u * b) * np.tan(phi)) / m_alpha
            denom += W * np.sin(alpha)
        if abs(denom) < 1e-12:
            return None
        if denom < 0:
            # Net moment is opposite to the chosen slide direction.
            return None
        fs_new = numer / denom
        if not np.isfinite(fs_new) or fs_new <= 0:
            return None
        if abs(fs_new - fs) < tol:
            return float(fs_new)
        fs = fs_new
    return float(fs)


# ---------- analysis driver -------------------------------------------------

def resolve_geometry(cfg):
    """Build dam / core polygons from one dam configuration block."""
    if cfg.get('polygon') is not None:
        dam = unclosed(close_polygon(cfg['polygon']))
    else:
        dam = build_trapezoid_dam(**cfg['geometry'])

    core = None
    if cfg.get('core') is not None:
        if cfg.get('core_polygon') is not None:
            core = unclosed(close_polygon(cfg['core_polygon']))
        elif cfg.get('core_geometry') is not None:
            g = cfg['core_geometry']
            core = build_core_polygon(
                dam,
                crest_width=g['crest_width'],
                base_width=g['base_width'],
                center_x=g.get('center_x'),
            )
    return dam, core


def analyse_circle(dam, fill_props, center, radius, core=None, core_props=None,
                   foundation_props=None, phreatic_points=None,
                   reservoir_level=None, include_water=True,
                   num_slices=NUM_SLICES, slide_direction='downstream',
                   weight_samples=40, interval_probes=600, concrete_face=None):
    """
    Factor of safety of one circular slip surface.

    If the circle cuts two disconnected soil masses (typical when it dips
    below the dam base), each mass is analysed and the lower FS is kept.

    Returns a dict with keys fos, slices, center, radius, or None if the
    circle does not cut a valid failure mass.
    """
    cx, cy = center
    ymin = polygon_bounds(dam)[2]
    # Without a foundation layer the circular arc may not pass below the dam base.
    if foundation_props is None and (cy - radius) < ymin - 0.05:
        return None
    intervals = valid_slice_intervals(
        cx, cy, radius, dam, foundation_props, ymin, n_probe=interval_probes,
    )
    best = None
    for x_range in intervals:
        slices = assemble_slices(
            cx, cy, radius, dam, fill_props, core, core_props,
            foundation_props, phreatic_points, reservoir_level,
            include_water, num_slices, x_range=x_range,
            slide_direction=slide_direction, weight_samples=weight_samples,
            concrete_face=concrete_face,
        )
        if slices is None:
            continue
        fos = bishop_factor_of_safety(slices)
        if fos is None:
            continue
        candidate = {
            'fos': fos,
            'slices': slices,
            'center': (cx, cy),
            'radius': radius,
            'x_entry': slices[0]['x'] - 0.5 * slices[0]['width'],
            'x_exit': slices[-1]['x'] + 0.5 * slices[-1]['width'],
        }
        if best is None or fos < best['fos']:
            best = candidate
    return best


def slip_arc_points(result, n=300):
    """Coordinates of the lower arc between the first and last slice."""
    cx, cy = result['center']
    r = result['radius']
    xs = np.linspace(result['x_entry'], result['x_exit'], n)
    xo, yo = [], []
    for x in xs:
        y = lower_circle_y(cx, cy, r, x)
        if y is None:
            continue
        xo.append(x)
        yo.append(y)
    return np.asarray(xo), np.asarray(yo)


# ---------- plotting --------------------------------------------------------

FILL_COLOR = '#d9c2a3'
ROCKFILL_COLOR = '#a39a8c'
CORE_COLOR = '#7a5c4a'
FOUNDATION_COLOR = '#9d8b73'
FACE_COLOR = '#5c5c5c'
WATER_COLOR = '#6baed6'
PHREATIC_COLOR = '#1f4e79'
ARC_COLOR = '#c0392b'


def _draw_dam(ax, dam, core, reservoir_level, phreatic_points, title,
              foundation_props=None, fill_name='Earthfill', concrete_face=None):
    dam_c = close_polygon(dam)
    xmin, xmax, ymin, ymax = polygon_bounds(dam)
    box = foundation_box(dam, foundation_props)
    if box is not None:
        ax.add_patch(Rectangle(
            (box['xmin'], box['ybot']),
            box['xmax'] - box['xmin'],
            box['ytop'] - box['ybot'],
            facecolor=FOUNDATION_COLOR, edgecolor='k',
            linewidth=1.0, alpha=0.95, label='Foundation', zorder=0,
        ))
    body_color = ROCKFILL_COLOR if 'rock' in fill_name.lower() else FILL_COLOR
    ax.add_patch(MplPolygon(
        dam_c, closed=True, facecolor=body_color, edgecolor='k',
        linewidth=1.6, alpha=0.95, label=fill_name, zorder=2,
    ))
    if core is not None:
        ax.add_patch(MplPolygon(
            close_polygon(core), closed=True, facecolor=CORE_COLOR,
            edgecolor='k', linewidth=1.2, alpha=0.95, label='Clay core',
            zorder=3,
        ))

    xmin, xmax, ymin, ymax = polygon_bounds(dam)
    if (reservoir_level is not None
            and reservoir_level > ymin + 0.05):
        x_up = x_on_upstream_face(dam, reservoir_level)
        x_left, _ = upstream_toe(dam)
        water = np.array([
            [x_left - 0.08 * (xmax - xmin), ymin],
            [x_left - 0.08 * (xmax - xmin), reservoir_level],
            [x_up, reservoir_level],
            [x_left, ymin],
        ])
        ax.add_patch(MplPolygon(
            water, closed=True, facecolor=WATER_COLOR, edgecolor='none',
            alpha=0.45, label='Reservoir', zorder=1,
        ))
        ax.axhline(reservoir_level, color=WATER_COLOR, lw=1.0, ls=':',
                   zorder=4)

    if phreatic_points is not None:
        pts = np.asarray(phreatic_points)
        ax.plot(pts[:, 0], pts[:, 1], color=PHREATIC_COLOR, ls='--', lw=2.0,
                label='Phreatic line', zorder=5)
        ax.plot(pts[:, 0], pts[:, 1], 'o', color=PHREATIC_COLOR, ms=5, zorder=5)

    if concrete_face:
        (x0, y0), (x1, y1) = upstream_face_ends(dam)
        ax.plot([x0, x1], [y0, y1], color=FACE_COLOR, lw=4.5,
                solid_capstyle='butt', zorder=7,
                label=concrete_face.get('name', 'Concrete face'))

    ax.plot(dam_c[:, 0], dam_c[:, 1], 'k-', lw=1.8, zorder=6)
    ax.set_title(title, fontsize=18, fontweight='bold')
    ax.set_xlabel('x (m)')
    ax.set_ylabel('y (m)')
    ax.set_aspect('equal', adjustable='box')
    ax.grid(True, alpha=0.3)


def _draw_result(ax, result, fs_corner='upper right'):
    if result is None:
        ax.text(0.5, 0.55, 'No valid slip surface\nfor this circle',
                transform=ax.transAxes, ha='center', va='center',
                fontsize=12, color='firebrick',
                bbox=dict(boxstyle='round', facecolor='white', edgecolor='firebrick'))
        return

    cx, cy = result['center']
    r = result['radius']
    xs, ys = slip_arc_points(result)
    ax.plot(xs, ys, color=ARC_COLOR, lw=2.6, zorder=8,
            label=f"Slip surface  FS = {result['fos']:.3f}")
    ax.plot(cx, cy, 'o', color=ARC_COLOR, ms=8, zorder=9)
    ax.plot([cx, xs[0]], [cy, ys[0]], color=ARC_COLOR, lw=0.8, ls=':', alpha=0.7)
    ax.plot([cx, xs[-1]], [cy, ys[-1]], color=ARC_COLOR, lw=0.8, ls=':', alpha=0.7)

    if DRAW_SLICES:
        for sl in result['slices'][:: max(1, len(result['slices']) // 16)]:
            ax.plot([sl['x'], sl['x']], [sl['y_base'], sl['y_top']],
                    color='0.35', lw=0.6, alpha=0.7, zorder=7)

    if fs_corner == 'upper left':
        tx, ty, ha, va = 0.02, 0.98, 'left', 'top'
    else:
        tx, ty, ha, va = 0.98, 0.98, 'right', 'top'
    ax.text(
        tx, ty,
        f"FS = {result['fos']:.3f}\n"
        f"centre ({cx:.1f}, {cy:.1f}) m\n"
        f"R = {r:.1f} m",
        transform=ax.transAxes, ha=ha, va=va,
        fontsize=12, fontweight='bold', zorder=12,
        bbox=dict(boxstyle='round,pad=0.4', facecolor='#fff6b0',
                  edgecolor=ARC_COLOR, linewidth=1.4),
    )


def _place_materials_legend(ax, grid_on_left, grid_y_mid):
    """Materials legend at the grid's mid-height, on the opposite side."""
    y0, y1 = ax.get_ylim()
    y_frac = (grid_y_mid - y0) / (y1 - y0) if y1 != y0 else 0.5
    y_frac = min(max(y_frac, 0.18), 0.82)
    if grid_on_left:
        ax.legend(loc='center right', bbox_to_anchor=(0.98, y_frac),
                  fontsize=12, framealpha=0.92)
    else:
        ax.legend(loc='center left', bbox_to_anchor=(0.02, y_frac),
                  fontsize=12, framealpha=0.92)


def plot_analyses(cases, save_path=None):
    """Plot one or more dams stacked vertically."""
    n = len(cases)
    fig, axes = plt.subplots(n, 1, figsize=(10.5, 5.6 * n), squeeze=False)
    axes = axes[:, 0]
    grid_cfg = placed_grid_config(cases[0]['dam'])
    grid_mid_x = grid_cfg['lower_left_x'] + 0.5 * grid_cfg['grid_width']
    grid_y_mid = grid_cfg['lower_left_y'] + 0.5 * grid_cfg['grid_height']

    for ax, case in zip(axes, cases):
        dam = case['dam']
        core = case['core']
        _draw_dam(ax, dam, core, case['reservoir_level'], case['phreatic'],
                 case['title'], case.get('foundation'),
                 fill_name=case['fill']['name'],
                 concrete_face=case.get('concrete_face'))
        xmin, xmax, ymin, ymax = polygon_bounds(dam)
        box = foundation_box(dam, case.get('foundation'))
        grid_on_left = grid_mid_x <= 0.5 * (xmin + xmax)
        fs_corner = 'upper right' if grid_on_left else 'upper left'
        _draw_result(ax, case['result'], fs_corner=fs_corner)
        y_top = ymax
        if case['result'] is not None:
            y_top = max(y_top, case['result']['center'][1])
        pad = 0.08 * max(xmax - xmin, 1.0)
        x0 = box['xmin'] if box is not None else xmin
        x1 = box['xmax'] if box is not None else xmax
        y0 = box['ybot'] if box is not None else ymin
        ax.set_xlim(x0 - 0.12 * (xmax - xmin), x1 + pad)
        ax.set_ylim(y0 - 0.04 * (y_top - y0 + 1), Y_AXIS_MAX)
        _place_materials_legend(ax, grid_on_left, grid_y_mid)

    fig.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=160, bbox_inches='tight')
        print(f'  Figure saved: {save_path}')
    return fig


# ---------- reporting -------------------------------------------------------

def print_case(case):
    dam = case['dam']
    core = case['core']
    result = case['result']
    fill_props = case['fill']
    core_props = case['core_props']
    xmin, xmax, ymin, ymax = polygon_bounds(dam)
    print()
    print('=' * 72)
    print(case['title'])
    print('=' * 72)
    print(f'  Dam outline: {unclosed(dam).tolist()}')
    print(f'  Dam base: {xmax - xmin:.2f} m    height: {ymax - ymin:.2f} m')
    print(f'  Fill : {fill_props["name"]}  '
          f"c'={fill_props['cohesion']} kPa  "
          f"phi'={fill_props['friction_angle']} deg  "
          f"gamma={fill_props['unit_weight']} kN/m3")
    face = case.get('concrete_face')
    if face:
        print(f'  Face : {face.get("name", "Concrete face")}  '
              f'thickness={face.get("thickness", 0):.2f} m  '
              f'gamma={face.get("unit_weight", 0):.1f} kN/m3')
    if core is not None and core_props is not None:
        cmin, cmax, *_ = polygon_bounds(core)
        print(f'  Core : {core_props["name"]}  '
              f"c'={core_props['cohesion']} kPa  "
              f"phi'={core_props['friction_angle']} deg  "
              f"gamma={core_props['unit_weight']} kN/m3")
        print(f'         base width {cmax - cmin:.2f} m')
    found = case.get('foundation')
    if found:
        print(f'  Foundation: {found["name"]}  '
              f"c'={found['cohesion']} kPa  "
              f"phi'={found['friction_angle']} deg  "
              f"gamma={found['unit_weight']} kN/m3")
        print(f'         thickness {found.get("thickness", 0):.2f} m')
    print(f'  Slide direction: {case["slide_direction"]}')
    if case['reservoir_level'] is not None:
        print(f'  Reservoir level: {case["reservoir_level"]:.2f} m')
    pfl = case.get('phreatic_from_level')
    if (pfl is not None and case['reservoir_level'] is not None
            and pfl > case['reservoir_level'] + 1e-6):
        print(f'  Rapid drawdown : phreatic held from {pfl:.2f} m pool, '
              f'reservoir lowered to {case["reservoir_level"]:.2f} m')
    elif pfl is not None:
        print(f'  Phreatic from  : {pfl:.2f} m')
    if result is None:
        print('  Factor of safety:  (invalid circle for this geometry)')
        print('  Tip: move the centre or change the radius so the circle')
        print('       cuts the slope (it may pass through the foundation).')
        return
    print(f'  Circle centre: ({result["center"][0]:.3f}, {result["center"][1]:.3f}) m')
    print(f'  Circle radius: {result["radius"]:.3f} m')
    print(f'  Slices used  : {len(result["slices"])}')
    print(f'  Factor of safety (Bishop simplified): {result["fos"]:.4f}')


def resolve_water_levels(rapid_drawdown=None, normal_level=None, drawdown_level=None):
    """
    Return (reservoir_level, phreatic_from_level) for the chosen condition.

    Rapid drawdown: empty reservoir (0 m / dam base), phreatic from the
    normal pool. Steady seepage: both follow NORMAL_RESERVOIR_LEVEL.
    """
    rapid = RAPID_DRAWDOWN if rapid_drawdown is None else rapid_drawdown
    normal = NORMAL_RESERVOIR_LEVEL if normal_level is None else normal_level
    if rapid:
        drawn = 0.0 if drawdown_level is None else drawdown_level
        return drawn, normal
    return normal, None


def cfrd_phreatic_from_waterline(dam, points, reservoir_level):
    """
    Put the first phreatic point on the upstream face at the waterline,
    then keep the remaining points as the low seepage line behind the slab.
    """
    pts = [list(p) for p in points]
    xmin, xmax, ymin, ymax = polygon_bounds(dam)
    if reservoir_level is not None and reservoir_level > ymin + 0.05:
        level = reservoir_level
    else:
        level = NORMAL_RESERVOIR_LEVEL
    level = min(max(float(level), ymin), ymax)
    x_start = x_on_upstream_face(dam, level)
    pts[0] = [x_start, level]
    if len(pts) >= 2 and pts[1][0] <= x_start + 0.2:
        pts[1][0] = x_start + 1.0
    return [tuple(p) for p in pts]


def resolve_phreatic_points(cfg, dam, core):
    """Phreatic polyline: dam override, then the section-1 vector, then default."""
    phreatic = cfg.get('phreatic_line')
    if phreatic is None:
        if cfg.get('concrete_face'):
            phreatic = PHREATIC_LINE_CFRD
        elif core is not None:
            phreatic = PHREATIC_LINE_CLAY_CORE
        else:
            phreatic = PHREATIC_LINE_HOMOGENEOUS
    if phreatic is not None:
        pts = list(phreatic)
        if cfg.get('concrete_face'):
            reservoir_level, _ = resolve_water_levels()
            if RAPID_DRAWDOWN:
                reservoir_level = polygon_bounds(dam)[2]
            pts = cfrd_phreatic_from_waterline(dam, pts, reservoir_level)
        return pts
    reservoir_level, phreatic_from_level = resolve_water_levels()
    seepage_level = (phreatic_from_level
                     if phreatic_from_level is not None
                     else reservoir_level)
    return default_phreatic_line(dam, seepage_level, core)


def active_slide_direction():
    return 'upstream' if RAPID_DRAWDOWN else 'downstream'


def case_title(cfg):
    base = cfg.get('title', 'Earthfill dam')
    if ' — ' in base:
        base = base.split(' — ')[0]
    face = ('inner (upstream) slope' if RAPID_DRAWDOWN
            else 'outer (downstream) slope')
    return f'{base} — {face}'


def circle_on_active_face(cx, cy, radius, dam):
    """Mirror the trial circle onto the inner or outer face."""
    xmin, xmax, *_ = polygon_bounds(dam)
    xmid = 0.5 * (xmin + xmax)
    if RAPID_DRAWDOWN and cx > xmid:
        cx = 2.0 * xmid - cx
    elif (not RAPID_DRAWDOWN) and cx < xmid:
        cx = 2.0 * xmid - cx
    return cx, cy, radius


def placed_grid_config(dam, grid_cfg=None):
    """Return the search-grid config, using lower_left_x if given."""
    cfg = dict(GRID_CONFIG if grid_cfg is None else grid_cfg)
    if cfg.get('lower_left_x') is not None:
        return cfg
    xmin, xmax, *_ = polygon_bounds(dam)
    width = cfg['grid_width']
    margin = min(5.0, 0.05 * max(xmax - xmin, 1.0))
    if RAPID_DRAWDOWN:
        cfg['lower_left_x'] = xmin + margin
    else:
        cfg['lower_left_x'] = xmax - margin - width
    return cfg


def analyse_dam(cfg):
    """Run Bishop analysis for one dam configuration block."""
    slide = active_slide_direction()
    dam, core = resolve_geometry(cfg)
    cx, cy, radius = resolve_slip_circle(cfg['slip_circle'])
    cx, cy, radius = circle_on_active_face(cx, cy, radius, dam)
    core_props = cfg.get('core') if core is not None else None
    reservoir_level, phreatic_from_level = resolve_water_levels()
    ymin = polygon_bounds(dam)[2]
    if RAPID_DRAWDOWN:
        reservoir_level = ymin
    phreatic = resolve_phreatic_points(cfg, dam, core)

    result = analyse_circle(
        dam=dam,
        fill_props=cfg['fill'],
        center=(cx, cy),
        radius=radius,
        core=core,
        core_props=core_props,
        foundation_props=cfg.get('foundation'),
        phreatic_points=phreatic,
        reservoir_level=reservoir_level,
        include_water=cfg.get('include_reservoir_water_weight', True),
        num_slices=NUM_SLICES,
        slide_direction=slide,
        concrete_face=cfg.get('concrete_face'),
    )
    return {
        'title': case_title(cfg),
        'dam': dam,
        'core': core,
        'fill': cfg['fill'],
        'core_props': core_props,
        'reservoir_level': reservoir_level,
        'phreatic_from_level': phreatic_from_level,
        'phreatic': phreatic,
        'slide_direction': slide,
        'rapid_drawdown': RAPID_DRAWDOWN,
        'foundation': cfg.get('foundation'),
        'concrete_face': cfg.get('concrete_face'),
        'result': result,
    }


def prepare_dam(cfg):
    """Geometry, materials and water for one dam, without evaluating a circle."""
    slide = active_slide_direction()
    dam, core = resolve_geometry(cfg)
    reservoir_level, phreatic_from_level = resolve_water_levels()
    ymin = polygon_bounds(dam)[2]
    if RAPID_DRAWDOWN:
        reservoir_level = ymin
    phreatic = resolve_phreatic_points(cfg, dam, core)
    core_props = cfg.get('core') if core is not None else None
    return {
        'title': case_title(cfg),
        'dam': dam,
        'core': core,
        'fill': cfg['fill'],
        'core_props': core_props,
        'foundation': cfg.get('foundation'),
        'reservoir_level': reservoir_level,
        'phreatic_from_level': phreatic_from_level,
        'phreatic': phreatic,
        'slide_direction': slide,
        'include_water': cfg.get('include_reservoir_water_weight', True),
        'rapid_drawdown': RAPID_DRAWDOWN,
        'concrete_face': cfg.get('concrete_face'),
        'result': None,
    }


def evaluate_circle(prepared, center, radius, num_slices=NUM_SLICES,
                    weight_samples=40, interval_probes=600):
    return analyse_circle(
        dam=prepared['dam'],
        fill_props=prepared['fill'],
        center=center,
        radius=radius,
        core=prepared['core'],
        core_props=prepared['core_props'],
        foundation_props=prepared['foundation'],
        phreatic_points=prepared['phreatic'],
        reservoir_level=prepared['reservoir_level'],
        include_water=prepared['include_water'],
        num_slices=num_slices,
        slide_direction=prepared['slide_direction'],
        weight_samples=weight_samples,
        interval_probes=interval_probes,
        concrete_face=prepared.get('concrete_face'),
    )


def make_center_grid(cfg):
    ll_x = cfg['lower_left_x']
    ll_y = cfg['lower_left_y']
    nx = max(2, int(np.round(cfg['grid_width'] / cfg['grid_spacing_x'])) + 1)
    ny = max(2, int(np.round(cfg['grid_height'] / cfg['grid_spacing_y'])) + 1)
    x_centers = np.linspace(ll_x, ll_x + cfg['grid_width'], nx)
    y_centers = np.linspace(ll_y, ll_y + cfg['grid_height'], ny)
    return x_centers, y_centers


def radii_for_centre(cy, radii, y_crest, y_floor):
    """
    Use the configured radii, but stretch them if they cannot reach the dam.

    A centre high above the crest needs a larger R than one sitting just
    over the slope; otherwise that grid cell is never coloured.
    """
    n = max(2, len(radii))
    r_lo = float(np.min(radii))
    r_hi = float(np.max(radii))
    r_touch = cy - y_crest + 0.5
    r_deep = cy - y_floor - 0.05
    if r_hi < r_touch and r_deep > r_touch:
        r_lo = max(r_touch, 1.0)
        r_hi = max(r_deep, r_lo + 1.0)
        return np.linspace(r_lo, r_hi, n)
    return np.asarray(radii, dtype=float)


def search_dam(cfg, x_centers, y_centers, radii):
    prepared = prepare_dam(cfg)
    nx, ny = len(x_centers), len(y_centers)
    n_total = nx * ny * len(radii)
    fos_grid = np.full((ny, nx), np.nan)
    best = None
    tested = 0
    valid = 0
    t0 = time.time()
    next_report = max(1, n_total // 10)

    print()
    print('=' * 72)
    print(f"Grid search: {prepared['title']}")
    print('=' * 72)
    print(f"  Slide direction : {prepared['slide_direction']}")
    print(f"  Centres         : {nx} x {ny} = {nx * ny}")
    print(f"  Radii           : {len(radii)}  "
          f"({radii[0]:.1f} to {radii[-1]:.1f} m)")
    print(f"  Combinations    : {n_total}")

    ymin = polygon_bounds(prepared['dam'])[2]
    ymax = polygon_bounds(prepared['dam'])[3]
    foundation_props = prepared['foundation']
    box = foundation_box(prepared['dam'], foundation_props)
    y_floor = box['ybot'] if box is not None else ymin

    for j, cy in enumerate(y_centers):
        local_radii = radii_for_centre(cy, radii, ymax, y_floor)
        for i, cx in enumerate(x_centers):
            best_here = np.inf
            for radius in local_radii:
                tested += 1
                if foundation_props is None and (cy - radius) < ymin - 0.05:
                    continue
                result = evaluate_circle(
                    prepared, (cx, cy), radius,
                    SEARCH_NUM_SLICES, SEARCH_WEIGHT_SAMPLES,
                    interval_probes=180,
                )
                if result is None:
                    continue
                fos = result['fos']
                if not (0.0 < fos < 100.0):
                    continue
                valid += 1
                if fos < best_here:
                    best_here = fos
                if best is None or fos < best['fos']:
                    best = result
                    print(f"    New minimum FS = {fos:.3f}  "
                          f"centre ({cx:.1f}, {cy:.1f})  R = {radius:.1f} m")
                if tested % next_report == 0:
                    elapsed = time.time() - t0
                    print(f"    ... {tested}/{n_total} "
                          f"({100.0 * tested / n_total:.0f}%)  "
                          f"{elapsed:.1f} s")
            if best_here < np.inf:
                fos_grid[j, i] = best_here

    elapsed = time.time() - t0
    n_cells = nx * ny
    n_coloured = int(np.sum(~np.isnan(fos_grid)))
    print(f"  Tested {tested} circles, {valid} valid, in {elapsed:.1f} s")
    print(f"  Coloured centres  : {n_coloured}/{n_cells}")

    if best is not None:
        refined = evaluate_circle(
            prepared, best['center'], best['radius'],
            NUM_SLICES, 40, interval_probes=600,
        )
        if refined is not None:
            best = refined
        print(f"  Critical FS     : {best['fos']:.4f}")
        print(f"  Circle centre   : ({best['center'][0]:.3f}, "
              f"{best['center'][1]:.3f}) m")
        print(f"  Circle radius   : {best['radius']:.3f} m")
    else:
        print('  No valid slip surface found in this grid.')
        print('  Move the grid, enlarge it, or change the radius range.')

    prepared['result'] = best
    prepared['fos_grid'] = fos_grid
    prepared['x_centers'] = x_centers
    prepared['y_centers'] = y_centers
    return prepared


def plot_search(cases, grid_cfg, save_path=None):
    n = len(cases)
    fig, axes = plt.subplots(n, 1, figsize=(10.5, 5.8 * n), squeeze=False)
    axes = axes[:, 0]

    ll_x = grid_cfg['lower_left_x']
    ll_y = grid_cfg['lower_left_y']
    width = grid_cfg['grid_width']
    height = grid_cfg['grid_height']

    for ax, case in zip(axes, cases):
        _draw_dam(ax, case['dam'], case['core'], case['reservoir_level'],
                  case['phreatic'], case['title'], case.get('foundation'),
                  fill_name=case['fill']['name'],
                  concrete_face=case.get('concrete_face'))

        grid_patch = Rectangle(
            (ll_x, ll_y), width, height,
            linewidth=1.4, edgecolor='royalblue', facecolor='none',
            linestyle='--', zorder=4, label='Search grid',
        )
        ax.add_patch(grid_patch)

        fos_grid = case['fos_grid']
        x_c = case['x_centers']
        y_c = case['y_centers']
        dx = 0.5 * (x_c[1] - x_c[0]) if len(x_c) > 1 else 0.5
        dy = 0.5 * (y_c[1] - y_c[0]) if len(y_c) > 1 else 0.5
        x_edges = np.concatenate([x_c[:1] - dx, 0.5 * (x_c[1:] + x_c[:-1]),
                                  x_c[-1:] + dx])
        y_edges = np.concatenate([y_c[:1] - dy, 0.5 * (y_c[1:] + y_c[:-1]),
                                  y_c[-1:] + dy])
        X, Y = np.meshgrid(x_edges, y_edges)
        cmap = plt.get_cmap('RdYlGn').copy()
        cmap.set_bad(color='#d0d0d0', alpha=0.85)
        display = np.ma.masked_invalid(np.clip(fos_grid, None, MAX_DISPLAY_FS))
        im = ax.pcolormesh(
            X, Y, display, cmap=cmap, vmin=0.0, vmax=MAX_DISPLAY_FS,
            alpha=0.7, shading='flat', zorder=3,
        )
        cbar = fig.colorbar(im, ax=ax, fraction=0.035, pad=0.02)
        cbar.set_label('Minimum FS at centre (grey = no valid circle)')
        finite = fos_grid[np.isfinite(fos_grid)]
        if len(finite) and np.nanmax(finite) > MAX_DISPLAY_FS:
            cbar.ax.text(0.5, 1.04, f'>{MAX_DISPLAY_FS:g}',
                         transform=cbar.ax.transAxes,
                         ha='center', va='bottom', fontsize=8)

        xmin, xmax, ymin, ymax = polygon_bounds(case['dam'])
        box = foundation_box(case['dam'], case.get('foundation'))
        grid_mid = ll_x + 0.5 * width
        dam_mid = 0.5 * (xmin + xmax)
        grid_on_left = grid_mid <= dam_mid
        fs_corner = 'upper right' if grid_on_left else 'upper left'
        _draw_result(ax, case['result'], fs_corner=fs_corner)

        y_top = max(ymax, ll_y + height)
        if case['result'] is not None:
            y_top = max(y_top, case['result']['center'][1])
        pad = 0.08 * max(xmax - xmin, 1.0)
        x0 = min(xmin, ll_x)
        x1 = max(xmax, ll_x + width)
        y0 = ymin
        if box is not None:
            x0 = min(x0, box['xmin'])
            x1 = max(x1, box['xmax'])
            y0 = box['ybot']
        ax.set_xlim(x0 - 0.08 * (xmax - xmin), x1 + pad)
        ax.set_ylim(y0 - 0.04 * (y_top - y0 + 1), Y_AXIS_MAX)
        _place_materials_legend(ax, grid_on_left, ll_y + 0.5 * height)

    fig.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=160, bbox_inches='tight')
        print(f'  Figure saved: {save_path}')
    return fig


# ---------- main ------------------------------------------------------------

def print_water_condition():
    reservoir_level, phreatic_from_level = resolve_water_levels()
    print()
    if RAPID_DRAWDOWN:
        print('Water condition : RAPID DRAWDOWN')
        print(f'  Reservoir (empty)            : {reservoir_level:.2f} m')
        print(f'  Phreatic line (from old pool): {phreatic_from_level:.2f} m')
        print('  Search face                  : inner (upstream) slope')
    else:
        print('Water condition : STEADY SEEPAGE')
        print(f'  Reservoir and phreatic line  : {reservoir_level:.2f} m')
        print('  Search face                  : outer (downstream) slope')
    print(f"Analysis mode    : "
          f"{'grid search for critical circle' if FIND_CRITICAL_CIRCLE else 'single slip circle'}")


def enabled_dams():
    configs = [HOMOGENEOUS_DAM, CLAY_CORE_DAM, ROCKFILL_CFRD_DAM]
    cases = [c for c in configs if c.get('enabled', True)]
    if not cases:
        raise ValueError('No dams enabled. Set enabled=True on at least one dam block.')
    return cases


def run(return_figure=False):
    print_water_condition()
    configs = enabled_dams()
    save_path = FIGURE_NAME if SAVE_FIGURE else None

    if FIND_CRITICAL_CIRCLE:
        first_dam, _ = resolve_geometry(configs[0])
        grid_cfg = placed_grid_config(first_dam)
        x_centers, y_centers = make_center_grid(grid_cfg)
        radii = np.linspace(
            RADIUS_CONFIG['min_radius'],
            RADIUS_CONFIG['max_radius'],
            RADIUS_CONFIG['num_radii'],
        )
        cases = [search_dam(cfg, x_centers, y_centers, radii) for cfg in configs]
        fig = plot_search(cases, grid_cfg, save_path)
    else:
        cases = []
        for cfg in configs:
            case = analyse_dam(cfg)
            print_case(case)
            cases.append(case)
        fig = plot_analyses(cases, save_path)

    if return_figure:
        return cases, fig
    if SHOW_PLOT:
        plt.show()
    else:
        plt.close(fig)
    return cases


if __name__ == '__main__':
    run()
