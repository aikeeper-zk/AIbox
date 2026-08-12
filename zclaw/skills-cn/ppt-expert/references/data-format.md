# JSON数据格式规范

## 顶层结构

```json
{
  "title": "PPT标题",
  "subtitle": "副标题",
  "date": "日期",
  "slides": []
}
```

## slides数组支持的版式

### cover（封面）
```json
{"type": "cover", "title": "主标题", "subtitle": "副标题", "date": "日期"}
```

### toc（目录）
```json
{"type": "toc", "items": ["第一章名", "第二章名", "第三章名"]}
```

### section（章节页）
```json
{"type": "section", "number": "01", "title": "章节标题", "desc": "章节描述"}
```

### text（正文）
```json
{"type": "text", "title": "页面标题", "items": ["要点一", "要点二", "要点三"]}
```

### data（数据页）
```json
{"type": "data", "title": "标题", "metrics": [
  {"value": "数值", "label": "指标名"}
]}
```

### compare（对比页）
```json
{"type": "compare", "title": "对比标题", "old_title": "传统方案", "new_title": "新方案",
 "old_items": ["痛点一", "痛点二"], "new_items": ["优势一", "优势二"]}
```

### timeline（时间线）
```json
{"type": "timeline", "title": "标题", "items": [
  {"time": "时间段", "event": "事件描述"}
]}
```

### end（结尾页）
```json
{"type": "end", "text": "谢谢", "contact": "联系方式"}
```