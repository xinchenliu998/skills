---
name: halcon-matching
description: >-
  HALCON 2D template matching and localization across all approaches: correlation
  (NCC), shape-based (create_generic_shape_model / train_generic_shape_model /
  find_generic_shape_model and the classic create/find_shape_model,
  create_scaled_shape_model, create_aniso_shape_model), local deformable,
  perspective (planar) deformable, and descriptor-based matching. Use this skill
  whenever a HALCON/HDevelop task needs to find and localize an object in an
  image and return a pose, rotation, scale, score or homography — for robot
  guidance, assembly alignment, defect localization, or multi-instance
  counting. Trigger on choosing between create_shape_model / find_shape_model /
  create_ncc_model / create_local_deformable_model /
  create_planar_uncalib_deformable_model / create_uncalib_descriptor_model, on
  MinScore / Greediness / AngleStep / Metric / SubPixel tuning, on template
  preparation (reduce_domain + inspect_shape_model), on reusing saved models, or
  on converting match results into an affine/homography transform for alignment.
---

# HALCON 2D 匹配（模板匹配/定位）

> 定位：像素流水线的"定位层"——先在搜索图里找到已知目标，输出位姿/单应，供对齐、引导、测量、缺陷定位。
> 上游 `read_image`/`grab_image`，下游 `vector_angle_to_rigid`/`hom_mat2d_compose`+`affine_trans_*`。
> 编写规范见 `../_authoring/`（conventions.md 为精简总结；完整规范在 halcon_skill.md；脚本格式/CLI 见同名 *_reference.md）。
> 版本要点：HALCON 26.05 用**通用接口** `create_generic_shape_model`/`find_generic_shape_model`（经典 `create_shape_model`/`create_scaled_shape_model`/`create_aniso_shape_model`/`find_shape_model` 为前代，概念一致，见文末映射）。

---

## 一、五法选型（核心速查）

| 方法 | 关键算子 | 变换能力 | 适用 | 不适合 |
|---|---|---|---|---|
| **Correlation (NCC)** | `create_ncc_model`/`find_ncc_model` | 平移+旋转（无缩放） | 纹理随机、轻微形变/失焦、纯光照 | 大尺度/遮挡/杂波 |
| **Shape-Based** ⭐ | `create_generic_shape_model`/`find_generic_shape_model` | 平移+旋转+均匀/各向异性缩放 | 有清晰轮廓、刚性、需抗遮挡/杂波 | 透视、纯纹理 |
| **Local Deformable** | `create_local_deformable_model`/`find_local_deformable_model` | 平移+旋转+缩放+局部变形 | 柔软/卷曲、需校直/矢量场 | 需角度/尺度输出 |
| **Perspective Deformable** | `create_planar_uncalib_deformable_model`/`find_planar_uncalib_deformable_model` | 透视（返回单应）/标定版返回3D位姿 | 平面斜拍、透视变形 | 正交视图（慢） |
| **Descriptor-Based** | `create_uncalib_descriptor_model`/`find_uncalib_descriptor_model` | 透视、固定纹理（兴趣点） | 高纹理(标签/书页)、需3D位姿 | 无纹理圆润边缘、各向异性缩放 |

**口诀**：3D→3D matching（见 `halcon-3d-vision`）；平面+透视→perspective（有清晰轮廓/各向异性缩放）或 descriptor（有纹理/更快）；正交 2D→shape（需尺度/遮挡/颜色）或 NCC（纹理/模糊/轻微形变）或 local-deformable（局部变形）。

---

## 二、通用 workflow（5 步）

```
1. 选 ROI 模板        gen_rectangle1/2 或 blob 分析(threshold+connection+fill_up+select_shape)；复杂 ROI union2/difference
2. 裁剪模板          reduce_domain (Image, ROI, ImageReduced)
3. 建模型            方法专用算子（可 'auto' 自动估参）
4. (部分方法) 训练     train_generic_shape_model / 参数配置
5. 搜索 → 结果        find_* → 位置/角/尺度/分数/变换矩阵
```

