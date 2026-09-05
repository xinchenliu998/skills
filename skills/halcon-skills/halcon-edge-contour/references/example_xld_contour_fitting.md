# Halcon XLD轮廓拟合与操作技能手册

> 学习来源: `XLD/Features/`, `XLD/Contour/`, `Filters/Contour/`
> 涵盖Task06+Task07：轮廓拟合(圆/椭圆/直线)、轮廓操作(分割/合并/选择)

---

## 一、XLD轮廓拟合算子对比表

| 算子 | 拟合目标 | 输出 | 精度 | ⭐场景 |
|---|---|---|---|---|
| **fit_circle_contour_xld** ⭐ | 圆 | Row,Col,Radius | 亚像素 | ⭐圆孔/圆柱检测 |
| **fit_ellipse_contour_xld** | 椭圆 | Row,Col,Phi,Ra,Rb | 亚像素 | 椭圆形目标 |
| **fit_line_contour_xld** | 直线 | RowB,ColB,RowE,ColE | 亚像素 | 直线边缘 |
| **fit_rectangle2_contour_xld** | 矩形 | Row,Col,Phi,L1,L2 | 亚像素 | 矩形目标 |

---

## 二、XLD轮廓拟合详解

### fit_circle_contour_xld ⭐ — 圆拟合
```
fit_circle_contour_xld(Contours, Algorithm, MaxNumPoints, MaxClosureDist, 
                        ClippingEndPoints, Iterations, ClippingFactor,
                        Row, Column, Radius, StartPhi, EndPhi, PointOrder)
```
**关键参数:**
| 参数 | 值 | 说明 |
|---|---|---|
| Algorithm | `'atukey'`⭐/`'algebraic'`/`'geometric'` | 拟合算法(atukey鲁棒) |
| MaxNumPoints | -1 | 最大点数(-1=全部) |
| MaxClosureDist | 0 | 最大闭合距离 |
| ClippingEndPoints | 0 | 裁剪端点数 |
| Iterations | 3 | 迭代次数 |
| ClippingFactor | 2.0 | 异常值裁剪系数 |

**Algorithm选择:**
- `'algebraic'`: 最快，适合无噪声
- `'atukey'`⭐: 鲁棒拟合，自动排除异常点
- `'geometric'`: 最精确但最慢

### fit_ellipse_contour_xld — 椭圆拟合
```
fit_ellipse_contour_xld(Contours, Algorithm, MaxNumPoints, MaxClosureDist,
                         ClippingEndPoints, VossTabSize, Iterations, ClippingFactor,
                         Row, Column, Phi, Radius1, Radius2, StartPhi, EndPhi, PointOrder)
```

### fit_line_contour_xld — 直线拟合
```
fit_line_contour_xld(Contours, Algorithm, MaxNumPoints, ClippingEndPoints, 
                      Iterations, ClippingFactor,
                      RowBegin, ColBegin, RowEnd, ColEnd, Nr, Nc, Dist)
```

---

## 三、XLD轮廓操作算子

### 轮廓生成
| 算子 | 功能 |
|---|---|
| `edges_sub_pix` | 亚像素边缘→XLD |
| `threshold_sub_pix` | 亚像素阈值→XLD |
| `gen_contour_polygon_xld` | 点序列→XLD |
| `gen_circle_contour_xld` | 圆参数→XLD |
| `gen_ellipse_contour_xld` | 椭圆参数→XLD |

### 轮廓处理
| 算子 | 功能 | ⭐场景 |
|---|---|---|
| `segment_contours_xld` ⭐ | 分割为直线/圆弧段 | 复杂轮廓分析 |
| `union_adjacent_contours_xld` | 合并相邻轮廓 | 断开轮廓修复 |
| `union_collinear_contours_xld` | 合并共线轮廓 | 直线段合并 |
| `smooth_contours_xld` | 平滑轮廓 | 降噪 |
| `close_contours_xld` | 闭合轮廓 | 轮廓闭合 |
| `clip_contours_xld` | 裁剪轮廓 | ROI限制 |
| `select_contours_xld` | 按长度/开闭选择 | 过滤 |
| `select_shape_xld` | 按形状特征选择 | ⭐特征筛选 |

