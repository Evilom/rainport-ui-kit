#!/usr/bin/env python3
"""Generate the Rainport UI kit from the engine-neutral token source."""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
TOKENS_PATH = ROOT / "tokens" / "rainport.tokens.json"
TOKENS = json.loads(TOKENS_PATH.read_text(encoding="utf-8"))


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value.rstrip() + "\n", encoding="utf-8", newline="\n")


def write_json(path: Path, value: object) -> None:
    write_text(path, json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True))


def color(name: str) -> str:
    return TOKENS["color"][name]["value"]


def rgba(name: str) -> tuple[int, int, int, int]:
    value = color(name).lstrip("#")
    return tuple(int(value[index : index + 2], 16) for index in (0, 2, 4)) + (255,)


def godot_color(name: str) -> str:
    red, green, blue, _ = rgba(name)
    return f"Color({red / 255:.6f}, {green / 255:.6f}, {blue / 255:.6f}, 1)"


def svg_document(width: int, height: int, body: str) -> str:
    return f"""<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"{width}\" height=\"{height}\" viewBox=\"0 0 {width} {height}\">
  {body.strip()}
</svg>
"""


def panel_svg(fill: str, shadow: str, accent: str | None = None) -> str:
    accent_markup = ""
    if accent:
        accent_markup = f'<path d="M14 17H65V25H14Z" fill="{accent}" stroke="{color("ink")}" stroke-width="3"/>'
    return svg_document(
        128,
        128,
        f"""
<rect x="12" y="12" width="108" height="108" rx="7" fill="{shadow}" stroke="{color('ink')}" stroke-width="3"/>
<rect x="5" y="5" width="108" height="108" rx="7" fill="{fill}" stroke="{color('ink')}" stroke-width="3"/>
{accent_markup}
""",
    )


def button_svg(fill: str, state: str = "normal") -> str:
    positions = {
        "normal": (5, 5, 7, 7),
        "hover": (3, 3, 9, 9),
        "pressed": (8, 8, 2, 2),
    }
    x, y, shadow_x, shadow_y = positions[state]
    return svg_document(
        160,
        64,
        f"""
<rect x="{x + shadow_x}" y="{y + shadow_y}" width="142" height="46" rx="3" fill="{color('ink')}"/>
<rect x="{x}" y="{y}" width="142" height="46" rx="3" fill="{fill}" stroke="{color('ink')}" stroke-width="3"/>
<path d="M{x + 14} {y + 34}H{x + 60}" stroke="{color('ink')}" stroke-width="3" stroke-dasharray="7 5"/>
""",
    )


def alert_svg() -> str:
    return svg_document(
        192,
        96,
        f"""
<rect x="12" y="12" width="174" height="76" fill="{color('ink')}"/>
<rect x="4" y="4" width="174" height="76" fill="{color('danger')}" stroke="{color('ink')}" stroke-width="3"/>
<rect x="16" y="17" width="44" height="44" transform="rotate(-3 38 39)" fill="{color('signal')}" stroke="{color('ink')}" stroke-width="3"/>
<path d="M38 27V45M38 52V55" stroke="{color('ink')}" stroke-width="5"/>
<path d="M74 24H157M74 39H166M74 55H142" stroke="{color('white')}" stroke-width="5"/>
""",
    )


def tag_svg(fill: str) -> str:
    return svg_document(
        112,
        48,
        f"""
<rect x="9" y="9" width="96" height="30" fill="{color('ink')}"/>
<rect x="4" y="4" width="96" height="30" fill="{fill}" stroke="{color('ink')}" stroke-width="3"/>
<path d="M16 19H63" stroke="{color('ink')}" stroke-width="4"/>
""",
    )


def receipt_svg() -> str:
    return svg_document(
        176,
        208,
        f"""
<path d="M13 12H169V188L161 196L153 188L145 196L137 188L129 196L121 188L113 196L105 188L97 196L89 188L81 196L73 188L65 196L57 188L49 196L41 188L33 196L25 188L13 196Z" fill="{color('ink')}"/>
<path d="M5 4H161V180L153 188L145 180L137 188L129 180L121 188L113 180L105 188L97 180L89 188L81 180L73 188L65 180L57 188L49 180L41 188L33 180L25 188L17 180L5 188Z" fill="{color('white')}" stroke="{color('ink')}" stroke-width="3"/>
<path d="M24 30H142M24 45H118" stroke="{color('ink')}" stroke-width="5"/>
<path d="M24 68H142M24 88H142M24 108H142M24 128H142" stroke="{color('muted')}" stroke-width="2" stroke-dasharray="8 6"/>
<path d="M24 151H142" stroke="{color('ink')}" stroke-width="4"/>
""",
    )


def stripe_svg() -> str:
    stripes = []
    for x in range(-20, 120, 24):
        stripes.append(f'<path d="M{x} 18L{x + 14} 2H{x + 30}L{x + 16} 18Z" fill="{color("ink")}"/>')
    return svg_document(
        96,
        20,
        f'<rect width="96" height="20" fill="{color("signal")}"/><g>{"".join(stripes)}</g><path d="M0 1H96M0 19H96" stroke="{color("ink")}" stroke-width="2"/>',
    )


def grain_svg() -> str:
    dots = []
    for index in range(34):
        x = (index * 37 + 11) % 128
        y = (index * 53 + 17) % 128
        radius = 1 if index % 3 else 1.5
        opacity = 0.08 if index % 2 else 0.12
        dots.append(f'<circle cx="{x}" cy="{y}" r="{radius}" fill="{color("ink")}" opacity="{opacity}"/>')
    return svg_document(
        128,
        128,
        f'<rect width="128" height="128" fill="{color("paper")}"/>{"".join(dots)}<path d="M-20 44L44 -20M12 140L140 12M84 148L148 84" stroke="{color("ink")}" stroke-width="1" opacity="0.035"/>',
    )


def icon_svg(geometry: str, accent: str = "") -> str:
    return svg_document(
        64,
        64,
        f"""
<g transform="translate(4 4)" fill="{color('rain')}" stroke="{color('ink')}" stroke-width="3" stroke-linecap="square" stroke-linejoin="round">{geometry}</g>
<g fill="{color('white')}" stroke="{color('ink')}" stroke-width="3" stroke-linecap="square" stroke-linejoin="round">{geometry}</g>
<g fill="{color('signal')}" stroke="{color('ink')}" stroke-width="2.5" stroke-linecap="square" stroke-linejoin="round">{accent}</g>
""",
    )


