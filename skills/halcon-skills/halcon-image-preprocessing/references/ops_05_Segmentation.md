# HALCON 算子分类详解：Segmentation（分割）

> **分类**：Segmentation 分割
> **子类数**：7 个（Classification、Edges、MSER、Region Growing、Threshold、Topography、Misc）
> **算子数**：约 110 个
> **学习优先级**：⭐⭐⭐⭐（阈值解决不了时的进阶武器）
> **典型应用场景**：光照不均场景、多目标复杂粘连、纹理区域分离、自然场景文字/Logo 提取、地形/医学图像水域分割——当传统固定阈值无能为力时的核心算法库。

---

## 1. 概述

**Segmentation 分类在 HALCON 体系中的定位**

Segmentation 是 Image/Filters 之后，Regions 之前的"过渡层"，把图像转为有意义的 Region。它覆盖了比"固定阈值"更复杂的场景：

1. **阈值类**：从最简单的全局 `threshold` 到自适应 `local_threshold`、动态 `dyn_threshold`、双阈值 `hysteresis_threshold`。
2. **区域生长类**：`regiongrowing` / `regiongrowing_mean` 等基于像素相似性扩散。
3. **分水岭类**：`watersheds` / `watersheds_marker` / `watersheds_threshold` 处理粘连多目标。
4. **MSER 类**：`segment_image_mser` 自然场景文本/Logo 检测。
5. **边缘类**：`detect_edge_segments` / `zero_crossing` 等基于边缘的分割。
6. **拓扑类**：`local_max` / `local_min` / `critical_points_sub_pix` / `plateaus` / `lowlands`。
7. **分类类**：基于 N 维特征的像素级分类（`class_ndim_norm`）。

**与其他分类的关系**

- **上游**：从 **Image** + **Filters** 接收图像。
- **下游**：输出 Region 给 **Regions**（后处理、特征统计）；输出 XLD 给 **XLD**（高精度边缘）。
- **平行**：与 **Morphology** 紧密合作（开闭运算清理）；与 **Filters**（Canny 边缘）有重叠。

**为什么 Segmentation 重要**

简单项目用 `threshold` 即可。但工业现场 60% 的项目有**光照不均、噪声干扰、多目标粘连**等问题——这些场景必须靠分割算法解决。`dyn_threshold` + `regiongrowing_mean` + `watersheds_marker` 几乎是工业 AOI 项目的三大法宝。

---

## 2. 应用场景

### 场景 A：PCB AOI 缺陷分割
- **行业**：3C 电子
- **问题**：PCB 焊点缺陷（短路、缺锡、虚焊）需在光照不均背景下分割。
- **算法选择**：`mean_image`（生成参考图）→ `dyn_threshold`（动态阈值）→ `connection` → `select_shape`。
- **期望产出**：缺陷 Region。

### 场景 B：医学细胞计数
- **行业**：医学影像
- **问题**：血细胞粘连成团，难以计数。
- **算法选择**：`watersheds_marker`（带强制标记的分水岭）→ `select_shape` → `count_obj`。
- **期望产出**：独立细胞 Region + 数量。

### 场景 C：金属表面磨痕
- **行业**：金属加工
- **问题**：金属表面磨痕（细长暗线）需提取。
- **算法选择**：`local_threshold`（局部自适应阈值）→ `connection` → `select_shape`（长宽比过滤）。
- **期望产出**：磨痕二值图。

### 场景 D：自然场景文字提取
- **行业**：文档数字化
- **问题**：自然场景中文字（Logo/标牌）需识别。
- **算法选择**：`segment_image_mser`（MSER 最大稳定极值区域）。
- **期望产出**：候选文字 Region。

### 场景 E：遥感图像水域分割
- **行业**：地理信息
- **问题**：卫星图中的河流、湖泊分割。
- **算法选择**：`threshold`（NDVI 指数）→ `watersheds`（细化边界）。
- **期望产出**：水域 Region。

### 场景 F：地形图等高线
- **行业**：地理信息
- **问题**：从 DEM（高程图）提取等高线。
- **算法选择**：`zero_crossing_sub_pix`（过零点）→ `gen_contours_skeleton_xld`。
- **期望输出**：等高线 XLD。

---

## 3. 子分类详解

