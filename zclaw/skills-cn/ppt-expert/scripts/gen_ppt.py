#!/usr/bin/env python3
"""
智体PPT专家 v2 - PPT生成引擎
支持动态建页、图表、图片、时间线、对比页等多种版式
"""
import json, sys, os, argparse
from pptx import Presentation
from pptx.util import Emu, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.chart import XL_CHART_TYPE
from pptx.chart.data import CategoryChartData

SW = Emu(12192000)
SH = Emu(6858000)
BASE = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE, "..", "templates")

# 模板配色索引
THEME_COLORS = {
    "tech-blue":       {"p": (0x1A,0x27,0x44), "s": (0x25,0x63,0xEB), "a": (0x3B,0x82,0xF6), "bg": (0xFF,0xFF,0xFF), "t": (0x33,0x33,0x33), "tl": (0x94,0xA3,0xB8)},
    "consulting-gold": {"p": (0x1B,0x26,0x3B), "s": (0x33,0x41,0x55), "a": (0xC9,0xA2,0x27), "bg": (0xFF,0xFF,0xFF), "t": (0x33,0x33,0x33), "tl": (0x94,0xA3,0xB8)},
    "dark-tech":       {"p": (0x0D,0x0D,0x1A), "s": (0x1A,0x27,0x44), "a": (0x3B,0x82,0xF6), "bg": (0x0F,0x17,0x2A), "t": (0xE2,0xE8,0xF0), "tl": (0x94,0xA3,0xB8)},
    "clean-white":     {"p": (0x1E,0x29,0x3B), "s": (0x3B,0x82,0xF6), "a": (0x25,0x63,0xEB), "bg": (0xFF,0xFF,0xFF), "t": (0x33,0x33,0x33), "tl": (0x94,0xA3,0xB8)},
    "vibrant-orange":  {"p": (0x1A,0x1A,0x2E), "s": (0xF9,0x73,0x16), "a": (0xFB,0x92,0x3C), "bg": (0xFF,0xFF,0xFF), "t": (0x33,0x33,0x33), "tl": (0x94,0xA3,0xB8)},
    "business-gray":   {"p": (0x33,0x41,0x55), "s": (0x47,0x55,0x69), "a": (0x3B,0x82,0xF6), "bg": (0xFF,0xFF,0xFF), "t": (0x33,0x33,0x33), "tl": (0x94,0xA3,0xB8)},
    "nature-green":    {"p": (0x0A,0x26,0x18), "s": (0x16,0xA3,0x4A), "a": (0x22,0xC5,0x5E), "bg": (0xFF,0xFF,0xFF), "t": (0x33,0x33,0x33), "tl": (0x94,0xA3,0xB8)},
    "creative-purple": {"p": (0x0F,0x34,0x60), "s": (0x7C,0x3A,0xED), "a": (0x8B,0x5C,0xF6), "bg": (0xFF,0xFF,0xFF), "t": (0x33,0x33,0x33), "tl": (0x94,0xA3,0xB8)},
}

def rgb(c):
    return RGBColor(*c)

def add_shape(slide, l, t, w, h, fill_color=None, line_color=None):
    sp = slide.shapes.add_shape(1, l, t, w, h)
    if fill_color:
        sp.fill.solid()
        sp.fill.fore_color.rgb = rgb(fill_color) if isinstance(fill_color, tuple) else fill_color
    else:
        sp.fill.background()
    if line_color:
        sp.line.color.rgb = rgb(line_color) if isinstance(line_color, tuple) else line_color
    else:
        sp.line.fill.background()
    return sp

def add_text(slide, l, t, w, h, text, sz=14, color=(0x33,0x33,0x33), bold=False, align=PP_ALIGN.LEFT):
    box = slide.shapes.add_textbox(l, t, w, h)
    tf = box.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]; p.text = text
    p.font.size = Pt(sz); p.font.color.rgb = rgb(color)
    p.font.bold = bold; p.font.name = "Microsoft YaHei"; p.alignment = align
    return box

