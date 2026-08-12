# SVG常用代码片段参考

> 供AI Logo生成器使用的SVG代码片段库，按需调用，减少手写错误。

---

## 1. 渐变定义

### 1.1 线性渐变（水平方向）
```svg
<linearGradient id="gold" x1="0%" y1="0%" x2="100%" y2="100%">
  <stop offset="0%" stop-color="#B8860B"/>
  <stop offset="25%" stop-color="#F5D76E"/>
  <stop offset="50%" stop-color="#DAA520"/>
  <stop offset="75%" stop-color="#F5D76E"/>
  <stop offset="100%" stop-color="#B8860B"/>
</linearGradient>
```

### 1.2 径向渐变（中心光晕）
```svg
<radialGradient id="starGlow" cx="50%" cy="50%" r="50%">
  <stop offset="0%" stop-color="#FFF3B0" stop-opacity="0.8"/>
  <stop offset="50%" stop-color="#F5D76E" stop-opacity="0.3"/>
  <stop offset="100%" stop-color="#F5D76E" stop-opacity="0"/>
</radialGradient>
```

### 1.3 径向渐变（深色背景底）
```svg
<radialGradient id="bgBlue" cx="50%" cy="50%" r="50%">
  <stop offset="0%" stop-color="#1A3A6A"/>
  <stop offset="60%" stop-color="#0C2461"/>
  <stop offset="100%" stop-color="#081838"/>
</radialGradient>
```

---

## 2. 弧形文字

### 2.1 上弧文字（viewBox="0 0 400 400", 中心在200,200）
```svg
<!-- 路径：半径越大弧越平缓 -->
<path id="topArc" d="M 28 200 A 172 172 0 0 1 372 200" fill="none"/>
<text font-family="'Noto Serif SC','Source Han Serif SC','SimSun','STSong',serif"
      font-size="26" font-weight="bold" fill="url(#gold)" letter-spacing="8">
  <textPath href="#topArc" startOffset="50%" text-anchor="middle">香江俱乐部</textPath>
</text>
```

**参数速查表（半径→文字位置）：**

| 半径 | 文字起始M点 | 适用字号 | 说明 |
|:----:|:----------:|:--------:|------|
| 155 | M 45 200 | 28px | 靠近内圈，弧线较陡 |
| 172 | M 28 200 | 26px | 适中位置（推荐） |
| 180 | M 20 200 | 24px | 偏外圈，弧线较平缓 |

### 2.2 下弧文字
```svg
<!-- 注意：A参数最后一位是 0 0 0（顺时针） -->
<path id="btmArc" d="M 35 200 A 165 165 0 0 0 365 200" fill="none"/>
<text font-family="'Georgia','Times New Roman',serif"
      font-size="14" font-weight="bold" fill="url(#gold)" letter-spacing="4">
  <textPath href="#btmArc" startOffset="50%" text-anchor="middle">XIANGJIANG CLUB</textPath>
</text>
```

---

## 3. 装饰金点阵列

### 3.1 12点均匀分布（r=190）
```svg
<g fill="url(#gold)">
  <circle cx="200" cy="10" r="4"/>
  <circle cx="295" cy="35.5" r="4"/>
  <circle cx="364.5" cy="105" r="4"/>
  <circle cx="390" cy="200" r="4"/>
  <circle cx="364.5" cy="295" r="4"/>
  <circle cx="295" cy="364.5" r="4"/>
  <circle cx="200" cy="390" r="4"/>
  <circle cx="105" cy="364.5" r="4"/>
  <circle cx="35.5" cy="295" r="4"/>
  <circle cx="10" cy="200" r="4"/>
  <circle cx="35.5" cy="105" r="4"/>
  <circle cx="105" cy="35.5" r="4"/>
</g>
```

### 3.2 8点均匀分布（r=190, 从22.5°开始）
```svg
<g fill="url(#gold)">
  <circle cx="272.7" cy="17.5" r="4"/>
  <circle cx="375.4" cy="127.3" r="4"/>
  <circle cx="375.4" cy="272.7" r="4"/>
  <circle cx="272.7" cy="382.5" r="4"/>
  <circle cx="127.3" cy="382.5" r="4"/>
  <circle cx="24.6" cy="272.7" r="4"/>
  <circle cx="24.6" cy="127.3" r="4"/>
  <circle cx="127.3" cy="17.5" r="4"/>
</g>
```

