# 中英文字体搭配指南

> 在Logo设计中，字体选择直接影响品牌调性的传达。以下搭配指南适用于不同Logo类型。

---

## 一、Logo字体选择原则

1. **中英文字体需协调**：同一Logo中的中英文字体应有相似的笔画气质
2. **有衬线配衬线，无衬线配无衬线**：混搭时需谨慎，除非刻意制造反差
3. **字形风格匹配品牌调性**：高端品牌用经典字体，科技品牌用现代字体
4. **可商用优先**：优先使用系统预装字体或开源字体

---

## 二、弧形文字推荐搭配（徽章/圆形Logo）

| 风格方向 | 中文推荐 | 英文推荐 | 适用场景 |
|---------|---------|---------|---------|
| 🏛️ 经典传统 | `Noto Serif SC`, `SimSun`, `STSong` | `Georgia`, `Times New Roman` | 高端俱乐部、老字号、金融 |
| 🏗️ 现代商务 | `Noto Sans SC`, `Microsoft YaHei`, `PingFang SC` | `Arial`, `Helvetica`, `Open Sans` | 科技公司、咨询、互联网 |
| ✍️ 人文雅致 | `STKaiti`, `KaiTi`, `ZCOOL XiaoWei` | `Palatino`, `Garamond`, `Crimson Text` | 文化品牌、教育、艺术 |
| 🎯 力量感 | `Source Han Serif SC` (Heavy), `SimHei` | `Impact`, `Oswald`, `Montserrat` | 体育、工业、重资产 |

---

## 三、字体尺寸比例参考（徽章式Logo，viewBox=400×400）

| 场景 | 中文字号 | 英文字号 | 比例 |
|:----:|:--------:|:--------:|:----:|
| 中文为主（加英文副标） | 26-28px | 13-15px | ~2:1 |
| 中英文并重 | 22-24px | 16-18px | ~1.3:1 |
| 英文为主 | 18-20px | 18-22px | ~1:1 |
| 底部标语 | 不适用 | 8-10px | 极小字辅助 |

### letter-spacing（字距）参考
- 中文徽章弧形文字：`letter-spacing="6-10"`（字距较大更显庄重）
- 英文徽章弧形文字：`letter-spacing="3-5"`
- 正常排列Logo：`letter-spacing="1-3"`

---

## 四、文字标（纯文字Logo）字体选择

### 4.1 中文文字标
| 风格 | 推荐字体 | 调性 |
|:----:|---------|:----:|
| 书法手写 | `STXingkai`, `ZCOOL KuaiLe`, `Ma Shan Zheng` | 人文、艺术、东方韵味 |
| 宋体精致 | `Noto Serif SC`, `STSong` | 高端、文化、经典 |
| 黑体现代 | `Noto Sans SC`, `PingFang SC` | 科技、简约、国际化 |
| 圆体亲和 | `Weibei SC`, `PingFang SC` | 亲民、温暖、可靠 |

### 4.2 英文文字标
| 风格 | 推荐字体 | 调性 |
|:----:|---------|:----:|
| 衬线经典 | `Georgia`, `Times New Roman`, `Playfair Display` | 奢华、传统、信赖 |
| 无衬线现代 | `Helvetica`, `Arial`, `Montserrat`, `Open Sans` | 现代、洁净、专业 |
| 手写优雅 | `Pacifico`, `Alex Brush`, `Great Vibes` | 优雅、艺术、独特 |
| 几何力量 | `Futura`, `Century Gothic`, `Avenir` | 建筑、科技、力量 |

---

## 五、字体搭配禁忌

| ❌ 不要这样做 | 原因 |
|-------------|------|
| 宋体+Helvetica | 中英笔画风格差异过大，不协调 |
| 颜体+Comic Sans | 一个厚重传统，一个轻佻随意 |
| 超过3种字体在同一Logo中 | 视觉混乱，缺乏统一感 |
| 书法体用于弧形文字 | 笔画变化大，弧形排列会影响辨识度 |
| 极细字体用于小尺寸 | 缩小后笔画丢失，不可识别 |

---

## 六、SVG中的字体声明写法

### 推荐写法（优先使用系统字体，逐级降级）
```svg
<!-- 中文 -->
font-family="'Noto Serif SC','Source Han Serif SC','SimSun','STSong',serif"

<!-- 英文 -->
font-family="'Georgia','Times New Roman',serif"

<!-- 现代无衬线 -->
font-family="'Noto Sans SC','PingFang SC','Microsoft YaHei',sans-serif"

<!-- 书法体 -->
font-family="'STXingkai','KaiTi',cursive"
```

**注意**：SVG中使用的字体取决于用户的系统安装情况。优先使用跨平台通用字体。
