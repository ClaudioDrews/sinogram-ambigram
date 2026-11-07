"""PRC construction method: reconciling the extremities of a rotated form.

The Japanese inventory is built from stroke skeletons. The PRC inventory
(MMah ``graphics.txt``, Arphic Public License) carries stroke *medians*
instead, which is closer to how a PRC form is actually written: the median of
a stroke is its spine, and the spine carries the information a reader uses to
separate one stroke from the next.

This module turns that data into geometry a construction can act on:

* :func:`reconcile` moves and re-weights the *extremities* of the strokes so
  that a form and its half-turn describe the same drawing;
* :func:`find_centre` searches the rotation centre, which is the single
  parameter that decides whether a form reads at all in both orientations;
* :func:`legibility` returns the two-part proxy used to rank candidates.

The rules and the constants are documented in ``theory/prc-construction-method.md``.
Nothing here certifies that a drawing is readable: the output is a candidate,
and reader evidence is still required before any legibility claim.

**Units.** Every length is in *box units* on a 109 x 109 grid, the same grid
the rest of the pipeline uses. One box unit is 0.99% of the em square.
"""
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path

import numpy as np

EM = 109.0
GRID = 109

#: Length over which a terminal is faded in and out, in box units.
KAPPA = 6.0
#: Two extremities closer than this are treated as the same place.
#: Measured: the median terminal-to-terminal distance is 7.99 units.
DELTA_F = 8.0
#: A terminal is contested when foreign ink comes this close.
#: Measured: the 75th percentile of the terminal-to-terminal distance.
R_CONTESTED = 12.4
#: A half-turn image further than this from any stroke is an orphan.
ORPHAN_TOL = 2.0
#: Centre offsets searched around the ink centroid, in box units.
CENTRE_STEP = 1.5
CENTRE_MAX = 3.0
#: Thickness multipliers a sector may take (see :func:`search_sector_multipliers`).
SECTOR_MULTIPLIERS = (0.55, 0.70, 0.85, 1.00, 1.15, 1.30, 1.45)
#: A sector manipulation may not erase more than this share of the original ink.
RETENTION_MIN = 0.90
#: ... nor add more than this share of ink.
GROWTH_MAX = 1.30
#: Cells kept away from a sector border, so the multiplier is exact inside.
SECTOR_MARGIN = 6
#: Smoothing of the sector multiplier field, in cells.
SECTOR_SIGMA = 3.0

_NUM = re.compile(r"-?\d*\.?\d+(?:[eE][-+]?\d+)?")


# --------------------------------------------------------------------------
# geometry primitives
# --------------------------------------------------------------------------
@dataclass
class Stroke:
    """A stroke spine plus its half-width profile."""

    median: np.ndarray
    half_width: np.ndarray

    @property
    def length(self) -> float:
        return float(np.linalg.norm(np.diff(self.median, axis=0), axis=1).sum())

    def arc(self) -> np.ndarray:
        """Arc length at every sample, from the start of the stroke."""
        seg = np.linalg.norm(np.diff(self.median, axis=0), axis=1)
        return np.concatenate([[0.0], np.cumsum(seg)])

    def ends(self) -> list[np.ndarray]:
        return [self.median[0], self.median[-1]]


@dataclass
class Terminal:
    """One extremity of one stroke."""

    stroke: int
    end: int            # 0 = start of the stroke, 1 = end
    point: np.ndarray
    weight: float

    def as_dict(self) -> dict:
        return {"stroke": self.stroke, "end": self.end,
                "x": float(self.point[0]), "y": float(self.point[1]),
                "weight": float(self.weight)}


def resample(poly: np.ndarray, step: float = 1.0) -> np.ndarray:
    """Resample a polyline at a constant arc-length step."""
    poly = np.asarray(poly, dtype=np.float64)
    if len(poly) < 2:
        return poly
    seg = np.linalg.norm(np.diff(poly, axis=0), axis=1)
    cum = np.concatenate([[0.0], np.cumsum(seg)])
    total = cum[-1]
    if total <= 0:
        return poly[:1]
    n = max(2, int(np.ceil(total / step)) + 1)
    t = np.linspace(0.0, total, n)
    return np.column_stack([np.interp(t, cum, poly[:, 0]),
                            np.interp(t, cum, poly[:, 1])])


