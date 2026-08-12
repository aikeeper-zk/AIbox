# Mermaid-First 提示词模板库

> 核心策略：**先声明图类型 + 约束，仅输出代码，加负面约束**。复杂图先用 `%%` 注释规划。

## 通用骨架
```
Output ONLY valid Mermaid code. No explanation, no markdown wrapper.
Create a <diagram-type> for: <描述>
<节点/参与者/关系/约束>
Do NOT: add explanations; use trailing semicolons; exceed 12 nodes in one pass; use Chinese as node IDs.
```

## 流程图（flowchart）
```
Output ONLY valid Mermaid code.
Create a flowchart LR for the process: <过程描述>
Nodes (use English IDs, Chinese labels in brackets): ...
Decision points: ...
Style: max 12 nodes; arrow labels in |...|; Chinese labels must be quoted if they contain () & # ,
```
起点模板：`templates/flowchart.mmd`

## 时序图（sequenceDiagram）
```
Output ONLY a Mermaid sequenceDiagram. No explanation.
Participants: A(用户), B(系统), C(服务)
Interaction: 1. A->>B: 请求  2. B->>C: 调用  3. C-->>B: 响应  4. B-->>A: 结果
Include alt/opt/loop where branching exists.
```
起点模板：`templates/sequence.mmd`

## 架构图（flowchart LR + subgraph）
```
Output ONLY valid Mermaid code.
Create an architecture diagram using flowchart LR with subgraphs for layers:
- 接入层: ...
- 应用层: ...
- 数据层: ...
Use English subgraph IDs with Chinese titles: subgraph id["标题"]
```
起点模板：`templates/architecture.mmd`

## 类图（classDiagram）
```
Output ONLY a Mermaid classDiagram. No explanation.
Classes: <类名 + 字段 + 方法>
Relationships: 1..* / *-- / <|-- 
```
起点模板：`templates/class.mmd`

## 思维导图（mindmap）
```
Output ONLY a Mermaid mindmap. No explanation.
Center: <主题>
Branches (indentation = hierarchy): ...
```
起点模板：`templates/mindmap.mmd`

## 时间线（timeline）
```
Output ONLY a Mermaid timeline. No explanation.
Title: <标题>
Entries: 时间 : 事件
```
起点模板：`templates/timeline.mmd`

## 进阶技巧
1. **Comment-First**：>12 节点时先写 `%% 规划: 层1=... 层2=...` 注释，再填语法，减少错误。
2. **Iterative Refinement**：先出 ≤12 节点最简版渲染通过，再逐轮加细节。
3. **Error Recovery**：渲染失败，把报错原文返给模型修正（见 SKILL.md Step 4）。
