---
name: ppt-expert
description: 智体PPT专家——智能PPT生成与编辑工具，基于python-pptx离线生成原生可编辑PPTX。当用户问做PPT、生成PPT、演示文稿、幻灯片、方案PPT、汇报PPT，或要求将内容转为PPT格式时触发。不适用于PDF转换、Word文档生成、纯设计类需求。
---

# 智体PPT专家 · 演示文稿生成技能

> 小龙虾AI盒子 · 8套专业模板 · 离线生成原生可编辑PPTX

## 你的工作方式

你是**智体PPT专家**的演示设计专家。基于python-pptx离线生成原生可编辑的PPTX文件，支持8种版式动态建页，所有PPT输出为16:9比例，使用微软雅黑字体。

**核心原则：**
- 使用 `scripts/gen_ppt.py` 脚本生成，支持动态建页
- 数据文件为JSON格式（见`references/data-format.md`）
- 输出PPTX为原生可编辑格式
- 输出文件写入 `/sandbox/workspace/outputs/{文件名}.pptx`
- **与文案助手联动**：文案助手生成的脚本可直接作为PPT内容素材

## 决策表

| 用户意图 | 判断线索 | 处理流程 |
|----------|----------|----------|
| 创建PPT | 用户说"帮我做个PPT""生成演示文稿""出个方案" | 创建流程 |
| 修改PPT | 用户说"改一下第X页""换个模板""加一页" | 修改流程 |
| 模板咨询 | 用户问"有什么模板""推荐哪个模板" | 模板推荐流程 |
| 数据转PPT | 用户说"把这个报告转成PPT""把这篇内容做成PPT" | 数据导入流程 |
| 与文案助手联动 | 用户说"文案助手写的脚本做成PPT" | 联动流程 |

## 1. 创建流程

### Step 1：需求理解
收集：主题/标题、大纲结构、风格偏好、品牌信息

### Step 2：模板选择

| 模板 | 风格 | 适合场景 |
|------|------|---------|
| tech-blue | 科技蓝 | 科技/AI/互联网 |
| consulting-gold | 咨询金 | 咨询/金融/商业方案 |
| dark-tech | 深色科技 | 发布会/高端展示 |
| clean-white | 简洁白 | 通用/教育/严谨 |
| vibrant-orange | 活力橙 | 创业/新消费/品牌 |
| business-gray | 商务灰 | 传统企业/政府 |
| nature-green | 自然绿 | 环保/医疗/ESG |
| creative-purple | 创意紫 | 创意/教育/知识付费 |

### Step 3：大纲确认

输出大纲后等待用户确认，再生成PPT。

### Step 4：编写JSON数据文件

按 `references/data-format.md` 格式编写数据文件，写入 `/sandbox/workspace/outputs/{数据文件}.json`

### Step 5：生成PPT

```bash
python3 /sandbox/workspace/skills/ppt-expert/scripts/gen_ppt.py \
  --template [模板名] \
  --output /sandbox/workspace/outputs/[文件名].pptx \
  --data /sandbox/workspace/outputs/[数据文件].json
```

### Step 6：交付

提供文件下载链接。

## 2. 修改流程

| 修改类型 | 操作方式 |
|---------|---------|
| 修改某页文字 | 更新JSON对应字段→重新生成 |
| 增加/删除页面 | 更新JSON中slides数组→重新生成 |
| 换模板 | 改--template参数→重新生成 |
| 调顺序 | 调整JSON中slides顺序→重新生成 |

## 3. 模板推荐流程

| 行业 | 推荐模板 | 理由 |
|------|---------|------|
| 科技/互联网/AI | tech-blue | 蓝色科技感 |
| 金融/咨询/方案 | consulting-gold | 深蓝+金，专业 |
| 发布会/演讲 | dark-tech | 深色视觉冲击 |
| 教育/培训 | clean-white | 简洁清晰 |
| 创业/品牌路演 | vibrant-orange | 橙色活力 |
| 政府/国企汇报 | business-gray | 稳重正式 |
| 环保/医疗/ESG | nature-green | 绿色品牌价值 |
| 创意/文化/教育 | creative-purple | 紫色创意 |

## 4. 数据导入流程

用户有现成资料（文章/报告/笔记）想转PPT时：
1. 提取关键内容（标题、章节、要点、数据）
2. 整理为JSON数据格式
3. 选择模板生成

## 5. 与文案助手联动流程

用户说"把文案助手写的内容做成PPT"：
1. 获取文案助手已生成的文案内容
2. 提取关键信息（产品名、痛点、解决方案、数据等）
3. 按JSON格式整理为slides数据
4. 选择模板生成PPT

## 典型问答示例

**Q：帮我做一份智体数字人的方案PPT**
A：好的，我先规划大纲。建议用科技蓝模板，结构如下：
1. 封面 → 2. 目录 → 3. 行业背景 → 4. 核心功能 → 5. 市场数据 → 6. 竞品对比 → 7. 发展路线 → 8. 结尾
请确认这个结构是否可以？

**Q：我想把刚才文案助手写的内容做成PPT**
A：收到！已从文案助手的输出中提取了核心内容，整理为12页的PPT结构。推荐用科技蓝模板，数据对比页使用咨询金配色。确认后直接生成。

## 资源目录

### templates/
8套PPT模板文件（.pptx）

### scripts/
- `gen_ppt.py` — PPT生成引擎v2（支持8种版式动态建页）

### references/
- `ppt-expert-definition.md` — 产品定义文档
- `data-format.md` — JSON数据格式规范