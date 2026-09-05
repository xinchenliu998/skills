# HALCON 算子分类详解：3D Object Model（3D 对象模型）

> **HALCON 版本**：26.05.0.0 Progress
> **分类代码**：3D Object Model（三维对象模型 / 点云与网格处理）
> **算子规模**：约 80 个
> **一级分类入口**：`C:\Program Files\MVTec\HALCON-26.05-Progress\doc\html\reference\operators\toc_3dobjectmodel.html`
> **学习层级**：L2–L3（进阶到高级）
> **典型应用**：点云生成 / ICP 配准 / 三角网格操作 / 3D 测量 / 可视化

---

## 1. 概述

3D Object Model 是 HALCON 中**所有三维数据**的统一抽象。从 RGB-D 相机、激光扫描仪、双目视觉、结构光扫描得到的点云 / 网格；从 CAD 文件（STL、PLY、OM3D）读入的三角网格；甚至 `gen_box_object_model_3d` 这种基本几何体，都用同一个 `ObjectModel3D` 句柄表示。

HALCON 26.05 的 3D Object Model 分为 **5 个子分类**：

| 子分类 | 主要功能 | 典型算子数 |
|--------|---------|-----------|
| Creation | 生成 / 读取 / 转换对象模型 | ~20 |
| Features | 计算面积/体积/包围盒/矩等特征 | ~12 |
| Segmentation | 分割、聚类、拟合基元 | ~12 |
| Transformations | 几何变换、可视化、投影 | ~15 |
| Misc（属性/查询/操作） | 法向量、简化、平滑、属性管理 | ~15 |

核心数据形式：
- **点云** (`xyz_to_object_model_3d`)：仅顶点 + 法向（可选）。
- **三角网格** (`triangulate_object_model_3d`)：顶点 + 三角面片。
- **线集** (`gen_object_model_3d_from_points`)：仅顶点。
- **带属性的多边形** (`set_object_model_3d_attrib`)：含 RGB、法向、自定义属性。

---

## 2. 应用场景

### 场景 1：逆向工程
- 用手持激光扫描仪扫描实物（零件、雕塑、文物）。
- 多帧点云拼接（ICP 配准）→ 三角网格化 → CAD 软件修复。
- 核心算子：`read_object_model_3d` + `register_object_model_3d_global` + `triangulate_object_model_3d` + `write_object_model_3d`。

### 场景 2：3D 打印质量检测
- 用工业 CT / 结构光扫描打印件。
- 与原始 STL 模型对比，计算几何偏差。
- 核心算子：`distance_object_model_3d` + `create_distance_transform`（可视化偏差）。

### 场景 3：工业 3D 测量
- 在工装台上扫描工件，提取关键尺寸（孔径、平面度、位置度）。
- 核心算子：`fit_primitives_object_model_3d`（拟合平面/球/圆柱）+ `distance_object_model_3d` + `volume_object_model_3d_relative_to_plane`。

### 场景 4：仓储物流尺寸量测
- 用 ToF 相机或双目相机测量包裹体积。
- 核心算子：`xyz_to_object_model_3d` + `convex_hull_object_model_3d` + `volume_object_model_3d_relative_to_plane`。

### 场景 5：自动驾驶 / AGV 环境感知
- LiDAR 点云分割、地面检测、障碍物提取。
- 核心算子：`segment_object_model_3d` + `select_object_model_3d` + `fit_primitives_object_model_3d`（拟合地面平面）+ `sample_object_model_3d`。

---

## 3. 子分类详解

### 3.1 Creation（创建与读取）

- **基本几何**：`gen_box_object_model_3d` / `gen_cylinder_object_model_3d` / `gen_sphere_object_model_3d` / `gen_plane_object_model_3d`。
- **从图像生成**：`xyz_to_object_model_3d(X, Y, Z, ObjectModel3D)`（深度图转点云，最常用）。
- **从文件读取**：`read_object_model_3d(FileName, Scale, ..., ObjectModel3D, Status)`（支持 STL、PLY、OBJ、OM3D、XYZ、DXF）。
- **从点集生成**：`gen_object_model_3d_from_points` / `gen_object_model_3d_from_points_rgb`（带颜色）。

### 3.2 Features（特征计算）

- `area_object_model_3d`（表面积）/ `volume_object_model_3d_relative_to_plane`（体积）
- `max_diameter_object_model_3d` / `smallest_bounding_box_object_model_3d` / `smallest_sphere_object_model_3d`
- `moments_object_model_3d`（3D 矩）/ `distance_object_model_3d`（两模型间最近距离）

### 3.3 Segmentation（分割与拟合）