def retarget(median: np.ndarray, half_width: np.ndarray) -> np.ndarray:
    """Re-map a width profile onto a median whose shape has changed."""
    if len(half_width) < 2 or len(median) < 2:
        return half_width
    t_old = np.linspace(0.0, 1.0, len(half_width))
    arc = Stroke(median, half_width).arc()
    total = arc[-1]
    if total <= 0:
        return half_width
    return np.interp(arc / total, t_old, half_width)


def stroke_polygon(median: np.ndarray, half_width: np.ndarray) -> np.ndarray:
    """Outline of a tapered stroke: the spine offset by half the width."""
    if len(median) < 2:
        return np.zeros((0, 2))
    tang = np.gradient(median, axis=0)
    norm = np.linalg.norm(tang, axis=1, keepdims=True)
    norm[norm == 0] = 1.0
    tang = tang / norm
    normal = np.column_stack([-tang[:, 1], tang[:, 0]])
    left = median + normal * (half_width / 2)[:, None]
    right = median - normal * (half_width / 2)[:, None]
    return np.vstack([left, right[::-1]])


def fill_polygon(poly: np.ndarray, grid: np.ndarray) -> None:
    """Even-odd scanline fill of one polygon into a boolean grid."""
    if len(poly) < 3:
        return
    n = grid.shape[0]
    ys = poly[:, 1]
    for row in range(max(0, int(np.floor(ys.min()))), min(n - 1, int(np.ceil(ys.max()))) + 1):
        yc = row + 0.5
        xs = []
        m = len(poly)
        for i in range(m):
            ax, ay = poly[i]
            bx, by = poly[(i + 1) % m]
            if (ay <= yc < by) or (by <= yc < ay):
                t = (yc - ay) / (by - ay)
                xs.append(ax + t * (bx - ax))
        xs.sort()
        for k in range(0, len(xs) - 1, 2):
            xa = max(0, int(np.ceil(xs[k] - 0.5)))
            xb = min(n - 1, int(np.floor(xs[k + 1] - 0.5)))
            if xb >= xa:
                grid[row, xa:xb + 1] = True


def raster(strokes: list[Stroke], grid: int = GRID) -> np.ndarray:
    """Render strokes as an occupancy grid."""
    out = np.zeros((grid, grid), dtype=bool)
    for s in strokes:
        fill_polygon(stroke_polygon(s.median, s.half_width), out)
    return out


def half_turn(points: np.ndarray, centre: tuple[float, float]) -> np.ndarray:
    """Half-turn about ``centre``: R_c(p) = 2c - p."""
    return np.column_stack([2 * centre[0] - points[:, 0],
                             2 * centre[1] - points[:, 1]])


def half_turn_grid(grid: np.ndarray, centre: tuple[float, float]) -> np.ndarray:
    """Half-turn of an occupancy grid about ``centre``."""
    out = np.zeros_like(grid)
    src = np.argwhere(grid)
    if len(src) == 0:
        return out
    x = src[:, 1] + 0.5
    y = src[:, 0] + 0.5
    cc = np.clip(np.round(2 * centre[0] - x - 0.5).astype(int), 0, grid.shape[1] - 1)
    rr = np.clip(np.round(2 * centre[1] - y - 0.5).astype(int), 0, grid.shape[0] - 1)
    out[rr, cc] = True
    return out


def ink_overlap(a: np.ndarray, b: np.ndarray) -> float:
    """Share of one drawing's ink that the other drawing also covers."""
    if not a.any() or not b.any():
        return 0.0
    inter = int(np.logical_and(a, b).sum())
    return inter / max(int(a.sum()), int(b.sum()))


def symmetric_ink(strokes: list[Stroke], centre: tuple[float, float],
                  reference: np.ndarray | None = None) -> float:
    """The share of the *original* ink that is symmetric under the half-turn.

    Measuring against the original drawing and not against the edited one is
    what stops the rules from winning by erasing: a drawing can always be
    made symmetric by deleting everything that is not, and a relative
    overlap would reward exactly that.
    """
    g = raster(strokes)
    both = int(np.logical_and(g, half_turn_grid(g, centre)).sum())
    ref = g if reference is None else reference
    return both / max(float(ref.sum()), 1.0)


