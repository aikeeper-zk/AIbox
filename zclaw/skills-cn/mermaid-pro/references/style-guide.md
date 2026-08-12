# 样式指南（主题 / 配色 / 中文字体）

## 一、主题（render.sh 的 -t 参数）
| 主题 | 观感 | 适用 |
|---|---|---|
| `default` | 蓝白清爽 | 通用、文档 |
| `dark` | 深色背景 | 暗色 PPT、演示 |
| `forest` | 绿调 | 自然/生态主题 |
| `neutral` | 灰调中性 | 商务、打印 |

## 二、风格（look，写在 config.json）
- `classic`：标准几何风（默认，最专业）
- `handDrawn`：手绘风（轻松、草稿感）

## 三、中文字体（已配，沙箱实测可用）
- 系统已装 **Noto Serif CJK SC**（思源宋体）。
- `config.json` 中已设 `fontFamily` 与 `themeVariables.fontFamily`，渲染中文无需额外操作。
- 如需黑体（思源黑体），先 `apt-get install fonts-noto-cjk`（含 Sans），再改 config 的 fontFamily。

## 四、品牌色（可在 config.json 的 themeVariables 自定义）
当前默认一套蓝调：
```
primaryColor: #2563eb   主色（节点填充）
primaryTextColor: #ffffff
primaryBorderColor: #1e40af
lineColor: #475569      连线
secondaryColor: #e0f2fe
tertiaryColor: #f1f5f9
mainBkg: #eff6ff
```
> 把 `primaryColor` 换成智体共合品牌色即可一键统一视觉。

## 五、自定义 CSS（-C 参数，进阶）
可建 `style.css` 注入更细样式，例如：
```css
.node rect { rx: 8px; ry: 8px; }
```
调用：`bash scripts/render.sh -i x.mmd -o x.png -C style.css`

## 六、输出尺寸与清晰度
- PNG 默认缩放 `-s 2`（2 倍清晰度）。需要更高清用 `-s 3`。
- 指定画布：`scripts/render.sh -i x.mmd -o x.png -w 1920 -H 1080`
- 透明背景：在 render.sh 加 `-b transparent`（如需在 config 同层加 `-b` 参数）。
