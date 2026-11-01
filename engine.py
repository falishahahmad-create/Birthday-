"""engine.py - game logic, editable content and Pillow image magic for Birthday Quest.

Everything you will want to personalise lives in CONFIG right below.
"""
from __future__ import annotations

import base64
import io
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

# =============================================================================
# EDIT ME: all the content of the game lives here
# =============================================================================
CONFIG = {
    # Used when the visitor leaves the name box empty.
    "default_name": "Birthday Star",

    # Free audio URL for the background-music toggle. Swap in any direct .mp3 link.
    "music_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",

    # Level 1: how many gift boxes (3 columns) and how many of them hide a photo.
    "gift_count": 9,
    "gift_photo_count": 3,
    "gift_messages": [
        "You make every room brighter just by walking in. 🌷",
        "Coupon: one free hug, redeemable anytime. 🤗",
        "Another year of being wonderfully you. ✨",
        "You deserve cake, naps and all the good things. 🍰",
        "Thank you for being such a cozy person to know. 🧸",
        "May your day be as sweet as frosting. 🧁",
        "Wishing you laughter that makes your cheeks hurt. 😊",
        "You are loved more than you know. 💖",
        "Today the world celebrates you. 🎀",
    ],

    # Level 2: number of pairs (6 pairs = 12 cards).
    "memory_pairs": 6,

    # Captions printed on the polaroid frames (cycled).
    "captions": ["sweet memory", "sunshine day", "so cute", "forever us",
                 "best day", "happy times"],

    # Level 3: five questions. "answer" is the index (starting at 0) of the correct option.
    # {name} is replaced with the birthday person's name.
    "quiz": [
        {"q": "What is {name}'s favourite colour?",
         "options": ["Baby pink", "Ocean blue", "Forest green", "Sunny yellow"], "answer": 0},
        {"q": "Which dessert would {name} pick first?",
         "options": ["Cheesecake", "Chocolate cake", "Ice cream", "Cookies"], "answer": 1},
        {"q": "What is {name}'s dream holiday?",
         "options": ["Beach getaway", "Mountain cabin", "City trip", "Cozy staycation"], "answer": 3},
        {"q": "Which drink is {name}'s go-to?",
         "options": ["Coffee", "Tea", "Bubble tea", "Hot chocolate"], "answer": 2},
        {"q": "What does {name} love doing most on a free day?",
         "options": ["Watching movies", "Reading", "Shopping", "Napping"], "answer": 0},
    ],

    # Final level: the typewriter letter. {name} is replaced with the name.
    "letter": (
        "Dear {name},\n\n"
        "Happy Birthday! Today is all about you, and I hope it is wrapped in "
        "love, laughter and a very big slice of cake.\n\n"
        "Thank you for every smile, every memory and every little moment we have "
        "shared. You make life softer, brighter and so much more fun.\n\n"
        "May this new year bring you gentle mornings, big adventures and every "
        "wish you just made on those candles.\n\n"
        "With all my love,\nYour favourite person"
    ),

    # Short text printed on the downloadable birthday card image.
    "card_message": "Wishing you a day full of love, laughter and cake. "
                    "Thank you for being you, {name}!",

    # Folder (next to app.py) where you can drop photos instead of using the uploader.
    "images_folder": "images",
    "max_photos": 12,
}

COLORS = {
    "beige": "#F5EBDD",
    "pink": "#F7C6D0",
    "brown": "#6F4E37",
    "cream": "#FFF8F0",
    "rose": "#E88AA0",
}

EXTS = {".jpg", ".jpeg", ".png", ".webp"}


def _rgb(hex_color: str) -> tuple[int, int, int]:
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]


BEIGE, PINK, BROWN, CREAM, ROSE = (_rgb(COLORS[k]) for k in
                                   ("beige", "pink", "brown", "cream", "rose"))

# =============================================================================
# Fonts
# =============================================================================
_FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial Rounded Bold.ttf",
    "Arial Bold.ttf",
    "arialbd.ttf",
]


