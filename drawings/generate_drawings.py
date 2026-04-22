"""
X3-1500-72 外转子轮毂电机优化方案（V2.0）工程图纸生成脚本
生成6张高分辨率工程图纸（300 DPI，PNG格式）
"""

import os
import sys
import warnings
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyArrowPatch, Arc, Rectangle, FancyBboxPatch
from matplotlib.lines import Line2D
from matplotlib.table import Table
import matplotlib.patheffects as pe
from matplotlib.path import Path
import matplotlib.colors as mcolors

warnings.filterwarnings('ignore')

# ─────────────────────────── 输出目录 ────────────────────────────
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ─────────────────────────── 字体设置 ────────────────────────────
USE_CHINESE = False
FONT_NAME = 'DejaVu Sans'

_CN_CANDIDATES = [
    'SimHei', 'Microsoft YaHei', 'PingFang SC',
    'Noto Sans CJK SC', 'WenQuanYi Zen Hei', 'Arial Unicode MS'
]

def _try_chinese_fonts():
    """尝试加载中文字体，返回可用字体名或None"""
    import matplotlib.font_manager as fm
    available = {f.name for f in fm.fontManager.ttflist}
    for name in _CN_CANDIDATES:
        if name in available:
            return name
    return None

_cn = _try_chinese_fonts()
if _cn:
    USE_CHINESE = True
    FONT_NAME = _cn
    matplotlib.rcParams['font.family'] = [_cn, 'DejaVu Sans']
else:
    matplotlib.rcParams['font.family'] = ['DejaVu Sans']

matplotlib.rcParams['axes.unicode_minus'] = False

def T(zh: str, en: str) -> str:
    """根据字体可用性返回中文或英文文本"""
    return zh if USE_CHINESE else en


# ─────────────────────────── 全局样式 ────────────────────────────
FIG_SIZE = (16.54, 11.69)   # A3横向（英寸）
DPI = 300
VERSION = 'V2.0'
DATE = '2026-04'
MODEL = 'X3-1500-72'

COLORS = dict(
    rim='#C0C0C0',          # 轮辋 6061-T6
    rotor_yoke='#606060',   # 转子轭
    magnet='#DC143C',       # 永磁体
    stator='#FF8C00',       # 定子铁芯
    winding='#FFD700',      # 绕组
    shaft='#808080',        # 固定轴
    bearing='#1C3A6E',      # 轴承
    spring='#228B22',       # 波形弹簧
    rubber='#FF4500',       # 橡胶缓冲块
    airgap='white',
    cam_line='#1565C0',
    cam_fill='#BBDEFB',
    cam_boundary='#9E9E9E',
    needle='#C62828',
)


# ─────────────────────────── 通用辅助函数 ─────────────────────────

def add_title_block(fig, subtitle: str, fig_num: int):
    """在图纸右下角添加标题栏（工程图格式）"""
    ax_tb = fig.add_axes([0.60, 0.0, 0.40, 0.055])
    ax_tb.set_xlim(0, 10)
    ax_tb.set_ylim(0, 3)
    ax_tb.axis('off')
    # 边框
    for x in [0, 10]:
        ax_tb.axvline(x, color='k', lw=1.0)
    for y in [0, 1, 2, 3]:
        ax_tb.axhline(y, color='k', lw=0.8)
    ax_tb.axvline(4, color='k', lw=0.6, ymin=0, ymax=1)
    ax_tb.axvline(7, color='k', lw=0.6, ymin=0, ymax=1)
    # 内容
    ax_tb.text(2, 2.5, MODEL, ha='center', va='center', fontsize=8, fontweight='bold',
               fontfamily=FONT_NAME)
    fig_label = T(f'图{fig_num} {subtitle}', f'Fig.{fig_num} {subtitle}')
    ax_tb.text(5.5, 2.5, fig_label, ha='center', va='center', fontsize=7,
               fontfamily=FONT_NAME)
    ax_tb.text(8.5, 2.5, f'{VERSION} | {DATE}', ha='center', va='center', fontsize=7)
    ax_tb.text(2, 1.5, T('比例 1:2', 'Scale 1:2'), ha='center', va='center', fontsize=6)
    ax_tb.text(5.5, 1.5, T('材料：见明细表', 'Material: See BOM'), ha='center', va='center',
               fontsize=6, fontfamily=FONT_NAME)
    ax_tb.text(8.5, 1.5, T('单位 mm', 'Unit: mm'), ha='center', va='center', fontsize=6)
    ax_tb.text(2, 0.5, T('绘图', 'Drawn'), ha='center', va='center', fontsize=6)
    ax_tb.text(5.5, 0.5, T('审核', 'Checked'), ha='center', va='center', fontsize=6)
    ax_tb.text(8.5, 0.5, T('批准', 'Approved'), ha='center', va='center', fontsize=6)


def dim_arrow(ax, x1, y1, x2, y2, label, offset=3, color='k', fontsize=6.5,
              text_pos='mid', orientation='h'):
    """绘制带双箭头的尺寸标注线"""
    arrowprops = dict(arrowstyle='<->', color=color, lw=0.8,
                      mutation_scale=8)
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=arrowprops)
    if orientation == 'h':
        mx = (x1 + x2) / 2
        my = y1 + offset
    else:
        mx = x1 + offset
        my = (y1 + y2) / 2
    ax.text(mx, my, label, ha='center', va='center', fontsize=fontsize,
            color=color, fontfamily=FONT_NAME,
            bbox=dict(boxstyle='round,pad=0.1', fc='white', ec='none', alpha=0.8))


# ══════════════════════════════════════════════════════════════════
# 图1：整机轴向全剖面图
# ══════════════════════════════════════════════════════════════════

