#!/usr/bin/env python3
"""
Generate a 2×2 UI-mockup figure for the TabgenQA paper.

Panels:
  (a) Generate tab  – parameter form + SSE progress bar
  (b) History tab   – filter chips + task cards
  (c) Evaluate modal – model config + live progress
  (d) Leaderboard   – ranked table + slide-in detail panel
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import matplotlib.gridspec as gridspec

# ── palette ──────────────────────────────────────────────────────────────────
C_BG      = "#F8F9FA"
C_PANEL   = "#FFFFFF"
C_BORDER  = "#DEE2E6"
C_BLUE    = "#3B82F6"
C_BLUE_LT = "#DBEAFE"
C_GREEN   = "#22C55E"
C_GREEN_LT= "#DCFCE7"
C_RED     = "#EF4444"
C_RED_LT  = "#FEE2E2"
C_GREY    = "#6B7280"
C_DARK    = "#1F2937"
C_PURPLE  = "#7C3AED"
C_PURP_LT = "#EDE9FE"
C_AMBER   = "#F59E0B"
C_AMBER_LT= "#FEF3C7"
C_HEADER  = "#1E40AF"

# ── helpers ──────────────────────────────────────────────────────────────────
def panel_bg(ax, color=C_PANEL):
    ax.set_facecolor(color)
    for sp in ax.spines.values():
        sp.set_edgecolor(C_BORDER)
        sp.set_linewidth(1.2)

def rbox(ax, x, y, w, h, fc, ec, lw=0.8, radius=0.03, hatch=None):
    kw = dict(boxstyle=f"round,pad={radius}",
              facecolor=fc, edgecolor=ec, linewidth=lw)
    if hatch:
        kw["hatch"] = hatch
    r = FancyBboxPatch((x, y), w, h, transform=ax.transAxes, **kw,
                       clip_on=True)
    ax.add_patch(r)

def txt(ax, x, y, s, fs=7, color=C_DARK, weight="normal",
        ha="left", va="center", transform=None):
    t = transform or ax.transAxes
    ax.text(x, y, s, transform=t,
            fontsize=fs, color=color, fontweight=weight,
            ha=ha, va=va, clip_on=True)

def chip(ax, x, y, label, w=0.18, h=0.07,
         fc=C_BLUE_LT, ec=C_BLUE, tc=C_HEADER):
    rbox(ax, x, y, w, h, fc, ec, lw=0.7)
    txt(ax, x + w / 2, y + h / 2, label, fs=6.5, color=tc,
        ha="center", weight="bold")

def progress_bar(ax, x, y, w, h, frac, fc=C_BLUE, bg=C_BORDER):
    rbox(ax, x, y, w, h, bg, C_BORDER, lw=0.5, radius=0.02)
    if frac > 0:
        rbox(ax, x, y, w * frac, h, fc, fc, lw=0, radius=0.02)


# ════════════════════════════════════════════════════════════════════════════
fig = plt.figure(figsize=(14, 9), facecolor=C_BG)
gs = gridspec.GridSpec(2, 2, figure=fig,
                       hspace=0.32, wspace=0.22,
                       left=0.04, right=0.97,
                       top=0.93, bottom=0.05)

# ──────────────────────────────────────────────────────────────────────────
# Panel (a) – Generate Tab
# ──────────────────────────────────────────────────────────────────────────
ax_a = fig.add_subplot(gs[0, 0])
panel_bg(ax_a)
ax_a.set_xlim(0, 1); ax_a.set_ylim(0, 1); ax_a.axis("off")

# tab bar
for i, (tab, sel) in enumerate([("Generate", True), ("History", False), ("Leaderboard", False)]):
    fc = C_BLUE if sel else C_BG
    tc = "white" if sel else C_GREY
    rbox(ax_a, 0.04 + i * 0.295, 0.90, 0.28, 0.08, fc, C_BORDER if not sel else C_BLUE, lw=0.8)
    txt(ax_a, 0.04 + i * 0.295 + 0.14, 0.94, tab, fs=7, color=tc, ha="center", weight="bold")

# form title
txt(ax_a, 0.05, 0.83, "Generate Benchmark", fs=9, color=C_DARK, weight="bold")

# form rows
rows = [
    ("Domain",         "environmental",  0.72),
    ("Question Type",  "sum",            0.62),
    ("Num Tables",     "5",              0.52),
    ("Num Samples",    "100",            0.42),
    ("Col Cardinality","20",             0.32),
]
for label, val, yy in rows:
    txt(ax_a, 0.05, yy + 0.03, label + ":", fs=7, color=C_GREY)
    rbox(ax_a, 0.42, yy - 0.01, 0.50, 0.07, "white", C_BORDER)
    txt(ax_a, 0.44, yy + 0.025, val, fs=7, color=C_DARK)

# generate button
rbox(ax_a, 0.30, 0.185, 0.40, 0.075, C_BLUE, C_BLUE)
txt(ax_a, 0.50, 0.224, "Generate", fs=8, color="white", ha="center", weight="bold")

# progress bar (55 % done)
txt(ax_a, 0.05, 0.13, "Progress  55 / 100  instances …", fs=6.8, color=C_GREY)
progress_bar(ax_a, 0.05, 0.075, 0.90, 0.045, 0.55)
txt(ax_a, 0.50, 0.098, "55%", fs=6.5, color="white", ha="center", weight="bold")

ax_a.set_title("(a)  Benchmark generation", fontsize=9, color=C_DARK, pad=5)

# ──────────────────────────────────────────────────────────────────────────
# Panel (b) – History Tab
# ──────────────────────────────────────────────────────────────────────────
ax_b = fig.add_subplot(gs[0, 1])
panel_bg(ax_b)
ax_b.set_xlim(0, 1); ax_b.set_ylim(0, 1); ax_b.axis("off")

# tab bar
for i, (tab, sel) in enumerate([("Generate", False), ("History", True), ("Leaderboard", False)]):
    fc = C_BLUE if sel else C_BG
    tc = "white" if sel else C_GREY
    rbox(ax_b, 0.04 + i * 0.295, 0.90, 0.28, 0.08, fc, C_BORDER if not sel else C_BLUE)
    txt(ax_b, 0.04 + i * 0.295 + 0.14, 0.94, tab, fs=7, color=tc, ha="center", weight="bold")

# filter chips
txt(ax_b, 0.04, 0.85, "Filter:", fs=7, color=C_GREY)
chip(ax_b, 0.20, 0.815, "environmental", w=0.24)
chip(ax_b, 0.46, 0.815, "sum", w=0.12)
chip(ax_b, 0.60, 0.815, "5 tables", w=0.16,
     fc=C_PURP_LT, ec=C_PURPLE, tc=C_PURPLE)

# task cards
tasks = [
    ("env · sum · 5 tables · 100 samples", "done",    "#22C55E", "2026-06-01 14:32", "100"),
    ("finance · avg · 3 tables · 50 samples","done",  "#22C55E", "2026-06-01 09:14", "50"),
    ("health · super · 10 tables · 80 samp","running","#F59E0B", "2026-06-03 08:01", "37/80"),
]
yy = 0.77
for cfg, status, sc, ts, cnt in tasks:
    rbox(ax_b, 0.04, yy - 0.09, 0.92, 0.14, "white", C_BORDER)
    txt(ax_b, 0.07, yy + 0.005, cfg, fs=6.8, color=C_DARK, weight="bold")
    txt(ax_b, 0.07, yy - 0.038, ts + f"   ·   {cnt} instances", fs=6.2, color=C_GREY)
    # status badge
    rbox(ax_b, 0.72, yy - 0.025, 0.12, 0.05, sc + "22", sc, radius=0.025)
    txt(ax_b, 0.78, yy, status, fs=6.2, color=sc, ha="center", weight="bold")
    # action buttons
    rbox(ax_b, 0.06, yy - 0.082, 0.15, 0.038, C_BLUE_LT, C_BLUE, radius=0.015)
    txt(ax_b, 0.135, yy - 0.063, "Download", fs=6, color=C_HEADER, ha="center")
    rbox(ax_b, 0.24, yy - 0.082, 0.13, 0.038, C_GREEN_LT, C_GREEN, radius=0.015)
    txt(ax_b, 0.305, yy - 0.063, "Evaluate", fs=6, color="#166534", ha="center")
    yy -= 0.22

ax_b.set_title("(b)  Run history with filtering", fontsize=9, color=C_DARK, pad=5)

# ──────────────────────────────────────────────────────────────────────────
# Panel (c) – Evaluate Modal
# ──────────────────────────────────────────────────────────────────────────
ax_c = fig.add_subplot(gs[1, 0])
panel_bg(ax_c)
ax_c.set_xlim(0, 1); ax_c.set_ylim(0, 1); ax_c.axis("off")

# modal card
rbox(ax_c, 0.05, 0.05, 0.90, 0.90, "white", C_BORDER, lw=1.2, radius=0.04)

txt(ax_c, 0.50, 0.90, "Evaluate  –  env · sum · 5 tables", fs=9,
    color=C_DARK, ha="center", weight="bold")

fields = [
    ("Model Type",   "OpenAI",           0.76),
    ("Model Name",   "gpt-4o-mini",      0.65),
    ("API Key",      "sk-••••••••••••",  0.54),
    ("Base URL",     "(optional)",       0.43),
]
for lbl, val, yy in fields:
    txt(ax_c, 0.10, yy + 0.04, lbl, fs=7.5, color=C_GREY)
    rbox(ax_c, 0.10, yy - 0.005, 0.78, 0.075, "white", C_BORDER)
    txt(ax_c, 0.13, yy + 0.033, val, fs=7.5, color=C_DARK)

# model type radio chips
for i, (mtype, sel) in enumerate([("OpenAI","yes"),("Claude",""),
                                   ("Gemini",""),("HuggingFace","")]):
    fc = C_BLUE if sel else C_BG
    tc = "white" if sel else C_GREY
    rbox(ax_c, 0.10 + i * 0.205, 0.78, 0.185, 0.055, fc,
         C_BLUE if sel else C_BORDER)
    txt(ax_c, 0.10 + i * 0.205 + 0.0925, 0.808, mtype, fs=6.5,
        color=tc, ha="center", weight="bold" if sel else "normal")

# live progress bar (38 %)
txt(ax_c, 0.10, 0.27, "Inference  38 / 100  …", fs=7, color=C_GREY)
progress_bar(ax_c, 0.10, 0.215, 0.78, 0.045, 0.38)
txt(ax_c, 0.49, 0.238, "38%", fs=6.5, color="white", ha="center", weight="bold")

# start / cancel buttons
rbox(ax_c, 0.28, 0.11, 0.24, 0.07, C_BLUE, C_BLUE)
txt(ax_c, 0.40, 0.145, "Start", fs=8, color="white", ha="center", weight="bold")
rbox(ax_c, 0.56, 0.11, 0.24, 0.07, C_BG, C_BORDER)
txt(ax_c, 0.68, 0.145, "Cancel", fs=8, color=C_GREY, ha="center")

ax_c.set_title("(c)  Model evaluation configuration", fontsize=9, color=C_DARK, pad=5)

# ──────────────────────────────────────────────────────────────────────────
# Panel (d) – Leaderboard + detail panel
# ──────────────────────────────────────────────────────────────────────────
ax_d = fig.add_subplot(gs[1, 1])
panel_bg(ax_d)
ax_d.set_xlim(0, 1); ax_d.set_ylim(0, 1); ax_d.axis("off")

# tab bar
for i, (tab, sel) in enumerate([("Generate", False), ("History", False), ("Leaderboard", True)]):
    fc = C_BLUE if sel else C_BG
    tc = "white" if sel else C_GREY
    rbox(ax_d, 0.02 + i * 0.295, 0.90, 0.28, 0.08, fc, C_BORDER if not sel else C_BLUE)
    txt(ax_d, 0.02 + i * 0.295 + 0.14, 0.94, tab, fs=7, color=tc, ha="center", weight="bold")

# leaderboard table (left 54 %)
rbox(ax_d, 0.02, 0.05, 0.53, 0.82, "white", C_BORDER, lw=0.8, radius=0.02)
# header
rbox(ax_d, 0.02, 0.82, 0.53, 0.05, C_HEADER, C_HEADER, radius=0.01)
for hdr, xh in [("Rank", 0.055), ("Model", 0.13), ("Acc", 0.38), ("F1", 0.46)]:
    txt(ax_d, xh, 0.845, hdr, fs=6.5, color="white", weight="bold")

leaderboard = [
    ("1", "gpt-4o-mini",    "OpenAI",  "72.4%", "0.741", True),
    ("2", "claude-3-haiku", "Claude",  "68.1%", "0.701", False),
    ("3", "gemini-flash",   "Gemini",  "65.9%", "0.679", False),
    ("4", "Qwen2.5-7B",     "vLLM",   "58.2%", "0.614", False),
]
badge_colors = {"OpenAI": (C_BLUE_LT, C_BLUE, C_HEADER),
                "Claude": (C_AMBER_LT, C_AMBER, "#92400E"),
                "Gemini": (C_GREEN_LT, C_GREEN, "#166534"),
                "vLLM":   (C_PURP_LT,  C_PURPLE, C_PURPLE)}
yy = 0.78
for rank, model, mtype, acc, f1, selected in leaderboard:
    row_fc = C_BLUE_LT if selected else "white"
    rbox(ax_d, 0.02, yy - 0.065, 0.53, 0.065, row_fc, C_BORDER, lw=0.5, radius=0.01)
    txt(ax_d, 0.055, yy - 0.032, rank, fs=7, color=C_DARK, ha="center")
    txt(ax_d, 0.11, yy - 0.032, model, fs=6.5, color=C_DARK, weight="bold" if selected else "normal")
    # type badge
    bfc, bec, btc = badge_colors[mtype]
    rbox(ax_d, 0.255, yy - 0.055, 0.09, 0.042, bfc, bec, lw=0.6, radius=0.02)
    txt(ax_d, 0.30, yy - 0.034, mtype, fs=5.5, color=btc, ha="center")
    txt(ax_d, 0.385, yy - 0.032, acc, fs=7, color=C_DARK, ha="center")
    txt(ax_d, 0.465, yy - 0.032, f1, fs=7, color=C_DARK, ha="center")
    # tiny bar
    bar_w = 0.07 * float(acc.replace("%", "")) / 100
    progress_bar(ax_d, 0.355, yy - 0.055, 0.07, 0.022, float(acc.replace("%", "")) / 100,
                 fc=C_GREEN if float(acc.replace("%", "")) > 65 else C_AMBER)
    yy -= 0.10

# detail panel (right 43 %)
rbox(ax_d, 0.565, 0.05, 0.425, 0.82, "white", C_BLUE, lw=1.2, radius=0.02)
txt(ax_d, 0.778, 0.84, "gpt-4o-mini  –  instance #7", fs=7.5,
    color=C_HEADER, ha="center", weight="bold")

# instance detail
txt(ax_d, 0.575, 0.795, "Question:", fs=6.5, color=C_GREY, weight="bold")
rbox(ax_d, 0.575, 0.715, 0.395, 0.075, C_BG, C_BORDER, radius=0.01)
txt(ax_d, 0.581, 0.758,
    "What is the total amount\nspent on Q1 orders?",
    fs=6.2, color=C_DARK)

txt(ax_d, 0.575, 0.695, "Tables:", fs=6.5, color=C_GREY, weight="bold")
rbox(ax_d, 0.575, 0.615, 0.395, 0.072, "#FFFBEB", C_AMBER, lw=0.7, radius=0.01,
     hatch="...")
txt(ax_d, 0.773, 0.651, "▶  Table 1, Table 2  (click to expand)",
    fs=6, color=C_AMBER, ha="center")

txt(ax_d, 0.575, 0.593, "Gold answer:", fs=6.5, color=C_GREY, weight="bold")
rbox(ax_d, 0.575, 0.545, 0.18, 0.042, C_GREEN_LT, C_GREEN, radius=0.01)
txt(ax_d, 0.665, 0.566, "12 847.32", fs=7, color="#166534", ha="center", weight="bold")

txt(ax_d, 0.775, 0.593, "Model answer:", fs=6.5, color=C_GREY, weight="bold")
rbox(ax_d, 0.775, 0.545, 0.18, 0.042, C_GREEN_LT, C_GREEN, radius=0.01)
txt(ax_d, 0.865, 0.566, "12 847.32", fs=7, color="#166534", ha="center", weight="bold")

txt(ax_d, 0.575, 0.523, "Reasoning:", fs=6.5, color=C_GREY, weight="bold")
rbox(ax_d, 0.575, 0.08, 0.395, 0.438, "#FAFAFA", C_BORDER, radius=0.01)
reasoning = (
    "Step 1: Filter orders where\n"
    "  quarter = 'Q1'.\n"
    "Step 2: Join with amounts table\n"
    "  on order_id.\n"
    "Step 3: SUM(amount) =\n"
    "  4 210.00 + 5 381.12 +\n"
    "  3 256.20 = 12 847.32\n\n"
    "Final answer: 12847.32"
)
txt(ax_d, 0.580, 0.495, reasoning, fs=5.8, color=C_DARK, va="top")

# filter tabs on detail panel
for i, (flabel, fsel) in enumerate([("All", False), ("Correct", True), ("Wrong", False)]):
    fc = C_GREEN if fsel else C_BG
    tc = "white" if fsel else C_GREY
    rbox(ax_d, 0.575 + i * 0.138, 0.855, 0.125, 0.042,
         fc, C_GREEN if fsel else C_BORDER, lw=0.6)
    txt(ax_d, 0.575 + i * 0.138 + 0.0625, 0.876, flabel,
        fs=6.2, color=tc, ha="center", weight="bold" if fsel else "normal")

ax_d.set_title("(d)  Leaderboard with prediction detail", fontsize=9, color=C_DARK, pad=5)

# ── main title ───────────────────────────────────────────────────────────────
fig.suptitle("TabgenQA – User Interface Overview",
             fontsize=13, fontweight="bold", color=C_DARK, y=0.985)

plt.savefig("ui_overview.pdf", bbox_inches="tight", dpi=200)
plt.savefig("ui_overview.png", bbox_inches="tight", dpi=200)
print("Saved ui_overview.pdf and ui_overview.png")
