# HALCON 算子分类详解：XLD

> **分类**：XLD（eXtended Line Descriptions，亚像素轮廓）
> **子类数**：7（Access / Creation / Features / Geometric / Sets / Transformations / Misc）
> **学习优先级**：⭐⭐⭐⭐（高精度测量的灵魂，所有亚像素级几何拟合的基石）
> **典型应用场景**：从像素级边缘中提取亚像素轮廓（精度 0.01 px 量级），并用代数/鲁棒算法拟合圆、直线、椭圆、矩形，用于精密机械与汽车零部件的尺寸与形位公差测量。

---

## 1. 概述

XLD（eXtended Line Descriptions）是 HALCON 特有的**亚像素轮廓数据结构**。与 Region（像素级集合）不同，XLD 用连续浮点坐标表达物体边缘，因此可以在 0.01 像素量级描述曲线。在 HALCON 体系内，XLD 处于"上游边缘算子"（`edges_sub_pix`）与"下游测量/拟合算子"（`fit_circle_contour_xld`、`distance_*`）之间，是高精度测量（2D Metrology、1D Measuring、GD&T 形位公差）的基础。

XLD 与其他分类的关系：

- **来源**：从 Filters（`edges_sub_pix`、`lines_gauss`）或 Regions（`gen_contour_region_xld`、`boundary`）得到。
- **特征计算**：XLD 拥有与 Region 类似的几何/拓扑特征（`area_center_xld`、`circularity_xld` 等），可作为 Region 的"高精度替代品"。
- **拟合输出**：XLD 经拟合（`fit_*_contour_xld`）后回退到 Region（`gen_*_contour_xld`）或直接得到几何参数。
- **匹配输入**：XLD 也可以作为 Shape Model（`create_shape_model_xld`）的输入。

---

## 2. 应用场景

1. **精密机械零件尺寸检测**：轴承内外圈直径、键槽宽度、孔位间距。
2. **PCB 线路与焊盘测量**：线宽、线距、焊盘圆度。
3. **玻璃/金属边缘定位**：亚像素级直线度、平行度、垂直度。
4. **汽车零部件形位公差**：圆度、圆柱度、直线度、对称度（GD&T 符号）。
5. **注塑件轮廓度**：自由曲线到 CAD 的最佳拟合偏差。

---

## 3. 子分类详解

| 子分类 | 职责 | 代表算子 |
|--------|------|----------|
| **Access** | 读取 XLD 的点坐标与属性 | `get_contour_xld`、`get_lines_xld`、`get_polygon_xld`、`get_contour_angle_xld`、`get_contour_attrib_xld`、`get_contour_global_attrib_xld`、`get_regress_params_xld` |
| **Creation** | 从区域、点云、几何参数、NURBS 等生成 XLD | `gen_contour_region_xld`、`gen_polygons_xld`、`gen_contour_polygon_xld`、`gen_rectangle2_contour_xld`、`gen_circle_contour_xld`、`gen_ellipse_contour_xld`、`gen_contour_nurbs_xld`、`gen_parallels_xld`、`read_contour_xld_arc_info/dxf` |
| **Features** | XLD 的几何/拓扑特征 | `area_center_xld`、`length_xld`、`circularity_xld`、`compactness_xld`、`convexity_xld`、`eccentricity_xld`、`elliptic_axis_xld`、`orientation_xld`、`moments_*_xld`、`smallest_circle_xld`、`smallest_rectangle1/2_xld`、`fit_circle/line/ellipse/rectangle2_contour_xld` |
| **Geometric** | 几何变换 | `affine_trans_contour_xld`、`polar_trans_contour_xld`、`projective_trans_contour_xld` |
| **Sets** | 集合运算 | `intersection_contours_xld`、`union2_closed_contours_xld`、`difference_closed_contours_xld`、`symm_difference_closed_contours_xld`、`test_closed_xld`、`test_self_intersection_xld` |
| **Transformations** | 简化/平滑/合并/分割 | `approx_chain`、`approx_chain_simple`、`clip_contours_xld`、`crop_contours_xld`、`merge_cont_line_scan_xld`、`regress_contours_xld`、`segment_contours_xld`、`segment_contour_attrib_xld`、`smooth_contours_xld`、`sort_contours_xld`、`split_contours_xld`、`union_adjacent_contours_xld`、`union_collinear_contours_xld`、`union_cocircular_contours_xld`、`union_cotangential_contours_xld`、`union_straight_contours_xld`、`shape_trans_xld` |
| **Misc** | 其他 | `local_max_contours_xld` |