def draw_figure_01():
    fig = plt.figure(figsize=FIG_SIZE, dpi=DPI)
    fig.patch.set_facecolor('white')

    # 主绘图区（保留空间给标题栏和图例）
    ax = fig.add_axes([0.06, 0.12, 0.88, 0.80])
    ax.set_xlim(-20, 135)
    ax.set_ylim(-5, 105)
    ax.set_aspect('equal')
    ax.axis('off')

    # ── 半剖坐标系（X=轴向，Y=径向，Y=0为轴线） ──────────────────
    # 各径向尺寸（半径，mm）
    R_RIM_OUT = 98.2       # 轮辋外半径 ≈ 196.4/2
    R_RIM_IN = 95.2        # 轮辋内壁
    R_ROTOR_OUT = 95.2     # 转子轭外半径
    R_ROTOR_IN = 86.2      # 转子轭内半径（厚9mm）
    R_MAG_OUT = 86.2       # 磁钢外半径
    R_MAG_IN = 81.2        # 磁钢内半径（厚5mm）
    R_AIRGAP = 81.2        # 气隙外缘
    R_STATOR_OUT = 82.5    # 定子铁芯外半径 = 165/2
    R_STATOR_IN = 51.5     # 定子铁芯内半径 = 103/2
    R_GUIDE = 15.0         # 导向段半径 φ30mm
    R_SHAFT = 11.0         # 螺旋槽段半径 φ22mm

    # 轴向尺寸
    AX_TOTAL = 115          # 总轴向长
    AX_LEFT = 0             # 左端
    AX_STATOR_L = 36.5     # 定子左端（居中于轴向）
    AX_STATOR_R = AX_STATOR_L + 42   # 定子右端
    AX_MAG_L = 28.5        # 磁钢左端（Lm=58mm，居中）
    AX_MAG_R = AX_MAG_L + 58

    def rect(ax, x, y, w, h, color, alpha=1.0, ec='#333', lw=0.5, hatch=None):
        r = patches.Rectangle((x, y), w, h, facecolor=color, edgecolor=ec,
                               linewidth=lw, alpha=alpha, hatch=hatch)
        ax.add_patch(r)

    # 1. 轮辋（最外层）
    rect(ax, AX_LEFT, R_RIM_IN, AX_TOTAL, R_RIM_OUT - R_RIM_IN,
         COLORS['rim'], lw=0.8)
    ax.text(-2, (R_RIM_IN + R_RIM_OUT) / 2, T('轮辋\n6061-T6', 'Rim\n6061-T6'),
            ha='right', va='center', fontsize=5.5, fontfamily=FONT_NAME, color='#333')

    # 2. 转子轭
    rect(ax, AX_LEFT, R_ROTOR_IN, AX_TOTAL, R_ROTOR_OUT - R_ROTOR_IN,
         COLORS['rotor_yoke'], lw=0.8)
    ax.text(-2, (R_ROTOR_IN + R_ROTOR_OUT) / 2,
            T('转子轭', 'Rotor Yoke'), ha='right', va='center', fontsize=5.5,
            fontfamily=FONT_NAME, color='white')

    # 3. 永磁体阵列（磁钢，居中）
    rect(ax, AX_MAG_L, R_MAG_IN, 58, R_MAG_OUT - R_MAG_IN,
         COLORS['magnet'], lw=0.8)
    # 磁钢斜线表示极性
    for i in range(8):
        xp = AX_MAG_L + i * 7.25
        ax.plot([xp, xp + 7.25], [R_MAG_IN, R_MAG_OUT], color='white', lw=0.4, alpha=0.5)

    # 4. 气隙（留白，0.7mm 放大表示）
    # 在图上用2mm表示（已放大表示）
    airgap_vis = 2.0
    rect(ax, AX_STATOR_L, R_STATOR_OUT, AX_STATOR_R - AX_STATOR_L, airgap_vis,
         'white', ec='#AAA', lw=0.3)

    # 5. 定子铁芯
    rect(ax, AX_STATOR_L, R_STATOR_IN, 42, R_STATOR_OUT - R_STATOR_IN,
         COLORS['stator'], lw=0.8)

    # 绕组（在定子槽内，金黄色）
    slot_h = (R_STATOR_OUT - R_STATOR_IN) * 0.55
    slot_w = 42 / 24 * 0.55
    for i in range(24):
        sx = AX_STATOR_L + i * (42 / 24) + (42 / 24) * 0.22
        rect(ax, sx, R_STATOR_IN + (R_STATOR_OUT - R_STATOR_IN) * 0.1,
             slot_w, slot_h, COLORS['winding'], ec='#CC9900', lw=0.3)

    # 6. 固定轴
    rect(ax, AX_LEFT - 5, 0, AX_TOTAL + 10, R_SHAFT,
         COLORS['shaft'], lw=0.8)
    # 螺旋槽段标注区域
    rect(ax, AX_STATOR_L + 5, 0, 30, R_SHAFT,
         '#A0A0A0', ec='#555', lw=0.4, hatch='///')
    ax.text(AX_STATOR_L + 20, R_SHAFT + 2,
            T('螺旋槽', 'Cam Groove'), ha='center', va='bottom', fontsize=5,
            fontfamily=FONT_NAME)

    # 导向段（φ30mm 段）
    rect(ax, AX_LEFT, 0, AX_STATOR_L, R_GUIDE,
         '#909090', ec='#555', lw=0.4)
    ax.text(AX_STATOR_L / 2, R_GUIDE + 1,
            T('导向段φ30', 'Guide φ30'), ha='center', va='bottom', fontsize=5)

    # 7. 轴承（驱动侧左，非驱动侧右）
    def draw_bearing(ax, x_center, r_in, r_out, label):
        bw = 12
        rect(ax, x_center - bw / 2, r_in, bw, r_out - r_in,
             COLORS['bearing'], alpha=0.85, ec='#0A1F5A', lw=0.6)
        # 内外圆环表示
        for r in [r_in + 1.5, r_out - 1.5]:
            arc = Arc((x_center, 0), 2 * r, 2 * r,
                      theta1=0, theta2=90, color='#8FA8D4', lw=0.8)
            ax.add_patch(arc)
        ax.text(x_center, r_out + 2, label, ha='center', va='bottom', fontsize=5,
                fontfamily=FONT_NAME)

    draw_bearing(ax, 8, R_GUIDE, R_ROTOR_IN - 1,
                 T('6308\n驱动侧', '6308\nDrive'))
    draw_bearing(ax, 107, R_GUIDE, R_ROTOR_IN - 1,
                 T('6307\n非驱动侧', '6307\nNon-Drive'))

    # 8. 波形弹簧（绿色锯齿线）
    spring_x = np.linspace(AX_STATOR_R + 2, AX_STATOR_R + 14, 80)
    spring_y = R_GUIDE + 5 + 2 * np.sin(spring_x * np.pi / 2)
    ax.plot(spring_x, spring_y, color=COLORS['spring'], lw=1.2, zorder=5)
    ax.text(AX_STATOR_R + 8, R_GUIDE + 5 + 5,
            T('波形弹簧\n6层叠合', 'Wave Spring\n6-layer'), ha='center', va='bottom',
            fontsize=5, color=COLORS['spring'], fontfamily=FONT_NAME)

    # 9. 橡胶缓冲块（两端）
    for bx in [AX_STATOR_L - 3, AX_STATOR_R + 0.5]:
        rect(ax, bx, R_STATOR_IN, 2.5, 8, COLORS['rubber'], ec='#8B0000', lw=0.5)
    ax.text(AX_STATOR_L - 5, R_STATOR_IN + 4,
            T('橡胶\n缓冲块', 'Rubber\nBuffer'), ha='center', va='center',
            fontsize=5, color=COLORS['rubber'], fontfamily=FONT_NAME)

    # ── 轴线 ──────────────────────────────────────────────────────
    ax.axhline(0, color='k', lw=0.6, linestyle='-.')
    ax.text(130, 0.5, T('轴线', 'C/L'), fontsize=5, color='k')

    # ── 尺寸标注 ─────────────────────────────────────────────────
    # 总轴向长115mm
    dim_arrow(ax, AX_LEFT, 101, AX_TOTAL, 101,
              T('总长 115mm', 'Total 115mm'), offset=1.5, fontsize=6)

    # 定子轴向42mm
    dim_arrow(ax, AX_STATOR_L, 95, AX_STATOR_R, 95,
              T('Ls=42mm', 'Ls=42mm'), offset=1.5, fontsize=6,
              color=COLORS['stator'])

    # 磁钢轴向58mm
    dim_arrow(ax, AX_MAG_L, 90, AX_MAG_R, 90,
              T('Lm=58mm', 'Lm=58mm'), offset=1.5, fontsize=6,
              color=COLORS['magnet'])

    # 径向尺寸标注（右侧引线）
    r_labels = [
        (R_RIM_OUT, 'φ196.4'),
        (R_STATOR_OUT, 'φ165'),
        (R_STATOR_IN, 'φ103'),
        (R_GUIDE, 'φ30'),
        (R_SHAFT, 'φ22'),
    ]
    for r, lbl in r_labels:
        ax.annotate('', xy=(120, r), xytext=(118, r),
                    arrowprops=dict(arrowstyle='->', color='k', lw=0.6, mutation_scale=6))
        ax.text(120.5, r, lbl, va='center', fontsize=5.5)

    # 气隙引线标注
    ax.annotate(T('气隙 g=0.7mm\n（放大示意）', 'Air gap g=0.7mm\n(enlarged)'),
                xy=(AX_STATOR_L + 10, R_STATOR_OUT + 1),
                xytext=(AX_STATOR_L - 10, R_STATOR_OUT + 10),
                arrowprops=dict(arrowstyle='->', color='#555', lw=0.6),
                fontsize=5.5, ha='center', fontfamily=FONT_NAME,
                bbox=dict(boxstyle='round,pad=0.2', fc='lightyellow', ec='#AAA', lw=0.5))

    # 定子可轴向移动标注
    ax.annotate(T('定子铁芯\n可轴向移动 ↔', 'Stator Core\nAxially Movable ↔'),
                xy=(AX_STATOR_L + 21, R_STATOR_IN + 15),
                xytext=(15, R_STATOR_IN + 15),
                arrowprops=dict(arrowstyle='->', color=COLORS['stator'], lw=0.8),
                fontsize=6, ha='center', color=COLORS['stator'], fontfamily=FONT_NAME,
                bbox=dict(boxstyle='round,pad=0.2', fc='#FFF3E0', ec=COLORS['stator'], lw=0.6))

    # ── 图例 ──────────────────────────────────────────────────────
    legend_items = [
        (COLORS['rim'], T('轮辋 6061-T6', 'Rim 6061-T6')),
        (COLORS['rotor_yoke'], T('转子轭', 'Rotor Yoke')),
        (COLORS['magnet'], T('永磁体', 'Magnets')),
        (COLORS['stator'], T('定子铁芯', 'Stator Core')),
        (COLORS['winding'], T('绕组', 'Windings')),
        (COLORS['shaft'], T('固定轴', 'Fixed Shaft')),
        (COLORS['bearing'], T('轴承', 'Bearing')),
        (COLORS['spring'], T('波形弹簧', 'Wave Spring')),
        (COLORS['rubber'], T('橡胶缓冲', 'Rubber Buffer')),
    ]
    ax_leg = fig.add_axes([0.06, 0.82, 0.18, 0.14])
    ax_leg.set_xlim(0, 10)
    ax_leg.set_ylim(0, len(legend_items) * 1.1)
    ax_leg.axis('off')
    ax_leg.add_patch(patches.FancyBboxPatch((0, 0), 10, len(legend_items) * 1.1,
                                            boxstyle='round,pad=0.3',
                                            fc='white', ec='#666', lw=0.8))
    for i, (col, lbl) in enumerate(reversed(legend_items)):
        y = i * 1.1 + 0.4
        ax_leg.add_patch(patches.Rectangle((0.5, y), 1.5, 0.7, fc=col, ec='#333', lw=0.5))
        ax_leg.text(2.3, y + 0.35, lbl, va='center', fontsize=5.5, fontfamily=FONT_NAME)

    ax.set_title(T('图1  X3-1500-72 整机轴向全剖面图（上半截面）',
                    'Fig.1  X3-1500-72 Axial Cross-Section (Upper Half)'),
                 fontsize=10, fontfamily=FONT_NAME, pad=8)

    add_title_block(fig, T('整机轴向全剖面', 'Axial Cross-Section'), 1)

    path = os.path.join(OUTPUT_DIR, 'figure_01_cross_section.png')
    fig.savefig(path, dpi=DPI, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f'[OK] figure_01_cross_section.png')


