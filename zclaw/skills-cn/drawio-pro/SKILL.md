---
name: drawio-pro
author: 随风话雪
description: 专业 Draw.io 绘图助手——用自然语言生成可编辑的 .drawio 图表（流程图、架构图、时序图、信息图等）。基于 draw.io (mxGraph) XML 格式，支持自动布局算法、SVG 预览，产出可在 app.diagrams.net 直接打开编辑的源文件。当用户需要画专业图表、信息图、架构图、需要像素级精确控制，或说"在 draw.io 里打开""导出 drawio 格式""画个能继续编辑的图"时触发。不适用于纯文本图表（用 mermaid-pro）、纯美术设计、位图编辑。
---
# Draw.io 专业绘图助手（drawio-pro）

用自然语言产出**可编辑的专业图表**：自然语言 → 逻辑结构 → 自动布局 → `.drawio` 可编辑源文件 + SVG 预览。

> **与 mermaid-pro 的关系**：互补双技能。mermaid-pro 主打快速出图、自动布局、文档内嵌；drawio-pro 主打像素级精确控制、自由排版、专业设计感、可继续编辑。根据场景二选一。

---

## 一、何时使用（触发词）

- 用户说：画个/做个/生成 **流程图、架构图、信息图、时序图、ER图、网络拓扑、组织结构图、思维导图、商业画布、自由排版图**
- 用户说：「导出 .drawio 格式」「能在 draw.io 里打开编辑的」「给我一个可编辑的源文件」
- 用户说：「像素级控制」「精确排版」「这个图我要继续改」
- 用户上传/描述复杂逻辑，需要精细布局的图

**不适用** → 纯文本快速出图、Markdown 文档内嵌 → 用 `mermaid-pro`。

## 一·五、决策路由表

| # | 用户意图 | 布局类型 | direction | 说明 |
|---|---|---|---|---|
| 1 | 业务流程 / 审批链 | flowchart | LR | 从左到右，按层排列 |
| 2 | 自上而下的流程 | flowchart | TB | 从上到下 |
| 3 | 系统 / 产品分层架构 | architecture | LR | 每层一个 layer，含 subgraph |
| 4 | 数据流转 / 管道 | flowchart | LR | 强调数据流向 |
| 5 | 组织结构 / 层级 | flowchart | TB | 树状展开 |
| 6 | 信息图 / 对比 | flowchart | LR | 自由排版，多列 |
| 7 | 部署架构 | architecture | LR | 硬件+软件分层 |
| 8 | 交互时序 / API调用链 | sequence | LR | 参与者横向排列，消息纵向 |
| 9 | 数据模型 / 实体关系 | er | LR | 实体-关系，自动排布 |
| 10 | UML 类图 / 数据模型 | uml | LR | 三分栏类名/属性/方法，支持继承/实现/聚合/组合/关联/依赖 |
| 11 | 思维导图 | mindmap | TB | 辐射状（需 Python 扩展） |

> 不确定时默认 `flowchart LR`。序号可在 SOP 中引用。

## 二、核心能力

