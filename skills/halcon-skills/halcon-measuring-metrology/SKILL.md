---
name: halcon-measuring-metrology
description: >-
  HALCON dimensional measurement: 1D caliper measuring (gen_measure_rectangle2 /
  gen_measure_arc, measure_pos, measure_pairs, measure_thresh, measure_projection,
  fuzzy_measure_pairs), 2D metrology models (create_metrology_model,
  add_metrology_object_circle/ellipse/rectangle2/line_measure, apply_metrology_model,
  get_metrology_object_result), 2D-measuring tool selection (Region vs Contour vs
  Metrology vs Geometric Operations), and measuring in world coordinates. Use this
  skill whenever a HALCON/HDevelop task measures a distance, width, angle, radius,
  position or orientation of an object — caliper measurements on a line/arc, fitting
  circles/lines/rectangles to edges with subpixel precision, tolerances, or
  multi-feature metrology models. Trigger on gen_measure_rectangle2 / measure_pairs /
  create_metrology_model / add_metrology_object_* / apply_metrology_model,
  Sigma / Threshold / Transition / measure_select tuning, or when deciding whether to
  use Region processing, Contour processing, or a Metrology model for a measurement.
---

# HALCON 测量（1D 卡尺 / 2D 计量 / 世界坐标）

> 定位：把"要测什么特征"落到正确的测量工具，输出可用的尺寸/角度/位姿。
> 四大基本工具：Region Processing、Contour Processing、2D Metrology、Geometric Operations（见 `halcon-edge-contour` 与 `halcon-image-preprocessing`）。
> 编写规范见 `../_authoring/`（conventions.md 为精简总结；完整规范在 halcon_skill.md；脚本格式/CLI 见同名 *_reference.md）。

---

## 一、工具选择（从"特征+外观"到工具）

| 要测什么 | 对象外观 | 用哪个 |
|---|---|---|
| 面积/尺寸 | 同类灰度/颜色/纹理区域 | **Region Processing**（`halcon-image-preprocessing`） |
| 面积/尺寸 | 清晰边缘、轮廓可分解为简单形状、需亚像素 | **Contour Processing**（`halcon-edge-contour`） |
| 面积/尺寸/位置 | 简单形状且参数近似已知 | **2D Metrology** |
| 朝向/位置/数量 | 同一复杂形状 | **Matching**（`halcon-matching`） |
| 垂直于线/弧的边缘位置/距离 | 边缘近似垂直 | **1D Measuring** |
| 角/距（对象间） | 由已得朝向/位置计算 | **Geometric Operations** |

**Region vs Contour 关键差异**：Contour 可亚像素、能抗离群点（`'tukey'`）、开放+闭合均可、只依赖过渡；Region 快得多、像素级、对象须整域满足灰度约束、对差对比鲁棒。需要精度/开放轮廓/抗离群 → Contour；追求速度/整域同类灰度/像素精度够 → Region。

---

## 二、1D Measuring（卡尺）

### 创建 Measure Object（用数值坐标，**不用 reduce_domain**）
```hdevelop
gen_measure_rectangle2 (Row, Column, Phi, Length1, Length2, Width, Height, Interpolation, MeasureHandle)
gen_measure_arc (CenterRow, CenterCol, Radius, AngleStart, AngleExtent, AnnulusRadius, Width, Height, Interpolation, MeasureHandle)
```
- `Length1`=沿测量线半长；`Length2`=垂直方向半宽（ROI 宽度=2·Length2）；`Interpolation`=`'bilinear'`（折中）/`'nearest_neighbor'`（快）/`'bicubic'`（最精最慢，边距≥2px）。

