---
name: mermaid-pro
author: 随风话雪
description: 专业 Mermaid 绘图助手——用自然语言一键生成流程图、架构图、时序图、类图、ER图、思维导图、时间线、甘特图等 24+ 类图表。基于 Mermaid v11 文本即图语法，内置自动布局、中文避坑规则与「渲染验证循环」质量保障，输出可编辑 .mmd 源文件 + PNG/SVG 预览，并可无缝嵌入 Markdown/公众号/笔记。当用户需要画流程图、架构图、时序图、类图、ER图、思维导图、时间线、甘特图、状态机、用户旅程、C4架构图、象限图、桑基图、饼图，或说"画个XX图""生成XX图""把这段逻辑画成图""做个架构示意图"时触发。不适用于纯美术设计、位图编辑、需要像素级自由排版的复杂信息图（此类用 draw.io 副格式兜底）。
---

# Mermaid 专业绘图助手（mermaid-pro）

用「说人话」的方式产出专业图表：自然语言 → Mermaid 代码 → 渲染验证 → 可编辑源文件 + 预览图。

## 一、何时使用（触发词）
- 用户说：画个/做个/生成/画一张 **流程图、架构图、时序图、类图、ER图、思维导图、时间线、甘特图、状态机、用户旅程、C4架构图、象限图、桑基图、饼图**……
- 用户说：「把这个逻辑画成图」「把这段流程可视化」「帮我出一张 XX 示意图」
- 用户上传文本/笔记/文档，希望转成图表

## 一·五、决策路由表（意图 → 图类型 → 起点模板）

| 用户意图 | 首选图类型 | 起点模板 |
|---|---|---|
| 流程 / 步骤 / 审批链 | flowchart（TD 上↓下 / LR 左→右） | `templates/flowchart.mmd` |
| 多方交互 / 接口调用时序 | sequenceDiagram | `templates/sequence.mmd` |
| 系统 / 产品分层架构 | flowchart LR + subgraph | `templates/architecture.mmd` |
| 类 / 数据模型关系 | classDiagram | `templates/class.mmd` |
| 发散 / 归纳结构 | mindmap | `templates/mindmap.mmd` |
| 里程碑 / 演进时间线 | timeline | `templates/timeline.mmd` |
| 边缘AI部署（真实范例） | flowchart LR + subgraph | `templates/edge-ai-deployment.mmd` |
| 技术栈交互（真实范例） | sequenceDiagram | `templates/fed-tech-sequence.mmd` |
| Agent 数据模型（真实范例） | classDiagram | `templates/agent-data-model.mmd` |
| 产品演进（真实范例） | timeline | `templates/product-evolution.mmd` |

> 不确定图型时：架构/流程默认 `flowchart LR`，自上而下流程默认 `flowchart TD`。

## 二、核心能力
1. **24+ 图表类型**：流程、时序、类、ER、状态、架构(C4)、甘特、时间线、思维导图、旅程、象限、数据可视化等。
2. **自动布局**：Mermaid 内置 dagre 引擎自动排版，无需手动算坐标。
3. **中文友好**：内置中文字体配置与避坑规则，中文标签开箱可用。
4. **质量保障（渲染验证循环）**：生成即渲染，失败自动回灌修正，确保产出合法可渲染。
5. **可嵌入**：输出 ```mermaid 代码块，可直接进 Markdown/公众号/笔记。

## 三、工作流 SOP（严格按序执行）

### Step 1 · 澄清意图
确认：① 图类型（不确定就参考「决策路由表」让模型推荐）；② 核心内容与节点/参与者；③ 导出格式（默认 PNG，可选 SVG/PDF）；④ 是否要嵌入 Markdown/公众号。

### Step 2 · 选图类型 + 结构化
根据描述 + 决策路由表选定 Mermaid 类型，梳理出语义结构（节点/参与者/关系/层次/约束）。不确定时优先 `flowchart LR`（架构/流程）或 `flowchart TD`（自上而下流程）。

### Step 3 · 生成 Mermaid 代码
套用 `references/prompt-templates.md` 的 **Mermaid-First 模板**，并严格遵守 `references/pitfalls.md` 的中文避坑规则。仅输出 Mermaid 代码，无解释。

### Step 4 · 渲染验证循环（质量命门）
1. 将代码写入 `<name>.mmd`（`templates/` 下有各类起点模板可参考）。
2. 执行渲染脚本（自动安装依赖、中文字体已配）：
   ```bash
   bash scripts/render.sh -i <name>.mmd -o <name>.png -t default
   ```
3. **成功** → 进入 Step 5。
4. **失败** → 把终端报错原文完整复制，返给模型要求修正对应 `.mmd`，再次渲染。**最多 3 轮**。仍失败则简化（拆 subgraph / 减节点）或转人工。

> 也可用 `bash scripts/validate.sh <name>.mmd` 一步完成「渲染 + 错误提示」。

### Step 5 · 交付
向用户交付：
- 可编辑源文件 `<name>.mmd`
- 预览图 `<name>.png`（如需 SVG：`scripts/render.sh -i x.mmd -o x.svg`）
- 可嵌入的 ```` ```mermaid ```` 代码块
- 若用户要进公众号/笔记：结合 `wechat-rich-text` 等技能转富文本

