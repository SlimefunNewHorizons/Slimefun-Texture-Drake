#!/usr/bin/env python3
"""
Generador de:
1) Badges de rangos con estetica griega (Dorado #D4AF37/#FFD700 + Morado Real #6A0DAD/#9B59B6 + laureles/meandro)
   SVG -> PNG nitido (4x, altura 44px para height=11 en Minecraft) via librsvg2 + libcairo2.
2) Modelos 3D de Auras de DrakesRankup (9 estilos) con cuboides reales en JSON + texturas 64x64 SVG->PNG.
"""
import ctypes
import json
import math
import os
import struct
from pathlib import Path

# --- librsvg2 + libcairo2 via ctypes ---
libcairo = ctypes.CDLL("libcairo.so.2")
librsvg = ctypes.CDLL("librsvg-2.so.2")

CAIRO_FORMAT_ARGB32 = 0

class RsvgRectangle(ctypes.Structure):
    _fields_ = [
        ("x", ctypes.c_double),
        ("y", ctypes.c_double),
        ("width", ctypes.c_double),
        ("height", ctypes.c_double),
    ]

libcairo.cairo_image_surface_create.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int]
libcairo.cairo_image_surface_create.restype = ctypes.c_void_p
libcairo.cairo_create.argtypes = [ctypes.c_void_p]
libcairo.cairo_create.restype = ctypes.c_void_p
libcairo.cairo_surface_write_to_png.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
libcairo.cairo_surface_write_to_png.restype = ctypes.c_int
libcairo.cairo_destroy.argtypes = [ctypes.c_void_p]
libcairo.cairo_surface_destroy.argtypes = [ctypes.c_void_p]

librsvg.rsvg_handle_new_from_data.argtypes = [ctypes.c_char_p, ctypes.c_size_t, ctypes.POINTER(ctypes.c_void_p)]
librsvg.rsvg_handle_new_from_data.restype = ctypes.c_void_p
librsvg.rsvg_handle_render_document.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.POINTER(RsvgRectangle), ctypes.POINTER(ctypes.c_void_p)]
librsvg.rsvg_handle_render_document.restype = ctypes.c_int
libgobject = ctypes.CDLL("libgobject-2.0.so.0")
libgobject.g_object_unref.argtypes = [ctypes.c_void_p]

def svg_to_png(svg_str: str, out_png: Path, width: int, height: int):
    data = svg_str.encode("utf-8")
    err = ctypes.c_void_p()
    handle = librsvg.rsvg_handle_new_from_data(data, len(data), ctypes.byref(err))
    if not handle:
        raise RuntimeError(f"rsvg_handle_new_from_data failed for {out_png}")
    surface = libcairo.cairo_image_surface_create(CAIRO_FORMAT_ARGB32, width, height)
    cr = libcairo.cairo_create(surface)
    vp = RsvgRectangle(0.0, 0.0, float(width), float(height))
    ok = librsvg.rsvg_handle_render_document(handle, cr, ctypes.byref(vp), ctypes.byref(err))
    if not ok:
        raise RuntimeError(f"rsvg_handle_render_document failed for {out_png}")
    out_png.parent.mkdir(parents=True, exist_ok=True)
    status = libcairo.cairo_surface_write_to_png(surface, str(out_png).encode("utf-8"))
    libcairo.cairo_destroy(cr)
    libcairo.cairo_surface_destroy(surface)
    libgobject.g_object_unref(handle)
    if status != 0:
        raise RuntimeError(f"cairo_surface_write_to_png failed ({status}) for {out_png}")