# ══════════════════════════════════════════════════════════════════
# 图2：螺旋槽凸轮副机构详图
# ══════════════════════════════════════════════════════════════════

def draw_figure_02():
    fig, axes = plt.subplots(1, 3, figsize=FIG_SIZE, dpi=DPI)
    fig.patch.set_facecolor('white')
    fig.subplots_adjust(left=0.05, right=0.97, bottom=0.12, top=0.88, wspace=0.35)

    # ── 子图1：螺旋槽展开图 ───────────────────────────────────────
    ax1 = axes[0]
    theta = np.linspace(0, 160, 300)
    disp = theta / 160 * 14.2

    # 槽中心线
    ax1.plot(theta, disp, color=COLORS['cam_line'], lw=2.0, label=T('槽中心线', 'Groove Center'))

    # 槽边界（槽宽8mm → 角度偏移约4.5°等效宽度）
    half_w = 4.5
    ax1.plot(theta, disp + 0.8, '--', color=COLORS['cam_boundary'], lw=0.8)
    ax1.plot(theta, disp - 0.8, '--', color=COLORS['cam_boundary'], lw=0.8)
    ax1.fill_between(theta, disp - 0.8, disp + 0.8, color=COLORS['cam_fill'],
                     alpha=0.5, label=T('槽区域', 'Groove Area'))

    # 滚针当前位置（中间）
    mid_i = 150
    ax1.plot(theta[mid_i], disp[mid_i], 'o', color=COLORS['needle'],
             ms=8, zorder=10, label=T('滚针位置', 'Needle Position'))
    ax1.annotate(T('滚针φ6mm', 'Needle φ6'),
                 xy=(theta[mid_i], disp[mid_i]),
                 xytext=(theta[mid_i] + 15, disp[mid_i] - 2),
                 arrowprops=dict(arrowstyle='->', color='k', lw=0.7),
                 fontsize=7, fontfamily=FONT_NAME)

    # 升角标注
    x0, y0 = 20, 20 / 160 * 14.2
    dx, dy = 25, 25 / 160 * 14.2
    ax1.annotate('', xy=(x0 + dx, y0), xytext=(x0, y0),
                 arrowprops=dict(arrowstyle='->', color='gray', lw=0.8))
    ax1.annotate('', xy=(x0 + dx, y0 + dy), xytext=(x0 + dx, y0),
                 arrowprops=dict(arrowstyle='->', color='gray', lw=0.8))
    ax1.text(x0 + dx / 2, y0 + dy / 2 + 0.3,
             T('ψ=15.8°', 'ψ=15.8°'), fontsize=7.5, ha='center', color='gray')

    # 端点标注
    ax1.text(2, 0.3, T('增磁端\n(Flux+)', 'Boost End'), fontsize=7, ha='left',
             color='green', fontfamily=FONT_NAME,
             bbox=dict(boxstyle='round,pad=0.2', fc='#E8F5E9', ec='green', lw=0.6))
    ax1.text(155, 13.5, T('弱磁端\n(Flux-)', 'Weaken End'), fontsize=7, ha='right',
             color='#B71C1C', fontfamily=FONT_NAME,
             bbox=dict(boxstyle='round,pad=0.2', fc='#FFEBEE', ec='#B71C1C', lw=0.6))

    # 行程标注
    ax1.annotate('', xy=(160, 14.2), xytext=(160, 0),
                 arrowprops=dict(arrowstyle='<->', color='#1565C0', lw=1.0,
                                 mutation_scale=8))
    ax1.text(165, 7.1, T('14.2mm', '14.2mm'), fontsize=7, color='#1565C0', va='center')

    ax1.set_xlim(-5, 185)
    ax1.set_ylim(-1.5, 16)
    ax1.set_xlabel(T('周向角度 (°)', 'Circumferential Angle (°)'), fontsize=8,
                   fontfamily=FONT_NAME)
    ax1.set_ylabel(T('轴向位移 (mm)', 'Axial Displacement (mm)'), fontsize=8,
                   fontfamily=FONT_NAME)
    ax1.set_title(T('螺旋槽展开图', 'Groove Unrolled View'), fontsize=9,
                  fontfamily=FONT_NAME)
    ax1.set_xticks([0, 40, 80, 120, 160])
    ax1.grid(True, alpha=0.3)
    ax1.legend(fontsize=6.5, loc='upper left')
    ax1.text(80, -1.0,
             T('旋转160°，行程14.2mm，升角15.8°',
               'Rotation 160°, Stroke 14.2mm, Lead Angle 15.8°'),
             ha='center', fontsize=7, fontfamily=FONT_NAME, style='italic', color='#555')

    # ── 子图2：A-A截面图 ──────────────────────────────────────────
    ax2 = axes[1]
    ax2.set_xlim(-20, 20)
    ax2.set_ylim(-14, 8)
    ax2.set_aspect('equal')
    ax2.axis('off')
    ax2.set_title(T('A-A 截面图', 'Section A-A'), fontsize=9, fontfamily=FONT_NAME)

    # 固定轴外圆弧（φ22mm半径11mm）
    shaft_arc = Arc((0, 0), 22, 22, theta1=190, theta2=350,
                    color=COLORS['shaft'], lw=2.0)
    ax2.add_patch(shaft_arc)
    # 轴填充
    shaft_fill = patches.Wedge((0, 0), 11, 190, 350, facecolor='#B0B0B0',
                                edgecolor=COLORS['shaft'], lw=1.0)
    ax2.add_patch(shaft_fill)
    ax2.text(0, 0, T('固定轴\nφ22', 'Shaft\nφ22'), ha='center', va='center',
             fontsize=6.5, fontfamily=FONT_NAME, color='white')

    # U型槽（宽8mm，深6mm）
    slot_x = [-4, 4, 4, -4, -4]
    slot_y = [-11, -11, -11 - 6, -11 - 6, -11]
    ax2.fill(slot_x, slot_y, facecolor='white', edgecolor='#333', lw=1.2)
    ax2.plot([-4, -4, 4, 4], [-11, -17, -17, -11], color='#333', lw=1.2)

    # 滚针（φ6mm = 半径3mm）
    needle_circle = plt.Circle((0, -14), 3, facecolor=COLORS['needle'],
                                edgecolor='#8B0000', lw=1.0)
    ax2.add_patch(needle_circle)
    ax2.text(0, -14, T('滚针', 'Needle'), ha='center', va='center',
             fontsize=5.5, color='white', fontfamily=FONT_NAME)

    # 尺寸标注
    ax2.annotate('', xy=(-4, -13.5), xytext=(4, -13.5),
                 arrowprops=dict(arrowstyle='<->', color='k', lw=0.7, mutation_scale=7))
    ax2.text(0, -13, T('槽宽8mm', 'W=8mm'), ha='center', va='bottom', fontsize=6.5,
             fontfamily=FONT_NAME)
    ax2.annotate('', xy=(6, -11), xytext=(6, -17),
                 arrowprops=dict(arrowstyle='<->', color='k', lw=0.7, mutation_scale=7))
    ax2.text(7, -14, T('槽深\n6mm', 'D=6mm'), ha='left', va='center', fontsize=6.5,
             fontfamily=FONT_NAME)
    ax2.text(0, -11, T('φ6mm 间隙0.1mm', 'φ6mm Clearance 0.1mm'),
             ha='center', va='bottom', fontsize=5.5, fontfamily=FONT_NAME,
             bbox=dict(boxstyle='round,pad=0.2', fc='lightyellow', ec='#AAA', lw=0.5))
    ax2.text(0, 6.5,
             T('材料：42CrMo+渗氮 HRC58+', 'Material: 42CrMo+Nitriding HRC58+'),
             ha='center', va='center', fontsize=6, fontfamily=FONT_NAME,
             bbox=dict(boxstyle='round,pad=0.3', fc='#F5F5F5', ec='#666', lw=0.6))

    # ── 子图3：力学分析图 ─────────────────────────────────────────
    ax3 = axes[2]
    ax3.set_xlim(-1, 11)
    ax3.set_ylim(-1, 9)
    ax3.set_aspect('equal')
    ax3.axis('off')
    ax3.set_title(T('力学分析图', 'Force Analysis'), fontsize=9, fontfamily=FONT_NAME)

    # 斜面基础（升角15.8°）
    angle_rad = np.radians(15.8)
    L = 7.0
    bx, by = 1.0, 2.0
    ex = bx + L * np.cos(angle_rad)
    ey = by + L * np.sin(angle_rad)
    # 斜面
    ax3.plot([bx, ex], [by, ey], color='#333', lw=2.0)
    ax3.fill([bx, ex, ex, bx], [by, ey, by, by], color='#E0E0E0', alpha=0.5)

    # 力矢量
    origin_x = bx + L / 2 * np.cos(angle_rad)
    origin_y = by + L / 2 * np.sin(angle_rad)

    # Ft（切向力，水平蓝色箭头）
    Ft_len = 2.5
    ax3.annotate('', xy=(origin_x + Ft_len, origin_y),
                 xytext=(origin_x, origin_y),
                 arrowprops=dict(arrowstyle='->', color='#1565C0', lw=1.5,
                                 mutation_scale=12))
    ax3.text(origin_x + Ft_len + 0.1, origin_y,
             T('Ft（切向力）', 'Ft (Tangential)'), fontsize=7, va='center',
             color='#1565C0', fontfamily=FONT_NAME)

    # Fa（轴向力，绿色垂直向上）
    Fa_len = 2.5
    ax3.annotate('', xy=(origin_x, origin_y + Fa_len),
                 xytext=(origin_x, origin_y),
                 arrowprops=dict(arrowstyle='->', color='#2E7D32', lw=1.5,
                                 mutation_scale=12))
    ax3.text(origin_x - 0.1, origin_y + Fa_len + 0.1,
             T('Fa=1630N', 'Fa=1630N'), fontsize=7, ha='right', va='bottom',
             color='#2E7D32', fontfamily=FONT_NAME)

    # Ff（摩擦力，红色沿斜面方向）
    Ff_len = 2.0
    ax3.annotate('', xy=(origin_x - Ff_len * np.cos(angle_rad),
                         origin_y - Ff_len * np.sin(angle_rad)),
                 xytext=(origin_x, origin_y),
                 arrowprops=dict(arrowstyle='->', color=COLORS['needle'], lw=1.5,
                                 mutation_scale=12))
    ax3.text(origin_x - Ff_len * np.cos(angle_rad) - 0.3,
             origin_y - Ff_len * np.sin(angle_rad) - 0.2,
             T('Ff=722N', 'Ff=722N'), fontsize=7, ha='right', va='top',
             color=COLORS['needle'], fontfamily=FONT_NAME)

    # 角度标注
    angle_arc = Arc((bx, by), 2.0, 2.0, theta1=0, theta2=15.8,
                    color='#555', lw=0.8)
    ax3.add_patch(angle_arc)
    ax3.text(bx + 1.2, by + 0.3, T('ψ=15.8°', 'ψ=15.8°'), fontsize=7, color='#555')

    # 效率文字框
    info_text = (T('η⁺ = 75.3%（正向驱动）\n', 'η⁺ = 75.3% (Forward)\n') +
                 T('驱动余量 = 7.8×\n', 'Drive margin = 7.8×\n') +
                 T('φf = 4.75°（当量摩擦角）', 'φf = 4.75° (Friction Angle)'))
    ax3.text(5.5, 8.2, info_text, ha='center', va='top', fontsize=7,
             fontfamily=FONT_NAME,
             bbox=dict(boxstyle='round,pad=0.4', fc='#E3F2FD', ec='#1565C0', lw=0.8))

    fig.suptitle(T('图2  X3-1500-72 螺旋槽凸轮副机构详图',
                    'Fig.2  X3-1500-72 Helical Cam Mechanism Detail'),
                 fontsize=10, fontfamily=FONT_NAME, y=0.96)

    add_title_block(fig, T('螺旋槽凸轮副机构', 'Cam Mechanism'), 2)

    path = os.path.join(OUTPUT_DIR, 'figure_02_cam_mechanism.png')
    fig.savefig(path, dpi=DPI, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f'[OK] figure_02_cam_mechanism.png')


