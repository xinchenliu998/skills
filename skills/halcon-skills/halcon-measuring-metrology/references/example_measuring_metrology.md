# Halcon 1D测量与2D计量技能手册

> 学习来源: `Measuring/`, `Metrology/`
> 涵盖Task13：1D边缘测量、2D计量模型

---

## 一、测量方法对比

| 方法 | 算子 | 维度 | 精度 | 适用 |
|---|---|---|---|---|
| **1D Measuring** ⭐ | `measure_pos/pairs` | 1D投影 | 亚像素 | ⭐引脚宽度/间距/边缘位置 |
| **2D Metrology** ⭐ | `create_metrology_model` | 2D拟合 | 亚像素 | ⭐几何尺寸(圆/线/矩形) |
| XLD拟合 | `fit_circle/line` | 2D | 亚像素 | 轮廓级拟合(Task06) |

---

## 二、1D Measuring 边缘测量 ⭐

### 完整流程
```
1. gen_measure_rectangle2 → 创建测量矩形(定义测量方向和范围)
2. measure_pos → 测量边缘位置(单边缘)
   或 measure_pairs → 测量边缘对(宽度)
3. close_measure → 释放
```

### 核心算子

#### gen_measure_rectangle2 — 创建测量矩形
```
gen_measure_rectangle2(Row, Column, Phi, Length1, Length2, Width, Height, Interpolation, MeasureHandle)
```
| 参数 | 说明 |
|---|---|
| Row, Column | 矩形中心 |
| Phi | 旋转角度(rad), 测量方向=Phi方向 |
| Length1 | 沿测量方向半长 |
| Length2 | 垂直方向半宽(投影宽度) |
| Interpolation | `'nearest_neighbor'`/`'bilinear'` |

#### measure_pos — 测量边缘位置
```
measure_pos(Image, MeasureHandle, Sigma, Threshold, Transition, Select,
            RowEdge, ColEdge, Amplitude, Distance)
```
| 参数 | 典型值 | 说明 |
|---|---|---|
| Sigma | 1.0 | 高斯平滑 |
| Threshold | 30 | 边缘阈值 |
| Transition | `'all'`/`'positive'`/`'negative'` | 边缘方向 |
| Select | `'all'`/`'first'`/`'last'` | 选择边缘 |

#### measure_pairs — 测量边缘对（宽度）
```
measure_pairs(Image, MeasureHandle, Sigma, Threshold, Transition, Select,
              RowEdgeFirst, ColEdgeFirst, AmplFirst, RowEdgeSec, ColEdgeSec, AmplSec, 
              IntraDistance, InterDistance)
```
- **IntraDistance**: 边缘对内距离=物体宽度 ⭐
- **InterDistance**: 边缘对间距离=物体间距

---

## 三、2D Metrology 计量模型 ⭐

### 完整流程
```
1. create_metrology_model → 创建计量模型
2. set_metrology_model_image_size → 设置图像尺寸
3. add_metrology_object_circle_measure → 添加圆测量对象
   或 add_metrology_object_line_measure → 添加线测量
   或 add_metrology_object_rectangle2_measure → 添加矩形测量
   或 add_metrology_object_ellipse_measure → 添加椭圆测量
4. apply_metrology_model → 执行测量
5. get_metrology_object_result → 获取结果
6. clear_metrology_model → 释放
```

### 核心算子

#### add_metrology_object_circle_measure — 添加圆测量
```
add_metrology_object_circle_measure(MetrologyHandle, Row, Column, Radius,
    MeasureLength1, MeasureLength2, MeasureSigma, MeasureThreshold,
    GenParamName, GenParamValue, Index)
```

#### apply_metrology_model — 执行测量
```
apply_metrology_model(Image, MetrologyHandle)
```

#### get_metrology_object_result — 获取结果
```
get_metrology_object_result(MetrologyHandle, Index, Instance, GenParamName, GenParamValue)
```
- GenParamName: `'result_type'` → `'all_param'`/`'row'`/`'column'`/`'radius'`