1. **自动布局**：LLM 只产出逻辑结构（节点、边、层次），坐标由布局引擎自动计算，彻底解决 AI 算坐标翻车问题。
2. **draw.io 原生格式**：输出合法的 `mxGraphModel` XML，可在 [app.diagrams.net](https://app.diagrams.net) 直接打开、编辑、导出。
3. **SVG 预览**：从同一数据源同步渲染 SVG 预览图，所见即所得。
4. **精准控制**：支持自定义节点宽高、形状（圆角/椭圆/菱形/圆柱）、颜色、连线样式。
5. **可继续编辑**：交付 `.drawio` 源文件，用户可在 draw.io 桌面版/在线版中继续细化。

## 三、工作流 SOP

### Step 1 · 澄清意图
确认：① 图类型（流程图/架构图/信息图）；② 核心内容与节点列表；③ 布局方向（默认 LR 从左到右）；④ 是否需要 SVG 预览（默认需要）。

### Step 2 · 产出逻辑结构
LLM 将用户描述转化为结构化 JSON：
- `nodes`：节点列表（id, label, color, layer, shape）
- `edges`：连线列表（from, to, label）
- `layout`：布局参数（type, direction）

LLM **只产出逻辑结构**，不涉及任何坐标计算。

### Step 2.5 · 用户确认逻辑结构 ⚡【确认门】
将生成的 logic.json 展示给用户确认：
- 节点数量、标签、层级是否准确？
- 连线关系、方向是否正确？
- 布局方向 LR/TB 是否符合预期？
- 用户可要求增删改节点或重新选择图类型。

> 用户确认后再进入 Step 3。若用户不满意，返回 Step 2 修改逻辑结构。

### Step 3 · 自动布局 + 生成文件
调用 `scripts/build_drawio.py`：
```bash
python3 scripts/build_drawio.py -i <name>.json -o output/<name>.drawio -p output/<name>.svg
```
脚本自动完成：
1. 按 `layer` 分层，从左到右（LR）或从上到下（TB）均匀排布
2. 生成合法 `.drawio` XML（含 mxCell 节点/连线/样式）
3. 同步渲染 SVG 预览图

### Step 3.5 · 反馈修改循环 🔄【多轮迭代】
将生成的 SVG 预览展示给用户。若用户不满意：
1. **定位问题**：节点位置/配色/尺寸/连线/缺少内容？
2. **修改 logic.json**：对应调整 labels / colors / layers / width/height / edges
3. **重跑 Step 3**：`python3 scripts/build_drawio.py -i ...`
4. 最多 **3 轮**。仍不满意 → 降级（见下方）。

### Step 4 · 交付
向用户交付：
- **可编辑源文件** `<name>.drawio`（可在 app.diagrams.net 打开继续编辑）
- **SVG 预览** `<name>.svg`（浏览器可直接查看）
- **快捷链接**：`https://app.diagrams.net/#U<drawio 文件 URL>`（需上传后使用）
- 建议文案：「此文件可在 [diagrams.net](https://app.diagrams.net) 中打开，支持进一步编辑和导出 PNG/SVG/PDF。」

### 降级策略
- 超复杂信息图/多页/自由画布 → 建议用户直接在 app.diagrams.net 中手动编辑，skill 给出初始骨架。
- 快速出图/文档内嵌 → 推荐使用 `mermaid-pro`。
- 多轮修改仍不满意 → 输出当前 logic.json 给用户，建议直接编辑 JSON 后重新生成。

## 四、自动布局规范

### 4.1 分层规则
- `layer` 决定节点所在层数（0 = 第一层）
- LR 方向：每层水平排列，层间距 200px，层内节点垂直间距 80px
- TB 方向：每层垂直排列，层间距 130px，层内节点水平间距 80px
- 边距 padding 40px

### 4.2 节点尺寸
- 默认宽 140px × 高 50px
- 可在 logic.json 中显式指定 `width` / `height`

### 4.3 形状与颜色
| shape 值 | 效果 | 典型用途 |
|---|---|---|
| `rounded` | 圆角矩形 | 通用流程节点 |
| `rect` | 直角矩形 | 处理/操作 |
| `start` | 椭圆 | 开始 |
| `end` | 椭圆 | 结束 |
| `diamond` | 菱形 | 判断/分支 |
| `cylinder` | 圆柱 | 数据库 |

| color 值 | 填充色 | 文字色 | 用途 |
|---|---|---|---|
| `blue` | #2563eb | #ffffff | 主色/关键节点 |
| `lightblue` | #e0f2fe | #0f172a | 一般流程 |
| `green` | #dcfce7 | #0f172a | 成功/完成 |
| `gray` | #f1f5f9 | #0f172a | 辅助/默认 |
| `red` | #fef2f2 | #0f172a | 警告/异常 |
| `purple` | #f3e8ff | #0f172a | 特殊/系统 |
| `orange` | #fff7ed | #0f172a | 注意/待办 |

### 4.4 连线样式
- `orthogonal`（默认）：正交折线，适合流程图
- `curved`：曲线，适合架构图/数据流

## 五、目录结构

```
drawio-pro/
├── SKILL.md                      # 核心指令
├── references/
│   ├── xml-reference.md          # draw.io XML 规范速查
│   ├── style-guide.md            # 样式参考
│   └── prompt-templates.md       # LLM 生成 logic.json 的提示词模板
├── scripts/
│   └── build_drawio.py           # 核心引擎：自动布局 + XML生成 + SVG预览
├── templates/
│   ├── test-flow.json            # 测试用例（AI龙虾盒子部署流程）
│   └── logic-ai-box-arch.json    # 真实案例（AI龙虾盒子技术架构）
└── config.json
```

## 六、技术说明

### 6.1 .drawio 文件格式
- 基于 mxGraphModel XML，官方格式文档见 [draw.io AI Diagram Generation](https://www.draw.io/ai-diagram-generation)
- 每个图表包含根 cell（id=0/1）、节点 cell（vertex=1）、连线 cell（edge=1）
- 节点位置由 `<mxGeometry x=".." y=".." width=".." height=".." />` 定义
- 样式用 style 字符串表达：`key=value;key=value;`

### 6.2 渲染后端
- 生成阶段：Python 3.12（无需外部依赖）
- 预览阶段：Python 生成 SVG（无需外部依赖）
- 用户编辑：[app.diagrams.net](https://app.diagrams.net)（免费在线）或 draw.io 桌面版（离线）

### 6.3 参考 & 致谢
- [draw.io / diagrams.net](https://www.diagrams.net) — 开源专业绘图工具
- [mxGraph](https://github.com/jgraph/mxgraph) — 底层绘图引擎
- [draw.io AI Diagram Generation](https://www.draw.io/ai-diagram-generation) — 官方 AI 生成规范
- 参考 `references/prompt-templates.md` — LLM 组装 logic.json 的提示词模板

---

> **作者：随风话雪** | 基于 ima.copilot 构建 | 与 [mermaid-pro](https://ima.copilot) 互补使用

---

## 七、典型问答示例

**Q1：帮我画一个用户登录的流程图。**
→ 路由：#1 flowchart LR。逻辑结构：开始→输入账号→验证→判断（是/否）→登录成功/失败。提示：判断节点用 `diamond` 形状 + `orange` 颜色；成功路径用 `green`，失败用 `red`。

**Q2：画一张 AI 龙虾盒子的技术架构分层图。**
→ 路由：#3 architecture LR。5层：应用场景（blue）→ Agent引擎（lightblue）→ AI引擎+调度器（green+orange）→ OpenClaw系统（purple）→ 硬件Lite/Pro（gray）。交付 .drawio 源文件 + SVG 预览，建议用户用 app.diagrams.net 打开微调。

**Q3：画一个下单到发货的电商时序交互图。**
→ 路由：#8 sequence LR。参与者：用户、前端、订单服务、支付系统、仓储。用户→前端：下单；前端→订单服务：创建订单；订单服务→支付系统：发起支付；支付系统→订单服务：支付回调；订单服务→仓储：发货通知。

**Q4：用户说"节点位置不太对，帮我调一下"。**
→ 走 Step 3.5 修改循环：定位问题（节点所在 layer 不对或间距需要调整）→ 修改 logic.json 中的 `layer` 值或 `width`/`height` → 重新运行 build_drawio.py → 展示新预览。最多 3 轮。

**Q5：用户说"我要能在 draw.io 里继续编辑的"。**
→ 直接选 drawio-pro 而非 mermaid-pro。走完整 SOP：产出 logic.json → build_drawio.py 生成 .drawio → 交付源文件 + 附言"用 app.diagrams.net 打开即可继续编辑"。