| 子类 | 算子数 | 代表算子 | 用途速览 |
|------|-------|---------|---------|
| **Classification** | ~5 | `class_ndim_norm`, `learn_ndim_norm`, `class_2dim_sup`, `class_2dim_unsup`, `learn_ndim_norm_protected` | 基于 N 维特征的像素分类 |
| **Edges** | ~10 | `detect_edge_segments`, `zero_crossing`, `zero_crossing_sub_pix`, `watersheds`, `watersheds_marker`, `watersheds_threshold` | 基于边缘的分割 |
| **MSER** | ~3 | `segment_image_mser`, `segment_image_mser_gray`, `set_mser_params` | 最大稳定极值区域 |
| **Region Growing** | ~5 | `regiongrowing`, `regiongrowing_mean`, `regiongrowing_n`, `regiongrowing_label` | 基于相似性的区域生长 |
| **Threshold** | ~15 | `threshold`, `auto_threshold`, `binary_threshold`, `char_threshold`, `check_difference`, `dual_threshold`, `dyn_threshold`, `fast_threshold`, `global`, `hysteresis_threshold`, `local_threshold`, `var_threshold`, `bin_threshold`, `histo_to_thresh` | 各类阈值分割 |
| **Topography** | ~15 | `critical_points_sub_pix`, `local_max`, `local_max_sub_pix`, `local_min`, `local_min_sub_pix`, `plateaus`, `plateaus_center`, `lowlands`, `lowlands_center`, `saddle_points_sub_pix`, `topographic_sketch` | 拓扑特征提取 |
| **Misc** | ~5 | `class_ndim_norm_protected` 等辅助算子 | 杂项 |

---

## 4. 核心算子详解

1. **threshold** — 全局固定阈值 / 输入：`Image, Region, MinGray, MaxGray`；最基础。
2. **binary_threshold** — Otsu 自动阈值 / 输出二值 Region。
3. **auto_threshold** — 多阈值分割（用于多目标）。
4. **fast_threshold** — 快速阈值（无参数检查，比 `threshold` 略快）。
5. **dyn_threshold** — 动态阈值 / 输入：`Image, ImageReference, Region, Offset, LightDark`；处理光照不均。
6. **local_threshold** — 局部自适应阈值 / 输入：`Image, Region, Method, MaskSize → RegionLocal`。
7. **var_threshold** — 基于方差的阈值 / 处理纹理背景。
8. **hysteresis_threshold** — 双阈值（高/低）+ 连接性 / Canny 风格阈值。
9. **dual_threshold** — 双段阈值 / 输入：`Image, Region1, MinSize1, Region2, MinSize2`。
10. **char_threshold** — 字符专用阈值 / 适合打印/喷码字符。
11. **check_difference** — 两图差异分割。
12. **regiongrowing** — 区域生长（固定灰度差） / 输入：`Image, Row, Column, Tolerance, MinSize → Regions`。
13. **regiongrowing_mean** — 区域生长（基于局部均值差） / 输入：`Image, Row, Column, Tolerance, MinSize → Regions`。
14. **regiongrowing_n** — 区域生长（基于最近 N 邻域均值）。
15. **watersheds** — 分水岭分割 / 输入：`Image, Basins, Watersheds`；像素级分水岭。
16. **watersheds_threshold** — 带高低阈值的分水岭。
17. **watersheds_marker** — 带强制标记的分水岭（去过分割）。
18. **segment_image_mser** — MSER 自然场景分割 / 输入：`Image, MSERRegions, Polarity, MinArea, MaxArea → Regions`。
19. **detect_edge_segments** — 基于边缘生长的线段检测。
20. **zero_crossing** — 过零点检测（拉普拉斯过零点）。
21. **zero_crossing_sub_pix** — 亚像素过零点。
22. **local_max** / **local_max_sub_pix** — 局部极大值（像素级 / 亚像素级）。
23. **local_min** / **local_min_sub_pix** — 局部极小值。
24. **plateaus** / **plateaus_center** — 平台区域 / 平台中心。
25. **lowlands** / **lowlands_center** — 低谷区域。
26. **critical_points_sub_pix** — 亚像素临界点。
27. **saddle_points_sub_pix** — 亚像素鞍点。
28. **topographic_sketch** — 完整地形草图（Max/Min/Saddle）。

---

## 5. HDevelop 示例代码

### 示例 1：PCB AOI 焊点缺陷分割（动态阈值 + 区域生长）

**场景**：PCB 焊点短路/缺锡检测。
**功能**：均值滤波生成参考图 → 动态阈值 → 形态学清理 → 缺陷分类。
**预期输出**：缺陷类型分类显示。