- `convex_hull_object_model_3d`（凸包）/ `segment_object_model_3d`（属性分割）
- `connection_object_model_3d`（距离聚类）/ `fit_primitives_object_model_3d`（拟合平面/球/圆柱/直线）
- `sample_object_model_3d`（采样）/ `select_object_model_3d`（按属性筛选）/ `union_object_model_3d`（合并）

### 3.4 Transformations（变换与可视化）

- **几何变换**：`rigid_trans_object_model_3d`（刚体，最常用）/ `affine_trans_object_model_3d`（12 自由度）/ `projective_trans_object_model_3d`（15 自由度）。
- **投影与渲染**：`project_object_model_3d`（3D → 2D 像素）/ `render_object_model_3d`（带遮挡剔除渲染为图像）。
- **混合**：`fuse_object_model_3d`（多模型融合）。

### 3.5 Misc（属性 / 简化 / 法向）

- **属性管理**：`get/set/remove_object_model_3d_attrib` / `get_object_model_3d_params` / `copy_object_model_3d`。
- **预处理**：`prepare_object_model_3d`（为某用途准备，如 Kd-tree）。
- **算法**：`simplify_object_model_3d`（下采样）/ `triangulate_object_model_3d`（点云→网格）/ `smooth_object_model_3d`（平滑）/ `edges_object_model_3d`（边缘）/ `surface_normals_object_model_3d`（法向量）。

---

## 4. 核心算子详解

### 4.1 `xyz_to_object_model_3d` — 深度图转点云

```
xyz_to_object_model_3d(X : Y : Z : ObjectModel3D)
```

**功能**：从三个图像（X 坐标、Y 坐标、Z 深度）生成点云。**深度图处理最核心算子**。

**典型用法**：
```hdevelop
* ToF 相机 → 距离图 + X/Y 像素坐标
xyz_to_object_model_3d(ImageX, ImageY, ImageDistance, SceneModel)
```

### 4.2 `read_object_model_3d` — 读取 CAD / 扫描文件

```
read_object_model_3d(FileName, Scale, GenParamName, GenParamValue, ObjectModel3D, Status)
```

**功能**：读取 STL / PLY / OBJ / OM3D 文件。`Scale = 'mm'` / `'m'` 控制单位。

**关键参数**：
- `'xyz_unit'`：输入文件的单位（默认 'm'，STL 常为 'mm'）。
- `'convert_to_triangles'`：自动转为三角网格。

### 4.3 `register_object_model_3d_global` — 全局 ICP 配准

```
register_object_model_3d_global(ObjectModels, GenParamName, GenParamValue, TransformedModels, Score)
```

**功能**：把多帧点云统一到同一坐标系，**多视角扫描必备**。HALCON 自动做粗匹配 + 精炼 ICP。

**关键参数**：
- `'num_levels'`：金字塔层数（默认 4）。
- `'max_overlap_dist'`：最大重叠距离。
- `'inlier_threshold'`：内点距离阈值。

### 4.4 `register_object_model_3d_pair` — 两点云 ICP

```
register_object_model_3d_pair(ObjectModel3DFrom, ObjectModel3DTo, PoseIn, Mode, GenParamName, GenParamValue, PoseOut, Score)
```

**功能**：两个点云配准，需要初值 PoseIn（粗对齐）。

### 4.5 `triangulate_object_model_3d` — 点云三角化

```
triangulate_object_model_3d(ObjectModel3D, GenParamName, GenParamValue, TriangulatedModel)
```

**功能**：把点云转为三角网格（必须先有法向量）。常用 `'greedy'` 或 `'gripping'` 算法。

### 4.6 `convex_hull_object_model_3d` — 凸包

```
convex_hull_object_model_3d(ObjectModel3D, ConvexHullModel)
```

**功能**：计算 3D 凸包，用于包裹体积测量、碰撞检测、简化模型。

### 4.7 `fit_primitives_object_model_3d` — 基元拟合

```
fit_primitives_object_model_3d(ObjectModel3D, ParamName, ParamValue, Primitives, Errors)
```

**功能**：从点云中自动检测平面、球、圆柱、圆锥（用于工装测量：地面平面、管道圆柱、平面度）。

### 4.8 `simplify_object_model_3d` — 简化

```
simplify_object_model_3d(ObjectModel3D, Method, Amount, GenParamName, GenParamValue, SimplifiedModel)
```

**方法**：
- `'preserve_normal'`：保留法向量特征（细节保留）。
- `'preserve_general'`：通用采样（最常用）。
- `'preserve_points_borders'`：保留边界点（适合轮廓测量）。
- `'preserve_topology'`：保留拓扑（适合曲面）。