def get_font(size: int) -> ImageFont.ImageFont:
    for path in _FONT_CANDIDATES:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    try:
        return ImageFont.load_default(size=size)
    except TypeError:  # very old Pillow
        return ImageFont.load_default()


# =============================================================================
# Small drawing helpers
# =============================================================================
def heart_points(cx: float, cy: float, width: float, n: int = 90):
    k = width / 34.0
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        x = 16 * math.sin(t) ** 3
        y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        pts.append((cx + x * k, cy - y * k))
    return pts


def star_points(cx, cy, outer, inner, n=5):
    pts = []
    for i in range(n * 2):
        r = outer if i % 2 == 0 else inner
        a = -math.pi / 2 + i * math.pi / n
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def sparkle_points(cx, cy, r):
    q = r * 0.25
    return [(cx, cy - r), (cx + q, cy - q), (cx + r, cy), (cx + q, cy + q),
            (cx, cy + r), (cx - q, cy + q), (cx - r, cy), (cx - q, cy - q)]


def _cover(img: Image.Image, size: tuple[int, int]) -> Image.Image:
    return ImageOps.fit(img.convert("RGB"), size, Image.Resampling.LANCZOS)


def add_shadow(img: Image.Image, offset=(5, 9), blur=12, alpha=95) -> Image.Image:
    """Soft brown drop shadow around an RGBA image."""
    pad = blur * 3
    canvas = Image.new("RGBA", (img.width + pad * 2, img.height + pad * 2), BROWN + (0,))
    shadow = Image.new("RGBA", img.size, BROWN + (255,))
    shadow.putalpha(img.split()[3].point(lambda a: int(a * alpha / 255)))
    canvas.paste(shadow, (pad + offset[0], pad + offset[1]), shadow)
    canvas = canvas.filter(ImageFilter.GaussianBlur(blur))
    canvas.alpha_composite(img, (pad, pad))
    return canvas


def to_data_uri(img: Image.Image, quality: int = 82) -> str:
    """PIL image -> base64 data URI (WEBP when transparent, JPEG otherwise)."""
    buf = io.BytesIO()
    if img.mode in ("RGBA", "LA", "P"):
        img.convert("RGBA").save(buf, "WEBP", quality=quality)
        mime = "image/webp"
    else:
        img.convert("RGB").save(buf, "JPEG", quality=quality, optimize=True)
        mime = "image/jpeg"
    return f"data:{mime};base64," + base64.b64encode(buf.getvalue()).decode()


# =============================================================================
# Sample photos (used when nothing is uploaded)
# =============================================================================
_PALETTES = [
    ("#F7C6D0", "#F5EBDD"), ("#F5EBDD", "#E9B8A6"), ("#FBD9E0", "#F2D4B7"),
    ("#F9E1D0", "#F7C6D0"), ("#EBD3C0", "#F7C6D0"), ("#FCE4EC", "#F5EBDD"),
]


