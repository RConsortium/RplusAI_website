#!/usr/bin/env python3
"""Generate R+AI speaker cards for social media.

Layout: brand R+AI hexagon (left) · text (center) · speaker headshot hexagon (right).

Usage:
  .venv-speaker-cards/bin/python scripts/make_speaker_card.py \\
    --headshot images/joseph-barbier.jpg \\
    --name "Joseph Barbier" \\
    --title "Yellow Sunflower" \\
    --talk "50 lines of code to rebuild Claude Code in R" \\
    --when "November 10 · 10:05 AM Eastern" \\
    --output images/speaker-cards/joseph-barbier.png
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TEMPLATE = ROOT / "images" / "RplusAI-main-image-no-text.png"

# Pointy-top hexagons on the 1024×576 brand template
# Brand mark outer bbox measured from template: 218×251 centered at (186, 287.5)
BRAND_HEX_CENTER = (186, 288)
SPEAKER_HEX_CENTER = (1024 - BRAND_HEX_CENTER[0], BRAND_HEX_CENTER[1])  # exact mirror
HEX_OUTER_RADIUS = 126  # half of brand outer height (251)
HEX_BORDER = 13  # match brand outline (outer edge − gold fill ≈ 12–13px)
# Horizontal inset of pointy-top hex ≈ radius * √3 / 2
HEX_HALF_WIDTH = HEX_OUTER_RADIUS * math.sqrt(3) / 2

GOLD = (212, 154, 50)
WHITE = (255, 255, 255)
SOFT_WHITE = (245, 240, 230)


def pointy_hexagon(cx: float, cy: float, radius: float) -> list[tuple[float, float]]:
    """Regular pointy-top hexagon vertices."""
    return [
        (
            cx + radius * math.sin(math.radians(angle)),
            cy - radius * math.cos(math.radians(angle)),
        )
        for angle in range(0, 360, 60)
    ]


def load_font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size=size)


def wrap_text(
    text: str, font: ImageFont.ImageFont, max_width: int, draw: ImageDraw.ImageDraw
) -> list[str]:
    words = text.split()
    if not words:
        return []
    lines: list[str] = []
    current = words[0]
    for word in words[1:]:
        trial = f"{current} {word}"
        if draw.textlength(trial, font=font) <= max_width:
            current = trial
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def cover_face(headshot: Image.Image, size: int) -> Image.Image:
    """Center-crop to square, slightly biased upward for portraits, then resize."""
    w, h = headshot.size
    side = min(w, h)
    left = (w - side) // 2
    top = max(0, int((h - side) * 0.15))
    if top + side > h:
        top = h - side
    cropped = headshot.crop((left, top, left + side, top + side))
    return cropped.resize((size, size), Image.Resampling.LANCZOS)


def make_hex_portrait(
    headshot: Image.Image,
    outer_radius: int,
    border: int,
    nudge_y: int = 0,
    fill_rgb: tuple[int, int, int] | None = None,
) -> Image.Image:
    diameter = outer_radius * 2
    inner_radius = outer_radius - border

    canvas = Image.new("RGBA", (diameter, diameter), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)

    outer = pointy_hexagon(outer_radius, outer_radius, outer_radius)
    draw.polygon(outer, fill=WHITE + (255,))

    photo = cover_face(headshot.convert("RGB"), diameter).convert("RGBA")
    if nudge_y:
        # Shift portrait down within the hex; fill revealed top with brand mustard
        # (or a sampled edge color) so the tip isn't empty/transparent.
        fill = fill_rgb or photo.getpixel((diameter // 2, 2))[:3]
        layer = Image.new("RGBA", (diameter, diameter), fill + (255,))
        layer.paste(photo, (0, nudge_y), photo)
        photo = layer

    mask = Image.new("L", (diameter, diameter), 0)
    mask_draw = ImageDraw.Draw(mask)
    inner = pointy_hexagon(outer_radius, outer_radius, inner_radius)
    mask_draw.polygon(inner, fill=255)

    hex_photo = Image.new("RGBA", (diameter, diameter), (0, 0, 0, 0))
    hex_photo.paste(photo, (0, 0), mask)
    canvas.paste(hex_photo, (0, 0), hex_photo)
    return canvas


def fit_font(
    path: str,
    text: str,
    max_width: int,
    draw: ImageDraw.ImageDraw,
    max_size: int,
    min_size: int,
) -> ImageFont.FreeTypeFont:
    for size in range(max_size, min_size - 1, -1):
        font = load_font(path, size)
        if draw.textlength(text, font=font) <= max_width:
            return font
    return load_font(path, min_size)


def draw_speaker_text(
    base: Image.Image,
    name: str,
    title: str,
    talk: str,
    when: str,
    badge: str | None = None,
) -> None:
    draw = ImageDraw.Draw(base)
    bold = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
    regular = "/System/Library/Fonts/Supplemental/Arial.ttf"

    pad_left = 40  # clearance from R+AI hexagon
    pad_right = 22
    text_left = int(BRAND_HEX_CENTER[0] + HEX_HALF_WIDTH + pad_left)
    text_right = int(SPEAKER_HEX_CENTER[0] - HEX_HALF_WIDTH - pad_right)
    max_width = text_right - text_left
    # Pull text in from band edges (rules ~117 / ~458); center without stretching
    band_top = 148
    band_bottom = 427
    available = band_bottom - band_top

    name_font = fit_font(bold, name, max_width, draw, max_size=36, min_size=22)
    title_font = fit_font(regular, title, max_width, draw, max_size=20, min_size=14)
    meta_font = fit_font(regular, when, max_width, draw, max_size=18, min_size=13)

    badge_font = load_font(bold, 15)
    badge_pad_x, badge_pad_y = 12, 5
    badge_h = badge_font.size + 2 * badge_pad_y if badge else 0
    gap_badge_name = 14 if badge else 0

    # Largest talk title that still fits in the band with other lines
    talk_font = load_font(bold, 34)
    talk_lines: list[str] = []
    gap_name_aff = 8
    gap_aff_talk = 28
    gap_talk_when = 28
    talk_line_gap = 8

    for size in range(36, 20, -1):
        talk_font = load_font(bold, size)
        talk_lines = wrap_text(talk, talk_font, max_width, draw)
        if len(talk_lines) > 5:
            continue
        talk_line_h = talk_font.size + talk_line_gap
        block = (
            badge_h
            + gap_badge_name
            + name_font.size
            + gap_name_aff
            + title_font.size
            + gap_aff_talk
            + len(talk_lines) * talk_line_h
            + gap_talk_when
            + meta_font.size
        )
        if block <= available:
            break
    else:
        talk_lines = wrap_text(talk, talk_font, max_width, draw)[:5]
        if len(talk_lines) == 5:
            talk_lines[-1] = talk_lines[-1].rstrip(".,;:") + "…"

    talk_line_h = talk_font.size + talk_line_gap
    block_height = (
        badge_h
        + gap_badge_name
        + name_font.size
        + gap_name_aff
        + title_font.size
        + gap_aff_talk
        + len(talk_lines) * talk_line_h
        + gap_talk_when
        + meta_font.size
    )
    y = band_top + max(0, (available - block_height) // 2)

    if badge:
        badge_w = int(draw.textlength(badge, font=badge_font)) + 2 * badge_pad_x
        draw.rounded_rectangle(
            (text_left, y, text_left + badge_w, y + badge_h), radius=4, fill=GOLD
        )
        draw.text(
            (text_left + badge_pad_x, y + badge_pad_y - 1),
            badge,
            font=badge_font,
            fill=(30, 22, 10),
        )
        y += badge_h + gap_badge_name

    draw.text((text_left, y), name, font=name_font, fill=WHITE)
    y += name_font.size + gap_name_aff
    draw.text((text_left, y), title, font=title_font, fill=GOLD)
    y += title_font.size + gap_aff_talk

    for line in talk_lines:
        draw.text((text_left, y), line, font=talk_font, fill=SOFT_WHITE)
        y += talk_line_h
    y += gap_talk_when - talk_line_gap

    draw.text((text_left, y), when, font=meta_font, fill=WHITE)


def generate_card(
    template_path: Path,
    headshot_path: Path,
    name: str,
    title: str,
    talk: str,
    when: str,
    output_path: Path,
    portrait_nudge_y: int = 0,
    badge: str | None = None,
) -> Path:
    base = Image.open(template_path).convert("RGBA")
    headshot = Image.open(headshot_path)
    portrait = make_hex_portrait(
        headshot,
        HEX_OUTER_RADIUS,
        HEX_BORDER,
        nudge_y=portrait_nudge_y,
        fill_rgb=GOLD if portrait_nudge_y else None,
    )

    paste_xy = (
        SPEAKER_HEX_CENTER[0] - HEX_OUTER_RADIUS,
        SPEAKER_HEX_CENTER[1] - HEX_OUTER_RADIUS,
    )
    base.paste(portrait, paste_xy, portrait)

    rgb = base.convert("RGB")
    draw_speaker_text(
        rgb, name=name, title=title, talk=talk, when=when, badge=badge
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    rgb.save(output_path, "PNG", optimize=True)
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Create an R+AI speaker social card")
    parser.add_argument("--template", type=Path, default=DEFAULT_TEMPLATE)
    parser.add_argument("--headshot", type=Path, required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--title", required=True, help="Role / affiliation")
    parser.add_argument("--talk", required=True, help="Talk title")
    parser.add_argument("--when", required=True, help="Date and time line")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--portrait-nudge-y",
        type=int,
        default=0,
        help="Shift headshot down within the hexagon (pixels), filling the top with mustard",
    )
    parser.add_argument(
        "--badge",
        default=None,
        help='Optional label above the speaker name, e.g. "OPENING KEYNOTE"',
    )
    args = parser.parse_args()

    path = generate_card(
        template_path=args.template,
        headshot_path=args.headshot,
        name=args.name,
        title=args.title,
        talk=args.talk,
        when=args.when,
        output_path=args.output,
        portrait_nudge_y=args.portrait_nudge_y,
        badge=args.badge,
    )
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