- **参考点（模型原点）**：默认=ROI 中心；建议**不改**（精度随偏移线性下降，`set_*_model_origin`）。XLD 模型参考点在图像原点，含负坐标。
- **ROI 外灰度影响模型**：影响范围约 `2^NumLevels` 像素；ROI 宽度经验 `2^(NumLevels-1)` 像素。ROI 外灰值应与搜索图相近。
- **结果坐标还原**：匹配返回的是**相对参考点**的量（参考点默认移到 (0,0)）。用 `get_generic_shape_model_result(...,'hom_mat_2d',...)` 拿变换阵 → `affine_trans_contour_xld`/`affine_trans_pixel`/`affine_trans_region`/`affine_trans_image`。
  - **关键坑**：必须用 `affine_trans_pixel`，**不要用 `affine_trans_point_2d`**（后者坐标系统差 0.5 像素、中心在像素中心）。

---

## 三、Shape-Based（最通用）——通用接口步骤

```hdevelop
gen_rectangle1 (ModelROI, ...)
reduce_domain (Image, ModelROI, ModelImage)
create_generic_shape_model (ModelID)
set_generic_shape_model_param (ModelID, ParamName, ParamValue)   * 配置
train_generic_shape_model (ModelImage, ModelID)                  * 训练
find_generic_shape_model (SearchImage, ModelID, MatchResultID, NumMatchResult)
get_generic_shape_model_result (MatchResultID, 'all', ResultName, Value)
```
> 模型自身参数必须在训练前设置；`'needs_training'`=true 时需重新训练。modelID 可传 tuple 一次搜多模型（更快）。

### 关键模型参数（set_generic_shape_model_param）
| 参数 | 含义 | 默认/推荐 |
|---|---|---|
| `'contrast_low'`/`'contrast_high'` | 边缘点对比度阈值（单值或滞后 `[low,high]`） | `'auto'` |
| `'min_size'` | 抑制小于该点数的连通分量（去杂波） | `'auto'` |
| `'num_levels'` | 金字塔层数 | `'auto'`；最高层仍须 ≥10–15px |
| `'optimization'` | 减点数提速 | `'auto'` |
| `'iso_scale_min/max'`+`'iso_scale_step'` | 均匀缩放范围/步长 | step `'auto'` |
| `'aniso_scale_*_min/max/step'`（row/col） | 非均匀缩放 | step `'auto'` |
| `'angle_start'`/`'angle_end'`/`'angle_step'` | 旋转范围/步长 | 默认 0–2π |
| `'metric'` | `'use_polarity'`/`'ignore_global_polarity'`/`'ignore_local_polarity'`/`'ignore_color_polarity'` | `'use_polarity'` |
| `'min_contrast'` | 搜索点最小对比度 | `'auto'` |
| `'max_deformation'` | 允许轮廓最大变形像素 | 0（需配合 least-squares） |

### 搜索参数（find 阶段）
`'greediness'`(0 详尽~1 快但险，**先取 0 保证全找到**)、`'min_score'`、`'num_matches'`、`'max_overlap'`、`'subpixel'`、`'pyramid_level_highest'`、`'border_shape_models'`。
- **角步长/缩放步长自动最优**：`φopt = arccos(1 - 2/l²)`，`Δsopt = 2/l`（l=中心到轮廓最大距离）。手动值建议在 `[1/3·opt, 3·opt]`；太大→score 骤降甚至失败，太小→无精度增益。
- **`'subpixel'`**：`'none'`/`'interpolation'`（~1/20 像素）/`'least_squares'`/`'least_squares_high'`/`'least_squares_very_high'`（更准更慢；配 max_deformation 用 least-squares）。细分不更新 score。

### Clutter（杂波/禁区）
`set_generic_shape_model_object (ClutterRegion, ModelID, 'clutter_region')`（训练前）或训练后 `set_generic_shape_model_param(ModelID,'clutter_hom_mat_2d',HomMat2D)`。用"物体周围应无边缘"约束筛选匹配（如机械手抓取留空）。注意：只在匹配管线末端生效，不减少运行时间。

### 模型检查/复用
`inspect_shape_model (ImageReduced, ModelImages, ModelRegions, NumLevels, Contrast)`（`[40,70]`=滞后阈值；`[40,40,30]`=带 min_size）；`get_generic_shape_model_*`；`determine_shape_model_params`；`write_shape_model`/`read_shape_model`。