### 四种操作
```hdevelop
* 边上无  位置（单边）
measure_pos (Image, MeasureHandle, Sigma, Threshold, Transition, Select, RowEdge, ColEdge, Amp, Distance)
* 边缘对（对象被两条边界包围）→ 三线宽
measure_pairs (Image, MeasureHandle, Sigma, Threshold, Transition, Select, RowE1,ColE1,A1, RowE2,ColE2,A2, IntraDist, InterDist)
* 特定灰度值点
measure_thresh (Image, MeasureHandle, GrayThreshold, Select, RowEdge, ColEdge)
* 灰度剖面（未平滑 tuple）
measure_projection (Image, MeasureHandle, GrayValues)
```
| 参数 | 含义 | 典型值 |
|---|---|---|
| `Sigma` | profile 高斯平滑σ | 0.3~3（越大越稳，弱边被抑制） |
| `Threshold` | 一阶导数阈值（选边缘） | 10~40 |
| `Transition` | `'negative'`/`'positive'`/`'all'`；可加 `'_strongest'` | 边缘对：negative=包围暗区 |
| `Select` | `'all'`/`'first'`/`'last'` | `'all'` 常用 |

- **`Transition`+`'_strongest'`**：同一 transition 多条连续边缘时只取最强（避免宽 ROI 同向序列误取）。
- 边缘对中心：`RowCenter := (RowE1+RowE2)/2`。
- **坑**：measure 工具忽略图像 domain；不适合弯曲边缘（若需，减小 ROI 宽度）。

### 边缘对中心 / 世界坐标 / 对齐
- 世界坐标：`image_points_to_world_plane(CamParam, WorldPose, Row, Col, 'mm', X, Y)` + `distance_pp`。
- 镜头畸变：修正图像坐标或 rectifiy（见 `halcon-calibration`）。
- 对齐：仅平移用 `translate_measure(MeasureHandle,Row,Column,HandleTrans)`；平移+旋转用 shape-based 匹配结果重算并新建 measure。

### Fuzzy Measure Object（控制边缘选择）
- 用 `set_fuzzy_measure(Handle, SetType, MembershipFunc)` 或 `set_fuzzy_measure_norm_pair(Handle, PairSize, SetType, NormFunc)`；函数用 `create_funct_1d_pairs(X,Y,Func)` 建分段线性。
- 应用：`fuzzy_measure_pos`/`fuzzy_measure_pairs(..., Sigma, AmpThresh, FuzzyThresh, Transition, ...)`，`FuzzyThresh`（典型 0.5）典型仅调这个。
- SetType/Subtype：`contrast`、`position`(及 `_center`/`_end`/`_first_edge`/`_last_edge`)、`position_pair`、`size`(及 `_diff`/`_abs_diff`)、`gray`。**同一 set type 只能一个 subtype**；多个 set type 用**几何平均**聚合。
- **坑**：边缘对会分析所有可能对，只指定 position 不指定 size 可能漏掉小对（大对优先）→ 建议同时指定 `position_pair`+`size`。

---

## 三、2D Metrology（参数近似已知的简单形状）

```hdevelop
create_metrology_model (MetrologyHandle)
set_metrology_model_image_size (MetrologyHandle, Width, Height)
add_metrology_object_rectangle2_measure (MetrologyHandle, Row,Col,Phi, L1,L2, Tolerance, MLen1,MLen2,Sigma,Thresh,Select, Index)
add_metrology_object_circle_measure        (MetrologyHandle, Row,Col,Radius, RadiusTol, MLen1,MLen2,Sigma, Index)
apply_metrology_model (Image, MetrologyHandle)
get_metrology_object_result (MetrologyHandle, Index, 'all', 'result_type', 'all_param', Param)
```
- 形状：`add_metrology_object_{circle,ellipse,line,rectangle2}_measure`；`add_metrology_object_generic` 一次加多种；无 `_measure` 版用 `set_metrology_object_param` 设测量参数。
- 常用测量参数（`set_metrology_object_param`）：`'measure_length1'`/`'measure_length2'`/`'measure_sigma'`(1.0)/`'measure_threshold'`(30.0)/`'measure_select'`(`'all'`)/`'measure_transition'`(`'all'`)/`'measure_interpolation'`/`'min_score'`(0.3)/`'num_measures'`(1)/`'measure_direction'`。
- 结果：`get_metrology_object_result(... 'all_param')`；模型轮廓 `get_metrology_object_model_contour`;测量区 `get_metrology_object_measures`。
- **对齐 Metrology Model**（3 种，参考 `measure_stamping_part.hdev`）：
  1. **Shape-based matching**：`create_generic_shape_model`+`train_...`，设 `set_metrology_model_param(H,'reference_system',[RowModel,ColumnModel,0])`；在线 `find_generic_shape_model`+取 angle → `align_metrology_model(H, Row,Column,Angle)`。
  2. **Region processing**：`area_center`+`orientation_region` 求参考位姿。
  3. **Rigid（点对应）**：`vector_to_rigid` + `hom_mat2d_to_affine_par`。

