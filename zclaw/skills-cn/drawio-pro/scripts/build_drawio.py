#!/usr/bin/env python3
"""
drawio-pro 核心引擎：逻辑结构 → .drawio XML + SVG 预览

用法：
  python3 build_drawio.py --input logic.json --output diagram.drawio [--preview diagram.svg]

logic.json 格式：
{
  "type": "flowchart|architecture|sequence|uml",  # 布局类型（uml=类图）
  "title": "图表标题",
  "direction": "LR|TB",                       # 布局方向（默认 LR）
  "nodes": [
    {"id": "n1", "label": "节点名", "shape": "rounded|rect|process|start|end|cylinder",
     "color": "blue|lightblue|green|gray|red|purple|orange", "layer": 0, "width": 140, "height": 50},
  ],
  "edges": [
    {"from": "n1", "to": "n2", "label": "连线标签", "style": "orthogonal|curved"}
  ]
}
"""
import argparse
import json
import os
import sys
import uuid
from datetime import datetime, timezone
from xml.sax.saxutils import escape as xml_escape

# ============ 配色方案 ============
COLORS = {
    "blue":       {"fill": "#2563eb", "stroke": "#1e40af", "font": "#ffffff",  "label": "主色蓝"},
    "lightblue":  {"fill": "#e0f2fe", "stroke": "#0284c7", "font": "#0f172a",  "label": "浅蓝"},
    "green":      {"fill": "#dcfce7", "stroke": "#16a34a", "font": "#0f172a",  "label": "绿"},
    "lightgreen": {"fill": "#dcfce7", "stroke": "#16a34a", "font": "#0f172a",  "label": "浅绿"},
    "gray":       {"fill": "#f1f5f9", "stroke": "#64748b", "font": "#0f172a",  "label": "灰"},
    "red":        {"fill": "#fef2f2", "stroke": "#dc2626", "font": "#0f172a",  "label": "红"},
    "purple":     {"fill": "#f3e8ff", "stroke": "#9333ea", "font": "#0f172a",  "label": "紫"},
    "orange":     {"fill": "#fff7ed", "stroke": "#ea580c", "font": "#0f172a",  "label": "橙"},
    "white":      {"fill": "#ffffff", "stroke": "#475569", "font": "#0f172a",  "label": "白"},
}

SHAPE_STYLES = {
    "rounded":    "rounded=1;whiteSpace=wrap;html=1;arcSize=12;",
    "rect":       "whiteSpace=wrap;html=1;",
    "process":    "rounded=1;whiteSpace=wrap;html=1;arcSize=8;",
    "start":      "ellipse;whiteSpace=wrap;html=1;",
    "end":        "ellipse;whiteSpace=wrap;html=1;",
    "cylinder":   "shape=cylinder;whiteSpace=wrap;html=1;boundedLbl=1;",
    "diamond":    "rhombus;whiteSpace=wrap;html=1;",
    "subgraph":   "rounded=1;whiteSpace=wrap;html=1;dashed=1;fillColor=#f8fafc;fontColor=#0f172a;",
}

# UML 类图节点样式（带 HTML 三分栏）
UML_CLASS_STYLE = "rounded=1;whiteSpace=wrap;html=1;overflow=hidden;labelBackgroundColor=#ffffff;"

# UML 关系连线样式映射
UML_EDGE_STYLES = {
    "inheritance":  "edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=block;endFill=0;html=1;",
    "realization":  "edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=block;endFill=0;dashed=1;html=1;",
    "aggregation":  "edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=diamond;endFill=0;html=1;",
    "composition":  "edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=diamond;endFill=1;html=1;",
    "association":  "edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=open;html=1;",
    "dependency":   "edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=open;dashed=1;html=1;",
}
DEFAULT_SHAPE = "rounded"
DEFAULT_NODE_W = 140
DEFAULT_NODE_H = 50
LAYER_GAP_X = 200  # 层间水平间距
LAYER_GAP_Y = 80   # 层内垂直间距
PADDING = 40       # 画布边距


