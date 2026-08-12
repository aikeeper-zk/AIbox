# Draw.io XML 规范速查

## 文件结构
```xml
<?xml version="1.0" encoding="UTF-8"?>
<mxfile host="..." modified="..." agent="..." version="24.7.6" etag="..." type="device">
  <diagram name="图表名" id="...">
    <mxGraphModel dx="0" dy="0" grid="1" gridSize="10" ...>
      <root>
        <mxCell id="0" />                          <!-- 根 cell，必需 -->
        <mxCell id="1" parent="0" />               <!-- 默认父 cell，必需 -->
        <!-- 节点、连线... -->
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

## 节点（vertex）
```xml
<mxCell id="2" value="标签文字" style="..." vertex="1" parent="1">
  <mxGeometry x="40" y="40" width="120" height="40" as="geometry" />
</mxCell>
```

## 连线（edge）
```xml
<mxCell id="3" value="标签" style="..." edge="1" parent="1" source="2" target="4">
  <mxGeometry relative="1" as="geometry" />
</mxCell>
```

## 常用样式
| 样式 | 效果 |
|---|---|
| `rounded=1;whiteSpace=wrap;html=1;` | 圆角矩形 |
| `ellipse;whiteSpace=wrap;html=1;` | 椭圆 |
| `rhombus;whiteSpace=wrap;html=1;` | 菱形 |
| `shape=cylinder;whiteSpace=wrap;html=1;` | 圆柱 |
| `shape=process;whiteSpace=wrap;html=1;` | 流程框 |
| `edgeStyle=orthogonalEdgeStyle;` | 正交折线 |
| `edgeStyle=curved;` | 曲线 |
| `fillColor=#2563eb;strokeColor=#1e40af;fontColor=#ffffff;` | 配色 |