---

## 4. 核心算子详解

| 算子 | 用途 | 输入 | 输出 | 典型用法 |
|------|------|------|------|----------|
| `edges_sub_pix` | 亚像素 Canny 边缘 | Image, Filter, Alpha, Low, High | Edges | XLD 的主要来源之一 |
| `gen_contour_region_xld` | 区域边界转 XLD | Region | Contour | Region→XLD 桥接 |
| `gen_contour_polygon_xld` | 多边形顶点序列→XLD | Row, Col | Contour | 标定板、ROI 边缘 |
| `gen_circle_contour_xld` | 圆几何参数→XLD | Row, Col, Radius | Contour | 可视化拟合结果 |
| `gen_ellipse_contour_xld` | 椭圆几何参数→XLD | Row, Col, Phi, Ra, Rb | Contour | 拟合结果可视化 |
| `gen_rectangle2_contour_xld` | 矩形几何参数→XLD | Row, Col, Phi, L1, L2 | Contour | 拟合结果可视化 |
| `length_xld` | XLD 长度 | XLD | Length | 圆周、轮廓长度 |
| `area_center_xld` | 闭轮廓面积 + 质心 | XLD | Area, Row, Col | 重心定位 |
| `smallest_circle_xld` | 最小包围圆 | XLD | Row, Col, Radius | 等效直径 |
| `smallest_rectangle1_xld` | 轴对齐最小矩形 | XLD | Row1, Col1, Row2, Col2 | 包围盒 |
| `smallest_rectangle2_xld` | 任意朝向最小矩形 | XLD | Row, Col, Phi, L1, L2 | 旋转 ROI |
| `fit_line_contour_xld` | 直线鲁棒拟合 | XLD, Algorithm, MaxNumPoints, ClippingEndPoints, Iterations, ClippingFactor | RowBegin, ColBegin, RowEnd, ColEnd, Nr, Nc, Dist | 测量边长 |
| `fit_circle_contour_xld` | 圆鲁棒拟合 | XLD, Algorithm, MaxNumPoints, MaxClosingDist, MaxClosingAngle, Iterations, ClippingFactor | Row, Col, Radius, StartPhi, EndPhi, PointOrder | 圆孔直径 |
| `fit_ellipse_contour_xld` | 椭圆鲁棒拟合 | XLD, Algorithm, MaxNumPoints, MaxClosingDist, Iterations, ClippingFactor | Row, Col, Phi, Ra, Rb, StartPhi, EndPhi, PointOrder | 椭圆零件 |
| `fit_rectangle2_contour_xld` | 矩形鲁棒拟合 | XLD, Algorithm, MaxNumPoints, MaxClosingDist, Iterations, ClippingFactor | Row, Col, Phi, L1, L2 | 矩形零件 |
| `segment_contours_xld` | 按方向突变拆线 | XLD, Mode, SmoothCont, MaxLineDist1, MaxLineDist2 | Contours | 拆分多段折线 |
| `select_contours_xld` | 按属性筛选 | XLD, Feature, Min1, Max1, Min2, Max2 | SelectedContours | 长度/曲率过滤 |
| `smooth_contours_xld` | XLD 平滑（高斯） | XLD, NumRegressPoints | SmoothedContours | 减少拟合噪声 |
| `approx_chain` | Douglas–Peucker 简化 | XLD, Mode, MaxDist | ApproxContour | 减少 XLD 点数 |
| `union_collinear_contours_xld` | 共线段合并 | XLD, MaxDistAbs, MaxDistRel, MaxShift, MaxAngle, Mode | UnionContours | 拼接直线段 |
| `union_cocircular_contours_xld` | 共弧段合并 | XLD, MaxArcAngleDiff, MaxDist, MaxRadiusDiff, MaxTangentAngle | UnionContours | 拼接圆弧段 |
| `get_contour_global_attrib_xld` | 读全局属性 | XLD, Name | Attrib | 读 `regr_norm_*` 残差 |
| `regress_contours_xld` | 沿法线方向回归 | XLD, Mode, Iterations | RegressContours | 局部宽度/方向 |
| `affine_trans_contour_xld` | 仿射变换 | XLD, HomMat2D | ContoursTrans | 坐标对齐 |
| `test_closed_xld` | 是否闭合 | XLD | IsClosed | 闭合检测 |
| `test_self_intersection_xld` | 是否自交 | XLD | IsSelfIntersection | 闭合自检 |
| `clip_contours_xld` | 裁剪到 ROI | XLD, ROI | ClippedContours | 限定测量范围 |
| `crop_contours_xld` | 矩形裁剪 | XLD, Row1, Col1, Row2, Col2 | CroppedContours | 区域提取 |
| `polar_trans_contour_xld` | 极坐标变换 | XLD, Row, Col, RadiusStart, RadiusEnd, AngleStart, AngleEnd, Direction, Width, Height | PolarTransContour | 圆环展开 |