### 4.9 `render_object_model_3d` — 渲染

```
render_object_model_3d(ObjectModel3D, CamParam, Pose, GenParamName, GenParamValue, Image)
```

**功能**：把 3D 模型渲染为图像（带光照、遮挡剔除）。用于可视化、调试、生成训练数据。

### 4.10 `project_object_model_3d` — 投影到图像

```
project_object_model_3d(ObjectModel3D, CamParam, Pose, Width, Height, ProjectionMode, _, _, _, _, _, _, _)
```

**功能**：把 3D 模型按相机投影到 2D 像素坐标（带深度信息）。

---

## 5. HDevelop 示例代码

### 示例 1：从 ToF 相机深度图生成点云 + 测量

```hdevelop
* 3D Object Model - ToF Camera Pipeline
* 适用：物流体积测量 / 视觉检测

* === 1. 加载相机参数（已标定）===
read_cam_par('tof_camera_parameters.dat', CameraParam)

* === 2. 读 X/Y/Z 三元图 ===
read_image(ImageX, 'X.map')   * X 坐标 (单位 mm)
read_image(ImageY, 'Y.map')   * Y 坐标 (单位 mm)
read_image(ImageZ, 'Z.map')   * 深度图 (单位 mm)

* === 3. 转点云 ===
xyz_to_object_model_3d(ImageX, ImageY, ImageZ, SceneModel)

* === 4. 下采样（场景百万点 → 万级）===
simplify_object_model_3d(SceneModel, 'preserve_general', 5.0, [], [], SceneSimplified)

* === 5. 滤波：剔除离群点（统计离群） ===
remove_noise_object_model_3d(SceneSimplified, 'neighbor', 'num_neighbors', 20, CleanedModel)

* === 6. 计算凸包 + 体积 ===
convex_hull_object_model_3d(CleanedModel, HullModel)
* 在底部自动找最小平面 → 计算体积
get_object_model_3d_params(HullModel, 'center', Center)
volume_object_model_3d_relative_to_plane(CleanedModel, [Center[0], Center[1], Center[2]-1000, 0, 0, 0, 0], 'signed', VolumeMM3)

* === 7. 显示 ===
dev_open_window(0, 0, 640, 480, 'black', WindowHandle)
Pose := [0, 0, 800, 90, 0, 0, 0]
disp_object_model_3d(WindowHandle, [CleanedModel, HullModel], [], Pose, ['color_0', 'color_1', 'alpha_1'], ['gray', 'green', 0.5], [], [], [], PoseOut)

* === 8. 清理 ===
clear_object_model_3d(SceneModel)
clear_object_model_3d(CleanedModel)
clear_object_model_3d(HullModel)
```

### 示例 2：多帧扫描 ICP 配准（逆向工程）

```hdevelop
* 3D Object Model - Multi-View Registration
* 适用：手持激光扫描

* === 1. 读多帧点云 ===
list_files('scans', 'files', FileNames)
Models := []
for i := 0 to |FileNames|-1 by 1
    read_object_model_3d(FileNames[i], 'mm', [], [], Model, Status)
    Models[i] := Model
endfor

* === 2. 全局配准（自动）===
register_object_model_3d_global(Models, ['num_levels', 'max_overlap_dist', 'inlier_threshold'],
                                 [3, 5.0, 2.0],
                                 AlignedModels, Scores)

* === 3. 合并所有帧 ===
union_object_model_3d(AlignedModels, MergedModel)

* === 4. 三角网格化（生成 STL）===
surface_normals_object_model_3d(MergedModel, 'mls', 'mls_force_outward', 'mls_kNN', 30, NormalModel)
triangulate_object_model_3d(NormalModel, 'greedy', [], TriMesh)

* === 5. 平滑 + 简化 ===
smooth_object_model_3d(TriMesh, 'low', 1.0, [], [], SmoothedMesh)
simplify_object_model_3d(SmoothedMesh, 'preserve_normal', 0.5, [], [], FinalMesh)

* === 6. 导出 STL ===
write_object_model_3d(FinalMesh, 'reconstructed.stl', 'mm', [], [])
disp_message(WindowHandle, 'Reconstruction Complete', 'window', 12, 12, 'green', 'false')
```

### 示例 3：平面/圆柱拟合（工装测量）

