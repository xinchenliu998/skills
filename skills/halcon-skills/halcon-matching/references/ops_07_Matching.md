# HALCON 算子分类详解：Matching

> **分类**：Matching（模板匹配）
> **子类数**：6（Correlation-based / Deep Counting / Deformable / Descriptor-based / Shape-based / Generic）
> **学习优先级**：⭐⭐⭐⭐⭐（工业视觉最核心的能力之一，所有"找东西 + 定位 + 引导"任务的基石）
> **典型应用场景**：在图像中快速定位已知模板（单实例/多实例），输出位姿 (Row, Col, Angle) 或 (Pose)，用于机器人引导、装配对位、缺陷定位。

---

## 1. 概述

Matching 是 HALCON 的核心模块，覆盖从最经典的灰度相关匹配（NCC）到基于深度学习的高级计数/通用匹配模型。它处于 HALCON 流水线的"定位层"，通常：

- **上游**：`grab_image` / `read_image` 采集图像。
- **匹配层**：`create_*_model` 训练 + `find_*_model` 推理。
- **下游**：得到位姿后用 `vector_angle_to_rigid` / `vector_to_*` 得到变换矩阵，再 `affine_trans_*` 对齐 ROI，或用位姿引导机械手。

HALCON 26 的 Matching 家族包括 **6 大算法族**与 **1 个通用框架**，可覆盖从灰度近似、形状刚体、缩放/各向异性、平面变形、杂乱堆叠、深度计数、CNN 端到端学习的全部工业匹配需求。

---

## 2. 应用场景

1. **PCB 元件定位**：阻容/IC 位置 → 贴片机对位引导。
2. **机器人抓取 / Bin Picking**：杂乱堆叠零件识别 + 6D 位姿。
3. **柔性材料对位**：印刷品、皮革、橡胶有形变 → Deformable。
4. **3C 装配定位**：手机壳体按键、摄像头孔位对位。
5. **产线快速计数**：电池极片颗粒数、药片数 → Deep Counting。

---

## 3. 子分类详解

| 子分类 | 适用场景 | 代表算子 |
|--------|----------|----------|
| **Correlation-based (NCC)** | 灰度近似、纹理丰富、轻度旋转/光照变化 | `create_ncc_model`、`find_ncc_model`、`find_ncc_models`、`set_ncc_model_param`、`get_ncc_model_*` |
| **Shape-based** | 边缘清晰、刚性、可能的等比缩放/各向异性缩放 | `create_shape_model`、`create_aniso_shape_model`、`create_scaled_shape_model`、`create_shape_model_xld`、`find_shape_model`、`find_shape_models`、`find_aniso_shape_model`、`find_scaled_shape_model`、`inspect_shape_model`、`set_shape_model_*` |
| **Deformable** | 易变形物体（布、橡胶、印刷品、皮革），可平面变形 | `create_planar_uncalib_deformable_model`、`create_planar_calib_deformable_model`、`create_local_deformable_model`、`find_planar_uncalib_deformable_model`、`find_planar_calib_deformable_model`、`find_local_deformable_model`、`set_deformable_model_*`、`refine_deformable_*` |
| **Descriptor-based** | 杂乱堆叠、局部可见、含噪声/背景 | `create_calib_descriptor_model`、`create_uncalib_descriptor_model`、`find_calib_descriptor_model`、`find_uncalib_descriptor_model`、`get_descriptor_model_*` |
| **Component-based** | 多部件空间关系组装 | `create_trained_component_model`、`train_model_components`、`create_component_model`、`find_component_model`、`gen_initial_components`、`inspect_clustered_components`、`get_component_*`、`cluster_model_components`、`modify_component_relations` |
| **Deep Counting / Generic / Misc** | 快速计数、自定义特征 + CNN | `create_deep_counting_model`、`apply_deep_counting_model`、`read/write_deep_counting_model`、`create_generic_shape_model`、`train_generic_shape_model`、`find_generic_shape_model`、`apply_deep_matching_3d`、`create_deep_matching_3d` |

---

## 4. 核心算子详解

