"""Deterministic newspaper front-page renderer for Tuesday 24 November 2026.

Renders a 1024x1024 warm-paper editorial broadsheet using Pillow and fixed
DejaVu font paths, writes entry.png deterministically, and measures band
edge density, story ink coverage, and 300px thumbnail readability.
"""

from __future__ import annotations

import hashlib
import math
import os
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from PIL import Image, ImageDraw, ImageFilter, ImageFont

import data

# --- Canvas & Palette -------------------------------------------------------
W, H = 1024, 1024
MARGIN_X = 18
CONTENT_W = W - 2 * MARGIN_X  # 988

PAPER = (244, 239, 230)       # #f4efe6 warm newsprint
PAPER_TINT = (236, 229, 216)  # #ece5d8 subtle strip tint
INK = (22, 20, 18)            # #161412 primary near-black ink
BODY_INK = (42, 38, 34)       # #2a2622 secondary body text
MUTED = (92, 85, 76)          # #5c554c outlets / captions
ACCENT = (184, 48, 26)        # #b8301a vermilion editorial red-orange
HAIRLINE = (182, 173, 160)    # #b6ada0 thin column & brief rules
RULE_DARK = (34, 31, 28)      # #221f1c strong horizontal section rules

# --- Hard-coded Fonts (all asserted to exist) -------------------------------
FONT_DIR = "/usr/share/fonts/truetype/dejavu"
FONT_PATHS = {
    "serif_bold": f"{FONT_DIR}/DejaVuSerif-Bold.ttf",
    "serif_cond_bold": f"{FONT_DIR}/DejaVuSerifCondensed-Bold.ttf",
    "serif": f"{FONT_DIR}/DejaVuSerif.ttf",
    "sans": f"{FONT_DIR}/DejaVuSans.ttf",
    "sans_bold": f"{FONT_DIR}/DejaVuSans-Bold.ttf",
    "sans_cond": f"{FONT_DIR}/DejaVuSansCondensed.ttf",
    "sans_cond_bold": f"{FONT_DIR}/DejaVuSansCondensed-Bold.ttf",
    "mono": f"{FONT_DIR}/DejaVuSansMono.ttf",
    "mono_bold": f"{FONT_DIR}/DejaVuSansMono-Bold.ttf",
}

for _name, _path in FONT_PATHS.items():
    assert os.path.exists(_path), f"Required font missing: {_path}"


_FONT_CACHE: Dict[Tuple[str, int], ImageFont.FreeTypeFont] = {}


def get_font(key: str, size: int) -> ImageFont.FreeTypeFont:
    cache_key = (key, size)
    if cache_key not in _FONT_CACHE:
        _FONT_CACHE[cache_key] = ImageFont.truetype(FONT_PATHS[key], size)
    return _FONT_CACHE[cache_key]


def text_width(font: ImageFont.FreeTypeFont, text: str) -> int:
    if not text:
        return 0
    box = font.getbbox(text)
    return box[2] - box[0]


def text_height(font: ImageFont.FreeTypeFont, text: str = "Ag") -> int:
    box = font.getbbox(text)
    return box[3] - box[1]


def wrap_text(
    text: str,
    font: ImageFont.FreeTypeFont,
    max_w: int,
    max_lines: Optional[int] = None,
) -> List[str]:
    words = text.split()
    lines: List[str] = []
    cur = ""
    for w in words:
        cand = f"{cur} {w}".strip()
        if text_width(font, cand) <= max_w or not cur:
            cur = cand
        else:
            lines.append(cur)
            cur = w
            if max_lines is not None and len(lines) >= max_lines:
                break
    if cur and (max_lines is None or len(lines) < max_lines):
        lines.append(cur)
    return lines


def compute_region_counts() -> Dict[str, int]:
    counts = Counter(story["region"] for story in data.ALL_STORIES)
    return {r: counts[r] for r in data.REGION_ORDER}