---

## 四、其它方法的要点差异

| 方法 | 创建/查找 | 返回 | 要点 |
|---|---|---|---|
| **NCC** | `create_ncc_model`/`find_ncc_model` | Row,Col,Angle,Score | `SubPixel='true'` 亚像素；`'timeout'` 限时；ROI 别太薄 |
| **Local Deformable** | `create_local_deformable_model`/`find_local_deformable_model` | **仅位置** + `ImageRectified`/`VectorField`/`DeformedContours` | `ResultType` 取 `['image_rectified','vector_field','deformed_contours']`；矢量场是**绝对坐标** |
| **Perspective Deformable** | `create_planar_uncalib_deformable_model`/`find_planar_uncalib_deformable_model` | **单应 HomMat2D**（未标定）/Pose（标定版 `_calib_`） | `projective_trans_contour_xld` 显示；不各向异性缩放 |
| **Descriptor** | `create_uncalib_descriptor_model`/`find_uncalib_descriptor_model` | **单应/3D位姿** | 兴趣点均匀分布约 50–450；`MinScore` 按 `'inlier_ratio'` 语义≥0.1；`ScoreType='num_points'`≥10 |

---

## 五、经典算子 → 通用接口映射（26.05）
| 经典 | 通用 |
|---|---|
| `create_shape_model` | `create_generic_shape_model`（不设 scale 范围） |
| `create_scaled_shape_model` | `'iso_scale_min/max/step'` |
| `create_aniso_shape_model` | `'aniso_scale_*'` |
| `create_ncc_model` | ——（无通用版，仍用 NCC） |
| `find_shape_model(...,Row,Col,Angle,Score)` | `find_generic_shape_model`+`get_generic_shape_model_result` |
| `find_shaped_models`（多模型） | `find_generic_shape_model(ModelIDs tuple)` |

---

## 六、参数调优速查
| 参数 | 含义 | 稳 | 快 |
|---|---|---|---|
| `MinScore` | 最低匹配分 | 0.5–0.7 | 0.8–0.85 |
| `Greediness` | 搜索贪婪度 | 0.5 | 0.9–0.95 |
| `NumLevels` | 金字塔层 | 低层多（慢准） | 4–6 |
| `SubPixel` | 亚像素 | `'least_squares'` | `'interpolation'` |
| `MaxOverlap` | 最大重叠 | — | 0.4–0.5 |

---

## 七、常见陷阱与最佳实践
1. 选含**垂直方向轮廓**的模型以在检测方向有精度；环形轮廓各向精度最佳。
2. **对称物体**（方形<90°、矩形<180°、圆 0°）限制角度范围，否则多实例乱跳。
3. `Greediness`/`MinScore` 是速度-精度双旋钮：先保证全找到（greediness=0、降 min_score），再提速度。
4. 训练图与生产图光照/极性：用 `'ignore_global_polarity'`/`'ignore_color_polarity'` 适配反转。
5. `'num_matches'` 每层截断候选会丢"高层分低但低层分高"实例——多返回几个再挑最高分。
6. 训练前 `inspect_shape_model` 检查金字塔；去杂波用滞后阈值/环形 ROI/`opening_circle`+`fill_up`。
7. 透视场景若沿用同一视角，先**校直图像**再做 shape matching，比 perspective matching 更快更准。

---

## 八、引用
- 中文算子总览：`references/ops_07_Matching.md`、`ops_12_3DMatching.md`
- 逐算子签名/默认值：`references/ref_OPERATOR_REFERENCE.md`（Matching 章）。
- 关联：`halcon-measuring-metrology`（对齐后测量）、`halcon-calibration`（标定版位姿）、`halcon-3d-vision`（3D 匹配）、`halcon-image-preprocessing`（ROI/预处理）。


---

## 用例参考（example_*.md）

本 skill 目录下 `references/` 含以下项目里抽出的真实用例（按主题归档，可直接借鉴实现思路/算子组合）：

- `references/example_correlation_deformable_matching.md`
- `references/example_shape_matching.md`