def make_sample(i: int, size: int = 640) -> Image.Image:
    """Cute generated 'photo' so the app looks lovely with zero uploads."""
    s = size * 2
    c1, c2 = (_rgb(c) for c in _PALETTES[i % len(_PALETTES)])
    mask = Image.linear_gradient("L").resize((s, s))
    img = Image.composite(Image.new("RGB", (s, s), c2), Image.new("RGB", (s, s), c1), mask)
    d = ImageDraw.Draw(img)
    cx = cy = s // 2
    deep = (232, 138, 160)
    kind = i % 6
    if kind == 0:  # heart
        pts = heart_points(cx, cy, s * 0.55)
        d.polygon(pts, fill=deep)
        d.line(pts + [pts[0]], fill=BROWN, width=10)
    elif kind == 1:  # star
        pts = star_points(cx, cy, s * 0.3, s * 0.13)
        d.polygon(pts, fill=(247, 214, 120))
        d.line(pts + [pts[0]], fill=BROWN, width=10)
    elif kind == 2:  # flower
        r, pr = s * 0.17, s * 0.13
        for a in range(6):
            ang = a * math.pi / 3
            x, y = cx + r * math.cos(ang), cy + r * math.sin(ang)
            d.ellipse((x - pr, y - pr, x + pr, y + pr), fill=deep, outline=BROWN, width=8)
        d.ellipse((cx - s * .08, cy - s * .08, cx + s * .08, cy + s * .08),
                  fill=(247, 214, 120), outline=BROWN, width=8)
    elif kind == 3:  # cake
        d.rectangle((cx - .28 * s, cy, cx + .28 * s, cy + .26 * s), fill=(201, 154, 116), outline=BROWN, width=8)
        d.rectangle((cx - .18 * s, cy - .18 * s, cx + .18 * s, cy), fill=PINK, outline=BROWN, width=8)
        for k in range(7):
            x = cx - .28 * s + k * (.56 * s / 6)
            d.ellipse((x - .04 * s, cy - .03 * s, x + .04 * s, cy + .05 * s), fill=PINK, outline=BROWN, width=5)
        d.rectangle((cx - .015 * s, cy - .3 * s, cx + .015 * s, cy - .18 * s), fill=(247, 214, 120), outline=BROWN, width=4)
        d.ellipse((cx - .025 * s, cy - .38 * s, cx + .025 * s, cy - .3 * s), fill=(250, 160, 80))
    elif kind == 4:  # balloon
        d.line([(cx, cy + .12 * s), (cx - .05 * s, cy + .25 * s), (cx + .04 * s, cy + .35 * s)], fill=BROWN, width=8)
        d.ellipse((cx - .2 * s, cy - .3 * s, cx + .2 * s, cy + .12 * s), fill=deep, outline=BROWN, width=8)
        d.polygon([(cx, cy + .11 * s), (cx - .03 * s, cy + .16 * s), (cx + .03 * s, cy + .16 * s)], fill=BROWN)
        d.ellipse((cx - .12 * s, cy - .22 * s, cx - .06 * s, cy - .12 * s), fill=(255, 225, 232))
    else:  # bow
        d.polygon([(cx, cy), (cx - .3 * s, cy - .2 * s), (cx - .3 * s, cy + .2 * s)], fill=deep, outline=BROWN)
        d.polygon([(cx, cy), (cx + .3 * s, cy - .2 * s), (cx + .3 * s, cy + .2 * s)], fill=deep, outline=BROWN)
        d.polygon([(cx - .04 * s, cy + .04 * s), (cx - .12 * s, cy + .3 * s), (cx - .02 * s, cy + .24 * s)], fill=PINK, outline=BROWN)
        d.polygon([(cx + .04 * s, cy + .04 * s), (cx + .12 * s, cy + .3 * s), (cx + .02 * s, cy + .24 * s)], fill=PINK, outline=BROWN)
        d.ellipse((cx - .07 * s, cy - .07 * s, cx + .07 * s, cy + .07 * s), fill=PINK, outline=BROWN, width=8)
    for fx, fy in [(.15, .18), (.82, .22), (.2, .8), (.8, .75)]:
        d.polygon(sparkle_points(fx * s, fy * s, .05 * s), fill=(255, 250, 240))
    return img.resize((size, size), Image.Resampling.LANCZOS)


# =============================================================================
# Loading photos
# =============================================================================
def _prep(im: Image.Image, max_side: int = 1400) -> Image.Image:
    im = ImageOps.exif_transpose(im).convert("RGB")
    im.thumbnail((max_side, max_side))
    return im


def _folder_files(folder: str) -> list[Path]:
    p = Path(__file__).parent / folder
    if not p.is_dir():
        return []
    return [f for f in sorted(p.iterdir()) if f.suffix.lower() in EXTS]


