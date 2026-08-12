#!/usr/bin/env python3
"""
drawio-pro 端到端完整性测试脚本
测试场景覆盖决策表 #1 流程图 / #3 架构图 / #8 时序交互
"""
import json
import os
import subprocess
import sys
import traceback
from xml.etree import ElementTree as ET

WORKSPACE = "/sandbox/workspace"
OUTPUT_DIR = f"{WORKSPACE}/output"
SCRIPT = f"{WORKSPACE}/drawio-pro/scripts/build_drawio.py"

results = {
    "passed": 0,
    "failed": 0,
    "skipped": 0,
    "details": []
}

def report(test_name, status, detail=""):
    r = {"name": test_name, "status": status, "detail": detail}
    results["details"].append(r)
    if status == "PASS":
        results["passed"] += 1
        print(f"  ✅ PASS: {test_name}")
    elif status == "FAIL":
        results["failed"] += 1
        print(f"  ❌ FAIL: {test_name} — {detail}")
    else:
        results["skipped"] += 1
        print(f"  ⏭️  SKIP: {test_name} — {detail}")

def check_file(path, min_bytes=100):
    if not os.path.exists(path):
        return False, f"文件不存在: {path}"
    size = os.path.getsize(path)
    if size < min_bytes:
        return False, f"文件过小: {size} bytes (需 ≥{min_bytes})"
    return True, f"{size} bytes"

def check_drawio_xml(path):
    try:
        tree = ET.parse(path)
        root = tree.getroot()
        # 检查关键元素
        if root.tag != "mxfile":
            return False, f"根标签不是 mxfile，而是 {root.tag}"
        diag = root.find("diagram")
        if diag is None:
            return False, "缺少 <diagram> 标签"
        model = diag.find("mxGraphModel")
        if model is None:
            return False, "缺少 <mxGraphModel> 标签"
        cells = model.findall(".//mxCell")
        cell_count = len(cells)
        return True, f"合法 XML，{cell_count} 个 mxCell"
    except ET.ParseError as e:
        return False, f"XML 解析失败: {e}"
    except Exception as e:
        return False, f"XML 检查异常: {e}"

def check_svg(path):
    try:
        with open(path, "r") as f:
            content = f.read()
        if "<svg" not in content:
            return False, "缺少 <svg> 标签"
        if "xmlns" not in content:
            return False, "缺少 xmlns 声明"
        if "</svg>" not in content:
            return False, "缺少 </svg> 闭合标签"
        return True, f"合法 SVG，{len(content)} bytes"
    except Exception as e:
        return False, f"SVG 检查异常: {e}"

def check_png(path):
    try:
        with open(path, "rb") as f:
            header = f.read(8)
        if header[:4] != b'\x89PNG':
            return False, f"文件头不是 PNG 格式: {header[:4].hex()}"
        size = os.path.getsize(path)
        return True, f"合法 PNG，{size} bytes"
    except Exception as e:
        return False, f"PNG 检查异常: {e}"