| 算子 | 用途 | 输入 | 输出 | 典型用法 |
|------|------|------|------|----------|
| `create_shape_model` | 训练形状模型 | Template, NumLevels, AngleStart, AngleExtent, AngleStep, Optimization, Metric, Contrast, MinContrast | ModelID | **最常用**，边缘匹配 |
| `find_shape_model` | 搜索形状模型 | Image, ModelID, AngleStart, AngleExtent, MinScore, NumMatches, MaxOverlap, SubPixel, NumLevels, Greediness | Row, Column, Angle, Score | 单/多实例定位 |
| `find_shape_models` | 多模型同步搜索 | Image, ModelIDs, AngleStart, AngleExtent, MinScore, NumMatches, MaxOverlap, SubPixel, NumLevels, Greediness | Row, Column, Angle, Score, ModelIdx | 多产品混合线 |
| `create_aniso_shape_model` | 训练各向异性缩放模型 | Template, NumLevels, AngleStart, AngleExtent, AngleStep, ScaleRMin, ScaleRMax, ScaleRStep, ScaleCMin, ScaleCMax, ScaleCStep, Optimization, Metric, Contrast, MinContrast | ModelID | 长宽比变化 |
| `find_aniso_shape_model` | 搜索各向异性 | Image, ModelID, AngleStart, AngleExtent, ScaleRMin, ScaleRMax, ScaleCMin, ScaleCMax, MinScore, NumMatches, MaxOverlap, SubPixel, NumLevels, Greediness | Row, Column, Angle, ScaleR, ScaleC, Score | 同上 |
| `create_scaled_shape_model` | 训练等比缩放模型 | Template, NumLevels, AngleStart, AngleExtent, AngleStep, ScaleMin, ScaleMax, ScaleStep, Optimization, Metric, Contrast, MinContrast | ModelID | 远近缩放 |
| `find_scaled_shape_model` | 搜索等比缩放 | Image, ModelID, AngleStart, AngleExtent, ScaleMin, ScaleMax, MinScore, NumMatches, MaxOverlap, SubPixel, NumLevels, Greediness | Row, Column, Angle, Scale, Score | 同上 |
| `create_ncc_model` | 训练 NCC 灰度模型 | Template, NumLevels, AngleStart, AngleExtent, AngleStep, Metric | ModelID | 印刷/纹理 |
| `find_ncc_model` | 搜索 NCC | Image, ModelID, AngleStart, AngleExtent, MinScore, NumMatches, MaxOverlap, SubPixel, NumLevels | Row, Column, Angle, Score | 同上 |
| `find_ncc_models` | 多 NCC 同步 | Image, ModelIDs, ... | Row, Column, Angle, Score, ModelIdx | 同上 |
| `inspect_shape_model` | 交互查看模型金字塔 | ModelID, Image, NumLevels, ModelLevel | ModelContours, ModelImage | 训练可视化 |
| `set_shape_model_metric` | 设置匹配指标 | ModelID, Image, Metric, AxisChangeAngle, ... |  | 提高鲁棒性 |
| `set_shape_model_clutter` | 设置杂乱容忍度 | ModelID, Image, ClutterRegion |  | 局部遮挡 |
| `set_shape_model_origin` | 设置模型原点 | ModelID, Row, Column |  | 控制位姿原点 |
| `create_planar_uncalib_deformable_model` | 训练未标定平面变形模型 | Template, NumLevels, AngleStart, AngleExtent, AngleStep, ScaleRMin, ScaleRMax, ScaleCMin, ScaleCMax, Optimization, Metric, Contrast, MinContrast, MinThreshold, GenParamNames, GenParamValues | ModelID | 印刷品形变 |
| `find_planar_uncalib_deformable_model` | 搜索未标定平面变形 | Image, ModelID, AngleStart, AngleExtent, ScaleRMin, ScaleRMax, ScaleCMin, ScaleCMax, MinScore, NumMatches, MaxOverlap, SubPixel, NumLevels, Greediness, ParamName, ParamValue | Row, Column, Angle, Score, Model | 形变定位 |
| `create_local_deformable_model` | 训练局部变形 | Template, NumLevels, AngleStart, AngleExtent, AngleStep, ScaleRMin, ScaleRMax, ScaleCMin, ScaleCMax, Optimization, Metric, Contrast, MinContrast, MinThreshold, GenParamNames, GenParamValues | ModelID | 局部形变 |
| `find_local_deformable_model` | 搜索局部变形 | Image, ModelID, AngleStart, AngleExtent, ScaleRMin, ScaleRMax, ScaleCMin, ScaleCMax, MinScore, NumMatches, MaxOverlap, SubPixel, NumLevels, Greediness, ParamName, ParamValue | Row, Column, Angle, Score, Model | 同上 |
| `refine_deformable_model` | 精化形变结果 | Image, DeformedContours, Model, MinScore, Iterations | RefinedContours, Scores | 提升精度 |
| `create_calib_descriptor_model` | 训练标定描述子模型 | Template, CamParam, ... | ModelID | 杂乱堆叠（标定） |
| `find_calib_descriptor_model` | 搜索标定描述子 | Image, ModelID, MinScore, NumMatches, Pose, Score | Pose, Score | 6D 杂乱抓取 |
| `create_uncalib_descriptor_model` | 训练未标定描述子 | Template, ... | ModelID | 无相机参数 |
| `find_uncalib_descriptor_model` | 搜索未标定描述子 | Image, ModelID, MinScore, NumMatches, HomMat2D, Score | HomMat2D, Score | 2D 杂乱 |
| `create_component_model` | 训练组件模型 | ComponentRegions, ... | ModelID | 多部件空间关系 |
| `find_component_model` | 搜索组件 | Image, ComponentModelID, MinScore, NumMatches, MaxOverlap, Greediness | Row, Column, Angle, Score, ModelComp, Relations, RowComp, ColComp, AngleComp, ScoreComp | 杂乱场景 |
| `create_generic_shape_model` | 创建通用形状模型 | Contours, NumLevels, AngleStart, AngleExtent, AngleStep, ScaleRMin, ScaleRMax, ScaleCMin, ScaleCMax, GenParamNames, GenParamValues | ModelID | 自定义特征 |
| `train_generic_shape_model` | 训练通用模型 | Image, ModelID, Row, Column, Angle, ScaleR, ScaleC | ModelID | 端到端 CNN |
| `find_generic_shape_model` | 搜索通用模型 | Image, ModelID, AngleStart, AngleExtent, ScaleRMin, ScaleRMax, ScaleCMin, ScaleCMax, MinScore, NumMatches, MaxOverlap, GenParamNames, GenParamValues | Row, Column, Angle, Score, GenericlModelMatches | 多场景通用 |
| `create_deep_counting_model` | 创建深度计数模型 | GenParam | ModelID | 快速计数 |
| `apply_deep_counting_model` | 推理计数 | Image, ModelID, GenParam | Count, Confidence | 任意姿态计数 |

