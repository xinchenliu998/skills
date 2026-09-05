# Halcon NCC匹配与变形匹配技能手册

> 学习来源: `Matching/Correlation-Based/`, `Matching/Deformable/`
> 涵盖Task12：NCC相关匹配、局部变形匹配、平面变形匹配

---

## 一、匹配方法对比（含Task11形状匹配）

| 方法 | 基于 | 旋转 | 缩放 | 变形 | 速度 | 遮挡鲁棒 | ⭐场景 |
|---|---|---|---|---|---|---|---|
| Shape-Based ⭐ | 边缘梯度 | ✅ | ✅ | ❌ | 最快 | ✅好 | ⭐标准定位 |
| **NCC** | 灰度相关 | ✅ | ❌ | ❌ | 快 | ❌差 | 纹理丰富/低对比度 |
| **Local Deformable** | 边缘+变形 | ✅ | ✅ | ✅局部 | 慢 | ✅ | 柔性物体(包装袋等) |
| **Planar Deformable** | 边缘+透视 | ✅ | ✅ | ✅透视 | 中 | ✅ | 平面目标透视变换 |

---

## 二、NCC相关匹配

### 完整流程
```
1. create_ncc_model(Template, NumLevels, AngleStart, AngleExtent, AngleStep, Metric, ModelID)
2. find_ncc_model(Image, ModelID, AngleStart, AngleExtent, MinScore, NumMatches, MaxOverlap, SubPixel, NumLevels, Row, Col, Angle, Score)
3. clear_ncc_model(ModelID)
```

### 核心算子
| 算子 | 功能 |
|---|---|
| `create_ncc_model` | 创建NCC模型 |
| `find_ncc_model` | 搜索匹配 |
| `write/read_ncc_model` | 保存/加载 |
| `clear_ncc_model` | 释放 |

### vs Shape-Based 选择
| 条件 | 选择 |
|---|---|
| 有清晰边缘 | Shape-Based ⭐ |
| 纹理丰富但边缘不清 | NCC |
| 有部分遮挡 | Shape-Based |
| 光照变化大 | NCC(Metric='use_polarity') |

---

## 三、局部变形匹配 (Local Deformable)

### 完整流程
```
1. create_local_deformable_model(Template, NumLevels, AngleStart, AngleExtent, AngleStep,
     ScaleRMin, ScaleRMax, ScaleRStep, ScaleCMin, ScaleCMax, ScaleCStep,
     Optimization, Metric, Contrast, MinContrast, GenParamName, GenParamValue, ModelID)
2. find_local_deformable_model(Image, ImageRectified, VectorField, DeformRegion,
     ModelID, AngleStart, AngleExtent, ScaleRMin, ScaleRMax, ScaleCMin, ScaleCMax,
     MinScore, NumMatches, MaxOverlap, NumLevels, Greediness,
     ResultType, GenParamName, GenParamValue, Row, Col, Angle, Score, MatchID)
```
- 输出变形场(VectorField)和校正图(ImageRectified)

---

## 四、平面变形匹配 (Planar Deformable)

### 完整流程
```
1. create_planar_uncalib_deformable_model(Template, NumLevels, AngleStart, AngleExtent, AngleStep,
     ScaleRMin, ScaleRMax, ScaleRStep, ScaleCMin, ScaleCMax, ScaleCStep,
     Optimization, Metric, Contrast, MinContrast, GenParamName, GenParamValue, ModelID)
2. find_planar_uncalib_deformable_model(Image, ModelID, ..., HomMat2D, Score)
```
- 输出单应矩阵HomMat2D → 平面透视变换

---

## 五、C# HalconDotNet 代码模板

### 模板1: NCC匹配
```csharp
HObject templateImg, searchImg, templateReduced;
HTuple modelID, row, col, angle, score;

HOperatorSet.ReadImage(out templateImg, templatePath);
HOperatorSet.GenRectangle1(out var roi, r1, c1, r2, c2);
HOperatorSet.ReduceDomain(templateImg, roi, out templateReduced);

// 创建NCC模型
HOperatorSet.CreateNccModel(templateReduced, "auto", -0.2, 0.4, "auto", "use_polarity", out modelID);

// 搜索
HOperatorSet.ReadImage(out searchImg, searchPath);
HOperatorSet.FindNccModel(searchImg, modelID, -0.2, 0.4, 0.6, 1, 0.5, "true", 0,
    out row, out col, out angle, out score);

Console.WriteLine($"NCC匹配: ({row[0].D:F1},{col[0].D:F1}), 分数={score[0].D:F3}");

HOperatorSet.ClearNccModel(modelID);
searchImg.Dispose(); templateReduced.Dispose(); roi.Dispose(); templateImg.Dispose();
```

### 模板2: 匹配方法选择辅助
```csharp
// 根据场景选择匹配方法:
// 1. 有清晰边缘 → CreateShapeModel (Task11)
// 2. 纹理丰富、边缘弱 → CreateNccModel
// 3. 目标有局部变形 → CreateLocalDeformableModel
// 4. 目标有透视变换 → CreatePlanarUncalibDeformableModel
```
