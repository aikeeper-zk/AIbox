# 公众号富文本组件代码模板

以下为每个组件的完整HTML代码模板。所有模板中的 `[占位符]` 需根据实际内容替换。

配色变量说明：
- `[PD]` = primary-dark
- `[P]` = primary
- `[A]` = accent
- 封面渐变：`[PD] → [P] → [A]`

---

## 1. 封面标题区

```html
<section style="background:linear-gradient(135deg,[PD] 0%,[P] 50%,[A] 100%);border-radius:12px;padding:40px 30px;margin-bottom:30px;text-align:center;">
<p style="font-size:28px;font-weight:bold;color:#ffffff;margin:0 0 8px 0;letter-spacing:2px;">[标题]</p>
<p style="font-size:16px;color:#e0e0e0;margin:0 0 20px 0;letter-spacing:1px;">[副标题]</p>
<p style="font-size:12px;color:#aaa;margin:0;">整理时间：[日期] | 来源：公开信息综合整理</p>
</section>
```

---

## 2. 章节标题条

```html
<section style="background:[P];border-radius:8px;padding:12px 20px;margin-bottom:16px;">
<p style="font-size:18px;font-weight:bold;color:#ffffff;margin:0;">[编号] [章节标题]</p>
</section>
```

编号对照：①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑳

---

## 3. 分隔线

```html
<section style="border:none;height:2px;background:linear-gradient(to right,[P],#e0e0e0,[P]);margin:25px 0;"></section>
```

---

## 4. 正文段落

```html
<p style="margin:0 0 16px 0;font-size:15px;color:#333;line-height:1.8;">[正文内容]，<strong style="color:[A];">强调文字</strong>，普通文字。</p>
```

---

## 5. 数据表格（Flex实现）

### 表头行

```html
<section style="background:[P];padding:8px 16px;display:flex;">
<p style="flex:[列1比例];margin:0;font-weight:bold;color:#fff;font-size:13px;">[列名1]</p>
<p style="flex:[列2比例];margin:0;font-weight:bold;color:#fff;font-size:13px;">[列2]</p>
<p style="flex:[列3比例];margin:0;font-weight:bold;color:#fff;font-size:13px;">[列3]</p>
</section>
```

### 数据行（白底交替灰底）

```html
<!-- 灰底行 -->
<section style="padding:10px 16px;display:flex;background:#f8fafc;border-bottom:1px solid #eee;">
<p style="flex:[列1比例];margin:0;font-size:13px;color:#333;">[数据1]</p>
<p style="flex:[列2比例];margin:0;font-size:13px;color:[A];font-weight:bold;">[数据2]</p>
<p style="flex:[列3比例];margin:0;font-size:13px;color:#555;">[数据3]</p>
</section>

<!-- 白底行 -->
<section style="padding:10px 16px;display:flex;background:#fff;border-bottom:1px solid #eee;">
<p style="flex:[列1比例];margin:0;font-size:13px;color:#333;">[数据1]</p>
<p style="flex:[列2比例];margin:0;font-size:13px;color:[A];font-weight:bold;">[数据2]</p>
<p style="flex:[列3比例];margin:0;font-size:13px;color:#555;">[数据3]</p>
</section>
```

### 高亮行（强调背景色）

```html
<section style="padding:10px 16px;display:flex;background:#e8f5e9;border-bottom:1px solid #eee;">
<p style="flex:[比例];margin:0;font-size:13px;color:[A];font-weight:bold;">[高亮数据]</p>
</section>
```

### 表尾最后一行（无border-bottom）

```html
<section style="padding:10px 16px;display:flex;background:#fff;">
<p style="flex:[列1比例];margin:0;font-size:13px;color:#333;">[数据1]</p>
<p style="flex:[列2比例];margin:0;font-size:13px;color:[A];font-weight:bold;">[数据2]</p>
<p style="flex:[列3比例];margin:0;font-size:13px;color:#555;">[数据3]</p>
</section>
```

### 表格整体包裹（可选，加圆角边框）

```html
<section style="background:#ffffff;border-radius:8px;border:1px solid #ddd;overflow:hidden;margin-bottom:16px;">
  <!-- 表头行 -->
  <!-- 数据行 -->
  <!-- 表尾行 -->
</section>
```

---

## 6. 引用块

### 正面/洞察型（品牌色强调）