# ══════════════════════════════════════════════════════════════════
# 图3：三工况轴向位置对比图
# ══════════════════════════════════════════════════════════════════

def draw_figure_03():
    fig, axes = plt.subplots(3, 1, figsize=FIG_SIZE, dpi=DPI)
    fig.patch.set_facecolor('white')
    fig.subplots_adjust(left=0.08, right=0.82, bottom=0.08, top=0.90,
                        hspace=0.55)

    # 三个工况参数
    conditions = [
        dict(
            label=T('工况A：低速增磁', 'Condition A: Low-Speed Flux Boost'),
            offset=0, overlap=42.0,
            color_overlap='#4CAF50', color_label='green',
            info=T('偏移 0mm | 重叠 42mm | 磁通 +17%\n弹簧力 200N | 转速 <200rpm',
                   'Offset 0mm | Overlap 42mm | Flux +17%\nSpring 200N | Speed <200rpm'),
            flux=T('磁通 Φ₀+17%', 'Flux Φ₀+17%'),
        ),
        dict(
            label=T('工况B：额定工况', 'Condition B: Rated Operation'),
            offset=5, overlap=37.0,
            color_overlap='#2196F3', color_label='#1565C0',
            info=T('偏移 5mm | 重叠 37mm | 基准磁通 Φ₀\n弹簧力 575N | 转速 350rpm | 扭矩 20.5N·m',
                   'Offset 5mm | Overlap 37mm | Flux Φ₀\nSpring 575N | Speed 350rpm | Torque 20.5N·m'),
            flux=T('磁通 Φ₀', 'Flux Φ₀'),
        ),
        dict(
            label=T('工况C：高速弱磁', 'Condition C: High-Speed Flux Weakening'),
            offset=14.2, overlap=27.8,
            color_overlap='#F44336', color_label='#B71C1C',
            info=T('偏移 14.2mm | 重叠 27.8mm | 磁通 -24%\n弹簧力 2200N | 转速 700rpm',
                   'Offset 14.2mm | Overlap 27.8mm | Flux -24%\nSpring 2200N | Speed 700rpm'),
            flux=T('磁通 Φ₀-24%', 'Flux Φ₀-24%'),
        ),
    ]

    # 参考尺寸
    MAG_L_REF = 0       # 磁钢左端
    MAG_R_REF = 58      # 磁钢右端
    STATOR_LEN = 42     # 定子长度

    for i, (ax, cond) in enumerate(zip(axes, conditions)):
        offset = cond['offset']
        stator_l = MAG_L_REF + offset
        stator_r = stator_l + STATOR_LEN
        overlap_l = max(MAG_L_REF, stator_l)
        overlap_r = min(MAG_R_REF, stator_r)

        ax.set_xlim(-15, 90)
        ax.set_ylim(-2, 16)
        ax.set_aspect('equal')
        ax.axis('off')

        # 磁钢区域（背景，红色半透明）
        ax.add_patch(patches.Rectangle((MAG_L_REF, 8), 58, 6,
                                       facecolor='#FFCDD2', edgecolor=COLORS['magnet'],
                                       lw=1.2, label=T('磁钢', 'Magnets')))
        ax.text(MAG_L_REF + 29, 11, T('磁钢 Lm=58mm', 'Magnets Lm=58mm'),
                ha='center', va='center', fontsize=7, fontfamily=FONT_NAME,
                color=COLORS['magnet'])

        # 非重叠磁钢区域（浅色）
        if stator_l > MAG_L_REF:
            ax.add_patch(patches.Rectangle((MAG_L_REF, 1), stator_l - MAG_L_REF, 6,
                                           facecolor='#FFCDD2', edgecolor=COLORS['stator'],
                                           lw=0.8, alpha=0.4))
        if stator_r < MAG_R_REF:
            ax.add_patch(patches.Rectangle((stator_r, 1), MAG_R_REF - stator_r, 6,
                                           facecolor='#FFCDD2', edgecolor=COLORS['stator'],
                                           lw=0.8, alpha=0.4))

        # 定子铁芯
        ax.add_patch(patches.Rectangle((stator_l, 1), STATOR_LEN, 6,
                                       facecolor=COLORS['stator'], edgecolor='#CC4400',
                                       lw=1.2, alpha=0.85))
        ax.text(stator_l + STATOR_LEN / 2, 4,
                T('定子 Ls=42mm', 'Stator Ls=42mm'),
                ha='center', va='center', fontsize=7, fontfamily=FONT_NAME, color='white')

        # 重叠区域高亮
        if overlap_r > overlap_l:
            ax.add_patch(patches.Rectangle((overlap_l, 0.2), overlap_r - overlap_l, 14.6,
                                           facecolor=cond['color_overlap'], alpha=0.15,
                                           edgecolor=cond['color_overlap'], lw=1.2,
                                           linestyle='--'))

        # 偏移标注箭头
        if offset > 0:
            ax.annotate('', xy=(stator_l, -0.5), xytext=(MAG_L_REF, -0.5),
                        arrowprops=dict(arrowstyle='<->', color='#555',
                                        lw=0.8, mutation_scale=8))
            ax.text((stator_l + MAG_L_REF) / 2, -1.3,
                    f'{T("偏移", "Offset")} {offset}mm',
                    ha='center', fontsize=6.5, fontfamily=FONT_NAME, color='#555')

        # 重叠标注
        if overlap_r > overlap_l:
            ax.annotate('', xy=(overlap_r, 15.5), xytext=(overlap_l, 15.5),
                        arrowprops=dict(arrowstyle='<->', color=cond['color_label'],
                                        lw=0.8, mutation_scale=8))
            ax.text((overlap_l + overlap_r) / 2, 15.9,
                    f'{T("重叠", "Overlap")} {cond["overlap"]}mm',
                    ha='center', va='bottom', fontsize=6.5, fontfamily=FONT_NAME,
                    color=cond['color_label'])

        # 标题
        ax.set_title(cond['label'], fontsize=9, fontfamily=FONT_NAME,
                     color=cond['color_label'], loc='left', x=0.01)

        # 信息框
        ax.text(78, 7.5, cond['info'], ha='left', va='center', fontsize=7,
                fontfamily=FONT_NAME,
                bbox=dict(boxstyle='round,pad=0.4', fc='#F5F5F5',
                          ec=cond['color_label'], lw=0.8),
                transform=ax.transData, clip_on=False)

    fig.suptitle(T('图3  X3-1500-72 三工况轴向位置对比图',
                    'Fig.3  X3-1500-72 Three Operating Conditions Comparison'),
                 fontsize=10, fontfamily=FONT_NAME, y=0.96)

    add_title_block(fig, T('三工况轴向位置对比', 'Three-Condition Comparison'), 3)

    path = os.path.join(OUTPUT_DIR, 'figure_03_three_conditions.png')
    fig.savefig(path, dpi=DPI, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f'[OK] figure_03_three_conditions.png')