---

## 5. 八种匹配算法对比（核心速查表）

| 算法 | 适用 | 不适用 | 关键算子 | 训练时间 | 推理速度 | 鲁棒性 |
|------|------|--------|----------|----------|----------|--------|
| **NCC（灰度相关）** | 纹理丰富、灰度近似、轻度旋转 | 大缩放、强光照、软变形 | `create_ncc_model` / `find_ncc_model` | 快 | 极快 | 中 |
| **Shape-Based（形状）** | 边缘清晰、刚性件、含小角度变化 | 软变形、纹理主导 | `create_shape_model` / `find_shape_model` | 中 | 快 | 高 |
| **Aniso Shape（各向异性）** | 长宽比变化的零件 | 软变形 | `create_aniso_shape_model` / `find_aniso_shape_model` | 中 | 中 | 高 |
| **Scaled Shape（等比缩放）** | 远近缩放 | 软变形 | `create_scaled_shape_model` / `find_scaled_shape_model` | 中 | 中 | 高 |
| **Deformable（可变形）** | 布/橡胶/印刷品/皮革 | 刚性件 | `create_planar_uncalib_deformable_model` / `find_planar_*_deformable_model` | 慢 | 中 | 高 |
| **Component-Based（组件）** | 多部件 + 空间关系 | 单部件 | `create_component_model` / `find_component_model` | 慢 | 中 | 高 |
| **Descriptor-Based（描述子）** | 杂乱堆叠、局部可见 | 全目标完整可见 | `create_calib/uncalib_descriptor_model` / `find_*descriptor_model` | 慢 | 慢 | 极高 |
| **Deep Counting（深度计数）** | 任意姿态目标的快速计数 | 单目标定位 | `create_deep_counting_model` / `apply_deep_counting_model` | 极慢 | 极快 | 极高 |
| **Generic Shape（通用）** | 自定义特征 + CNN 学习 | 经典简单场景 | `create_generic_shape_model` / `find_generic_shape_model` | 极慢 | 中 | 极高 |

