#!/usr/bin/env python3
"""
generate_assets.py — Generate all illustration PNGs for Mission Espace levels 2-4.
Run: python3 generate_assets.py
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import math
import random

ROOT = Path(__file__).parent
ROMY_DIR = ROOT / "assets" / "illustrations" / "romy"
OSCAR_DIR = ROOT / "assets" / "illustrations" / "oscar"
ROMY_DIR.mkdir(parents=True, exist_ok=True)
OSCAR_DIR.mkdir(parents=True, exist_ok=True)

W, H = 460, 280
BG = (11, 11, 46)           # #0B0B2E
GOLD = (255, 215, 0)        # #FFD700
WHITE = (232, 232, 255)     # #E8E8FF
PURPLE = (206, 147, 216)    # #CE93D8
TEAL = (128, 203, 196)      # #80CBC4
ORANGE = (255, 140, 66)     # #FF8C42
RED = (255, 80, 80)
GREEN = (80, 220, 80)
BLUE = (80, 150, 255)
PINK = (255, 150, 180)
DIM = (68, 68, 102)
LIGHT_BLUE = (135, 206, 235)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def find_font(size):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
        "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass
    return ImageFont.load_default()


def new_canvas():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    rng = random.Random(42)
    for _ in range(60):
        x = rng.randint(0, W)
        y = rng.randint(0, H)
        brightness = rng.randint(80, 160)
        r = rng.randint(0, 1)
        if r == 0:
            draw.point((x, y), fill=(brightness, brightness, brightness + 30))
        else:
            draw.ellipse([x - r, y - r, x + r, y + r],
                         fill=(brightness, brightness, brightness + 30))
    return img, draw


def draw_text_centered(draw, text, y, font, color=WHITE):
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    x = (W - w) // 2
    draw.text((x, y), text, font=font, fill=color)
    return bbox[3] - bbox[1]


def text_width(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0]


def save(img, path):
    img.save(path, "PNG")
    print(f"  ✓ {path.name}")


def draw_star(draw, cx, cy, r, color=GOLD):
    """Draw a 5-pointed star centred at (cx, cy) with outer radius r."""
    pts = []
    for i in range(10):
        angle = math.radians(-90 + i * 36)
        radius = r if i % 2 == 0 else r * 0.42
        pts.append((cx + radius * math.cos(angle), cy + radius * math.sin(angle)))
    draw.polygon(pts, fill=color, outline=color)


def draw_rocket(draw, cx, cy, w=18, h=30, color=BLUE):
    """Simple rocket: body + nose + fins."""
    # body
    draw.rectangle([cx - w // 2, cy - h // 4, cx + w // 2, cy + h // 2],
                   fill=color)
    # nose (triangle)
    draw.polygon([
        (cx, cy - h // 2),
        (cx - w // 2, cy - h // 4),
        (cx + w // 2, cy - h // 4),
    ], fill=WHITE)
    # fins
    draw.polygon([
        (cx - w // 2, cy + h // 4),
        (cx - w // 2 - 6, cy + h // 2),
        (cx - w // 2, cy + h // 2),
    ], fill=ORANGE)
    draw.polygon([
        (cx + w // 2, cy + h // 4),
        (cx + w // 2 + 6, cy + h // 2),
        (cx + w // 2, cy + h // 2),
    ], fill=ORANGE)


def draw_border(draw, color=GOLD, width=4):
    draw.rectangle([width // 2, width // 2, W - width // 2, H - width // 2],
                   outline=color, width=width)


def draw_planet(draw, cx, cy, r, color, ring=False):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)
    if ring:
        draw.arc([cx - int(r * 1.5), cy - r // 3, cx + int(r * 1.5), cy + r // 3],
                 0, 360, fill=GOLD, width=2)


# ---------------------------------------------------------------------------
# ROMY Level 2 — Mathématiques
# ---------------------------------------------------------------------------

def gen_romy_l2_m09(path):
    img, draw = new_canvas()
    f_big = find_font(28)
    f_sub = find_font(17)
    # Space station: central circle + cross arms
    cx, cy = W // 2, H // 2 - 10
    draw.ellipse([cx - 30, cy - 30, cx + 30, cy + 30], fill=GOLD, outline=WHITE, width=2)
    draw.rectangle([cx - 70, cy - 8, cx + 70, cy + 8], fill=GOLD)   # horizontal arm
    draw.rectangle([cx - 8, cy - 55, cx + 8, cy + 55], fill=GOLD)   # vertical arm
    # Panels at arm tips
    for px, py in [(cx - 85, cy - 12), (cx + 65, cy - 12)]:
        draw.rectangle([px, py, px + 20, py + 24], fill=BLUE, outline=WHITE, width=1)
    draw_text_centered(draw, "STATION MATHS", H - 70, f_big, WHITE)
    draw_text_centered(draw, "Crée le dossier!", H - 40, f_sub, TEAL)
    save(img, path)


def gen_romy_l2_m10(path):
    img, draw = new_canvas()
    f = find_font(20)
    # 7 gold stars in pattern 3-2-2
    positions = [
        (130, 80), (230, 80), (330, 80),
        (180, 140), (280, 140),
        (155, 200), (305, 200),
    ]
    for (sx, sy) in positions:
        draw_star(draw, sx, sy, 28, GOLD)
    draw_text_centered(draw, "Combien d'étoiles ?", H - 38, f, WHITE)
    save(img, path)


def gen_romy_l2_m11(path):
    img, draw = new_canvas()
    f_huge = find_font(72)
    f_med = find_font(22)
    y = 60
    # "14" in blue
    draw.text((52, y), "14", font=f_huge, fill=BLUE)
    # "+" in white
    draw.text((178, y), "+", font=f_huge, fill=WHITE)
    # "23" in orange
    draw.text((258, y), "23", font=f_huge, fill=ORANGE)
    # "= ?" in gold
    draw_text_centered(draw, "= ?", H - 55, find_font(38), GOLD)
    draw_text_centered(draw, "Calcule l'addition", H - 28, f_med, TEAL)
    save(img, path)


def gen_romy_l2_m12(path):
    img, draw = new_canvas()
    f_huge = find_font(72)
    f_med = find_font(22)
    y = 60
    draw.text((52, y), "52", font=f_huge, fill=BLUE)
    draw.text((178, y + 4), "−", font=f_huge, fill=WHITE)
    draw.text((258, y), "18", font=f_huge, fill=RED)
    draw_text_centered(draw, "= ?", H - 55, find_font(38), GOLD)
    draw_text_centered(draw, "Calcule la soustraction", H - 28, f_med, TEAL)
    save(img, path)


def gen_romy_l2_m13(path):
    img, draw = new_canvas()
    f_big = find_font(44)
    f_med = find_font(20)
    # 2 columns of 6 circles
    cols = 2
    rows = 6
    r = 14
    col_x = [W // 2 - 50, W // 2 + 50]
    start_y = 28
    gap_y = (H - 80 - start_y) // (rows - 1)
    colors = [PURPLE, TEAL]
    for c in range(cols):
        for row in range(rows):
            cx = col_x[c]
            cy = start_y + row * gap_y
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=colors[c], outline=WHITE, width=1)
    draw_text_centered(draw, "2 × 6 = ?", H - 40, f_big, GOLD)
    save(img, path)


def gen_romy_l2_m14(path):
    img, draw = new_canvas()
    f_big = find_font(40)
    # 5 rows of 4 stars
    rows = 5
    cols = 4
    sw = W // (cols + 2)
    sh = (H - 80) // rows
    for row in range(rows):
        for col in range(cols):
            cx = sw + col * sw + sw // 2
            cy = 22 + row * sh + sh // 2
            draw_star(draw, cx, cy, 18, GOLD)
    draw_text_centered(draw, "5 × 4 = ?", H - 40, f_big, WHITE)
    save(img, path)


def gen_romy_l2_m15(path):
    img, draw = new_canvas()
    f_label = find_font(16)
    f_name = find_font(14)
    # Three shapes
    # Square (CARRÉ) — left
    draw.rectangle([40, 70, 130, 160], fill=PURPLE, outline=WHITE, width=2)
    draw_text_centered_x(draw, "CARRÉ", 85 + 10, 170, f_name, WHITE)
    # Triangle (TRIANGLE) — center
    draw.polygon([(200, 70), (155, 165), (245, 165)], fill=TEAL, outline=WHITE)
    draw_text_centered_x(draw, "TRIANGLE", 155, 170, f_name, WHITE)
    # Circle (CERCLE) — right
    draw.ellipse([290, 70, 420, 165], fill=ORANGE, outline=WHITE, width=2)
    draw_text_centered_x(draw, "CERCLE", 290, 170, f_name, WHITE)
    draw_text_centered(draw, "Formes géométriques", H - 35, f_label, GOLD)
    save(img, path)


def draw_text_centered_x(draw, text, x1, y, font, color):
    """Draw text centred between x1 and x2 (x2 unused — uses x1 as centre)."""
    # reuse as: centred at x1, top at y
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    draw.text((x1 - w // 2, y), text, font=font, fill=color)


def gen_romy_l2_m16(path):
    img, draw = new_canvas()
    f_big = find_font(32)
    f_med = find_font(18)
    # 4 groups of 3 planets (circles)
    group_cols = 4
    planet_cols = 3
    r = 12
    gw = W // (group_cols + 1)
    for g in range(group_cols):
        gx = gw * (g + 1)
        gy = H // 2 - 40
        # Draw a faint group circle
        draw.ellipse([gx - 46, gy - 20, gx + 46, gy + 55], outline=DIM, width=1)
        for p in range(planet_cols):
            px = gx + (p - 1) * 30
            py = gy + 18
            col = [BLUE, PURPLE, TEAL][p]
            draw.ellipse([px - r, py - r, px + r, py + r], fill=col, outline=WHITE, width=1)
    draw_text_centered(draw, "3 × 4 = ?", H - 50, f_big, GOLD)
    draw_text_centered(draw, "planètes × galaxies", H - 22, f_med, TEAL)
    save(img, path)


# ---------------------------------------------------------------------------
# ROMY Level 3 — Langage
# ---------------------------------------------------------------------------

def gen_romy_l3_m17(path):
    img, draw = new_canvas()
    f_big = find_font(22)
    f_sub = find_font(14)
    # Spaceship silhouette
    cx, cy = W // 2, H // 2 - 15
    # Body ellipse
    draw.ellipse([cx - 90, cy - 28, cx + 90, cy + 28], fill=PURPLE, outline=WHITE, width=2)
    # Nose cone
    draw.polygon([(cx + 90, cy), (cx + 130, cy - 12), (cx + 130, cy + 12)],
                 fill=WHITE)
    # Tail fins
    draw.polygon([(cx - 90, cy), (cx - 120, cy - 30), (cx - 95, cy)],
                 fill=TEAL)
    draw.polygon([(cx - 90, cy), (cx - 120, cy + 30), (cx - 95, cy)],
                 fill=TEAL)
    # Cockpit window
    draw.ellipse([cx - 20, cy - 16, cx + 20, cy + 16], fill=BLUE, outline=WHITE, width=2)
    draw.ellipse([cx - 8, cy - 6, cx + 8, cy + 6], fill=LIGHT_BLUE)
    draw_text_centered(draw, "VAISSEAU DU LANGAGE", H - 55, f_big, WHITE)
    draw_text_centered(draw, "Explore le langage!", H - 28, f_sub, TEAL)
    save(img, path)


def gen_romy_l3_m18(path):
    img, draw = new_canvas()
    f_hd = find_font(16)
    f_cell = find_font(17)
    f_title = find_font(20)
    rows = [("Je", "suis"), ("Tu", "es"), ("Il/Elle", "est")]
    col_x = [60, 230]
    col_w = [140, 160]
    row_h = 46
    start_y = 48
    draw_text_centered(draw, "Conjugaison : ÊTRE", 10, f_title, GOLD)
    for i, (pron, verb) in enumerate(rows):
        y0 = start_y + i * row_h
        y1 = y0 + row_h - 4
        fill = GOLD if i == 0 else (30, 30, 80)
        text_col = (20, 20, 40) if i == 0 else WHITE
        for j, (x, cw) in enumerate(zip(col_x, col_w)):
            draw.rectangle([x, y0, x + cw, y1], fill=fill, outline=WHITE, width=1)
            label = pron if j == 0 else verb
            bbox = draw.textbbox((0, 0), label, font=f_cell)
            lw = bbox[2] - bbox[0]
            lh = bbox[3] - bbox[1]
            draw.text((x + (cw - lw) // 2, y0 + (row_h - 4 - lh) // 2),
                      label, font=f_cell, fill=text_col)
    draw_text_centered(draw, "Verbe ÊTRE au présent", H - 28, f_hd, TEAL)
    save(img, path)


def gen_romy_l3_m19(path):
    img, draw = new_canvas()
    f_huge = find_font(54)
    f_big = find_font(26)
    f_med = find_font(18)
    draw_text_centered(draw, "jouer", 14, f_big, WHITE)
    # "Il JOUE au foot" — JOUE highlighted
    line = [("Il ", WHITE), ("JOUE", GOLD), (" au foot", WHITE)]
    total_w = sum(text_width(draw, t, f_big) for t, _ in line)
    x = (W - total_w) // 2
    y = 70
    for t, col in line:
        draw.text((x, y), t, font=f_big, fill=col)
        x += text_width(draw, t, f_big)
    # Large highlighted JOUE
    draw_text_centered(draw, "JOUE", 115, f_huge, GOLD)
    draw_text_centered(draw, "← conjugaison présent", H - 35, f_med, TEAL)
    save(img, path)


def gen_romy_l3_m20(path):
    img, draw = new_canvas()
    f_big = find_font(22)
    f_med = find_font(17)
    f_sm = find_font(14)
    mid = W // 2
    # Left: Masculin (blue tint)
    draw.rectangle([0, 0, mid - 1, H], fill=(20, 20, 80))
    # Right: Féminin (pink tint)
    draw.rectangle([mid + 1, 0, W, H], fill=(60, 10, 50))
    # Stars on top
    rng2 = random.Random(99)
    for _ in range(30):
        x = rng2.randint(0, W)
        y = rng2.randint(0, H)
        b = rng2.randint(80, 160)
        draw.point((x, y), fill=(b, b, b))
    # Dividing line
    draw.line([(mid, 0), (mid, H)], fill=WHITE, width=2)
    # Left content
    draw_text_centered_x(draw, "♂ Masculin", mid // 2, 20, f_big, BLUE)
    draw_text_centered_x(draw, "le soleil", mid // 2, 80, f_med, WHITE)
    # Sun
    draw.ellipse([mid // 2 - 28, 120, mid // 2 + 28, 176], fill=(255, 220, 0))
    for angle in range(0, 360, 45):
        ex = mid // 2 + int(40 * math.cos(math.radians(angle)))
        ey = 148 + int(40 * math.sin(math.radians(angle)))
        dx = mid // 2 + int(30 * math.cos(math.radians(angle)))
        dy = 148 + int(30 * math.sin(math.radians(angle)))
        draw.line([(dx, dy), (ex, ey)], fill=(255, 220, 0), width=2)
    # Right content
    draw_text_centered_x(draw, "♀ Féminin", mid + mid // 2, 20, f_big, PINK)
    draw_text_centered_x(draw, "la lune", mid + mid // 2, 80, f_med, WHITE)
    # Moon
    mx = mid + mid // 2
    draw.ellipse([mx - 28, 116, mx + 28, 176], fill=(200, 200, 240))
    draw.ellipse([mx - 14, 112, mx + 38, 176], fill=(60, 10, 50))
    save(img, path)


def gen_romy_l3_m21(path):
    img, draw = new_canvas()
    f_word = find_font(26)
    f_syl = find_font(30)
    f_count = find_font(50)
    syllables = [("CA", RED), ("PI", BLUE), ("TAI", PURPLE), ("NE", TEAL)]
    box_w = 90
    gap = 10
    total = len(syllables) * box_w + (len(syllables) - 1) * gap
    sx = (W - total) // 2
    sy = 60
    for i, (syl, col) in enumerate(syllables):
        x0 = sx + i * (box_w + gap)
        draw.rectangle([x0, sy, x0 + box_w, sy + 70], fill=col, outline=WHITE, width=2)
        bbox = draw.textbbox((0, 0), syl, font=f_syl)
        sw = bbox[2] - bbox[0]
        sh = bbox[3] - bbox[1]
        draw.text((x0 + (box_w - sw) // 2, sy + (70 - sh) // 2), syl, font=f_syl, fill=WHITE)
    draw_text_centered(draw, "capitaine", 15, f_word, WHITE)
    # Count
    draw.text((W - 90, H - 80), "4", font=f_count, fill=GOLD)
    draw_text_centered(draw, "syllabes", H - 35, find_font(18), GOLD)
    save(img, path)


def gen_romy_l3_m22(path):
    img, draw = new_canvas()
    f_en = find_font(20)
    f_fr = find_font(13)
    colors_data = [
        ("RED", "rouge", (220, 50, 50)),
        ("BLUE", "bleu", (60, 120, 220)),
        ("YELLOW", "jaune", (255, 215, 0)),
        ("GREEN", "vert", (60, 180, 80)),
    ]
    bw = 90
    gap = 16
    total = len(colors_data) * bw + (len(colors_data) - 1) * gap
    sx = (W - total) // 2
    sy = 50
    bh = 120
    for i, (en, fr, col) in enumerate(colors_data):
        x0 = sx + i * (bw + gap)
        draw.rectangle([x0, sy, x0 + bw, sy + bh], fill=col, outline=WHITE, width=2)
        bbox = draw.textbbox((0, 0), en, font=f_en)
        ew = bbox[2] - bbox[0]
        draw.text((x0 + (bw - ew) // 2, sy + bh // 2 - 14), en, font=f_en, fill=WHITE)
        bbox2 = draw.textbbox((0, 0), fr, font=f_fr)
        fw = bbox2[2] - bbox2[0]
        draw.text((x0 + (bw - fw) // 2, sy + bh + 6), fr, font=f_fr, fill=WHITE)
    draw_text_centered(draw, "Les couleurs / Colors", H - 28, find_font(16), TEAL)
    save(img, path)


def gen_romy_l3_m23(path):
    img, draw = new_canvas()
    f_num = find_font(22)
    f_word = find_font(15)
    items = [
        ("1", "one", "★"),
        ("2", "two", "✦"),
        ("3", "three", "☽"),
        ("4", "four", "◉"),
        ("5", "five", "☀"),
    ]
    col_w = W // len(items)
    for i, (num, word, sym) in enumerate(items):
        cx = col_w * i + col_w // 2
        colors = [GOLD, TEAL, PURPLE, ORANGE, RED]
        # Number circle
        draw.ellipse([cx - 22, 20, cx + 22, 64], fill=colors[i], outline=WHITE, width=2)
        bbox = draw.textbbox((0, 0), num, font=f_num)
        nw = bbox[2] - bbox[0]
        nh = bbox[3] - bbox[1]
        draw.text((cx - nw // 2, 20 + (44 - nh) // 2), num, font=f_num, fill=WHITE)
        # Symbol
        draw.text((cx - 10, 82), sym, font=find_font(28), fill=colors[i])
        # English word
        bbox2 = draw.textbbox((0, 0), word, font=f_word)
        ww = bbox2[2] - bbox2[0]
        draw.text((cx - ww // 2, 126), word, font=f_word, fill=WHITE)
    draw_text_centered(draw, "Numbers 1 to 5", H - 34, find_font(18), GOLD)
    save(img, path)


def gen_romy_l3_m24(path):
    img, draw = new_canvas()
    f_big = find_font(26)
    f_med = find_font(18)
    # Simple astronaut (circles)
    ax, ay = 90, 130
    draw.ellipse([ax - 22, ay - 60, ax + 22, ay - 16], fill=WHITE, outline=BLUE, width=2)  # helmet
    draw.ellipse([ax - 14, ay - 52, ax + 14, ay - 24], fill=LIGHT_BLUE)  # visor
    draw.rectangle([ax - 20, ay - 18, ax + 20, ay + 28], fill=(180, 180, 200), outline=WHITE, width=1)  # body
    # Arms
    draw.line([(ax - 20, ay - 10), (ax - 38, ay + 10)], fill=WHITE, width=6)
    draw.line([(ax + 20, ay - 10), (ax + 38, ay + 10)], fill=WHITE, width=6)
    # Legs
    draw.line([(ax - 10, ay + 28), (ax - 14, ay + 55)], fill=WHITE, width=6)
    draw.line([(ax + 10, ay + 28), (ax + 14, ay + 55)], fill=WHITE, width=6)
    # Speech bubble
    bx1, by1, bx2, by2 = 140, 60, 430, 160
    draw.rounded_rectangle([bx1, by1, bx2, by2], radius=16, fill=(30, 30, 80), outline=WHITE, width=2)
    # Bubble tail
    draw.polygon([(bx1 + 10, by2 - 10), (bx1 - 18, by2 + 18), (bx1 + 30, by2 - 4)],
                 fill=(30, 30, 80), outline=WHITE)
    draw_text_in_box(draw, "My name is", bx1, by1, bx2, by2, f_big, WHITE, offset_y=-20)
    draw_text_in_box(draw, "___________", bx1, by1, bx2, by2, f_med, GOLD, offset_y=18)
    save(img, path)


def draw_text_in_box(draw, text, x1, y1, x2, y2, font, color, offset_y=0):
    cx = (x1 + x2) // 2
    cy = (y1 + y2) // 2 + offset_y
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    draw.text((cx - w // 2, cy - h // 2), text, font=font, fill=color)


# ---------------------------------------------------------------------------
# ROMY Level 4 — Sciences
# ---------------------------------------------------------------------------

def gen_romy_l4_m25(path):
    img, draw = new_canvas()
    f_big = find_font(22)
    f_sub = find_font(14)
    cx, cy = W // 2, H // 2 - 20
    # Atom: nucleus + orbits
    draw.ellipse([cx - 14, cy - 14, cx + 14, cy + 14], fill=TEAL, outline=WHITE, width=2)
    for angle, col in [(0, GOLD), (60, PURPLE), (120, ORANGE)]:
        a = math.radians(angle)
        draw.arc([cx - 60, cy - 30, cx + 60, cy + 30],
                 angle, angle + 180, fill=col, width=2)
        draw.arc([cx - 60, cy - 30, cx + 60, cy + 30],
                 angle + 180, angle + 360, fill=col, width=1)
        # Electron dot
        ex = cx + int(60 * math.cos(a))
        ey = cy + int(30 * math.sin(a))
        draw.ellipse([ex - 5, ey - 5, ex + 5, ey + 5], fill=col)
    draw_text_centered(draw, "PLANÈTE DES SCIENCES", H - 58, f_big, WHITE)
    draw_text_centered(draw, "Laboratoire spatial", H - 30, f_sub, TEAL)
    save(img, path)


def gen_romy_l4_m26(path):
    img, draw = new_canvas()
    f_label = find_font(13)
    f_title = find_font(18)
    # Sun
    draw.ellipse([14, H // 2 - 34, 80, H // 2 + 34], fill=(255, 220, 0), outline=ORANGE, width=2)
    # Planets increasing in size
    planets = [
        (118, H // 2, 10, (180, 140, 100), "1 MERCURE"),
        (178, H // 2, 14, (220, 160, 80), "2 VÉNUS"),
        (250, H // 2, 18, BLUE, "3 TERRE"),
        (332, H // 2, 15, RED, "4 MARS"),
    ]
    for (px, py, r, col, name) in planets:
        draw.ellipse([px - r, py - r, px + r, py + r], fill=col, outline=WHITE, width=1)
        # Label below
        bbox = draw.textbbox((0, 0), name, font=f_label)
        lw = bbox[2] - bbox[0]
        draw.text((px - lw // 2, py + r + 4), name, font=f_label, fill=WHITE)
    draw_text_centered(draw, "L'ordre des planètes", H - 28, f_title, GOLD)
    save(img, path)


def gen_romy_l4_m27(path):
    img, draw = new_canvas()
    f_label = find_font(14)
    f_title = find_font(18)
    groups = [
        ("CARNIVORES", RED, "🦁", [(100, 90)]),
        ("HERBIVORES", GREEN, "🐄", [(230, 90)]),
        ("OMNIVORES", ORANGE, "🐻", [(360, 90)]),
    ]
    r = 46
    for (name, col, icon, positions) in groups:
        for (cx, cy) in positions:
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col, outline=WHITE, width=2)
            # Icon text
            draw.text((cx - 16, cy - 20), icon, font=find_font(30), fill=WHITE)
        bbox = draw.textbbox((0, 0), name, font=f_label)
        lw = bbox[2] - bbox[0]
        draw.text((positions[0][0] - lw // 2, positions[0][1] + r + 8),
                  name, font=f_label, fill=WHITE)
    draw_text_centered(draw, "Classification des animaux", H - 30, f_title, GOLD)
    save(img, path)


def gen_romy_l4_m28(path):
    img, draw = new_canvas()
    f_label = find_font(14)
    f_title = find_font(18)
    # Water cycle: Sun → arrow → cloud → rain → puddle
    # Sun
    sun_cx, sun_cy = 60, 60
    draw.ellipse([sun_cx - 22, sun_cy - 22, sun_cx + 22, sun_cy + 22], fill=(255, 215, 0))
    draw.text((sun_cx - 20, sun_cy + 26), "Soleil", font=f_label, fill=GOLD)
    # Arrow up-right
    draw.line([(90, 60), (150, 40)], fill=WHITE, width=2)
    draw.polygon([(150, 40), (138, 44), (146, 52)], fill=WHITE)
    draw.text((100, 26), "Évaporation", font=f_label, fill=TEAL)
    # Cloud
    cloud_cx, cloud_cy = 230, 50
    draw.ellipse([cloud_cx - 40, cloud_cy - 20, cloud_cx + 40, cloud_cy + 20], fill=(180, 180, 220))
    draw.ellipse([cloud_cx - 60, cloud_cy - 8, cloud_cx + 10, cloud_cy + 22], fill=(180, 180, 220))
    draw.ellipse([cloud_cx + 10, cloud_cy - 8, cloud_cx + 60, cloud_cy + 22], fill=(180, 180, 220))
    draw.text((cloud_cx - 20, cloud_cy + 22), "Nuages", font=f_label, fill=WHITE)
    # Arrow down
    draw.line([(cloud_cx, cloud_cy + 42), (cloud_cx, cloud_cy + 80)], fill=WHITE, width=2)
    draw.polygon([(cloud_cx, cloud_cy + 80), (cloud_cx - 6, cloud_cy + 68), (cloud_cx + 6, cloud_cy + 68)], fill=WHITE)
    draw.text((cloud_cx + 6, cloud_cy + 54), "Pluie", font=f_label, fill=BLUE)
    # Rain drops
    rain_y = cloud_cy + 85
    for rx in range(cloud_cx - 30, cloud_cx + 40, 15):
        draw.line([(rx, rain_y), (rx - 4, rain_y + 18)], fill=BLUE, width=2)
    # Puddle
    draw.ellipse([cloud_cx - 50, 170, cloud_cx + 50, 200], fill=BLUE, outline=LIGHT_BLUE, width=1)
    draw.text((cloud_cx - 18, 202), "Eau", font=f_label, fill=LIGHT_BLUE)
    # Arrow to sun (cycle)
    draw.arc([380, 40, 450, 200], -90, 90, fill=DIM, width=2)
    draw_text_centered(draw, "Le cycle de l'eau", H - 28, f_title, GOLD)
    save(img, path)


def gen_romy_l4_m29(path):
    img, draw = new_canvas()
    f_label = find_font(14)
    f_title = find_font(17)
    senses = [
        ("VUE", "👁", BLUE, (W // 2, 60)),
        ("OUÏE", "👂", PURPLE, (W // 2 - 120, 130)),
        ("ODORAT", "👃", TEAL, (W // 2 + 120, 130)),
        ("GOÛT", "👅", RED, (W // 2 - 80, 210)),
        ("TOUCHER", "✋", ORANGE, (W // 2 + 80, 210)),
    ]
    # Draw lines from centre to each sense
    for (name, icon, col, (sx, sy)) in senses:
        draw.line([(W // 2, H // 2 - 10), (sx, sy)], fill=DIM, width=1)
    for (name, icon, col, (sx, sy)) in senses:
        r = 34
        draw.ellipse([sx - r, sy - r, sx + r, sy + r], fill=col, outline=WHITE, width=2)
        draw.text((sx - 12, sy - 18), icon, font=find_font(22), fill=WHITE)
        bbox = draw.textbbox((0, 0), name, font=f_label)
        nw = bbox[2] - bbox[0]
        draw.text((sx - nw // 2, sy + r + 2), name, font=f_label, fill=WHITE)
    draw_text_centered(draw, "Les 5 sens", H - 30, f_title, GOLD)
    save(img, path)


def gen_romy_l4_m30(path):
    img, draw = new_canvas()
    f_title = find_font(22)
    f_name = find_font(38)
    f_sub = find_font(14)
    # Gold border
    draw_border(draw, GOLD, 6)
    # Corner stars
    for (sx, sy) in [(22, 22), (W - 22, 22), (22, H - 22), (W - 22, H - 22)]:
        draw_star(draw, sx, sy, 14, GOLD)
    # Edge stars
    rng = random.Random(7)
    for _ in range(12):
        sx = rng.randint(30, W - 30)
        sy = rng.choice([rng.randint(6, 22), rng.randint(H - 22, H - 6)])
        draw_star(draw, sx, sy, 8, GOLD)
    draw_text_centered(draw, "★ DIPLÔME DE CAPITAINE ★", 38, f_title, GOLD)
    draw_text_centered(draw, "ROMY", 95, f_name, WHITE)
    draw.line([(60, 152), (400, 152)], fill=GOLD, width=2)
    draw_text_centered(draw, "Mission Espace accomplie!", 162, f_sub, TEAL)
    draw_text_centered(draw, "Niveau 4 complété avec succès", H - 50, f_sub, WHITE)
    save(img, path)


# ---------------------------------------------------------------------------
# OSCAR Level 2 — Mathématiques
# ---------------------------------------------------------------------------

def gen_oscar_l2_m10(path):
    img, draw = new_canvas()
    f_big = find_font(22)
    f_sub = find_font(14)
    # Rocket shape
    cx, cy = W // 2 - 60, H // 2 - 10
    draw_rocket(draw, cx, cy, 22, 38, TEAL)
    # Calculator shape
    cx2 = W // 2 + 60
    draw.rounded_rectangle([cx2 - 30, cy - 45, cx2 + 30, cy + 45], radius=6,
                            fill=(40, 40, 100), outline=GOLD, width=2)
    # Buttons grid
    for row in range(3):
        for col in range(3):
            bx = cx2 - 20 + col * 16
            by = cy - 10 + row * 16
            draw.rectangle([bx, by, bx + 12, by + 12], fill=TEAL, outline=WHITE, width=1)
    draw_text_centered(draw, "MODULE MATHÉMATIQUES", H - 55, f_big, WHITE)
    draw_text_centered(draw, "Prêt pour les calculs ?", H - 28, f_sub, TEAL)
    save(img, path)


def gen_oscar_l2_m11(path):
    img, draw = new_canvas()
    f_huge = find_font(64)
    f_line = find_font(38)
    f_med = find_font(18)
    # Long multiplication layout
    draw_text_centered(draw, "47", 20, f_huge, BLUE)
    draw_text_centered(draw, "×   8", 90, f_line, ORANGE)
    # Separator line
    draw.line([(W // 2 - 80, 148), (W // 2 + 80, 148)], fill=WHITE, width=3)
    draw_text_centered(draw, "?", 155, f_huge, GOLD)
    draw_text_centered(draw, "Quelle est la réponse ?", H - 28, f_med, TEAL)
    save(img, path)


def gen_oscar_l2_m12(path):
    img, draw = new_canvas()
    f_huge = find_font(56)
    f_med = find_font(22)
    f_sm = find_font(16)
    y = 50
    draw.text((38, y), "156", font=f_huge, fill=BLUE)
    draw.text((198, y + 6), "÷", font=find_font(48), fill=WHITE)
    draw.text((260, y), "4", font=f_huge, fill=ORANGE)
    draw_text_centered(draw, "= ?", H - 80, find_font(44), GOLD)
    # Remainder box hint
    draw.rounded_rectangle([W // 2 - 60, H - 58, W // 2 + 60, H - 30],
                            radius=6, fill=(30, 30, 80), outline=DIM, width=1)
    draw_text_centered(draw, "reste ?", H - 53, find_font(14), DIM)
    draw_text_centered(draw, "Division euclidienne", H - 22, f_sm, TEAL)
    save(img, path)


def gen_oscar_l2_m13(path):
    img, draw = new_canvas()
    f_frac = find_font(64)
    f_title = find_font(18)
    # Pizza circle divided into 4, 3 colored
    cx, cy, r = W // 2, H // 2 - 10, 90
    slice_colors = [ORANGE, GOLD, RED, (40, 40, 80)]  # 4th slice = dark (missing)
    for i in range(4):
        start = -90 + i * 90
        end = start + 90
        draw.pieslice([cx - r, cy - r, cx + r, cy + r], start, end,
                      fill=slice_colors[i], outline=WHITE, width=2)
    # Fraction label
    draw_text_centered(draw, "3/4", H - 60, f_frac, GOLD)
    draw_text_centered(draw, "Fraction de pizza", H - 24, f_title, WHITE)
    save(img, path)


def gen_oscar_l2_m14(path):
    img, draw = new_canvas()
    f_huge = find_font(60)
    f_med = find_font(22)
    y = 55
    draw.text((28, y), "2,5", font=f_huge, fill=BLUE)
    draw.text((178, y + 4), "+", font=find_font(52), fill=WHITE)
    draw.text((260, y), "1,3", font=f_huge, fill=ORANGE)
    draw_text_centered(draw, "= ?", H - 60, find_font(44), GOLD)
    draw_text_centered(draw, "Addition de décimaux", H - 28, f_med, TEAL)
    save(img, path)


def gen_oscar_l2_m15(path):
    img, draw = new_canvas()
    f_label = find_font(16)
    f_formula = find_font(20)
    f_title = find_font(16)
    # Rectangle with labeled sides
    rx1, ry1, rx2, ry2 = 80, 60, 360, 180
    draw.rectangle([rx1, ry1, rx2, ry2], fill=(30, 30, 90), outline=TEAL, width=3)
    # Side labels
    draw_text_centered_x(draw, "7 cm", (rx1 + rx2) // 2, ry1 - 22, f_label, WHITE)
    draw_text_centered_x(draw, "7 cm", (rx1 + rx2) // 2, ry2 + 6, f_label, WHITE)
    draw.text((rx1 - 44, (ry1 + ry2) // 2 - 8), "3 cm", font=f_label, fill=WHITE)
    draw.text((rx2 + 6, (ry1 + ry2) // 2 - 8), "3 cm", font=f_label, fill=WHITE)
    # Formula
    draw_text_centered(draw, "P = 2×(7+3) = ?", H - 42, f_formula, GOLD)
    draw_text_centered(draw, "Périmètre du rectangle", H - 20, f_title, TEAL)
    save(img, path)


def gen_oscar_l2_m16(path):
    img, draw = new_canvas()
    f_formula = find_font(22)
    f_title = find_font(16)
    # 7×3 grid
    cell = 36
    grid_w = 7 * cell
    grid_h = 3 * cell
    gx = (W - grid_w) // 2
    gy = 30
    for row in range(3):
        for col in range(7):
            x0 = gx + col * cell
            y0 = gy + row * cell
            col_idx = (row * 7 + col) % 4
            fill = [PURPLE, TEAL, BLUE, ORANGE][col_idx]
            draw.rectangle([x0 + 2, y0 + 2, x0 + cell - 2, y0 + cell - 2],
                           fill=fill, outline=WHITE, width=1)
    draw_text_centered(draw, "A = 7 × 3 = ?", gy + grid_h + 16, f_formula, GOLD)
    draw_text_centered(draw, "Aire du rectangle", H - 22, f_title, TEAL)
    save(img, path)


def gen_oscar_l2_m17(path):
    img, draw = new_canvas()
    f_big = find_font(36)
    f_med = find_font(18)
    # 9 rows of 7 dots
    dot_r = 7
    cols = 7
    rows = 9
    total_w = cols * (dot_r * 2 + 4)
    total_h = rows * (dot_r * 2 + 4)
    sx = (W - total_w) // 2
    sy = 14
    for row in range(rows):
        for col in range(cols):
            cx = sx + col * (dot_r * 2 + 4) + dot_r
            cy = sy + row * (dot_r * 2 + 4) + dot_r
            col_idx = row % 3
            fill = [GOLD, TEAL, PURPLE][col_idx]
            draw.ellipse([cx - dot_r, cy - dot_r, cx + dot_r, cy + dot_r], fill=fill)
    draw_text_centered(draw, "9 × 7 = ?", H - 45, f_big, WHITE)
    draw_text_centered(draw, "Table de 9", H - 20, f_med, GOLD)
    save(img, path)


def gen_oscar_l2_m18(path):
    img, draw = new_canvas()
    f_big = find_font(26)
    f_med = find_font(16)
    # 24 stars in 3 groups of 8
    star_r = 10
    groups = 3
    per_group = 8
    cols_per_group = 4
    rows_per_group = 2
    gw = W // groups
    for g in range(groups):
        # Group circle (highlight first group)
        gcx = gw * g + gw // 2
        gcy = H // 2 - 20
        highlight = g == 0
        draw.ellipse([gcx - 60, gcy - 36, gcx + 60, gcy + 36],
                     outline=GOLD if highlight else DIM, width=2 if highlight else 1)
        for i in range(per_group):
            row = i // cols_per_group
            col = i % cols_per_group
            sx = gcx - 42 + col * 28
            sy = gcy - 22 + row * 28
            draw_star(draw, sx, sy, star_r, GOLD if highlight else WHITE)
    draw_text_centered(draw, "1/3 de 24 = ?", H - 50, f_big, GOLD)
    draw_text_centered(draw, "Fraction d'une quantité", H - 26, f_med, TEAL)
    save(img, path)


# ---------------------------------------------------------------------------
# OSCAR Level 3 — Communication
# ---------------------------------------------------------------------------

def gen_oscar_l3_m19(path):
    img, draw = new_canvas()
    f_big = find_font(22)
    f_sub = find_font(14)
    # Radio tower / antenna
    cx, cy = W // 2, H // 2 + 20
    # Tower body
    draw.polygon([
        (cx - 6, cy + 50), (cx + 6, cy + 50),
        (cx + 2, cy - 60), (cx - 2, cy - 60),
    ], fill=TEAL, outline=WHITE)
    # Cross beams
    for yb in [cy - 30, cy - 10, cy + 10, cy + 30]:
        span = int((yb - (cy - 60)) / 110 * 50) + 10
        draw.line([(cx - span, yb), (cx + span, yb)], fill=TEAL, width=2)
    # Signal waves
    for i, r in enumerate([20, 35, 50]):
        alpha = 255 - i * 50
        draw.arc([cx - r, cy - 80 - r, cx + r, cy - 80 + r], -60, 60,
                 fill=GOLD, width=2)
    draw_text_centered(draw, "CENTRE COMMUNICATION", H - 55, f_big, WHITE)
    draw_text_centered(draw, "Missions de langage", H - 28, f_sub, TEAL)
    save(img, path)


def gen_oscar_l3_m20(path):
    img, draw = new_canvas()
    f_big = find_font(22)
    f_med = find_font(16)
    f_verb = find_font(26)
    # Timeline arrow
    arrow_y = H // 2 - 10
    draw.line([(30, arrow_y), (W - 30, arrow_y)], fill=WHITE, width=3)
    draw.polygon([(W - 30, arrow_y), (W - 44, arrow_y - 7), (W - 44, arrow_y + 7)], fill=WHITE)
    # Past / Present labels
    draw.text((40, arrow_y - 30), "PASSÉ", font=f_med, fill=BLUE)
    draw_text_centered_x(draw, "PRÉSENT", W // 2, arrow_y - 30, f_med, GREEN)
    # Rocket on past side
    draw_rocket(draw, 100, arrow_y - 50, 14, 24, BLUE)
    # Marker dot on past
    draw.ellipse([88, arrow_y - 7, 112, arrow_y + 7], fill=BLUE)
    # Marker dot on present
    draw.ellipse([W // 2 - 7, arrow_y - 7, W // 2 + 7, arrow_y + 7], fill=GREEN)
    # Labels
    draw.text((50, arrow_y + 12), "j'ai joué", font=f_verb, fill=BLUE)
    draw_text_centered_x(draw, "je joue", W // 2, arrow_y + 12, f_verb, GREEN)
    draw_text_centered(draw, "Passé composé : JOUER", H - 28, f_big, GOLD)
    save(img, path)


def gen_oscar_l3_m21(path):
    img, draw = new_canvas()
    f_cat = find_font(18)
    f_ex = find_font(14)
    f_title = find_font(17)
    sections = [
        ("NOM", "astronaute", BLUE),
        ("VERBE", "voler", RED),
        ("ADJECTIF", "spatial", GREEN),
    ]
    bw = 120
    gap = 20
    total = len(sections) * bw + (len(sections) - 1) * gap
    sx = (W - total) // 2
    sy = 40
    bh = 140
    for i, (cat, ex, col) in enumerate(sections):
        x0 = sx + i * (bw + gap)
        draw.rectangle([x0, sy, x0 + bw, sy + bh], fill=col, outline=WHITE, width=2)
        bbox = draw.textbbox((0, 0), cat, font=f_cat)
        cw = bbox[2] - bbox[0]
        draw.text((x0 + (bw - cw) // 2, sy + 12), cat, font=f_cat, fill=WHITE)
        draw.line([(x0 + 10, sy + 44), (x0 + bw - 10, sy + 44)], fill=WHITE, width=1)
        bbox2 = draw.textbbox((0, 0), ex, font=f_ex)
        ew = bbox2[2] - bbox2[0]
        draw.text((x0 + (bw - ew) // 2, sy + 56), ex, font=f_ex, fill=WHITE)
    draw_text_centered(draw, "Classes de mots", H - 26, f_title, GOLD)
    save(img, path)


def gen_oscar_l3_m22(path):
    img, draw = new_canvas()
    f_big = find_font(22)
    f_med = find_font(17)
    f_sm = find_font(14)
    # Subject → verb
    draw_text_centered(draw, "Les astronautes", 32, f_big, TEAL)
    # Arrow
    draw.line([(W // 2, 80), (W // 2, 120)], fill=WHITE, width=2)
    draw.polygon([(W // 2, 120), (W // 2 - 7, 108), (W // 2 + 7, 108)], fill=WHITE)
    # Verb with S highlighted
    verb_parts = [("voyage", WHITE), ("nt", GOLD)]
    total_w = sum(text_width(draw, t, f_big) for t, _ in verb_parts)
    x = (W - total_w) // 2
    y = 128
    for t, col in verb_parts:
        draw.text((x, y), t, font=f_big, fill=col)
        x += text_width(draw, t, f_big)
    draw.text((50, 32), "Sujet pluriel →", font=f_sm, fill=DIM)
    draw.text((50, 128), "Verbe pluriel", font=f_sm, fill=DIM)
    draw_text_centered(draw, "Accord sujet-verbe", H - 28, find_font(16), GOLD)
    save(img, path)


def gen_oscar_l3_m23(path):
    img, draw = new_canvas()
    f_title = find_font(18)
    f_cell = find_font(14)
    f_verb = find_font(16)
    rows = [
        ("je", "SERAI"), ("tu", "SERAS"), ("il/elle", "SERA"),
        ("nous", "SERONS"), ("vous", "SEREZ"), ("ils/elles", "SERONT"),
    ]
    highlight_row = 3  # "nous SERONS"
    col_w = [110, 120]
    col_x = [(W - col_w[0] - col_w[1]) // 2, (W - col_w[0] - col_w[1]) // 2 + col_w[0]]
    row_h = 32
    start_y = 28
    draw_text_centered(draw, "ÊTRE au futur simple", 4, f_title, GOLD)
    for i, (pron, verb) in enumerate(rows):
        y0 = start_y + i * row_h
        y1 = y0 + row_h - 2
        is_hl = (i == highlight_row)
        fill_p = GOLD if is_hl else (25, 25, 70)
        fill_v = GOLD if is_hl else (35, 35, 90)
        tc = (20, 20, 40) if is_hl else WHITE
        draw.rectangle([col_x[0], y0, col_x[0] + col_w[0], y1], fill=fill_p, outline=DIM, width=1)
        draw.rectangle([col_x[1], y0, col_x[1] + col_w[1], y1], fill=fill_v, outline=DIM, width=1)
        bbox = draw.textbbox((0, 0), pron, font=f_cell)
        pw = bbox[2] - bbox[0]
        draw.text((col_x[0] + (col_w[0] - pw) // 2, y0 + 6), pron, font=f_cell, fill=tc)
        bbox2 = draw.textbbox((0, 0), verb, font=f_verb)
        vw = bbox2[2] - bbox2[0]
        draw.text((col_x[1] + (col_w[1] - vw) // 2, y0 + 4), verb, font=f_verb, fill=tc)
    save(img, path)


def gen_oscar_l3_m24(path):
    img, draw = new_canvas()
    f_center = find_font(26)
    f_syn = find_font(18)
    # Central word
    cx, cy = W // 2, H // 2 - 10
    draw.rounded_rectangle([cx - 56, cy - 22, cx + 56, cy + 22], radius=8,
                            fill=BLUE, outline=WHITE, width=2)
    draw_text_in_box(draw, "GRAND", cx - 56, cy - 22, cx + 56, cy + 22, f_center, WHITE)
    synonymes = [
        ("IMMENSE", (cx - 170, cy - 70)),
        ("GIGANTESQUE", (cx + 150, cy - 70)),
        ("ÉNORME", (cx - 160, cy + 70)),
        ("VASTE", (cx + 150, cy + 70)),
    ]
    for (syn, (sx, sy)) in synonymes:
        draw.line([(cx, cy), (sx, sy)], fill=DIM, width=1)
        bbox = draw.textbbox((0, 0), syn, font=f_syn)
        sw = bbox[2] - bbox[0]
        sh = bbox[3] - bbox[1]
        draw.rounded_rectangle([sx - sw // 2 - 6, sy - sh // 2 - 4,
                                 sx + sw // 2 + 6, sy + sh // 2 + 4],
                                radius=6, fill=(30, 30, 80), outline=PURPLE, width=1)
        draw.text((sx - sw // 2, sy - sh // 2), syn, font=f_syn, fill=PURPLE)
    draw_text_centered(draw, "Synonymes", H - 22, find_font(16), GOLD)
    save(img, path)


def gen_oscar_l3_m25(path):
    img, draw = new_canvas()
    f_big = find_font(22)
    f_sm = find_font(14)
    # Football / soccer ball (hexagon pattern approximation)
    bx, by, br = 110, H // 2 - 10, 56
    draw.ellipse([bx - br, by - br, bx + br, by + br], fill=WHITE, outline=(50, 50, 50), width=2)
    # Hexagon patches (approximate)
    patch_cols = [(0, 0, 0), (0, 0, 0), (50, 50, 50)]
    for angle, size in [(0, 18), (60, 14), (180, 14), (270, 14), (120, 14)]:
        px = bx + int(28 * math.cos(math.radians(angle)))
        py = by + int(28 * math.sin(math.radians(angle)))
        draw.ellipse([px - size // 2, py - size // 2, px + size // 2, py + size // 2],
                     fill=(0, 0, 0))
    draw.ellipse([bx - 10, by - 10, bx + 10, by + 10], fill=(0, 0, 0))
    # Speech bubble
    bx1, by1, bx2, by2 = 190, 60, 440, 160
    draw.rounded_rectangle([bx1, by1, bx2, by2], radius=14, fill=(20, 20, 70), outline=TEAL, width=2)
    draw.polygon([(bx1 + 16, by2 - 8), (bx1 - 14, by2 + 18), (bx1 + 36, by2 - 2)],
                 fill=(20, 20, 70), outline=TEAL)
    draw_text_in_box(draw, "I like football", bx1, by1, bx2, by2, f_big, WHITE, offset_y=-10)
    draw_text_in_box(draw, "J'aime le football", bx1, by1, bx2, by2, f_sm, TEAL, offset_y=20)
    save(img, path)


def gen_oscar_l3_m26(path):
    img, draw = new_canvas()
    f_label = find_font(14)
    f_title = find_font(18)
    # Family tree
    # Parents at top
    parents = [("MOTHER", W // 2 - 100, 50), ("FATHER", W // 2 + 100, 50)]
    children = [("BROTHER", W // 2 - 80, 170), ("SISTER", W // 2 + 80, 170)]
    box_w, box_h = 100, 38
    for (label, px, py) in parents:
        draw.rounded_rectangle([px - box_w // 2, py, px + box_w // 2, py + box_h],
                                radius=6, fill=BLUE, outline=WHITE, width=2)
        bbox = draw.textbbox((0, 0), label, font=f_label)
        lw = bbox[2] - bbox[0]
        draw.text((px - lw // 2, py + (box_h - (bbox[3] - bbox[1])) // 2),
                  label, font=f_label, fill=WHITE)
    # Line between parents
    draw.line([(W // 2 - 50, 69), (W // 2 + 50, 69)], fill=WHITE, width=2)
    # Line down to children
    draw.line([(W // 2, 69), (W // 2, 130)], fill=WHITE, width=2)
    draw.line([(W // 2 - 80, 130), (W // 2 + 80, 130)], fill=WHITE, width=2)
    for (label, px, py) in children:
        draw.line([(px, 130), (px, py)], fill=WHITE, width=2)
        draw.rounded_rectangle([px - box_w // 2, py, px + box_w // 2, py + box_h],
                                radius=6, fill=PURPLE, outline=WHITE, width=2)
        bbox = draw.textbbox((0, 0), label, font=f_label)
        lw = bbox[2] - bbox[0]
        draw.text((px - lw // 2, py + (box_h - (bbox[3] - bbox[1])) // 2),
                  label, font=f_label, fill=WHITE)
    draw_text_centered(draw, "My Family / Ma Famille", H - 28, f_title, GOLD)
    save(img, path)


def gen_oscar_l3_m27(path):
    img, draw = new_canvas()
    f_title = find_font(20)
    f_text = find_font(16)
    f_blank = find_font(20)
    # Pencil
    px, py = 80, H // 2 - 10
    draw.polygon([(px - 8, py - 50), (px + 8, py - 50), (px + 8, py + 30), (px - 8, py + 30)],
                 fill=(255, 220, 50), outline=WHITE, width=1)
    draw.polygon([(px - 8, py + 30), (px + 8, py + 30), (px, py + 52)],
                 fill=(220, 180, 140))
    draw.line([(px - 8, py - 36), (px + 8, py - 36)], fill=(180, 0, 0), width=3)
    # Notebook lines
    nx, ny = 150, 50
    for i in range(5):
        y = ny + i * 36
        draw.line([(nx, y), (W - 30, y)], fill=DIM, width=1)
    # Text with blank
    text1 = "Les astronautes"
    text2 = "voyage____"
    text3 = "dans l'espace."
    draw.text((nx + 6, ny + 4), text1, font=f_text, fill=WHITE)
    # highlight blank
    x2 = nx + 6
    draw.text((x2, ny + 40), "voyage", font=f_text, fill=WHITE)
    x2 += text_width(draw, "voyage", f_text)
    draw.text((x2, ny + 36), "____", font=f_blank, fill=GOLD)
    draw.text((nx + 6, ny + 76), text3, font=f_text, fill=WHITE)
    draw_text_centered(draw, "Complète la dictée", H - 28, f_title, GOLD)
    save(img, path)


# ---------------------------------------------------------------------------
# OSCAR Level 4 — Sciences
# ---------------------------------------------------------------------------

def gen_oscar_l4_m28(path):
    img, draw = new_canvas()
    f_big = find_font(22)
    f_sub = find_font(14)
    # Microscope (simplified)
    mx, my = W // 2 - 70, H // 2 - 10
    draw.rectangle([mx - 6, my - 50, mx + 6, my + 40], fill=WHITE, outline=DIM, width=1)
    draw.ellipse([mx - 16, my + 30, mx + 16, my + 60], fill=TEAL, outline=WHITE, width=2)
    draw.ellipse([mx - 10, my - 62, mx + 10, my - 42], fill=PURPLE)
    draw.line([(mx - 30, my + 20), (mx + 30, my + 20)], fill=WHITE, width=4)
    # Telescope (simplified)
    tx, ty = W // 2 + 70, H // 2 - 10
    draw.line([(tx - 60, ty), (tx + 30, ty - 20)], fill=GOLD, width=8)
    draw.ellipse([tx + 24, ty - 28, tx + 44, ty - 8], fill=WHITE, outline=GOLD, width=2)
    draw.ellipse([tx - 68, ty - 8, tx - 52, ty + 8], fill=WHITE, outline=GOLD, width=2)
    # Tripod
    draw.line([(tx - 10, ty + 8), (tx - 30, ty + 50)], fill=GOLD, width=3)
    draw.line([(tx - 10, ty + 8), (tx + 10, ty + 50)], fill=GOLD, width=3)
    draw_text_centered(draw, "LABORATOIRE SPATIAL", H - 55, f_big, WHITE)
    draw_text_centered(draw, "Sciences en mission!", H - 28, f_sub, TEAL)
    save(img, path)


def gen_oscar_l4_m29(path):
    img, draw = new_canvas()
    f_title = find_font(20)
    f_label = find_font(14)
    f_eq = find_font(13)
    # Sun
    draw.ellipse([20, 30, 80, 90], fill=(255, 215, 0))
    # Arrow
    draw.line([(82, 60), (130, 100)], fill=WHITE, width=2)
    draw.polygon([(130, 100), (118, 92), (124, 106)], fill=WHITE)
    draw.text((84, 66), "lumière", font=find_font(10), fill=DIM)
    # Leaf
    leaf_cx, leaf_cy = 210, 130
    draw.ellipse([leaf_cx - 60, leaf_cy - 36, leaf_cx + 60, leaf_cy + 36],
                 fill=GREEN, outline=(40, 160, 40), width=2)
    # Leaf vein
    draw.line([(leaf_cx - 56, leaf_cy), (leaf_cx + 56, leaf_cy)], fill=(40, 160, 40), width=2)
    for i in range(-3, 4):
        ox = i * 14
        draw.line([(leaf_cx + ox, leaf_cy), (leaf_cx + ox - 16, leaf_cy - 20)],
                  fill=(40, 160, 40), width=1)
        draw.line([(leaf_cx + ox, leaf_cy), (leaf_cx + ox + 16, leaf_cy + 20)],
                  fill=(40, 160, 40), width=1)
    # Equation inside leaf
    eq_lines = ["CO₂ + H₂O", "→ Glucose + O₂"]
    for i, line in enumerate(eq_lines):
        bbox = draw.textbbox((0, 0), line, font=f_eq)
        lw = bbox[2] - bbox[0]
        draw.text((leaf_cx - lw // 2, leaf_cy - 10 + i * 18), line, font=f_eq, fill=WHITE)
    # Input arrows
    draw.text((leaf_cx - 90, leaf_cy - 60), "CO₂", font=f_label, fill=TEAL)
    draw.line([(leaf_cx - 64, leaf_cy - 52), (leaf_cx - 54, leaf_cy - 32)],
              fill=TEAL, width=2)
    draw.text((leaf_cx - 90, leaf_cy + 40), "H₂O", font=f_label, fill=BLUE)
    draw.line([(leaf_cx - 64, leaf_cy + 50), (leaf_cx - 54, leaf_cy + 32)],
              fill=BLUE, width=2)
    # Output arrows
    draw.text((leaf_cx + 70, leaf_cy - 60), "O₂", font=f_label, fill=TEAL)
    draw.line([(leaf_cx + 62, leaf_cy - 30), (leaf_cx + 72, leaf_cy - 50)],
              fill=TEAL, width=2)
    draw_text_centered(draw, "PHOTOSYNTHÈSE", H - 28, f_title, GOLD)
    save(img, path)


def gen_oscar_l4_m30(path):
    img, draw = new_canvas()
    f_title = find_font(16)
    f_state = find_font(15)
    f_label = find_font(13)
    # Three panels
    panels = [
        ("SOLIDE", "Glace", LIGHT_BLUE, 60),
        ("LIQUIDE", "Eau", BLUE, 210),
        ("GAZEUX", "Vapeur", (200, 200, 220), 360),
    ]
    pw = 110
    ph = 150
    py0 = 40
    for (state, ex, col, px) in panels:
        draw.rectangle([px - pw // 2, py0, px + pw // 2, py0 + ph],
                       fill=(20, 20, 60), outline=col, width=2)
        # Shape inside
        if state == "SOLIDE":
            draw.rectangle([px - 28, py0 + 30, px + 28, py0 + 90],
                           fill=col, outline=WHITE, width=1)
        elif state == "LIQUIDE":
            for i in range(3):
                dx = (i - 1) * 22
                draw.ellipse([px + dx - 12, py0 + 40, px + dx + 12, py0 + 80],
                             fill=col)
        else:
            for i in range(3):
                wy = py0 + 32 + i * 20
                draw.arc([px - 24, wy, px + 24, wy + 18], 0, 180, fill=col, width=3)
        bbox = draw.textbbox((0, 0), state, font=f_state)
        sw = bbox[2] - bbox[0]
        draw.text((px - sw // 2, py0 + ph - 28), state, font=f_state, fill=col)
        bbox2 = draw.textbbox((0, 0), ex, font=f_label)
        ew = bbox2[2] - bbox2[0]
        draw.text((px - ew // 2, py0 + ph + 6), ex, font=f_label, fill=WHITE)
    # Transition arrows
    for ax in [130, 285]:
        draw.line([(ax, py0 + ph // 2), (ax + 50, py0 + ph // 2)], fill=DIM, width=2)
        draw.polygon([(ax + 50, py0 + ph // 2),
                      (ax + 40, py0 + ph // 2 - 5),
                      (ax + 40, py0 + ph // 2 + 5)], fill=DIM)
    draw_text_centered(draw, "États de la matière : l'eau", H - 28, f_title, GOLD)
    save(img, path)


def gen_oscar_l4_m31(path):
    img, draw = new_canvas()
    f_title = find_font(18)
    f_label = find_font(14)
    f_icon = find_font(30)
    draw_text_centered(draw, "CHAÎNE ALIMENTAIRE", 14, find_font(20), GOLD)
    items = [
        ("☀", "Soleil", (255, 215, 0)),
        ("🌿", "Plante", GREEN),
        ("🐇", "Lapin", WHITE),
        ("🦊", "Renard", ORANGE),
    ]
    item_x = [70, 180, 300, 410]
    item_y = H // 2 + 10
    for i, ((icon, label, col), ix) in enumerate(zip(items, item_x)):
        draw.ellipse([ix - 30, item_y - 30, ix + 30, item_y + 30], fill=(20, 20, 60), outline=col, width=2)
        draw.text((ix - 14, item_y - 18), icon, font=f_icon, fill=col)
        bbox = draw.textbbox((0, 0), label, font=f_label)
        lw = bbox[2] - bbox[0]
        draw.text((ix - lw // 2, item_y + 34), label, font=f_label, fill=col)
        if i < len(items) - 1:
            nx = item_x[i + 1]
            draw.line([(ix + 32, item_y), (nx - 32, item_y)], fill=WHITE, width=2)
            draw.polygon([(nx - 32, item_y), (nx - 42, item_y - 5), (nx - 42, item_y + 5)],
                         fill=WHITE)
    save(img, path)


def gen_oscar_l4_m32(path):
    img, draw = new_canvas()
    f_label = find_font(12)
    f_title = find_font(18)
    f_q = find_font(22)
    # Same layout as Romy l4 m26 but with "4 = ?" hint
    draw.ellipse([14, H // 2 - 34, 80, H // 2 + 34], fill=(255, 220, 0), outline=ORANGE, width=2)
    planets = [
        (118, H // 2, 10, (180, 140, 100), "1"),
        (178, H // 2, 14, (220, 160, 80), "2"),
        (250, H // 2, 18, BLUE, "3"),
        (332, H // 2, 15, RED, "4 ?"),
    ]
    names = ["MERCURE", "VÉNUS", "TERRE", "???"]
    for i, ((px, py, r, col, num), name) in enumerate(zip(planets, names)):
        draw.ellipse([px - r, py - r, px + r, py + r], fill=col, outline=WHITE, width=1)
        bbox = draw.textbbox((0, 0), num, font=f_label)
        lw = bbox[2] - bbox[0]
        draw.text((px - lw // 2, py - r - 18), num, font=f_label,
                  fill=GOLD if i == 3 else WHITE)
        bbox2 = draw.textbbox((0, 0), name, font=f_label)
        lw2 = bbox2[2] - bbox2[0]
        draw.text((px - lw2 // 2, py + r + 4), name, font=f_label,
                  fill=GOLD if i == 3 else WHITE)
    draw_text_centered(draw, "Quelle est la 4ème planète ?", H - 42, f_title, GOLD)
    save(img, path)


def gen_oscar_l4_m33(path):
    img, draw = new_canvas()
    f_title = find_font(18)
    f_count = find_font(44)
    f_label = find_font(14)
    cx, cy = W // 2, H // 2 - 10
    r = 72
    # Square
    draw.rectangle([cx - r, cy - r, cx + r, cy + r], fill=(20, 20, 70), outline=TEAL, width=3)
    # 4 axes of symmetry
    # Horizontal
    draw.line([(cx - r - 16, cy), (cx + r + 16, cy)], fill=GOLD, width=2)
    # Vertical
    draw.line([(cx, cy - r - 16), (cx, cy + r + 16)], fill=GOLD, width=2)
    # Diagonal 1
    d = int(r * 0.95)
    draw.line([(cx - d - 10, cy - d - 10), (cx + d + 10, cy + d + 10)], fill=PURPLE, width=2)
    # Diagonal 2
    draw.line([(cx + d + 10, cy - d - 10), (cx - d - 10, cy + d + 10)], fill=PURPLE, width=2)
    # Arrow ends on axes
    for (ax, ay) in [(cx + r + 16, cy), (cx, cy + r + 16)]:
        draw.ellipse([ax - 3, ay - 3, ax + 3, ay + 3], fill=GOLD)
    draw.text((W - 80, 20), "4", font=f_count, fill=GOLD)
    draw.text((W - 72, 72), "axes", font=f_label, fill=GOLD)
    draw_text_centered(draw, "Combien d'axes de symétrie ?", H - 28, f_title, WHITE)
    save(img, path)


def gen_oscar_l4_m34(path):
    img, draw = new_canvas()
    f_title = find_font(20)
    f_name = find_font(42)
    f_sub = find_font(13)
    # Elaborate border
    draw_border(draw, GOLD, 7)
    draw_border(draw, PURPLE, 3)
    draw.rectangle([14, 14, W - 14, H - 14], outline=GOLD, width=1)
    # Stars on border
    rng = random.Random(13)
    for _ in range(18):
        sx = rng.randint(10, W - 10)
        sy = rng.choice([rng.randint(4, 18), rng.randint(H - 18, H - 4)])
        draw_star(draw, sx, sy, 8, GOLD)
    for _ in range(6):
        sx = rng.choice([rng.randint(4, 18), rng.randint(W - 18, W - 4)])
        sy = rng.randint(18, H - 18)
        draw_star(draw, sx, sy, 8, GOLD)
    # Corner trophies
    for (sx, sy) in [(24, 24), (W - 24, 24), (24, H - 24), (W - 24, H - 24)]:
        draw_star(draw, sx, sy, 14, GOLD)
    draw_text_centered(draw, "DIPLÔME DE COMMANDANT", 32, f_title, GOLD)
    draw_text_centered(draw, "OSCAR", 80, f_name, WHITE)
    draw.line([(55, 138), (W - 55, 138)], fill=GOLD, width=2)
    save(img, path)


def generate_all():
    print("Generating Mission Espace illustrations...")
    tasks = [
        # Romy Level 2
        (gen_romy_l2_m09, ROMY_DIR / "romy_l2_m09.png"),
        (gen_romy_l2_m10, ROMY_DIR / "romy_l2_m10.png"),
        (gen_romy_l2_m11, ROMY_DIR / "romy_l2_m11.png"),
        (gen_romy_l2_m12, ROMY_DIR / "romy_l2_m12.png"),
        (gen_romy_l2_m13, ROMY_DIR / "romy_l2_m13.png"),
        (gen_romy_l2_m14, ROMY_DIR / "romy_l2_m14.png"),
        (gen_romy_l2_m15, ROMY_DIR / "romy_l2_m15.png"),
        (gen_romy_l2_m16, ROMY_DIR / "romy_l2_m16.png"),
        # Romy Level 3
        (gen_romy_l3_m17, ROMY_DIR / "romy_l3_m17.png"),
        (gen_romy_l3_m18, ROMY_DIR / "romy_l3_m18.png"),
        (gen_romy_l3_m19, ROMY_DIR / "romy_l3_m19.png"),
        (gen_romy_l3_m20, ROMY_DIR / "romy_l3_m20.png"),
        (gen_romy_l3_m21, ROMY_DIR / "romy_l3_m21.png"),
        (gen_romy_l3_m22, ROMY_DIR / "romy_l3_m22.png"),
        (gen_romy_l3_m23, ROMY_DIR / "romy_l3_m23.png"),
        (gen_romy_l3_m24, ROMY_DIR / "romy_l3_m24.png"),
        # Romy Level 4
        (gen_romy_l4_m25, ROMY_DIR / "romy_l4_m25.png"),
        (gen_romy_l4_m26, ROMY_DIR / "romy_l4_m26.png"),
        (gen_romy_l4_m27, ROMY_DIR / "romy_l4_m27.png"),
        (gen_romy_l4_m28, ROMY_DIR / "romy_l4_m28.png"),
        (gen_romy_l4_m29, ROMY_DIR / "romy_l4_m29.png"),
        (gen_romy_l4_m30, ROMY_DIR / "romy_l4_m30.png"),
        # Oscar Level 2
        (gen_oscar_l2_m10, OSCAR_DIR / "oscar_l2_m10.png"),
        (gen_oscar_l2_m11, OSCAR_DIR / "oscar_l2_m11.png"),
        (gen_oscar_l2_m12, OSCAR_DIR / "oscar_l2_m12.png"),
        (gen_oscar_l2_m13, OSCAR_DIR / "oscar_l2_m13.png"),
        (gen_oscar_l2_m14, OSCAR_DIR / "oscar_l2_m14.png"),
        (gen_oscar_l2_m15, OSCAR_DIR / "oscar_l2_m15.png"),
        (gen_oscar_l2_m16, OSCAR_DIR / "oscar_l2_m16.png"),
        (gen_oscar_l2_m17, OSCAR_DIR / "oscar_l2_m17.png"),
        (gen_oscar_l2_m18, OSCAR_DIR / "oscar_l2_m18.png"),
        # Oscar Level 3
        (gen_oscar_l3_m19, OSCAR_DIR / "oscar_l3_m19.png"),
        (gen_oscar_l3_m20, OSCAR_DIR / "oscar_l3_m20.png"),
        (gen_oscar_l3_m21, OSCAR_DIR / "oscar_l3_m21.png"),
        (gen_oscar_l3_m22, OSCAR_DIR / "oscar_l3_m22.png"),
        (gen_oscar_l3_m23, OSCAR_DIR / "oscar_l3_m23.png"),
        (gen_oscar_l3_m24, OSCAR_DIR / "oscar_l3_m24.png"),
        (gen_oscar_l3_m25, OSCAR_DIR / "oscar_l3_m25.png"),
        (gen_oscar_l3_m26, OSCAR_DIR / "oscar_l3_m26.png"),
        (gen_oscar_l3_m27, OSCAR_DIR / "oscar_l3_m27.png"),
        # Oscar Level 4
        (gen_oscar_l4_m28, OSCAR_DIR / "oscar_l4_m28.png"),
        (gen_oscar_l4_m29, OSCAR_DIR / "oscar_l4_m29.png"),
        (gen_oscar_l4_m30, OSCAR_DIR / "oscar_l4_m30.png"),
        (gen_oscar_l4_m31, OSCAR_DIR / "oscar_l4_m31.png"),
        (gen_oscar_l4_m32, OSCAR_DIR / "oscar_l4_m32.png"),
        (gen_oscar_l4_m33, OSCAR_DIR / "oscar_l4_m33.png"),
        (gen_oscar_l4_m34, OSCAR_DIR / "oscar_l4_m34.png"),
    ]
    errors = 0
    for fn, path in tasks:
        try:
            fn(path)
        except Exception as e:
            print(f"  ✗ {path.name}: {e}")
            errors += 1
    total = len(tasks)
    ok = total - errors
    print(f"\nDone! {ok}/{total} illustrations generated.")
    if errors:
        print(f"  {errors} error(s) — check output above")


if __name__ == "__main__":
    generate_all()
