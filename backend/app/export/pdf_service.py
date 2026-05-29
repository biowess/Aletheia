"""
Aletheia Clinical Workstation — PDF Export Service (v2)
=======================================================
A premium, print-ready PDF report generator using ReportLab.

Design language is derived directly from the Aletheia Design System
(BRANDING.md, index.css) — navy/slate palette, sharp corners, TeX Gyre Termes
serif, structured hierarchy, and intentional colour-coded severity/urgency.

Improvements over the original pdf_service.py:
  · Full Aletheia colour palette (navy, slate, semantic severity/urgency states)
  · Official wordmark logo in a structured cover header
  · Severity badge rendered with colour (bg fill + border + label)
  · Finding cards with coloured left-accent strip and tinted background
  · Differential table with confidence percentage + visual bar
  · Urgency + category badges for next-step entries
  · Numbered citation references with evidence-level annotation
  · Two-pass NumberedCanvas: running header, page N/M footer, divider rule
  · Section accent bars (navy 4-pt left strip) for visual hierarchy
  · Follow-up timeline rendered as structured entries, not bare bullets
  · Clean spacing, no clutter, print-first layout
"""

import os
import sys
import re
import textwrap
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image, KeepTogether, PageBreak,
)
try:
    from reportlab.platypus import HRFlowable
except ImportError:
    from reportlab.platypus.flowables import HRFlowable
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from app.core.config import settings
from app.models.case import Case
from app.models.report_version import ReportVersion
from app.models.follow_up_entry import FollowUpEntry


# ─────────────────────────────────────────────────────────────────────────────
# ASSET PATHS
# ─────────────────────────────────────────────────────────────────────────────

_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.abspath(os.path.join(_HERE, "../../.."))

# When running as a PyInstaller-frozen bundle, __file__ lives inside the
# temporary extraction directory and frontend/ is never present there.
# Assets are bundled via the `datas` key in backend.spec and land under
# sys._MEIPASS at the destination paths specified there.
def _asset(relative_path: str) -> str:
    """Resolve an asset path for both dev and frozen (PyInstaller) runs."""
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    
    # In Dev Mode, assets are located in the frontend source tree
    if relative_path.startswith("assets" + os.sep) or relative_path.startswith("assets/"):
        return os.path.join(_PROJECT_ROOT, "frontend", "src", relative_path)
        
    return os.path.join(_PROJECT_ROOT, relative_path)

LOGO_PATH = _asset(os.path.join("assets", "logo.png"))
FONT_DIR  = _asset(os.path.join("fonts", "tex-gyre-termes"))


# ─────────────────────────────────────────────────────────────────────────────
# FONT REGISTRATION
# ─────────────────────────────────────────────────────────────────────────────

FONT_NAME      = "Helvetica"
FONT_BOLD      = "Helvetica-Bold"
FONT_ITALIC    = "Helvetica-Oblique"
FONT_BOLD_ITALIC = "Helvetica-BoldOblique"
HAS_CUSTOM_FONT = False

try:
    def _font_path(stem: str) -> Optional[str]:
        for ext in (".ttf", ".otf"):
            p = os.path.join(FONT_DIR, f"{stem}{ext}")
            if os.path.exists(p):
                return p
        return None

    _r  = _font_path("texgyretermes-regular")
    _b  = _font_path("texgyretermes-bold")
    _i  = _font_path("texgyretermes-italic")
    _bi = _font_path("texgyretermes-bolditalic")

    if _r and _b and _i and _bi:
        pdfmetrics.registerFont(TTFont("TGT",    _r))
        pdfmetrics.registerFont(TTFont("TGT-B",  _b))
        pdfmetrics.registerFont(TTFont("TGT-I",  _i))
        pdfmetrics.registerFont(TTFont("TGT-BI", _bi))
        pdfmetrics.registerFontFamily(
            "TGT",
            normal="TGT", bold="TGT-B",
            italic="TGT-I", boldItalic="TGT-BI",
        )
        FONT_NAME       = "TGT"
        FONT_BOLD       = "TGT-B"
        FONT_ITALIC     = "TGT-I"
        FONT_BOLD_ITALIC = "TGT-BI"
        HAS_CUSTOM_FONT = True
except Exception:
    pass  # Graceful fallback to Helvetica family


# ─────────────────────────────────────────────────────────────────────────────
# ALETHEIA DESIGN TOKENS (translated to ReportLab HexColor)
# ─────────────────────────────────────────────────────────────────────────────

# Brand anchors
NAVY  = HexColor("#162C41")
SLATE = HexColor("#4F606F")

# Text hierarchy
C_TEXT_PRIMARY   = HexColor("#162C41")
C_TEXT_SECONDARY = HexColor("#4F606F")
C_TEXT_MUTED     = HexColor("#7C8A97")
C_TEXT_FAINT     = HexColor("#A7B4C0")

# Backgrounds & surfaces
C_BG_PRIMARY    = HexColor("#F5F8FB")
C_BG_SECONDARY  = HexColor("#EDF3F8")
C_SURFACE       = HexColor("#FFFFFF")
C_SURFACE_MUTED = HexColor("#F2F6FA")

# Borders
C_BORDER_SUBTLE  = HexColor("#E7EEF5")
C_BORDER_DEFAULT = HexColor("#D7E2EC")
C_BORDER_STRONG  = HexColor("#C4D3E0")