```hdevelop
* 3D Object Model - Primitive Fitting
* 适用：工件平面度/圆度检测

* === 1. 加载扫描点云 + 拟合基元 ===
read_object_model_3d('bracket.om3', 'mm', [], [], BracketModel)
fit_primitives_object_model_3d(BracketModel, ['primitive_type', 'fitting_algorithm'],
                                ['all', 'least_squares_tukey'], Primitives, FitErrors)

* === 2. 平面度测量（Primitives[0] 是顶面）===
get_object_model_3d_params(Primitives[0], 'primitive_parameter', Params)
distance_object_model_3d(BracketModel, Primitives[0], [0,0,0,0,0,0,0], 50.0, DistanceHandle, ['max_distance'], [50.0])
get_distance_object_model_3d_result(DistanceHandle, 'max', MaxDist)

* 显示结果
disp_message(WindowHandle, 'Plane Flatness: ' + MaxDist$'.3f' + ' mm', 'window', 12, 12, 'green', 'false')
```

---

## 6. 典型工业流水线

### 流水线 A：物流体积测量

```
ToF 相机（X, Y, Z 三图）→ xyz_to_object_model_3d → simplify + remove_noise
→ convex_hull_object_model_3d → volume_object_model_3d_relative_to_plane → 输出 (mm³)
```

### 流水线 B：逆向建模

```
多帧扫描 → register_object_model_3d_global（自动对齐）→ union → surface_normals
→ triangulate → smooth + simplify → write_object_model_3d（STL）
```

### 流水线 C：3D 质量检测

```
参考 STL + 实测点云 → register_pair（ICP 对齐）→ distance_object_model_3d
→ 可视化 → 判定 PASS / FAIL
```

### 流水线 D：自动导航 / AGV

```
LiDAR → segment + fit_primitives（地面）→ 减地面 → connection（聚类障碍）→ select_object_model_3d（按尺寸）→ bounding_box
```

---

## 7. 常见陷阱与最佳实践

### 陷阱 1：单位不一致
CAD 是 mm、ToF 相机输出是 m、ICP 计算单位混乱 → 配准失败。
- **最佳实践**：**统一用 mm** 或 m，但内部所有数据保持一致。`read_object_model_3d` 必须指定 `'mm'` / `'m'`。

### 陷阱 2：点云没有法向量导致三角化失败
直接 `triangulate_object_model_3d` 不带法向量 → 错误。
- **最佳实践**：先 `surface_normals_object_model_3d(Model, 'mls', 'mls_force_outward', 'mls_kNN', 30, ...)`。

### 陷阱 3：百万级点云全量 ICP 导致 OOM
`register_object_model_3d_pair` 处理 10M 点 → 内存爆炸。
- **最佳实践**：`simplify_object_model_3d` 下采样到 5–10 万点；用 `'num_levels'` 金字塔分层。

### 陷阱 4：初值不准导致 ICP 收敛到局部最优
两个点云初始偏离 > 30° → ICP refine 失败。
- **最佳实践**：先用全局配准（`register_object_model_3d_global` 自动粗对齐）+ 手动关键点。

### 陷阱 5：`triangulate_object_model_3d` 用法不当
对噪声点云用 `'gripping'` → 出现飞点三角片。
- **最佳实践**：先 `smooth_object_model_3d`，再用 `'greedy'` + `'num_samples_per_node' = 10`。

### 陷阱 6：`distance_object_model_3d` 在密集点云上慢
百万点 × 百万点距离 → 数十分钟。
- **最佳实践**：先 `sample_object_model_3d` 抽稀（10 万点以内）；用 `'max_distance'` 限制搜索范围。

### 陷阱 7：`render_object_model_3d` 内存不足
渲染大模型到 4K 图像 → OOM。
- **最佳实践**：
  - `simplify_object_model_3d` 先简化（< 10 万面）。
  - `'quality'` 参数调低（如 `'low'`）。

### 陷阱 8：忘记清理对象模型
`ObjectModel3D` 是 GPU/CPU 资源，不清理 → 内存泄漏。
- **最佳实践**：每个模型用完 `clear_object_model_3d`；HDevelop 用 try/catch/finally 保证清理。

---

## 8. 参数调优指南

### 采样 / ICP 配准

| 参数 | 含义 | 典型值 |
|------|------|--------|
| `'amount'`（simplify） | 简化比例 | 0.3–0.5 |
| `'method'`（simplify） | 简化策略 | `'preserve_general'` / `'preserve_normal'` / `'preserve_topology'` |
| `'num_levels'`（ICP） | 金字塔层数 | 3–5 |
| `'max_overlap_dist'`（ICP） | 最大重叠距离 | 5–20 mm |
| `'inlier_threshold'`（ICP） | 内点距离 | 1–3 mm |

### 三角化 / 法向量