def run_test_scenario(name, logic_data, output_name):
    print(f"\n━━━ 测试场景: {name} ━━━")
    
    # 1. 写 logic.json
    logic_path = f"{OUTPUT_DIR}/test_{output_name}.json"
    drawio_path = f"{OUTPUT_DIR}/test_{output_name}.drawio"
    svg_path = f"{OUTPUT_DIR}/test_{output_name}.svg"
    png_path = f"{OUTPUT_DIR}/test_{output_name}.png"
    
    try:
        with open(logic_path, "w", encoding="utf-8") as f:
            json.dump(logic_data, f, ensure_ascii=False, indent=2)
        report(f"{name}·创建 logic.json", "PASS")
    except Exception as e:
        report(f"{name}·创建 logic.json", "FAIL", str(e))
        return

    # 2. 运行 build_drawio.py
    cmd = ["python3", SCRIPT, "-i", logic_path, "-o", drawio_path, "-p", svg_path, "--png", png_path]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            report(f"{name}·build_drawio.py 运行", "PASS")
        else:
            report(f"{name}·build_drawio.py 运行", "FAIL", f"exit={result.returncode}, stderr={result.stderr[:200]}")
            # 即使失败也继续检查产出物
    except subprocess.TimeoutExpired:
        report(f"{name}·build_drawio.py 运行", "FAIL", "超时 30s")
        return
    except Exception as e:
        report(f"{name}·build_drawio.py 运行", "FAIL", str(e))
        return

    # 3. 验证 .drawio
    ok, msg = check_file(drawio_path, 500)
    if ok:
        ok2, msg2 = check_drawio_xml(drawio_path)
        report(f"{name}·验证 .drawio", "PASS" if ok2 else "FAIL", msg2)
    else:
        report(f"{name}·验证 .drawio", "FAIL", msg)

    # 4. 验证 .svg
    ok, msg = check_file(svg_path, 500)
    if ok:
        ok2, msg2 = check_svg(svg_path)
        report(f"{name}·验证 .svg", "PASS" if ok2 else "FAIL", msg2)
    else:
        report(f"{name}·验证 .svg", "FAIL", msg)

    # 5. 验证 .png
    ok, msg = check_file(png_path, 5000)
    if ok:
        ok2, msg2 = check_png(png_path)
        report(f"{name}·验证 .png", "PASS" if ok2 else "FAIL", msg2)
    else:
        report(f"{name}·验证 .png", "FAIL", msg)

    # 6. 验证节点/连线数量
    try:
        with open(drawio_path, "r") as f:
            content = f.read()
        vertex_count = content.count('vertex="1"')
        edge_count = content.count('edge="1"')
        expected_nodes = len(logic_data.get("nodes", []))
        expected_edges = len(logic_data.get("edges", []))
        if vertex_count == expected_nodes:
            report(f"{name}·节点数匹配 ({vertex_count})", "PASS")
        else:
            report(f"{name}·节点数匹配", "FAIL", f"预期 {expected_nodes}，实际 {vertex_count}")
        if edge_count == expected_edges:
            report(f"{name}·连线数匹配 ({edge_count})", "PASS")
        else:
            report(f"{name}·连线数匹配", "FAIL", f"预期 {expected_edges}，实际 {edge_count}")
    except Exception as e:
        report(f"{name}·节点/连线检查", "FAIL", str(e))