```html
<section style="background:#f0f4f8;border-radius:6px;padding:12px 18px;border-left:4px solid [P];margin:0 0 16px 0;">
<p style="margin:0;font-size:14px;color:#555;">💡 [洞察内容]</p>
</section>
```

### 正面型（绿色强调）

```html
<section style="background:#e8f5e9;border-radius:6px;padding:12px 18px;border-left:4px solid #2e7d32;margin:0 0 16px 0;">
<p style="margin:0;font-size:14px;color:#555;">💡 [正面洞察]</p>
</section>
```

### 警示型（橙色）

```html
<section style="background:#fff3e0;border-radius:6px;padding:12px 18px;border-left:4px solid #e65100;margin:0 0 16px 0;">
<p style="margin:0;font-size:14px;color:#555;">⚠️ [警示内容]</p>
</section>
```

### 危险型（红色）

```html
<section style="background:#fce4ec;border-radius:6px;padding:12px 18px;border-left:4px solid #c62828;margin:0 0 16px 0;">
<p style="margin:0;font-size:14px;color:#555;">🔴 [危险/风险内容]</p>
</section>
```

### 关键标注型（品牌色粗体标题）

```html
<section style="background:#f0f4f8;border-radius:6px;padding:12px 18px;border-left:4px solid [A];margin:0 0 16px 0;">
<p style="margin:0;font-size:14px;color:[A];font-weight:bold;">📌 [关键标注内容]</p>
</section>
```

---

## 7. 信息列表块

```html
<section style="background:#f0f4f8;border-radius:8px;padding:14px 18px;margin-bottom:16px;">
<p style="margin:0 0 4px 0;font-size:14px;color:#333;">📌 <strong style="color:[P];">[关键信息1]</strong>：[内容]</p>
<p style="margin:0 0 4px 0;font-size:14px;color:#333;">📌 <strong style="color:[P];">[关键信息2]</strong>：[内容]</p>
<p style="margin:0;font-size:14px;color:#333;">📌 <strong style="color:[P];">[关键信息3]</strong>：[内容]</p>
</section>
```

---

## 8. 深色参数卡

```html
<section style="background:linear-gradient(135deg,[PD],[A]);border-radius:8px;padding:20px;margin-bottom:16px;">
<p style="font-size:16px;font-weight:bold;color:#ffffff;margin:0 0 12px 0;">🔥 [产品名] 核心参数</p>
<p style="margin:0 0 6px 0;font-size:14px;color:#e8e0f0;">📌 [参数1]：<strong style="color:#ffffff;font-size:16px;">[值]</strong></p>
<p style="margin:0 0 6px 0;font-size:14px;color:#e8e0f0;">📌 [参数2]：<strong style="color:#ffffff;">[值]</strong></p>
<p style="margin:0;font-size:14px;color:#e8e0f0;">📌 [参数3]：<strong style="color:#ffffff;">[值]</strong></p>
</section>
```

---

## 9. ✅优势 / ❌挑战 双卡

### 优势卡

```html
<section style="background:#e8f5e9;border-radius:8px;padding:16px 20px;margin-bottom:16px;border:1px solid #c8e6c9;">
<p style="font-size:16px;font-weight:bold;color:#2e7d32;margin:0 0 12px 0;">✅ 优势</p>
<p style="margin:0 0 8px 0;font-size:14px;color:#333;"><strong style="color:#2e7d32;">1. [优势1]</strong>——[说明]</p>
<p style="margin:0 0 8px 0;font-size:14px;color:#333;"><strong style="color:#2e7d32;">2. [优势2]</strong>——[说明]</p>
<p style="margin:0;font-size:14px;color:#333;"><strong style="color:#2e7d32;">3. [优势3]</strong>——[说明]</p>
</section>
```

### 挑战卡

```html
<section style="background:#fce4ec;border-radius:8px;padding:16px 20px;margin-bottom:16px;border:1px solid #f8bbd0;">
<p style="font-size:16px;font-weight:bold;color:#c62828;margin:0 0 12px 0;">❌ 挑战</p>
<p style="margin:0 0 8px 0;font-size:14px;color:#333;"><strong style="color:#c62828;">1. [挑战1]</strong>——[说明]</p>
<p style="margin:0 0 8px 0;font-size:14px;color:#333;"><strong style="color:#c62828;">2. [挑战2]</strong>——[说明]</p>
<p style="margin:0;font-size:14px;color:#333;"><strong style="color:#c62828;">3. [挑战3]</strong>——[说明]</p>
</section>
```