def photos_signature(uploaded_files, folder: str | None = None) -> tuple:
    folder = folder or CONFIG["images_folder"]
    up = tuple((f.name, f.size) for f in (uploaded_files or []))
    fo = tuple((f.name, int(f.stat().st_mtime)) for f in _folder_files(folder))
    return up + fo


def load_photos(uploaded_files=None, folder: str | None = None) -> tuple[list[Image.Image], bool]:
    """Return (photos, using_samples). Uploads first, then images/ folder, else samples."""
    folder = folder or CONFIG["images_folder"]
    photos: list[Image.Image] = []
    for f in uploaded_files or []:
        try:
            data = f.getvalue() if hasattr(f, "getvalue") else f
            photos.append(_prep(Image.open(io.BytesIO(data))))
        except Exception:
            continue
    for fp in _folder_files(folder):
        try:
            photos.append(_prep(Image.open(fp)))
        except Exception:
            continue
    if photos:
        return photos[: CONFIG["max_photos"]], False
    return [make_sample(i) for i in range(6)], True


# =============================================================================
# Pillow effects
# =============================================================================
def polaroid(img: Image.Image, caption: str = "", size: int = 320, angle: float = 0,
             shadow: bool = True) -> Image.Image:
    """Polaroid frame with a baby-pink border, cream paper and a handwritten-ish caption."""
    pad = max(10, int(size * 0.07))
    bottom = max(34, int(size * 0.22))
    edge = max(4, int(pad * 0.4))
    photo = _cover(img, (size, size))
    w, h = size + 2 * pad, size + pad + bottom
    card = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(card)
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=16, fill=PINK)
    d.rounded_rectangle((edge, edge, w - edge - 1, h - edge - 1), radius=12, fill=CREAM)
    card.paste(photo, (pad, pad))
    if caption:
        font = get_font(max(13, size // 14))
        tw = d.textlength(caption, font=font)
        d.text(((w - tw) / 2, size + pad + bottom * 0.28), caption, font=font, fill=BROWN)
    else:
        d.polygon(heart_points(w / 2, size + pad + bottom * 0.5, bottom * 0.4), fill=ROSE)
    if angle:
        card = card.rotate(angle, expand=True, resample=Image.Resampling.BICUBIC)
    return add_shadow(card) if shadow else card


def circle_avatar(img: Image.Image, size: int = 300) -> Image.Image:
    """Circular profile picture with a pink ring."""
    sq = _cover(img, (size, size)).convert("RGBA")
    big = Image.new("L", (size * 4, size * 4), 0)
    ImageDraw.Draw(big).ellipse((0, 0, size * 4 - 1, size * 4 - 1), fill=255)
    mask = big.resize((size, size), Image.Resampling.LANCZOS)
    out = Image.new("RGBA", (size + 24, size + 24), (0, 0, 0, 0))
    d = ImageDraw.Draw(out)
    d.ellipse((0, 0, size + 23, size + 23), fill=PINK)
    d.ellipse((6, 6, size + 17, size + 17), fill=CREAM)
    out.paste(sq, (12, 12), mask)
    return out


def blurred_bg(photos: list[Image.Image], size=(1000, 700), tint=PINK, strength=0.6,
               radius: int = 28) -> Image.Image:
    """Blurred, theme-tinted background made from up to three photos."""
    W, H = size
    tint = _rgb(tint) if isinstance(tint, str) else tint
    base = Image.new("RGB", size, BEIGE)
    use = photos[:3]
    if use:
        part = W // len(use)
        for i, p in enumerate(use):
            base.paste(_cover(p, (part + 2, H)), (i * part, 0))
        base = base.filter(ImageFilter.GaussianBlur(radius))
    return Image.blend(base, Image.new("RGB", size, tint), strength)


def grid_for(n: int) -> tuple[int, int]:
    cols = min(4, max(2, math.ceil(math.sqrt(n))))
    rows = max(1, math.ceil(n / cols))
    return cols, rows


def scrapbook(photos: list[Image.Image], size=(1200, 900), cols: int = 3, rows: int = 2,
              seed: int = 7, captions: list[str] | None = None) -> Image.Image:
    """Scrapbook collage of tilted polaroids over a soft tinted background, with hearts."""
    rnd = random.Random(seed)
    W, H = size
    bg = blurred_bg(photos, size, tint=BEIGE, strength=0.72)
    cw, ch = W / cols, H / rows
    side = max(80, int(min(cw - 40, ch - 100) * 1.05))
    caps = captions or [""]
    order = list(range(cols * rows))
    rnd.shuffle(order)
    for k in order:
        pol = polaroid(photos[k % len(photos)], caps[k % len(caps)], size=side,
                       angle=rnd.uniform(-10, 10))
        cx = (k % cols + 0.5) * cw + rnd.uniform(-cw * .05, cw * .05)
        cy = (k // cols + 0.5) * ch + rnd.uniform(-ch * .05, ch * .05)
        bg.paste(pol, (int(cx - pol.width / 2), int(cy - pol.height / 2)), pol)
    d = ImageDraw.Draw(bg)
    for _ in range(cols * rows * 2):
        x, y = rnd.uniform(0, W), rnd.uniform(0, H)
        if rnd.random() < 0.5:
            d.polygon(heart_points(x, y, rnd.uniform(18, 34)), fill=ROSE)
        else:
            d.polygon(sparkle_points(x, y, rnd.uniform(9, 17)), fill=CREAM)
    return bg


def _wrap(d: ImageDraw.ImageDraw, text: str, font, max_w: float) -> list[str]:
    lines: list[str] = []
    for para in text.split("\n"):
        cur = ""
        for word in para.split():
            trial = (cur + " " + word).strip()
            if d.textlength(trial, font=font) <= max_w:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        lines.append(cur)
    return lines


def _center(d, text, y, font, fill, W):
    tw = d.textlength(text, font=font)
    d.text(((W - tw) / 2, y), text, font=font, fill=fill)


def birthday_card(name: str, photos: list[Image.Image], message: str,
                  size=(1080, 1500)) -> bytes:
    """Themed birthday card as PNG bytes."""
    W, H = size
    img = blurred_bg(photos, size, tint=PINK, strength=0.72).convert("RGBA")
    # soft shadow + card
    sh = Image.new("RGBA", size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((70, 84, W - 50, H - 36), radius=60, fill=BROWN + (110,))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(18)))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((60, 60, W - 60, H - 60), radius=60, fill=CREAM, outline=PINK, width=14)
    d.rounded_rectangle((92, 92, W - 92, H - 92), radius=44, outline=BROWN, width=3)

    font = get_font(104)
    while d.textlength("Happy Birthday!", font=font) > W - 380 and font.size > 40:
        font = get_font(font.size - 6)
    _center(d, "Happy Birthday!", 150, font, BROWN, W)
    nfont = get_font(78)
    while d.textlength(name, font=nfont) > W - 260 and nfont.size > 30:
        nfont = get_font(nfont.size - 6)
    _center(d, name, 285, nfont, ROSE, W)
    for i in range(5):
        d.polygon(heart_points(W / 2 + (i - 2) * 70, 410, 38), fill=ROSE if i % 2 else PINK)

    av = circle_avatar(photos[0], 250)
    img.alpha_composite(av, ((W - av.width) // 2, 450))

    angles = [-7, 3, 7]
    n = min(3, len(photos)) if len(photos) >= 3 else 3
    for i in range(n):
        pol = polaroid(photos[(i + 1) % len(photos)], "", size=200, angle=angles[i])
        x = int(W * (i + 1) / (n + 1) - pol.width / 2)
        img.alpha_composite(pol, (x, 760))

    d = ImageDraw.Draw(img)
    mfont = get_font(38)
    lines = _wrap(d, message.replace("{name}", name), mfont, W - 300)[:4]
    y = 1200
    for ln in lines:
        _center(d, ln, y, mfont, BROWN, W)
        y += 52
    for fx in (150, W - 150):
        d.polygon(sparkle_points(fx, 170, 28), fill=PINK)
        d.polygon(sparkle_points(fx, H - 170, 28), fill=PINK)
    buf = io.BytesIO()
    img.convert("RGB").save(buf, "PNG")
    return buf.getvalue()


# =============================================================================
# Game logic
# =============================================================================
def build_gifts(count: int, n_photos: int, seed: int | None = None) -> list[dict]:
    rnd = random.Random(seed)
    n_photo = min(CONFIG["gift_photo_count"], count) if n_photos else 0
    msgs = CONFIG["gift_messages"]
    gifts = [{"kind": "photo", "idx": i % max(1, n_photos)} for i in range(n_photo)]
    gifts += [{"kind": "msg", "text": msgs[i % len(msgs)]} for i in range(count - n_photo)]
    rnd.shuffle(gifts)
    return gifts


def build_memory(pairs: int, n_photos: int, seed: int | None = None) -> dict:
    rnd = random.Random(seed)
    deck = [{"pair": p, "photo": p % max(1, n_photos)} for p in range(pairs)] * 2
    rnd.shuffle(deck)
    return {"deck": deck, "flipped": [], "matched": [], "moves": 0}


def memory_flip(mem: dict, i: int) -> str:
    """Flip card i. Returns 'ignored', 'first', 'match' or 'miss'."""
    if i in mem["matched"] or i in mem["flipped"]:
        return "ignored"
    if len(mem["flipped"]) == 2:  # previous mismatch gets hidden again
        mem["flipped"] = []
    mem["flipped"].append(i)
    if len(mem["flipped"]) == 2:
        mem["moves"] += 1
        a, b = mem["flipped"]
        if mem["deck"][a]["pair"] == mem["deck"][b]["pair"]:
            mem["matched"] += [a, b]
            mem["flipped"] = []
            return "match"
        return "miss"
    return "first"


def memory_stars(moves: int, pairs: int) -> int:
    if moves <= pairs + 3:
        return 3
    if moves <= pairs * 2:
        return 2
    return 1


def quiz_stars(correct: int, total: int) -> int:
    if total == 0 or correct == 0:
        return 0
    ratio = correct / total
    return 3 if ratio >= 1 else 2 if ratio >= 0.6 else 1


def compute_score(p: dict) -> dict:
    """p keys: gifts_opened, gifts_total, pairs_matched, pairs_total, memory_moves,
    quiz_correct, quiz_total, quiz_finished, candles_blown."""
    gifts, gt = p["gifts_opened"], p["gifts_total"]
    pairs, pt = p["pairs_matched"], p["pairs_total"]
    qc, qt = p["quiz_correct"], p["quiz_total"]
    stars = round(3 * gifts / gt) if gt else 0
    if pt and pairs >= pt:
        stars += memory_stars(p["memory_moves"], pt)
    if p.get("quiz_finished"):
        stars += quiz_stars(qc, qt)
    if p["candles_blown"]:
        stars += 1
    points = gifts * 10 + pairs * 20 + qc * 30 + (50 if p["candles_blown"] else 0)
    badges = []
    if gt and gifts >= gt:
        badges.append("🎁 Gift Hunter")
    if pt and pairs >= pt:
        badges.append("🧠 Memory Maestro")
    if p.get("quiz_finished") and qt and qc >= math.ceil(qt * 0.8):
        badges.append("🍰 Cake Master")
    if p.get("quiz_finished") and qt and qc == qt:
        badges.append("💯 Perfect Pal")
    if p["candles_blown"]:
        badges.append("🕯️ Wish Maker")
    if len(badges) >= 4 and p["candles_blown"]:
        badges.append("🎀 Birthday Legend")
    return {"stars": stars, "hearts": gifts + pairs, "points": points, "badges": badges}