def main():
    print("=" * 60)
    print("  drawio-pro 端到端完整性测试")
    print("=" * 60)
    
    # ====== 场景一：流程图（#1）======
    scenario1 = {
        "type": "flowchart",
        "title": "用户注册登录流程",
        "direction": "LR",
        "nodes": [
            {"id": "n1", "label": "访问页面", "color": "blue", "shape": "start", "layer": 0},
            {"id": "n2", "label": "填写信息", "color": "lightblue", "shape": "rounded", "layer": 1},
            {"id": "n3", "label": "验证信息", "color": "orange", "shape": "diamond", "layer": 1},
            {"id": "n4", "label": "注册成功", "color": "green", "shape": "rounded", "layer": 2},
            {"id": "n5", "label": "提示错误", "color": "red", "shape": "rounded", "layer": 2},
            {"id": "n6", "label": "进入首页", "color": "purple", "shape": "end", "layer": 3}
        ],
        "edges": [
            {"from": "n1", "to": "n2", "label": "点击注册"},
            {"from": "n2", "to": "n3", "label": "提交"},
            {"from": "n3", "to": "n5", "label": "不合法"},
            {"from": "n3", "to": "n4", "label": "合法"},
            {"from": "n5", "to": "n2", "label": "重新填写"},
            {"from": "n4", "to": "n6", "label": "自动跳转"}
        ]
    }
    run_test_scenario("① 流程图-用户注册登录", scenario1, "flow")

    # ====== 场景二：架构图（#3）======
    scenario2 = {
        "type": "architecture",
        "title": "小龙虾AI盒子·完整技术架构",
        "direction": "LR",
        "nodes": [
            {"id": "n1", "label": "工业质检", "color": "blue", "shape": "rounded", "layer": 0},
            {"id": "n2", "label": "小微零售", "color": "blue", "shape": "rounded", "layer": 0},
            {"id": "n3", "label": "智慧社区", "color": "blue", "shape": "rounded", "layer": 0},
            {"id": "n4", "label": "AI Agent引擎", "color": "lightblue", "shape": "rounded", "layer": 1},
            {"id": "n5", "label": "工作流编排引擎\n零代码可视化", "color": "lightblue", "shape": "rounded", "layer": 1, "width": 160, "height": 60},
            {"id": "n6", "label": "本地AI推理\nOllama+千问7B", "color": "green", "shape": "rounded", "layer": 2, "width": 160, "height": 60},
            {"id": "n7", "label": "智能调度器", "color": "orange", "shape": "diamond", "layer": 2},
            {"id": "n8", "label": "云端AI网关\nDeepSeek/Qwen", "color": "green", "shape": "rounded", "layer": 2, "width": 160, "height": 60},
            {"id": "n9", "label": "数据存储\n本地SSD+云端", "color": "gray", "shape": "cylinder", "layer": 2, "width": 160, "height": 60},
            {"id": "n10", "label": "OpenClaw框架", "color": "purple", "shape": "rect", "layer": 3, "width": 150},
            {"id": "n11", "label": "小龙虾AI系统\n定制Linux", "color": "purple", "shape": "rect", "layer": 3, "width": 150},
            {"id": "n12", "label": "Lite/Pro双版本\nRK3588/Jetson", "color": "gray", "shape": "rounded", "layer": 4, "width": 170, "height": 60}
        ],
        "edges": [
            {"from": "n1", "to": "n4", "label": ""},
            {"from": "n2", "to": "n4", "label": ""},
            {"from": "n3", "to": "n4", "label": ""},
            {"from": "n4", "to": "n5", "label": "编排"},
            {"from": "n5", "to": "n6", "label": "本地"},
            {"from": "n5", "to": "n7", "label": "调度"},
            {"from": "n5", "to": "n8", "label": "云端"},
            {"from": "n5", "to": "n9", "label": "存储"},
            {"from": "n7", "to": "n6", "label": ""},
            {"from": "n7", "to": "n8", "label": ""},
            {"from": "n6", "to": "n10", "label": ""},
            {"from": "n8", "to": "n10", "label": ""},
            {"from": "n9", "to": "n11", "label": ""},
            {"from": "n7", "to": "n10", "label": ""},
            {"from": "n10", "to": "n11", "label": ""},
            {"from": "n11", "to": "n12", "label": ""}
        ]
    }
    run_test_scenario("② 架构图-龙虾盒子完整架构", scenario2, "arch")

    # ====== 场景三：时序交互（#8）======
    scenario3 = {
        "type": "flowchart",
        "title": "用户下单时序交互",
        "direction": "LR",
        "nodes": [
            {"id": "n1", "label": "用户", "color": "blue", "shape": "start", "layer": 0},
            {"id": "n2", "label": "前端页面", "color": "lightblue", "shape": "rounded", "layer": 1},
            {"id": "n3", "label": "订单服务", "color": "green", "shape": "rounded", "layer": 2},
            {"id": "n4", "label": "支付系统", "color": "orange", "shape": "diamond", "layer": 2},
            {"id": "n5", "label": "仓储系统", "color": "gray", "shape": "cylinder", "layer": 3},
            {"id": "n6", "label": "下单完成", "color": "purple", "shape": "end", "layer": 4}
        ],
        "edges": [
            {"from": "n1", "to": "n2", "label": "提交订单"},
            {"from": "n2", "to": "n3", "label": "创建订单"},
            {"from": "n3", "to": "n4", "label": "发起支付"},
            {"from": "n4", "to": "n3", "label": "支付成功"},
            {"from": "n3", "to": "n5", "label": "发货通知"},
            {"from": "n5", "to": "n6", "label": "完成"}
        ]
    }
    run_test_scenario("③ 时序交互-用户下单流程", scenario3, "sequence")

    # ====== 汇总 ======
    total = results["passed"] + results["failed"] + results["skipped"]
    print("\n" + "=" * 60)
    print("  测试汇总")
    print("=" * 60)
    print(f"  总计: {total}  通过: {results['passed']}  失败: {results['failed']}  跳过: {results['skipped']}")
    
    if results["failed"] == 0:
        print("\n  🎉 全部通过！drawio-pro 端到端链路完整可用。")
    else:
        print(f"\n  ⚠️  {results['failed']} 项未通过，请检查上述 FAIL 项。")
    
    pass_rate = results["passed"] / max(total - results["skipped"], 1) * 100
    print(f"  通过率: {pass_rate:.0f}%")
    print("=" * 60)
    
    return 0 if results["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