ICON_GEOMETRY = {
    "icon_alert": (
        '<path d="M32 8L57 53H7Z"/><path d="M32 22V37M32 44V47" fill="none"/>',
        '<rect x="49" y="7" width="8" height="8" transform="rotate(5 53 11)"/>',
    ),
    "icon_clock": (
        '<circle cx="32" cy="32" r="23"/><path d="M32 18V33L43 40" fill="none"/><path d="M20 8H44" fill="none"/>',
        '<rect x="8" y="43" width="10" height="10" transform="rotate(-6 13 48)"/>',
    ),
    "icon_budget": (
        '<path d="M9 19H51V49H9Z"/><path d="M37 28H57V42H37Z"/><circle cx="44" cy="35" r="2" fill="none"/>',
        '<circle cx="16" cy="15" r="7"/>',
    ),
    "icon_dry": (
        '<path d="M32 7C32 7 16 26 16 39C16 49 23 56 32 56C41 56 48 49 48 39C48 26 32 7 32 7Z"/><path d="M12 52L52 12" fill="none"/>',
        '<rect x="46" y="45" width="10" height="10"/>',
    ),
    "icon_shield": (
        '<path d="M32 7L53 15V30C53 44 44 54 32 58C20 54 11 44 11 30V15Z"/><path d="M21 31L29 39L44 23" fill="none"/>',
        '<rect x="8" y="8" width="9" height="9" transform="rotate(-5 12.5 12.5)"/>',
    ),
    "icon_umbrella": (
        '<path d="M8 32Q32 8 56 32Q50 28 44 32Q38 28 32 32Q26 28 20 32Q14 28 8 32Z"/><path d="M32 31V49C32 55 39 58 44 53" fill="none"/>',
        '<rect x="47" y="12" width="9" height="9" transform="rotate(7 51.5 16.5)"/>',
    ),
    "icon_raincoat": (
        '<path d="M23 11L32 7L41 11L55 24L47 31L44 25V56H20V25L17 31L9 24Z"/><path d="M27 9L24 20L32 25L40 20L37 9M32 25V56" fill="none"/>',
        '<path d="M24 45H40V54H24Z"/>',
    ),
    "icon_bag": (
        '<path d="M19 20L13 53H51L45 20Z"/><path d="M24 20C24 12 40 12 40 20M28 13L24 7M36 13L40 7" fill="none"/>',
        '<rect x="43" y="42" width="10" height="10" transform="rotate(4 48 47)"/>',
    ),
    "icon_shoe": (
        '<path d="M8 37C19 37 25 32 27 20L39 23C41 33 48 37 56 39V52H8Z"/><path d="M15 43H50M29 29L38 31" fill="none"/>',
        '<rect x="8" y="11" width="10" height="10" transform="rotate(-4 13 16)"/>',
    ),
    "icon_receipt": (
        '<path d="M14 7H50V56L44 51L38 56L32 51L26 56L20 51L14 56Z"/><path d="M22 20H42M22 29H42M22 38H37" fill="none"/>',
        '<rect x="42" y="9" width="11" height="11" transform="rotate(5 47.5 14.5)"/>',
    ),
    "icon_check": (
        '<rect x="10" y="10" width="44" height="44" transform="rotate(-2 32 32)"/><path d="M20 31L29 40L45 22" fill="none"/>',
        '<rect x="7" y="45" width="11" height="11"/>',
    ),
}


SURFACE_BUILDERS = {
    "panel_paper": lambda: panel_svg(color("white"), color("ink"), color("rain")),
    "panel_night": lambda: panel_svg(color("night"), color("ink"), color("signal")),
    "panel_signal": lambda: panel_svg(color("signal"), color("danger"), None),
    "button_signal": lambda: button_svg(color("signal"), "normal"),
    "button_signal_hover": lambda: button_svg(color("signal"), "hover"),
    "button_signal_pressed": lambda: button_svg(color("signal"), "pressed"),
    "button_night": lambda: button_svg(color("night"), "normal"),
    "button_danger": lambda: button_svg(color("danger"), "normal"),
    "button_disabled": lambda: button_svg(color("disabled"), "normal"),
    "alert_danger": alert_svg,
    "tag_signal": lambda: tag_svg(color("signal")),
    "tag_danger": lambda: tag_svg(color("danger")),
    "receipt_paper": receipt_svg,
    "stripe_warning": stripe_svg,
    "paper_grain": grain_svg,
}


ASSET_META = {
    "panel_paper": {"mode": "sliced", "size": [128, 128], "slice": {"left": 18, "top": 18, "right": 26, "bottom": 26}, "minSize": [52, 52]},
    "panel_night": {"mode": "sliced", "size": [128, 128], "slice": {"left": 18, "top": 18, "right": 26, "bottom": 26}, "minSize": [52, 52]},
    "panel_signal": {"mode": "sliced", "size": [128, 128], "slice": {"left": 18, "top": 18, "right": 26, "bottom": 26}, "minSize": [52, 52]},
    "button_signal": {"mode": "sliced", "size": [160, 64], "slice": {"left": 18, "top": 14, "right": 24, "bottom": 22}, "minSize": [54, 48]},
    "button_signal_hover": {"mode": "sliced", "size": [160, 64], "slice": {"left": 18, "top": 14, "right": 26, "bottom": 24}, "minSize": [54, 48]},
    "button_signal_pressed": {"mode": "sliced", "size": [160, 64], "slice": {"left": 20, "top": 16, "right": 20, "bottom": 18}, "minSize": [54, 48]},
    "button_night": {"mode": "sliced", "size": [160, 64], "slice": {"left": 18, "top": 14, "right": 24, "bottom": 22}, "minSize": [54, 48]},
    "button_danger": {"mode": "sliced", "size": [160, 64], "slice": {"left": 18, "top": 14, "right": 24, "bottom": 22}, "minSize": [54, 48]},
    "button_disabled": {"mode": "sliced", "size": [160, 64], "slice": {"left": 18, "top": 14, "right": 24, "bottom": 22}, "minSize": [54, 48]},
    "alert_danger": {"mode": "sliced", "size": [192, 96], "slice": {"left": 72, "top": 16, "right": 20, "bottom": 24}, "minSize": [120, 72]},
    "tag_signal": {"mode": "sliced", "size": [112, 48], "slice": {"left": 14, "top": 12, "right": 20, "bottom": 18}, "minSize": [42, 34]},
    "tag_danger": {"mode": "sliced", "size": [112, 48], "slice": {"left": 14, "top": 12, "right": 20, "bottom": 18}, "minSize": [42, 34]},
    "receipt_paper": {"mode": "fixed", "size": [176, 208]},
    "stripe_warning": {"mode": "tile", "size": [96, 20]},
    "paper_grain": {"mode": "tile", "size": [128, 128]},
}


def scaled_points(points: list[tuple[float, float]], scale: int, offset: tuple[float, float] = (0, 0)) -> list[tuple[int, int]]:
    return [(round((x + offset[0]) * scale), round((y + offset[1]) * scale)) for x, y in points]


