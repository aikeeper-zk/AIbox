# Mermaid 模板库 (templates/)

本目录提供可直接复用的 Mermaid 源文件（`.mmd`），分为两类：

- **骨架模板**：通用语法骨架，适合照着改结构。
- **真实范例**：基于智体共合真实业务沉淀，结构/风格已验证可渲染，可直接参考。

| 文件 | 图类型 | 说明 | 性质 |
|------|--------|------|------|
| `flowchart.mmd` | 流程图 | 通用流程 / 步骤编排骨架 | 骨架 |
| `sequence.mmd` | 时序图 | 多方交互时序骨架 | 骨架 |
| `architecture.mmd` | 架构图 | 系统 / 产品分层架构骨架 | 骨架 |
| `class.mmd` | 类图 | 面向对象类关系骨架 | 骨架 |
| `mindmap.mmd` | 思维导图 | 发散 / 归纳结构骨架 | 骨架 |
| `timeline.mmd` | 时间线 | 里程碑 / 演进时间线骨架 | 骨架 |
| `edge-ai-deployment.mmd` | 架构图 (flowchart) | 小龙虾AI盒子「边缘AI部署架构」真实范例 | 真实范例 |
| `fed-tech-sequence.mmd` | 时序图 (sequence) | 智体联邦「技术栈交互时序」真实范例 | 真实范例 |
| `agent-data-model.mmd` | 类图 (class) | 智体联邦「Agent 数据模型」真实范例 | 真实范例 |
| `product-evolution.mmd` | 时间线 (timeline) | 智体共合「产品与生态演进」真实范例 | 真实范例 |

> 当前共 10 个模板：**6 骨架 + 4 真实业务范例**（flowchart / sequence / class / timeline 四类均有真实范例可循）。

## 使用方式
- 生成图前，先到本目录挑一个**同类型模板**作参考（真实范例的结构与配色已验证可正常渲染）。
- 渲染命令：
  ```bash
  bash scripts/render.sh -i templates/<file>.mmd -o output/<name>.png -t default
  ```
- 真实范例的 `.mmd` 已同步在 `output/` 下渲染出 PNG / SVG 供预览。
- 中文标签用 `<br/>` 换行，节点 ID 用英文、中文只放标签，避免渲染报错。
