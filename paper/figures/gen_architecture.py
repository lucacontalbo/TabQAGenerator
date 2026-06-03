#!/usr/bin/env python3
"""Generate the TabgenQA architecture diagram."""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

# ── colour palette ──────────────────────────────────────────────────────────
COL_FRONT  = "#4A90D9"   # blue  – frontend
COL_BACK   = "#5BA85B"   # green – backend
COL_EXT    = "#8E6BBF"   # purple – external / black-box
COL_EXTBG  = "#F3EEF9"
COL_FRONTBG= "#EEF4FC"
COL_BACKBG = "#EEF6EE"
COL_ARROW  = "#555555"
HATCH_COL  = "#C8B8E8"

fig, ax = plt.subplots(figsize=(13, 6.8))
ax.set_xlim(0, 13)
ax.set_ylim(0, 6.8)
ax.axis("off")

# ── helpers ─────────────────────────────────────────────────────────────────
def column_bg(x, y, w, h, color, label, label_color):
    """Draw a column background panel with a header label."""
    rect = FancyBboxPatch((x, y), w, h,
                          boxstyle="round,pad=0.12",
                          linewidth=1.5, edgecolor=color,
                          facecolor=color + "22")   # 13 % alpha via hex
    ax.add_patch(rect)
    ax.text(x + w / 2, y + h + 0.07, label,
            ha="center", va="bottom",
            fontsize=11, fontweight="bold", color=label_color)

def box(x, y, w, h, text, facecolor, edgecolor, fontsize=9.5,
        hatch=None, text_color="white", bold=False):
    kw = dict(boxstyle="round,pad=0.15", linewidth=1.4,
              edgecolor=edgecolor, facecolor=facecolor)
    if hatch:
        kw["hatch"] = hatch
    rect = FancyBboxPatch((x, y), w, h, **kw)
    ax.add_patch(rect)
    weight = "bold" if bold else "normal"
    ax.text(x + w / 2, y + h / 2, text,
            ha="center", va="center",
            fontsize=fontsize, color=text_color, fontweight=weight,
            multialignment="center")

def arrow(x1, y1, x2, y2, label="", color=COL_ARROW, lw=1.6,
          both=False):
    style = "<->" if both else "->"
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle=style, color=color,
                                lw=lw, connectionstyle="arc3,rad=0.0"))
    if label:
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        ax.text(mx, my + 0.18, label,
                ha="center", va="bottom",
                fontsize=8, color=color,
                bbox=dict(facecolor="white", edgecolor="none",
                          boxstyle="round,pad=0.1"))

# ══ column backgrounds ═══════════════════════════════════════════════════════
column_bg(0.25, 0.35, 3.3, 5.9, COL_FRONT,
          "Frontend  (React / Tailwind CSS)", COL_FRONT)
column_bg(4.45, 0.35, 4.1, 5.9, COL_BACK,
          "Backend  (FastAPI)", COL_BACK)
column_bg(9.35, 0.35, 3.3, 5.9, COL_EXT,
          "External Services", COL_EXT)

# ══ frontend boxes ════════════════════════════════════════════════════════════
FX, FW, FH = 0.55, 2.7, 0.90
box(FX, 4.95, FW, FH, "Generate Tab",
    COL_FRONT, COL_FRONT, text_color="white", bold=True)
box(FX, 3.70, FW, FH, "History Tab",
    COL_FRONT, COL_FRONT, text_color="white", bold=True)
box(FX, 2.45, FW, FH, "Leaderboard Tab",
    COL_FRONT, COL_FRONT, text_color="white", bold=True)
box(FX, 0.65, FW, 1.45,
    "SSE Progress\nStream (browser)",
    "#2E6FAA", COL_FRONT, text_color="white")

# ══ backend boxes ════════════════════════════════════════════════════════════
BX, BW, BH = 4.75, 3.5, 0.90
box(BX, 4.95, BW, BH, "REST API  /api/*",
    COL_BACK, COL_BACK, text_color="white", bold=True)
box(BX, 3.70, BW, BH, "Task Manager",
    COL_BACK, COL_BACK, text_color="white", bold=True)
box(BX, 2.45, BW, BH, "Eval Runner\n(subprocess workers)",
    COL_BACK, COL_BACK, text_color="white", bold=True)
box(BX, 0.65, BW, 1.45,
    "SSE Progress\nStream (server)",
    "#3A7A3A", COL_BACK, text_color="white")

# ══ external service boxes ════════════════════════════════════════════════════
EX, EW = 9.6, 2.8
# Gradino – hatched to signal black-box
box(EX, 3.80, EW, 2.0,
    "Gradino Library\n\n(black box:\ninput → QA instances)",
    COL_EXTBG, COL_EXT, fontsize=9, hatch="//",
    text_color="#4A3570")
# LLM APIs
box(EX, 0.65, EW, 2.8,
    "LLM  APIs\n\nOpenAI\nAnthropic Claude\nGoogle Gemini\nvLLM / HuggingFace",
    COL_EXTBG, COL_EXT, fontsize=8.5,
    text_color="#4A3570")

# ══ arrows ════════════════════════════════════════════════════════════════════
# Frontend ↔ Backend (REST)
arrow(3.25, 5.40, 4.75, 5.40, label="HTTP REST", both=True, color=COL_FRONT, lw=2.0)
# Frontend ↔ Backend (SSE)
arrow(3.25, 1.38, 4.75, 1.38, label="SSE", both=True, color="#888888", lw=1.6)
# Backend → Gradino
arrow(8.25, 4.40, 9.60, 4.40, label="subprocess", color=COL_EXT, lw=1.8)
# Gradino → Backend (return instances)
arrow(9.60, 3.90, 8.25, 3.90, label="instances", color=COL_EXT, lw=1.8)
# Backend → LLM APIs
arrow(8.25, 1.85, 9.60, 1.85, label="HTTPS / SDK", color=COL_EXT, lw=1.8)
# LLM → Backend (return)
arrow(9.60, 1.35, 8.25, 1.35, label="predictions", color=COL_EXT, lw=1.8)

# ── title ────────────────────────────────────────────────────────────────────
ax.set_title("TabgenQA – System Architecture",
             fontsize=13, fontweight="bold", pad=14, color="#222222")

plt.tight_layout()
plt.savefig("architecture.pdf", bbox_inches="tight", dpi=200)
plt.savefig("architecture.png", bbox_inches="tight", dpi=200)
print("Saved architecture.pdf and architecture.png")