def render_surface_png(name: str, scale: int) -> Image.Image:
    width, height = ASSET_META[name]["size"]
    image = Image.new("RGBA", (width * scale, height * scale), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    s = lambda value: round(value * scale)
    stroke = s(3)

    if name.startswith("panel_"):
        fills = {"panel_paper": "white", "panel_night": "night", "panel_signal": "signal"}
        shadows = {"panel_paper": "ink", "panel_night": "ink", "panel_signal": "danger"}
        draw.rounded_rectangle((s(12), s(12), s(120), s(120)), radius=s(7), fill=rgba(shadows[name]), outline=rgba("ink"), width=stroke)
        draw.rounded_rectangle((s(5), s(5), s(113), s(113)), radius=s(7), fill=rgba(fills[name]), outline=rgba("ink"), width=stroke)
        if name == "panel_paper":
            draw.rectangle((s(14), s(17), s(65), s(25)), fill=rgba("rain"), outline=rgba("ink"), width=stroke)
        elif name == "panel_night":
            draw.rectangle((s(14), s(17), s(65), s(25)), fill=rgba("signal"), outline=rgba("ink"), width=stroke)
        return image

    if name.startswith("button_"):
        state = "normal"
        if name.endswith("_hover"):
            state = "hover"
        elif name.endswith("_pressed"):
            state = "pressed"
        positions = {"normal": (5, 5, 7, 7), "hover": (3, 3, 9, 9), "pressed": (8, 8, 2, 2)}
        x, y, shadow_x, shadow_y = positions[state]
        fill_name = "signal"
        if name == "button_night":
            fill_name = "night"
        elif name == "button_danger":
            fill_name = "danger"
        elif name == "button_disabled":
            fill_name = "disabled"
        draw.rounded_rectangle((s(x + shadow_x), s(y + shadow_y), s(x + shadow_x + 142), s(y + shadow_y + 46)), radius=s(3), fill=rgba("ink"))
        draw.rounded_rectangle((s(x), s(y), s(x + 142), s(y + 46)), radius=s(3), fill=rgba(fill_name), outline=rgba("ink"), width=stroke)
        draw.line((s(x + 14), s(y + 34), s(x + 60), s(y + 34)), fill=rgba("ink"), width=stroke)
        return image

    if name == "alert_danger":
        draw.rectangle((s(12), s(12), s(186), s(88)), fill=rgba("ink"))
        draw.rectangle((s(4), s(4), s(178), s(80)), fill=rgba("danger"), outline=rgba("ink"), width=stroke)
        draw.rectangle((s(16), s(17), s(60), s(61)), fill=rgba("signal"), outline=rgba("ink"), width=stroke)
        draw.line((s(38), s(27), s(38), s(45)), fill=rgba("ink"), width=s(5))
        draw.line((s(38), s(52), s(38), s(55)), fill=rgba("ink"), width=s(5))
        for y, end in ((24, 157), (39, 166), (55, 142)):
            draw.line((s(74), s(y), s(end), s(y)), fill=rgba("white"), width=s(5))
        return image

    if name.startswith("tag_"):
        fill_name = "signal" if name == "tag_signal" else "danger"
        draw.rectangle((s(9), s(9), s(105), s(39)), fill=rgba("ink"))
        draw.rectangle((s(4), s(4), s(100), s(34)), fill=rgba(fill_name), outline=rgba("ink"), width=stroke)
        draw.line((s(16), s(19), s(63), s(19)), fill=rgba("ink"), width=s(4))
        return image

    if name == "receipt_paper":
        zigzag = [(13, 12), (169, 12), (169, 188)]
        for x in range(161, 20, -8):
            zigzag.append((x, 196 if (x // 8) % 2 else 188))
        zigzag.extend([(13, 196), (13, 12)])
        draw.polygon(scaled_points(zigzag, scale), fill=rgba("ink"))
        front = [(5, 4), (161, 4), (161, 180)]
        for x in range(153, 12, -8):
            front.append((x, 188 if (x // 8) % 2 else 180))
        front.extend([(5, 188), (5, 4)])
        draw.polygon(scaled_points(front, scale), fill=rgba("white"), outline=rgba("ink"))
        draw.line(scaled_points(front, scale), fill=rgba("ink"), width=stroke, joint="curve")
        draw.line((s(24), s(30), s(142), s(30)), fill=rgba("ink"), width=s(5))
        draw.line((s(24), s(45), s(118), s(45)), fill=rgba("ink"), width=s(5))
        for y in (68, 88, 108, 128):
            for x in range(24, 142, 14):
                draw.line((s(x), s(y), s(min(x + 8, 142)), s(y)), fill=rgba("muted"), width=s(2))
        draw.line((s(24), s(151), s(142), s(151)), fill=rgba("ink"), width=s(4))
        return image

    if name == "stripe_warning":
        draw.rectangle((0, 0, width * scale, height * scale), fill=rgba("signal"))
        for x in range(-20, 120, 24):
            draw.polygon(scaled_points([(x, 18), (x + 14, 2), (x + 30, 2), (x + 16, 18)], scale), fill=rgba("ink"))
        draw.line((0, s(1), width * scale, s(1)), fill=rgba("ink"), width=s(2))
        draw.line((0, s(19), width * scale, s(19)), fill=rgba("ink"), width=s(2))
        return image

    if name == "paper_grain":
        draw.rectangle((0, 0, width * scale, height * scale), fill=rgba("paper"))
        for index in range(34):
            x = (index * 37 + 11) % 128
            y = (index * 53 + 17) % 128
            radius = 1 if index % 3 else 1.5
            opacity = 20 if index % 2 else 30
            draw.ellipse((s(x - radius), s(y - radius), s(x + radius), s(y + radius)), fill=rgba("ink")[:3] + (opacity,))
        return image

    raise KeyError(f"Unknown surface: {name}")


def draw_icon_geometry(draw: ImageDraw.ImageDraw, name: str, scale: int, fill_name: str, offset: tuple[int, int]) -> None:
    s = lambda value: round(value * scale)
    points = lambda values: scaled_points(values, scale, offset)
    ox, oy = offset
    fill = rgba(fill_name)
    ink = rgba("ink")
    stroke = s(3)

    def line(values: list[tuple[float, float]], width: int = 3) -> None:
        draw.line(points(values), fill=ink, width=s(width), joint="curve")

    if name == "icon_alert":
        polygon = [(32, 8), (57, 53), (7, 53)]
        draw.polygon(points(polygon), fill=fill)
        line(polygon + [polygon[0]])
        line([(32, 22), (32, 37)], 4)
        line([(32, 44), (32, 47)], 4)
    elif name == "icon_clock":
        draw.ellipse((s(9 + ox), s(9 + oy), s(55 + ox), s(55 + oy)), fill=fill, outline=ink, width=stroke)
        line([(32, 18), (32, 33), (43, 40)])
        line([(20, 8), (44, 8)])
    elif name == "icon_budget":
        draw.rectangle((s(9 + ox), s(19 + oy), s(51 + ox), s(49 + oy)), fill=fill, outline=ink, width=stroke)
        draw.rectangle((s(37 + ox), s(28 + oy), s(57 + ox), s(42 + oy)), fill=fill, outline=ink, width=stroke)
        draw.ellipse((s(42 + ox), s(33 + oy), s(46 + ox), s(37 + oy)), outline=ink, width=s(2))
    elif name == "icon_dry":
        drop = [(32, 7), (23, 19), (17, 31), (16, 40), (19, 49), (25, 55), (32, 57), (39, 55), (45, 49), (48, 40), (47, 31), (41, 19)]
        draw.polygon(points(drop), fill=fill)
        line(drop + [drop[0]])
        line([(12, 52), (52, 12)], 4)
    elif name == "icon_shield":
        shield = [(32, 7), (53, 15), (53, 30), (49, 42), (41, 51), (32, 58), (23, 54), (15, 46), (11, 30), (11, 15)]
        draw.polygon(points(shield), fill=fill)
        line(shield + [shield[0]])
        line([(21, 31), (29, 39), (44, 23)], 4)
    elif name == "icon_umbrella":
        dome = [(8, 32), (13, 24), (21, 17), (32, 12), (43, 17), (51, 24), (56, 32), (50, 28), (44, 32), (38, 28), (32, 32), (26, 28), (20, 32), (14, 28)]
        draw.polygon(points(dome), fill=fill)
        line(dome + [dome[0]])
        line([(32, 31), (32, 49), (34, 54), (39, 57), (44, 53)], 3)
    elif name == "icon_raincoat":
        coat = [(23, 11), (32, 7), (41, 11), (55, 24), (47, 31), (44, 25), (44, 56), (20, 56), (20, 25), (17, 31), (9, 24)]
        draw.polygon(points(coat), fill=fill)
        line(coat + [coat[0]])
        line([(27, 9), (24, 20), (32, 25), (40, 20), (37, 9)])
        line([(32, 25), (32, 56)])
    elif name == "icon_bag":
        bag = [(19, 20), (13, 53), (51, 53), (45, 20)]
        draw.polygon(points(bag), fill=fill)
        line(bag + [bag[0]])
        line([(24, 20), (25, 14), (29, 11), (35, 11), (39, 14), (40, 20)])
        line([(28, 13), (24, 7)])
        line([(36, 13), (40, 7)])
    elif name == "icon_shoe":
        shoe = [(8, 37), (17, 36), (23, 31), (27, 20), (39, 23), (43, 32), (49, 36), (56, 39), (56, 52), (8, 52)]
        draw.polygon(points(shoe), fill=fill)
        line(shoe + [shoe[0]])
        line([(15, 43), (50, 43)])
        line([(29, 29), (38, 31)])
    elif name == "icon_receipt":
        receipt = [(14, 7), (50, 7), (50, 56), (44, 51), (38, 56), (32, 51), (26, 56), (20, 51), (14, 56)]
        draw.polygon(points(receipt), fill=fill)
        line(receipt + [receipt[0]])
        line([(22, 20), (42, 20)])
        line([(22, 29), (42, 29)])
        line([(22, 38), (37, 38)])
    elif name == "icon_check":
        draw.rectangle((s(10 + ox), s(10 + oy), s(54 + ox), s(54 + oy)), fill=fill, outline=ink, width=stroke)
        line([(20, 31), (29, 40), (45, 22)], 4)
    else:
        raise KeyError(f"Unknown icon: {name}")


def draw_icon_accent(draw: ImageDraw.ImageDraw, name: str, scale: int) -> None:
    s = lambda value: round(value * scale)
    boxes = {
        "icon_alert": (49, 7, 57, 15),
        "icon_clock": (8, 43, 18, 53),
        "icon_budget": (9, 8, 23, 22),
        "icon_dry": (46, 45, 56, 55),
        "icon_shield": (8, 8, 17, 17),
        "icon_umbrella": (47, 12, 56, 21),
        "icon_raincoat": (24, 45, 40, 54),
        "icon_bag": (43, 42, 53, 52),
        "icon_shoe": (8, 11, 18, 21),
        "icon_receipt": (42, 9, 53, 20),
        "icon_check": (7, 45, 18, 56),
    }
    box = boxes[name]
    draw.rectangle(tuple(s(value) for value in box), fill=rgba("signal"), outline=rgba("ink"), width=s(2))


def render_icon_png(name: str, scale: int) -> Image.Image:
    image = Image.new("RGBA", (64 * scale, 64 * scale), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw_icon_geometry(draw, name, scale, "rain", (4, 4))
    draw_icon_geometry(draw, name, scale, "white", (0, 0))
    draw_icon_accent(draw, name, scale)
    return image


def render_assets() -> list[str]:
    source_dir = ROOT / "assets" / "source"
    png_dirs = {1: ROOT / "assets" / "png" / "1x", 2: ROOT / "assets" / "png" / "2x"}
    names: list[str] = []

    for name, builder in SURFACE_BUILDERS.items():
        svg = builder()
        write_text(source_dir / f"{name}.svg", svg)
        for scale, output_dir in png_dirs.items():
            output_dir.mkdir(parents=True, exist_ok=True)
            render_surface_png(name, scale).save(output_dir / f"{name}.png", format="PNG", optimize=False)
        names.append(name)

    for name, (geometry, accent) in ICON_GEOMETRY.items():
        svg = icon_svg(geometry, accent)
        write_text(source_dir / f"{name}.svg", svg)
        for scale, output_dir in png_dirs.items():
            output_dir.mkdir(parents=True, exist_ok=True)
            render_icon_png(name, scale).save(output_dir / f"{name}.png", format="PNG", optimize=False)
        names.append(name)

    manifest = {
        "version": TOKENS["version"],
        "referenceScale": 1,
        "notes": "Slice values are pixels at 1x. Multiply by texture scale for 2x assets.",
        "assets": {name: {"file": f"assets/png/1x/{name}.png", **meta} for name, meta in ASSET_META.items()},
        "icons": {name: {"file": f"assets/png/1x/{name}.png", "size": [64, 64], "mode": "simple"} for name in ICON_GEOMETRY},
    }
    write_json(ROOT / "generated" / "asset-slices.json", manifest)
    return names


def generate_css_tokens() -> None:
    lines = [":root {"]
    for name, data in TOKENS["color"].items():
        kebab = "".join((f"-{char.lower()}" if char.isupper() else char) for char in name)
        lines.append(f"  --rp-{kebab}: {data['value']};")
    for name, value in TOKENS["border"].items():
        lines.append(f"  --rp-border-{name}: {value}px;")
    for name, value in TOKENS["radius"].items():
        lines.append(f"  --rp-radius-{name}: {value}px;")
    for name, value in TOKENS["space"].items():
        lines.append(f"  --rp-space-{name}: {value}px;")
    lines.append("}")
    write_text(ROOT / "generated" / "web" / "rainport.tokens.css", "\n".join(lines))


def generate_unity_tokens() -> None:
    lines = ["/* AUTO-GENERATED. Edit tokens/rainport.tokens.json instead. */", ":root {"]
    for name, data in TOKENS["color"].items():
        kebab = "".join((f"-{char.lower()}" if char.isupper() else char) for char in name)
        lines.append(f"    --rp-{kebab}: {data['value']};")
    lines.extend(
        [
            f"    --rp-border-thin: {TOKENS['border']['thin']}px;",
            f"    --rp-border-base: {TOKENS['border']['base']}px;",
            f"    --rp-radius-small: {TOKENS['radius']['small']}px;",
            f"    --rp-radius-medium: {TOKENS['radius']['medium']}px;",
            f"    --rp-shadow-small: {TOKENS['shadow']['small']['x']}px;",
            f"    --rp-shadow-medium: {TOKENS['shadow']['medium']['x']}px;",
            "}",
        ]
    )
    write_text(ROOT / "adapters" / "unity" / "Runtime" / "Styles" / "RainportTokens.uss", "\n".join(lines))


def generate_godot_tokens() -> None:
    lines = ["# AUTO-GENERATED. Edit tokens/rainport.tokens.json instead.", "class_name RainportTokens", "extends RefCounted", ""]
    for name, data in TOKENS["color"].items():
        lines.append(f'const {name.upper()} := Color("{data["value"]}")')
    lines.extend(
        [
            "",
            f"const BORDER_THIN := {TOKENS['border']['thin']}",
            f"const BORDER_BASE := {TOKENS['border']['base']}",
            f"const RADIUS_SMALL := {TOKENS['radius']['small']}",
            f"const RADIUS_MEDIUM := {TOKENS['radius']['medium']}",
            f"const SHADOW_SMALL := Vector2({TOKENS['shadow']['small']['x']}, {TOKENS['shadow']['small']['y']})",
            f"const SHADOW_MEDIUM := Vector2({TOKENS['shadow']['medium']['x']}, {TOKENS['shadow']['medium']['y']})",
        ]
    )
    write_text(ROOT / "adapters" / "godot" / "addons" / "rainport_ui" / "rainport_tokens.gd", "\n".join(lines))


def stylebox(resource_id: str, fill: str, shadow: str = "ink", offset: int = 7, radius: int = 7) -> str:
    return f"""[sub_resource type=\"StyleBoxFlat\" id=\"{resource_id}\"]
bg_color = {godot_color(fill)}
border_width_left = 3
border_width_top = 3
border_width_right = 3
border_width_bottom = 3
border_color = {godot_color('ink')}
corner_radius_top_left = {radius}
corner_radius_top_right = {radius}
corner_radius_bottom_right = {radius}
corner_radius_bottom_left = {radius}
content_margin_left = 18.0
content_margin_top = 14.0
content_margin_right = 18.0
content_margin_bottom = 14.0
shadow_color = {godot_color(shadow)}
shadow_size = 1
shadow_offset = Vector2({offset}, {offset})
"""


def generate_godot_theme() -> None:
    theme = f"""[gd_resource type=\"Theme\" load_steps=11 format=3]

[ext_resource type=\"FontFile\" path=\"res://addons/rainport_ui/fonts/NotoSansSC-Variable.ttf\" id=\"1_body\"]
[ext_resource type=\"FontFile\" path=\"res://addons/rainport_ui/fonts/ZCOOLKuaiLe-Regular.ttf\" id=\"2_display\"]

{stylebox('StyleBox_button', 'signal')}
{stylebox('StyleBox_button_hover', 'signal', offset=9)}
{stylebox('StyleBox_button_pressed', 'signal', offset=1)}
{stylebox('StyleBox_button_danger', 'danger')}
{stylebox('StyleBox_button_night', 'night')}
{stylebox('StyleBox_panel_paper', 'white')}
{stylebox('StyleBox_panel_night', 'night')}
{stylebox('StyleBox_panel_alert', 'danger')}

[resource]
default_font = ExtResource(\"1_body\")
default_font_size = 18
Button/colors/font_color = {godot_color('ink')}
Button/colors/font_hover_color = {godot_color('ink')}
Button/colors/font_pressed_color = {godot_color('ink')}
Button/colors/font_disabled_color = {godot_color('paperDeep')}
Button/font_sizes/font_size = 18
Button/styles/normal = SubResource(\"StyleBox_button\")
Button/styles/hover = SubResource(\"StyleBox_button_hover\")
Button/styles/pressed = SubResource(\"StyleBox_button_pressed\")
Button/styles/focus = SubResource(\"StyleBox_button_hover\")
RainportDangerButton/base_type = &\"Button\"
RainportDangerButton/colors/font_color = {godot_color('white')}
RainportDangerButton/styles/normal = SubResource(\"StyleBox_button_danger\")
RainportNightButton/base_type = &\"Button\"
RainportNightButton/colors/font_color = {godot_color('white')}
RainportNightButton/styles/normal = SubResource(\"StyleBox_button_night\")
RainportPaperPanel/base_type = &\"PanelContainer\"
RainportPaperPanel/styles/panel = SubResource(\"StyleBox_panel_paper\")
RainportNightPanel/base_type = &\"PanelContainer\"
RainportNightPanel/styles/panel = SubResource(\"StyleBox_panel_night\")
RainportAlertPanel/base_type = &\"PanelContainer\"
RainportAlertPanel/styles/panel = SubResource(\"StyleBox_panel_alert\")
RainportDisplayLabel/base_type = &\"Label\"
RainportDisplayLabel/fonts/font = ExtResource(\"2_display\")
RainportDisplayLabel/font_sizes/font_size = 42
RainportDisplayLabel/colors/font_color = {godot_color('ink')}
RainportKickerLabel/base_type = &\"Label\"
RainportKickerLabel/font_sizes/font_size = 13
RainportKickerLabel/colors/font_color = {godot_color('muted')}
"""
    write_text(ROOT / "adapters" / "godot" / "addons" / "rainport_ui" / "rainport_theme.tres", theme)


def generate_cocos_tokens() -> None:
    colors = ",\n".join(f'  {name}: "{data["value"]}"' for name, data in TOKENS["color"].items())
    spaces = ",\n".join(f"  s{name}: {value}" for name, value in TOKENS["space"].items())
    value = f"""// AUTO-GENERATED. Edit tokens/rainport.tokens.json instead.
export const RAINPORT_COLORS = Object.freeze({{
{colors}
}});

export const RAINPORT_METRICS = Object.freeze({{
  borderThin: {TOKENS['border']['thin']},
  borderBase: {TOKENS['border']['base']},
  radiusSmall: {TOKENS['radius']['small']},
  radiusMedium: {TOKENS['radius']['medium']},
  shadowSmall: Object.freeze({{ x: {TOKENS['shadow']['small']['x']}, y: {TOKENS['shadow']['small']['y']} }}),
  shadowMedium: Object.freeze({{ x: {TOKENS['shadow']['medium']['x']}, y: {TOKENS['shadow']['medium']['y']} }}),
  pressTranslate: Object.freeze({{ x: {TOKENS['motion']['pressTranslate']['x']}, y: {TOKENS['motion']['pressTranslate']['y']} }}),
  touchTargetMin: {TOKENS['density']['touchTargetMin']},
  space: Object.freeze({{
{spaces}
  }})
}});
"""
    write_text(ROOT / "adapters" / "cocos" / "assets" / "rainport-ui" / "scripts" / "rainport-tokens.ts", value)


def nine_slice(image: Image.Image, target: tuple[int, int], slices: dict[str, int]) -> Image.Image:
    left, top, right, bottom = (slices[key] for key in ("left", "top", "right", "bottom"))
    source_width, source_height = image.size
    target_width, target_height = target
    output = Image.new("RGBA", target, (0, 0, 0, 0))
    x_source = [0, left, source_width - right, source_width]
    y_source = [0, top, source_height - bottom, source_height]
    x_target = [0, left, target_width - right, target_width]
    y_target = [0, top, target_height - bottom, target_height]
    for row in range(3):
        for column in range(3):
            source_box = (x_source[column], y_source[row], x_source[column + 1], y_source[row + 1])
            target_box = (x_target[column], y_target[row], x_target[column + 1], y_target[row + 1])
            patch = image.crop(source_box)
            target_size = (max(1, target_box[2] - target_box[0]), max(1, target_box[3] - target_box[1]))
            if patch.size != target_size:
                patch = patch.resize(target_size, Image.Resampling.NEAREST)
            output.alpha_composite(patch, (target_box[0], target_box[1]))
    return output


def load_font(path: Path, size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    if path.exists():
        return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


def preview_canvas(width: int, height: int, background: str = "paper") -> tuple[Image.Image, ImageDraw.ImageDraw]:
    canvas = Image.new("RGBA", (width, height), rgba(background))
    if background == "paper":
        grain = Image.open(ROOT / "assets" / "png" / "1x" / "paper_grain.png").convert("RGBA")
        for y in range(0, height, grain.height):
            for x in range(0, width, grain.width):
                canvas.alpha_composite(grain, (x, y))
    else:
        rain_draw = ImageDraw.Draw(canvas)
        for index in range(28):
            x = (index * 83 + 19) % width
            y = (index * 137 + 31) % height
            rain_draw.line((x, y, x - 18, y + 42), fill=rgba("blue"), width=2)
    return canvas, ImageDraw.Draw(canvas)


def preview_asset(name: str, size: tuple[int, int] | None = None) -> Image.Image:
    source = Image.open(ROOT / "assets" / "png" / "1x" / f"{name}.png").convert("RGBA")
    if size is None or source.size == size:
        return source
    metadata = ASSET_META.get(name, {})
    if metadata.get("mode") == "sliced":
        return nine_slice(source, size, metadata["slice"])
    return source.resize(size, Image.Resampling.LANCZOS)


def paste_preview_asset(canvas: Image.Image, name: str, box: tuple[int, int, int, int]) -> None:
    x, y, width, height = box
    canvas.alpha_composite(preview_asset(name, (width, height)), (x, y))


def preview_fonts() -> dict[str, ImageFont.FreeTypeFont | ImageFont.ImageFont]:
    display_path = ROOT / "assets" / "fonts" / "ZCOOLKuaiLe-Regular.ttf"
    body_path = ROOT / "assets" / "fonts" / "NotoSansSC-Variable.ttf"
    return {
        "display": load_font(display_path, 68),
        "title": load_font(display_path, 38),
        "engine": load_font(display_path, 27),
        "metric": load_font(display_path, 82),
        "body": load_font(body_path, 22),
        "label": load_font(body_path, 17),
        "small": load_font(body_path, 14),
    }


def draw_preview_button(
    canvas: Image.Image,
    draw: ImageDraw.ImageDraw,
    fonts: dict[str, ImageFont.FreeTypeFont | ImageFont.ImageFont],
    name: str,
    label: str,
    box: tuple[int, int, int, int],
) -> None:
    x, y, width, height = box
    paste_preview_asset(canvas, name, box)
    text_color = rgba("white") if name in ("button_night", "button_danger") else rgba("ink")
    draw.text((x + 24, y + 17), label, font=fonts["label"], fill=text_color)


def draw_preview_meter(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    value: int,
    fill: str,
) -> None:
    x, y, width, height = box
    draw.rectangle((x, y, x + width, y + height), fill=rgba("white"), outline=rgba("ink"), width=3)
    inner_width = max(0, round((width - 8) * value / 100))
    if inner_width:
        draw.rectangle((x + 4, y + 4, x + 4 + inner_width, y + height - 4), fill=rgba(fill))


def draw_preview_alert(
    canvas: Image.Image,
    draw: ImageDraw.ImageDraw,
    fonts: dict[str, ImageFont.FreeTypeFont | ImageFont.ImageFont],
    label: str,
    box: tuple[int, int, int, int],
) -> None:
    x, y, width, height = box
    paste_preview_asset(canvas, "alert_danger", box)
    draw.rectangle((x + 76, y + 16, x + width - 22, y + height - 24), fill=rgba("danger"))
    text_box = draw.textbbox((0, 0), label, font=fonts["body"])
    text_height = text_box[3] - text_box[1]
    draw.text((x + 96, y + (height - text_height) // 2 - 4), label, font=fonts["body"], fill=rgba("white"))


def generate_loadout_preview() -> None:
    canvas, draw = preview_canvas(1440, 900)
    fonts = preview_fonts()

    paste_preview_asset(canvas, "panel_night", (28, 24, 1384, 86))
    draw.text((58, 43), "雨港市公共体面管理局", font=fonts["title"], fill=rgba("white"))
    draw.text((1110, 55), "装备审查 / 08:41", font=fonts["label"], fill=rgba("mint"))

    draw.text((42, 142), "COMMUTE LOADOUT / 通勤装备", font=fonts["label"], fill=rgba("danger"))
    draw.text((40, 168), "今天也要体面地出门", font=fonts["display"], fill=rgba("ink"))
    draw.text((44, 244), "预报说只是小雨。预报还说过很多别的。", font=fonts["body"], fill=rgba("muted"))

    cards = [
        ("panel_paper", 40, "icon_umbrella", "祖传折叠伞", "优点是轻，缺点也是轻。", "覆盖 42%  ·  重量 +1"),
        ("panel_signal", 465, "icon_raincoat", "香蕉黄长雨衣", "远看像路标，近看像放弃抵抗。", "覆盖 88%  ·  体面 +3"),
    ]
    for panel, x, icon_name, title, description, meta in cards:
        paste_preview_asset(canvas, panel, (x, 292, 390, 324))
        canvas.alpha_composite(preview_asset(icon_name, (86, 86)), (x + 28, 330))
        draw.text((x + 130, 329), title, font=fonts["title"], fill=rgba("ink"))
        draw.text((x + 30, 438), description, font=fonts["body"], fill=rgba("ink"))
        draw.line((x + 30, 505, x + 344, 505), fill=rgba("ink"), width=3)
        draw.text((x + 30, 526), meta, font=fonts["label"], fill=rgba("muted"))
        draw.text((x + 30, 566), "已装入背包", font=fonts["small"], fill=rgba("danger"))

    paste_preview_asset(canvas, "panel_night", (890, 292, 510, 324))
    draw.text((926, 326), "今日风险评估", font=fonts["title"], fill=rgba("white"))
    draw.text((925, 382), "67", font=fonts["metric"], fill=rgba("signal"))
    draw.text((1035, 428), "% 还能维持体面", font=fonts["body"], fill=rgba("white"))
    draw.text((926, 498), "迟到风险", font=fonts["label"], fill=rgba("rain"))
    draw_preview_meter(draw, (1060, 500, 286, 24), 58, "danger")
    draw.text((926, 545), "袜子生还", font=fonts["label"], fill=rgba("rain"))
    draw_preview_meter(draw, (1060, 547, 286, 24), 19, "signal")

    draw_preview_button(canvas, draw, fonts, "button_signal", "确认，硬着头皮上", (42, 652, 272, 66))
    draw_preview_button(canvas, draw, fonts, "button_night", "再塞两个塑料袋", (338, 652, 272, 66))
    draw_preview_button(canvas, draw, fonts, "button_disabled", "天气预报说没事", (634, 652, 272, 66))
    draw_preview_alert(
        canvas,
        draw,
        fonts,
        "认真通知：你不是准备充分，你只是塑料袋带得比较多。",
        (42, 754, 1358, 110),
    )

    output = ROOT / "preview" / "rainport-ui-loadout.png"
    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(output, format="PNG", optimize=False)


def generate_result_preview() -> None:
    canvas, draw = preview_canvas(1440, 900, "night")
    fonts = preview_fonts()

    paste_preview_asset(canvas, "panel_signal", (30, 24, 1380, 88))
    draw.text((62, 42), "你淋湿了吗？", font=fonts["title"], fill=rgba("ink"))
    draw.text((1118, 56), "ARRIVAL / 09:01", font=fonts["label"], fill=rgba("ink"))
    draw.text((44, 146), "今日通勤受灾报告", font=fonts["display"], fill=rgba("white"))
    draw.text((48, 220), "衣服可以湿，数据必须说清楚。", font=fonts["body"], fill=rgba("rain"))

    paste_preview_asset(canvas, "panel_paper", (40, 278, 820, 554))
    canvas.alpha_composite(preview_asset("icon_dry", (96, 96)), (82, 352))
    draw.text((205, 313), "衣物干燥率", font=fonts["title"], fill=rgba("white"))
    draw.text((202, 362), "67", font=fonts["metric"], fill=rgba("danger"))
    draw.text((310, 409), "%", font=fonts["title"], fill=rgba("ink"))

    meters = [
        ("衬衫", 83, "rain"),
        ("西裤", 46, "signal"),
        ("袜子", 0, "danger"),
        ("笔记本电脑", 100, "mint"),
    ]
    for index, (label, value, fill) in enumerate(meters):
        y = 486 + index * 72
        draw.text((88, y), label, font=fonts["label"], fill=rgba("ink"))
        draw_preview_meter(draw, (260, y + 2, 430, 26), value, fill)
        draw.text((712, y - 1), f"{value}%", font=fonts["label"], fill=rgba("ink"))

    receipt = preview_asset("receipt_paper", (410, 506))
    canvas.alpha_composite(receipt, (944, 282))
    draw.rectangle((978, 310, 1318, 716), fill=rgba("white"))
    draw.text((998, 326), "今日受灾小票", font=fonts["title"], fill=rgba("ink"))
    draw.text((1000, 388), "到达时间      09:01", font=fonts["label"], fill=rgba("ink"))
    draw.text((1000, 430), "通勤花费       4 元", font=fonts["label"], fill=rgba("ink"))
    draw.text((1000, 472), "违规次数       1 次", font=fonts["label"], fill=rgba("ink"))
    draw.line((998, 520, 1298, 520), fill=rgba("muted"), width=2)
    draw.text((1000, 548), "袜子：确认阵亡", font=fonts["body"], fill=rgba("danger"))
    draw.text((1000, 594), "电脑：毫发无伤", font=fonts["body"], fill=rgba("blue"))
    draw.text((1000, 632), "今日称号", font=fonts["small"], fill=rgba("muted"))
    draw.text((998, 652), "电脑没事", font=fonts["engine"], fill=rgba("ink"))
    draw.text((998, 686), "人有点事", font=fonts["engine"], fill=rgba("danger"))

    draw_preview_alert(canvas, draw, fonts, "结论：准时了，但不完全准时。", (900, 800, 500, 74))

    output = ROOT / "preview" / "rainport-ui-result.png"
    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(output, format="PNG", optimize=False)


def generate_engine_preview() -> None:
    canvas, draw = preview_canvas(1440, 900)
    fonts = preview_fonts()

    paste_preview_asset(canvas, "panel_night", (28, 24, 1384, 92))
    draw.text((58, 43), "ONE UI SYSTEM / THREE ENGINES", font=fonts["title"], fill=rgba("white"))
    draw.text((1174, 56), "RP/UI 0.1", font=fonts["label"], fill=rgba("mint"))
    draw.text((42, 150), "一套令牌，三种落地方式", font=fonts["display"], fill=rgba("ink"))
    draw.text((46, 224), "组件结构可以因引擎而变，视觉规则不能各过各的。", font=fonts["body"], fill=rgba("muted"))

    engines = [
        {
            "x": 42,
            "panel": "panel_paper",
            "icon": "icon_shield",
            "title": "UNITY",
            "subtitle": "UI Toolkit / uGUI",
            "lines": ["UXML + USS", "UPM 本地包", "9-slice Sprite", "rp- 公共类名"],
            "button": "button_signal",
            "button_text": "INSTALL PACKAGE",
            "text": "ink",
        },
        {
            "x": 512,
            "panel": "panel_night",
            "icon": "icon_dry",
            "title": "GODOT",
            "subtitle": "Control / Theme",
            "lines": ["Theme + TRES", "StyleBox 组件", "Addon 目录", "类型变体"],
            "button": "button_signal",
            "button_text": "COPY ADDON",
            "text": "white",
        },
        {
            "x": 982,
            "panel": "panel_signal",
            "icon": "icon_check",
            "title": "COCOS CREATOR",
            "subtitle": "Sprite / TypeScript",
            "lines": ["Token 常量", "Sliced Sprite", "Button 状态", "Assets 目录"],
            "button": "button_night",
            "button_text": "IMPORT ASSETS",
            "text": "ink",
        },
    ]

    for engine in engines:
        x = engine["x"]
        paste_preview_asset(canvas, engine["panel"], (x, 294, 416, 472))
        canvas.alpha_composite(preview_asset(engine["icon"], (78, 78)), (x + 28, 344))
        text_color = rgba(engine["text"])
        secondary = rgba("rain") if engine["text"] == "white" else rgba("muted")
        draw.text((x + 122, 350), engine["title"], font=fonts["engine"], fill=text_color)
        draw.text((x + 124, 388), engine["subtitle"], font=fonts["label"], fill=secondary)
        draw.line((x + 30, 436, x + 370, 436), fill=text_color, width=3)
        for index, line in enumerate(engine["lines"]):
            y = 468 + index * 48
            draw.rectangle((x + 34, y + 6, x + 48, y + 20), fill=rgba("signal"), outline=rgba("ink"), width=2)
            draw.text((x + 66, y), line, font=fonts["body"], fill=text_color)
        draw_preview_button(canvas, draw, fonts, engine["button"], engine["button_text"], (x + 30, 682, 340, 62))

    stripe = preview_asset("stripe_warning")
    for x in range(32, 1408, stripe.width):
        canvas.alpha_composite(stripe, (x, 808))
    draw.text((44, 846), "TOKEN SOURCE → PLATFORM ADAPTER → PROJECT OVERRIDE", font=fonts["label"], fill=rgba("ink"))
    draw.text((1018, 846), "ZERO VISUAL DRIFT", font=fonts["label"], fill=rgba("danger"))

    output = ROOT / "preview" / "rainport-ui-engines.png"
    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(output, format="PNG", optimize=False)


def generate_contact_sheet() -> None:
    width, height = 1600, 1120
    sheet = Image.new("RGBA", (width, height), rgba("paper"))
    draw = ImageDraw.Draw(sheet)
    grain = Image.open(ROOT / "assets" / "png" / "1x" / "paper_grain.png").convert("RGBA")
    for y in range(0, height, grain.height):
        for x in range(0, width, grain.width):
            sheet.alpha_composite(grain, (x, y))

    display_font = load_font(ROOT / "assets" / "fonts" / "ZCOOLKuaiLe-Regular.ttf", 66)
    label_font = load_font(ROOT / "assets" / "fonts" / "NotoSansSC-Variable.ttf", 22)
    small_font = load_font(ROOT / "assets" / "fonts" / "NotoSansSC-Variable.ttf", 17)

    draw.rectangle((28, 28, 1572, 116), fill=rgba("night"), outline=rgba("ink"), width=4)
    draw.rectangle((48, 48, 104, 104), fill=rgba("signal"), outline=rgba("white"), width=3)
    draw.text((128, 40), "RAINPORT PRINT-ARCADE UI", font=display_font, fill=rgba("white"))
    draw.text((1240, 64), "CORE KIT / 0.1.0", font=small_font, fill=rgba("mint"))

    draw.text((52, 146), "01 / STRETCHABLE SURFACES", font=label_font, fill=rgba("ink"))
    panels = ["panel_paper", "panel_night", "panel_signal"]
    for index, name in enumerate(panels):
        source = Image.open(ROOT / "assets" / "png" / "1x" / f"{name}.png").convert("RGBA")
        stretched = nine_slice(source, (430, 170), ASSET_META[name]["slice"])
        x = 52 + index * 510
        sheet.alpha_composite(stretched, (x, 184))
        label_color = rgba("white") if name == "panel_night" else rgba("ink")
        draw.text((x + 26, 224), name.replace("_", " ").upper(), font=label_font, fill=label_color)
        draw.text((x + 26, 268), "3PX INK / HARD SHADOW / 7PX RADIUS", font=small_font, fill=label_color)

    draw.text((52, 392), "02 / BUTTON STATES", font=label_font, fill=rgba("ink"))
    buttons = ["button_signal", "button_signal_hover", "button_signal_pressed", "button_night", "button_danger", "button_disabled"]
    for index, name in enumerate(buttons):
        row, column = divmod(index, 3)
        source = Image.open(ROOT / "assets" / "png" / "1x" / f"{name}.png").convert("RGBA")
        x, y = 52 + column * 510, 430 + row * 92
        sheet.alpha_composite(source, (x, y))
        text_color = rgba("white") if name in ("button_night", "button_danger") else rgba("ink")
        draw.text((x + 24, y + 18), name.replace("button_", "").upper(), font=small_font, fill=text_color)

    draw.text((52, 638), "03 / INTERFACE ICONS", font=label_font, fill=rgba("ink"))
    for index, name in enumerate(ICON_GEOMETRY):
        icon = Image.open(ROOT / "assets" / "png" / "2x" / f"{name}.png").convert("RGBA").resize((80, 80), Image.Resampling.LANCZOS)
        x = 52 + index * 135
        sheet.alpha_composite(icon, (x, 682))
        draw.text((x, 770), name.removeprefix("icon_").upper(), font=small_font, fill=rgba("ink"))

    draw.text((52, 832), "04 / SYSTEM PALETTE", font=label_font, fill=rgba("ink"))
    palette = ["ink", "night", "blue", "rain", "paper", "signal", "danger", "mint", "white"]
    for index, name in enumerate(palette):
        x = 52 + index * 166
        draw.rectangle((x, 875, x + 140, 958), fill=rgba(name), outline=rgba("ink"), width=3)
        draw.text((x, 970), name.upper(), font=small_font, fill=rgba("ink"))
        draw.text((x, 997), color(name), font=small_font, fill=rgba("muted"))

    draw.rectangle((42, 1053, 1558, 1073), fill=rgba("signal"), outline=rgba("ink"), width=2)
    stripe = Image.open(ROOT / "assets" / "png" / "1x" / "stripe_warning.png").convert("RGBA")
    for x in range(42, 1558, stripe.width):
        sheet.alpha_composite(stripe, (x, 1053))
    draw.text((52, 1083), "SERIOUS LABEL + SPECIFIC ABSURD CONSEQUENCE", font=small_font, fill=rgba("ink"))

    output = ROOT / "preview" / "rainport-ui-kit-sheet.png"
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.convert("RGB").save(output, format="PNG", optimize=False)


def copy_tree_assets() -> None:
    targets = [
        ROOT / "adapters" / "unity" / "Runtime" / "Assets",
        ROOT / "adapters" / "godot" / "addons" / "rainport_ui" / "assets",
        ROOT / "adapters" / "cocos" / "assets" / "rainport-ui" / "textures",
    ]
    for target in targets:
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(ROOT / "assets" / "png" / "1x", target / "1x")
        shutil.copytree(ROOT / "assets" / "png" / "2x", target / "2x")
        shutil.copy2(ROOT / "generated" / "asset-slices.json", target / "asset-slices.json")

    font_source = ROOT / "assets" / "fonts"
    if font_source.exists() and any(font_source.glob("*.ttf")):
        font_targets = [
            ROOT / "adapters" / "unity" / "Runtime" / "Fonts",
            ROOT / "adapters" / "godot" / "addons" / "rainport_ui" / "fonts",
            ROOT / "adapters" / "cocos" / "assets" / "rainport-ui" / "fonts",
        ]
        for target in font_targets:
            target.mkdir(parents=True, exist_ok=True)
            for font in sorted(font_source.glob("*.ttf")):
                shutil.copy2(font, target / font.name)


def copy_legal_files() -> None:
    for target in (
        ROOT / "adapters" / "unity",
        ROOT / "adapters" / "godot",
        ROOT / "adapters" / "cocos",
    ):
        shutil.copy2(ROOT / "LICENSE-POLICY.md", target / "LICENSE-POLICY.md")
        shutil.copy2(ROOT / "THIRD_PARTY_NOTICES.md", target / "THIRD_PARTY_NOTICES.md")
        licenses = target / "third-party"
        if licenses.exists():
            shutil.rmtree(licenses)
        shutil.copytree(ROOT / "third-party", licenses)


def tree_hash(paths: list[Path]) -> str:
    digest = hashlib.sha256()
    for path in sorted(paths, key=lambda item: item.as_posix()):
        digest.update(path.relative_to(ROOT).as_posix().encode("utf-8"))
        digest.update(path.read_bytes())
    return digest.hexdigest()


def main() -> None:
    asset_names = render_assets()
    generate_css_tokens()
    generate_unity_tokens()
    generate_godot_tokens()
    generate_godot_theme()
    generate_cocos_tokens()
    generate_contact_sheet()
    generate_loadout_preview()
    generate_result_preview()
    generate_engine_preview()
    copy_tree_assets()
    copy_legal_files()

    generated_paths = [
        *sorted((ROOT / "assets" / "source").glob("*.svg")),
        *sorted((ROOT / "assets" / "png" / "1x").glob("*.png")),
        *sorted((ROOT / "assets" / "png" / "2x").glob("*.png")),
        ROOT / "generated" / "asset-slices.json",
        ROOT / "generated" / "web" / "rainport.tokens.css",
        *sorted((ROOT / "preview").glob("*.png")),
    ]
    print(json.dumps({"version": TOKENS["version"], "assets": len(asset_names), "sha256": tree_hash(generated_paths)}, indent=2))


if __name__ == "__main__":
    main()
