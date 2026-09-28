import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

fig, ax = plt.subplots(figsize=(9, 12))
ax.set_xlim(0, 10)
ax.set_ylim(0, 24)
ax.axis("off")

NAVY = "#1F3864"
ACCENT = "#2E74B5"
GREEN = "#2E7D32"
GREY = "#595959"

boxes = [
    ("IO-VNBD Dataset  +  Smartphone / External IMU", 22, ACCENT),
    ("Preprocessing & Timestamp Synchronization\n(elapsedRealtimeNanos, common rate)", 19.3, NAVY),
    ("Orientation & Gravity Calibration\n(phone \u2192 vehicle frame)", 16.6, NAVY),
    ("IMU Feature Extraction\n(sliding windows)", 13.9, NAVY),
    ("AI Model: 1D-CNN \u2192 GRU\n(speed, motion class, calibrated confidence)", 11.2, GREEN),
    ("Adaptive EKF Fusion\n(GNSS + IMU + AI speed + ZUPT + NHC)", 8.5, GREEN),
    ("Map-Matching\n(offline OpenStreetMap road constraint)", 5.8, NAVY),
    ("Continuous Position + Confidence Radius", 3.1, ACCENT),
]

for text, y, color in boxes:
    box = FancyBboxPatch((1, y - 1.1), 8, 2.0, boxstyle="round,pad=0.15,rounding_size=0.2",
                          linewidth=1.5, edgecolor=color, facecolor="white")
    ax.add_patch(box)
    ax.text(5, y - 0.1, text, ha="center", va="center", fontsize=10.5, color=color, weight="bold", wrap=True)

for i in range(len(boxes) - 1):
    y_start = boxes[i][1] - 1.1
    y_end = boxes[i + 1][1] + 0.9
    arrow = FancyArrowPatch((5, y_start), (5, y_end), arrowstyle="-|>", mutation_scale=18,
                             color=GREY, linewidth=1.5)
    ax.add_patch(arrow)

# Deployment fork at the bottom
ax.text(5, 1.4, "Android Application  |  Edge-Deployable Software Engine",
        ha="center", va="center", fontsize=10, color=GREY, style="italic")
arrow = FancyArrowPatch((5, 2.0), (5, 1.7), arrowstyle="-|>", mutation_scale=14, color=GREY)
ax.add_patch(arrow)

ax.set_title("Intelligent Dead Reckoning \u2014 System Architecture", fontsize=13, weight="bold", color=NAVY, pad=15)

plt.tight_layout()
plt.savefig("docs/architecture.png", dpi=160, bbox_inches="tight")
print("saved docs/architecture.png")