---

## 四、测量策略决策树

```
测量需求
├─ 测量边缘位置/间距？
│   └─ 1D Measuring: gen_measure_rectangle2 → measure_pos ⭐
├─ 测量物体宽度(边缘对)？
│   └─ 1D Measuring: measure_pairs → IntraDistance ⭐
├─ 精确圆尺寸？
│   └─ 2D Metrology: add_circle_measure → apply → get_result ⭐
├─ 精确线段位置？
│   └─ 2D Metrology: add_line_measure
├─ 多个几何形状同时测量？
│   └─ 2D Metrology(一个模型添加多个对象)
└─ 背光小孔直径？
    └─ 方案1: fit_circle_contour_xld (Task06)
    └─ 方案2: 2D Metrology circle ⭐
```

---

## 五、C# HalconDotNet 代码模板

### 模板1: 1D边缘测量 ⭐
```csharp
HObject image;
HTuple measureHandle, rowEdge, colEdge, amplitude, distance;

HOperatorSet.ReadImage(out image, imagePath);
HTuple width, height;
HOperatorSet.GetImageSize(image, out width, out height);

// 创建测量矩形(中心300,400, 水平方向, 半长100, 半宽20)
HOperatorSet.GenMeasureRectangle2(300, 400, 0, 100, 20, width, height, "bilinear", out measureHandle);

// 测量边缘
HOperatorSet.MeasurePos(image, measureHandle, 1.0, 30, "all", "all",
    out rowEdge, out colEdge, out amplitude, out distance);

for (int i = 0; i < rowEdge.Length; i++)
    Console.WriteLine($"边缘{i+1}: ({rowEdge[i].D:F1},{colEdge[i].D:F1}), 幅值={amplitude[i].D:F1}");

HOperatorSet.CloseMeasure(measureHandle);
image.Dispose();
```

### 模板2: 1D宽度测量(边缘对)
```csharp
HTuple rowFirst, colFirst, amplFirst, rowSec, colSec, amplSec, intra, inter;

HOperatorSet.MeasurePairs(image, measureHandle, 1.0, 30, "positive", "all",
    out rowFirst, out colFirst, out amplFirst,
    out rowSec, out colSec, out amplSec,
    out intra, out inter);

for (int i = 0; i < intra.Length; i++)
    Console.WriteLine($"物体{i+1}: 宽度={intra[i].D:F1}px, 间距={inter[i].D:F1}px");
```

### 模板3: 2D计量圆测量 ⭐
```csharp
HObject image;
HTuple metroHandle, circleIdx;

HOperatorSet.ReadImage(out image, imagePath);
HTuple width, height;
HOperatorSet.GetImageSize(image, out width, out height);

// 创建计量模型
HOperatorSet.CreateMetrologyModel(out metroHandle);
HOperatorSet.SetMetrologyModelImageSize(metroHandle, width, height);

// 添加圆测量(初始圆心300,400, 半径50)
HOperatorSet.AddMetrologyObjectCircleMeasure(metroHandle, 300, 400, 50,
    20, 5, 1.0, 30, new HTuple(), new HTuple(), out circleIdx);

// 执行测量
HOperatorSet.ApplyMetrologyModel(image, metroHandle);

// 获取结果
HTuple resultRow, resultCol, resultRadius;
HOperatorSet.GetMetrologyObjectResult(metroHandle, circleIdx, "all", "result_type", "row", out resultRow);
HOperatorSet.GetMetrologyObjectResult(metroHandle, circleIdx, "all", "result_type", "column", out resultCol);
HOperatorSet.GetMetrologyObjectResult(metroHandle, circleIdx, "all", "result_type", "radius", out resultRadius);

Console.WriteLine($"圆: 中心=({resultRow.D:F2},{resultCol.D:F2}), 半径={resultRadius.D:F2}px");

HOperatorSet.ClearMetrologyModel(metroHandle);
image.Dispose();
```
