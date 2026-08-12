# Prompt 模板 · 生成 logic.json

## 通用模板

将用户描述转化为 `logic.json` 结构。只输出 JSON，不输出解释。

```
根据以下用户需求，生成 draw.io 图表用的 logic.json：

用户需求：[用户描述]
图类型：[flowchart|architecture]
布局方向：[LR|TB]

要求：
1. nodes 中每个节点必须有 id（n1/n2...）、label（中文标签）、color（配色名）、layer（层数，从0开始）、shape（形状名）
2. edges 中每个连线必须有 from、to，可选 label
3. 只输出 JSON 代码块，不输出任何其他内容
```

## 流程图专用（#1/#2）

```
生成一个 [标题] 的流程图 logic.json。

节点列表：
- 开始：形状 start，颜色 blue，layer 0
- [节点2]：形状 rounded，颜色 lightblue，layer 1
- [节点3]：形状 diamond（判断），颜色 orange，layer 1
- [节点4]：形状 rounded，颜色 green，layer 2
- 结束：形状 end，颜色 purple，layer 2

连线：
- n1 → n2（标签："开始"）
- n2 → n3
- n3 → n4（标签："是"）
- n2 → n4（标签："否"）
- n4 → n5
```

## 架构图专用（#3/#7）

```
生成一个 [标题] 的分层架构图 logic.json。

层级结构（从下到上或从左到右）：
- 硬件层：layer 0，包含 [节点]，颜色 gray
- 系统层：layer 1，包含 [节点]，颜色 purple
- 引擎层：layer 2，包含 [节点]，颜色 green
- 能力层：layer 3，包含 [节点]，颜色 lightblue
- 应用层：layer 4，包含 [节点]，颜色 blue

连线：下层向上层提供服务。例如 n1(layer0) → n2(layer1)，n2 → n3(layer2) 等。
```