# --- 1. RANK BADGES (Greek Gold + Royal Purple + Laurel + Meander) ---
# (id, label, codepoint_hex, accent1, accent2, icon_type, bg_top, bg_bot)
BADGES = [
    # Staff
    ("rank_owner",     "DUEÑO",     "E140", "#FFD700", "#FFF3A1", "crown",   "#4B0B7A", "#22053B"),
    ("rank_admin",     "ADMIN",     "E141", "#FF9F1C", "#FFD166", "shield",  "#520D7A", "#26053D"),
    ("rank_dev",       "DEV",       "E142", "#E879F9", "#F5D0FE", "code",    "#4A0E78", "#210538"),
    ("rank_mod",       "MOD",       "E143", "#38BDF8", "#BAE6FD", "sword",   "#3B126E", "#1B0738"),
    ("rank_builder",   "BUILDER",   "E144", "#FBBF24", "#FEF08A", "hammer",  "#4A146B", "#220836"),
    ("rank_jefedev",   "JEFE DEV",  "E149", "#C084FC", "#F3E8FF", "crown",   "#5B1191", "#260542"),
    ("rank_helper",    "HELPER",    "E14A", "#4ADE80", "#BBF7D0", "star",    "#3A1268", "#1A0733"),
    ("rank_tutorsf",   "TUTOR SF",  "E14B", "#22D3EE", "#CFFAFE", "book",    "#3A1268", "#1A0733"),

    # Civiles / Especiales / Media / Booster
    ("rank_polis",     "POLIS",     "E145", "#D4AF37", "#FDE68A", "pillar",  "#3E1063", "#1E0736"),
    ("rank_streamer",  "STREAMER",  "E147", "#F472B6", "#FBCFE8", "play",    "#5A1080", "#29063D"),
    ("rank_sfmaster",  "SFMASTER",  "E148", "#FB923C", "#FED7AA", "gear",    "#4F1173", "#240638"),
    ("rank_oldschool", "OLDSCHOOL", "E14C", "#FACC15", "#FEF08A", "laurel",  "#45106B", "#210636"),
    ("rank_booster",   "BOOSTER",   "E14D", "#F472B6", "#FFFFFF", "diamond", "#7E22CE", "#3B0764"),
    ("rank_creador",   "CREADOR",   "E14E", "#E056FD", "#F5D0FE", "star",    "#5A1080", "#29063D"),
    ("rank_rankup",    "RANKUP",    "E14F", "#FFD700", "#C084FC", "flame",   "#4F0E7A", "#24063B"),

    # VIPs Mitologicos (Dioses & Titanes)
    ("rank_zeus",      "ZEUS",      "E146", "#FFE033", "#FFFBEB", "bolt",    "#4E107D", "#23053D"),
    ("rank_hercules",  "HERCULES",  "E150", "#F59E0B", "#FDE68A", "shield",  "#4A1173", "#220638"),
    ("rank_hestia",    "HESTIA",    "E151", "#FB7185", "#FFE4E6", "flame",   "#4E1175", "#24063A"),
    ("rank_hermes",    "HERMES",    "E152", "#38BDF8", "#E0F2FE", "wing",    "#3F1170", "#1D0638"),
    ("rank_hefesto",   "HEFESTO",   "E153", "#F87171", "#FEE2E2", "hammer",  "#4F0F6E", "#260536"),
    ("rank_artemisa",  "ARTEMISA",  "E154", "#4ADE80", "#DCFCE7", "moon",    "#3D126B", "#1B0736"),
    ("rank_afrodita",  "AFRODITA",  "E155", "#F472B6", "#FCE7F3", "heart",   "#541078", "#27063B"),
    ("rank_atenea",    "ATENEA",    "E156", "#C084FC", "#F3E8FF", "shield",  "#521085", "#240540"),
    ("rank_thor",      "THOR",      "E157", "#60A5FA", "#DBEAFE", "bolt",    "#3C1170", "#1B0638"),
    ("rank_anubis",    "ANUBIS",    "E158", "#A855F7", "#E9D5FF", "eye",     "#360B5E", "#160429"),
    ("rank_poseidon",  "POSEIDON",  "E159", "#22D3EE", "#CFFAFE", "trident", "#32136E", "#160736"),
    ("rank_titan",     "TITAN",     "E15A", "#FF3366", "#FFD700", "crown",   "#590B6E", "#290433"),
    ("rank_penelope",  "PENELOPE",  "E15B", "#FFB7C5", "#FFF0F3", "crown",   "#57107A", "#28063B"),
]

