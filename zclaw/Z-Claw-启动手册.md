# 🦞 Z-Claw V1.0 启动手册

> **Z-Claw Portable AI Agent** — 便携式 AI 智能体
> 基于 OpenClaw 引擎（版本：2026.7.1-2），支持 Windows / macOS 双平台即插即用。
>
> 📖 本手册由 **智体共合技术部** 编制
> 🌐 官网：[www.594agent.com](https://www.594agent.com)

---

## 目录

1. [产品简介](#1-产品简介)
2. [目录结构说明](#2-目录结构说明)
3. [系统要求](#3-系统要求)
4. [首次安装（环境搭建）](#4-首次安装环境搭建)
5. [启动方式](#5-启动方式)
6. [启动流程详解](#6-启动流程详解)
7. [首次使用配置](#7-首次使用配置)
8. [常用功能菜单](#8-常用功能菜单)
9. [常见问题排查](#9-常见问题排查)
10. [运维与维护](#10-运维与维护)

---

## 1. 产品简介

Z-Claw 是一款**便携式 AI 智能体**，将完整的 OpenClaw 运行环境封装在单个文件夹内，无需安装、免配置即可在任意电脑上运行：

- ✅ **免安装**：自带 Node.js 运行时，无需预装任何环境
- ✅ **即插即用**：支持 U 盘 / 移动硬盘携带，换电脑直接启动
- ✅ **本地优先**：所有数据存储在本机 `data/` 目录，拔盘不留痕
- ✅ **多平台**：Windows x64、macOS（Apple Silicon / Intel）
- ✅ **开箱即用**：内置 QQ 机器人插件 + 国内优化技能包（skills-cn）
- ✅ **缓存加速**：自动将浏览器缓存 / V8 编译缓存迁移到本机硬盘，U 盘运行不卡顿

---

## 2. 目录结构说明

```
zclaw/
├── Windows-Start.bat        # ⭐ Windows 一键启动
├── Mac-Start.command        # ⭐ macOS 一键启动
├── Windows-Menu.bat         # Windows 功能菜单
├── Mac-Menu.command         # macOS 功能菜单
├── Windows-Install.bat      # Windows 安装（环境搭建）
├── Mac-Install.command      # macOS 安装（环境搭建）
├── setup.bat / setup.ps1    # Windows 环境搭建脚本（bat 版 / PowerShell 版）
├── setup.sh                 # macOS 环境搭建脚本
├── Windows-Diagnose.bat     # Windows 诊断工具
├── Mac-Diagnose.command     # macOS 诊断工具
├── OpenClaw-CLI.bat         # OpenClaw 命令行入口
├── OpenClaw-Doctor.bat      # 自动修复工具
├── Windows-IntranetFix.bat  # 内网/自建模型直连修复
├── Windows-LocalModel.bat   # 本地模型配置
├── Config.html              # 网页配置中心入口
├── Welcome.html             # 欢迎页
├── SkillHub.html            # 技能市场页
├── Z-Claw.html              # 产品主页
├── default-config.json      # 默认配置文件
├── OPENCLAW_VERSION         # 版本号文件
├── app/                     # 应用核心（首次安装后生成）
│   ├── core/                #   OpenClaw 引擎 + npm 依赖
│   └── runtime/             #   Node.js 运行时（win-x64 / mac-arm64 / mac-x64）
├── config-server/           # 配置中心服务（端口 18788）
├── lib/                     # 辅助库（启动页、缓存加速、更新检查等）
├── skills-cn/               # 国内优化技能包
└── data/                    # 数据目录（首次启动自动生成）
    ├── .openclaw/
    │   └── openclaw.json    #   ⭐ 核心配置文件（模型、渠道、密钥）
    ├── memory/              # 记忆数据
    ├── backups/             # 备份数据
    └── logs/                # 运行日志
```

> **提示**：`app/` 和 `data/` 在首次安装 / 启动时自动生成，无需手动创建。

---

## 3. 系统要求

| 项目 | 要求 |
|------|------|
| 操作系统 | Windows 10/11 (x64) 或 macOS 12+（Apple Silicon / Intel） |
| 磁盘空间 | 至少 2 GB（安装后约 1.5 GB） |
| 文件系统 | **NTFS（推荐）**；exFAT/FAT32 运行会非常慢 |
| 网络 | 安装时需要联网；运行时建议联网（调用 AI 模型） |
| 其他 | 无特殊要求，无需管理员权限 |

---

## 4. 首次安装（环境搭建）

> 官方发布包（`Z-Claw-portable-*.zip`）已内置全部依赖，**解压后可直接启动，无需安装**。
> 以下步骤仅适用于从源码构建或依赖缺失的情况。

### Windows

**方式一：双击 `setup.bat`**

自动完成：
1. 下载 Node.js v24.18.0 (win-x64) 到 `app/runtime/`
2. 安装 OpenClaw（版本取自 `OPENCLAW_VERSION` 文件）到 `app/core/`
3. 安装 QQ 机器人插件（`@sliverp/qqbot`）
4. 复制国内优化技能包（skills-cn）

**方式二：PowerShell**

```powershell
# 仅当前平台
.\setup.ps1

# 准备跨平台 U 盘（额外下载 Mac 运行时）
.\setup.ps1 -AllPlatforms
```

**方式三：命令行 bat**

```cmd
setup.bat --all-platforms
```

### macOS

```bash
chmod +x setup.sh
bash setup.sh
# 跨平台 U 盘：
bash setup.sh --all-platforms
```

> **注意**：macOS 首次运行可能提示"无法验证开发者"，请在 **系统设置 → 隐私与安全性** 中点击"仍要打开"，或执行 `xattr -rd com.apple.quarantine <目录>` 解除隔离。

---

## 5. 启动方式

### ⭐ Windows 一键启动（推荐）

**双击 `Windows-Start.bat`**，脚本会自动：

1. 检测并加载内置 Node.js 运行时
2. 初始化数据目录（`data/`）
3. 迁移缓存到本机硬盘（加速）
4. 首次运行自动生成默认配置
5. 启动配置中心（端口 18788）
6. 查找空闲网关端口（18789–18799）
7. 打开**启动页面** + **配置中心**
8. 启动 OpenClaw 网关

**启动后会自动打开两个页面：**

| 页面 | 地址 | 用途 |
|------|------|------|
| 启动页 | `file://.../loading.html` | 显示启动进度，就绪后进入选择页 |
| 配置中心 | `http://127.0.0.1:18788/` | 配置模型、充值/获取 Key、连接渠道 |

### ⭐ macOS 一键启动

**双击 `Mac-Start.command`**（首次需在终端执行 `chmod +x Mac-Start.command`），脚本会自动：

1. 检测 CPU 架构（Apple Silicon → arm64，Intel → x64）
2. 自动移除 macOS 安全隔离属性
3. 初始化数据目录、生成默认配置
4. 启动配置中心 + OpenClaw 网关
5. 打开 Dashboard 和配置中心

**运行后访问：**

| 页面 | 地址 |
|------|------|
| Dashboard（聊天界面） | `http://127.0.0.1:<端口>/#token=zclaw` |
| 配置中心 | `http://127.0.0.1:18788/` |

> 网关端口默认为 18789，若被占用会自动递增至 18799，可在启动日志中查看实际端口。

### 停止运行

- **Windows**：关闭 `Windows-Start.bat` 窗口即可
- **macOS**：在终端按 `Ctrl + C`，或在启动窗口关闭

> ⚠️ **重要**：Z-Claw 运行期间请勿关闭启动窗口，否则服务会停止。

---

## 6. 启动流程详解

### 6.1 Windows 启动流程（Windows-Start.bat）

```
┌─────────────────────────────────────────────────┐
│ 1. 检查 Node.js 运行时（app\runtime\node-win-x64）│
│ 2. 初始化数据目录（data\ 及子目录）                │
│ 3. 缓存加速：lib\portable-cache.mjs               │
│    → 浏览器缓存/V8 编译缓存迁移到本机硬盘          │
│ 4. 配置初始化：                                   │
│    → 已有配置：跳过                                │
│    → 旧版 config.json：自动迁移                    │
│    → 全新安装：生成默认配置（token=zclaw）         │
│ 5. 依赖检查：node_modules 缺失时自动 npm install   │
│    （使用国内镜像 registry.npmmirror.com）         │
│ 6. 内网代理修复：lib\resolve-no-proxy.mjs          │
│    → 自动将内网模型地址加入 NO_PROXY               │
│ 7. 异步检查更新（不阻塞启动）                      │
│ 8. 自动安装微信插件（如附带）                      │
│ 9. 启动配置中心（127.0.0.1:18788）                 │
│ 10. 查找空闲网关端口（18789→18799）               │
│ 11. 打开启动页 + 配置中心                          │
│ 12. 启动 OpenClaw Gateway（--allow-unconfigured） │
└─────────────────────────────────────────────────┘
```

### 6.2 macOS 启动流程（Mac-Start.command）

与 Windows 类似，额外包含：
- **架构检测**：自动选择 `node-mac-arm64` 或 `node-mac-x64`
- **隔离解除**：自动执行 `xattr -rd com.apple.quarantine`
- **优雅退出**：按 `Ctrl + C` 自动清理后台进程

### 6.3 端口说明

| 端口 | 服务 | 说明 |
|------|------|------|
| 18788 | 配置中心 | Config Server，固定端口 |
| 18789–18799 | OpenClaw 网关 | Dashboard / API，自动递增查找空闲端口 |

---

## 7. 首次使用配置

启动后，在**配置中心**（`http://127.0.0.1:18788/`）完成以下配置：

### 7.1 配置 AI 模型

支持主流国内模型：

| 模型 | Provider | API 地址 |
|------|----------|----------|
| DeepSeek | Custom Provider | `https://api.deepseek.com/v1` |
| Kimi | Moonshot AI | 平台提供 |
| Qwen 通义千问 | Qwen | 平台提供 |
| 豆包 Doubao | Volcano Engine | 平台提供 |

配置步骤：
1. 打开配置中心 → 模型设置
2. 选择模型提供商，填入 **API Key**
3. 保存后重启网关生效

> 也可在功能菜单中选 **`[1] Setup wizard`** 按向导配置。

### 7.2 连接聊天渠道

| 渠道 | 说明 | 准备材料 |
|------|------|----------|
| QQ 机器人 | 预装插件，只需 AppID + AppSecret | 前往 [q.qq.com](https://q.qq.com) 创建机器人 |
| 微信 | iPad 协议插件 | 菜单 [4c] 自动安装 |
| 飞书 | 企业场景 | [open.feishu.cn](https://open.feishu.cn) 创建应用 |
| Telegram | 国际 | 联系 @BotFather 获取 Token |
| Discord | 游戏社区 | [discord.com/developers](https://discord.com/developers) |

### 7.3 内网/自建模型（可选）

如使用内网模型（`http://10.x` / `192.168.x` 等地址）：
- 双击 **`Windows-IntranetFix.bat`** 或 **`Mac-IntranetFix.command`**
- 脚本会自动将内网地址加入 `NO_PROXY`，绕过公司代理直连

---

## 8. 常用功能菜单

双击 **`Windows-Menu.bat`**（Mac 为 `Mac-Menu.command`）打开功能菜单：

| 编号 | 功能 | 说明 |
|------|------|------|
| 1 | Setup wizard | 配置向导（模型、API Key） |
| 2 | Open web dashboard | 启动网关并打开聊天界面 |
| 3 | QQ Bot | 配置 QQ 机器人（AppID + AppSecret） |
| 4 | Other platforms | 飞书 / Telegram / 微信 / Discord |
| 5 | Diagnostics | 运行诊断并自动修复 |
| 6 | Backup config | 备份配置 + 记忆数据 |
| 7 | Restore backup | 从备份恢复 |
| 8 | System info | 查看系统 / 版本 / 占用信息 |
| 9 | Kill residual processes | 清理残留进程（端口被占用时使用） |
| 10 | View logs | 查看 / 导出 / 清理日志 |
| 11 | Factory reset | 恢复出厂设置（删除全部配置与记忆） |
| 12 | Uninstall | 卸载 |
| 13 | Check for updates | 检查 OpenClaw 更新 |
| 14 | Disk cleanup | 磁盘清理（旧备份、旧日志、npm 缓存） |
| 15 | Plugin management | 插件管理（列表 / 安装 / 移除） |
| 0 | Exit | 退出菜单 |

---

## 9. 常见问题排查

### Q1：双击启动后没反应 / 闪退

1. 双击 **`Windows-Diagnose.bat`** 运行诊断，查看 `diagnostic-log.txt`
2. 检查 `app\runtime\node-win-x64\node.exe` 是否存在
3. 检查 `app\core\node_modules` 是否存在（缺失则重新运行 `setup.bat`）

### Q2：首次启动等待时间较长

- USB 盘首次启动需要 **30–90 秒** 解包依赖，属正常现象
- 第二次启动会因缓存加速显著变快
- 建议使用 **NTFS** 文件系统；exFAT/FAT32 会非常慢

### Q3：端口 18789 被占用

脚本会自动尝试 18790–18799，直到找到空闲端口。若全部占用：
- 菜单 → **`[9] Kill residual processes`** 清理残留进程
- 或手动释放相关端口

### Q4：配置中心打不开（127.0.0.1:18788）

1. 确认 `Windows-Start.bat` 窗口仍在运行
2. 检查防火墙是否拦截本机端口
3. 菜单 → `[10] View logs` 查看网关日志

### Q5：调用模型报错 / 连不上

1. 确认配置中心中已正确填写 API Key 和模型地址
2. 内网模型请先运行 **IntranetFix** 脚本
3. 检查公司网络代理是否影响访问

### Q6：macOS 提示"无法验证开发者"

```bash
# 在终端中解除隔离后重新启动
xattr -rd com.apple.quarantine ~/Desktop/Z-Claw
```

### Q7：诊断工具显示"node_modules 缺失"

说明依赖不完整：
1. 重新运行 `setup.bat` / `setup.ps1` 安装依赖
2. 或从 GitHub Releases 重新下载完整版 `Z-Claw-portable-*.zip`（已预装依赖，约 200 MB）

---

## 10. 运维与维护

### 数据备份

- 所有数据位于 `data/` 目录
- 建议定期使用菜单 **`[6] Backup config`** 备份（含配置 + 记忆）
- 备份保存于 `data/backups/`，可用 **`[7] Restore backup`** 恢复

### 更新升级

- 菜单 **`[13] Check for updates`** 检查并更新 OpenClaw
- 启动时会**异步自动检查**新版本，若有更新会在欢迎页 / 配置中心显示横幅

### 磁盘清理

- 菜单 **`[14] Disk cleanup`**：
  - 清理 7 天前的旧日志
  - 清理多余备份（保留最近 3 份）
  - 清理 npm 缓存

### 恢复出厂

- 菜单 **`[11] Factory reset`**（输入 `RESET` 确认）
- 操作前会自动备份当前配置和记忆到 `data/backups/pre-reset_*`

### 卸载

- **便携版**：直接删除整个 Z-Claw 文件夹即可（数据在 `data/` 内，如需保留请先备份）
- **安装版**：系统设置 → 应用 → 找到 Z-Claw → 卸载

---

## 附：关键信息速查

| 项目 | 值 |
|------|-----|
| 产品版本 | Z-Claw V1.0 |
| OpenClaw 版本 | 2026.7.1-2 |
| Node.js 版本 | v24.18.0（Windows / Mac） |
| 配置中心端口 | 18788 |
| 网关端口范围 | 18789–18799 |
| 默认访问 Token | `zclaw` |
| 配置文件 | `data/.openclaw/openclaw.json` |
| 日志目录 | `data/logs/` |
| 备份目录 | `data/backups/` |
| npm 镜像 | `https://registry.npmmirror.com` |
| Node 镜像 | `https://npmmirror.com/mirrors/node` |

---

## 关于智体共合

**智体共合**（智体共合科技有限公司）是一家专注于 AI 智能体与分布式智能协作网络的高科技企业，致力于让每个个人与企业都能轻松拥有专属 AI 智能体。

- 🌐 官网：[www.594agent.com](https://www.594agent.com)
- 📧 商务邮箱：[shangwu@594agent.com](mailto:shangwu@594agent.com)
- 🦞 Z-Claw 由 **智体共合技术部** 研发与维护
- 💡 更多产品：小龙虾 AI 智能盒、灵虾平台、智体联邦等，详见官网