---

## 4. 徽章边框体系

### 4.1 经典双环
```svg
<circle cx="200" cy="200" r="195" fill="none" stroke="url(#gold)" stroke-width="5"/>
<circle cx="200" cy="200" r="184" fill="none" stroke="url(#gold)" stroke-width="2.5"/>
```

### 4.2 三环豪华版
```svg
<circle cx="200" cy="200" r="195" fill="none" stroke="url(#gold)" stroke-width="4"/>
<circle cx="200" cy="200" r="188" fill="none" stroke="url(#gold)" stroke-width="1.5" opacity="0.6"/>
<circle cx="200" cy="200" r="170" fill="none" stroke="url(#gold)" stroke-width="3"/>
```

### 4.3 内圈底色（深色背景衬底）
```svg
<circle cx="200" cy="200" r="182" fill="#0A1628"/>
<circle cx="200" cy="200" r="168" fill="url(#bgBlue)"/>
```

---

## 5. 水波纹（底部装饰）

### 5.1 三层波浪
```svg
<path d="M-90,42 Q-58,20 -26,42 Q8,64 40,42 Q72,20 90,42" fill="none" stroke="url(#waveMix)" stroke-width="4.5" opacity="0.8"/>
<path d="M-78,54 Q-50,34 -22,54 Q8,74 36,54 Q64,34 78,54" fill="none" stroke="url(#waveMix)" stroke-width="3" opacity="0.55"/>
<path d="M-66,64 Q-42,46 -18,64 Q8,82 34,64 Q58,46 66,64" fill="none" stroke="url(#waveMix)" stroke-width="2" opacity="0.35"/>
```

### 5.2 顶部装饰弧
```svg
<path d="M-95,28 Q-60,8 -25,28 Q10,48 45,28 Q80,8 95,28" fill="none" stroke="url(#gold)" stroke-width="1.5" opacity="0.3"/>
```

---

## 6. 星辰/星星

### 6.1 五角星（普通大小）
```svg
<polygon points="0,-76 3.5,-66 15,-66 6.5,-59 9,-48 0,-55 -9,-48 -6.5,-59 -15,-66 -3.5,-66" fill="url(#gold)"/>
```

### 6.2 五角星（放大版+光晕）
```svg
<circle cx="0" cy="-72" r="28" fill="url(#starGlow)"/>
<polygon points="0,-86 5,-73 20,-73 9,-64 12,-50 0,-58 -12,-50 -9,-64 -20,-73 -5,-73" fill="url(#gold)"/>
<line x1="0" y1="-100" x2="0" y2="-88" stroke="url(#gold)" stroke-width="3" stroke-linecap="round" opacity="0.8"/>
<line x1="-16" y1="-96" x2="-9" y2="-86" stroke="url(#gold)" stroke-width="2.5" stroke-linecap="round" opacity="0.6"/>
<line x1="16" y1="-96" x2="9" y2="-86" stroke="url(#gold)" stroke-width="2.5" stroke-linecap="round" opacity="0.6"/>
```

---

## 7. 常用配色组合

| 色系 | 主色 | 辅色 | 适用场景 |
|:----:|:----:|:----:|---------|
| 🥇 蓝+金 | #0C2461 | #DAA520 | 高端/金融/俱乐部 |
| 🥈 墨绿+金 | #1B4332 | #C9A84C | 庄园/酒庄/奢侈品 |
| 🥉 酒红+金 | #5C1010 | #D4AF37 | 经典/传统/会员制 |
| 🩵 科技蓝+白 | #1565C0 | #FFFFFF | AI/科技/互联网 |
| 🖤 黑+金 | #1A1A1A | #F5D76E | 奢华/高端定制 |
| 💚 青+白 | #00897B | #FFFFFF | 健康/环保/创新 |