# Semantic states
C_STABLE   = HexColor("#3E6B61")   # low severity — teal-green
C_EVOLVING = HexColor("#C58A2B")   # moderate     — amber
C_DECLINED = HexColor("#9B4A4A")   # high/critical — dark red
C_INFO     = HexColor("#244B73")   # informational — deep navy

# ── Severity badge (bg, text, border) ────────────────────────────────────────
SEVERITY_PALETTE = {
    "low":      (HexColor("#EAF1EF"), C_STABLE,   HexColor("#8DBBB3")),
    "moderate": (HexColor("#FBF5E8"), C_EVOLVING, HexColor("#DEB86E")),
    "high":     (HexColor("#F5ECEC"), C_DECLINED, HexColor("#CE9898")),
    "critical": (HexColor("#EEE2E2"), C_DECLINED, HexColor("#BB7070")),
}

# ── Urgency badge (bg, text, border) ─────────────────────────────────────────
URGENCY_PALETTE = {
    "routine":  (C_SURFACE_MUTED,   C_TEXT_MUTED,  C_BORDER_DEFAULT),
    "urgent":   (HexColor("#FBF5E8"), C_EVOLVING,   HexColor("#DEB86E")),
    "emergent": (HexColor("#F5ECEC"), C_DECLINED,   HexColor("#CE9898")),
}

# ── Finding card (accent strip colour, background colour) ─────────────────────
FINDING_PALETTE = {
    "supporting":    (C_STABLE,   HexColor("#F0F7F5")),
    "contradictory": (C_EVOLVING, HexColor("#FDF8EE")),
}

# ── Confidence bar fill colour based on level ─────────────────────────────────
def _conf_colour(conf: float) -> HexColor:
    if conf >= 0.75:
        return C_INFO
    if conf >= 0.50:
        return HexColor("#5D7892")
    return HexColor("#A5B4C2")


# ─────────────────────────────────────────────────────────────────────────────
# PAGE GEOMETRY
# ─────────────────────────────────────────────────────────────────────────────

PAGE_W, PAGE_H = A4            # 595.27 × 841.89 pt
MARGIN_L   = 1.75 * cm         # 56.69 pt
MARGIN_R   = 1.75 * cm
MARGIN_T   = 2.0 * cm         # leaves space for running header
MARGIN_B   = 2.0 * cm         # leaves space for footer
BODY_W     = PAGE_W - MARGIN_L - MARGIN_R   # ≈ 481.89 pt

# Logo: original 1920 × 562 px — render at height 36 pt
_LOGO_AR   = 1920 / 562
LOGO_H     = 36.0
LOGO_W     = LOGO_H * _LOGO_AR   # ≈ 122.9 pt


# ─────────────────────────────────────────────────────────────────────────────
# PARAGRAPH STYLES
# ─────────────────────────────────────────────────────────────────────────────

def _ps(name, **kw) -> ParagraphStyle:
    """Convenience factory for ParagraphStyle with Aletheia defaults."""
    defaults = dict(
        fontName=FONT_NAME, fontSize=10, leading=14,
        textColor=C_TEXT_PRIMARY, spaceAfter=0, spaceBefore=0,
    )
    defaults.update(kw)
    return ParagraphStyle(name, **defaults)

PS_BODY      = _ps("body",     fontSize=10, leading=15, spaceAfter=6, alignment=TA_JUSTIFY)
PS_BODY_MUTED = _ps("bodyMuted", fontSize=9.5, leading=14,
                    textColor=C_TEXT_SECONDARY, spaceAfter=4)
PS_SMALL     = _ps("small",    fontSize=8.5, leading=12,
                    textColor=C_TEXT_MUTED)
PS_CAPTION   = _ps("caption",  fontSize=8,   leading=11,
                    textColor=C_TEXT_FAINT)

PS_H1 = _ps("h1",
    fontName=FONT_BOLD, fontSize=18, leading=22,
    textColor=NAVY, spaceAfter=4,
)
PS_H2 = _ps("h2",
    fontName=FONT_BOLD, fontSize=13, leading=17,
    textColor=NAVY, spaceBefore=2, spaceAfter=4,
)
PS_H3 = _ps("h3",
    fontName=FONT_BOLD, fontSize=11, leading=15,
    textColor=C_TEXT_PRIMARY, spaceBefore=2, spaceAfter=3,
)

PS_LABEL = _ps("label",
    fontName=FONT_BOLD, fontSize=8, leading=10,
    textColor=C_TEXT_MUTED,
)
PS_LABEL_NAVY = _ps("labelNavy",
    fontName=FONT_BOLD, fontSize=8, leading=10,
    textColor=NAVY,
)

PS_META_R = _ps("metaR",
    fontName=FONT_NAME, fontSize=9, leading=12,
    textColor=C_TEXT_SECONDARY, alignment=TA_RIGHT,
)

PS_FINDING_TITLE = _ps("ftitle",
    fontName=FONT_BOLD, fontSize=10, leading=14,
    textColor=C_TEXT_PRIMARY, spaceAfter=3,
)

PS_REF = _ps("ref",
    fontName=FONT_NAME, fontSize=8.5, leading=13,
    textColor=C_TEXT_SECONDARY, spaceAfter=5,
    leftIndent=16, firstLineIndent=-16,
)
PS_REF_BOLD = _ps("refbold",
    fontName=FONT_BOLD, fontSize=8.5, leading=13,
    textColor=C_TEXT_PRIMARY,
)