# ══════════════════════════════════════════════════════════════════
# 图4：三层阻尼系统特性图
# ══════════════════════════════════════════════════════════════════

def draw_figure_04():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=FIG_SIZE, dpi=DPI)
    fig.patch.set_facecolor('white')
    fig.subplots_adjust(left=0.07, right=0.97, bottom=0.12, top=0.88, wspace=0.38)

    # ── 子图1：阻尼力-位移综合图 ──────────────────────────────────
    x = np.linspace(0, 14.2, 300)

    # 第一层：斜槽摩擦（蓝色水平线）
    F1 = np.full_like(x, 722.0)

    # 第二层：润滑脂间隙（绿色，30~300N随速度变化，用带状表示）
    F2_low = np.full_like(x, 30.0)
    F2_high = 30 + 270 * np.exp(-x / 8)  # 随位移略变化

    # 第三层：橡胶缓冲（红色，12~14.2mm指数上升）
    F3 = np.where(x < 12, 0,
                  2200 * ((x - 12) / 2.2) ** 2.5)

    # 总阻尼（取平均值估算）
    F_total = F1 + (F2_low + F2_high) / 2 + F3

    ax1.plot(x, F1, '-', color='#1565C0', lw=2.0, label=T('第一层：斜槽摩擦', 'Layer1: Cam Friction'))
    ax1.fill_between(x, F2_low, F2_high, color='#4CAF50', alpha=0.3,
                     label=T('第二层：润滑脂阻尼', 'Layer2: Grease Damping'))
    ax1.plot(x, F2_high, '--', color='#4CAF50', lw=1.0)
    ax1.plot(x, F3, '-', color='#F44336', lw=2.0, label=T('第三层：橡胶缓冲', 'Layer3: Rubber Buffer'))
    ax1.plot(x, F_total, '--k', lw=2.5, label=T('总阻尼合力', 'Total Damping Force'))

    # 标注关键点
    ax1.axhline(722, color='#1565C0', lw=0.5, linestyle=':', alpha=0.5)
    ax1.text(0.3, 745, T('第一层 722N（恒定）', 'Layer1 722N (Const.)'),
             fontsize=7, color='#1565C0', fontfamily=FONT_NAME)
    ax1.axvline(12, color='#F44336', lw=0.5, linestyle=':', alpha=0.5)
    ax1.text(12.1, 1000, T('缓冲起始\n12mm', 'Buffer Start\n12mm'),
             fontsize=6.5, color='#F44336', fontfamily=FONT_NAME)
    ax1.text(13.8, 2300, T('2200N', '2200N'), fontsize=7, color='#F44336',
             ha='center', fontfamily=FONT_NAME)

    ax1.set_xlim(0, 15)
    ax1.set_ylim(0, 2600)
    ax1.set_xlabel(T('轴向位移 (mm)', 'Axial Displacement (mm)'), fontsize=8,
                   fontfamily=FONT_NAME)
    ax1.set_ylabel(T('阻尼力 (N)', 'Damping Force (N)'), fontsize=8,
                   fontfamily=FONT_NAME)
    ax1.set_title(T('三层阻尼力-位移特性', 'Three-Layer Damping Force vs. Displacement'),
                  fontsize=9, fontfamily=FONT_NAME)
    ax1.legend(fontsize=7, loc='upper left', framealpha=0.9)
    ax1.grid(True, alpha=0.3)

    # ── 子图2：全温域对比 ─────────────────────────────────────────
    temp = np.linspace(-20, 80, 200)

    # V1.0硅油油腔（温度敏感，对数坐标）
    # -20°C约20000N，+80°C约80N（指数变化）
    F_v10 = 20000 * np.exp(-(temp + 20) / 25)
    F_v10 = np.clip(F_v10, 80, 25000)

    # V2.0三层阻尼（400~1200N，基本稳定）
    F_v20_low = 400 + 50 * np.cos((temp - 20) / 100 * np.pi)
    F_v20_high = 1200 + 100 * np.cos((temp - 20) / 100 * np.pi)

    ax2.semilogy(temp, F_v10, '-', color='#F44336', lw=2.0,
                 label=T('V1.0 硅油油腔', 'V1.0 Silicone Oil'))
    ax2.semilogy(temp, F_v20_low, '-', color='#1565C0', lw=1.5,
                 label=T('V2.0 三层阻尼', 'V2.0 Three-Layer'))
    ax2.semilogy(temp, F_v20_high, '-', color='#1565C0', lw=1.5)
    ax2.fill_between(temp, F_v20_low, F_v20_high, color='#BBDEFB', alpha=0.6)

    # 标注区域
    ax2.axvline(-10, color='#F44336', lw=0.8, linestyle='--', alpha=0.6)
    ax2.axhline(2200, color='gray', lw=0.5, linestyle=':', alpha=0.5)
    ax2.text(-19, 6000, T('低温锁死区\n(V1.0失效)', 'Low-Temp Lock\n(V1.0 Fail)'),
             fontsize=7, color='#B71C1C', fontfamily=FONT_NAME,
             bbox=dict(boxstyle='round,pad=0.3', fc='#FFEBEE', ec='#F44336', lw=0.6))
    ax2.text(20, 600, T('V2.0正常工作区\n400~1200N', 'V2.0 Normal Zone\n400~1200N'),
             fontsize=7, color='#1565C0', fontfamily=FONT_NAME,
             bbox=dict(boxstyle='round,pad=0.3', fc='#E3F2FD', ec='#1565C0', lw=0.6))
    ax2.text(2.2, 2300, T('弹簧最大载荷 2200N', 'Max Spring Load 2200N'),
             fontsize=6.5, color='gray', fontfamily=FONT_NAME)

    ax2.set_xlim(-20, 80)
    ax2.set_ylim(50, 50000)
    ax2.set_xlabel(T('温度 (°C)', 'Temperature (°C)'), fontsize=8,
                   fontfamily=FONT_NAME)
    ax2.set_ylabel(T('阻尼力 (N) — 对数坐标', 'Damping Force (N) — Log Scale'), fontsize=8,
                   fontfamily=FONT_NAME)
    ax2.set_title(T('全温域阻尼力对比（V1.0 vs V2.0）',
                     'Full-Temp-Range Damping Comparison (V1.0 vs V2.0)'),
                  fontsize=9, fontfamily=FONT_NAME)
    ax2.legend(fontsize=7.5, loc='upper right')
    ax2.grid(True, alpha=0.3, which='both')

    fig.suptitle(T('图4  X3-1500-72 三层阻尼系统特性图',
                    'Fig.4  X3-1500-72 Three-Layer Damping System Characteristics'),
                 fontsize=10, fontfamily=FONT_NAME, y=0.96)

    add_title_block(fig, T('三层阻尼系统特性', 'Damping System Characteristics'), 4)

    path = os.path.join(OUTPUT_DIR, 'figure_04_damping_system.png')
    fig.savefig(path, dpi=DPI, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f'[OK] figure_04_damping_system.png')