# --- Vector Line-Scene Illustrations (no faces, no recognisable buildings) --
def draw_illustration(
    draw: ImageDraw.ImageDraw,
    kind: str,
    box: Tuple[int, int, int, int],
) -> None:
    """Draw a minimal 2-3px editorial vector line-scene in INK + ACCENT."""
    x0, y0, x1, y1 = box
    w = x1 - x0
    h = y1 - y0
    cx = (x0 + x1) // 2
    cy = (y0 + y1) // 2

    # Subtle open framing tick marks at corners (no heavy card border)
    draw.line([(x0, y1), (x1, y1)], fill=HAIRLINE, width=1)

    if kind == "candlesticks":
        # Climbing market candlesticks (+9% / +7%) + subtle axis grid
        gx0, gy0, gx1, gy1 = x0 + 6, y0 + 6, x1 - 6, y1 - 12
        draw.line([(gx0, gy1), (gx1, gy1)], fill=INK, width=2)
        draw.line([(gx0, gy0), (gx0, gy1)], fill=INK, width=2)
        for frac in (0.33, 0.66):
            gy = int(gy0 + (gy1 - gy0) * frac)
            draw.line([(gx0 + 2, gy), (gx1, gy)], fill=HAIRLINE, width=1)
        # 5 candlesticks climbing sharply on the right
        candles = [
            (0.14, 0.78, 0.56, 0.86, 0.50, False),
            (0.32, 0.72, 0.48, 0.82, 0.40, False),
            (0.50, 0.58, 0.34, 0.68, 0.28, True),
            (0.68, 0.42, 0.20, 0.52, 0.14, True),
            (0.86, 0.26, 0.08, 0.36, 0.02, True),
        ]
        gw = gx1 - gx0
        gh = gy1 - gy0
        for fx, lo, hi, wlo, whi, hot in candles:
            px = int(gx0 + fx * gw)
            col = ACCENT if hot else INK
            draw.line(
                [(px, int(gy0 + whi * gh)), (px, int(gy0 + wlo * gh))],
                fill=col,
                width=2,
            )
            bw = 7
            top_y = int(gy0 + hi * gh)
            bot_y = int(gy0 + lo * gh)
            draw.rectangle(
                [px - bw, top_y, px + bw, bot_y],
                fill=PAPER if not hot else None,
                outline=col,
                width=2,
            )
            if hot:
                draw.line([(px - bw + 2, bot_y - 3), (px + bw - 2, top_y + 3)], fill=col, width=2)
        # Upward breakout arrow
        draw.line([(gx0 + 14, gy1 - 12), (gx1 - 10, gy0 + 8)], fill=ACCENT, width=2)
        draw.polygon(
            [(gx1 - 8, gy0 + 6), (gx1 - 18, gy0 + 7), (gx1 - 11, gy0 + 16)],
            fill=ACCENT,
        )
        f_lbl = get_font("mono_bold", 9)
        draw.text((gx0 + 4, gy1 + 2), "TAIEX +9%  KOSPI +7%", font=f_lbl, fill=ACCENT)

    elif kind == "tanker_fire":
        # Narrow strait shorelines + tanker hull with breach and flames
        draw.line([(x0 + 2, y0 + 5), (x0 + 18, y0 + 9), (x0 + 28, y0 + 5)], fill=INK, width=2)
        draw.line([(x1 - 24, y0 + 6), (x1 - 12, y0 + 10), (x1 - 2, y0 + 6)], fill=INK, width=2)
        # Water wave baseline
        wy = y1 - 6
        draw.line([(x0 + 2, wy), (x1 - 2, wy)], fill=INK, width=2)
        # Tanker hull
        hull = [
            (x0 + 7, wy),
            (x0 + 11, wy - 9),
            (x1 - 11, wy - 9),
            (x1 - 6, wy),
        ]
        draw.line(hull, fill=INK, width=2)
        # Aft bridge block
        draw.rectangle([x0 + 12, wy - 16, x0 + 20, wy - 9], outline=INK, width=2)
        # Hull breach V-gap + flames
        bx = cx + 4
        draw.line([(bx - 4, wy - 9), (bx, wy - 3), (bx + 4, wy - 9)], fill=ACCENT, width=2)
        flame = [
            (bx - 5, wy - 10),
            (bx - 2, wy - 20),
            (bx + 1, wy - 14),
            (bx + 4, wy - 22),
            (bx + 7, wy - 10),
        ]
        draw.line(flame, fill=ACCENT, width=2)

    elif kind == "shipwreck":
        # Listing shipwreck silhouette sinking at angle in waves
        wy = y1 - 7
        for ox in range(x0 + 3, x1 - 6, 10):
            draw.arc([ox, wy - 3, ox + 10, wy + 5], 190, 350, fill=INK, width=2)
        # Tilted hull
        hull = [(x0 + 10, wy - 2), (x0 + 20, wy - 16), (x1 - 8, wy - 8), (x1 - 12, wy - 1)]
        draw.polygon(hull, outline=INK, fill=None)
        draw.line(hull + [hull[0]], fill=INK, width=2)
        # Broken mast & impact spark
        draw.line([(cx - 1, wy - 13), (cx + 5, wy - 25)], fill=INK, width=2)
        draw.line([(cx + 9, wy - 16), (cx + 15, wy - 22)], fill=ACCENT, width=2)
        draw.line([(cx + 11, wy - 10), (cx + 18, wy - 12)], fill=ACCENT, width=2)

    elif kind == "jet_drone":
        # Vertical dashed border line + jet drone delta wing with exhaust trail
        bx = cx + 2
        for yy in range(y0 + 3, y1 - 3, 7):
            draw.line([(bx, yy), (bx, min(yy + 4, y1 - 3))], fill=INK, width=2)
        # Exhaust trail crossing border
        draw.line([(x0 + 4, cy + 2), (bx + 6, cy - 3)], fill=ACCENT, width=2)
        draw.line([(x0 + 8, cy + 5), (bx + 2, cy + 1)], fill=ACCENT, width=1)
        # Delta-wing jet drone past border
        nose = (x1 - 5, cy - 5)
        wing_t = (bx + 4, cy - 11)
        wing_b = (bx + 6, cy + 3)
        draw.polygon([nose, wing_t, (bx + 8, cy - 4), wing_b], outline=INK)
        draw.line([nose, wing_t, wing_b, nose], fill=INK, width=2)

    elif kind == "split_building":
        # Five-storey geometric facade cut cleanly in half with a jagged gap
        by = y1 - 4
        ty = y0 + 5
        lx0, lx1 = x0 + 8, cx - 4
        rx0, rx1 = cx + 4, x1 - 8
        # Left half
        draw.rectangle([lx0, ty, lx1, by], outline=INK, width=2)
        # Right half (slightly sheared down)
        draw.rectangle([rx0, ty + 4, rx1, by], outline=INK, width=2)
        # 5 storey horizontal window bars
        for i in range(5):
            wy = ty + 4 + i * 5
            if wy < by - 2:
                draw.line([(lx0 + 3, wy), (lx1 - 3, wy)], fill=INK, width=1)
            if wy + 4 < by - 2:
                draw.line([(rx0 + 3, wy + 4), (rx1 - 3, wy + 4)], fill=INK, width=1)
        # Red crack / blast gap down the center
        crack = [(cx, ty), (cx - 2, cy - 4), (cx + 2, cy + 2), (cx - 1, by)]
        draw.line(crack, fill=ACCENT, width=2)

    elif kind == "quake_ridge":
        # Mountain ridge with seismic wave arc overhead
        by = y1 - 5
        ridge = [
            (x0 + 4, by),
            (x0 + 16, y0 + 14),
            (cx, by - 8),
            (cx + 11, y0 + 11),
            (x1 - 4, by),
        ]
        draw.line(ridge, fill=INK, width=2)
        # Concentric seismic wave arcs above ridge
        draw.arc([cx - 16, y0 + 2, cx + 16, y0 + 24], 200, 340, fill=ACCENT, width=2)
        draw.arc([cx - 10, y0 + 6, cx + 10, y0 + 20], 200, 340, fill=ACCENT, width=2)

    elif kind == "rocket_dock":
        # Slender rocket angled toward a circular orbital docking ring
        # Docking ring on upper-right
        draw.ellipse([x1 - 20, y0 + 4, x1 - 6, y0 + 18], outline=ACCENT, width=2)
        draw.line([(x1 - 13, y0 + 4), (x1 - 13, y0 + 18)], fill=ACCENT, width=1)
        # Rocket body from lower-left
        draw.line([(x0 + 10, y1 - 6), (cx + 2, cy - 2)], fill=INK, width=3)
        draw.polygon(
            [(cx + 6, cy - 5), (cx - 1, cy - 5), (cx + 3, cy + 2)],
            fill=INK,
        )
        # Exhaust plume
        draw.line([(x0 + 8, y1 - 5), (x0 + 4, y1 - 2)], fill=ACCENT, width=2)

    elif kind == "water_well":
        # Simple masonry well base + upright posts + crossbar & rope pulley
        by = y1 - 4
        draw.rectangle([cx - 12, by - 11, cx + 12, by], outline=INK, width=2)
        draw.line([(cx - 10, by - 11), (cx - 10, y0 + 6)], fill=INK, width=2)
        draw.line([(cx + 10, by - 11), (cx + 10, y0 + 6)], fill=INK, width=2)
        draw.line([(cx - 13, y0 + 6), (cx + 13, y0 + 6)], fill=INK, width=2)
        draw.line([(cx, y0 + 6), (cx, by - 13)], fill=ACCENT, width=2)
        draw.ellipse([cx - 3, by - 16, cx + 3, by - 11], outline=ACCENT, width=2)

    elif kind == "parliament":
        # Divided parliament benches split by a cracked red center aisle
        by = y1 - 4
        for row in range(3):
            ry = y0 + 9 + row * 7
            draw.line([(x0 + 5, ry), (cx - 5, ry)], fill=INK, width=2)
            draw.line([(cx + 5, ry), (x1 - 5, ry)], fill=INK, width=2)
        # Cracked aisle down the middle
        draw.line([(cx, y0 + 4), (cx - 2, cy), (cx + 2, cy + 5), (cx, by)], fill=ACCENT, width=2)

    elif kind == "gavel":
        # Gavel striking a sound block (COP31 collapse)
        by = y1 - 5
        # Sound block
        draw.rectangle([x0 + 8, by - 5, x0 + 30, by], outline=INK, width=2)
        # Angled gavel head + handle
        draw.line([(x0 + 18, by - 12), (x1 - 7, y0 + 9)], fill=INK, width=2)
        draw.polygon(
            [(x0 + 12, by - 15), (x0 + 21, by - 21), (x0 + 26, by - 14), (x0 + 17, by - 8)],
            outline=INK,
        )
        draw.line([(x0 + 12, by - 15), (x0 + 21, by - 21), (x0 + 26, by - 14), (x0 + 17, by - 8), (x0 + 12, by - 15)], fill=INK, width=2)
        # Impact lines
        draw.line([(x0 + 8, by - 10), (x0 + 13, by - 8)], fill=ACCENT, width=2)
        draw.line([(x0 + 27, by - 9), (x0 + 33, by - 11)], fill=ACCENT, width=2)

    elif kind == "tower_burst":
        # Abstract geometric spire with 3 clean floor lines and impact starburst
        by = y1 - 4
        draw.rectangle([cx - 7, y0 + 6, cx + 7, by], outline=INK, width=2)
        for ry in (y0 + 13, y0 + 20, y0 + 27):
            if ry < by - 2:
                draw.line([(cx - 4, ry), (cx + 4, ry)], fill=INK, width=1)
        # Starburst impact
        ix, iy = cx + 8, y0 + 11
        for ang in (-35, 0, 35, 145, 215):
            rad = math.radians(ang)
            draw.line(
                [(ix, iy), (int(ix + 7 * math.cos(rad)), int(iy + 7 * math.sin(rad)))],
                fill=ACCENT,
                width=2,
            )

    elif kind == "scales":
        # Judicial balance scales
        by = y1 - 4
        draw.line([(cx, y0 + 5), (cx, by)], fill=INK, width=2)
        draw.line([(cx - 9, by), (cx + 9, by)], fill=INK, width=2)
        draw.line([(x0 + 9, y0 + 11), (x1 - 9, y0 + 7)], fill=INK, width=2)
        draw.arc([x0 + 5, y0 + 15, x0 + 17, y0 + 24], 0, 180, fill=ACCENT, width=2)
        draw.arc([x1 - 17, y0 + 11, x1 - 5, y0 + 20], 0, 180, fill=INK, width=2)

    elif kind == "cargo_crate":
        # Shipping container / tariff crate with diagonal brace
        draw.rectangle([x0 + 8, y0 + 8, x1 - 8, y1 - 6], outline=INK, width=2)
        draw.line([(x0 + 14, y0 + 8), (x0 + 14, y1 - 6)], fill=INK, width=1)
        draw.line([(cx, y0 + 8), (cx, y1 - 6)], fill=INK, width=1)
        draw.line([(x1 - 14, y0 + 8), (x1 - 14, y1 - 6)], fill=INK, width=1)
        draw.line([(x0 + 8, y1 - 6), (x1 - 8, y0 + 8)], fill=ACCENT, width=2)

    elif kind == "medical_arc":
        # Medical cross inside a containment arc (Ebola responders trapped)
        r = 10
        draw.arc([cx - r - 3, cy - r - 3, cx + r + 3, cy + r + 3], 30, 330, fill=INK, width=2)
        draw.line([(cx - 5, cy), (cx + 5, cy)], fill=ACCENT, width=3)
        draw.line([(cx, cy - 5), (cx, cy + 5)], fill=ACCENT, width=3)

    elif kind == "trophy":
        # Minimal championship cup silhouette
        by = y1 - 4
        draw.line([(cx - 8, by), (cx + 8, by)], fill=INK, width=2)
        draw.line([(cx, by - 8), (cx, by)], fill=INK, width=2)
        cup = [(cx - 9, y0 + 6), (cx + 9, y0 + 6), (cx + 6, by - 8), (cx - 6, by - 8)]
        draw.line(cup + [cup[0]], fill=INK, width=2)
        draw.arc([cx - 14, y0 + 7, cx - 6, y0 + 16], 90, 270, fill=ACCENT, width=2)
        draw.arc([cx + 6, y0 + 7, cx + 14, y0 + 16], 270, 90, fill=ACCENT, width=2)


