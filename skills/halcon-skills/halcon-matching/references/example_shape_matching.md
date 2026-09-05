# Halcon 形状匹配技能手册

> 学习来源: `Matching/Shape-Based/`, `Matching/Deformable/`
> 涵盖Task11：形状匹配(Shape-Based Matching)

---

## 一、形状匹配方法对比

| 方法 | 算子前缀 | 旋转 | 缩放 | 变形 | 速度 | ⭐场景 |
|---|---|---|---|---|---|---|
| **Shape-Based** ⭐ | `create/find_shape_model` | ✅ | ✅ | ❌ | 最快 | ⭐标准定位(最常用) |
| **Scaled Shape** | `create/find_scaled_shape_model` | ✅ | ✅ | ❌ | 快 | 有缩放变化 |
| **Aniso Shape** | `create/find_aniso_shape_model` | ✅ | XY独立缩放 | ❌ | 中 | 各向异性缩放 |
| **Deformable** | `create/find_local_deformable_model` | ✅ | ✅ | ✅ | 慢 | 柔性变形目标 |
| **Planar Deformable** | `create/find_planar_deformable_model` | ✅ | ✅ | 透视 | 中 | 平面透视变换 |

---

## 二、Shape-Based Matching 完整流程 ⭐

```
1. read_image → 读取模板图
2. 手动/自动获取模板ROI区域
3. reduce_domain → 裁剪模板图到ROI
4. create_shape_model → 创建模型
5. find_shape_model → 在目标图中搜索
6. get_shape_model_results → 获取匹配位置
7. 仿射变换还原位姿
```

### 核心算子

#### create_shape_model — 创建模型
```
create_shape_model(Template, NumLevels, AngleStart, AngleExtent, AngleStep, 
                    Optimization, Metric, Contrast, MinContrast, ModelID)
```
| 参数 | 典型值 | 说明 |
|---|---|---|
| NumLevels | `'auto'`/4 | 金字塔层数(auto自动) |
| AngleStart | -0.39 | 起始角度(rad) |
| AngleExtent | 0.78 | 角度范围 |
| AngleStep | `'auto'` | 角度步长 |
| Optimization | `'auto'` | 优化模式 |
| Metric | `'use_polarity'` | 极性:亮→暗 / `'ignore_global_polarity'` |
| Contrast | `'auto'`/30 | 边缘对比度阈值 |
| MinContrast | `'auto'`/10 | 搜索时最小对比度 |

#### find_shape_model — 搜索匹配
```
find_shape_model(Image, ModelID, AngleStart, AngleExtent, MinScore, NumMatches, 
                  MaxOverlap, SubPixel, NumLevels, Greediness,
                  Row, Column, Angle, Score)
```
| 参数 | 典型值 | 说明 |
|---|---|---|
| MinScore | 0.5~0.8 | 最小匹配分数 |
| NumMatches | 1~10 | 最大匹配数量 |
| MaxOverlap | 0.5 | 最大重叠率 |
| SubPixel | `'least_squares'` | 亚像素精度 |
| Greediness | 0.7~0.9 | 贪婪度(越高越快但可能漏) |

#### create_scaled_shape_model — 带缩放的模型
```
create_scaled_shape_model(Template, NumLevels, AngleStart, AngleExtent, AngleStep,
                           ScaleMin, ScaleMax, ScaleStep, Optimization, Metric, 
                           Contrast, MinContrast, ModelID)
```
- 额外参数: ScaleMin(0.8), ScaleMax(1.2), ScaleStep('auto')

---

## 三、模型管理

| 算子 | 功能 |
|---|---|
| `write_shape_model(ModelID, FileName)` | 保存模型到文件 |
| `read_shape_model(FileName, ModelID)` | 从文件加载模型 |
| `clear_shape_model(ModelID)` | 释放模型内存 |
| `get_shape_model_contours(Contours, ModelID, Level)` | 获取模型轮廓 |
| `get_shape_model_params(ModelID, ...)` | 获取模型参数 |
| `inspect_shape_model(Template, ...)` | 检查模板质量 |

---

## 四、匹配后位姿还原