---

## 6. HDevelop 示例代码

### 示例 1：Shape-Based 单目标定位（最经典流水线）

**场景**：PCB 上 IC 定位（已知模板）。
**功能**：`create_shape_model` 训练 → `find_shape_model` 搜索 → 仿射变换对齐。
**预期输出**：目标位置、角度、Score，叠加显示。

```hdevelop
* ============================================================
* 示例1：Shape-Based 单目标定位
* ============================================================
dev_update_off ()
dev_close_window ()
read_image (Image, 'ic/ic_01')
get_image_size (Image, Width, Height)
dev_open_window (0, 0, Width / 2, Height / 2, 'black', WindowHandle)
dev_display (Image)

* 1) 准备模板：缩小 ROI 以加快训练
gen_rectangle1 (ModelROI, 200, 230, 380, 460)
reduce_domain (Image, ModelROI, TemplateImage)

* 2) 创建形状模型（金字塔层数 4，对比度 30/60）
create_shape_model (TemplateImage, 4, rad(-30), rad(60), 'auto', 'none', \
                    'use_polarity', 30, 10, ModelID)

* 3) 推理（在另一张图上找）
read_image (SearchImage, 'ic/ic_02')
find_shape_model (SearchImage, ModelID, rad(-30), rad(60), 0.7, 0, 0, \
                  'least_squares', 4, 0.8, Row, Column, Angle, Score)

* 4) 可视化
dev_set_color ('green')
dev_set_line_width (3)
disp_cross (WindowHandle, Row, Column, 30, Angle)
dev_set_color ('yellow')
disp_text (WindowHandle, 'Score=' + Score$'.3f', 'window', Row - 30, Column, \
           'black', 'box', 'false')
dev_set_line_width (1)

clear_shape_model (ModelID)
dev_update_on ()
stop ()
```

### 示例 2：多实例 + 缩放（找电池颗粒）

**场景**：圆形电池片等比缩放计数。
**功能**：`create_scaled_shape_model` 训练 → `find_scaled_shape_model` 多实例。
**预期输出**：每个圆的 (Row, Col, Scale, Score)。

```hdevelop
* ============================================================
* 示例2：Scaled Shape 找电池颗粒
* ============================================================
dev_update_off ()
dev_close_window ()
read_image (Image, 'battery/battery_01')
get_image_size (Image, Width, Height)
dev_open_window (0, 0, Width / 2, Height / 2, 'black', WindowHandle)
dev_display (Image)

* 1) 模板
gen_rectangle1 (ModelROI, 100, 100, 280, 280)
reduce_domain (Image, ModelROI, TemplateImage)

* 2) 等比缩放模型（缩放范围 0.8 ~ 1.2，步长 auto）
create_scaled_shape_model (TemplateImage, 4, 0, rad(360), 'auto', 0.8, 1.2, \
                           'auto', 'none', 'use_polarity', 30, 10, ModelID)

* 3) 多实例搜索（最多 50 个，允许多目标）
find_scaled_shape_model (Image, ModelID, 0, rad(360), 0.7, 50, 0.5, \
                         'least_squares', 4, 0.8, Row, Column, Angle, Scale, Score)

* 4) 可视化：每个圆 + Scale 文本
gen_empty_obj (Circles)
for i := 0 to |Score| - 1 by 1
    gen_circle_contour_xld (Circle, Row[i], Column[i], 30 * Scale[i], \
                            0, 6.28318, 'positive', 1)
    concat_obj (Circles, Circle, Circles)
endfor
dev_set_color ('green')
dev_set_line_width (2)
dev_display (Circles)

dev_set_color ('yellow')
disp_text (WindowHandle, 'Found: ' + |Score|, 'window', 10, 10, 'black', 'box', 'false')
dev_set_line_width (1)

clear_shape_model (ModelID)
dev_update_on ()
stop ()
```