```hdevelop
* 示例 1：PCB AOI 焊点缺陷分割
* 场景：SMT 焊点检测

dev_update_window ('off')
dev_update_pc ('off')
dev_update_var ('off')

* 1. 读取 PCB 图
read_image (PCBImage, 'pcb/pcb_solder_01')
read_image (PCBRef, 'pcb/pcb_solder_ref')
get_image_size (PCBImage, PWidth, PHeight)

* 2. 灰度化
rgb1_to_gray (PCBImage, GrayPCB)

* 3. 动态阈值（处理光照不均）
dyn_threshold (GrayPCB, PCBRef, DiffRegion, 15, 'dark')

* 4. 形态学清理
opening_circle (DiffRegion, CleanedDiff, 1.5)
closing_circle (CleanedDiff, ClosedDiff, 1.5)

* 5. 填充孔洞
fill_up (ClosedDiff, FilledDiff)

* 6. 连通域
connection (FilledDiff, ConnectedDefects)
select_shape (ConnectedDefects, ValidDefects, 'area', 'and', 30, 99999)

* 7. 缺陷分类（按面积）
select_shape (ValidDefects, MinorDefects, 'area', 'and', 30, 100)
select_shape (ValidDefects, MajorDefects, 'area', 'and', 100, 500)
select_shape (ValidDefects, CriticalDefects, 'area', 'and', 500, 99999)

* 8. 区域生长（寻找扩展缺陷）
regiongrowing_mean (GrayPCB, RowSeed, ColSeed, 3.0, 100, GrownRegions)

* 9. 显示
dev_open_window (0, 0, PWidth, PHeight, 'black', SolderWindow)
dev_display (PCBImage)

* 10. 分类显示
count_obj (MinorDefects, MinorCount)
count_obj (MajorDefects, MajorCount)
count_obj (CriticalDefects, CriticalCount)

dev_set_draw ('margin')
dev_set_line_width (2)
dev_set_color ('yellow')
dev_display (MinorDefects)
dev_set_color ('orange')
dev_display (MajorDefects)
dev_set_color ('red')
dev_display (CriticalDefects)

* 11. 输出统计
TotalCount := MinorCount + MajorCount + CriticalCount
dev_disp_text ('Defects: ' + TotalCount$'.0' + ' (Minor=' + MinorCount$'.0' + ', Major=' + MajorCount$'.0' + ', Crit=' + CriticalCount$'.0' + ')', 'window', 12, 12, 'yellow', 'box', 'true')

dev_update_pc ('on')
dev_update_var ('on')
dev_update_window ('on')
```

### 示例 2：医学细胞分离（分水岭算法）

**场景**：血细胞粘连团分离。
**功能**：阈值 → 分水岭标记 → 强制标记分水岭 → 独立细胞统计。
**预期输出**：独立细胞 Region + 数量。

```hdevelop
* 示例 2：血细胞分离计数
* 场景：医学影像

dev_update_window ('off')
dev_update_pc ('off')
dev_update_var ('off')

* 1. 读取细胞图像
read_image (CellImage, 'cell/cell_cluster_01')
get_image_size (CellImage, CWidth, CHeight)
rgb1_to_gray (CellImage, GrayCell)

* 2. 高斯平滑
gauss_filter (GrayCell, SmoothCell, 3, 1.0)

* 3. 阈值分割细胞团
threshold (SmoothCell, CellRegion, 50, 200)

* 4. 连通域 → 找到每个细胞团
connection (CellRegion, ConnectedClusters)

* 5. 对每个细胞团做腐蚀得到中心标记
erosion_circle (CellRegion, ErodedSeeds, 3)

* 6. 分水岭（带强制标记）
watersheds_marker (SmoothCell, ErodedSeeds, Watersheds, RegionWatersheds)

* 7. 取分水岭脊线作为分割边界
* 但这里我们直接用分水岭结果作为分割 Region
dev_open_window (0, 0, CWidth, CHeight, 'black', CellWindow)
dev_display (CellImage)
dev_disp_text ('Cell Image', 'window', 12, 12, 'yellow', 'box', 'true')

* 8. 用 regiongrowing_mean 替代（更稳定）
regiongrowing_mean (SmoothCell, CWidth / 2, CHeight / 2, 5.0, 50, InitialRegions)
connection (InitialRegions, ConnectedCells)

* 9. 按面积过滤（去掉过大团块和过小碎片）
select_shape (ConnectedCells, ValidCells, 'area', 'and', 200, 2000)

* 10. 圆度过滤（细胞大致圆形）
select_shape (ValidCells, RoundCells, 'circularity', 'and', 0.6, 1.0)

* 11. 计数
count_obj (RoundCells, CellCount)

* 12. 计算每个细胞的特征
area_center (RoundCells, CellArea, CellRow, CellCol)

* 13. 显示
dev_set_color ('green')
dev_set_draw ('margin')
dev_set_line_width (2)
dev_display (RoundCells)

* 14. 标注每个细胞
for i := 0 to min([CellCount - 1, 50]) by 1
    disp_cross (CellWindow, CellRow[i], CellCol[i], 8, 0)
endfor

* 15. 输出
dev_disp_text ('Cell count: ' + CellCount$'.0', 'window', 30, 12, 'green', 'box', 'true')

dev_update_pc ('on')
dev_update_var ('on')
dev_update_window ('on')
```