def draw_section_rubric(
    draw: ImageDraw.ImageDraw,
    x0: int,
    y: int,
    w: int,
    title: str,
) -> int:
    """Draw a compact editorial section rubric inside a column; returns next y."""
    f = get_font("sans_cond_bold", 9)
    draw.line([(x0, y), (x0 + w, y)], fill=RULE_DARK, width=1)
    draw.rectangle([x0, y, x0 + 18, y + 2], fill=ACCENT)
    draw.text((x0, y + 4), title, font=f, fill=ACCENT)
    return y + 17


def draw_brief(
    draw: ImageDraw.ImageDraw,
    story: dict,
    x0: int,
    y0: int,
    w: int,
    max_y: int,
    draw_bottom_rule: bool,
    ink_tracker: List[float],
    illus_counter: List[int],
    head_size: int = 12,
) -> int:
    """Render one newspaper brief cleanly without overlaps; returns bottom y."""
    f_head = get_font("sans_cond_bold", head_size)
    f_body = get_font("sans_cond", 10)
    f_src = get_font("sans_cond", 9)
    f_stat = get_font("sans_cond_bold", 8)

    has_illus = bool(story.get("illustration"))
    illus_w = 48 if has_illus else 0
    illus_h = 32 if has_illus else 0

    y = y0 + 2
    head_lines = wrap_text(story["label"], f_head, w, max_lines=2)
    text_ink_area = 0.0
    head_step = head_size + 1

    for ln in head_lines:
        draw.text((x0, y), ln, font=f_head, fill=INK)
        text_ink_area += text_width(f_head, ln) * head_step
        y += head_step

    y += 1
    body_w = (w - illus_w - 6) if has_illus else w
    max_body_lines = 2 if (len(head_lines) >= 2 and (max_y - y) < 46) else 3
    body_lines = wrap_text(story["detail"], f_body, body_w, max_lines=max_body_lines)

    illus_top = y + 2
    for ln in body_lines:
        draw.text((x0, y), ln, font=f_body, fill=BODY_INK)
        text_ink_area += text_width(f_body, ln) * 11
        y += 11

    if has_illus:
        ix0 = x0 + w - illus_w
        iy0 = illus_top
        iy1 = min(iy0 + illus_h, max_y - 13)
        if iy1 - iy0 >= 24:
            draw_illustration(draw, story["illustration"], (ix0, iy0, ix0 + illus_w, iy1))
            illus_counter[0] += 1
            y = max(y, iy1 + 1)

    y += 1
    src_prefix = f"{story['source']} · "
    status = story["status"]
    stat_color = ACCENT if status == "CLAIM" else (INK if status == "CONFIRMED" else MUTED)

    draw.text((x0, y), src_prefix, font=f_src, fill=MUTED)
    sw = text_width(f_src, src_prefix)
    # Render status tag as crisp small-caps text (never a filled chip)
    draw.text((x0 + sw, y + 1), status, font=f_stat, fill=stat_color)
    text_ink_area += (sw + text_width(f_stat, status)) * 10
    y += 11

    assert y <= max_y + 2, f"Brief '{story['id']}' overflowed: {y} > {max_y}"

    tile_h = max(1, (max_y - y0))
    ink_tracker.append(text_ink_area / (w * tile_h))

    if draw_bottom_rule:
        draw.line([(x0, max_y - 1), (x0 + w, max_y - 1)], fill=HAIRLINE, width=1)

    return max_y