---

## 10. 时间线/事件列表

```html
<section style="background:#f0f4f8;border-radius:8px;padding:16px 20px;margin-bottom:16px;">
<p style="font-size:16px;font-weight:bold;color:[P];margin:0 0 12px 0;">📅 [时间线标题]</p>
<p style="margin:0 0 8px 0;font-size:14px;color:#333;">📌 <strong style="color:[A];">[时间1]</strong> [事件1]</p>
<p style="margin:0 0 8px 0;font-size:14px;color:#333;">📌 <strong style="color:[A];">[时间2]</strong> [事件2]</p>
<p style="margin:0;font-size:14px;color:#333;">📌 <strong style="color:[A];">[时间3]</strong> [事件3]</p>
</section>
```

---

## 11. 数据速览表（结尾汇总）

```html
<section style="background:#ffffff;border-radius:8px;border:1px solid #ddd;overflow:hidden;margin-bottom:0;">
<section style="background:[P];padding:8px 16px;display:flex;">
<p style="flex:1;margin:0;font-weight:bold;color:#fff;font-size:14px;">指标</p>
<p style="flex:1.5;margin:0;font-weight:bold;color:#fff;font-size:14px;">数据</p>
</section>
<section style="padding:8px 16px;display:flex;background:#f8fafc;border-bottom:1px solid #eee;">
<p style="flex:1;margin:0;font-size:13px;color:#555;">[指标1]</p>
<p style="flex:1.5;margin:0;font-size:13px;color:[A];font-weight:bold;">[数据1]</p>
</section>
<!-- 更多行... -->
<section style="padding:8px 16px;display:flex;background:#fff;">
<p style="flex:1;margin:0;font-size:13px;color:#555;">[指标N]</p>
<p style="flex:1.5;margin:0;font-size:13px;color:[A];font-weight:bold;">[数据N]</p>
</section>
</section>
```

---

## 12. 尾部声明

```html
<section style="text-align:center;padding:10px 0;">
<p style="font-size:12px;color:#999;margin:0;">本文基于公开信息整理，仅供研究参考</p>
</section>
```

---

## 完整文章结构模板

```html
<!-- 封面 -->
<section style="background:linear-gradient(135deg,[PD] 0%,[P] 50%,[A] 100%);border-radius:12px;padding:40px 30px;margin-bottom:30px;text-align:center;">
<p style="font-size:28px;font-weight:bold;color:#ffffff;margin:0 0 8px 0;letter-spacing:2px;">[标题]</p>
<p style="font-size:16px;color:#e0e0e0;margin:0 0 20px 0;letter-spacing:1px;">[副标题]</p>
<p style="font-size:12px;color:#aaa;margin:0;">整理时间：[日期] | 来源：公开信息综合整理</p>
</section>

<!-- ① 第一章 -->
<section style="background:[P];border-radius:8px;padding:12px 20px;margin-bottom:16px;">
<p style="font-size:18px;font-weight:bold;color:#ffffff;margin:0;">① [章节1标题]</p>
</section>
<p style="margin:0 0 16px 0;font-size:15px;color:#333;line-height:1.8;">[正文]</p>

<!-- 分隔线 -->
<section style="border:none;height:2px;background:linear-gradient(to right,[P],#e0e0e0,[P]);margin:25px 0;"></section>

<!-- ② 第二章 -->
<section style="background:[P];border-radius:8px;padding:12px 20px;margin-bottom:16px;">
<p style="font-size:18px;font-weight:bold;color:#ffffff;margin:0;">② [章节2标题]</p>
</section>
<p style="margin:0 0 16px 0;font-size:15px;color:#333;line-height:1.8;">[正文]</p>

<!-- ...更多章节... -->

<!-- 数据速览 -->
<section style="background:[P];border-radius:8px;padding:12px 20px;margin:25px 0 16px 0;">
<p style="font-size:18px;font-weight:bold;color:#ffffff;margin:0;">📊 数据速览</p>
</section>
<section style="background:#ffffff;border-radius:8px;border:1px solid #ddd;overflow:hidden;margin-bottom:0;">
<!-- 表头+数据行 -->
</section>

<!-- 尾部声明 -->
<section style="text-align:center;padding:10px 0;">
<p style="font-size:12px;color:#999;margin:0;">本文基于公开信息整理，仅供研究参考</p>
</section>
```