def icon_svg(kind: str, c1: str, c2: str) -> str:
    # Drawn in 16x16 box translated to (x=11, y=14) -> fits nicely inside 44px height badge
    shapes = {
        "crown": f'<path d="M1 12 L2.5 5 L5.5 8.5 L8 3 L10.5 8.5 L13.5 5 L15 12 Z" fill="{c1}" stroke="#1A0529" stroke-width="1"/><rect x="2" y="12.2" width="12" height="2" rx="0.6" fill="{c2}"/>',
        "shield": f'<path d="M8 1.5 L14 4 V8.5 C14 12 11 14 8 15 C5 14 2 12 2 8.5 V4 Z" fill="{c1}" stroke="#1A0529" stroke-width="1"/><path d="M8 3.5 V12.8 M4.5 7.5 H11.5" stroke="{c2}" stroke-width="1.3"/>',
        "code": f'<path d="M5.5 4 L1.8 8 L5.5 12 M10.5 4 L14.2 8 L10.5 12 M9 3 L7 13" fill="none" stroke="{c1}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>',
        "sword": f'<path d="M13 2 L14 3 L6.5 10.5 L5.5 9.5 Z" fill="{c2}"/><path d="M13.5 2.5 L6 10" stroke="{c1}" stroke-width="2" stroke-linecap="round"/><path d="M4 8.5 L7.5 12 M3 13 L5.5 10.5" stroke="#FFD700" stroke-width="1.8" stroke-linecap="round"/>',
        "hammer": f'<rect x="3" y="2.5" width="10" height="4.5" rx="1" fill="{c1}" stroke="#1A0529" stroke-width="0.9"/><rect x="7" y="7" width="2.2" height="7.5" rx="0.6" fill="#FFD700"/>',
        "star": f'<path d="M8 1.2 L10 5.8 L15 6.3 L11.2 9.5 L12.4 14.5 L8 11.8 L3.6 14.5 L4.8 9.5 L1 6.3 L6 5.8 Z" fill="{c1}" stroke="#1A0529" stroke-width="0.8"/>',
        "book": f'<path d="M2 3.5 C4.5 2.5 6.8 3 8 4.2 C9.2 3 11.5 2.5 14 3.5 V12.5 C11.5 11.5 9.2 12 8 13.2 C6.8 12 4.5 11.5 2 12.5 Z" fill="{c1}" stroke="#1A0529" stroke-width="0.9"/><line x1="8" y1="4.2" x2="8" y2="13.2" stroke="{c2}" stroke-width="1.1"/>',
        "pillar": f'<rect x="2.5" y="2" width="11" height="2" rx="0.5" fill="#FFD700"/><rect x="4" y="4.2" width="2" height="8" fill="{c2}"/><rect x="7" y="4.2" width="2" height="8" fill="{c1}"/><rect x="10" y="4.2" width="2" height="8" fill="{c2}"/><rect x="2.5" y="12.2" width="11" height="2" rx="0.5" fill="#FFD700"/>',
        "play": f'<polygon points="4,2.5 14,8 4,13.5" fill="{c1}" stroke="#1A0529" stroke-width="0.9"/><polygon points="5.5,4.8 11.2,8 5.5,11.2" fill="{c2}" opacity="0.65"/>',
        "gear": f'<circle cx="8" cy="8" r="4.8" fill="{c1}" stroke="#1A0529" stroke-width="0.9"/><circle cx="8" cy="8" r="2.1" fill="#2A0845"/>' + "".join(f'<rect x="7" y="1" width="2" height="2.4" fill="#FFD700" transform="rotate({a} 8 8)"/>' for a in range(0, 360, 45)),
        "laurel": f'<path d="M5 13 C2 10 2 5 6 2.5 M11 13 C14 10 14 5 10 2.5" fill="none" stroke="#FFD700" stroke-width="1.8" stroke-linecap="round"/><circle cx="8" cy="8" r="2.4" fill="{c1}"/>',
        "diamond": f'<polygon points="8,1 14.5,6.5 8,15 1.5,6.5" fill="{c1}" stroke="#1A0529" stroke-width="0.9"/><polygon points="8,1 11.5,6.5 8,15 4.5,6.5" fill="{c2}" opacity="0.7"/><line x1="1.5" y1="6.5" x2="14.5" y2="6.5" stroke="#FFFFFF" stroke-width="0.9"/>',
        "flame": f'<path d="M8 1 C11.5 4.5 13.5 7.5 12.5 11 C11.8 13.5 10 14.8 8 14.8 C6 14.8 4.2 13.5 3.5 11 C2.5 7.5 4.5 4.5 8 1 Z" fill="{c1}" stroke="#1A0529" stroke-width="0.8"/><path d="M8 5.5 C9.8 7.5 10.5 9.5 9.8 11.5 C9.4 12.8 8.7 13.4 8 13.4 C7.3 13.4 6.6 12.8 6.2 11.5 C5.5 9.5 6.2 7.5 8 5.5 Z" fill="{c2}"/>',
        "bolt": f'<polygon points="9.5,1 3,9 7.8,9 6.2,15 13,6.8 8.4,6.8" fill="{c1}" stroke="#1A0529" stroke-width="0.8"/>',
        "wing": f'<path d="M2 12 C4 6 8 3 14 2.5 C12 5.5 11.5 7 13 8 C10 8.5 9.5 10 11 11 C8 11.5 5 12.5 2 12 Z" fill="{c1}" stroke="#1A0529" stroke-width="0.8"/>',
        "moon": f'<path d="M10.8 2.2 A6.2 6.2 0 1 0 10.8 13.8 A4.8 4.8 0 1 1 10.8 2.2 Z" fill="{c1}" stroke="#1A0529" stroke-width="0.8"/>',
        "heart": f'<path d="M8 14 C8 14 2 10 2 5.8 C2 3.5 3.8 2 5.8 2 C7 2 7.7 2.8 8 3.6 C8.3 2.8 9 2 10.2 2 C12.2 2 14 3.5 14 5.8 C14 10 8 14 8 14 Z" fill="{c1}" stroke="#1A0529" stroke-width="0.8"/>',
        "eye": f'<path d="M1.5 8 Q8 2.5 14.5 8 Q8 13.5 1.5 8 Z" fill="{c2}" stroke="#1A0529" stroke-width="0.9"/><circle cx="8" cy="8" r="2.6" fill="{c1}"/><circle cx="8" cy="8" r="1.1" fill="#1A0529"/>',
        "trident": f'<path d="M8 2 V14.5 M4 3 V7.5 C4 9 6 9.5 8 9.5 C10 9.5 12 9 12 7.5 V3" fill="none" stroke="{c1}" stroke-width="1.8" stroke-linecap="round"/><polygon points="8,1 6.5,3.5 9.5,3.5" fill="{c2}"/>',
    }
    return shapes.get(kind, shapes["star"])