| 参数 | 调优 |
|------|------|
| `'num_samples_per_node'` | 5–20 |
| `'max_gap'` | 单位 mm，建议点云平均间距 5–10 倍 |
| `'greedy_method'` | `'greedy'` / `'gripping'` / `'poisson'` |
| `'mls_kNN'` | 10–50（密集点云大值） |

### 拟合 / 渲染

| 算子 | 关键参数 | 调优 |
|------|---------|------|
| `fit_primitives` | `'primitive_type'` | `'plane'` / `'cylinder'` / `'sphere'` / `'all'` |
| `fit_primitives` | `'fitting_algorithm'` | `'least_squares'` / `'huber'` / `'tukey'`（抗噪声后两者） |
| `render_*` | `'quality'` | `'low'`（快）/ `'high'`（高质量） |
| `render_*` | `'hidden_surface_removal'` | `'true'`（默认必备） |

---

## 9. 相关分类

| 关联分类 | 协作方式 |
|----------|----------|
| **3D Matching** | 3D Matching 的输入（场景点云）必来自 3D Object Model（`xyz_to_object_model_3d`） |
| **3D Reconstruction** | 双目/光片/结构光重建后输出点云 / 网格 → 用 3D Object Model 处理 |
| **Calibration** | `project_object_model_3d` / `render_object_model_3d` 必须有 `CameraParam` |
| **Transformations** | `rigid_trans_object_model_3d` / `affine_trans_object_model_3d` 与 `hom_mat3d_*` / Pose 转换互为桥梁 |
| **Graphics → 3D Scene** | `add_scene_3d_instance` / `render_scene_3d` 是 3D Object Model 可视化的现代方案 |
| **File → 3D** | `write_object_model_3d` / `read_object_model_3d` 持久化 |
| **Tuple / Matrix** | ICP 算法内部大量矩阵运算，特征数据可导出为矩阵 |

---

## 10. 学习小结

3D Object Model 是 HALCON 中所有"三维几何数据"的核心数据结构——它把点云、网格、几何体统一在一个句柄下，并通过 ~80 个算子提供完整的生成、处理、可视化能力。

### 学习路线建议

1. **第 1 周**：理解 ObjectModel3D 句柄；用 `gen_box_object_model_3d` / `gen_sphere_object_model_3d` 生成基础几何；用 `read_object_model_3d` 读 STL 文件；用 `disp_object_model_3d` 显示。
2. **第 2 周**：掌握 `xyz_to_object_model_3d` + `simplify` + `surface_normals` + `triangulate` 全流程；理解点云 → 网格的标准流程。
3. **第 3 周**：学 `register_object_model_3d_global` 做多视角配准；学 `distance_object_model_3d` 做偏差测量。
4. **第 4 周**：学 `fit_primitives_object_model_3d` + `segment_object_model_3d` 做工业测量。
5. **第 5 周**：学 `render_object_model_3d` / `project_object_model_3d` + 3D Scene 高级可视化。

### 核心要点回顾

1. **ObjectModel3D 是核心句柄**：所有 3D 视觉算法的输入输出都是它，理解其生命周期（创建 → 处理 → 显示 → 清理）是基础。

2. **单位 / 法向量 / 采样** 三大基础：① 单位 mm/m 必须全局统一；② 法向量必须计算（ICP、三角化、面积都依赖）；③ 采样密度决定性能与精度平衡。

3. **ICP 配准的两层结构**：粗配准（特征/手动）→ 精配准（ICP/HALCON）。`register_object_model_3d_global` 自动做粗+精。

4. **测量场景用 `fit_primitives`**：工业测量（平面度、圆度、孔径）的核心不是显示点云，而是把点云拟合为几何基元。

5. **可视化是调试眼睛**：`disp_object_model_3d` + 多色 + 多模型叠加是日常调试必备。

### 推荐示例程序

HALCON 自带 `%HALCONEXAMPLES%\hdevelop\3D-Object-Model\`（约 30+ 个 demo），必看：
- `xyz_to_object_model_3d_workflow.hdev`（深度图 → 点云 → 测量）
- `icp_registration_global.hdev` / `icp_registration_pair.hdev`（ICP）
- `triangulation_of_points.hdev` / `fit_primitives.hdev`
- `distance_object_model_3d.hdev`（3D 偏差测量）
- `volume_of_object_model_3d.hdev`（体积测量）

掌握 3D Object Model 是 3D Matching、3D Reconstruction 与 Calibration 三类算子的"载体基础"。三类合计约 240 算子，覆盖 90% 工业机器人视觉项目的数据流（采集 → 处理 → 匹配 → 决策）。