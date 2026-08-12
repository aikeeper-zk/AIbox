#!/usr/bin/env bash
# validate.sh - 渲染并验证 Mermaid .mmd，失败则输出错误供模型修正
# 这是「Error Recovery Loop（渲染验证循环）」的一环：脚本只负责渲染与报错，
# 模型看到错误后修正 .mmd 再次调用本脚本，最多 3 轮。
# 用法: bash scripts/validate.sh input.mmd [output.png]
set -uo pipefail

INPUT="${1:-}"
OUTPUT="${2:-${INPUT%.mmd}.png}"

if [ -z "$INPUT" ] || [ ! -f "$INPUT" ]; then
  echo "❌ 用法: bash scripts/validate.sh input.mmd [output.png]" >&2
  exit 2
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if "$SCRIPT_DIR/render.sh" -i "$INPUT" -o "$OUTPUT"; then
  echo "✅ 渲染成功: $OUTPUT （可交付）" >&2
  exit 0
else
  echo "" >&2
  echo "❌ 渲染失败。请将上方 mmdc 的完整错误信息复制，返给模型要求修正 $INPUT 后重试。" >&2
  echo "   修正要点参考 references/pitfalls.md（中文标签引号、行尾禁分号、节点ID用英文等）。" >&2
  exit 1
fi