def make_badge_svg(label: str, c1: str, c2: str, icon_kind: str, bg_top: str, bg_bot: str):
    # Height = 44px (renders at height=11 in Minecraft => 4x HiDPI crisp!)
    # Width scales dynamically with label length so every badge is balanced and readable
    H = 44
    text_w = int(len(label) * 16.5)
    W = max(124, 52 + text_w + 26)
    # Round W to multiple of 4 for clean pixel scaling
    W = ((W + 3) // 4) * 4

    # Greek meander pattern ticks along top/bottom inner gold trim
    meander_top = "".join(
        f'<rect x="{x}" y="5" width="6" height="2" fill="#FFD700" opacity="0.55"/>'
        f'<rect x="{x+4}" y="7" width="2" height="2" fill="#D4AF37" opacity="0.45"/>'
        for x in range(18, W - 22, 12)
    )
    meander_bot = "".join(
        f'<rect x="{x}" y="{H-7}" width="6" height="2" fill="#FFD700" opacity="0.55"/>'
        for x in range(18, W - 22, 12)
    )

    # Left & right subtle golden laurel leaves on the outer frame
    laurel_l = (
        '<path d="M5,22 C2,17 4,11 9,9 C7,14 7,17 8,22 C7,27 7,30 9,35 C4,33 2,27 5,22 Z" fill="url(#goldGrad)" stroke="#1A0529" stroke-width="1"/>'
        '<ellipse cx="6" cy="14" rx="2.2" ry="3.5" transform="rotate(-25 6 14)" fill="#FFD700"/>'
        '<ellipse cx="6" cy="30" rx="2.2" ry="3.5" transform="rotate(25 6 30)" fill="#FFD700"/>'
    )
    laurel_r = (
        f'<path d="M{W-5},22 C{W-2},17 {W-4},11 {W-9},9 C{W-7},14 {W-7},17 {W-8},22 C{W-7},27 {W-7},30 {W-9},35 C{W-4},33 {W-2},27 {W-5},22 Z" fill="url(#goldGrad)" stroke="#1A0529" stroke-width="1"/>'
        f'<ellipse cx="{W-6}" cy="14" rx="2.2" ry="3.5" transform="rotate(25 {W-6} 14)" fill="#FFD700"/>'
        f'<ellipse cx="{W-6}" cy="30" rx="2.2" ry="3.5" transform="rotate(-25 {W-6} 30)" fill="#FFD700"/>'
    )

    text_x = 40 + (W - 56) // 2
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
  <defs>
    <linearGradient id="bgGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="{bg_top}"/>
      <stop offset="55%" stop-color="#350959"/>
      <stop offset="100%" stop-color="{bg_bot}"/>
    </linearGradient>
    <linearGradient id="goldGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#FFF2A6"/>
      <stop offset="38%" stop-color="#FFD700"/>
      <stop offset="72%" stop-color="#D4AF37"/>
      <stop offset="100%" stop-color="#8C6414"/>
    </linearGradient>
    <linearGradient id="textGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#FFFFFF"/>
      <stop offset="45%" stop-color="{c2}"/>
      <stop offset="100%" stop-color="{c1}"/>
    </linearGradient>
  </defs>

  <!-- Outer dark silhouette for crisp contrast on any chat background -->
  <rect x="6" y="2" width="{W-12}" height="{H-4}" rx="7" fill="#120420"/>

  <!-- Golden Greek metallic frame -->
  <rect x="8" y="3.5" width="{W-16}" height="{H-7}" rx="6" fill="url(#goldGrad)"/>

  <!-- Royal purple interior plaque -->
  <rect x="11" y="6.5" width="{W-22}" height="{H-13}" rx="4" fill="url(#bgGrad)"/>

  <!-- Subtle top glossy sheen -->
  <rect x="12" y="7" width="{W-24}" height="12" rx="3" fill="#FFFFFF" opacity="0.10"/>

  <!-- Greek meander trim -->
  {meander_top}
  {meander_bot}

  <!-- Golden laurel accents -->
  {laurel_l}
  {laurel_r}

  <!-- Emblem medallion socket -->
  <circle cx="27" cy="22" r="11" fill="#1A052E" stroke="#D4AF37" stroke-width="1.5"/>
  <g transform="translate(17.5, 12.5) scale(1.18)">
    {icon_svg(icon_kind, c1, c2)}
  </g>

  <!-- Rank label with hard drop shadow -->
  <text x="{text_x}" y="29.5" text-anchor="middle" font-family="DejaVu Sans, Liberation Sans, sans-serif" font-weight="900" font-size="21" letter-spacing="1.2" fill="#12031F">{label}</text>
  <text x="{text_x}" y="28" text-anchor="middle" font-family="DejaVu Sans, Liberation Sans, sans-serif" font-weight="900" font-size="21" letter-spacing="1.2" fill="url(#textGrad)">{label}</text>
</svg>'''
    return svg, W, H

# --- 2. 3D AURA MODELS FOR DRAKESRANKUP (9 AuraStyles) ---
AURAS = [
    ("aura_divine",      910001, "#FFD700", "#FFF4C2", "#9B59B6"),
    ("aura_ssj2",        910002, "#FFD728", "#FFFAC8", "#F59E0B"),
    ("aura_ssjgod",      910003, "#E61928", "#FF825A", "#991B1B"),
    ("aura_ssjblue",     910004, "#288CFF", "#BEF0FF", "#1D4ED8"),
    ("aura_mui",         910005, "#E2E8F0", "#FFFFFF", "#94A3B8"),
    ("aura_ultra_ego",   910006, "#9333EA", "#F0ABFC", "#581C87"),
    ("aura_gohan_beast", 910007, "#C026D3", "#FFFFFF", "#EF4444"),
    ("aura_broly",       910008, "#22C55E", "#D9F99D", "#15803D"),
    ("aura_kaioken",     910009, "#EF4444", "#FCA5A5", "#991B1B"),
]

def make_aura_texture_svg(c1: str, c2: str, c3: str) -> str:
    # 64x64 texture atlas:
    # Top-left (0..32, 0..32): golden/energy ring gradient with runes
    # Top-right (32..64, 0..32): bright crystal core
    # Bottom (0..64, 32..64): energy flame/ray streak
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="64" height="64">
  <defs>
    <linearGradient id="g1" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="{c2}"/>
      <stop offset="50%" stop-color="{c1}"/>
      <stop offset="100%" stop-color="{c3}"/>
    </linearGradient>
    <radialGradient id="g2" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#FFFFFF"/>
      <stop offset="55%" stop-color="{c2}"/>
      <stop offset="100%" stop-color="{c1}"/>
    </radialGradient>
  </defs>
  <rect x="0" y="0" width="32" height="32" fill="url(#g1)"/>
  <rect x="2" y="2" width="28" height="28" fill="none" stroke="#FFFFFF" stroke-width="2" opacity="0.65"/>
  <rect x="6" y="14" width="20" height="4" fill="#FFFFFF" opacity="0.5"/>
  <rect x="32" y="0" width="32" height="32" fill="url(#g2)"/>
  <rect x="0" y="32" width="64" height="32" fill="url(#g1)"/>
  <rect x="0" y="42" width="64" height="12" fill="{c2}" opacity="0.8"/>
</svg>'''

def make_aura_3d_model(aura_id: str) -> dict:
    """
    True 3D Minecraft cuboid model for DrakesRankup AuraHalo ItemDisplay:
    - Octagonal sacred floating ring (8 rotated beams around center [8, 8, 8])
    - 4 diagonal energy crystal spikes pointing outward
    - Central luminous octahedral core (2 crossed diamonds)
    All coordinates strictly inside [-16, 32] (Minecraft model limit!).
    """
    elements = []
    tex_ring = {"uv": [0, 0, 8, 8], "texture": "#aura"}
    tex_core = {"uv": [8, 0, 16, 8], "texture": "#aura"}
    tex_ray  = {"uv": [0, 8, 16, 16], "texture": "#aura"}

    def all_faces(face_def):
        return {d: dict(face_def) for d in ("north", "south", "east", "west", "up", "down")}

    # 8 ring segments (4 cardinal + 4 rotated 45 deg) forming a 3D sacred halo
    ring_bars = [
        # Cardinal ring bars
        ([3, 7.2, -3], [13, 8.8, -1.2], None),
        ([3, 7.2, 17.2], [13, 8.8, 19], None),
        ([-3, 7.2, 3], [-1.2, 8.8, 13], None),
        ([17.2, 7.2, 3], [19, 8.8, 13], None),
        # Diagonal ring bars (rotated 45 deg around Y at center 8,8,8)
        ([3, 7.4, -3], [13, 8.6, -1.2], {"origin": [8, 8, 8], "axis": "y", "angle": 45}),
        ([3, 7.4, 17.2], [13, 8.6, 19], {"origin": [8, 8, 8], "axis": "y", "angle": 45}),
        ([-3, 7.4, 3], [-1.2, 8.6, 13], {"origin": [8, 8, 8], "axis": "y", "angle": 45}),
        ([17.2, 7.4, 3], [19, 8.6, 13], {"origin": [8, 8, 8], "axis": "y", "angle": 45}),
    ]
    for frm, to, rot in ring_bars:
        el = {"from": frm, "to": to, "shade": False, "faces": all_faces(tex_ring)}
        if rot:
            el["rotation"] = rot
        elements.append(el)

    # 8 outward energy crown spikes (cardinal + diagonal, tilted slightly upward 22.5 deg)
    spikes = [
        ([7.2, 7.2, -7.5], [8.8, 8.8, -2.5], {"origin": [8, 8, -2.5], "axis": "x", "angle": -22.5}),
        ([7.2, 7.2, 18.5], [8.8, 8.8, 23.5], {"origin": [8, 8, 18.5], "axis": "x", "angle": 22.5}),
        ([-7.5, 7.2, 7.2], [-2.5, 8.8, 8.8], {"origin": [-2.5, 8, 8], "axis": "z", "angle": 22.5}),
        ([18.5, 7.2, 7.2], [23.5, 8.8, 8.8], {"origin": [18.5, 8, 8], "axis": "z", "angle": -22.5}),
    ]
    for frm, to, rot in spikes:
        elements.append({"from": frm, "to": to, "shade": False, "rotation": rot, "faces": all_faces(tex_ray)})

    # Central glowing star-crystal core (2 tilted cubes)
    elements.append({
        "from": [6, 6, 6], "to": [10, 10, 10], "shade": False,
        "rotation": {"origin": [8, 8, 8], "axis": "y", "angle": 45},
        "faces": all_faces(tex_core)
    })
    elements.append({
        "from": [6.4, 5.5, 6.4], "to": [9.6, 10.5, 9.6], "shade": False,
        "rotation": {"origin": [8, 8, 8], "axis": "x", "angle": 45},
        "faces": all_faces(tex_core)
    })

    return {
        "credit": "DrakesCraft Labs — DrakesRankup 3D Aura Halo",
        "textures": {
            "aura": f"drakescraft:item/aura/{aura_id}",
            "particle": f"drakescraft:item/aura/{aura_id}"
        },
        "elements": elements,
        "display": {
            "fixed": {"rotation": [0, 0, 0], "translation": [0, 0, 0], "scale": [1.35, 1.35, 1.35]},
            "head": {"rotation": [0, 0, 0], "translation": [0, 10, 0], "scale": [1.2, 1.2, 1.2]},
            "gui": {"rotation": [30, 45, 0], "translation": [0, 0, 0], "scale": [0.72, 0.72, 0.72]},
            "ground": {"rotation": [0, 0, 0], "translation": [0, 4, 0], "scale": [0.65, 0.65, 0.65]},
        }
    }

def main():
    out = Path("/tmp/drakes_v29_assets")
    if out.exists():
        import shutil
        shutil.rmtree(out)

    # 1. Generate Greek Rank Badges
    font_tex_dir = out / "assets/drakescraft/textures/font"
    font_svg_dir = out / "assets/drakescraft/textures/font/svg"
    font_svg_dir.mkdir(parents=True, exist_ok=True)
    badge_manifest = []
    for bid, label, cp, c1, c2, icon_kind, bg1, bg2 in BADGES:
        svg, w, h = make_badge_svg(label, c1, c2, icon_kind, bg1, bg2)
        (font_svg_dir / f"{bid}.svg").write_text(svg, encoding="utf-8")
        png_path = font_tex_dir / f"{bid}.png"
        svg_to_png(svg, png_path, w, h)
        # Verify PNG header
        raw = png_path.read_bytes()
        pw, ph = struct.unpack(">II", raw[16:24])
        assert (pw, ph) == (w, h), f"Mismatch {bid}: {pw}x{ph} != {w}x{h}"
        badge_manifest.append({
            "id": bid, "label": label, "codepoint": f"U+{cp}",
            "char": chr(int(cp, 16)), "file": f"drakescraft:font/{bid}.png",
            "width": pw, "height": ph, "bytes": len(raw)
        })

    # 2. Generate 9 DrakesRankup 3D Aura Models + Textures + 1.21.4+ Item Definitions
    aura_tex_dir = out / "assets/drakescraft/textures/item/aura"
    aura_svg_dir = out / "assets/drakescraft/textures/item/aura/svg"
    aura_mod_dir = out / "assets/drakescraft/models/item/aura"
    aura_itm_dir = out / "assets/drakescraft/items"
    for d in (aura_tex_dir, aura_svg_dir, aura_mod_dir, aura_itm_dir):
        d.mkdir(parents=True, exist_ok=True)

    aura_manifest = []
    for aid, cmd, c1, c2, c3 in AURAS:
        svg = make_aura_texture_svg(c1, c2, c3)
        (aura_svg_dir / f"{aid}.svg").write_text(svg, encoding="utf-8")
        png_path = aura_tex_dir / f"{aid}.png"
        svg_to_png(svg, png_path, 64, 64)

        model = make_aura_3d_model(aid)
        (aura_mod_dir / f"{aid}.json").write_text(json.dumps(model, indent=2), encoding="utf-8")

        item_def = {"model": {"type": "minecraft:model", "model": f"drakescraft:item/aura/{aid}"}}
        (aura_itm_dir / f"{aid}.json").write_text(json.dumps(item_def, indent=2), encoding="utf-8")

        aura_manifest.append({"id": aid, "custom_model_data": cmd, "item_model": f"drakescraft:{aid}"})

    (out / "manifest.json").write_text(json.dumps({"badges": badge_manifest, "auras": aura_manifest}, indent=2), encoding="utf-8")
    print(f"Generated {len(badge_manifest)} Greek badges and {len(aura_manifest)} 3D aura models successfully!")
    for b in badge_manifest[:6]:
        print(f"  Badge {b['id']:16s} {b['codepoint']} {b['width']}x{b['height']} ({b['bytes']}B)")
    print(f"  ... + {len(badge_manifest)-6} more badges (including rank_booster U+E14D)")

if __name__ == "__main__":
    main()
