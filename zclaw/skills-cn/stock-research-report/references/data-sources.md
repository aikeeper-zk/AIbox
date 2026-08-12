# 数据采集来源映射

本文件将研报所需的数据需求映射到可用的数据获取能力。优先使用已连接 / 可调用的金融数据 skill，必要时用联网搜索补充。所有取数务必记录口径（时点、币种、单位）。

## 可用数据能力

| 能力 | 调用方式 | 主要覆盖 |
| --- | --- | --- |
| `westock-data` | 调用 westock-data skill | 行情、财务、研报、新闻、公告、股东、分红、行业、宏观等结构化数据（A/H/US/日韩股、ETF、指数、板块、期货、外汇、可转债） |
| `wb-finance-skill` | 调用 wb-finance-skill skill | 金融场景总入口（行情、财报、估值、持仓、资讯、预警等） |
| `neodata-financial-search` | 调用 neodata-financial-search skill | 自然语言金融数据检索（股票 / 基金 / 指数 / 行业 / 宏观 / 外汇 / 大宗商品） |
| `westock-tool` | 调用 westock-tool skill | 选股 / 选基、条件筛选、排行榜、同业对比样本选取 |
| WebSearch / WebFetch | 联网搜索 | 最新新闻、行业政策、公司官网、招股书 / 年报原文、卖方研报观点 |

> 具体 skill 的参数与返回结构以各 skill 自身的说明为准；本文件只负责“要什么 → 找谁要”的映射。

## 需求 → 来源 映射

| 数据需求 | 首选来源 | 备选 / 补充 |
| --- | --- | --- |
| 实时 / 最新行情、现价、市值、52 周高低 | `westock-data`（行情） | `wb-finance-skill` |
| 估值指标 PE/PB/PS/股息率 | `westock-data`（估值/行情） | `neodata-financial-search` |
| 历史财务（三张表、毛利率/净利率/ROE/负债率/现金流） | `westock-data`（财务/财报） | `wb-finance-skill`、`neodata-financial-search` |
| 一致预期（未来 2–3 年 EPS、增速） | `westock-data`（盈利预测 / 研报） | 卖方研报汇总 |
| 行业空间、增速、竞争格局、政策 | `westock-data`（行业） + WebSearch | `neodata-financial-search`（行业） |
| 同业可比公司样本 | `westock-tool`（按行业 / 条件筛选） | `westock-data`（板块成分） |
| 重大公告、分红、回购 | `westock-data`（公告 / 分红） | 交易所公告原文（WebFetch） |
| 股东、机构持仓、高管增减持 | `westock-data`（股东 / 持仓） | — |
| 近期新闻、舆情、卖方观点 | `westock-data`（新闻 / 研报） + WebSearch | `neodata-financial-search` |
| 宏观与利率环境（用于 DCF 折现率） | `neodata-financial-search`（宏观） | WebSearch |

## 取数纪律

1. 先确定标的代码与市场，再取数；同业对比时统一口径（同一货币、同一报告期）。
2. 财报数据以最新披露定期报告为准，注明报告期（如“2025 年报 / 2026Q1”）。
3. 估值倍数用最新收盘日口径，与目标价推算保持时点一致。
4. 任何数值都要能回溯到来源；在报告表格下加“数据来源”脚注。
5. 数据缺失时写“N/A”，不要插值或估算后假装精确。
