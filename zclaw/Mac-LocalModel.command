#!/bin/bash
# ============================================================
# Z-Claw - 内网/本地模型一键配置 (macOS)
# 双击运行：命令行配 Ollama / newapi 并当场实测（不碰网页设置）
# ============================================================

zclaw_DIR="$(cd "$(dirname "$0")" && pwd)"
APP_DIR="$zclaw_DIR/app"
CONFIG_FILE="$zclaw_DIR/data/.openclaw/openclaw.json"

ARCH=$(uname -m)
case "$ARCH" in
    arm64)  NODE_BIN="$APP_DIR/runtime/node-mac-arm64/bin/node" ;;
    x86_64) NODE_BIN="$APP_DIR/runtime/node-mac-x64/bin/node" ;;
    *)      NODE_BIN="" ;;
esac
if [ ! -x "$NODE_BIN" ]; then NODE_BIN="$(command -v node)"; fi
if [ -z "$NODE_BIN" ] || [ ! -x "$NODE_BIN" ]; then
    echo "  [错误] 找不到 Node 运行环境。请先正常启动一次 Z-Claw。"
    read -p "  按回车关闭..."
    exit 1
fi

xattr -rd com.apple.quarantine "$zclaw_DIR" 2>/dev/null || true

"$NODE_BIN" "$zclaw_DIR/lib/setup-local-model.mjs" "$CONFIG_FILE"

echo ""
read -p "  按回车关闭..."
