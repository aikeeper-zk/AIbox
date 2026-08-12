# Mermaid 图表类型速查（v11，24+ 类型）

> 主推 8 类做模板库；其余给语法起点。所有示例均可直接渲染。

## 一、流程 / 逻辑
- **flowchart**（流程图）：`flowchart TD`（上→下）/`flowchart LR`（左→右）
  ```
  flowchart LR
    A[开始] --> B{判断}
    B -->|是| C[处理]
    B -->|否| D[结束]
  ```
- **stateDiagram-v2**（状态机）：`stateDiagram-v2` + `state 名 : 描述` + `[*] --> 状态`
- **block-beta**（块/架构块图）：`block-beta` + `columns 3` + `blockId["名"]`

## 二、交互 / 时序
- **sequenceDiagram**（时序图）：`actor`/`participant` + `A->>B: 消息` + `alt/opt/loop`
- **journey**（用户旅程）：`journey` + `section 阶段 : 任务: 评分`

## 三、结构 / 架构
- **classDiagram**（类图）：`class X { +字段 +方法 }` + 关系 `A *-- B`
- **erDiagram**（ER 图）：`ENTITY ||--o{ ENTITY : 关系`
- **C4**（架构，beta）：`C4Context` / `C4Container` / `C4Component` + `Person/System/Container/Rel`

## 四、规划 / 时间
- **gantt**（甘特图）：`gantt` + `section 阶段 : a1, 开始, 时长`
- **timeline**（时间线）：`timeline` + `标题 : 时间 : 事件`
- **gitgraph**（Git 图）：`gitGraph` + `commit` / `branch` / `merge`
- **kanban**（看板，beta）：`kanban` + `columns` / `taskId["名"]`

## 五、思维 / 分析
- **mindmap**（思维导图）：`mindmap` + `root((中心))` + 缩进层级
- **quadrantChart**（四象限）：`quadrantChart` + `x-axis / y-axis` + `point`
- **requirementDiagram**（需求）：`requirementDiagram` + `requirement/element/relationship`

## 六、数据 / 可视化
- **xychart-beta**（折线/柱状）：`xychart-beta` + `x-axis / y-axis`
- **sankey**（桑基，beta）：`sankey-beta` + `A --> B: 值`
- **pie**（饼图）：`pie` + `title` + `"标签" : 值`

## 七、网络
- **packet**（包结构，beta）：`packet` + `hdr` / `tlv`

> 更多语法见官方文档 https://mermaid.js.org/