# ══════════════════════════════════════════════════════════════════
# 图5：波形弹簧力-位移特性图
# ══════════════════════════════════════════════════════════════════

def draw_figure_05():
    fig, ax = plt.subplots(figsize=FIG_SIZE, dpi=DPI)
    fig.patch.set_facecolor('white')
    fig.subplots_adjust(left=0.08, right=0.70, bottom=0.10, top=0.88)

    # 弹簧力计算
    # 段1：0~7mm，刚度75N/mm，预紧力200N
    x1 = np.linspace(0, 7, 100)
    y1 = 200 + 75 * x1

    # 段2：7~14.2mm，刚度175N/mm
    x2 = np.linspace(7, 14.2, 100)
    y2 = y1[-1] + 175 * (x2 - 7)

    x_all = np.concatenate([x1, x2])
    y_all = np.concatenate([y1, y2])

    # 等效线性弹簧参考
    k_eq = (y_all[-1] - y_all[0]) / (x_all[-1] - x_all[0])
    y_lin = y_all[0] + k_eq * x_all

    # 刚度区间填充
    ax.fill_between(x1, 0, y1, color='#E8F5E9', alpha=0.7,
                    label=T('0~7mm 刚度区（75N/mm）', '0~7mm Zone (75N/mm)'))
    ax.fill_between(x2, 0, y2, color='#FFF3E0', alpha=0.7,
                    label=T('7~14.2mm 刚度区（175N/mm）', '7~14.2mm Zone (175N/mm)'))

    # 等效线性参考
    ax.plot(x_all, y_lin, '--', color='#9E9E9E', lw=1.5,
            label=T('等效线性弹簧（参考）', 'Equiv. Linear Spring (ref.)'))

    # 实际非线性弹簧
    ax.plot(x_all, y_all, '-', color='#1565C0', lw=3.0,
            label=T('实际波形弹簧', 'Actual Wave Spring'))

    # 关键点标注
    # 预紧力200N
    ax.plot(0, 200, 'o', color='green', ms=9, zorder=10)
    ax.annotate(T('预紧力 200N', 'Preload 200N'),
                xy=(0, 200), xytext=(1.5, 280),
                arrowprops=dict(arrowstyle='->', color='green', lw=0.8),
                fontsize=8, color='green', fontfamily=FONT_NAME,
                bbox=dict(boxstyle='round,pad=0.2', fc='#E8F5E9', ec='green', lw=0.6))

    # 刚度突变点7mm
    ax.plot(7, y1[-1], 's', color='#FF9800', ms=9, zorder=10)
    ax.annotate(T(f'刚度突变点\n7mm / {y1[-1]:.0f}N', f'Stiffness Change\n7mm / {y1[-1]:.0f}N'),
                xy=(7, y1[-1]), xytext=(9, 700),
                arrowprops=dict(arrowstyle='->', color='#FF9800', lw=0.8),
                fontsize=8, color='#FF9800', fontfamily=FONT_NAME,
                bbox=dict(boxstyle='round,pad=0.2', fc='#FFF3E0', ec='#FF9800', lw=0.6))

    # 最大载荷2200N@14.2mm
    ax.plot(14.2, y2[-1], '^', color='#F44336', ms=9, zorder=10)
    ax.annotate(T(f'最大载荷\n{y2[-1]:.0f}N @ 14.2mm', f'Max Load\n{y2[-1]:.0f}N @ 14.2mm'),
                xy=(14.2, y2[-1]), xytext=(11, 2100),
                arrowprops=dict(arrowstyle='->', color='#F44336', lw=0.8),
                fontsize=8, color='#F44336', fontfamily=FONT_NAME,
                bbox=dict(boxstyle='round,pad=0.2', fc='#FFEBEE', ec='#F44336', lw=0.6))

    # 工作点标注
    # 空载（offset=0, F=200N）
    ax.axvline(0, color='green', lw=0.6, linestyle=':', alpha=0.5)
    ax.plot(0, 200, 'D', color='green', ms=7, zorder=9,
            label=T('工作点：空载', 'Op. Point: No Load'))
    # 额定（offset=5mm）
    F_rated = 200 + 75 * 5
    ax.axvline(5, color='#1565C0', lw=0.6, linestyle=':', alpha=0.5)
    ax.plot(5, F_rated, 'D', color='#1565C0', ms=7, zorder=9,
            label=T(f'工作点：额定（{F_rated:.0f}N）', f'Op. Point: Rated ({F_rated:.0f}N)'))
    # 高速弱磁
    ax.axvline(14.2, color='#F44336', lw=0.6, linestyle=':', alpha=0.5)
    ax.plot(14.2, y2[-1], 'D', color='#F44336', ms=7, zorder=9,
            label=T(f'工作点：高速弱磁（{y2[-1]:.0f}N）',
                    f'Op. Point: High-Speed ({y2[-1]:.0f}N)'))

    # 刚度标注文字
    ax.text(3.5, 100, T('k₁ = 75 N/mm', 'k₁ = 75 N/mm'),
            ha='center', fontsize=8.5, color='#2E7D32', fontfamily=FONT_NAME,
            bbox=dict(boxstyle='round,pad=0.2', fc='#E8F5E9', ec='#4CAF50', lw=0.6))
    ax.text(10.5, 100, T('k₂ = 175 N/mm', 'k₂ = 175 N/mm'),
            ha='center', fontsize=8.5, color='#E65100', fontfamily=FONT_NAME,
            bbox=dict(boxstyle='round,pad=0.2', fc='#FFF3E0', ec='#FF9800', lw=0.6))

    ax.set_xlim(-0.5, 15.5)
    ax.set_ylim(0, 2600)
    ax.set_xlabel(T('压缩位移 (mm)', 'Compression Displacement (mm)'), fontsize=9,
                  fontfamily=FONT_NAME)
    ax.set_ylabel(T('弹簧力 (N)', 'Spring Force (N)'), fontsize=9,
                  fontfamily=FONT_NAME)
    ax.set_title(T('图5  X3-1500-72 波形弹簧力-位移特性图',
                    'Fig.5  X3-1500-72 Wave Spring Force-Displacement Characteristics'),
                 fontsize=10, fontfamily=FONT_NAME, pad=8)
    ax.legend(fontsize=7.5, loc='upper left', framealpha=0.9)
    ax.grid(True, alpha=0.3)
    ax.set_xticks(np.arange(0, 16, 1))

    # 右侧弹簧规格文字框
    spec_text = (
        T('波形弹簧规格\n', 'Wave Spring Specs\n') +
        T('────────────────\n', '────────────────\n') +
        T('内径：φ24mm\n', 'ID: φ24mm\n') +
        T('外径：φ46mm\n', 'OD: φ46mm\n') +
        T('层数：6层叠合\n', 'Layers: 6 stacked\n') +
        T('材料：17-7PH 不锈钢\n', 'Material: 17-7PH SS\n') +
        T('预紧力：200N\n', 'Preload: 200N\n') +
        T('最大载荷：2200N\n', 'Max Load: 2200N\n') +
        T('k₁（0~7mm）：75N/mm\n', 'k₁(0~7mm): 75N/mm\n') +
        T('k₂（7~14.2mm）：175N/mm', 'k₂(7~14.2mm): 175N/mm')
    )
    ax.text(1.04, 0.70, spec_text, transform=ax.transAxes,
            fontsize=8, fontfamily=FONT_NAME, va='top',
            bbox=dict(boxstyle='round,pad=0.5', fc='#F5F5F5', ec='#666', lw=0.8))

    add_title_block(fig, T('波形弹簧力-位移特性', 'Spring Force-Displacement'), 5)

    path = os.path.join(OUTPUT_DIR, 'figure_05_spring_characteristics.png')
    fig.savefig(path, dpi=DPI, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f'[OK] figure_05_spring_characteristics.png')