### 示例 3：Deformable 形变匹配（包装印刷图案）

**场景**：印刷包装上易变形的图案（材料拉伸、轻微褶皱）。
**功能**：`create_planar_uncalib_deformable_model` 训练 → `find_planar_uncalib_deformable_model` 搜索。
**预期输出**：形变后的轮廓 + 评分。

```hdevelop
* ============================================================
* 示例3：Deformable 形变匹配
* ============================================================
dev_update_off ()
dev_close_window ()
read_image (Image, 'packages/packages_01')
get_image_size (Image, Width, Height)
dev_open_window (0, 0, Width / 2, Height / 2, 'black', WindowHandle)
dev_display (Image)

* 1) 训练形变模型
read_image (Template, 'packages/packages_template')
create_planar_uncalib_deformable_model (Template, 'auto', rad(-20), rad(20), \
                                         'auto', 0.9, 1.1, 'auto', 0.9, 1.1, \
                                         'auto', 'none', 'use_polarity', 60, 30, \
                                         [], [], ModelID)

* 2) 形变搜索（最小 Score 0.5）
find_planar_uncalib_deformable_model (Image, ModelID, rad(-20), rad(20), \
                                       0.9, 1.1, 0.9, 1.1, 0.5, 1, 0.5, \
                                       'least_squares', 4, 0.8, [], [], \
                                       Row, Column, Angle, Score, Model)

* 3) 显示形变轮廓
get_deformable_model_contours (ModelContours, ModelID, 1)
dev_set_color ('green')
dev_set_line_width (2)
dev_display (ModelContours)
dev_set_color ('yellow')
disp_text (WindowHandle, 'Score=' + Score$'.3f', 'window', Row - 30, Column, \
           'black', 'box', 'false')
dev_set_line_width (1)

clear_deformable_model (ModelID)
dev_update_on ()
stop ()
```

---

## 7. 典型工业流水线

### 流水线 A：SMT 贴片对位

```
grab_image
  → create_shape_model (从参考 PCB 训练)
  → find_shape_model (实时图)
  → vector_angle_to_rigid (算出位姿)
  → affine_trans_image (贴片图与 PCB 对齐)
  → 偏差 → 调整贴装头
```

### 流水线 B：Bin Picking（杂乱抓取）

```
read_object_model_3d (CAD 模型)
  → prepare_object_model_3d
  → create_calib_descriptor_model
  → grab_image + 标定
  → find_calib_descriptor_model → 6D Pose
  → hand_eye 转换到机器人坐标系
  → 引导机械手
```

### 流水线 C：印刷品形变对位

```
create_planar_uncalib_deformable_model (模板)
  → find_planar_uncalib_deformable_model
  → vector_to_proj_hom_mat2d (形变 → 投影矩阵)
  → projective_trans_image (校正印刷形变)
  → 后续 OCR / 视觉检测
```

### 流水线 D：极简计数（不需定位）

```
create_deep_counting_model ('type', 'counting')
  → apply_deep_counting_model (Image)
  → Count + Confidence → MES 系统
```

---

## 8. 常见陷阱与最佳实践

1. **`Greediness` 调参**：默认 0.8 是速度/鲁棒平衡；提速调到 0.95、漏检减少调到 0.5。
2. **`MinScore` 阈值**：过低误检、过高漏检；工业经验值 0.7–0.85，配合 `set_shape_model_clutter` 提高杂乱容忍。
3. **训练图与运行图光照差异**：必须用 `Metric = 'ignore_color_polarity'` 或 `'use_polarity'`，并尽量让训练 ROI 与生产一致。
4. **`AngleExtent` 角度范围**：360° 全范围搜索慢 5–10 倍；先估计 ±30° 缩小范围。
5. **`NumLevels` 金字塔层数**：太大慢、太小漏大缩放；典型 4–6 层。
6. **`SubPixel = 'least_squares'`** 比 `'interpolation'` 慢但精度高（机器人抓取必用 least_squares）。
7. **`find_shape_models` 多模型同步**：每个模型的金字塔层/角度范围最好一致，否则内存暴涨。
8. **Deformable 不要训练**在背景复杂的图上——`MinThreshold` 设太低会让模型学进噪声。
9. **Descriptor-based 训练 CAD 投影图**：必须用与生产一致的相机标定参数 `CamParam`。
10. **`create_component_model` 训练时使用 `gen_initial_components`** 自动生成组件，否则需要手动标注所有部件 ROI。