def add_multi_text(slide, l, t, w, h, lines, sz=14, color=(0x33,0x33,0x33), bullet="▸"):
    """多行文本，每行一个段落"""
    box = slide.shapes.add_textbox(l, t, w, h)
    tf = box.text_frame; tf.word_wrap = True
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = f"{bullet} {line}" if bullet else line
        p.font.size = Pt(sz); p.font.color.rgb = rgb(color)
        p.font.name = "Microsoft YaHei"; p.space_after = Pt(6)
    return box

def add_title_bar(slide, c, title):
    """页标题通用"""
    add_shape(slide, Emu(700000), Emu(350000), Emu(600000), Emu(50000), fill_color=rgb(c["s"]))
    add_text(slide, Emu(700000), Emu(500000), Emu(10000000), Emu(500000), title, 24, c["p"], True)

def build_cover(slide, c, data):
    add_shape(slide, 0, 0, SW, SH, fill_color=rgb(c["p"]))
    add_shape(slide, 0, SH-Emu(80000), SW, Emu(80000), fill_color=rgb(c["s"]))
    add_text(slide, Emu(800000), Emu(1200000), Emu(10500000), Emu(1200000),
             data.get("title","[标题]"), 40, (0xFF,0xFF,0xFF), True)
    add_text(slide, Emu(800000), Emu(2500000), Emu(10500000), Emu(600000),
             data.get("subtitle",""), 20, (0xC0,0xC0,0xC0))
    add_text(slide, Emu(800000), Emu(3200000), Emu(10500000), Emu(400000),
             data.get("date",""), 14, c["tl"])

def build_toc(slide, c, items):
    add_text(slide, Emu(800000), Emu(400000), Emu(3000000), Emu(500000), "目录", 32, c["p"], True)
    add_shape(slide, Emu(700000), Emu(900000), Emu(400000), Emu(40000), fill_color=rgb(c["s"]))
    for i, item in enumerate(items):
        row, col = i // 2, i % 2
        x, y = Emu(800000 + col * 5200000), Emu(1600000 + row * 1200000)
        card = add_shape(slide, x, y, Emu(4800000), Emu(900000), fill_color=rgb(c["bg"]), line_color=(0xE2,0xE8,0xF0))
        add_text(slide, x+Emu(200000), y+Emu(100000), Emu(4400000), Emu(700000),
                 f"{i+1:02d}  {item}", 16, c["p"], True)

def build_section(slide, c, data):
    num = data.get("number","01")
    add_shape(slide, Emu(0), Emu(2400000), SW, Emu(2000000), fill_color=(0xF1,0xF5,0xF9))
    add_text(slide, Emu(800000), Emu(800000), Emu(2000000), Emu(500000), num, 48, c["s"], True)
    add_text(slide, Emu(800000), Emu(2700000), Emu(10500000), Emu(1000000),
             data.get("title",""), 36, c["p"], True)
    add_text(slide, Emu(800000), Emu(3800000), Emu(10500000), Emu(500000),
             data.get("desc",""), 16, c["tl"])

def build_text_slide(slide, c, data):
    add_title_bar(slide, c, data.get("title",""))
    items = data.get("items", [])
    if items:
        add_multi_text(slide, Emu(700000), Emu(1200000), Emu(10500000), Emu(5000000), items, 15, c["t"])

def build_data_slide(slide, c, data):
    add_title_bar(slide, c, data.get("title",""))
    metrics = data.get("metrics", [])
    for i, m in enumerate(metrics):
        x = Emu(700000 + i * 2800000)
        y = Emu(1400000)
        card = add_shape(slide, x, y, Emu(2500000), Emu(1800000),
                        fill_color=rgb(c["bg"]), line_color=(0xE2,0xE8,0xF0))
        add_shape(slide, x+Emu(200000), y+Emu(200000), Emu(600000), Emu(30000), fill_color=rgb(c["s"]))
        val = m.get("value","[X]")
        lbl = m.get("label","")
        add_text(slide, x+Emu(200000), y+Emu(300000), Emu(2100000), Emu(600000),
                 str(val), 36, c["s"], True, PP_ALIGN.CENTER)
        add_text(slide, x+Emu(200000), y+Emu(1000000), Emu(2100000), Emu(400000),
                 lbl, 14, c["tl"], align=PP_ALIGN.CENTER)