def parse_args():
    parser = argparse.ArgumentParser(description="Drawio 图表生成引擎")
    parser.add_argument("--input", "-i", required=True, help="输入 JSON 文件路径")
    parser.add_argument("--output", "-o", required=True, help="输出 .drawio 文件路径")
    parser.add_argument("--preview", "-p", help="输出 SVG 预览路径（可选）")
    parser.add_argument("--png", help="输出 PNG 高清图路径（可选，需 cairosvg 支持）")
    return parser.parse_args()


def load_input(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def auto_layout(data):
    """自动布局：计算每个节点的 x/y/width/height"""
    nodes = data.get("nodes", [])
    edges = data.get("edges", [])
    direction = data.get("direction", "LR")
    title = data.get("title", "")
    chart_type = data.get("type", "flowchart")

    # UML 类图：根据属性和方法数量动态计算节点高度
    for n in nodes:
        if chart_type == "uml":
            attrs = n.get("attributes", [])
            methods = n.get("methods", [])
            # 类名行(30) + 分隔线 + 属性(每行18) + 分隔线 + 方法(每行18) + padding
            line_count = 1 + len(attrs) + len(methods)
            n["height"] = max(60, 30 + line_count * 18 + 10)
            n["width"] = max(n.get("width", 180), 160)

    # 按 layer 分组
    layers = {}
    for n in nodes:
        l = n.get("layer", 0)
        layers.setdefault(l, []).append(n)

    if not layers:
        return nodes, edges

    sorted_layers = sorted(layers.keys())

    if direction == "LR":
        # 从左到右布局
        for li, l in enumerate(sorted_layers):
            layer_nodes = layers[l]
            n_count = len(layer_nodes)
            total_h = n_count * DEFAULT_NODE_H + (n_count - 1) * LAYER_GAP_Y
            start_y = PADDING + max(0, (500 - total_h) / 2)

            for ni, n in enumerate(layer_nodes):
                n["x"] = PADDING + li * (DEFAULT_NODE_W + LAYER_GAP_X)
                n["y"] = start_y + ni * (DEFAULT_NODE_H + LAYER_GAP_Y)
                n["width"] = n.get("width", DEFAULT_NODE_W)
                n["height"] = n.get("height", DEFAULT_NODE_H)
    else:
        # TB 从上到下布局
        for li, l in enumerate(sorted_layers):
            layer_nodes = layers[l]
            n_count = len(layer_nodes)
            total_w = n_count * DEFAULT_NODE_W + (n_count - 1) * LAYER_GAP_X
            start_x = PADDING + max(0, (600 - total_w) / 2)

            for ni, n in enumerate(layer_nodes):
                n["x"] = start_x + ni * (DEFAULT_NODE_W + LAYER_GAP_X)
                n["y"] = PADDING + li * (DEFAULT_NODE_H + LAYER_GAP_Y)
                n["width"] = n.get("width", DEFAULT_NODE_W)
                n["height"] = n.get("height", DEFAULT_NODE_H)

    return nodes, edges


def make_style(color_key, shape):
    """生成 draw.io style 字符串"""
    c = COLORS.get(color_key, COLORS["lightblue"])
    shape_style = SHAPE_STYLES.get(shape, SHAPE_STYLES[DEFAULT_SHAPE])
    return f"{shape_style}fillColor={c['fill']};strokeColor={c['stroke']};fontColor={c['font']};"


def build_drawio_xml(nodes, edges, data):
    """生成 .drawio mxGraphModel XML"""
    mxfile_id = str(uuid.uuid4())
    diag_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    chart_type = data.get("type", "flowchart")

    cells = []
    # 必须的根 cell
    cells.append('<mxCell id="0" />')
    cells.append('<mxCell id="1" parent="0" />')

    cell_id = 2
    # 节点
    for n in nodes:
        cid = str(cell_id)
        n["_cell_id"] = cid
        cell_id += 1
        color_key = n.get("color", "lightblue")
        c = COLORS.get(color_key, COLORS["lightblue"])
        x = n.get("x", 0)
        y = n.get("y", 0)
        w = n.get("width", DEFAULT_NODE_W)
        h = n.get("height", DEFAULT_NODE_H)

        if chart_type == "uml":
            # UML 类图：生成 HTML 三分栏
            label = n.get("label", "")
            stereotype = n.get("stereotype", "")
            attrs = n.get("attributes", [])
            methods = n.get("methods", [])

            html_parts = ['<div style="border:none;">']
            # 原型（如 <<interface>>）
            if stereotype:
                html_parts.append(f'<p style="margin:2px 0;text-align:center;font-style:italic;font-size:10px;">{xml_escape(stereotype)}</p>')
            # 类名
            html_parts.append(f'<p style="margin:4px 0 2px;text-align:center;font-weight:bold;font-size:12px;">{xml_escape(label)}</p>')
            html_parts.append('<hr style="margin:2px 0;">')
            # 属性
            for attr in attrs:
                html_parts.append(f'<p style="margin:1px 4px;font-size:10px;">{xml_escape(attr)}</p>')
            html_parts.append('<hr style="margin:2px 0;">')
            # 方法
            for method in methods:
                html_parts.append(f'<p style="margin:1px 4px;font-size:10px;">{xml_escape(method)}</p>')
            html_parts.append('</div>')
            value = "".join(html_parts)
            value_escaped = xml_escape(value)

            style = f"{UML_CLASS_STYLE}fillColor={c['fill']};strokeColor={c['stroke']};fontColor={c['font']};"
            cells.append(
                f'<mxCell id="{cid}" value="{value_escaped}" style="{style}" vertex="1" parent="1">\n'
                f'  <mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry" />\n'
                f'</mxCell>'
            )
        else:
            # 普通节点
            label = xml_escape(n.get("label", ""))
            shape = n.get("shape", DEFAULT_SHAPE)
            style = make_style(color_key, shape)
            cells.append(
                f'<mxCell id="{cid}" value="{label}" style="{style}" vertex="1" parent="1">\n'
                f'  <mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry" />\n'
                f'</mxCell>'
            )

    # 连线
    for e in edges:
        cid = str(cell_id)
        cell_id += 1
        src = e.get("from", "")
        tgt = e.get("to", "")
        label = xml_escape(e.get("label", ""))

        # 检查是否有 UML 关系类型
        uml_type = e.get("umlType", "")
        if chart_type == "uml" and uml_type in UML_EDGE_STYLES:
            style_str = UML_EDGE_STYLES[uml_type]
        else:
            edge_style = e.get("style", "orthogonal")
            if edge_style == "curved":
                style_str = "edgeStyle=curved;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;"
            else:
                style_str = "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;"

        # 查找源和目标的 cell_id
        src_id = next((n["_cell_id"] for n in nodes if n["id"] == src), src)
        tgt_id = next((n["_cell_id"] for n in nodes if n["id"] == tgt), tgt)

        cells.append(
            f'<mxCell id="{cid}" value="{label}" style="{style_str}" edge="1" parent="1" source="{src_id}" target="{tgt_id}">\n'
            f'  <mxGeometry relative="1" as="geometry" />\n'
            f'</mxCell>'
        )

    cells_xml = "\n".join(cells)

    xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<mxfile host="drawio-pro-skill" modified="{now}" agent="drawio-pro" version="24.7.6" etag="{mxfile_id}" type="device">
  <diagram name="{xml_escape(data.get('title', 'Diagram'))}" id="{diag_id}">
    <mxGraphModel dx="0" dy="0" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="850" pageHeight="1100" math="0" shadow="0">
      <root>
{cells_xml}
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>'''
    return xml


def build_svg_preview(nodes, edges, data):
    """从同一数据生成 SVG 预览图"""
    direction = data.get("direction", "LR")
    chart_type = data.get("type", "flowchart")

    # 计算画布尺寸
    if not nodes:
        return '<svg xmlns="http://www.w3.org/2000/svg" width="200" height="100"><text x="10" y="20">无节点</text></svg>'

    max_x = max(n.get("x", 0) + n.get("width", DEFAULT_NODE_W) for n in nodes) + PADDING
    max_y = max(n.get("y", 0) + n.get("height", DEFAULT_NODE_H) for n in nodes) + PADDING
    canvas_w = max(max_x, 400)
    canvas_h = max(max_y, 300)

    # 用 Sans 字体，屏幕显示更清晰
    svg_parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_w}" height="{canvas_h}" '
                 f'viewBox="0 0 {canvas_w} {canvas_h}" '
                 f'style="background:#ffffff;font-family:-apple-system,BlinkMacSystemFont,\'Noto Sans CJK SC\',\'PingFang SC\',\'Microsoft YaHei\',sans-serif;">']

    # 标题（字号 16 加粗）
    title = data.get("title", "")
    if title:
        svg_parts.append(f'<text x="{canvas_w/2}" y="24" text-anchor="middle" font-size="16" '
                         f'font-weight="bold" fill="#0f172a">{xml_escape(title)}</text>')

    # 箭头定义（放前面避免引用在前定义在后）
    svg_parts.append(
        '<defs><marker id="arrowhead" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto">'
        '<polygon points="0 0, 10 3.5, 0 7" fill="#475569"/></marker></defs>'
    )

    # 绘制连线
    for e in edges:
        src_id = e.get("from", "")
        tgt_id = e.get("to", "")
        src = next((n for n in nodes if n["id"] == src_id), None)
        tgt = next((n for n in nodes if n["id"] == tgt_id), None)
        if not src or not tgt:
            continue

        sx = src.get("x", 0) + src.get("width", DEFAULT_NODE_W)
        sy = src.get("y", 0) + src.get("height", DEFAULT_NODE_H) / 2
        tx = tgt.get("x", 0)
        ty = tgt.get("y", 0) + tgt.get("height", DEFAULT_NODE_H) / 2

        # 箭头线（加粗到 2px）
        svg_parts.append(
            f'<line x1="{sx}" y1="{sy}" x2="{tx}" y2="{ty}" '
            f'stroke="#64748b" stroke-width="2" marker-end="url(#arrowhead)"/>'
        )

        # 连线标签（字号 12）
        label = e.get("label", "")
        if label:
            mx = (sx + tx) / 2
            my = (sy + ty) / 2 - 10
            # 根据文字长度动态调整标签背景宽度
            lbl_w = max(len(label) * 8 + 10, 36)
            svg_parts.append(
                f'<rect x="{mx - lbl_w/2}" y="{my-8}" width="{lbl_w}" height="18" fill="white" rx="4" '
                f'stroke="#cbd5e1" stroke-width="0.5"/>'
                f'<text x="{mx}" y="{my+5}" text-anchor="middle" font-size="12" fill="#475569">'
                f'{xml_escape(label)}</text>'
            )

    # 绘制节点
    for n in nodes:
        x = n.get("x", 0)
        y = n.get("y", 0)
        w = n.get("width", DEFAULT_NODE_W)
        h = n.get("height", DEFAULT_NODE_H)
        label = n.get("label", "")
        color_key = n.get("color", "lightblue")
        c = COLORS.get(color_key, COLORS["lightblue"])

        if chart_type == "uml":
            # === UML 类图：三分栏渲染 ===
            stereotype = n.get("stereotype", "")
            attrs = n.get("attributes", [])
            methods = n.get("methods", [])

            # 计算各栏高度
            title_h = 28
            attr_h = len(attrs) * 18 + 4
            method_h = len(methods) * 18 + 4

            # 背景矩形
            svg_parts.append(
                f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" ry="6" '
                f'fill="{c["fill"]}" stroke="{c["stroke"]}" stroke-width="2"/>'
            )

            # 类名栏背景
            svg_parts.append(
                f'<rect x="{x+1}" y="{y+1}" width="{w-2}" height="{title_h}" rx="5" ry="5" '
                f'fill="{c["stroke"]}" opacity="0.15"/>'
            )

            # 原型（<<interface>> 等）
            if stereotype:
                svg_parts.append(
                    f'<text x="{x + w/2}" y="{y + 12}" text-anchor="middle" font-size="9" '
                    f'font-style="italic" fill="{c["font"]}">{xml_escape(stereotype)}</text>'
                )
                title_text_y = y + 24
            else:
                title_text_y = y + 19

            # 类名
            svg_parts.append(
                f'<text x="{x + w/2}" y="{title_text_y}" text-anchor="middle" font-size="12" '
                f'font-weight="bold" fill="{c["font"]}">{xml_escape(label)}</text>'
            )

            # 分隔线 1
            sep_y1 = y + title_h + 1
            svg_parts.append(f'<line x1="{x+2}" y1="{sep_y1}" x2="{x+w-2}" y2="{sep_y1}" '
                             f'stroke="{c["stroke"]}" stroke-width="1" stroke-dasharray="2,2"/>')

            # 属性栏
            for ai, attr in enumerate(attrs):
                svg_parts.append(
                    f'<text x="{x + 6}" y="{sep_y1 + 14 + ai * 18}" font-size="10" '
                    f'fill="{c["font"]}">{xml_escape(attr)}</text>'
                )

            # 分隔线 2
            sep_y2 = sep_y1 + attr_h + 1
            svg_parts.append(f'<line x1="{x+2}" y1="{sep_y2}" x2="{x+w-2}" y2="{sep_y2}" '
                             f'stroke="{c["stroke"]}" stroke-width="1" stroke-dasharray="2,2"/>')

            # 方法栏
            for mi, method in enumerate(methods):
                svg_parts.append(
                    f'<text x="{x + 6}" y="{sep_y2 + 14 + mi * 18}" font-size="10" '
                    f'fill="{c["font"]}">{xml_escape(method)}</text>'
                )
        else:
            shape = n.get("shape", DEFAULT_SHAPE)
            rx = 8 if shape in ("rounded", "process") else 0
            rx = 30 if shape in ("start", "end") else rx
            rx = 4 if shape == "rect" else rx

            svg_parts.append(
                f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" ry="{rx}" '
                f'fill="{c["fill"]}" stroke="{c["stroke"]}" stroke-width="2"/>'
            )

            # 多行文本处理（用 \n 分隔）
            lines = label.split("\n")
            line_count = len(lines)
            line_h = 18
            start_y = y + (h - line_count * line_h) / 2 + 14

            for li, line in enumerate(lines):
                svg_parts.append(
                    f'<text x="{x + w/2}" y="{start_y + li * line_h}" text-anchor="middle" font-size="13" '
                    f'font-weight="600" fill="{c["font"]}">{xml_escape(line)}</text>'
                )

    svg_parts.append('</svg>')
    return "\n".join(svg_parts)


def main():
    args = parse_args()
    data = load_input(args.input)
    nodes = data.get("nodes", [])
    edges = data.get("edges", [])

    # 自动布局
    nodes, edges = auto_layout(data)
    data["nodes"] = nodes
    data["edges"] = edges

    # 生成 .drawio XML
    drawio_xml = build_drawio_xml(nodes, edges, data)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(drawio_xml)
    print(f"✅ .drawio 已生成: {args.output}")

    # 生成 SVG 预览
    if args.preview:
        svg = build_svg_preview(nodes, edges, data)
        with open(args.preview, "w", encoding="utf-8") as f:
            f.write(svg)
        print(f"✅ SVG 预览已生成: {args.preview}")

    # 输出统计
    print(f"   节点: {len(nodes)} | 连线: {len(edges)}")

    # 生成 PNG 高清图
    if args.png:
        if args.preview:
            try:
                import cairosvg
                cairosvg.svg2png(url=args.preview, write_to=args.png, scale=2)
                print(f"✅ PNG 高清图已生成: {args.png} (scale=2)")
            except ImportError:
                print("⚠️ 未安装 cairosvg，跳过 PNG 生成。请执行: pip3 install cairosvg")
            except Exception as e:
                print(f"⚠️ PNG 生成失败: {e}")


if __name__ == "__main__":
    main()