---

## 9. 参数调优指南

| 算子 | 参数 | 含义 | 典型值 |
|------|------|------|--------|
| `create_shape_model` | `NumLevels` | 金字塔层数 | 4–6 |
| `create_shape_model` | `AngleStep` | 角度步长 | `'auto'`（推荐） |
| `create_shape_model` | `Metric` | 极性策略 | `'use_polarity'` / `'ignore_global_polarity'` / `'ignore_local_polarity'` / `'ignore_color_polarity'` |
| `create_shape_model` | `Contrast` | 对比度阈值 | 20–60 |
| `find_shape_model` | `MinScore` | 最低分数 | 0.7–0.85 |
| `find_shape_model` | `MaxOverlap` | 最大重叠比 | 0.4–0.5 |
| `find_shape_model` | `SubPixel` | 亚像素策略 | `'none'` / `'interpolation'` / `'least_squares'` / `'least_squares_high'` |
| `find_shape_model` | `Greediness` | 搜索贪婪度 | 0.5（稳）/ 0.8（默认）/ 0.95（快） |
| `find_shape_model` | `NumLevels` | 搜索层数 | 与训练一致或减少 |
| `create_aniso_shape_model` | `ScaleRMin/Max` | R 方向缩放 | 0.8–1.2 |
| `create_aniso_shape_model` | `ScaleRStep` | R 步长 | `'auto'` |
| `create_scaled_shape_model` | `ScaleMin/Max` | 等比缩放 | 0.5–2.0 |
| `find_planar_uncalib_deformable_model` | `MinScore` | 形变最低分 | 0.5–0.7 |
| `find_planar_uncalib_deformable_model` | GenParam `'min_size_reform'` | 形变平滑度 | 0.3–0.7 |
| `create_generic_shape_model` | `'metric'` | 通用指标 | `'ignore_color_polarity'` 等 |
| `apply_deep_counting_model` | `'min_score'` | 最低置信度 | 0.5 |
| `set_shape_model_clutter` | ClutterRegion | 杂乱允许区 | 标注好的遮挡/杂乱区域 |

---

## 10. 相关分类

- **Transformations**：`vector_angle_to_rigid`、`vector_to_hom_mat2d` 是匹配后位姿转矩阵的桥梁。
- **Graphics**：`disp_cross`、`disp_arrow`、`affine_trans_region` 用于结果可视化。
- **Image**：`reduce_domain` 是训练时缩小 ROI 的关键。
- **Filters**：`gauss_filter`、`emphasize` 等预处理能显著提升匹配率。
- **3D Matching**：从 2D 升级到 3D 模板（CAD）的同类能力。
- **Deep Learning**：`create_generic_shape_model` 在底层使用 CNN 特征，可与 DL 协同。

---

## 11. 学习小结

Matching 是 HALCON 的"找东西"核心。要点：

1. **8 种算法**（NCC、Shape、Aniso、Scaled、Deformable、Component、Descriptor、Deep Counting + Generic）必须按场景选型；先评估形变→杂叠→计数，再选。
2. **`create_shape_model` + `find_shape_model`** 是 80% 项目的首选；遇到缩放加 Aniso / Scaled、遇到形变加 Deformable、遇到杂乱堆叠加 Descriptor。
3. **`Greediness` 与 `MinScore`** 是匹配速度与精度的双旋钮：稳就 `0.5 + 0.8`、快就 `0.95 + 0.85`。
4. **`SubPixel = 'least_squares'`** 是机器人引导的必选（亚像素位姿 + 角度）。
5. **Descriptor-based + 手眼标定**是 3C 杂乱抓取（Bin Picking）的标准组合。
6. **Deep Counting** 不输出位姿只输出数量——典型用于产线极简统计。
7. 任何匹配流水线都建议：训练图与生产图 ROI 一致 + 训练前 `inspect_shape_model` 检查金字塔。
