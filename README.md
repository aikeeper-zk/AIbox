# 智体共合 · AIbox

> 你的 AI，由你掌控。

智体共合（智体共合科技（无锡）有限公司）官方开源仓库，包含 **官网网站**、**智探 GEO 服务** 与 **Z-Claw 便携式 AI 智能体** 三大核心项目。

- 🌐 官网：[594agent.com](https://594agent.com)
- 🌐 智探 GEO：[594agent.com/GEO](https://594agent.com/GEO/)
- 📧 商务邮箱：[shangwu@594agent.com](mailto:shangwu@594agent.com)

---

## 目录结构

```
AIbox/
├── zhiti/          # 智体共合官网（纯静态 HTML 网站，部署到 /）
├── GEO/            # 智探 GEO 服务落地页（部署到 /GEO/）
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
| `index.html` | 首页 | 产品总览（含智探 GEO 入口）、Agent 俱乐部入口 |
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

## 🔍 GEO/ — 智探 GEO 服务

智探 GEO 是智体共合旗下的 **GEO（生成式引擎优化）全链路服务**：通过诊断 → 词包 → 内容 → 技术 → 监测五个环节，帮企业在豆包、DeepSeek、通义千问等 AI 回答中「被看见、被推荐」。坚持三不承诺（不承诺 AI 排名 / 收录 / 固定线索量），以透明数据报告呈现进展。

纯静态站点，部署到 `https://594agent.com/GEO/`。

### 文件说明

| 文件 | 说明 |
|------|------|
| `index.html` | 服务落地页：五环节、价目、三不承诺、FAQ、开源白皮书展示 |
| `process.html` | **交互式全流程演示页**：进入视口自动播放五步动画，一眼看懂 GEO 如何起效 |
| `llms.txt` | 面向 AI 检索的结构化站点说明 |
| `sitemap.xml` / `robots.txt` | 站点索引（含 AI 爬虫许可声明） |
| `assets/` | LOGO、封面图、介绍文档 PDF、开源白皮书 PDF |

### 开源白皮书

`GEO/assets/为品牌取证_智探GEO2026白皮书_v2.1_正式版.pdf`（59 页，v2.1 正式版）

《为品牌取证：智探 GEO 2026 生成式引擎优化白皮书》——以效度理论审查 GEO 的证据基础，形式化生成式引擎可见性机制，提出「上下文席位」与「证据保真度」两个测量构造。可在落地页下载，或在 `index.html#whitepaper` 查看介绍。

### 本地预览

从**项目根目录**启动静态服务器（目录名 `GEO` 与线上路径一致，可真实还原线上 URL）：

```bash
python -m http.server 8000
# 访问 http://localhost:8000/GEO/ 与 http://localhost:8000/GEO/process.html
```

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
| 智探 GEO | GEO 生成式引擎优化全链路服务 | `GEO/index.html`、`GEO/process.html` |

---

## 贡献指南

1. Fork 本仓库
2. 新建功能分支：`git checkout -b feat/xxx`
3. 提交变更：`git commit -m "feat: xxx"`
4. 推送分支：`git push origin feat/xxx`
5. 发起 Pull Request

---

## 联系方式

- 🌐 官网：[594agent.com](https://594agent.com)
- 🌐 智探 GEO：[594agent.com/GEO](https://594agent.com/GEO/)
- 📧 商务邮箱：[shangwu@594agent.com](mailto:shangwu@594agent.com)
- 📱 微信公众号：见 `gongzhonghao.jpg`（或官网首页底部）

---

© 智体共合科技（无锡）有限公司。保留所有权利。