# ══════════════════════════════════════════════════════════════════
# 图6：优化前后对比总览图
# ══════════════════════════════════════════════════════════════════

def draw_figure_06():
    fig = plt.figure(figsize=FIG_SIZE, dpi=DPI)
    fig.patch.set_facecolor('white')

    # ── 上半部分：参数对比表格 ────────────────────────────────────
    ax_table = fig.add_axes([0.03, 0.45, 0.94, 0.48])
    ax_table.axis('off')

    col_labels = [
        T('对比项目', 'Comparison'),
        T('V1.0（原设计）', 'V1.0 (Original)'),
        T('V2.0（优化后）', 'V2.0 (Optimized)'),
    ]
    row_data = [
        [T('传动机构', 'Drive Mechanism'),
         T('T20×5 丝杠副', 'T20×5 Lead Screw'),
         T('螺旋槽凸轮副', 'Helical Cam')],
        [T('定子最大旋转角', 'Max Stator Rotation'),
         T('1152°  ❌', '1152°  ❌'),
         T('≤ 160°  ✓', '≤ 160°  ✓')],
        [T('正向传动效率', 'Forward Drive Efficiency'),
         '50.5%',
         '75.3%'],
        [T('低温性能（-20°C）', 'Low-Temp Performance (-20°C)'),
         T('锁死失效  ❌', 'Locked/Failed  ❌'),
         T('正常工作  ✓', 'Normal Operation  ✓')],
        [T('导电方式', 'Power Leads'),
         T('导电滑环（超载83%）❌', 'Slip Ring (83% overload)❌'),
         T('柔性线束  ✓', 'Flex Harness  ✓')],
        [T('阻尼方式', 'Damping Method'),
         T('硅油油腔（温敏）❌', 'Silicone Oil (temp-sensitive)❌'),
         T('三层复合阻尼  ✓', 'Three-Layer Composite  ✓')],
        [T('零件总数', 'Total Part Count'),
         T('~28件', '~28 parts'),
         T('~21件（-25%）✓', '~21 parts (-25%)  ✓')],
    ]

    n_rows = len(row_data)
    n_cols = 3
    col_widths = [0.28, 0.36, 0.36]

    tbl = ax_table.table(
        cellText=row_data,
        colLabels=col_labels,
        cellLoc='center',
        loc='center',
        colWidths=col_widths,
    )
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(8.5)
    tbl.scale(1.0, 2.2)

    # 设置表头颜色
    for j in range(n_cols):
        cell = tbl[0, j]
        cell.set_facecolor('#37474F')
        cell.set_text_props(color='white', fontsize=9, fontweight='bold',
                            fontfamily=FONT_NAME)

    # 数据行颜色
    for i in range(1, n_rows + 1):
        # 左列：浅灰
        tbl[i, 0].set_facecolor('#F5F5F5')
        tbl[i, 0].set_text_props(fontsize=8, fontfamily=FONT_NAME)
        # V1.0列：浅红色
        tbl[i, 1].set_facecolor('#FFEBEE')
        tbl[i, 1].set_text_props(fontsize=8, color='#B71C1C', fontfamily=FONT_NAME)
        # V2.0列：浅绿色
        tbl[i, 2].set_facecolor('#E8F5E9')
        tbl[i, 2].set_text_props(fontsize=8, color='#1B5E20', fontfamily=FONT_NAME)

    ax_table.set_title(T('图6  X3-1500-72 优化前后对比总览',
                           'Fig.6  X3-1500-72 Design Optimization Overview'),
                       fontsize=11, fontfamily=FONT_NAME, pad=10)

    # ── 下半部分：示意对比图 ─────────────────────────────────────
    ax_v10 = fig.add_axes([0.04, 0.08, 0.38, 0.30])
    ax_v20 = fig.add_axes([0.58, 0.08, 0.38, 0.30])
    ax_arrow = fig.add_axes([0.42, 0.14, 0.16, 0.18])

    for ax_diag, version, color, issues in [
        (ax_v10, 'V1.0', '#F44336', [
            T('传动：T20×5丝杠', 'Drive: T20×5 Screw'),
            T('旋转角：1152° ❌', 'Rotation: 1152° ❌'),
            T('导电滑环 ❌', 'Slip Ring ❌'),
            T('硅油阻尼（温敏）❌', 'Oil Damping (temp) ❌'),
            T('低温锁死 ❌', 'Low-temp Lock ❌'),
            T('零件数：~28件', 'Parts: ~28'),
        ]),
        (ax_v20, 'V2.0', '#4CAF50', [
            T('传动：螺旋槽凸轮副', 'Drive: Helical Cam'),
            T('旋转角：≤160° ✓', 'Rotation: ≤160° ✓'),
            T('柔性线束 ✓', 'Flex Harness ✓'),
            T('三层复合阻尼 ✓', '3-Layer Damping ✓'),
            T('全温域正常工作 ✓', 'Full-Temp Normal ✓'),
            T('零件数：~21件(-25%) ✓', 'Parts: ~21(-25%) ✓'),
        ]),
    ]:
        ax_diag.set_xlim(0, 10)
        ax_diag.set_ylim(0, 10)
        ax_diag.axis('off')
        ax_diag.add_patch(patches.FancyBboxPatch((0.1, 0.1), 9.8, 9.8,
                           boxstyle='round,pad=0.3',
                           fc='white', ec=color, lw=2.0))
        ax_diag.text(5, 9.3, version, ha='center', va='center',
                     fontsize=16, fontweight='bold', color=color)
        for j, issue in enumerate(issues):
            y = 8.0 - j * 1.25
            ax_diag.text(0.7, y, '• ' + issue, va='center', fontsize=8,
                         fontfamily=FONT_NAME, color=color if '❌' in issue or '✓' in issue
                         else '#333')

    # 中间箭头
    ax_arrow.set_xlim(0, 10)
    ax_arrow.set_ylim(0, 10)
    ax_arrow.axis('off')
    ax_arrow.annotate('', xy=(9.0, 5), xytext=(1.0, 5),
                      arrowprops=dict(arrowstyle='->', color='#FF9800', lw=3.0,
                                      mutation_scale=20))
    ax_arrow.text(5, 7.5, T('优化', 'Optimize'), ha='center', va='center',
                  fontsize=14, fontweight='bold', color='#FF9800',
                  fontfamily=FONT_NAME)
    ax_arrow.text(5, 3, T('V1.0 → V2.0', 'V1.0 → V2.0'), ha='center', va='center',
                  fontsize=10, color='#555')

    add_title_block(fig, T('优化前后对比总览', 'Design Comparison Overview'), 6)

    path = os.path.join(OUTPUT_DIR, 'figure_06_comparison.png')
    fig.savefig(path, dpi=DPI, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f'[OK] figure_06_comparison.png')


# ══════════════════════════════════════════════════════════════════
# 主程序
# ══════════════════════════════════════════════════════════════════

def main():
    font_msg = (f'中文字体：{FONT_NAME}' if USE_CHINESE
                else 'No Chinese font found, using English labels (DejaVu Sans)')
    print(f'X3-1500-72 工程图纸生成脚本 {VERSION}')
    print(f'输出目录：{OUTPUT_DIR}')
    print(f'字体设置：{font_msg}')
    print(f'分辨率：{DPI} DPI | 图幅：{FIG_SIZE[0]:.2f}" × {FIG_SIZE[1]:.2f}"')
    print('-' * 60)

    draw_figure_01()
    draw_figure_02()
    draw_figure_03()
    draw_figure_04()
    draw_figure_05()
    draw_figure_06()

    print('-' * 60)
    print('全部6张图纸生成完成。')


if __name__ == '__main__':
    main()
