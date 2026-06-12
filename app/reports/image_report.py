"""Vertical phone-friendly summary image via Pillow."""

from datetime import date
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from app.services.cfo_service import CfoSummary

IMAGE_DIR = Path(__file__).parent / "generated" / "images"
WIDTH, HEIGHT = 1080, 1920
BG = (16, 18, 24)
FG = (235, 235, 235)
ACCENT = (22, 163, 74)
WARN = (220, 80, 60)


def image_path_for(day: date) -> Path:
    return IMAGE_DIR / f"badger_cfo_{day.strftime('%Y_%m_%d')}.png"


def _font(size: int):
    for name in ("DejaVuSans-Bold.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def generate_image(
    summary: CfoSummary,
    top_actions: list[str] | None = None,
    risk_level: str = "low",
    day: date | None = None,
) -> Path:
    day = day or date.today()
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    path = image_path_for(day)

    img = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(img)

    title_font = _font(64)
    label_font = _font(40)
    value_font = _font(56)
    small_font = _font(34)

    y = 80
    draw.text((60, y), "BADGER CFO", font=title_font, fill=ACCENT)
    y += 90
    draw.text((60, y), day.isoformat(), font=small_font, fill=FG)
    y += 90

    rows = [
        ("Net Worth", f"${summary.net_worth:,.0f}"),
        ("Cash Available", f"${summary.available_cash:,.0f}"),
        ("Today Free Cash", f"${summary.today_free_cash:,.0f}"),
        ("Upcoming Payments (14d)", f"${summary.upcoming_obligations_total:,.0f}"),
        ("Crypto Portfolio", f"${summary.total_crypto:,.0f}"),
        ("Freedom Ratio", f"{summary.freedom_ratio * 100:.1f}%"),
    ]
    for label, value in rows:
        draw.text((60, y), label, font=label_font, fill=(150, 155, 165))
        y += 55
        draw.text((60, y), value, font=value_font, fill=FG)
        y += 110

    risk_color = WARN if risk_level == "high" else ACCENT if risk_level == "low" else (230, 180, 60)
    draw.text((60, y), "Risk Level", font=label_font, fill=(150, 155, 165))
    y += 55
    draw.text((60, y), risk_level.upper(), font=value_font, fill=risk_color)
    y += 120

    draw.text((60, y), "Top 3 Actions", font=label_font, fill=(150, 155, 165))
    y += 65
    for action in (top_actions or ["Save", "Track", "Hold the line"])[:3]:
        draw.text((60, y), f"• {action[:48]}", font=small_font, fill=FG)
        y += 55

    img.save(path)
    return path
