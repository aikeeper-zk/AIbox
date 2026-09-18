# 项目长期记忆

## 项目概况
- 本仓库是「智体共合」官网静态站点（纯 HTML + 内联 CSS/JS，无构建步骤）。
- **官网域名：594agent.com**（页脚、联系页、canonical 均以此为准）。另一个域名 594fast.com 若仍在使用，涉及根目录文件（llms.txt/robots.txt/sitemap.xml）需同步部署。
- 公司主体：智体共合科技（无锡）有限公司，注册地江苏省无锡市，商务邮箱 shangwu@594agent.com，微信公众号「智体共合」，开源仓库 github.com/aikeeper-zk/AIbox，领衔人陆鑫。
- 三大核心承诺：数据不出门 · 断网不停机 · 买断无订阅。
- 页面结构：12 个 html —— index（首页）、about、ai-box、udisk、hdd、openclaw、digital-human、computing-network、federation、lingxia-platform、business、contact。
- 关键价格：小龙虾AI盒子 Lite ¥8,999 / Pro ¥16,999 / Enterprise 面议；龙虾U盘 ¥999；SaaS ¥299/月/台。

## 约定与注意事项
- 全站全局 CSS 有 `img { max-width:100%; display:block; }`，图片若要与文字同行，需显式覆盖为 `display:inline-block;`。
- 页脚备案区固定两行：苏ICP备2026056933号-1、苏公网安备32021402005064号（公安备案图标 beian.png 在前、编号紧随，用 inline-flex 对齐 + 2px 间距）。
- 12 个页面的页脚内容需保持同步，改动时务必全量修改。
- JSON-LD 内联在 `</style>` 与 `</head>` 之间；JSON 字符串内禁止出现未转义的 ASCII 双引号，中文用「」代替。

## SEO / GEO（2026-09-18 建立）
- 已完成：llms.txt、robots.txt（放行 AI 爬虫）、sitemap.xml、12 页完整 meta（description/keywords/canonical/OG/Twitter）、12 页 JSON-LD（Organization + 产品/页面 + Breadcrumb + FAQPage）、首页与 ai-box.html 可见 FAQ 模块。
- 实体一致性写法：产品表述统一带品牌前缀「智体共合·小龙虾AI盒子」，用于与 OpenClaw 及其他厂商「龙虾盒」区分。
- 仍在推进：百度百科词条、内容投放（头条/知乎/百家号）、媒体背书、平台实测数据采集。