### 降级策略
超复杂自由排版 / 信息图（卡片网格、像素级定位）Mermaid 不擅长 → 转 **draw.io 副格式**（参见 `research-drawio-skill.md`），用 XML 精确控制坐标。

## 四、两大护城河

### 4.1 Mermaid-First 提示词
- 先声明图类型 + 约束；仅输出代码、无解释；用负面约束抑制自由发挥。
- 复杂图（>12 节点）先用 `%%` 注释规划结构，再填语法。
- 从最简图（≤12 节点）起步，逐轮扩充（Iterative Refinement）。
- 模型建议：Claude 攻坚复杂时序/类图；GPT-4o 擅长流程图/通用图。

### 4.2 Error Recovery Loop（渲染验证循环）
Mermaid 无 XSD 硬校验，靠「生成 → 渲染 → 捕获错误 → 回灌修正」循环保质量。这是专业与玩具的分水岭，必须执行 Step 4。

## 五、中文避坑硬规则（生成代码前必读 `references/pitfalls.md`）
- 节点 ID 用英文字母（camelCase），中文只放标签：`start[开始]` 或 `auth["认证服务"]`
- 标签含括号/`&`/`#`/`,`/空格 → 必须加双引号：`a["用户(未登录)"]`
- 行尾**不要分号**（Mermaid v11 不允许 `A --> B;`）
- subgraph 用 `subgraph id["显示名"]`，不以数字/特殊字符开头
- 连接标签用 `|文本|`：`A -->|是| B`
- 详情见 `references/pitfalls.md`

## 六、渲染后端
- 引擎：`@mermaid-js/mermaid-cli`（`mmdc`），依赖 Node ≥18 / puppeteer(Chromium)。
- 沙箱已具备：Node 20、中文字体 `Noto Serif CJK SC`。
- 首次渲染脚本会自动 `PUPPETEER_SKIP_DOWNLOAD=true npm install -g @mermaid-js/mermaid-cli`（仅装 CLI，Chrome 走动态探测到的本地二进制；联网装包，已缓存则秒过）。
- 配置：`config.json`（字体/主题/品牌色）、`puppeteer-config.json`（无头渲染）。

## 七、目录结构
```
mermaid-pro/
├── SKILL.md
├── references/        # diagram-types / style-guide / prompt-templates / pitfalls
├── scripts/           # render.sh（渲染封装）、validate.sh（渲染+错误提示）
├── templates/         # 10 个起点模板（6 骨架 + 4 真实业务范例）
├── config.json        # Mermaid 渲染配置（含中文）
└── puppeteer-config.json
```

## 八、参考资料
- Mermaid 官方文档 https://mermaid.js.org/
- mermaid-cli https://deepwiki.com/mermaid-js/mermaid-cli/2-installation-and-usage
- Mermaid Prompt Engineering https://mermaid2img.com/pt-BR/blog/mermaid-prompt-engineering-for-llms
- 副格式（draw.io）参考：research-drawio-skill.md

## 九、典型问答示例

**Q1：帮我画一个用户登录流程。**
→ 图型：flowchart；起点：`templates/flowchart.mmd`；要点：含"未登录/已登录"判断分支，标签含括号须加引号 `a["用户(未登录)"]`，连接标签用 `|是|`。

**Q2：画一张智体联邦的技术栈时序图。**
→ 图型：sequenceDiagram；起点：`templates/fed-tech-sequence.mmd`；要点：`participant 别名 as 显示名`，有分支用 `alt/opt`，消息用 `A->>B: 文本`。

**Q3：把这个产品架构画成图，还要进公众号。**
→ 图型：flowchart LR + subgraph；流程：写 `.mmd` → `render.sh` 出 PNG → 结合 `wechat-rich-text` 转富文本。起点参考 `templates/edge-ai-deployment.mmd`。