---

## 四、Geometric Operations（点/线/距/交）

- 距离：`distance_pp`/`distance_pl`/`distance_ps`/`distance_pc`/`distance_sl`/`distance_ss`/`distance_sc`/`distance_cc`/`distance_lc`/`distance_pr`。
- 角/交点/投影：`angle_ll`（两线夹角）、`angle_lx`（线与竖直轴）、`intersection_lines`、`projection_pl`。
- 仿射：`area_center`+`orientation_region` → `vector_angle_to_rigid(Row,Col,AngleSrc, Row,Col,AngleDst, HomMat2D)` → `affine_trans_region`/`affine_trans_contour_xld`/`affine_trans_pixel`。

---

## 五、典型实例 work
| 实例 | 流程 |
|---|---|
| 螺丝纹宽 | 旋转对齐→逐行测宽：`threshold`+`orientation_region`+`area_center`+`vector_angle_to_rigid`+`affine_trans_region` → `closing_circle`+`get_region_runs` → mean/min |
| 直线边距 | (a) 线拟合+`distance_pp`；(b) `gen_polygons_xld('ramer')`+`gen_parallels_xld`+`get_parallels_xld`；(c) `smallest_rectangle2`(Length=半距) |
| 圆半径/圆弧 | `fast_threshold`+`segment_contours_xld('lines_circles')`+`union_cocircular_contours_xld`+`fit_circle_contour_xld('algebraic')` |
| BGA 球 | 对称小物体用**灰度矩**：`fast_threshold`+`area_center_gray`+`elliptic_axis_gray`；归一化网格排布比对 |
| 矩形位姿 | `fast_threshold`+`opening_rectangle1`+`select_shape('rectangularity')`+`smallest_rectangle2`+`edges_sub_pix`+`union_adjacent_contours_xld`+`fit_rectangle2_contour_xld('tukey')` |

---

## 六、常见陷阱
1. Measure ROI 用数值坐标，不用 `reduce_domain`。
2. `measure_pairs` 的 `Transition` 对边缘对=边缘包围性质（negative=暗区）；同向连续用 `'_strongest'`。
3. Fuzzy：隶属函数定义与应用阈值（`FuzzyThresh`）分离；同 set type 单 subtype；建议 position_pair+size 同设。
4. Measure 不适合弯曲边缘。
5. 世界坐标测量：**轮廓处理→先测后转世界**（`contour_to_world_plane_xld`）；**区域处理→先校正图像再测**（`gen_image_to_world_plane_map`+`map_image`）。
6. `orientation_region` 返回 ±180°，`smallest_rectangle2` 返回 ±90°，两者算法不同。
7. 控制元组从 0 开始，图标元组（`count_obj`）从 1 开始。

---

## 七、引用
- 中文算子总览：`references/ops_28_2DMetrology.md`、`ops_29_1DMeasuring.md`、`ops_19_Transformations.md`
- 逐算子签名/默认值：`references/ref_OPERATOR_REFERENCE.md`（1D_Measuring / 2D_Metrology / Transformations 章）。
- 关联：`halcon-edge-contour`（亚像素边缘/拟合）、`halcon-calibration`（世界坐标）、`halcon-matching`（对齐）、`halcon-image-preprocessing`（区域/Blob）。


---

## 用例参考（example_*.md）

本 skill 目录下 `references/` 含以下项目里抽出的真实用例（按主题归档，可直接借鉴实现思路/算子组合）：

- `references/example_geometric_transforms.md`
- `references/example_measuring_metrology.md`