PS_TL_DATE  = _ps("tlDate",
    fontName=FONT_BOLD, fontSize=9, leading=12,
    textColor=C_INFO,
)
PS_TL_TITLE = _ps("tlTitle",
    fontName=FONT_NAME, fontSize=9.5, leading=13,
    textColor=C_TEXT_PRIMARY,
)
PS_TL_NOTE  = _ps("tlNote",
    fontName=FONT_ITALIC, fontSize=9, leading=12,
    textColor=C_TEXT_MUTED, spaceAfter=4,
)

PS_DIFF_NAME = _ps("diffName",
    fontName=FONT_BOLD, fontSize=10.5, leading=14,
    textColor=C_TEXT_PRIMARY,
)
PS_DIFF_CONF = _ps("diffConf",
    fontName=FONT_BOLD, fontSize=10, leading=14,
    textColor=C_INFO, alignment=TA_RIGHT,
)


# ─────────────────────────────────────────────────────────────────────────────
# UTILITY — XML ESCAPING
# ─────────────────────────────────────────────────────────────────────────────

def _xe(text: str) -> str:
    """Escape XML special chars for ReportLab Paragraph content."""
    return (text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;"))


def _cite_replace(text: str, idx_map: dict) -> str:
    """Replace {{cite:cN}} tokens with superscript [N] markers."""
    def _sub(m):
        cid = m.group(1)
        n   = idx_map.get(cid, "?")
        return f"<super><font size='7'>[{n}]</font></super>"
    return re.sub(r'\{\{cite:(\w+)\}\}', _sub, text)


def _safe(text: str, idx_map: dict | None = None) -> str:
    """Escape XML then substitute citation tokens."""
    t = _xe(text or "")
    if idx_map:
        t = _cite_replace(t, idx_map)
    return t


# ─────────────────────────────────────────────────────────────────────────────
# PRIMITIVE FLOWABLE HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _vspace(pts: float):
    return Spacer(1, pts)


def _rule(colour=C_BORDER_DEFAULT, thickness=0.5,
          space_before=6, space_after=6):
    return HRFlowable(
        width="100%", thickness=thickness, color=colour,
        spaceBefore=space_before, spaceAfter=space_after,
    )


def _navy_rule():
    return HRFlowable(
        width="100%", thickness=1.5, color=NAVY,
        spaceBefore=0, spaceAfter=0,
    )


# ─────────────────────────────────────────────────────────────────────────────
# INLINE BADGE HELPERS  (returned as Paragraph — embed in Table cells)
# ─────────────────────────────────────────────────────────────────────────────

def _badge_para(label: str, bg: HexColor, text_c: HexColor,
                border_c: HexColor, font_size: float = 7.5) -> Table:
    """Render a coloured rectangular badge as a 1-cell Table."""
    style = ParagraphStyle(
        f"_badge_{label}",
        fontName=FONT_BOLD, fontSize=font_size, leading=font_size + 2,
        textColor=text_c, alignment=TA_CENTER,
        spaceBefore=0, spaceAfter=0,
    )
    t = Table([[Paragraph(label.upper(), style)]])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), bg),
        ("BOX",           (0, 0), (-1, -1), 0.5, border_c),
        ("TOPPADDING",    (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return t


def severity_badge(severity: str) -> Table:
    bg, tc, bc = SEVERITY_PALETTE.get(severity.lower(),
                                       SEVERITY_PALETTE["moderate"])
    return _badge_para(severity, bg, tc, bc, font_size=8)


def urgency_badge(urgency: str) -> Table:
    bg, tc, bc = URGENCY_PALETTE.get(urgency.lower(),
                                      URGENCY_PALETTE["routine"])
    return _badge_para(urgency, bg, tc, bc, font_size=7.5)


def category_badge(category: str) -> Table:
    label = category.replace("_", " ")
    return _badge_para(label, C_SURFACE_MUTED, C_TEXT_MUTED, C_BORDER_DEFAULT,
                       font_size=7)


# ─────────────────────────────────────────────────────────────────────────────
# SECTION HEADER  — navy left-accent bar + bold heading
# ─────────────────────────────────────────────────────────────────────────────

def section_header(number: int, title: str) -> KeepTogether:
    """
    Section heading without the navy left bar – just bold text with bottom rule.
    """
    label = f"{number}.  {title.upper()}"
    para = Paragraph(label, PS_H2)
    rule = HRFlowable(width="100%", thickness=0.5, color=C_BORDER_DEFAULT,
                      spaceBefore=2, spaceAfter=6)
    return KeepTogether([para, rule, _vspace(4)])


# ─────────────────────────────────────────────────────────────────────────────
# FINDING CARD  — coloured left strip + tinted background
# ─────────────────────────────────────────────────────────────────────────────

def finding_card(
    finding_type: str,       # "supporting" | "contradictory"
    title_text: str,
    explanation: str,
    extra_label: str = "",   # strength or significance string
    idx_map: dict | None = None,
) -> KeepTogether:
    accent_c, bg_c = FINDING_PALETTE.get(finding_type, FINDING_PALETTE["supporting"])

    strip_w   = 4
    pad_w     = 10
    content_w = BODY_W - strip_w - pad_w - 8   # 8 = outer right padding

    items = [Paragraph(_safe(title_text), PS_FINDING_TITLE)]
    if explanation:
        items.append(Paragraph(_safe(explanation, idx_map), PS_BODY_MUTED))
    if extra_label:
        extra_style_map = {
            # strength
            "strong":   C_STABLE,
            "moderate": C_EVOLVING,
            "weak":     C_TEXT_MUTED,
        }
        lc = extra_style_map.get(extra_label.lower(), C_TEXT_MUTED)
        lps = _ps(f"el_{extra_label}",
                  fontName=FONT_BOLD, fontSize=8, leading=11,
                  textColor=lc, spaceBefore=4)
        items.append(Paragraph(extra_label.upper(), lps))

    inner = Table([[items]], colWidths=[content_w])
    inner.setStyle(TableStyle([
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING",   (0, 0), (-1, -1), 0),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
    ]))

    card = Table([["", inner]], colWidths=[strip_w, content_w + pad_w])
    card.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (0, -1), accent_c),
        ("BACKGROUND",    (1, 0), (1, -1), bg_c),
        ("BOX",           (0, 0), (-1, -1), 0.5,
         HexColor("#C4D3E0" if finding_type == "supporting" else "#DEB86E")),
        ("TOPPADDING",    (0, 0), (0, -1), 0),
        ("BOTTOMPADDING", (0, 0), (0, -1), 0),
        ("LEFTPADDING",   (0, 0), (-1, -1), 0),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
        ("TOPPADDING",    (1, 0), (1, -1), 8),
        ("BOTTOMPADDING", (1, 0), (1, -1), 8),
        ("LEFTPADDING",   (1, 0), (1, -1), 10),
        ("RIGHTPADDING",  (1, 0), (1, -1), 8),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
    ]))
    return KeepTogether([card, _vspace(5)])