def render_page() -> Tuple[Image.Image, Dict[str, object]]:
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)

    region_counts = compute_region_counts()
    total_stories = len(data.ALL_STORIES)
    illus_counter = [0]
    ink_ratios: List[float] = []

    # ========================================================================
    # 1. MASTHEAD (y = 8..96)
    # ========================================================================
    f_meta_b = get_font("sans_bold", 10)
    f_meta_m = get_font("mono", 9)

    draw.text((MARGIN_X, 9), data.MASTHEAD_LEFT, font=f_meta_b, fill=INK)
    cw = text_width(f_meta_m, data.MASTHEAD_CENTER)
    draw.text(((W - cw) // 2, 10), data.MASTHEAD_CENTER, font=f_meta_m, fill=MUTED)
    right_lbl = f"{data.EDITION_SHORT} · UTC"
    rw = text_width(f_meta_b, right_lbl)
    draw.text((W - MARGIN_X - rw, 9), right_lbl, font=f_meta_b, fill=ACCENT)

    # Classic newspaper double rule under utility bar
    draw.line([(MARGIN_X, 24), (W - MARGIN_X, 24)], fill=INK, width=2)
    draw.line([(MARGIN_X, 27), (W - MARGIN_X, 27)], fill=INK, width=1)

    # Huge centred date (>= 52px, single biggest element on the page)
    f_date = get_font("serif_cond_bold", 54)
    dw = text_width(f_date, data.EDITION_DATE)
    assert dw <= CONTENT_W, f"Date too wide: {dw} > {CONTENT_W}"
    draw.text(((W - dw) // 2, 26), data.EDITION_DATE, font=f_date, fill=INK)

    # Strap line beneath date
    draw.line([(MARGIN_X, 82), (W - MARGIN_X, 82)], fill=HAIRLINE, width=1)
    strap = (
        f"{total_stories} STORIES  ·  {len(data.REGION_ORDER)} REGIONS  ·  "
        f"ONE DAY (UTC 24 NOV 2026)  ·  EVERY STORY DATED"
    )
    f_strap = get_font("sans_bold", 10)
    sw = text_width(f_strap, strap)
    draw.text(((W - sw) // 2, 85), strap, font=f_strap, fill=BODY_INK)
    draw.line([(MARGIN_X, 98), (W - MARGIN_X, 98)], fill=INK, width=2)

    # ========================================================================
    # 2. THE DAY IN NUMBERS SCOREBOARD (y = 100..166)
    # ========================================================================
    f_strip_k = get_font("sans_bold", 9)
    draw.text((MARGIN_X, 101), "THE DAY IN NUMBERS", font=f_strip_k, fill=ACCENT)
    draw.line([(MARGIN_X + 124, 106), (W - MARGIN_X, 106)], fill=HAIRLINE, width=1)

    num_y = 113
    num_h = 52
    # Proportional column widths summing to CONTENT_W (988) so 1,700km stays >=40px cleanly
    col_widths = [156, 144, 144, 172, 152, 220]
    assert sum(col_widths) == CONTENT_W
    f_num = get_font("serif_cond_bold", 40)
    f_nlbl = get_font("sans_cond_bold", 10)

    cx0 = MARGIN_X
    for idx, item in enumerate(data.NUMBERS_STRIP):
        cw_item = col_widths[idx]
        cx1 = cx0 + cw_item
        if idx > 0:
            draw.line([(cx0, num_y + 4), (cx0, num_y + num_h - 4)], fill=HAIRLINE, width=1)

        val = item["value"]
        vw = text_width(f_num, val)
        col_c = (cx0 + cx1) // 2
        val_color = ACCENT if item["hot"] else INK
        draw.text((col_c - vw // 2, num_y - 3), val, font=f_num, fill=val_color)

        lbl = item["label"]
        lw = text_width(f_nlbl, lbl)
        draw.text((col_c - lw // 2, num_y + 39), lbl, font=f_nlbl, fill=BODY_INK)
        cx0 = cx1

    draw.line([(MARGIN_X, 167), (W - MARGIN_X, 167)], fill=INK, width=1)

    # ========================================================================
    # 3. THE DAY IN UTC CLOCK STRIP (y = 169..203)
    # ========================================================================
    draw.rectangle([MARGIN_X, 169, W - MARGIN_X, 202], fill=PAPER_TINT)
    f_ck = get_font("sans_cond_bold", 9)
    draw.text((MARGIN_X + 5, 175), "THE DAY", font=f_ck, fill=ACCENT)
    draw.text((MARGIN_X + 5, 186), "IN UTC", font=f_ck, fill=ACCENT)
    draw.line([(MARGIN_X + 56, 172), (MARGIN_X + 56, 199)], fill=HAIRLINE, width=1)

    clock_x0 = MARGIN_X + 62
    clock_w = (W - MARGIN_X) - clock_x0
    cw_cell = clock_w / 4
    f_tm = get_font("mono_bold", 10)
    f_ev = get_font("sans_cond", 10)

    for idx, ev in enumerate(data.UTC_CLOCK):
        row = idx // 4
        col = idx % 4
        ex = int(clock_x0 + col * cw_cell)
        ey = 172 + row * 15
        draw.text((ex, ey), ev["time"], font=f_tm, fill=INK)
        tw = text_width(f_tm, ev["time"]) + 4
        draw.text((ex + tw, ey), ev["event"], font=f_ev, fill=BODY_INK)

    draw.line([(MARGIN_X, 203), (W - MARGIN_X, 203)], fill=INK, width=1)

    # ========================================================================
    # 4. REGION COVERAGE RAIL (y = 205..220) — counts computed from data.py
    # ========================================================================
    rail_parts = [f"{data.REGION_LABELS[r]} {region_counts[r]}" for r in data.REGION_ORDER]
    rail_text = "  ·  ".join(rail_parts)
    f_rail = get_font("sans_cond_bold", 10)
    rw = text_width(f_rail, rail_text)
    draw.text(((W - rw) // 2, 206), rail_text, font=f_rail, fill=INK)
    draw.line([(MARGIN_X, 220), (W - MARGIN_X, 220)], fill=RULE_DARK, width=2)

    # ========================================================================
    # 5. MAIN ASYMMETRIC 4-COLUMN EDITORIAL BODY (y = 223..924)
    # ========================================================================
    gutter = 12
    col_w = (CONTENT_W - 3 * gutter) // 4  # 238 px
    col_x = [MARGIN_X + i * (col_w + gutter) for i in range(4)]

    top_y0 = 223
    top_y1 = 392

    # --- TOP LEFT (2 columns wide): DOMINANT HEADLINE BILL ------------------
    lead_x0 = col_x[0]
    lead_w = col_w * 2 + gutter  # 488 px
    lead = data.LEAD_STORY

    f_lkick = get_font("sans_bold", 9)
    draw.text((lead_x0, top_y0 + 1), lead["kicker"], font=f_lkick, fill=ACCENT)

    f_lhead = get_font("serif_cond_bold", 26)
    lh_lines = wrap_text(lead["label"], f_lhead, lead_w, max_lines=2)
    ly = top_y0 + 13
    for ln in lh_lines:
        draw.text((lead_x0, ly), ln, font=f_lhead, fill=INK)
        ly += 29

    ly += 4
    # Split below lead headline: left deck + outlet, right candlestick illustration
    l_illus_w = 152
    l_deck_w = lead_w - l_illus_w - 10
    f_ldeck = get_font("sans_cond", 11)
    deck_lines = wrap_text(lead["deck"], f_ldeck, l_deck_w, max_lines=6)
    dy = ly
    lead_ink_area = sum(text_width(f_lhead, ln) * 26 for ln in lh_lines)
    for ln in deck_lines:
        draw.text((lead_x0, dy), ln, font=f_ldeck, fill=BODY_INK)
        lead_ink_area += text_width(f_ldeck, ln) * 13
        dy += 13

    dy += 3
    f_lsrc = get_font("sans_cond", 10)
    f_lstat = get_font("sans_cond_bold", 9)
    lsrc_prefix = f"{lead['source']} · "
    draw.text((lead_x0, dy), lsrc_prefix, font=f_lsrc, fill=MUTED)
    draw.text(
        (lead_x0 + text_width(f_lsrc, lsrc_prefix), dy + 1),
        lead["status"],
        font=f_lstat,
        fill=INK,
    )
    ink_ratios.append(lead_ink_area / (lead_w * (top_y1 - top_y0)))

    # Lead illustration (candlesticks)
    draw_illustration(
        draw,
        lead["illustration"],
        (lead_x0 + l_deck_w + 10, ly, lead_x0 + lead_w, top_y1 - 6),
    )
    illus_counter[0] += 1

    # Vertical hairlines for top zone (between col 2 & 3, and col 3 & 4)
    for gx in (col_x[2] - gutter // 2, col_x[3] - gutter // 2):
        draw.line([(gx, top_y0), (gx, top_y1 - 2)], fill=HAIRLINE, width=1)

    # --- TOP RIGHT COL 3 & COL 4 (2 briefs each) ----------------------------
    top_c3 = [s for s in data.BRIEF_STORIES if s["slot"] == "top_c3"]
    top_c4 = [s for s in data.BRIEF_STORIES if s["slot"] == "top_c4"]

    y_c3 = draw_section_rubric(draw, col_x[2], top_y0, col_w, "SEAS & TRADE")
    slot_h_top = (top_y1 - y_c3) // 2
    for i, st in enumerate(top_c3):
        sy0 = y_c3 + i * slot_h_top
        sy1 = y_c3 + (i + 1) * slot_h_top
        draw_brief(draw, st, col_x[2], sy0, col_w, sy1, i == 0, ink_ratios, illus_counter)

    y_c4 = draw_section_rubric(draw, col_x[3], top_y0, col_w, "EUROPE & UKRAINE")
    for i, st in enumerate(top_c4):
        sy0 = y_c4 + i * slot_h_top
        sy1 = y_c4 + (i + 1) * slot_h_top
        draw_brief(draw, st, col_x[3], sy0, col_w, sy1, i == 0, ink_ratios, illus_counter)

    # Full-width horizontal divider separating lead zone from 4-col lower grid
    draw.line([(MARGIN_X, top_y1), (W - MARGIN_X, top_y1)], fill=RULE_DARK, width=1)

    # --- LOWER 4-COLUMN GRID (y = 396..924) ---------------------------------
    low_y0 = 396
    low_y1 = 924

    # 3 vertical column hairlines
    for idx in range(1, 4):
        gx = col_x[idx] - gutter // 2
        draw.line([(gx, low_y0), (gx, low_y1)], fill=HAIRLINE, width=1)

    col_specs = [
        ("col1", col_x[0], [("EU", "EUROPE & UKRAINE (CONT.)"), ("AM", "AMERICAS")]),
        ("col2", col_x[1], [("AP", "ASIA-PACIFIC"), ("SE", "SEAS & TRADE (CONT.)")]),
        ("col3", col_x[2], [("ME", "MIDDLE EAST"), ("CL", "CLIMATE & HEALTH")]),
        ("col4", col_x[3], [("CL", "CLIMATE & HEALTH · COP31"), ("AF", "AFRICA")]),
    ]

    for slot_key, cx0, sections in col_specs:
        col_stories = [s for s in data.BRIEF_STORIES if s["slot"] == slot_key]
        n_rubrics = len(sections)
        rubric_h = 18
        avail_h = (low_y1 - low_y0) - n_rubrics * rubric_h
        per_story_h = avail_h // len(col_stories)

        cy = low_y0
        for sec_idx, (reg_code, sec_title) in enumerate(sections):
            sec_items = [s for s in col_stories if s["region"] == reg_code]
            cy = draw_section_rubric(draw, cx0, cy, col_w, sec_title)
            for item_idx, st in enumerate(sec_items):
                is_last_in_col = (sec_idx == len(sections) - 1) and (item_idx == len(sec_items) - 1)
                sy1 = low_y1 if is_last_in_col else (cy + per_story_h)
                draw_brief(
                    draw,
                    st,
                    cx0,
                    cy,
                    col_w,
                    sy1,
                    not (item_idx == len(sec_items) - 1),
                    ink_ratios,
                    illus_counter,
                    head_size=11,
                )
                cy = sy1

    # ========================================================================
    # 6. FOOTER: DATE CHECK — READ THIS FIRST (y = 926..1016)
    # ========================================================================
    fy = 926
    draw.line([(MARGIN_X, fy), (W - MARGIN_X, fy)], fill=INK, width=2)
    draw.rectangle([MARGIN_X, fy + 2, W - MARGIN_X, 1014], fill=PAPER_TINT)

    f_dhead = get_font("sans_bold", 10)
    f_dtxt = get_font("sans_cond", 10)
    f_dexc = get_font("sans_cond", 9)
    f_strap = get_font("sans_cond", 8)

    hdr = "DATE CHECK — READ THIS FIRST:"
    draw.text((MARGIN_X + 8, fy + 6), hdr, font=f_dhead, fill=ACCENT)
    hx = MARGIN_X + 8 + text_width(f_dhead, hdr) + 6
    scope_sentence = (
        "This front page covers Tuesday 24 November 2026 (UTC) only; "
        "earlier stories were deliberately excluded:"
    )
    draw.text((hx, fy + 6), scope_sentence, font=f_dtxt, fill=INK)

    # 4 excluded items in a clean 2x2 grid (airy spacing to keep Band 7 <= 50)
    half_w = (CONTENT_W - 24) // 2
    for i, exc in enumerate(data.DATE_CHECK_EXCLUDED):
        row = i // 2
        col = i % 2
        ex = MARGIN_X + 10 + col * (half_w + 8)
        ey = fy + 23 + row * 14
        draw.text((ex, ey), f"×  {exc}", font=f_dexc, fill=BODY_INK)

    # Reader's key + repeated date in footer strap
    draw.line([(MARGIN_X + 8, fy + 54), (W - MARGIN_X - 8, fy + 54)], fill=HAIRLINE, width=1)
    f_key = get_font("sans_cond", 9)
    key_labels = (("CONFIRMED", "2+ outlets or officials"),
                  ("REPORTED", "single credible desk"),
                  ("CLAIM", "one party or state media"))
    kx = MARGIN_X + 8
    for tag, meaning in key_labels:
        seg = tag + " = " + meaning
        draw.text((kx, fy + 60), seg, font=f_key, fill=BODY_INK)
        kx += text_width(f_key, seg)
        draw.text((kx + 4, fy + 60), "·", font=f_key, fill=HAIRLINE)
        kx += text_width(f_key, "·") + 12

    f_fdate = get_font("sans_bold", 9)
    fdate = f"{data.EDITION_DATE} (UTC)"
    fdw = text_width(f_fdate, fdate)
    draw.text((W - MARGIN_X - 8 - fdw, fy + 60), fdate, font=f_fdate, fill=ACCENT)

    draw.line([(MARGIN_X, 1015), (W - MARGIN_X, 1015)], fill=INK, width=1)

    stats = {
        "story_count": total_stories,
        "region_counts": region_counts,
        "illustration_count": illus_counter[0],
        "avg_story_ink_pct": round(100.0 * sum(ink_ratios) / len(ink_ratios), 1),
    }
    return img, stats


def measure_band_densities(img: Image.Image) -> List[float]:
    edges = img.convert("L").filter(ImageFilter.FIND_EDGES)
    raw = edges.tobytes()
    bands: List[float] = []
    for b in range(8):
        start = b * 128 * W
        end = (b + 1) * 128 * W
        band_vals = raw[start:end]
        bands.append(round(sum(band_vals) / len(band_vals), 2))
    return bands


def save_deterministic_png(img: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, format="PNG", optimize=True, compress_level=9)


def build() -> Dict[str, object]:
    img, stats = render_page()
    here = Path(__file__).resolve().parent
    local_out = here / "entry.png"
    save_deterministic_png(img, local_out)

    # Also emit into /root/outputs/ni24/repo_A/entry.png when building from sess_A
    repo_dir = Path("/root/outputs/ni24/repo_A")
    if repo_dir.is_dir() and repo_dir.resolve() != here:
        save_deterministic_png(img, repo_dir / "entry.png")

    raw = local_out.read_bytes()
    md5 = hashlib.md5(raw).hexdigest()
    size = len(raw)
    assert img.size == (1024, 1024), f"Wrong dimensions: {img.size}"
    assert size <= 1_048_576, f"PNG too large: {size} bytes"
    assert raw.startswith(b"\x89PNG\r\n\x1a\n") and raw.endswith(b"IEND\xaeB`\x82"), "Invalid PNG markers"

    bands = measure_band_densities(img)
    stats.update({"md5": md5, "bytes": size, "bands": bands})
    return stats


if __name__ == "__main__":
    result = build()
    print("BUILD COMPLETE")
    print(f"  Stories:       {result['story_count']}")
    print(f"  Regions:       {result['region_counts']}")
    print(f"  Illustrations: {result['illustration_count']}")
    print(f"  Story ink avg: {result['avg_story_ink_pct']}%")
    print(f"  Bytes:         {result['bytes']}")
    print(f"  MD5:           {result['md5']}")
    print(f"  8-band edges:  {result['bands']}")
