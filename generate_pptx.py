"""
生成电机系统培训 PPT（motor_training.pptx）
依赖：python-pptx
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt, Cm
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

# ── 颜色常量 ──────────────────────────────────────────────────
DARK_BLUE = RGBColor(0x1F, 0x39, 0x64)   # 深蓝标题
MID_BLUE  = RGBColor(0x2E, 0x74, 0xB5)   # 中蓝强调
WHITE     = RGBColor(0xFF, 0xFF, 0xFF)
LIGHT_BG  = RGBColor(0xF2, 0xF7, 0xFF)   # 浅蓝底色
HIGHLIGHT = RGBColor(0xFF, 0xE6, 0x99)   # 高亮黄
RED_BOLD  = RGBColor(0xC0, 0x00, 0x00)   # 红色
GRAY_TEXT = RGBColor(0x44, 0x44, 0x44)
TABLE_HDR = RGBColor(0x2E, 0x74, 0xB5)

SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)

LOGO_PATH     = "logo.png"
TEMPLATE_PATH = "template.pptx"


# ── 基础工具 ──────────────────────────────────────────────────

def new_prs():
    if os.path.exists(TEMPLATE_PATH):
        return Presentation(TEMPLATE_PATH)
    prs = Presentation()
    prs.slide_width  = SLIDE_W
    prs.slide_height = SLIDE_H
    return prs


def blank_slide(prs):
    """添加一张完全空白的幻灯片（使用空白版式）"""
    blank_layout = prs.slide_layouts[6]   # 空白
    return prs.slides.add_slide(blank_layout)


def add_background(slide, color=LIGHT_BG):
    """为幻灯片添加纯色背景矩形"""
    txBox = slide.shapes.add_shape(
        1,  # MSO_SHAPE_TYPE.RECTANGLE
        Inches(0), Inches(0), SLIDE_W, SLIDE_H
    )
    fill = txBox.fill
    fill.solid()
    fill.fore_color.rgb = color
    txBox.line.color.rgb = color
    txBox.zorder = 0


def set_shape_bg(shape, color):
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.color.rgb = color


def add_title_bar(slide, title_text, bar_color=DARK_BLUE):
    """添加顶部深色标题栏"""
    bar = slide.shapes.add_shape(
        1,
        Inches(0), Inches(0), SLIDE_W, Inches(1.25)
    )
    set_shape_bg(bar, bar_color)

    tf = bar.text_frame
    tf.word_wrap = False
    tf.margin_left  = Inches(0.3)
    tf.margin_top   = Pt(6)
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.LEFT
    run = p.add_run()
    run.text = title_text
    run.font.size = Pt(32)
    run.font.bold = True
    run.font.color.rgb = WHITE


def add_textbox(slide, text, left, top, width, height,
                font_size=Pt(18), bold=False, color=GRAY_TEXT,
                align=PP_ALIGN.LEFT, word_wrap=True):
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = word_wrap
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = font_size
    run.font.bold = bold
    run.font.color.rgb = color
    return txBox


def add_bullet_textbox(slide, bullets, left, top, width, height,
                       font_size=Pt(18), color=GRAY_TEXT, bullet_char="·"):
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = True
    for i, b in enumerate(bullets):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = PP_ALIGN.LEFT
        p.space_before = Pt(4)
        run = p.add_run()
        run.text = f"{bullet_char} {b}"
        run.font.size = font_size
        run.font.color.rgb = color
    return txBox


def add_highlight_box(slide, text, left, top, width, height,
                      bg=HIGHLIGHT, font_size=Pt(18), bold=True, color=RED_BOLD):
    box = slide.shapes.add_shape(1, left, top, width, height)
    set_shape_bg(box, bg)
    box.line.color.rgb = RED_BOLD

    tf = box.text_frame
    tf.word_wrap = True
    tf.margin_left  = Inches(0.1)
    tf.margin_right = Inches(0.1)
    tf.margin_top   = Inches(0.05)
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = text
    run.font.size = font_size
    run.font.bold = bold
    run.font.color.rgb = color
    return box


def add_conclusion_box(slide, text, top):
    """结论句 —— 高亮黄底，占整行"""
    add_highlight_box(
        slide, text,
        left=Inches(0.4), top=top,
        width=Inches(12.5), height=Inches(0.6),
        bg=HIGHLIGHT, font_size=Pt(18), bold=True, color=RED_BOLD
    )


def add_page_number(slide, page_num):
    add_textbox(
        slide, str(page_num),
        left=Inches(12.5), top=Inches(7.1),
        width=Inches(0.7), height=Inches(0.35),
        font_size=Pt(12), color=GRAY_TEXT,
        align=PP_ALIGN.RIGHT
    )


def add_logo(slide):
    if os.path.exists(LOGO_PATH):
        slide.shapes.add_picture(
            LOGO_PATH,
            left=SLIDE_W - Cm(2.5),
            top=Cm(0.2),
            width=Cm(1.5)
        )


def add_simple_table(slide, data, col_widths, left, top, header_row=True):
    """
    data: list of list of str
    col_widths: list of Inches/Cm
    """
    rows = len(data)
    cols = len(data[0])
    width = sum(col_widths)
    height = Inches(0.4) * rows

    table = slide.shapes.add_table(rows, cols, left, top, width, height).table

    for c_idx, cw in enumerate(col_widths):
        table.columns[c_idx].width = cw

    for r_idx, row_data in enumerate(data):
        for c_idx, cell_text in enumerate(row_data):
            cell = table.cell(r_idx, c_idx)
            cell.text = cell_text
            tf = cell.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            run = p.runs[0] if p.runs else p.add_run()
            run.text = cell_text
            if r_idx == 0 and header_row:
                run.font.bold = True
                run.font.color.rgb = WHITE
                run.font.size = Pt(16)
                cell.fill.solid()
                cell.fill.fore_color.rgb = TABLE_HDR
            else:
                run.font.size = Pt(15)
                run.font.color.rgb = GRAY_TEXT
                if r_idx % 2 == 0:
                    cell.fill.solid()
                    cell.fill.fore_color.rgb = RGBColor(0xDE, 0xEB, 0xF7)
                else:
                    cell.fill.solid()
                    cell.fill.fore_color.rgb = WHITE
    return table


# ── 18 张幻灯片 ───────────────────────────────────────────────

def slide01_cover(prs, n):
    slide = blank_slide(prs)
    # 深蓝全页背景
    bg = slide.shapes.add_shape(1, Inches(0), Inches(0), SLIDE_W, SLIDE_H)
    set_shape_bg(bg, DARK_BLUE)

    # 主标题
    add_textbox(slide, "电机系统培训",
                Inches(1.5), Inches(2.2), Inches(10), Inches(1.4),
                font_size=Pt(54), bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    # 副标题
    add_textbox(slide, "电驱系统部门内训 · 1小时精简版",
                Inches(1.5), Inches(3.8), Inches(10), Inches(0.8),
                font_size=Pt(28), bold=False, color=RGBColor(0xBD, 0xD7, 0xEE),
                align=PP_ALIGN.CENTER)
    # 底部装饰线
    line = slide.shapes.add_shape(1,
        Inches(1.5), Inches(3.6), Inches(10), Inches(0.05))
    set_shape_bg(line, MID_BLUE)

    add_logo(slide)
    add_page_number(slide, n)


def slide02_objectives(prs, n):
    slide = blank_slide(prs)
    add_background(slide)
    add_title_bar(slide, "今天学完能做什么")
    add_bullet_textbox(slide,
        ["看懂一份电机规格书",
         "在评审会上识别方案风险",
         "和供应商 / 控制团队对话时不被牵着走"],
        Inches(0.8), Inches(1.5), Inches(11.8), Inches(4.5),
        font_size=Pt(24))
    add_logo(slide)
    add_page_number(slide, n)


def slide03_scenes(prs, n):
    slide = blank_slide(prs)
    add_background(slide)
    add_title_bar(slide, "不懂电机，会在这三个地方出问题")
    add_bullet_textbox(slide,
        ["需求端堆峰值功率 → 热失控，没人拦住",
         "供应商换槽极方案 → NVH 量产暴露",
         "降本压磁钢用量 → 续航投诉，责任链断裂"],
        Inches(0.8), Inches(1.5), Inches(11.8), Inches(3.5),
        font_size=Pt(20))
    add_conclusion_box(slide,
        "每个场景都有一个能提前发现问题的人，今天让你成为那个人",
        top=Inches(5.8))
    add_logo(slide)
    add_page_number(slide, n)


def slide04_what_is_motor(prs, n):
    slide = blank_slide(prs)
    add_background(slide)
    add_title_bar(slide, "转矩从哪来")
    add_bullet_textbox(slide,
        ["磁场 × 电流 × 有效长度 = 力",
         "转矩靠磁，转速靠电压，效率靠设计"],
        Inches(0.8), Inches(1.6), Inches(11.8), Inches(4),
        font_size=Pt(24))
    add_logo(slide)
    add_page_number(slide, n)


def slide05_three_limits(prs, n):
    slide = blank_slide(prs)
    add_background(slide)
    add_title_bar(slide, "电机性能的三条边界")

    data = [
        ["约束线", "机理", "工程含义"],
        ["① 电流线", "电流↑→铜损↑→温升↑→绝缘寿命↓", "峰值转矩能持续多久，本质是热约束"],
        ["② 电压线", "转速↑→反EMF↑→需要弱磁", "最高车速和基速之间有个硬墙"],
        ["③ 铁损线", "转速↑→频率↑→铁损↑", "效率图右侧高速区塌陷的原因"],
    ]
    col_widths = [Inches(1.8), Inches(5.5), Inches(4.8)]
    add_simple_table(slide, data, col_widths,
                     Inches(0.4), Inches(1.4))

    add_conclusion_box(slide,
        '看到任何电机数据，先问\u201c这个数字在约束哪条线\u201d',
        top=Inches(5.8))
    add_logo(slide)
    add_page_number(slide, n)


def slide06_topology(prs, n):
    slide = blank_slide(prs)
    add_background(slide)
    add_title_bar(slide, "拓扑选择逻辑")

    data = [
        ["轮毂电机", "中置电机"],
        ["传动链短 / 成本低", "骑行质感好 / 散热好"],
        ["非簧载质量大", "传动损耗存在"],
        ["散热差", "成本更高"],
    ]
    col_widths = [Inches(5.5), Inches(5.5)]
    add_simple_table(slide, data, col_widths,
                     Inches(1.2), Inches(1.4))

    add_conclusion_box(slide,
        "整车定位决定拓扑，不是电机性能决定",
        top=Inches(5.8))
    add_logo(slide)
    add_page_number(slide, n)


def slide07_peak_vs_rated(prs, n):
    slide = blank_slide(prs)
    add_background(slide)
    add_title_bar(slide, '峰值是\u201c能做到\u201d，额定是\u201c能持续\u201d')
    add_bullet_textbox(slide,
        ["区别在哪？热。",
         "峰值转矩持续30秒 vs 3分钟，是完全不同的热设计",
         "常见坑：规格书只写峰值，不写持续时间"],
        Inches(0.8), Inches(1.5), Inches(11.8), Inches(3.2),
        font_size=Pt(20))
    add_highlight_box(slide,
        "评审必问：峰值转矩能持续多久？热模型验证了吗？",
        Inches(0.8), Inches(5.2), Inches(11.8), Inches(0.8),
        bg=HIGHLIGHT, font_size=Pt(20), bold=True, color=RED_BOLD)
    add_logo(slide)
    add_page_number(slide, n)


def slide08_efficiency_map(prs, n):
    slide = blank_slide(prs)
    add_background(slide)
    add_title_bar(slide, "效率图是电机的真实能力地图")
    add_bullet_textbox(slide,
        ["高效区在哪？WLTC工况点落在哪？",
         "峰值效率95% ≠ 实际续航好",
         "工况点在低效区，实际效率可能只有82%"],
        Inches(0.8), Inches(1.5), Inches(11.8), Inches(3.2),
        font_size=Pt(20))
    add_highlight_box(slide,
        "评审必问：工况点在效率图上标出来了吗？实测还是仿真？",
        Inches(0.8), Inches(5.2), Inches(11.8), Inches(0.8),
        bg=HIGHLIGHT, font_size=Pt(20), bold=True, color=RED_BOLD)
    add_logo(slide)
    add_page_number(slide, n)


def slide09_magnet(prs, n):
    slide = blank_slide(prs)
    add_background(slide)
    add_title_bar(slide, "磁钢是转矩密度和可靠性的核心")
    add_bullet_textbox(slide,
        ["牌号N35~N52：数字越大Br越高 → 转矩密度越高",
         "温度系数：Br每升温10℃下降约1.2%，120℃下已掉约12%",
         "退磁：工作点跑出安全边界 → 永久性能下降"],
        Inches(0.8), Inches(1.5), Inches(11.8), Inches(3.2),
        font_size=Pt(20))
    add_highlight_box(slide,
        "评审必问：最高工作温度下退磁裕度是多少？",
        Inches(0.8), Inches(5.2), Inches(11.8), Inches(0.8),
        bg=HIGHLIGHT, font_size=Pt(20), bold=True, color=RED_BOLD)
    add_logo(slide)
    add_page_number(slide, n)


def slide10_insulation(prs, n):
    slide = blank_slide(prs)
    add_background(slide)
    add_title_bar(slide, "绝缘等级是温升上限，不是工作温度")

    data = [
        ["等级", "温度上限", "适用场景"],
        ["F级", "155℃", "两轮车多数场景"],
        ["H级", "180℃", "高频重载工况"],
        ["200级", "200℃", "特殊需求"],
    ]
    col_widths = [Inches(2.5), Inches(2.5), Inches(6.5)]
    add_simple_table(slide, data, col_widths,
                     Inches(1.0), Inches(1.4))

    add_conclusion_box(slide,
        "不是越高越好，是成本和工况的匹配",
        top=Inches(5.8))
    add_logo(slide)
    add_page_number(slide, n)


def slide11_ke(prs, n):
    slide = blank_slide(prs)
    add_background(slide)
    add_title_bar(slide, "Ke 决定基速，是电机与控制器的接口参数")
    add_bullet_textbox(slide,
        ["Ke大 → 基速低 → 弱磁区宽 → 高速控制复杂",
         "Ke小 → 基速高 → 峰值转矩密度受限"],
        Inches(0.8), Inches(1.5), Inches(11.8), Inches(3),
        font_size=Pt(22))
    add_conclusion_box(slide,
        "Ke的选择是电机与控制双方共同决定，不是单边定",
        top=Inches(5.8))
    add_logo(slide)
    add_page_number(slide, n)


def slide12_summary_params(prs, n):
    slide = blank_slide(prs)
    add_background(slide)
    add_title_bar(slide, "4条记忆线索")

    items = [
        ("转矩密度", "→ 看磁钢和尺寸"),
        ("持续能力", "→ 看热设计"),
        ("高速表现", "→ 看Ke和弱磁策略"),
        ("实际续航", "→ 看效率图 × 工况点"),
    ]
    top = Inches(1.5)
    for key, val in items:
        row = slide.shapes.add_shape(1,
            Inches(0.5), top, Inches(12.3), Inches(0.85))
        set_shape_bg(row, RGBColor(0xDE, 0xEB, 0xF7))
        row.line.color.rgb = MID_BLUE

        tf = row.text_frame
        tf.word_wrap = False
        tf.margin_left = Inches(0.2)
        p = tf.paragraphs[0]
        r1 = p.add_run()
        r1.text = key
        r1.font.bold = True
        r1.font.size = Pt(20)
        r1.font.color.rgb = DARK_BLUE
        r2 = p.add_run()
        r2.text = f"  {val}"
        r2.font.size = Pt(20)
        r2.font.color.rgb = GRAY_TEXT

        top += Inches(1.0)

    add_logo(slide)
    add_page_number(slide, n)


def slide13_vehicle(prs, n):
    slide = blank_slide(prs)
    add_background(slide)
    add_title_bar(slide, "续航 / 爬坡 / 最高车速的约束来自哪")
    add_bullet_textbox(slide,
        ["续航：效率图工况点 × 电池容量，两头都要对",
         "爬坡/加速：峰值转矩 × 持续时间（热约束）",
         "最高车速：弱磁深度 × 电压裕量，不是无限往上推"],
        Inches(0.8), Inches(1.5), Inches(11.8), Inches(4.5),
        font_size=Pt(22))
    add_logo(slide)
    add_page_number(slide, n)


def slide14_controller(prs, n):
    slide = blank_slide(prs)
    add_background(slide)
    add_title_bar(slide, "电机和控制器是一个系统")
    add_bullet_textbox(slide,
        ["电压平台（48V/60V/72V/96V）直接约束电机设计空间",
         "控制策略（MTPA/弱磁）需要电机预留对应参数",
         "Ld/Lq不匹配 → 控制器效率损失，是选型问题不是控制问题"],
        Inches(0.8), Inches(1.5), Inches(11.8), Inches(3.5),
        font_size=Pt(20))
    add_conclusion_box(slide,
        "分开选型是高风险",
        top=Inches(5.8))
    add_logo(slide)
    add_page_number(slide, n)


def slide15_five_questions(prs, n):
    slide = blank_slide(prs)
    add_background(slide)
    add_title_bar(slide, "评审会上，这5个问题必须问")

    questions = [
        "① 峰值转矩能持续多久？热模型验证了吗？",
        "② 效率图工况点在哪？实测还是仿真？",
        "③ 最高工作温度下退磁裕度是多少？",
        "④ 槽极方案改过吗？NVH测过哪些转速段？",
        "⑤ 绝缘等级，振动/盐雾认证状态？",
    ]
    top = Inches(1.45)
    for q in questions:
        box = slide.shapes.add_shape(1,
            Inches(0.5), top, Inches(12.3), Inches(0.72))
        set_shape_bg(box, RGBColor(0xDE, 0xEB, 0xF7))
        box.line.color.rgb = MID_BLUE

        tf = box.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.15)
        p = tf.paragraphs[0]
        run = p.add_run()
        run.text = q
        run.font.size = Pt(18)
        run.font.color.rgb = DARK_BLUE
        run.font.bold = True

        top += Inches(0.82)

    add_logo(slide)
    add_page_number(slide, n)


def slide16_three_takeaways(prs, n):
    slide = blank_slide(prs)
    add_background(slide)
    add_title_bar(slide, "带走这3条")

    items = [
        "① 峰值数字看热，效率数字看工况点",
        "② 磁钢和绝缘是可靠性的两条命线",
        "③ 电机和控制器是一个系统，分开看会出问题",
    ]
    top = Inches(1.5)
    for item in items:
        box = slide.shapes.add_shape(1,
            Inches(0.6), top, Inches(12.1), Inches(1.4))
        set_shape_bg(box, MID_BLUE)
        box.line.color.rgb = DARK_BLUE

        tf = box.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.2)
        tf.margin_top   = Inches(0.05)
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.LEFT
        run = p.add_run()
        run.text = item
        run.font.size = Pt(24)
        run.font.bold = True
        run.font.color.rgb = WHITE

        top += Inches(1.6)

    add_logo(slide)
    add_page_number(slide, n)


def slide17_toolkit(prs, n):
    slide = blank_slide(prs)
    add_background(slide)
    add_title_bar(slide, "今天发给大家的材料")
    add_bullet_textbox(slide,
        ["供应商评审5问 Checklist（一页纸）",
         "效率图示例（标注工况点）",
         "常见参数速查卡"],
        Inches(0.8), Inches(1.6), Inches(11.8), Inches(4.5),
        font_size=Pt(22))
    add_logo(slide)
    add_page_number(slide, n)


def slide18_end(prs, n):
    slide = blank_slide(prs)
    # 深蓝全页背景
    bg = slide.shapes.add_shape(1, Inches(0), Inches(0), SLIDE_W, SLIDE_H)
    set_shape_bg(bg, DARK_BLUE)

    add_textbox(slide, "电驱系统部门内训",
                Inches(1.5), Inches(2.2), Inches(10), Inches(1.2),
                font_size=Pt(48), bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    add_textbox(slide, "问题 / 讨论 / 下一步",
                Inches(1.5), Inches(3.6), Inches(10), Inches(0.8),
                font_size=Pt(28), color=RGBColor(0xBD, 0xD7, 0xEE),
                align=PP_ALIGN.CENTER)

    line = slide.shapes.add_shape(1,
        Inches(1.5), Inches(3.5), Inches(10), Inches(0.05))
    set_shape_bg(line, MID_BLUE)

    add_logo(slide)
    add_page_number(slide, n)


# ── 主程序 ────────────────────────────────────────────────────

def main():
    prs = new_prs()

    builders = [
        slide01_cover,
        slide02_objectives,
        slide03_scenes,
        slide04_what_is_motor,
        slide05_three_limits,
        slide06_topology,
        slide07_peak_vs_rated,
        slide08_efficiency_map,
        slide09_magnet,
        slide10_insulation,
        slide11_ke,
        slide12_summary_params,
        slide13_vehicle,
        slide14_controller,
        slide15_five_questions,
        slide16_three_takeaways,
        slide17_toolkit,
        slide18_end,
    ]

    for idx, builder in enumerate(builders, start=1):
        builder(prs, idx)

    out = "motor_training.pptx"
    prs.save(out)
    print(f"✅ 已生成：{out}（共 {len(builders)} 页）")


if __name__ == "__main__":
    main()