# ─────────────────────────────────────────────────────────────────────────────
# DIFFERENTIAL ENTRY — name + confidence bar
# ─────────────────────────────────────────────────────────────────────────────

def differential_entry(
    rank: int,
    diagnosis: str,
    confidence: float,
    reasoning: str,
    idx_map: dict | None = None,
) -> KeepTogether:
    conf_pct = min(max(confidence, 0.0), 1.0)
    conf_str = f"{conf_pct * 100:.0f}%"
    bar_fill = _conf_colour(conf_pct)

    # Title line with rank and diagnosis
    title_para = Paragraph(f"<b>{rank}. {_safe(diagnosis)}</b>", PS_DIFF_NAME)

    # Reasoning (if any)
    reasoning_para = None
    if reasoning:
        reasoning_para = Paragraph(_safe(reasoning, idx_map), PS_BODY_MUTED)

    # Confidence bar: a filled rectangle inside a table
    bar_width = BODY_W - 60   # same width as differential card
    bar_height = 6
    filled_width = bar_width * conf_pct

    # Build the bar as two colored cells
    bar_data = [
        [Paragraph("", _ps("empty", fontSize=1)),   # placeholder left
         Paragraph("", _ps("empty", fontSize=1))]   # placeholder right
    ]
    bar_table = Table(bar_data, colWidths=[filled_width, bar_width - filled_width],
                      rowHeights=[bar_height])
    bar_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), bar_fill),
        ("BACKGROUND", (1, 0), (1, 0), C_BG_SECONDARY),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))

    # Percentage label aligned to the right of the bar
    conf_label = Paragraph(f"<b>{conf_str}</b>",
                           _ps("conf_label", fontName=FONT_BOLD, fontSize=8,
                               textColor=bar_fill, alignment=TA_RIGHT))

    # Assemble: title, reasoning, bar+label
    items = [title_para]
    if reasoning_para:
        items.append(reasoning_para)
        items.append(_vspace(4))
    items.append(bar_table)
    items.append(_vspace(4))
    items.append(conf_label)   # appears just below the bar, right-aligned
    items.append(_vspace(2))

    # Card wrapper with subtle border (same as before)
    inner = Table([[items]], colWidths=[BODY_W - 32])
    inner.setStyle(TableStyle([
        ("TOPPADDING",    (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING",   (0, 0), (-1, -1), 12),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 12),
        ("BOX",           (0, 0), (-1, -1), 0.5, C_BORDER_DEFAULT),
        ("BACKGROUND",    (0, 0), (-1, -1), C_SURFACE),
    ]))
    return KeepTogether([inner, _vspace(5)])


# ─────────────────────────────────────────────────────────────────────────────
# NEXT-STEP CARD
# ─────────────────────────────────────────────────────────────────────────────

def next_step_card(
    rank: int,
    title: str,
    category: str,
    urgency: str,
    rationale: str,
    expected_outcome: str = "",
    risks_of_delay: str = "",
) -> KeepTogether:
    urg_bg, urg_tc, urg_bc = URGENCY_PALETTE.get(
        urgency.lower(), URGENCY_PALETTE["routine"])

    # Badge row
    badge_row = Table(
        [[urgency_badge(urgency), _vspace(0), category_badge(category)]],
        colWidths=[None, 6, None],
        style=[
            ("LEFTPADDING",   (0, 0), (-1, -1), 0),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
            ("TOPPADDING",    (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ],
    )

    title_para = Paragraph(
        f"<b>{rank}. {_safe(title)}</b>",
        _ps("nstitle", fontName=FONT_BOLD, fontSize=10.5, leading=14,
            textColor=C_TEXT_PRIMARY),
    )

    items: list = [badge_row, _vspace(4), title_para]
    if rationale:
        items += [_vspace(3),
                  Paragraph(_safe(rationale), PS_BODY_MUTED)]
    if expected_outcome:
        items += [_vspace(3),
                  Paragraph(
                      f"<b>Expected outcome:</b> {_safe(expected_outcome)}",
                      PS_BODY_MUTED)]
    if risks_of_delay:
        rps = _ps("risk", fontName=FONT_ITALIC, fontSize=9.5, leading=13,
                  textColor=C_DECLINED, spaceAfter=0)
        items += [_vspace(3),
                  Paragraph(f"Risk of delay: {_safe(risks_of_delay)}", rps)]

    inner = Table([[items]], colWidths=[BODY_W - 32])
    inner.setStyle(TableStyle([
        ("TOPPADDING",    (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING",   (0, 0), (-1, -1), 12),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 12),
        ("BOX",           (0, 0), (-1, -1), 0.5, C_BORDER_DEFAULT),
        ("BACKGROUND",    (0, 0), (-1, -1), C_SURFACE),
    ]))
    return KeepTogether([inner, _vspace(5)])


# ─────────────────────────────────────────────────────────────────────────────
# MISSING-INFO CARD
# ─────────────────────────────────────────────────────────────────────────────

def missing_info_card(
    rank: int,
    item: str,
    category: str,
    why: str,
    impact: str = "",
    implications: str = "",
) -> KeepTogether:
    title_para = Paragraph(
        f"<b>{rank}. {_safe(item)}</b>",
        _ps("mititle", fontName=FONT_BOLD, fontSize=10, leading=14,
            textColor=C_TEXT_PRIMARY),
    )
    items: list = [
        Table([[category_badge(category)]], style=[
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ]),
        _vspace(4),
        title_para,
    ]
    for label, val in [
        ("Why it matters", why),
        ("Impact on assessment", impact),
        ("Possible implications", implications),
    ]:
        if val:
            items.append(_vspace(3))
            items.append(
                Paragraph(f"<b>{label}:</b> {_safe(val)}", PS_BODY_MUTED)
            )

    inner = Table([[items]], colWidths=[BODY_W - 32])
    inner.setStyle(TableStyle([
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING",   (0, 0), (-1, -1), 12),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 12),
        ("BOX",           (0, 0), (-1, -1), 0.5, C_BORDER_SUBTLE),
        ("BACKGROUND",    (0, 0), (-1, -1), C_SURFACE_MUTED),
    ]))
    return KeepTogether([inner, _vspace(5)])


# ─────────────────────────────────────────────────────────────────────────────
# CITATION / REFERENCE BLOCK
# ─────────────────────────────────────────────────────────────────────────────

# Evidence level short labels
_EV_LABELS = {
    "guideline":          "GUIDELINE",
    "meta_analysis":      "META",
    "systematic_review":  "SYS. REV.",
    "rct":                "RCT",
    "cohort":             "COHORT",
    "case_control":       "CASE-CTRL",
    "case_report":        "CASE RPT.",
    "expert_opinion":     "EXPERT",
}


def citation_block(citations: list, available_width: float = None) -> list:
    if not citations:
        return [Paragraph("No references recorded.", PS_BODY_MUTED)]

    # Fallback to BODY_W if no specific width is provided
    if available_width is None:
        # If you know your gray box has, say, 12pt padding on each side, 
        # you can default to: BODY_W - 24
        available_width = BODY_W - 45

    # Helper: insert <wbr> after characters that are safe to break on
    def _breakable_text(text):
        for char in ['/', '.', '_', '?', '&', '=', '-']:
            text = text.replace(char, char + '<wbr>')
        return text

    rows = []
    for i, cit in enumerate(citations, 1):
        if not isinstance(cit, dict):
            continue

        # Build citation text
        title   = cit.get("title") or cit.get("label") or "Untitled"
        authors = cit.get("authors", [])
        journal = cit.get("journal", "")
        year    = cit.get("year", "")
        pmid    = cit.get("pmid", "")
        doi     = cit.get("doi", "")
        url     = cit.get("canonicalUrl") or cit.get("url", "")
        ev_lvl  = cit.get("evidenceLevel", "")
        van     = cit.get("vancouverString", "")

        if van:
            body_txt = _xe(van)
        else:
            author_str = ""
            if authors:
                listed = authors[:3]
                suffix = " et al." if len(authors) > 3 else ""
                author_str = ", ".join(_xe(a) for a in listed) + _xe(suffix) + ". "
            raw = (
                author_str
                + f"<b>{_xe(title)}</b>"
                + (f". {_xe(journal)}" if journal else "")
                + (f". {_xe(str(year))}" if year else "")
            )
            body_txt = raw + ("" if raw.endswith(".") else ".")

        if pmid:
            body_txt += f" PMID {_xe(str(pmid))}."

        if doi:
            doi_display = _breakable_text(_xe(doi))
            body_txt += f" DOI: {doi_display}."

        if url and not pmid and not doi:
            url_display = _breakable_text(_xe(url))
            body_txt += f" <a href='{url}'><u>{url_display}</u></a>"

        ev_label = _EV_LABELS.get(ev_lvl.lower() if ev_lvl else "", "")
        badge = None
        if ev_label:
            badge = _badge_para(ev_label, C_BG_SECONDARY, C_TEXT_MUTED,
                                C_BORDER_DEFAULT, font_size=6.5)

        num_style = _ps(f"refnum{i}",
                        fontName=FONT_BOLD, fontSize=8.5, leading=13,
                        textColor=C_INFO)
        num_para = Paragraph(f"[{i}]", num_style)
        ref_para = Paragraph(body_txt, PS_REF)

        # --- FIX: Dynamic column width math based on available_width ---
        if badge:
            ref_col_width = available_width - 24 - 58
            row_tbl = Table(
                [[num_para, ref_para, badge]],
                colWidths=[24, ref_col_width, 58],
                style=[
                    ("LEFTPADDING", (0,0), (-1,-1), 0),
                    ("RIGHTPADDING", (0,0), (-1,-1), 0),
                    ("TOPPADDING", (0,0), (-1,-1), 2),
                    ("BOTTOMPADDING", (0,0), (-1,-1), 2),
                    ("VALIGN", (0,0), (-1,-1), "TOP"),
                ]
            )
        else:
            ref_col_width = available_width - 24
            row_tbl = Table(
                [[num_para, ref_para]],
                colWidths=[24, ref_col_width],
                style=[
                    ("LEFTPADDING", (0,0), (-1,-1), 0),
                    ("RIGHTPADDING", (0,0), (-1,-1), 0),
                    ("TOPPADDING", (0,0), (-1,-1), 2),
                    ("BOTTOMPADDING", (0,0), (-1,-1), 2),
                    ("VALIGN", (0,0), (-1,-1), "TOP"),
                ]
            )
        rows.append(row_tbl)

    return rows

# ─────────────────────────────────────────────────────────────────────────────
# NUMBERED CANVAS — two-pass, running header + footer
# ─────────────────────────────────────────────────────────────────────────────

class _NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas that calculates total page count and draws:
      · Page 1: logo-only footer rule
      · Page 2+: slim running header (case title | version)
      · Every page: footer with Aletheia brand + generated date + page N/M
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved = []
        self._meta  = {}   # filled by PDFExportService before doc.build

    def showPage(self):
        self._saved.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        n = len(self._saved)
        for state in self._saved:
            self.__dict__.update(state)
            self._draw_decorations(n)
            super().showPage()
        super().save()

    def _draw_decorations(self, total: int):
        self.saveState()
        page = self._pageNumber

        # ── Footer ──────────────────────────────────────────────────────────
        fx = MARGIN_L
        fy = 20.0   # 20 pt from bottom

        self.setStrokeColor(C_BORDER_DEFAULT)
        self.setLineWidth(0.5)
        self.line(fx, fy + 11, PAGE_W - MARGIN_R, fy + 11)

        gen_date = self._meta.get("gen_date", "")
        footer_l = f"Aletheia Clinical Workstation  ·  Educational / research use only  ·  {gen_date}"
        footer_r = f"Page {page} of {total}"

        self.setFont(FONT_NAME, 7.5)
        self.setFillColor(C_TEXT_MUTED)
        self.drawString(fx, fy, footer_l)
        self.drawRightString(PAGE_W - MARGIN_R, fy, footer_r)

        # ── Running header (pages 2+) ────────────────────────────────────────
        if page > 1:
            case_title   = self._meta.get("case_title", "")
            version_str  = self._meta.get("version_str", "")

            hx = MARGIN_L
            hy = PAGE_H - 20.0

            self.setFont(FONT_BOLD, 7.5)
            self.setFillColor(NAVY)
            self.drawString(hx, hy, "CLINICAL REASONING REPORT")

            if case_title:
                self.setFont(FONT_NAME, 7.5)
                self.setFillColor(C_TEXT_SECONDARY)
                self.drawString(hx + 152, hy, f"·  {case_title}")

            if version_str:
                self.setFont(FONT_NAME, 7.5)
                self.drawRightString(PAGE_W - MARGIN_R, hy, version_str)

            self.setStrokeColor(C_BORDER_SUBTLE)
            self.setLineWidth(0.5)
            self.line(hx, hy - 4, PAGE_W - MARGIN_R, hy - 4)

        self.restoreState()


# ─────────────────────────────────────────────────────────────────────────────
# PDF EXPORT SERVICE
# ─────────────────────────────────────────────────────────────────────────────

class PDFExportService:
    """
    Generates a premium, print-ready PDF report for an Aletheia ReportVersion.

    Drop-in replacement for the original PDFExportService; same public API:
        pdf_path = PDFExportService().generate_report_pdf(report, case, follow_ups)
    """

    def __init__(self, output_dir: str = settings.pdf_output_dir):
        self.output_dir = output_dir

    # ── Internal helpers ─────────────────────────────────────────────────────

    def _ensure_output_dir(self) -> None:
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)

    def _cite_idx_map(self, citations: list) -> dict:
        return {
            c["id"]: i + 1
            for i, c in enumerate(citations or [])
            if isinstance(c, dict) and "id" in c
        }

    # ── Cover / page-1 header block ──────────────────────────────────────────

    def _build_cover_header(
        self,
        case: Case,
        report: ReportVersion,
        gen_date_str: str,
    ) -> list:
        story = []

        # Logo + title table
        logo_img: Image | str = ""
        if os.path.exists(LOGO_PATH):
            logo_img = Image(LOGO_PATH, width=LOGO_W, height=LOGO_H)

        title_style = _ps(
            "coverTitle",
            fontName=FONT_BOLD, fontSize=17, leading=21,
            textColor=NAVY, alignment=TA_RIGHT,
        )
        sub_style = _ps(
            "coverSub",
            fontName=FONT_NAME, fontSize=9, leading=13,
            textColor=C_TEXT_SECONDARY, alignment=TA_RIGHT,
        )

        right = [
            Paragraph("CLINICAL REASONING REPORT", title_style),
            _vspace(3),
            Paragraph(f"Version {report.version_number}  ·  {gen_date_str}", sub_style),
        ]

        hdr = Table(
            [[logo_img, right]],
            colWidths=[LOGO_W + 12, BODY_W - LOGO_W - 0],
        )
        hdr.setStyle(TableStyle([
            ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING",   (0, 0), (-1, -1), -6),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
            ("TOPPADDING",    (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ]))
        story.append(hdr)
        story.append(_vspace(10))
        story.append(_navy_rule())
        story.append(_vspace(10))

        # Case meta row
        severity  = ""
        if isinstance(report.summary, dict):
            severity = report.summary.get("severity", "")

        left_items: list = [
            Paragraph(
                f"<b>{_xe(case.title)}</b>",
                _ps("caseTitle", fontName=FONT_BOLD, fontSize=12,
                    leading=16, textColor=NAVY),
            ),
        ]
        if case.notes:
            left_items.append(
                Paragraph(_xe(str(case.notes)[:200]), PS_BODY_MUTED)
            )

        right_items: list = [Paragraph(gen_date_str, PS_META_R)]
        if severity:
            right_items.append(_vspace(4))
            right_items.append(
                Table(
                    [[severity_badge(severity)]],
                    style=[
                        ("LEFTPADDING",   (0, 0), (-1, -1), 0),
                        ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
                        ("TOPPADDING",    (0, 0), (-1, -1), 0),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                        ("ALIGN",         (0, 0), (-1, -1), "RIGHT"),
                    ],
                )
            )

        meta_tbl = Table(
            [[left_items, right_items]],
            colWidths=[BODY_W * 0.65, BODY_W * 0.35],
        )
        meta_tbl.setStyle(TableStyle([
            ("VALIGN",        (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING",   (0, 0), (-1, -1), 0),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
            ("TOPPADDING",    (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ]))
        story.append(meta_tbl)
        story.append(_vspace(6))
        story.append(_rule(C_BORDER_DEFAULT, space_before=0, space_after=0))
        story.append(_vspace(10))

        # AI model chip
        model_line = ""
        if report.ai_provider:
            model_line = (
                f"Generated by {_xe(report.ai_provider)}"
                + (f" ({_xe(report.ai_model)})" if report.ai_model else "")
                + ("  ·  Grounding: On" if report.grounding_used else "")
            )
            story.append(Paragraph(model_line, PS_CAPTION))
            story.append(_vspace(6))

        return story

    # ── Clinical summary block ───────────────────────────────────────────────

    def _build_summary(self, report: ReportVersion, idx_map: dict) -> list:
        if not isinstance(report.summary, dict):
            return []
        overview = report.summary.get("overview", "")
        if not overview:
            return []
        story = [section_header(1, "Clinical Summary")]
        text  = _safe(overview, idx_map)
        story.append(Paragraph(text, PS_BODY))
        return story

    # ── Supporting findings ─────────────────────────────────────────────────

    def _build_supporting(self, report: ReportVersion, idx_map: dict) -> list:
        findings = [f for f in (report.supporting_findings or [])
                    if isinstance(f, dict)]
        if not findings:
            return []
        story = [section_header(2, "Supporting Findings")]
        for sf in findings:
            story.append(finding_card(
                "supporting",
                sf.get("finding", ""),
                sf.get("explanation", ""),
                extra_label=sf.get("strength", ""),
                idx_map=idx_map,
            ))
        return story

    # ── Contradictory findings ──────────────────────────────────────────────

    def _build_contradictory(self, report: ReportVersion, idx_map: dict) -> list:
        findings = [f for f in (report.contradictory_findings or [])
                    if isinstance(f, dict)]
        if not findings:
            return []
        story = [section_header(3, "Contradictory Findings")]
        for cf in findings:
            story.append(finding_card(
                "contradictory",
                cf.get("finding", ""),
                cf.get("explanation", ""),
                extra_label=cf.get("significance", ""),
                idx_map=idx_map,
            ))
        return story

    # ── Differentials ───────────────────────────────────────────────────────

    def _build_differentials(self, report: ReportVersion, idx_map: dict) -> list:
        diffs = [d for d in (report.differentials or [])
                 if isinstance(d, dict)]
        if not diffs:
            return []
        story = [section_header(4, "Assessment & Differential Diagnoses")]
        # Sort by confidence descending
        diffs_sorted = sorted(diffs,
                              key=lambda x: float(x.get("confidence", 0)),
                              reverse=True)
        for i, diff in enumerate(diffs_sorted, 1):
            story.append(differential_entry(
                i,
                diff.get("diagnosis", "Unknown"),
                float(diff.get("confidence", 0.5)),
                diff.get("reasoning", ""),
                idx_map=idx_map,
            ))
        return story

    # ── Next steps ──────────────────────────────────────────────────────────

    def _build_next_steps(self, report: ReportVersion) -> list:
        steps = [s for s in (report.next_steps or [])
                 if isinstance(s, dict)]
        if not steps:
            return []
        story = [section_header(5, "Suggested Next Steps")]
        for i, step in enumerate(steps, 1):
            story.append(next_step_card(
                i,
                step.get("title", ""),
                step.get("category", "diagnostic"),
                step.get("urgency", "routine"),
                step.get("rationale", ""),
                step.get("expected_outcome", ""),
                step.get("risks_of_delay", ""),
            ))
        return story

    # ── Missing information ──────────────────────────────────────────────────

    def _build_missing(self, report: ReportVersion) -> list:
        items = [m for m in (report.missing_information or [])
                 if isinstance(m, dict)]
        if not items:
            return []
        story = [section_header(6, "Missing Information")]
        for i, mi in enumerate(items, 1):
            story.append(missing_info_card(
                i,
                mi.get("item", ""),
                mi.get("category", "labs"),
                mi.get("why_it_matters", ""),
                mi.get("impact_on_assessment", ""),
                mi.get("possible_implications", ""),
            ))
        return story

    # ── References ──────────────────────────────────────────────────────────

    def _build_references(self, report: ReportVersion) -> list:
        citations = report.citations or []
        if not citations:
            return []
        story = [section_header(7, "References")]

        # Outer container with subtle background
        ref_rows = citation_block(citations)

        wrapper = Table([[ref_rows]], colWidths=[BODY_W - 32])
        wrapper.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, -1), C_BG_PRIMARY),
            ("BOX",           (0, 0), (-1, -1), 0.5, C_BORDER_SUBTLE),
            ("TOPPADDING",    (0, 0), (-1, -1), 12),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
            ("LEFTPADDING",   (0, 0), (-1, -1), 10),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 5),
        ]))
        story.append(wrapper)
        return story

    # ── Follow-up timeline ───────────────────────────────────────────────────

    def _build_followups(
        self, follow_ups: list["FollowUpEntry"]
    ) -> list:
        if not follow_ups:
            return []

        story = [section_header(8, "Follow-Up Timeline")]

        sorted_fu = sorted(
            follow_ups,
            key=lambda x: x.created_at or datetime.min.replace(tzinfo=timezone.utc),
        )

        for fu in sorted_fu:
            date_str = (
                fu.created_at.strftime("%Y-%m-%d  %H:%M UTC")
                if fu.created_at else "Unknown date"
            )
            items: list = [
                Paragraph(date_str, PS_TL_DATE),
                _vspace(2),
                Paragraph(_xe(fu.title or ""), PS_TL_TITLE),
            ]

            entry_type = (fu.entry_type or "").replace("_", " ").title()
            if entry_type:
                items.append(
                    Table([[category_badge(fu.entry_type or "")]],
                          style=[
                              ("LEFTPADDING",   (0, 0), (-1, -1), 0),
                              ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
                              ("TOPPADDING",    (0, 0), (-1, -1), 2),
                              ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                          ])
                )

            if fu.free_text_note:
                items.append(_vspace(3))
                items.append(Paragraph(
                    _xe(fu.free_text_note[:400]), PS_TL_NOTE))

            # Dot indicator column (navy circle) + content column
            dot_style = _ps("dot",
                            fontName=FONT_BOLD, fontSize=14,
                            textColor=NAVY, leading=14)
            dot_cell  = [Paragraph("·", dot_style)]

            row_tbl = Table(
                [[dot_cell, items]],
                colWidths=[16, BODY_W - 16],
            )
            row_tbl.setStyle(TableStyle([
                ("LEFTPADDING",   (0, 0), (-1, -1), 0),
                ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
                ("TOPPADDING",    (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                ("VALIGN",        (0, 0), (-1, -1), "TOP"),
            ]))
            story.append(KeepTogether([row_tbl, _vspace(6)]))

        return story

    # ── Main entry point ─────────────────────────────────────────────────────

    def generate_report_pdf(
        self,
        report: ReportVersion,
        case: Case,
        follow_ups: list["FollowUpEntry"],
    ) -> str:
        self._ensure_output_dir()

        file_path = os.path.join(self.output_dir,
                                 f"report_{report.id}.pdf")

        doc = SimpleDocTemplate(
            file_path,
            pagesize=A4,
            leftMargin=MARGIN_L,
            rightMargin=MARGIN_R,
            topMargin=MARGIN_T,
            bottomMargin=MARGIN_B,
            title=f"Clinical Report — {case.title}",
            author="Aletheia Clinical Workstation",
        )

        gen_date_str = (
            report.created_at.strftime("%Y-%m-%d  %H:%M UTC")
            if report.created_at
            else datetime.now(timezone.utc).strftime("%Y-%m-%d  %H:%M UTC")
        )

        idx_map = self._cite_idx_map(report.citations)

        # ── Assemble story ───────────────────────────────────────────────────
        story: list = []
        story += self._build_cover_header(case, report, gen_date_str)
        story += self._build_summary(report, idx_map)
        story += self._build_supporting(report, idx_map)
        story += self._build_contradictory(report, idx_map)
        story += self._build_differentials(report, idx_map)
        story += self._build_next_steps(report)
        story += self._build_missing(report)
        story += self._build_references(report)
        story += self._build_followups(follow_ups)

        # ── Canvas factory with injected metadata ────────────────────────────
        meta = {
            "gen_date":    gen_date_str,
            "case_title":  case.title[:60] if case.title else "",
            "version_str": f"v{report.version_number}",
        }

        class _Canvas(_NumberedCanvas):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self._meta = meta

        doc.build(story, canvasmaker=_Canvas)
        return os.path.abspath(file_path)