```csharp
// 1. 获取匹配位置(Row, Col, Angle)
// 2. 构建仿射矩阵
HomMat2dIdentity → HomMat2dRotate(Angle, 0, 0) → HomMat2dTranslate(Row, Col)
// 3. 变换模型轮廓到实际位置
AffineTransContourXld(ModelContours, TransContours, HomMat)
```

---

## 五、参数调优指南

### MinScore (最小匹配分数)
| 值 | 效果 |
|---|---|
| 0.3~0.5 | 宽松匹配，可能误检 |
| 0.5~0.7 | ⭐标准工业场景 |
| 0.7~0.9 | 严格匹配 |

### Greediness (贪婪度)
| 值 | 效果 |
|---|---|
| 0.0~0.3 | 最安全，不漏检，但慢 |
| 0.5~0.7 | ⭐平衡 |
| 0.8~0.9 | 最快，可能漏弱目标 |

### Metric (极性)
| 值 | 场景 |
|---|---|
| `'use_polarity'` | 亮暗方向固定 |
| `'ignore_global_polarity'` | ⭐亮暗可能反转 |
| `'ignore_local_polarity'` | 局部极性变化 |
| `'ignore_color_polarity'` | 彩色极性 |

---

## 六、C# HalconDotNet 代码模板

### 模板1: 标准形状匹配 ⭐⭐
```csharp
HObject templateImg, searchImg, modelRegion, templateReduced;
HTuple modelID, row, col, angle, score;

// 1. 创建模板
HOperatorSet.ReadImage(out templateImg, templatePath);
HOperatorSet.GenRectangle1(out modelRegion, r1, c1, r2, c2); // 模板ROI
HOperatorSet.ReduceDomain(templateImg, modelRegion, out templateReduced);
HOperatorSet.CreateShapeModel(templateReduced, "auto", -0.39, 0.78, "auto",
    "auto", "use_polarity", "auto", "auto", out modelID);

// 2. 搜索匹配
HOperatorSet.ReadImage(out searchImg, searchPath);
HOperatorSet.FindShapeModel(searchImg, modelID, -0.39, 0.78,
    0.5, 1, 0.5, "least_squares", 0, 0.9,
    out row, out col, out angle, out score);

Console.WriteLine($"找到 {row.Length} 个匹配:");
for (int i = 0; i < row.Length; i++)
    Console.WriteLine($"  位置=({row[i].D:F1},{col[i].D:F1}), 角度={angle[i].D*180/Math.PI:F1}°, 分数={score[i].D:F3}");

// 3. 释放
HOperatorSet.ClearShapeModel(modelID);
searchImg.Dispose(); templateReduced.Dispose();
modelRegion.Dispose(); templateImg.Dispose();
```

### 模板2: 带缩放的形状匹配
```csharp
HTuple modelID, row, col, angle, scale, score;

// 创建带缩放模型
HOperatorSet.CreateScaledShapeModel(templateReduced, "auto", -0.39, 0.78, "auto",
    0.8, 1.2, "auto", "auto", "use_polarity", "auto", "auto", out modelID);

// 搜索
HOperatorSet.FindScaledShapeModel(searchImg, modelID, -0.39, 0.78, 0.8, 1.2,
    0.5, 1, 0.5, "least_squares", 0, 0.9,
    out row, out col, out angle, out scale, out score);
```

### 模板3: 匹配后仿射变换还原
```csharp
// 获取模型轮廓
HObject modelContours, transContours;
HOperatorSet.GetShapeModelContours(out modelContours, modelID, 1);

// 构建仿射矩阵
HTuple homMat;
HOperatorSet.HomMat2dIdentity(out homMat);
HOperatorSet.HomMat2dRotate(homMat, angle[0].D, 0, 0, out homMat);
HOperatorSet.HomMat2dTranslate(homMat, row[0].D, col[0].D, out homMat);

// 变换轮廓到实际位置
HOperatorSet.AffineTransContourXld(modelContours, out transContours, homMat);

transContours.Dispose(); modelContours.Dispose();
```

### 模板4: 保存/加载模型
```csharp
// 保存
HOperatorSet.WriteShapeModel(modelID, "model.shm");
// 加载
HTuple loadedModelID;
HOperatorSet.ReadShapeModel("model.shm", out loadedModelID);
```