---

## 5. HDevelop 示例代码

### 示例 1：亚像素直线拟合（边缘→线段→参数）

**场景**：金属板边缘直线度测量。
**功能**：`edges_sub_pix` 提取亚像素边缘 → `segment_contours_xld` 拆分 → `fit_line_contour_xld` 用 `'tukey'` 鲁棒算法拟合。
**预期输出**：直线的起点、终点、方向向量及平均残差，叠加显示在图上。

```hdevelop
* ============================================================
* 示例1：亚像素直线拟合（直线度/平行度基础）
* ============================================================
dev_update_off ()
dev_close_window ()
read_image (Image, 'metal_part_cyl/metal_part_cyl_01')
get_image_size (Image, Width, Height)
dev_open_window (0, 0, Width / 2, Height / 2, 'black', WindowHandle)
dev_display (Image)

* 1) 提取亚像素边缘
edges_sub_pix (Image, Edges, 'canny', 1.0, 20, 40)

* 2) 按方向突变拆分成多段线
segment_contours_xld (Edges, SegmentedContours, 'lines', 5, 4, 3)

* 3) 选段长 > 50 px 的线
select_contours_xld (SegmentedContours, SelectedContours, 'length', 50, 99999, 0, 0)

* 4) 用 Tukey 鲁棒算法拟合（抗离群点）
count_obj (SelectedContours, NumSegments)
for i := 1 to NumSegments by 1
    select_obj (SelectedContours, SingleContour, i)
    fit_line_contour_xld (SingleContour, 'tukey', -1, 0, 5, 2, \
                          RowBegin, ColBegin, RowEnd, ColEnd, Nr, Nc, Dist)
    dev_set_color ('green')
    dev_set_line_width (2)
    disp_line (WindowHandle, RowBegin, ColBegin, RowEnd, ColEnd)
    dev_set_color ('yellow')
    disp_text (WindowHandle, 'Dist=' + Dist$'.3f', 'window', RowBegin, ColBegin, \
               'black', 'box', 'false')
endfor

dev_set_line_width (1)
dev_update_on ()
stop ()
```

### 示例 2：圆孔直径测量（鲁棒圆拟合）

**场景**：法兰盘上圆孔直径亚像素测量。
**功能**：`edges_sub_pix` → `gen_contour_region_xld` ROI 提取 → `fit_circle_contour_xld` 用 `'huber'` 拟合。
**预期输出**：圆心坐标、半径，叠加可视化圆与直径文本。

