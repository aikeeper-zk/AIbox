#!/usr/bin/env bash
# render.sh - 将 Mermaid .mmd 渲染为图片（PNG/SVG/PDF）
# 用法: bash scripts/render.sh -i input.mmd -o output.png [-t theme] [-w width] [-H height] [-s scale]
# 依赖: @mermaid-js/mermaid-cli (mmdc) + puppeteer(Chromium)
set -euo pipefail

INPUT=""
OUTPUT=""
THEME="default"
WIDTH=""
HEIGHT=""
SCALE="2"

while [[ $# -gt 0 ]]; do
  case "$1" in
    -i) INPUT="$2"; shift 2;;
    -o) OUTPUT="$2"; shift 2;;
    -t) THEME="$2"; shift 2;;
    -w) WIDTH="$2"; shift 2;;
    -H) HEIGHT="$2"; shift 2;;
    -s) SCALE="$2"; shift 2;;
    *) echo "未知参数: $1" >&2; exit 1;;
  esac
done

if [ -z "$INPUT" ]; then
  echo "用法: bash scripts/render.sh -i input.mmd -o output.png [-t default|dark|forest|neutral]" >&2
  exit 1
fi
if [ ! -f "$INPUT" ]; then
  echo "输入文件不存在: $INPUT" >&2
  exit 1
fi

# 确保 mmdc 可用，缺失则自动安装（跳过 puppeteer 自动下载 Chromium，
# 因为我们用动态探测到的 Chrome；首次安装需联网）
if ! command -v mmdc >/dev/null 2>&1; then
  echo "[render.sh] 未检测到 mmdc，正在安装 @mermaid-js/mermaid-cli ..." >&2
  PUPPETEER_SKIP_DOWNLOAD=true npm install -g @mermaid-js/mermaid-cli
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
CONFIG="$ROOT_DIR/config.json"
PUPPETEER_TPL="$ROOT_DIR/puppeteer-config.json"

# —— 动态探测 Chrome，避免硬编码 executablePath ——
# 探测顺序：puppeteer 缓存(chrome) → chrome-headless-shell → 系统 chromium/chrome
# 多候选根目录兜底（$HOME 可能为空），取版本号最新者
detect_chrome() {
  local c base
  for base in "$HOME/.cache/puppeteer" "/root/.cache/puppeteer"; do
    [ -d "$base" ] || continue
    c=$(find "$base" -type f -name chrome 2>/dev/null | sort -V | tail -1)
    [ -n "$c" ] && { echo "$c"; return 0; }
  done
  for base in "$HOME/.cache/puppeteer" "/root/.cache/puppeteer"; do
    [ -d "$base" ] || continue
    c=$(find "$base" -type f -name "chrome-headless-shell" 2>/dev/null | sort -V | tail -1)
    [ -n "$c" ] && { echo "$c"; return 0; }
  done
  c=$(command -v chromium chromium-browser google-chrome google-chrome-stable 2>/dev/null | head -1)
  [ -n "$c" ] && { echo "$c"; return 0; }
  return 1
}
CHROME_BIN=$(detect_chrome)
if [ -z "$CHROME_BIN" ]; then
  echo "❌ 未找到 Chrome/Chromium，请先安装（见 SKILL.md 渲染后端章节）" >&2
  exit 1
fi

# 将模板配置与动态 executablePath 合并到临时文件，传给 mmdc
PUPPETEER_CONF=$(mktemp /tmp/mermaid-pro-pptr.XXXXXX.json)
python3 - "$PUPPETEER_TPL" "$CHROME_BIN" "$PUPPETEER_CONF" <<'PY'
import json, sys
tpl, chrome, out = sys.argv[1], sys.argv[2], sys.argv[3]
with open(tpl, encoding="utf-8") as f:
    cfg = json.load(f)
cfg["executablePath"] = chrome
with open(out, "w", encoding="utf-8") as f:
    json.dump(cfg, f, ensure_ascii=False)
PY

ARGS=(-i "$INPUT" -o "$OUTPUT" -t "$THEME" -s "$SCALE" -c "$CONFIG" -p "$PUPPETEER_CONF")
[ -n "$WIDTH" ]  && ARGS+=(-w "$WIDTH")
[ -n "$HEIGHT" ] && ARGS+=(-H "$HEIGHT")

echo "[render.sh] 渲染: $INPUT -> $OUTPUT (theme=$THEME)" >&2
echo "[render.sh] chrome: $CHROME_BIN" >&2
mmdc "${ARGS[@]}"
rm -f "$PUPPETEER_CONF"
echo "[render.sh] ✅ 渲染完成: $OUTPUT" >&2
