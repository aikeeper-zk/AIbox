#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票深度投资研究报告 -> 独立 HTML 渲染器（零外部依赖）

用法:
    python build_report.py --md report.md --meta meta.json --out report.html

参数:
    --md    研报正文 Markdown（从“投资要点”章节开始，不含封面信息）
    --meta  封面/指标元数据 JSON（字段见 report-template.md）
    --out   输出 HTML 路径
    --title 可选，覆盖 meta.title

说明:
    - 解析常见 Markdown: 标题/段落/有序无序列表/表格(GFM)/引用/代码块/分隔线/
      加粗/斜体/行内代码/链接/图片。
    - 自动生成目录(基于标题)、评级徽章、指标卡、表格与风险告警样式。
    - 输出单文件 HTML，可直接浏览器打开或打印为 PDF。
"""

import argparse
import html
import json
import re
import sys


# --------------------------------------------------------------------------
# Markdown 解析
# --------------------------------------------------------------------------

def _inline(text: str) -> str:
    """对一段纯文本做行内格式化。先转义，再套标签。"""
    s = html.escape(text, quote=False)
    # 图片 ![alt](url)
    s = re.sub(r'!\[([^\]]*)\]\(([^)\s]+)\)',
               r'<img alt="\1" src="\2" class="inline-img">', s)
    # 链接 [text](url)
    s = re.sub(r'\[([^\]]+)\]\(([^)\s]+)\)',
               r'<a href="\2" target="_blank" rel="noopener">\1</a>', s)
    # 加粗 **x** / __x__
    s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
    s = re.sub(r'__(.+?)__', r'<strong>\1</strong>', s)
    # 斜体 *x* / _x_
    s = re.sub(r'(?<!\*)\*(?!\*)([^*\n]+?)\*(?!\*)', r'<em>\1</em>', s)
    # 行内代码 `x`
    s = re.sub(r'`([^`]+)`', r'<code>\1</code>', s)
    return s


def _split_row(line: str):
    s = line.strip()
    if s.startswith('|'):
        s = s[1:]
    if s.endswith('|'):
        s = s[:-1]
    return [c.strip() for c in s.split('|')]


def _is_block_start(line: str) -> bool:
    s = line.lstrip()
    if s.startswith('```') or s.startswith('#') or s.startswith('>') \
       or s.startswith('- ') or s.startswith('* ') or s.startswith('+ ') \
       or re.match(r'^\d+\.\s', s) or re.match(r'^[-*_]\1{2,}\s*$', s) \
       or '|' in line and '-' in line:
        return True
    return False


def _render_table(header, rows):
    th = ''.join(f'<th>{_inline(h)}</th>' for h in header)
    body = ''
    for r in rows:
        cells = (r + [''] * len(header))[:len(header)]
        body += '<tr>' + ''.join(f'<td>{_inline(c)}</td>' for c in cells) + '</tr>'
    return f'<table class="rpt"><thead><tr>{th}</tr></thead><tbody>{body}</tbody></table>'


def md_to_html(md: str):
    lines = md.replace('\r\n', '\n').split('\n')
    out = []
    toc = []
    i, n = 0, len(lines)
    while i < n:
        line = lines[i]
        # 代码块
        if line.strip().startswith('```'):
            i += 1
            buf = []
            while i < n and not lines[i].strip().startswith('```'):
                buf.append(lines[i])
                i += 1
            i += 1
            code = html.escape('\n'.join(buf))
            out.append(f'<pre class="code"><code>{code}</code></pre>')
            continue
        # 表格
        if '|' in line and i + 1 < n and re.match(r'^\s*\|?[\s:|-]+\|?\s*$', lines[i + 1]) \
           and '-' in lines[i + 1]:
            header = _split_row(line)
            i += 2
            rows = []
            while i < n and lines[i].strip() and '|' in lines[i]:
                rows.append(_split_row(lines[i]))
                i += 1
            out.append(_render_table(header, rows))
            continue
        # 标题
        m = re.match(r'^(#{1,6})\s+(.*)$', line)
        if m:
            level = len(m.group(1))
            raw = m.group(2).strip()
            anchor = re.sub(r'[^a-z0-9\u4e00-\u9fff]+', '-', raw.lower()).strip('-')
            out.append(f'<h{level} id="{anchor}">{_inline(raw)}</h{level}>')
            if level <= 3:
                toc.append((level, raw, anchor))
            i += 1
            continue
        # 分隔线
        if re.match(r'^\s*([-*_])\1{2,}\s*$', line):
            out.append('<hr>')
            i += 1
            continue
        # 引用
        if line.lstrip().startswith('>'):
            buf = []
            while i < n and lines[i].lstrip().startswith('>'):
                buf.append(lines[i].lstrip()[1:].strip())
                i += 1
            out.append(f'<blockquote>{_inline(" ".join(buf))}</blockquote>')
            continue
        # 无序列表
        if re.match(r'^\s*[-*+]\s+', line):
            buf = []
            while i < n and re.match(r'^\s*[-*+]\s+', lines[i]):
                item = re.sub(r'^\s*[-*+]\s+', '', lines[i])
                buf.append(f'<li>{_inline(item)}</li>')
                i += 1
            out.append('<ul>' + ''.join(buf) + '</ul>')
            continue
        # 有序列表
        if re.match(r'^\s*\d+\.\s+', line):
            buf = []
            while i < n and re.match(r'^\s*\d+\.\s+', lines[i]):
                item = re.sub(r'^\s*\d+\.\s+', '', lines[i])
                buf.append(f'<li>{_inline(item)}</li>')
                i += 1
            out.append('<ol>' + ''.join(buf) + '</ol>')
            continue
        # 空行
        if not line.strip():
            i += 1
            continue
        # 段落
        buf = [line]
        i += 1
        while i < n and lines[i].strip() and not _is_block_start(lines[i]):
            buf.append(lines[i])
            i += 1
        out.append(f'<p>{_inline(" ".join(buf))}</p>')
    return '\n'.join(out), toc


# --------------------------------------------------------------------------
# 封面 / 元数据
# --------------------------------------------------------------------------

def _rating_color(rating: str) -> str:
    r = rating or ''
    if any(k in r for k in ('强烈推荐', '买入')):
        return '#c0392b'          # 红（涨）
    if any(k in r for k in ('增持', '推荐', '审慎推荐')):
        return '#e67e22'          # 橙
    if any(k in r for k in ('中性', '持有', '观望')):
        return '#7f8c8d'          # 灰
    if any(k in r for k in ('减持', '卖出', '回避', '强烈回避')):
        return '#1e8449'          # 绿（跌）
    return '#2c3e50'


def build_cover(meta: dict) -> str:
    rating = meta.get('rating', '—')
    color = _rating_color(rating)
    metrics = meta.get('metrics', [])
    cards = ''
    for m in metrics:
        note = m.get('note', '')
        cards += (
            f'<div class="metric"><div class="m-label">{html.escape(m.get("label",""))}</div>'
            f'<div class="m-value">{html.escape(str(m.get("value","")))}</div>'
            f'<div class="m-note">{html.escape(note)}</div></div>'
        )
    summary = meta.get('summary', '')
    sub = []
    if meta.get('ticker'):
        sub.append(html.escape(meta['ticker']))
    if meta.get('market'):
        sub.append(html.escape(meta['market']))
    if meta.get('industry'):
        sub.append(html.escape(meta['industry']))
    sub_html = ' · '.join(sub)

    price_line = ''
    if meta.get('current_price') or meta.get('target_price'):
        price_line = (
            f'<div class="price-line">'
            f'<span class="pl"><span class="pl-k">当前价</span> {html.escape(str(meta.get("current_price","")))}</span>'
            f'<span class="pl"><span class="pl-k">目标价</span> {html.escape(str(meta.get("target_price","")))}</span>'
            f'<span class="pl"><span class="pl-k">预期空间</span> {html.escape(str(meta.get("upside","")))}</span>'
            f'</div>'
        )

    return f'''
<header class="cover">
  <div class="cover-top">
    <div>
      <div class="badge" style="background:{color}">{html.escape(rating)}</div>
      <h1 class="cover-title">{html.escape(meta.get('company', meta.get('title', '股票研究报告')))}</h1>
      <div class="cover-sub">{sub_html}</div>
    </div>
  </div>
  {price_line}
  <div class="metrics">{cards}</div>
  {('<div class="summary">' + html.escape(summary) + '</div>') if summary else ''}
  <div class="cover-foot">
    <span>分析师：{html.escape(str(meta.get('analyst', '—')))}</span>
    <span>报告日期：{html.escape(str(meta.get('date', '—')))}</span>
  </div>
</header>'''


def build_toc(toc) -> str:
    if not toc:
        return ''
    items = []
    for level, raw, anchor in toc:
        indent = ' style="padding-left:%dpx"' % ((level - 1) * 16) if level > 1 else ''
        items.append(f'<li{indent}><a href="#{anchor}">{html.escape(raw)}</a></li>')
    return '<nav class="toc"><div class="toc-title">目录</div><ul>' + ''.join(items) + '</ul></nav>'


CSS = """
:root{
  --ink:#1f2933; --muted:#6b7280; --line:#e5e7eb; --bg:#ffffff;
  --accent:#c0392b; --soft:#f7f8fa; --code-bg:#f3f4f6;
}
*{box-sizing:border-box;}
body{
  margin:0; background:#eef0f3; color:var(--ink);
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif;
  line-height:1.75; font-size:15px;
}
.wrap{max-width:920px; margin:0 auto; background:var(--bg); padding:0 0 56px;}
.cover{
  background:linear-gradient(135deg,#1f2933 0%,#2c3e50 60%,#34495e 100%);
  color:#fff; padding:40px 48px 32px;
}
.badge{display:inline-block; color:#fff; font-weight:700; font-size:14px;
  padding:4px 14px; border-radius:999px; letter-spacing:1px;}
.cover-title{font-size:34px; margin:14px 0 6px; font-weight:800; letter-spacing:.5px;}
.cover-sub{color:#cbd5e1; font-size:14px;}
.price-line{display:flex; gap:28px; margin:22px 0 6px; flex-wrap:wrap;}
.pl{display:flex; flex-direction:column;}
.pl-k{font-size:12px; color:#cbd5e1;}
.pl{font-size:20px; font-weight:700;}
.metrics{display:grid; grid-template-columns:repeat(auto-fit,minmax(140px,1fr)); gap:12px; margin:18px 0 6px;}
.metric{background:rgba(255,255,255,.08); border:1px solid rgba(255,255,255,.16);
  border-radius:10px; padding:12px 14px;}
.m-label{font-size:12px; color:#cbd5e1;}
.m-value{font-size:19px; font-weight:700; margin:2px 0;}
.m-note{font-size:11px; color:#aeb9c7;}
.summary{margin-top:16px; background:rgba(255,255,255,.07); border-left:3px solid #e2b607;
  padding:12px 16px; border-radius:6px; font-size:14px; color:#eef2f7;}
.cover-foot{display:flex; justify-content:space-between; margin-top:20px; font-size:12px; color:#aeb9c7;}
.content{padding:32px 48px;}
.toc{background:var(--soft); border:1px solid var(--line); border-radius:10px;
  padding:14px 20px; margin:0 0 28px;}
.toc-title{font-weight:700; margin-bottom:8px; color:var(--muted); font-size:13px;}
.toc ul{list-style:none; margin:0; padding:0;}
.toc li{margin:4px 0;}
.toc a{color:#34495e; text-decoration:none; font-size:14px;}
.toc a:hover{color:var(--accent);}
h1,h2,h3,h4{color:#1f2933; line-height:1.3; margin:32px 0 12px;}
h2{border-left:4px solid var(--accent); padding-left:12px; font-size:22px;}
h3{font-size:18px; margin-top:24px;}
p{margin:12px 0;}
ul,ol{padding-left:24px; margin:12px 0;}
li{margin:6px 0;}
table.rpt{border-collapse:collapse; width:100%; margin:16px 0; font-size:14px;}
table.rpt th,table.rpt td{border:1px solid var(--line); padding:8px 12px; text-align:left;}
table.rpt thead th{background:var(--soft); font-weight:700;}
table.rpt tbody tr:nth-child(even){background:#fcfcfd;}
blockquote{background:var(--soft); border-left:4px solid #b0b8c1; margin:14px 0;
  padding:10px 16px; color:#374151; border-radius:0 6px 6px 0;}
pre.code{background:var(--code-bg); border:1px solid var(--line); border-radius:8px;
  padding:14px 16px; overflow:auto; font-size:13px;}
pre.code code{font-family:"SFMono-Regular",Consolas,"Liberation Mono",monospace; color:#222;}
code{background:var(--code-bg); padding:2px 6px; border-radius:4px; font-size:13px;
  font-family:"SFMono-Regular",Consolas,monospace;}
hr{border:none; border-top:1px solid var(--line); margin:28px 0;}
.inline-img{max-width:100%; border-radius:8px; margin:12px 0;}
a{color:var(--accent);}
.footer-note{margin:32px 48px 0; padding-top:16px; border-top:1px solid var(--line);
  color:var(--muted); font-size:12px;}
@media print{
  body{background:#fff;}
  .wrap{max-width:none;}
  .toc{break-after:page;}
}
"""


def render(md_text: str, meta: dict) -> str:
    body_html, toc = md_to_html(md_text)
    toc_html = build_toc(toc)
    cover_html = build_cover(meta)
    title = meta.get('title', meta.get('company', '股票研究报告'))
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<style>{CSS}</style>
</head>
<body>
<div class="wrap">
{cover_html}
<div class="content">
{toc_html}
{body_html}
</div>
</div>
</body>
</html>"""


def main():
    ap = argparse.ArgumentParser(description="股票研报 Markdown -> 独立 HTML 渲染器")
    ap.add_argument('--md', required=True, help='研报正文 Markdown 路径')
    ap.add_argument('--meta', required=True, help='封面/指标元数据 JSON 路径')
    ap.add_argument('--out', required=True, help='输出 HTML 路径')
    ap.add_argument('--title', default=None, help='可选，覆盖标题')
    args = ap.parse_args()

    try:
        with open(args.md, 'r', encoding='utf-8') as f:
            md_text = f.read()
        with open(args.meta, 'r', encoding='utf-8') as f:
            meta = json.load(f)
    except Exception as e:
        print(f"[错误] 读取输入失败: {e}", file=sys.stderr)
        sys.exit(1)

    if args.title:
        meta['title'] = args.title

    html_out = render(md_text, meta)
    try:
        with open(args.out, 'w', encoding='utf-8') as f:
            f.write(html_out)
    except Exception as e:
        print(f"[错误] 写入输出失败: {e}", file=sys.stderr)
        sys.exit(1)
    print(f"[完成] 已生成 HTML: {args.out}")


if __name__ == '__main__':
    main()
