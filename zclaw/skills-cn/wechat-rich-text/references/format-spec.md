# 公众号富文本排版完整规范

## 标签体系

### 允许的标签

| 标签 | 用途 | 说明 |
|---|---|---|
| `<section>` | 所有容器 | 替代 `<div>`，公众号兼容性最佳 |
| `<p>` | 所有文字 | 替代 `<span>` 嵌套，每段文字用 `<p>` |
| `<strong>` | 强调文字 | 配合 `style="color:品牌色"` 实现彩色强调 |

### 禁止的标签

| 标签 | 原因 |
|---|---|
| `<div>` | 公众号编辑器会压缩嵌套层级 |
| `<table>` / `<tr>` / `<td>` / `<th>` | 部分客户端渲染异常，用 flex `<section>` 替代 |
| `<span>` | 嵌套层级问题，用 `<strong style="">` 替代 |
| `<h1>` ~ `<h6>` | 公众号编辑器对heading标签处理不一致，用 `<p style="font-size:18px;font-weight:bold">` 替代 |
| `<ul>` / `<ol>` / `<li>` | 公众号对列表标签样式控制弱，用 📌/✓/✕/▸ 符号 + `<p>` 替代 |
| `<blockquote>` | 样式不可控，用 `<section>` + 左border替代 |

### 样式方式

- ✅ **所有样式写在 `style=""` 内联属性中**
- ❌ **禁止 `class=""` 属性**——公众号会过滤CSS类
- ❌ **禁止 `<style>` 标签**——公众号编辑器不支持
- ❌ **禁止外部样式表引用**——公众号不支持

## 文字与间距规范

### 正文文字

```html
<p style="margin:0 0 16px 0;">正文内容，<strong style="color:品牌accent色;">强调文字</strong></p>
```

- 字号：15px（正文）、14px（表格/引用块）、13px（表格行数据）
- 行高：1.8（继承外层 `<section>`）
- 颜色：#333（正文）、#555（次要说明）、#999（尾部注释）
- 段间距：margin-bottom 16px

### 强调文字

用 `<strong>` + 内联color，不用 `<span>`：

```html
<strong style="color:#3b82f6;">蓝色强调</strong>
<strong style="color:#c62828;">红色强调（亏损/风险）</strong>
<strong style="color:#2e7d32;">绿色强调（增长/正面）</strong>
<strong style="color:#e65100;">橙色强调（警示）</strong>
<strong style="color:#品牌accent色;">品牌色强调</strong>
```

### 列表项

不用 `<ul>/<li>`，用符号 + `<p>`：

```html
<p style="margin:0 0 8px 0;font-size:14px;color:#333;">📌 列表项内容</p>
<p style="margin:0 0 8px 0;font-size:14px;color:#333;">✓ 正面列表项</p>
<p style="margin:0 0 8px 0;font-size:14px;color:#333;">✕ 负面列表项</p>
<p style="margin:0 0 8px 0;font-size:14px;color:#333;">▸ 普通列表项</p>
```

## 配色方案规范

### 配色结构（每篇文章5色系）

| 色名 | 用途 | 固定值/可变 |
|---|---|---|
| primary-dark | 封面渐变起点、标题条bg | 可变（用户指定或推断） |
| primary | 章节标题条、表格头、分隔线、强调 | 可变 |
| accent | 关键数据高亮、品牌色强调 | 可变 |
| red | 亏损、风险、挑战 | 固定 #c62828 |
| orange | 警示、注意 | 固定 #e65100 |
| green | 增长、正面、优势 | 固定 #2e7d32 |

### 常用配色方案

| 主题 | primary-dark | primary | accent | 说明 |
|---|---|---|---|---|
| 英伟达/绿色品牌 | #0a2618 | #1a5c4e | #2d8659 | 经典绿色系 |
| 科技/AI/GPU | #0d0d1a | #1a2744 | #3b82f6 | 蓝色科技感 |
| 腾讯/社交 | #0a1628 | #0f3460 | #7c3aed | 蓝紫系 |
| 金融/官方 | #1b263b | #334155 | #c9a227 | 灰金系 |
| 创业/活力 | #1a1a2e | #2d2d44 | #f97316 | 橙色系 |
| Crimson/AMD | #1a0a0a | #8b0000 | #dc143c | 深红系 |

### 辅助色

| 用途 | 色值 |
|---|---|
| 正面背景浅色 | #e8f5e9 |
| 警示背景浅色 | #fff3e0 |
| 危险背景浅色 | #fce4ec |
| 信息背景浅色 | #f0f4f8 |
| 表格交替行 | #f8fafc / #fff |
| 表格高亮行 | #e8f5e9 |
| 封面渐变终点 | accent色 |

## 排版禁忌

1. **不嵌套超过3层 `<section>`**——公众号编辑器会压缩深层嵌套
2. **不在 `<p>` 内嵌套 `<section>`**——只有 `<section>` 包裹 `<p>`，不反向嵌套
3. **不在文字行内用 `<section>`**——文字用 `<p>` + `<strong>`
4. **表格不用 `<table>`**——用 `<section style="display:flex">` 实现列布局
5. **不在封面区放大量文字**——封面只放标题+副标题+日期
6. **分隔线不用 `<hr>`**——用 `<section style="height:2px;background:linear-gradient(...)">`
7. **不用emoji做章节编号**——用 ①②③④⑤⑥⑦⑧⑨⑩⑪⑫ 等Unicode编号