def retention(strokes: list[Stroke], reference: np.ndarray) -> float:
    """How much of the original ink the edited drawing still carries."""
    return float(raster(strokes).sum()) / max(float(reference.sum()), 1.0)


def ink_centroid(strokes: list[Stroke]) -> tuple[float, float]:
    """Centroid of the stroke spines - the natural rotation centre."""
    if not strokes:
        return (EM / 2, EM / 2)
    pts = np.vstack([s.median for s in strokes])
    return (float(pts[:, 0].mean()), float(pts[:, 1].mean()))


def terminals(strokes: list[Stroke]) -> list[Terminal]:
    out = []
    for i, s in enumerate(strokes):
        out.append(Terminal(i, 0, s.median[0], float(s.half_width[0])))
        out.append(Terminal(i, 1, s.median[-1], float(s.half_width[-1])))
    return out


def ramp(distance: np.ndarray, kappa: float = KAPPA) -> np.ndarray:
    """The taper profile psi(u) = (1 - u)^2 on [0, 1]."""
    return np.clip(1.0 - distance / kappa, 0.0, 1.0) ** 2


# --------------------------------------------------------------------------
# the rules
# --------------------------------------------------------------------------
def cluster_terminals(strokes: list[Stroke],
                      delta_f: float = DELTA_F) -> list[list[int]]:
    """Group the extremities into the places they occupy.

    Two extremities belong to the same place when they are within
    ``delta_f`` of each other. At a frame corner the horizontal and the
    vertical both end there, so the corner is one place shared by two
    extremities, not two places. Working per place is what makes the rules
    behave on real forms.
    """
    tp = terminals(strokes)
    parent = list(range(len(tp)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for i in range(len(tp)):
        for j in range(i + 1, len(tp)):
            if float(np.linalg.norm(tp[i].point - tp[j].point)) <= delta_f:
                a, b = find(i), find(j)
                if a != b:
                    parent[max(a, b)] = min(a, b)
    groups: dict[int, list[int]] = {}
    for i in range(len(tp)):
        groups.setdefault(find(i), []).append(i)
    return [sorted(v) for _, v in sorted(groups.items())]


def cluster_points(strokes: list[Stroke], clusters: list[list[int]]) -> list[np.ndarray]:
    """The centre of each place."""
    tp = terminals(strokes)
    out = []
    for c in clusters:
        pts = np.vstack([tp[i].point for i in c])
        out.append(pts.mean(axis=0))
    return out


def pair_places(strokes: list[Stroke], centre: tuple[float, float],
                delta_f: float = DELTA_F) -> list[tuple[int, int, float]]:
    """Pair the places that the half-turn maps onto each other.

    A place is paired with the place its half-turn image lands on, provided
    the two are within ``delta_f``. The pairing is mutual: if the image of
    place A lands on place B, the image of B lands back on A.
    """
    clusters = cluster_terminals(strokes, delta_f)
    centres = cluster_points(strokes, clusters)
    images = [half_turn(c.reshape(1, 2), centre)[0] for c in centres]
    best = []
    for i, q in enumerate(images):
        cand = None
        for j, c in enumerate(centres):
            if i == j:
                continue
            d = float(np.linalg.norm(c - q))
            if cand is None or d < cand[0]:
                cand = (d, j)
        best.append(cand)
    pairs = []
    for i, cand in enumerate(best):
        if cand is None or cand[0] > delta_f:
            continue
        j = cand[1]
        if j <= i:
            continue
        if best[j] is None or best[j][1] != i:
            continue
        pairs.append((i, j, max(cand[0], best[j][0])))
    return pairs, clusters, centres


def reconcile(strokes: list[Stroke], centre: tuple[float, float],
              delta_f: float = DELTA_F) -> dict:
    """Apply the extremity rules to a drawing, in place.

    The drawing has to be its own half-turn. The half-turn maps every place
    (a corner where one or more extremities meet) onto another place. The
    rules act on that correspondence:

    R1  *weight* - the places that the half-turn maps onto each other must
        carry the same weight. The lighter one is thickened over the taper
        length kappa until it matches the heavier one.
    R3  *structure* - when the half-turn image of a place falls on the body
        of a stroke instead of on one of its extremities, that stroke is
        split at the place, so that both orientations see the same
        extremity structure. The ink does not change; the stroke count of
        the drawing does.

    R2 (direction) is measured, not edited: the half-turn reverses the
    tangent of a stroke, so the two ends of a rotation-matched stroke must
    face opposite ways. The deviation is reported in ``direction_error``.

    Returns a summary of what changed.
    """
    clusters = cluster_terminals(strokes, delta_f)
    centres = cluster_points(strokes, clusters)
    images = [half_turn(c.reshape(1, 2), centre)[0] for c in centres]

    nearest = []
    for i, q in enumerate(images):
        best = None
        for j, c in enumerate(centres):
            if i == j:
                continue
            d = float(np.linalg.norm(c - q))
            if best is None or d < best[0]:
                best = (d, j)
        nearest.append(best)

    pairs = []
    for i, cand in enumerate(nearest):
        if cand is None or cand[0] > delta_f:
            continue
        j = cand[1]
        back = nearest[j]
        if back is None or back[1] != i or i >= j:
            continue
        pairs.append((i, j, max(cand[0], back[0])))

    tp = terminals(strokes)
    reweighted = 0
    for ia, ib, _gap in pairs:
        group = clusters[ia] + clusters[ib]
        target = max(tp[i].weight for i in group)
        for idx in group:
            _equalise(strokes, tp[idx], target)
            reweighted += 1

    trimmed = extended = orphans = 0
    for i, cand in enumerate(nearest):
        if cand is not None and cand[0] <= delta_f:
            continue        # already matched with a place
        q = images[i]
        hit = _stroke_at(strokes, q)
        if hit is None:
            orphans += 1
            continue
        si, j, dist = hit
        if dist > ORPHAN_TOL:
            orphans += 1
            continue
        s = strokes[si]
        if 0 < j < len(s.median) - 1:
            split_stroke(strokes, si, q, j)
            trimmed += 1
        else:
            orphans += 1

    return {"places": len(clusters), "pairs": len(pairs),
            "reweighted": reweighted, "trimmed": trimmed,
            "extended": extended, "orphans": orphans,
            "direction_error": direction_error(strokes, centre, delta_f)}


def split_stroke(strokes: list[Stroke], index: int, point: np.ndarray,
                 at: int) -> None:
    """Split a stroke at a point of its body, creating a new extremity.

    A PRC frame draws its top and right sides as one stroke (横折). The
    corner between them is a bend, not an extremity, so the drawing has an
    extremity there in one orientation only. Splitting the stroke at the
    corner gives both orientations the same extremity structure. The ink is
    unchanged; only the way the strokes are counted changes.
    """
    s = strokes[index]
    med, hw = s.median, s.half_width
    at = max(1, min(len(med) - 2, at))
    head = Stroke(med[:at + 1].copy(), hw[:at + 1].copy())
    tail = Stroke(med[at:].copy(), hw[at:].copy())
    head.median[-1] = point
    tail.median[0] = point
    strokes[index] = head
    strokes.insert(index + 1, tail)


def _stroke_at(strokes: list[Stroke], point: np.ndarray):
    """The stroke and the sample index closest to ``point``."""
    best = None
    for i, s in enumerate(strokes):
        d = np.linalg.norm(s.median - point, axis=1)
        k = int(np.argmin(d))
        if best is None or d[k] < best[2]:
            best = (i, k, float(d[k]))
    return best


def _retarget_end(stroke: Stroke, point: np.ndarray, index: int) -> int:
    """Move the nearer extremity of ``stroke`` onto ``point``.

    Returns +1 when the stroke was trimmed, -1 when it was extended and 0
    when nothing had to be done.
    """
    n = len(stroke.median)
    if n < 2:
        return 0
    index = max(0, min(n - 1, index))
    to_start = index
    to_end = n - 1 - index
    if to_start <= to_end:
        if np.allclose(stroke.median[0], point, atol=0.5):
            return 0
        stroke.median = stroke.median.copy()
        stroke.median[0] = point
        stroke.half_width = stroke.half_width.copy()
        stroke.half_width[0] = stroke.half_width[min(1, n - 1)]
        stroke.half_width = retarget(stroke.median, stroke.half_width)
        return 1
    if np.allclose(stroke.median[-1], point, atol=0.5):
        return 0
    stroke.median = stroke.median.copy()
    stroke.median[-1] = point
    stroke.half_width = stroke.half_width.copy()
    stroke.half_width[-1] = stroke.half_width[max(0, n - 2)]
    stroke.half_width = retarget(stroke.median, stroke.half_width)
    return 1


def direction_error(strokes: list[Stroke], centre: tuple[float, float],
                    delta_f: float = DELTA_F) -> float:
    """Median angular deviation of the rotation-matched extremities.

    The half-turn reverses a tangent, so the two ends of a rotation-matched
    pair must face opposite ways. A positive value means the ends disagree
    by that many degrees.
    """
    clusters = cluster_terminals(strokes, delta_f)
    centres = cluster_points(strokes, clusters)
    images = [half_turn(c.reshape(1, 2), centre)[0] for c in centres]
    tp = terminals(strokes)
    devs = []
    for i, c in enumerate(centres):
        q = images[i]
        best = None
        for j, c2 in enumerate(centres):
            if i == j:
                continue
            d = float(np.linalg.norm(c2 - q))
            if best is None or d < best[0]:
                best = (d, j)
        if best is None or best[0] > delta_f:
            continue
        j = best[1]
        if j <= i:
            continue
        for idx in clusters[i] + clusters[j]:
            s = strokes[tp[idx].stroke]
            end = tp[idx].end
            if len(s.median) < 3:
                continue
            tan = s.median[-1] - s.median[-2] if end == 1 else s.median[1] - s.median[0]
            n = np.linalg.norm(tan)
            if n == 0:
                continue
            tan = tan / n
            devs.append(float(np.degrees(np.arctan2(tan[1], tan[0]))))
    if not devs:
        return 0.0
    return float(np.median(devs))


def _equalise(strokes: list[Stroke], term: Terminal, target: float) -> None:
    """Thicken one extremity to ``target`` over the taper length."""
    s = strokes[term.stroke]
    if target <= term.weight + 1e-9:
        return
    arc = s.arc()
    s_end = arc[-1] if term.end == 1 else 0.0
    add = (target - term.weight) * ramp(np.abs(arc - s_end))
    s.half_width = s.half_width + add


def find_centre(strokes: list[Stroke], grid: int = GRID,
                step: float = CENTRE_STEP, span: float = CENTRE_MAX) -> tuple:
    """Search the rotation centre around the ink centroid.

    The centre is the parameter that decides whether a form reads in both
    orientations. On the PRC data the optimum sits systematically below the
    centre of the em square, because the source font places the ideographic
    square above the geometric centre of the em.
    """
    base = ink_centroid(strokes)
    offsets = np.arange(-span, span + 1e-9, step)
    ref = raster(strokes, grid)
    best = (base, -1.0)
    for dy in offsets:
        for dx in offsets:
            c = (base[0] + float(dx), base[1] + float(dy))
            o = symmetric_ink(strokes, c, ref)
            if o > best[1]:
                best = (c, o)
    return best


def legibility(strokes: list[Stroke], centre: tuple[float, float],
               reference: np.ndarray | None = None) -> dict:
    """The legibility proxy of the construction method.

    ``mu``  the share of the original ink that is symmetric under the
            half-turn - the absolute amount of ink that now works in both
            orientations;
    ``ret`` the share of the original ink that is still there, which has to
            stay high: a rule that buys symmetry by erasing is not a rule;
    ``pi``  the share of places that are rotation-matched;
    ``L``   the proxy, mu times the smaller of the two retentions.
    """
    ref = raster(strokes) if reference is None else reference
    mu = symmetric_ink(strokes, centre, ref)
    ret = retention(strokes, ref)
    pairs, clusters, _ = pair_places(strokes, centre)
    pi = 2 * len(pairs) / max(len(clusters), 1)
    return {"mu": mu, "ret": ret, "pi": pi, "L": mu * ret}


# --------------------------------------------------------------------------
# R-SECT: sector-wise thickness
# --------------------------------------------------------------------------
def gaussian_kernel(sigma: float) -> np.ndarray:
    r = max(1, int(3 * sigma))
    x = np.arange(-r, r + 1)
    k = np.exp(-0.5 * (x / sigma) ** 2)
    return k / k.sum()


def blur(img: np.ndarray, kernel: np.ndarray) -> np.ndarray:
    """Separable convolution with edge padding."""
    r = (len(kernel) - 1) // 2
    pad = np.pad(img, ((0, 0), (r, r)), mode="edge")
    out = np.zeros_like(img, dtype=np.float64)
    for i, w in enumerate(kernel):
        out += w * pad[:, i:i + img.shape[1]]
    pad = np.pad(out, ((r, r), (0, 0)), mode="edge")
    out2 = np.zeros_like(img, dtype=np.float64)
    for i, w in enumerate(kernel):
        out2 += w * pad[i:i + img.shape[0], :]
    return out2


def sector_masks(grid: int = GRID, margin: int = SECTOR_MARGIN) -> np.ndarray:
    """Nine binary sector masks, eroded so their interiors are exact.

    The box is divided in three rows and three columns. The masks are
    eroded by ``margin`` cells so that the multiplier field is exact in the
    interior of a sector and only blends near the borders.
    """
    masks = np.zeros((9, grid, grid), dtype=bool)
    step = grid / 3.0
    for i in range(3):
        for j in range(3):
            r0, r1 = int(round(i * step)), int(round((i + 1) * step))
            c0, c1 = int(round(j * step)), int(round((j + 1) * step))
            m = np.zeros((grid, grid), dtype=bool)
            m[r0:r1, c0:c1] = True
            if margin > 0:
                m[:r0 + margin, :] = False
                m[max(0, r1 - margin):, :] = False
                m[:, :c0 + margin] = False
                m[:, max(0, c1 - margin):] = False
            masks[i * 3 + j] = m
    return masks


def multiplier_field(multipliers, masks: np.ndarray,
                     kernel: np.ndarray | None = None) -> np.ndarray:
    """A smooth thickness field, exact in the interior of each sector.

    The field is a normalised convolution of the sector values, so the
    multiplier of a sector is exact away from the borders and the borders
    blend smoothly. A hard step at a sector border would put a visible
    notch in the middle of a stroke.
    """
    if kernel is None:
        kernel = gaussian_kernel(SECTOR_SIGMA)
    num = np.zeros(masks.shape[1:], dtype=np.float64)
    den = np.zeros(masks.shape[1:], dtype=np.float64)
    for s in range(9):
        num += blur(masks[s] * float(multipliers[s]), kernel)
        den += blur(masks[s].astype(np.float64), kernel)
    field = np.where(den > 1e-9, num / np.maximum(den, 1e-9), 1.0)
    return np.clip(field, 0.4, 1.7)


def apply_sector_field(strokes: list[Stroke], field: np.ndarray) -> list[Stroke]:
    """Scale the half-width of every stroke sample by the local multiplier."""
    out = []
    for s in strokes:
        r = np.clip(np.round(s.median[:, 1]).astype(int), 0, field.shape[0] - 1)
        c = np.clip(np.round(s.median[:, 0]).astype(int), 0, field.shape[1] - 1)
        out.append(Stroke(s.median.copy(), s.half_width * field[r, c]))
    return out


def sector_score(strokes: list[Stroke], centre: tuple[float, float],
                 reference: np.ndarray) -> dict:
    """The score of a manipulated drawing, with the honesty constraints.

    ``sym``       the share of the final drawing that is symmetric under the
                  half-turn;
    ``retention`` the share of the original ink that is still there - at
                  most ``RETENTION_MIN`` of it may go;
    ``growth``    how much ink was added - at most ``GROWTH_MAX`` of the
                  original may be added, otherwise the drawing could simply
                  be flooded.

    A manipulation that raises ``sym`` by erasing or by flooding is rejected
    by the constraints, not by the score.
    """
    g = raster(strokes)
    rot = half_turn_grid(g, centre)
    sym = float(np.logical_and(g, rot).sum()) / max(float(g.sum()), 1.0)
    keep = float(np.logical_and(g, reference).sum()) / max(float(reference.sum()), 1.0)
    growth = float(g.sum()) / max(float(reference.sum()), 1.0)
    return {"sym": sym, "retention": keep, "growth": growth,
            "ok": bool(keep >= RETENTION_MIN and growth <= GROWTH_MAX)}


def equalise_opposite_sectors(strokes: list[Stroke], centre: tuple[float, float],
                              masks: np.ndarray | None = None,
                              kernel: np.ndarray | None = None,
                              cap: float = 1.40):
    """R-SECT: thicken the lighter of every pair of opposite sectors.

    The half-turn maps sector ``(i, j)`` onto ``(2 - i, 2 - j)``. If one of
    the two carries less ink than the other, its thickness multiplier is
    raised by the ratio of the two, capped, so that the pair carries the
    same amount of ink. The rule only ever adds ink; the search below can
    also thin.
    """
    if masks is None:
        masks = sector_masks()
    if kernel is None:
        kernel = gaussian_kernel(SECTOR_SIGMA)
    # The comparison uses the full sectors, which tile the box; the eroded
    # masks exist only so that the multiplier field is exact in the
    # interiors. Counting on the eroded masks would drop the ink that lies
    # near a sector border, which for a narrow stroke is all of it.
    full = sector_masks(grid=masks.shape[1], margin=0)
    g = raster(strokes)
    mult = np.ones(9)
    for i in range(3):
        for j in range(3):
            s = i * 3 + j
            r = (2 - i) * 3 + (2 - j)
            if r <= s:
                continue
            a = float((g & full[s]).sum())
            b = float((g & full[r]).sum())
            if a <= 0 or b <= 0:
                continue
            ratio = b / a
            if ratio > 1.0:
                mult[s] = min(cap, ratio)
            else:
                mult[r] = min(cap, 1.0 / ratio)
    field = multiplier_field(mult, masks, kernel)
    return apply_sector_field(strokes, field), mult


def search_sector_multipliers(strokes: list[Stroke], centre: tuple[float, float],
                              reference: np.ndarray, masks: np.ndarray | None = None,
                              kernel: np.ndarray | None = None, rounds: int = 3):
    """Greedy coordinate descent over the nine sector multipliers.

    This is what the sector manipulation can buy at best inside the allowed
    multiplier range and under the constraints. It is not guaranteed to be
    the global optimum: greedy descent can be led astray, and widening the
    range does not always improve the result.
    """
    if masks is None:
        masks = sector_masks()
    if kernel is None:
        kernel = gaussian_kernel(SECTOR_SIGMA)
    mult = np.ones(9)
    best = sector_score(strokes, centre, reference)
    for _ in range(rounds):
        improved = False
        for s in range(9):
            for m in SECTOR_MULTIPLIERS:
                trial = mult.copy()
                trial[s] = m
                field = multiplier_field(trial, masks, kernel)
                cand = apply_sector_field(strokes, field)
                sc = sector_score(cand, centre, reference)
                if sc["ok"] and sc["sym"] > best["sym"] + 1e-9:
                    best, mult, improved = sc, trial, True
        if not improved:
            break
    field = multiplier_field(mult, masks, kernel)
    return apply_sector_field(strokes, field), mult, best


# --------------------------------------------------------------------------
# loading
# --------------------------------------------------------------------------
def parse_path(data: str) -> list[np.ndarray]:
    """Flatten an SVG path into a list of closed polygons."""
    tokens = re.findall(r"[A-Za-z]|-?\d*\.?\d+(?:[eE][-+]?\d+)?", data)
    polys: list[list[np.ndarray]] = []
    cur: list[list[float]] = []
    x = y = 0.0
    i = 0
    cmd = None
    while i < len(tokens):
        tok = tokens[i]
        if tok.isalpha():
            cmd = tok
            i += 1
            if cmd in ("Z", "z"):
                if len(cur) > 2:
                    polys.append(cur)
                cur = []
                continue
        nums = []
        need = {"M": 2, "L": 2, "Q": 4, "C": 6}.get(cmd, 0)
        while len(nums) < need and i < len(tokens) and not tokens[i].isalpha():
            nums.append(float(tokens[i]))
            i += 1
        if cmd in ("M", "L") and len(nums) >= 2:
            x, y = nums[0], nums[1]
            if cmd == "M":
                if len(cur) > 2:
                    polys.append(cur)
                cur = [[x, y]]
            else:
                cur.append([x, y])
        elif cmd == "Q" and len(nums) >= 4:
            x0, y0 = x, y
            cx, cy, x, y = nums
            for t in np.linspace(0.0, 1.0, 9, endpoint=False)[1:]:
                cur.append([(1 - t) ** 2 * x0 + 2 * (1 - t) * t * cx + t ** 2 * x,
                            (1 - t) ** 2 * y0 + 2 * (1 - t) * t * cy + t ** 2 * y])
            cur.append([x, y])
        elif cmd == "C" and len(nums) >= 6:
            x0, y0 = x, y
            c1x, c1y, c2x, c2y, x, y = nums
            for t in np.linspace(0.0, 1.0, 11, endpoint=False)[1:]:
                cur.append([(1 - t) ** 3 * x0 + 3 * (1 - t) ** 2 * t * c1x +
                            3 * (1 - t) * t ** 2 * c2x + t ** 3 * x,
                            (1 - t) ** 3 * y0 + 3 * (1 - t) ** 2 * t * c1y +
                            3 * (1 - t) * t ** 2 * c2y + t ** 3 * y])
            cur.append([x, y])
        else:
            i += 1
    if len(cur) > 2:
        polys.append(cur)
    return [np.asarray(p, dtype=np.float64) for p in polys]


def load_glyph(character: str, graphics: dict, centre: tuple[float, float],
               side: float) -> list[Stroke]:
    """Strokes of one glyph, in box coordinates, with a half-width profile.

    ``centre`` and ``side`` describe the em square in source coordinates
    (the 1024 x 1024 space of the MMah file).
    """
    entry = graphics[character]
    scale = EM / side
    out = []
    for k, med in enumerate(entry["medians"]):
        pts = (np.asarray(med, dtype=np.float64) - np.array(centre)) * scale + EM / 2
        spine = resample(pts)
        if len(spine) < 2:
            continue
        outline = []
        if k < len(entry.get("strokes", [])):
            for poly in parse_path(entry["strokes"][k]):
                outline.append((poly - np.array(centre)) * scale + EM / 2)
        if outline:
            outline = np.vstack(outline)
            hw = np.empty(len(spine))
            for i in range(0, len(spine), 256):
                chunk = spine[i:i + 256]
                d = np.sqrt(((chunk[:, None, :] - outline[None, :, :]) ** 2).sum(-1))
                hw[i:i + 256] = d.min(axis=1)
        else:
            hw = np.full(len(spine), 1.5)
        out.append(Stroke(spine, hw))
    return out


def load_graphics(path: Path) -> dict:
    out = {}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            d = json.loads(line)
            out[d["character"]] = d
    return out


# --------------------------------------------------------------------------
# command line
# --------------------------------------------------------------------------
def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Reconcile the extremities of PRC forms for half-turn reading.")
    parser.add_argument("--graphics", type=Path, required=True,
                        help="MMah graphics.txt (one JSON object per line)")
    parser.add_argument("--characters", type=str, default="",
                        help="comma separated list of characters to process")
    parser.add_argument("--em", type=str, default="512,384,984",
                        help="em square as cx,cy,side in source coordinates")
    parser.add_argument("--out", type=Path, default=None,
                        help="write the report as JSON to this path")
    args = parser.parse_args(argv)

    cx, cy, side = (float(v) for v in args.em.split(","))
    graphics = load_graphics(args.graphics)
    chars = [c for c in args.characters.split(",") if c] or sorted(graphics)[:8]

    report = []
    for ch in chars:
        if ch not in graphics:
            continue
        strokes = load_glyph(ch, graphics, (cx, cy), side)
        if not strokes:
            continue
        base = (EM / 2, EM / 2)
        g = raster(strokes)
        row = {"character": ch, "n_strokes": len(strokes),
               "box_overlap": ink_overlap(half_turn_grid(g, base), g),
               "centroid": list(ink_centroid(strokes))}
        row.update(legibility(strokes, row["centroid"]))
        centre, best = find_centre(strokes)
        row["best_centre"] = list(centre)
        row["centre_overlap"] = best
        work = [Stroke(s.median.copy(), s.half_width.copy()) for s in strokes]
        row["reconciled"] = reconcile(work, centre)
        g2 = raster(work)
        row["reconciled_overlap"] = ink_overlap(half_turn_grid(g2, centre), g2)
        row["reconciled_legibility"] = legibility(work, centre)
        report.append(row)
        print(f"{ch}\tbox {row['box_overlap']:.3f}\tcentre {row['centre_overlap']:.3f}"
              f"\treconciled {row['reconciled_overlap']:.3f}"
              f"\tpairs {row['reconciled']['pairs']}")

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(report, ensure_ascii=False, indent=1),
                            encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())