def build_compare_slide(slide, c, data):
    add_title_bar(slide, c, data.get("title",""))
    # Left (old)
    lc = add_shape(slide, Emu(700000), Emu(1300000), Emu(5000000), Emu(4800000),
                   fill_color=(0xFE,0xF2,0xF2), line_color=(0xFE,0xCA,0xCA))
    add_shape(slide, Emu(700000), Emu(1300000), Emu(5000000), Emu(50000), fill_color=(0xDC,0x26,0x26))
    add_text(slide, Emu(900000), Emu(1500000), Emu(4600000), Emu(400000),
             data.get("old_title","传统方式"), 20, (0xDC,0x26,0x26), True)
    add_multi_text(slide, Emu(900000), Emu(2000000), Emu(4600000), Emu(4000000),
                   data.get("old_items",[]), 14, (0x55,0x55,0x55))
    # Right (new)
    rc = add_shape(slide, Emu(6200000), Emu(1300000), Emu(5200000), Emu(4800000),
                   fill_color=(0xF0,0xF9,0xFF), line_color=(0xBF,0xDB,0xFE))
    add_shape(slide, Emu(6200000), Emu(1300000), Emu(5200000), Emu(50000), fill_color=rgb(c["s"]))
    add_text(slide, Emu(6400000), Emu(1500000), Emu(4800000), Emu(400000),
             data.get("new_title","新方案"), 20, c["s"], True)
    add_multi_text(slide, Emu(6400000), Emu(2000000), Emu(4800000), Emu(4000000),
                   data.get("new_items",[]), 14, (0x55,0x55,0x55))

def build_timeline_slide(slide, c, data):
    add_title_bar(slide, c, data.get("title",""))
    items = data.get("items", [])
    # Timeline line
    add_shape(slide, Emu(6000000), Emu(1300000), Emu(40000), Emu(4800000), fill_color=rgb(c["s"]))
    for i, item in enumerate(items):
        y = Emu(1400000 + i * 800000)
        dot = add_shape(slide, Emu(5950000), y+Emu(50000), Emu(100000), Emu(100000),
                        fill_color=rgb(c["s"]), line_color=rgb(c["s"]))
        add_text(slide, Emu(2500000), y, Emu(3200000), Emu(800000),
                 item.get("time",""), 16, c["s"], True, PP_ALIGN.RIGHT)
        add_text(slide, Emu(6250000), y, Emu(5500000), Emu(800000),
                 item.get("event",""), 14, c["t"])

def build_end_slide(slide, c, data):
    add_shape(slide, 0, 0, SW, SH, fill_color=rgb(c["p"]))
    add_text(slide, Emu(800000), Emu(1800000), Emu(10500000), Emu(1200000),
             data.get("text","谢谢"), 44, (0xFF,0xFF,0xFF), True, PP_ALIGN.CENTER)
    add_text(slide, Emu(800000), Emu(3200000), Emu(10500000), Emu(600000),
             data.get("contact",""), 18, (0xC0,0xC0,0xC0), align=PP_ALIGN.CENTER)

BUILDERS = {
    "cover": build_cover, "toc": build_toc, "section": build_section,
    "text": build_text_slide, "data": build_data_slide,
    "compare": build_compare_slide, "timeline": build_timeline_slide,
    "end": build_end_slide
}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--template", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--data", required=True)
    args = parser.parse_args()

    with open(args.data, "r", encoding="utf-8") as f:
        data = json.load(f)

    if args.template not in THEME_COLORS:
        print(f"❌ 未知模板: {args.template}，可选: {list(THEME_COLORS.keys())}")
        sys.exit(1)

    c = THEME_COLORS[args.template]
    prs = Presentation()
    prs.slide_width = SW; prs.slide_height = SH
    layout = prs.slide_layouts[6]  # blank

    slides_data = data.get("slides", [])
    for sd in slides_data:
        stype = sd.get("type", "text")
        if stype in BUILDERS:
            slide = prs.slides.add_slide(layout)
            BUILDERS[stype](slide, c, sd)
        else:
            print(f"⚠️ 未知版式: {stype}，已跳过")

    prs.save(args.output)
    print(f"✅ PPT已生成: {args.output} ({len(slides_data)}页)")

if __name__ == "__main__":
    main()