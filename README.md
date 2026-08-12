# 智体共合 · AIbox

> 你的 AI，由你掌控。

智体共合（智体共合科技有限公司）官方开源仓库，包含 **官网网站** 与 **Z-Claw 便携式 AI 智能体** 两大核心项目。

- 🌐 官网：[www.594agent.com](https://www.594agent.com)
- 📧 商务邮箱：[shangwu@594agent.com](mailto:shangwu@594agent.com)

---

## 目录结构

```
AIbox/
├── zhiti/          # 智体共合官网（纯静态 HTML 网站）
├── zclaw/          # Z-Claw 便携式 AI 智能体（核心产品）
├── gongzhonghao.jpg # 微信公众号二维码
└── README.md       # 本文件
```

---

## 🏠 zhiti/ — 智体共合官网

纯静态企业官网，无任何构建依赖，浏览器直接打开即可访问。

### 页面列表

| 文件 | 页面 | 说明 |
|------|------|------|
| `index.html` | 首页 | 产品总览、Agent 俱乐部入口 |
| `about.html` | 关于我们 | 公司介绍 |
| `ai-box.html` | AI 智能盒 | 小龙虾 AI 智能盒产品页 |
| `openclaw.html` | OpenClaw | 开源智能体引擎 |
| `udisk.html` | U 盘版 | Z-Claw U 盘便携版 |
| `hdd.html` | 硬盘版 | Z-Claw 硬盘版 |
| `computing-network.html` | 算力网络 | 去中心化算力网络 |
| `federation.html` | 智体联邦 | 智能体协作网络 |
| `lingxia-platform.html` | 灵虾平台 | 云侧协作平台 |
| `digital-human.html` | 数字人 | 智体数字人内容生产 |
| `business.html` | 商务合作 | 合作方式 |
| `contact.html` | 联系我们 | 联系方式与公众号 |

### 本地预览

直接用浏览器打开 `zhiti/index.html`，或启动任意静态服务器：

```bash
# Python
python -m http.server 8000 -d zhiti

# Node
npx serve zhiti
```

访问 `http://localhost:8000` 即可。

---

## 🦞 zclaw/ — Z-Claw 便携式 AI 智能体

**Z-Claw Portable AI Agent**：基于 OpenClaw 引擎的便携式 AI 智能体，无需安装、即插即用，支持 Windows / macOS 双平台。

### 快速开始

| 平台 | 操作 |
|------|------|
| Windows | 双击 `Windows-Start.bat` |
| macOS | 双击 `Mac-Start.command` |

启动后自动打开：
- **聊天界面**（Dashboard）：`http://127.0.0.1:<18789-18799>`
- **配置中心**：`http://127.0.0.1:18788/`

### 目录说明

```
zclaw/
├── Windows-Start.bat / Mac-Start.command  # 一键启动
├── Windows-Menu.bat / Mac-Menu.command    # 功能菜单（配置/诊断/备份等）
├── setup.bat / setup.ps1 / setup.sh       # 环境搭建脚本
├── Windows-Diagnose.bat                   # 诊断修复工具
├── Config.html / Welcome.html             # 配置中心 / 欢迎页
├── default-config.json                    # 默认配置
├── config-server/                         # 配置中心服务（端口 18788）
├── lib/                                   # 辅助库（缓存加速、更新检查等）
├── skills-cn/                             # 国内优化技能包
├── app/                                   # 应用核心（首次安装自动生成，不入库）
└── data/                                  # 数据目录（首次启动自动生成，不入库）
```

> 详细说明见 [`zclaw/Z-Claw-启动手册.md`](zclaw/Z-Claw-启动手册.md)，零基础用户见 [`zclaw/Z-Claw-小白启动手册.md`](zclaw/Z-Claw-小白启动手册.md)。

### 核心特性

- ✅ **免安装**：自带 Node.js 运行时
- ✅ **即插即用**：U 盘 / 移动硬盘随身携带
- ✅ **本地优先**：数据存本机 `data/`，拔盘不留痕
- ✅ **多平台**：Windows x64、macOS（Apple Silicon / Intel）
- ✅ **开箱即用**：内置 QQ 机器人插件 + 国内技能包
- ✅ **缓存加速**：自动迁移缓存到本机硬盘，U 盘运行不卡顿

---

## 产品矩阵

| 产品 | 简介 | 位置 |
|------|------|------|
| 小龙虾 AI 智能盒 | 边缘 AI 硬件 | `zhiti/ai-box.html` |
| Z-Claw 便携智能体 | 免安装 AI 智能体 | `zclaw/` |
| 灵虾平台 | 云侧协作平台 | `zhiti/lingxia-platform.html` |
| 智体联邦 | 去中心化智能体协作网络 | `zhiti/federation.html` |
| 算力网络 | 去中心化算力基础设施 | `zhiti/computing-network.html` |
| 智体数字人 | 3D 写实数字人内容生产 | `zhiti/digital-human.html` |

---

## 贡献指南

1. Fork 本仓库
2. 新建功能分支：`git checkout -b feat/xxx`
3. 提交变更：`git commit -m "feat: xxx"`
4. 推送分支：`git push origin feat/xxx`
5. 发起 Pull Request

---

## 联系方式

- 🌐 官网：[www.594agent.com](https://www.594agent.com)
- 📧 商务邮箱：[shangwu@594agent.com](mailto:shangwu@594agent.com)
- 📱 微信公众号：见 `gongzhonghao.jpg`（或官网首页底部）

---

© 智体共合科技有限公司。保留所有权利。