### 示例 3：金属磨痕提取（局部阈值 + 拓扑特征）

**场景**：金属表面磨痕（细长暗线）提取。
**功能**：局部阈值 → 形态学细化 → 拓扑特征过滤 → 磨痕标注。
**预期输出**：磨痕 XLD 与特征统计。

```hdevelop
* 示例 3：金属磨痕提取
* 场景：金属表面缺陷检测

dev_update_window ('off')
dev_update_pc ('off')
dev_update_var ('off')

* 1. 读取金属表面图
read_image (MetalImage, 'metal/metal_scratch_01')
get_image_size (MetalImage, MWidth, MHeight)
rgb1_to_gray (MetalImage, GrayMetal)

* 2. 局部自适应阈值（处理光照不均）
* 注：local_threshold 在某些版本中 MaskSize 可设为奇数
local_threshold (GrayMetal, ScratchesRegion, 'adapted_std_deviation', 'dark', [], [])

* 3. 连通域
connection (ScratchesRegion, ConnectedScratches)

* 4. 按面积过滤
select_shape (ConnectedScratches, ValidScratches, 'area', 'and', 50, 99999)

* 5. 形状过滤（磨痕：长宽比大、紧凑度低）
select_shape (ValidScratches, ValidScratches, 'anisometry', 'and', 2.0, 10.0)
select_shape (ValidScratches, ValidScratches, 'compactness', 'and', 0.1, 0.7)

* 6. 计算拓扑特征（找最长轴）
orientation_region (ValidScratches, ScratchOrientation)
area_center (ValidScratches, ScratchArea, ScratchRow, ScratchCol)

* 7. 转 XLD 亚像素轮廓
gen_contour_region_xld (ValidScratches, ScratchContours, 'border')

* 8. 计算每个磨痕的长度
length_xld (ScratchContours, ScratchLength)

* 9. 计数
count_obj (ValidScratches, ScratchCount)

* 10. 显示
dev_open_window (0, 0, MWidth, MHeight, 'black', MetalWindow)
dev_display (MetalImage)

* 11. 标注磨痕
dev_set_color ('red')
dev_set_draw ('margin')
dev_set_line_width (2)
dev_display (ValidScratches)
dev_display (ScratchContours)

* 12. 标注中心
dev_set_color ('yellow')
dev_set_draw ('fill')
for i := 0 to ScratchCount - 1 by 1
    disp_cross (MetalWindow, ScratchRow[i], ScratchCol[i], 12, ScratchOrientation[i])
endfor

* 13. 输出
TotalLength := sum(ScratchLength)
MaxLength := max(ScratchLength)
dev_disp_text ('Scratches: ' + ScratchCount$'.0' + ', Total length: ' + TotalLength$'.1f' + ' px', 'window', 12, 12, 'red', 'box', 'true')
dev_disp_text ('Max length: ' + MaxLength$'.1f' + ' px', 'window', 30, 12, 'red', 'box', 'true')

dev_update_pc ('on')
dev_update_var ('on')
dev_update_window ('on')
```

---

## 6. 典型工业流水线

### 流水线 1：光照不均场景分割链

```
原图 → mean_image / gauss_filter 生成参考图 → dyn_threshold (Offset=15) → opening_circle → closing_circle → fill_up → connection + select_shape
```

### 流水线 2：多目标粘连分离链