```hdevelop
* ============================================================
* 示例2：圆孔直径亚像素测量
* ============================================================
dev_update_off ()
dev_close_window ()
read_image (Image, 'pads/pad_01')
get_image_size (Image, Width, Height)
dev_open_window (0, 0, Width / 2, Height / 2, 'black', WindowHandle)
dev_display (Image)

* 1) 简单阈值得到孔 region（按图实际调整）
threshold (Image, Region, 100, 255)
connection (Region, ConnectedRegions)
select_shape (ConnectedRegions, HoleRegion, ['area','circularity'], 'and', [200, 0.7], [9999, 1.0])

* 2) Region → 亚像素轮廓
gen_contour_region_xld (HoleRegion, Contour, 'border')

* 3) 鲁棒圆拟合（huber 比 algebraic 更稳）
fit_circle_contour_xld (Contour, 'huber', -1, 2, 2, 3, 2, \
                        Row, Column, Radius, StartPhi, EndPhi, PointOrder)

* 4) 可视化
gen_circle_contour_xld (ResultContour, Row, Column, Radius, 0, 6.28318, 'positive', 1)
dev_set_color ('red')
dev_set_line_width (3)
dev_display (ResultContour)
dev_set_color ('yellow')
disp_text (WindowHandle, 'R=' + Radius$'.3f' + '  D=' + (2*Radius)$'.3f', \
           'window', Row - 30, Column - 60, 'black', 'box', 'false')
dev_set_line_width (1)
dev_update_on ()
stop ()
```

### 示例 3：合并共线段并拟合（多段折线→一条直线）

**场景**：折角边缘被亚像素边缘切分成了多条短折线。
**功能**：`union_collinear_contours_xld` 合并共线段 → `fit_line_contour_xld` 整体拟合。
**预期输出**：一条贯穿所有原始线段的最优直线。

```hdevelop
* ============================================================
* 示例3：合并共线段再拟合
* ============================================================
dev_update_off ()
dev_close_window ()
read_image (Image, 'rings/rings_01')
get_image_size (Image, Width, Height)
dev_open_window (0, 0, Width / 2, Height / 2, 'black', WindowHandle)
dev_display (Image)

* 1) 边缘 + 拆分
edges_sub_pix (Image, Edges, 'canny', 1.5, 10, 30)
segment_contours_xld (Edges, Segments, 'lines', 5, 3, 3)

* 2) 保留长段
select_contours_xld (Segments, LongSegments, 'length', 30, 99999, 0, 0)

* 3) 合并共线段（最大间距 5 px，最大角度 0.1 rad）
union_collinear_contours_xld (LongSegments, UnionContours, 5, 2, 0.1, 0.1, 'attr_keep')

* 4) 显示被合并的线 + 全局拟合直线
count_obj (UnionContours, NumLines)
dev_set_color ('green')
dev_set_line_width (2)
for i := 1 to NumLines by 1
    select_obj (UnionContours, C, i)
    fit_line_contour_xld (C, 'tukey', -1, 0, 5, 2, \
                          RowBegin, ColBegin, RowEnd, ColEnd, _, _, _)
    disp_line (WindowHandle, RowBegin, ColBegin, RowEnd, ColEnd)
endfor

dev_set_line_width (1)
dev_update_on ()
stop ()
```

---

## 6. 典型工业流水线

### 流水线 A：精密零件尺寸全检

```
grab_image
  → gauss_filter (去噪)
  → edges_sub_pix (亚像素 Canny)
  → segment_contours_xld (按方向拆分)
  → select_contours_xld (按长度过滤)
  → fit_line_contour_xld / fit_circle_contour_xld
  → distance_pp / distance_pl
  → 判定 + 写数据库
```

### 流水线 B：基于 XLD 的对位引导

```
read_image
  → edges_sub_pix
  → shape_trans_xld ('convex')
  → smallest_rectangle2_xld (主轴方向)
  → affine_trans_contour_xld (旋转到参考姿态)
  → find_shape_model (基于参考轮廓训练)
  → vector_angle_to_rigid → 引导机械手
```

### 流水线 C：圆弧/直线混合拟合

```
edges_sub_pix
  → segment_contours_xld (按 'lines_circles' 模式)
  → union_collinear_contours_xld (合并共线)
  → union_cocircular_contours_xld (合并共弧)
  → fit_line_contour_xld / fit_circle_contour_xld
  → get_contour_global_attrib_xld ('regr_norm_mean', 'regr_norm_deviation')
  → 残差超限报警
```

---

## 7. 常见陷阱与最佳实践

