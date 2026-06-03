#!/usr/bin/env python3
"""
TabgenQA — publication-quality system-overview figure for CIKM 2025.

Layout (full two-column width):
  ┌────────────────────────────────────────────────────────────┐
  │  Title                                                     │
  ├─────────────────┬─────────────────┬─────────────────────── │
  │  ① Generate     │  ② Review/Edit  │  ③ Evaluate & Compare  │
  │   bullets        │   bullets        │   bullets               │
  │  ─ ─ ─ ─ ─ ─ ─  │  ─ ─ ─ ─ ─ ─ ─  │  ─ ─ ─ ─ ─ ─ ─ ─ ─ ─  │
  │  [Gradino box]   │  [output box]    │  [Leaderboard box]     │
  ├─────────────────┴─────────────────┴────────────────────── │
  │  Usage Scenarios: Procurement  |  Diagnosis  |  Curation  │
  └────────────────────────────────────────────────────────────┘
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import matplotlib.patheffects as pe

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 8,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
    "figure.dpi": 300,
})

# ── palette ───────────────────────────────────────────────────────────────────
# step 1 – generate (cobalt blue)
G = dict(hdr="#1E40AF", body="#EFF6FF", edge="#93C5FD",
         txt="#1E3A8A", ib="#DBEAFE", ie="#60A5FA")
# step 2 – review/edit (violet)
R = dict(hdr="#5B21B6", body="#F5F3FF", edge="#C4B5FD",
         txt="#3B0764", ib="#EDE9FE", ie="#A78BFA")
# step 3 – evaluate (teal)
E = dict(hdr="#065F46", body="#ECFDF5", edge="#6EE7B7",
         txt="#022C22", ib="#D1FAE5", ie="#34D399")

ARROW   = "#4F46E5"
RULE    = "#CBD5E1"
TT      = "#0F172A"   # headline
TS      = "#475569"   # body
TL      = "#94A3B8"   # light / label
WHITE   = "#FFFFFF"

# scenario accent colours
SA, SB, SC_ = "#0284C7", "#BE185D", "#B45309"

# ── canvas ────────────────────────────────────────────────────────────────────
FW, FH = 8.4, 5.05
fig, ax = plt.subplots(figsize=(FW, FH))
ax.set_xlim(0, FW); ax.set_ylim(0, FH)
ax.axis("off")
fig.patch.set_facecolor(WHITE)
ax.set_facecolor(WHITE)

# ── drawing helpers ───────────────────────────────────────────────────────────
def rbox(x, y, w, h, fc, ec, lw=0.9, r=0.10, z=2):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                                boxstyle=f"round,pad={r}",
                                facecolor=fc, edgecolor=ec,
                                linewidth=lw, zorder=z))

def t(x, y, s, fs=7.5, c=TT, ha="left", va="top", w="normal",
      style="normal", z=5):
    ax.text(x, y, s, fontsize=fs, color=c, ha=ha, va=va,
            fontweight=w, fontstyle=style, zorder=z)

def harrow(x1, y, x2, label="", c=ARROW, lw=1.9, dy=0.10):
    ax.annotate("", xy=(x2, y), xytext=(x1, y),
                arrowprops=dict(arrowstyle="-|>", color=c,
                                lw=lw, mutation_scale=11))
    if label:
        ax.text((x1 + x2) / 2, y + dy, label,
                ha="center", va="bottom", fontsize=6.4,
                color=c, style="italic", zorder=6)

# ── layout ────────────────────────────────────────────────────────────────────
ML, MR = 0.32, 0.32
MB     = 0.22
MT     = 0.22

TITLE_H  = 0.52        # title strip height
SCEN_H   = 0.95        # usage-scenario strip
SEP_Y    = MB + SCEN_H + 0.10   # separator y

FLOW_BOT = SEP_Y + 0.22
FLOW_TOP = FH - MT - TITLE_H
FLOW_H   = FLOW_TOP - FLOW_BOT   # ≈ 2.77"

SGAP = 0.28            # gap between step panels
SW   = (FW - ML - MR - 2 * SGAP) / 3   # ≈ 2.39"
SH   = FLOW_H
HDR  = 0.43            # header height
IW   = SW - 0.28       # inner box width
FOOT = 0.56            # footer box height
FOOT_PAD = 0.14        # footer box bottom padding

s1x = ML
s2x = s1x + SW + SGAP
s3x = s2x + SW + SGAP
SY  = FLOW_BOT         # step panel bottom y

# footer box centre y (used for arrow y)
ARR_Y = SY + FOOT_PAD + FOOT / 2   # ≈ SY + 0.42

# ── title ─────────────────────────────────────────────────────────────────────
t(FW/2, FH - MT - 0.02,
  "TabgenQA — Benchmark Generation, Curation, and Evaluation",
  fs=11.8, c=TT, ha="center", va="top", w="bold")
t(FW/2, FH - MT - 0.30,
  "A web platform for non-relational multi-table numerical QA benchmarks",
  fs=8.3, c=TS, ha="center", va="top", style="italic")

# ── step panel constructor ────────────────────────────────────────────────────
def step(sx, cs, num, title, sub, bullets, ft_title, ft_sub):
    # body
    rbox(sx, SY, SW, SH, cs["body"], cs["edge"], lw=1.0, r=0.10, z=2)
    # header
    rbox(sx, SY + SH - HDR, SW, HDR, cs["hdr"], cs["hdr"], lw=0, r=0.08, z=3)
    # badge circle + number
    ax.add_patch(plt.Circle((sx + 0.28, SY + SH - HDR / 2),
                             0.152, color=WHITE, alpha=0.25, zorder=4))
    t(sx + 0.28, SY + SH - HDR / 2, num,
      fs=9.5, c=WHITE, ha="center", va="center", w="bold", z=5)
    t(sx + 0.50, SY + SH - HDR / 2, title,
      fs=9.0, c=WHITE, ha="left", va="center", w="bold", z=5)

    # subtitle
    cy = SY + SH - HDR - 0.25
    t(sx + 0.17, cy, sub, fs=6.9, c=cs["hdr"], w="semibold")

    # bullets  — tight line spacing, clipped per panel
    cy -= 0.22
    for b in bullets:
        ax.text(sx + 0.22, cy, "▸", fontsize=6.5,
                color=cs["hdr"], va="top", zorder=5)
        obj = ax.text(sx + 0.38, cy, b, fontsize=6.9,
                      color=TT, va="top", zorder=5)
        # clip so text cannot overflow into the inter-panel gap
        obj.set_clip_on(True)
        cy -= 0.230

    # footer inner box
    fy = SY + FOOT_PAD
    rbox(sx + 0.14, fy, IW, FOOT, cs["ib"], cs["ie"], lw=0.8, r=0.07, z=3)
    cx = sx + 0.14 + IW / 2
    t(cx, fy + FOOT - 0.13, ft_title,
      fs=7.1, c=cs["txt"], ha="center", va="top", w="bold", z=4)
    t(cx, fy + FOOT - 0.32, ft_sub,
      fs=6.3, c=cs["hdr"], ha="center", va="top", style="italic", z=4)

step(s1x, G, "①", "Generate",
     "Configure benchmark parameters:",
     ["Domain (envir. · fin. · health · prod.)",
      "Question type (sum · avg · superlative)",
      "Num. tables (2–20) · samples · columns"],
     "Gradino  [black box]",
     "multi-table QA generator")

step(s2x, R, "②", "Review & Edit",
     "Inspect and refine instances:",
     ["Edit question text and gold answer",
      "Table editor (add/remove rows & cols)",
      "History · filters · CSV / JSON export"],
     "Curated benchmark",
     "user-verified instances")

step(s3x, E, "③", "Evaluate & Compare",
     "Run automated LLM evaluation:",
     ["OpenAI · Anthropic Claude · Gemini",
      "Open-weight models via local vLLM",
      "Accuracy + F1 · chain-of-thought"],
     "Leaderboard  ·  Accuracy  ·  F1",
     "ranked models · per-instance view")

# ── arrows (drawn at footer-box mid-height — below all bullet text) ───────────
harrow(s1x + SW + 0.04, ARR_Y, s2x - 0.04, label="QA instances", dy=0.09)
harrow(s2x + SW + 0.04, ARR_Y, s3x - 0.04, label="curated set",  dy=0.09)

# ── separator ─────────────────────────────────────────────────────────────────
ax.plot([ML, FW - MR], [SEP_Y] * 2, color=RULE, lw=0.9, zorder=3)
t(FW / 2, SEP_Y + 0.06,
  "Usage Scenarios", fs=6.8, c=TL, ha="center", va="bottom",
  w="bold", style="italic")

# ── scenario cards ────────────────────────────────────────────────────────────
CGAP = 0.26
CW   = (FW - ML - MR - 2 * CGAP) / 3
c1x  = ML
c2x  = c1x + CW + CGAP
c3x  = c2x + CW + CGAP
CH   = SCEN_H - 0.08
AW   = 0.046   # accent bar width

CARDS = [
    (c1x, SA, "Procurement",
     "A user generates a Finance/Products\n"
     "domain benchmark to identify which\n"
     "LLM best handles procurement queries."),
    (c2x, SB, "Diagnosis",
     "A clinician evaluates LLMs on\n"
     "Healthcare tables to assess readiness\n"
     "for clinical decision support."),
    (c3x, SC_, "Curation",
     "A researcher reviews automatically\n"
     "generated instances and edits them\n"
     "to build a validated dataset."),
]

for sx, col, title, body in CARDS:
    rbox(sx, MB, CW, CH, "#F8FAFF", col + "40", lw=1.0, r=0.08, z=2)
    rbox(sx, MB, AW, CH, col, col,  lw=0, r=0.05, z=3)
    t(sx + 0.11, MB + CH - 0.16, title,
      fs=8.0, c=col, ha="left", va="top", w="bold")
    t(sx + 0.11, MB + CH - 0.36, body,
      fs=6.8, c=TS,  ha="left", va="top")

# ── save ──────────────────────────────────────────────────────────────────────
for fmt in ("pdf", "png"):
    plt.savefig(f"architecture.{fmt}", bbox_inches="tight", dpi=300)
print("Saved architecture.pdf / architecture.png")