### 轮廓特征
| 算子 | 输出 |
|---|---|
| `contour_point_num_xld` | 点数 |
| `length_xld` | 轮廓长度 |
| `area_center_xld` | 面积和中心 |
| `circularity_xld` | 圆度 |
| `eccentricity_xld` | 离心率 |
| `compactness_xld` | 紧凑度 |
| `moments_xld` | 矩 |
| `get_contour_xld` | 获取轮廓点坐标 |
| `get_contour_attrib_xld` | 获取轮廓属性(角度/宽度) |

### segment_contours_xld ⭐ — 轮廓分割
```
segment_contours_xld(Contours, ContoursSplit, Mode, SmoothCont, MaxLineDist1, MaxLineDist2)
```
- **Mode**: `'lines'`直线段 / `'lines_circles'`直线+圆弧
- 将复杂轮廓分割为几何基元→逐段拟合

---

## 四、XLD工作流决策树

```
XLD轮廓任务
├─ 需要亚像素边缘？
│   └─ edges_sub_pix → XLD轮廓
├─ 拟合圆？
│   ├─ 完整圆 → fit_circle_contour_xld('atukey') ⭐
│   └─ 部分弧 → fit_circle_contour_xld + MaxClosureDist
├─ 拟合椭圆？
│   └─ fit_ellipse_contour_xld
├─ 拟合直线？
│   └─ fit_line_contour_xld
├─ 复杂形状？
│   └─ segment_contours_xld → 分段 → 逐段拟合
├─ 轮廓断开？
│   └─ union_adjacent_contours_xld → 合并
└─ 背光小孔圆拟合？ ⭐
    └─ edges_sub_pix → select_shape_xld(长度) → fit_circle_contour_xld('atukey')
```

---

## 五、C# HalconDotNet 代码模板

### 模板1: 亚像素圆拟合 ⭐⭐
```csharp
HObject image, edges;
HTuple row, col, radius, startPhi, endPhi, pointOrder;

HOperatorSet.ReadImage(out image, imagePath);
// 亚像素边缘提取
HOperatorSet.EdgesSubPix(image, out edges, "canny", 1.0, 20, 40);
// 圆拟合(鲁棒算法)
HOperatorSet.FitCircleContourXld(edges, "atukey", -1, 0, 0, 3, 2.0,
    out row, out col, out radius, out startPhi, out endPhi, out pointOrder);

for (int i = 0; i < row.Length; i++)
    Console.WriteLine($"圆{i+1}: 中心=({row[i].D:F2},{col[i].D:F2}), 半径={radius[i].D:F2}");

edges.Dispose(); image.Dispose();
```

### 模板2: 轮廓分割+逐段拟合
```csharp
HObject image, edges, segments;

HOperatorSet.ReadImage(out image, imagePath);
HOperatorSet.EdgesSubPix(image, out edges, "canny", 1.0, 20, 40);
// 分割为直线和圆弧
HOperatorSet.SegmentContoursXld(edges, out segments, "lines_circles", 5, 4, 2);

HTuple count;
HOperatorSet.CountObj(segments, out count);
for (int i = 1; i <= count.I; i++)
{
    HObject seg;
    HOperatorSet.SelectObj(segments, out seg, i);
    HTuple type;
    HOperatorSet.GetContourGlobalAttribXld(seg, "cont_approx", out type);
    // type: 1=直线, 2=圆弧, 3=椭圆弧
    Console.WriteLine($"段{i}: 类型={type.I}");
    seg.Dispose();
}
segments.Dispose(); edges.Dispose(); image.Dispose();
```

### 模板3: 断开轮廓合并
```csharp
HObject image, edges, merged;

HOperatorSet.ReadImage(out image, imagePath);
HOperatorSet.EdgesSubPix(image, out edges, "canny", 1.0, 20, 40);
// 合并相邻轮廓(最大间距10px, 最大角度0.2rad)
HOperatorSet.UnionAdjacentContoursXld(edges, out merged, 10, 1, "attr_keep");

merged.Dispose(); edges.Dispose(); image.Dispose();
```

### 模板4: XLD特征筛选
```csharp
HObject image, edges, selected;

HOperatorSet.ReadImage(out image, imagePath);
HOperatorSet.EdgesSubPix(image, out edges, "canny", 1.0, 20, 40);
// 按长度筛选(>50像素)
HOperatorSet.SelectContoursXld(edges, out selected, "contour_length", 50, 9999, -0.5, 0.5);

selected.Dispose(); edges.Dispose(); image.Dispose();
```