```
原图
   ↓
gauss_filter 平滑
   ↓
distance_transform / 距离变换（隐含在 watersheds_marker 内部）
   ↓
erosion_circle 生成内部标记
   ↓
watersheds_marker 强制标记分水岭
   ↓
分水岭脊线作为分割边界
```

### 流水线 3：自然场景文字检测链

```
彩色原图
   ↓
rgb1_to_gray
   ↓
segment_image_mser MSER 检测
   ↓
select_shape 按面积/长宽比过滤
   ↓
union_collinear_contours_xld
   ↓
[下游 OCR / Deep OCR]
```

---

## 7. 常见陷阱与最佳实践

1. **陷阱：`watersheds` 严重过分割**——必须用 `watersheds_marker` 强制标记（前面 `connection` 的 blob 作为种子）。
2. **陷阱：`local_threshold` 的窗口大小**——窗口太小易噪，太大则不能适应局部。经验值：图像尺寸的 1/20 到 1/10。
3. **陷阱：`hysteresis_threshold` 低/高阈值比例**——典型 1:3（Canny 通用建议）；如 20/60 或 30/90。
4. **陷阱：`dyn_threshold` 需要参考图**——若是单图场景，需先 `mean_image` 或 `gauss_filter` 自生成参考图。
5. **陷阱：`regiongrowing_mean` 的种子点**——必须指定至少一个种子点 `(Row, Column)`；多目标场景手动指定麻烦。
6. **陷阱：`segment_image_mser` 参数**——`MinArea`/`MaxArea` 决定文字大小；`Polarity` 决定亮/暗。
7. **最佳实践：所有阈值化前先可视化直方图**——`gray_histo` + `histo_to_thresh` 自动给出建议阈值。
8. **最佳实践：`watersheds_marker` 必须先做距离变换**——HALCON 内部自动，但形态学腐蚀能增强稳定性。

---

## 8. 参数调优指南

| 算子 | 关键参数 | 推荐值 | 调整策略 |
|------|---------|--------|----------|
| `dyn_threshold` | `Offset, LightDark` | 5-30 | Offset 大→严格 |
| `local_threshold` | `Method, MaskSize` | 'adapted_std_deviation', 25 | MaskSize 必为奇数 |
| `var_threshold` | `MaskSize, StdDevScale, AbsThreshold` | 15, 0.2, 5 | 处理纹理 |
| `hysteresis_threshold` | `Low, High, MaxLength` | 20, 60, 10 | Low:High ≈ 1:3 |
| `regiongrowing_mean` | `Tolerance, MinSize` | 3-10, 50 | Tolerance 大→合并多 |
| `watersheds_marker` | （内部自动） | - | 必须有种子 |
| `segment_image_mser` | `Polarity, MinArea, MaxArea, Delta` | 'light', 50, 5000, 5 | Delta 大→稳定但粗 |
| `auto_threshold` | `Sigma` | 1-3 | Sigma 大→合并 |
| `binary_threshold` | `Method` | 'max_separability' | 'smooth_histo' 对噪声图 |
| `local_max` | `MaskShape, MaskSize` | 'octagon', 5 | 'octagon' 各向同性 |

---

## 9. 相关分类

- **Image**：分割算法的输入。
- **Filters**：分割前的预处理（去噪、增强）。
- **Regions**：分割后的形态学清理、特征统计。
- **Morphology**：分水岭算法本质是形态学的扩展应用。
- **XLD**：亚像素边缘（`zero_crossing_sub_pix`）→ XLD。
- **Matching**：模板匹配的预处理（`regiongrowing_mean` 准备 mask）。
- **Deep Learning**：复杂场景的分割逐渐被 DL 替代（语义分割）。

---

## 10. 学习小结

1. **`dyn_threshold` 是处理光照不均的瑞士军刀**：配 `mean_image` / `gauss_filter` 生成参考图，能解决 80% 不均匀光照场景。
2. **`watersheds_marker` 是粘连分离神器**：医学细胞、堆叠颗粒的分离首选；关键是提供合适的"种子"标记。
3. **`regiongrowing_mean` 是大目标均匀分割利器**：木材、木纹、布匹等大区域分割效果优于固定阈值。
4. **`segment_image_mser` 是自然场景文字/Logo 检测的最佳算法**：复杂背景下找稳定极值区域。
5. **`local_threshold` + `hysteresis_threshold` 是边缘检测替代**：不依赖 Canny，对纹理场景更稳健。