1. **拟合算法选错 = 灾难**：`'algebraic'` 速度最快但对噪声敏感；含噪场景必须 `'huber'` / `'tukey'`，极端噪声（> 20% 离群点）用 `'drop'`。
2. **`edges_sub_pix` 的 `Sigma`** 过大导致边缘模糊、过小则噪声敏感；典型 1.0–2.0。
3. **`fit_*_contour_xld` 的 `ClippingEndPoints`** 仅在拟合开放直线时生效（圆/椭圆无端点），常被混淆。
4. **`union_collinear_contours_xld` 前必须先 `segment_contours_xld`**：原始长 XLD 不带端点信息。
5. **`gen_contour_region_xld(Region, Contour, 'border')`** 的 `'border'` 是外边界；若需内孔要先 `boundary` + `fill_up_shape`。
6. **`smallest_rectangle1_xld` 与 `smallest_rectangle2_xld`** 一个是轴对齐、一个是任意朝向；测量形位公差时必须用 `*_2`。
7. **XLD 永远不要 `concat_obj` 后再 `select_obj` 索引超界**——空对象集会让 `count_obj` 返回 0。
8. **拟合前用 `smooth_contours_xld` 平滑**可以稳定残差，但会损失端点细节；推荐 3–5 个回归点。

---

## 8. 参数调优指南

| 算子 | 关键参数 | 推荐值 | 调整策略 |
|------|----------|--------|----------|
| `edges_sub_pix` | `Sigma` | 1.0–2.0 | 噪声大→上调；细节多→下调 |
| `edges_sub_pix` | `Low` / `High` | 10–20 / 30–50 | 高对比图调高；弱边缘调低 |
| `fit_line_contour_xld` | `Algorithm` | `'tukey'` | 噪声大用 tukey/huber；少噪用 algebraic 提速 |
| `fit_line_contour_xld` | `ClippingFactor` | 2.0 | tukey 越大越鲁棒（典型 1.5–3.0） |
| `fit_circle_contour_xld` | `MaxClosingDist` | 1.0–3.0 | 弧段缺口大时上调 |
| `fit_circle_contour_xld` | `MaxClosingAngle` | 0.1–0.3 | rad；半圆/圆弧残缺时上调 |
| `fit_circle_contour_xld` | `Algorithm` | `'huber'` | 抗离群点首选 |
| `segment_contours_xld` | `Mode` | `'lines'` / `'lines_arcs'` | 含弧用后者 |
| `segment_contours_xld` | `MaxLineDist1` | 3–5 | 越大越容易合并 |
| `union_collinear_contours_xld` | `MaxDistAbs` | 2–10 | 按像素比例；分辨率越高越大 |
| `union_collinear_contours_xld` | `MaxAngle` | 0.1–0.2 rad | 越大越宽松 |
| `smooth_contours_xld` | `NumRegressPoints` | 3–7 | 奇数；越大越平滑 |
| `approx_chain` | `MaxDist` | 1.0–2.0 | 越大点数越少 |

---

## 9. 相关分类

- **Filters**：`edges_sub_pix`、`lines_gauss` 是 XLD 的主要来源。
- **Regions**：XLD 是 Region 的高精度替代，`gen_contour_region_xld` 是桥接。
- **1D Measuring**：`measure_pairs`、`measure_pos` 也是亚像素测量，但基于灰度投影。
- **2D Metrology**：高阶测量框架，底层也会用 XLD 拟合输出结果。
- **Matching**：`create_shape_model_xld` 可以从 XLD 直接创建模板。
- **Graphics**：`disp_xld` / `disp_polygon` 用于 XLD 可视化。

---

## 10. 学习小结

XLD 是 HALCON 中"**精度**"的代名词。其核心要点：

1. **5 种拟合算法**（`algebraic` / `huber` / `tukey` / `gauss` / `drop`）必须理解：噪声大用 `tukey` / `drop`、少噪用 `algebraic` 提速、平衡选 `huber`。
2. **三种合并**（`union_collinear` / `union_cocircular` / `union_cotangential`）是处理"被边缘切碎的轮廓"的关键。
3. **闭合性判定**（`test_closed_xld`）与 **自交检测**（`test_self_intersection_xld`）是拟合前的必备检查。
4. **XLD 属性**（`get_contour_global_attrib_xld`）可以读出回归残差，是测量合格判定的一手数据。
5. 与 Region 相比，XLD 适合**亚像素精度 + 几何形态描述**，不适合做连通域/形态学运算（这类仍应回到 Region）。
