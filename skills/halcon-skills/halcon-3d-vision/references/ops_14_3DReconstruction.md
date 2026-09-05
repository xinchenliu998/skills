# HALCON 算子分类详解：3D Reconstruction（三维重建）

> **HALCON 版本**：26.05.0.0 Progress
> **分类代码**：3D Reconstruction（三维重建 / 从 2D 图像恢复 3D）
> **算子规模**：约 60 个
> **一级分类入口**：`C:\Program Files\MVTec\HALCON-26.05-Progress\doc\html\reference\operators\toc_3dreconstruction.html`
> **学习层级**：L2–L3（进阶到高级）
> **典型应用**：双目立体视觉 / 结构光扫描 / 光片法测量 / 摄影立体 / 逆向工程

---

## 1. 概述

3D Reconstruction 是 HALCON 中**从 2D 图像数据恢复 3D 几何形状**的算子族。与 3D Object Model（处理已有 3D 数据）不同，3D Reconstruction 的核心任务是"输入多张 2D 图像，输出 3D 几何（点云、网格、深度图）"。

HALCON 26.05 的 3D Reconstruction 分为 **7 个子分类**，每种方法对应不同的硬件原理：

| 子分类 | 物理原理 | 典型算子数 |
|--------|---------|-----------|
| Binocular Stereo | 双目立体视差（被动式） | ~15 |
| Depth from Focus | 离焦深度（单相机） | ~2 |
| Multi-view | 多视角立体（SfM/MVS） | ~5 |
| Photometric Stereo | 摄影立体（多光照） | ~8 |
| Sheet of Light | 光片法（激光线扫描） | ~15 |
| Structured Light | 结构光（投影图案） | ~8 |
| Misc（通用） | Stereo Model / Fundamental Matrix | ~5 |

**方法选择 = 硬件 × 精度 × 速度 × 物体特性**：
- 物体小、精度高、运动 → 结构光。
- 大场景、远距离 → 双目。
- 表面细节、显微 → 摄影立体。
- 连续激光线 → 光片法。
- 单图反推 → Shape from Shading。

---

## 2. 应用场景

### 场景 1：电子连接器针脚检测
- 1 mm 间距金属针脚，检测共面度、歪斜、缺针。
- 用双目相机拍 2 张图 → 视差 → 深度 → 3D 坐标。
- 核心：`binocular_calibration` + `binocular_disparity_mg` + `disparity_to_distance`。

### 场景 2：手机壳体表面缺陷检测
- 注塑件划伤、麻点、缩水痕；高精度结构光扫描 → 完整 3D 表面 → 找异常区域。
- 核心：`create_structured_light_model` + `decode_structured_light_pattern` + `reconstruct_surface_structured_light`。

### 场景 3：金属零件激光扫描
- 大尺寸工件（>500 mm）3D 形状；线激光 + 相机，运动机构带动。
- 核心：`create_sheet_of_light_model` + `measure_profile_sheet_of_light` + `apply_sheet_of_light_calibration`。

### 场景 4：硬币浮雕检测
- 浮雕高度 0.1–1 mm；4 方向 LED 光源 → 同一相机拍 4 张图 → 摄影立体反推法向。
- 核心：`photometric_stereo` + `radiometric_self_calibration`。

---

## 3. 子分类详解

### 3.1 Binocular Stereo（双目立体视觉）

**原理**：左右两相机同时拍同一物体 → 找同名点（匹配）→ 视差 → 三角测量得到深度。

**算子**：
- `binocular_calibration`：双目内外参标定
- `binocular_disparity_mg`：**多基线视差**（速度精度兼顾，最常用）
- `binocular_disparity` / `binocular_disparity_ms` / `binocular_distance`
- `disparity_to_distance` / `disparity_image_to_xyz` / `disparity_to_point_3d`
- `reconstruct_points_stereo` / `reconstruct_surface_stereo`（完整表面重建）

**Rectification**：`gen_binocular_rectification_map` / `gen_binocular_proj_rectification` / `map_image`。

### 3.2 Depth from Focus（离焦深度）

**原理**：不同焦距位置拍多张图 → 在每张图上找最锐利位置 → 深度。
- `depth_from_focus(ImageMultiFocus, Depth, Confidence, Filter, Selection)`。

### 3.3 Multi-view（多视角立体）

**原理**：一台相机在不同位置拍 N 张图 → 找特征点对应 → 三角测量 + 稠密匹配。
- `create_stereo_model` / `set/get_stereo_model_param` / `reconstruct_surface_stereo`（HALCON 26 引入）。

### 3.4 Photometric Stereo（摄影立体）

**原理**：相机不动，4+ 个方向光源依次点亮 → 同一物体亮度变化 → 表面法向 → 高度场。
- `photometric_stereo`（**核心**） / `uncalibrated_photometric_stereo`（无辐射标定）
- `radiometric_self_calibration`（处理高光） / `reconstruct_height_field_from_gradient`（梯度→高度）
- `sfs_lr` / `sfs_mod_lr` / `sfs_orig_lr` / `sfs_pentland`（Shape from Shading 单图反推）。

### 3.5 Sheet of Light（光片法）

**原理**：线激光打物体 → 相机斜拍得到每帧轮廓 → 多帧累积 → 完整 3D 轮廓。
- 标定：`create_sheet_of_light_calib_object` + `calibrate_sheet_of_light`
- 测量：`create_sheet_of_light_model` + `measure_profile_sheet_of_light` + `apply_sheet_of_light_calibration`
- 查询：`get_sheet_of_light_result_object_model_3d` / `set/get_sheet_of_light_param` / `estimate_sl_al_lr`。

### 3.6 Structured Light（结构光）

**原理**：投影仪投已知图案 → 相机拍变形图案 → 解码 → 每个像素对应唯一 3D 点。
- `create_structured_light_model` / `gen_structured_light_pattern` / `decode_structured_light_pattern` / `reconstruct_surface_structured_light`。
- 图案类型：`'simple_stripe'` / `'gray_code'` / `'phase_shift'` / `'multigrid'`。

### 3.7 Misc（通用/辅助）

- `find_caltab` / `caltab_points` / `reconst3d_from_fundamental_matrix`。

---

## 4. 核心算子详解

### 4.1 `binocular_calibration` — 双目标定

- `binocular_calibration(CamParamL, CamParamR, RelPose, CaltabFile, ..., CamParamLOut, CamParamROut, RelPoseOut, _, Error)`：通过拍摄多张标定板图像，同时优化左右相机内参、外参（基线 + 相对姿态）。
- **返回值**：`CamParamLOut` / `CamParamROut`（内参）+ `RelPoseOut`（基线+旋转）+ `Error`（平均投影误差 pixel，理想 < 0.1）。

### 4.2 `binocular_disparity_mg` — 多基线视差

- `binocular_disparity_mg(ImageL, ImageR, Disparity, Score, ..., Method, MinDisparity, MaxDisparity, NumLevels, ...)`：从双目图计算视差图。`mg` = Multi-Grid，速度快 5–10 倍。
- **关键参数**：`Method`（`'ncc'` / `'census'` / `'sad'` / `'sobel'`）、`MinDisparity` / `MaxDisparity`（视差范围）、`NumLevels`（金字塔层数，默认 5）。

### 4.3 `disparity_to_distance` — 视差转距离

- `disparity_to_distance(Disparity, Distance, CamParam)`：视差图 → 距离图（每个像素的真实 Z 距离）。

### 4.4 `create_structured_light_model` — 创建结构光模型

- `create_structured_light_model(SymbolType, PatternWidth, PatternHeight, ...)`：创建结构光模型（指定图案类型与分辨率）。
- `SymbolType`：`'gray_code'`（大范围） / `'phase_shift'`（高精度） / `'multigrid'`（平衡）。

### 4.5 `gen_structured_light_pattern` — 生成图案

- `gen_structured_light_pattern(StructuredLightModelID, _, PatternImage)`：生成投影图案图像（输出给 DLP/投影仪）。

### 4.6 `decode_structured_light_pattern` — 解码图案

```
decode_structured_light_pattern(CameraImages, _, StructuredLightModelID, _, DecodedImage, _)
```

**功能**：从相机拍到的变形图案解码出每个像素的编码值。

### 4.7 `reconstruct_surface_structured_light` — 重建 3D 表面

```
reconstruct_surface_structured_light(DecodedImage, _, StructuredLightModelID, _, ObjectModel3D)
```

**功能**：从解码后的图像 + 相机参数重建 3D 表面（输出 `ObjectModel3D`，可直接接 3D Object Model 类算子）。

### 4.8 `create_sheet_of_light_model` + `measure_profile_sheet_of_light` — 光片法核心

- `create_sheet_of_light_model(ProfileRegion, MinGray, MinStrokeWidth, ...)`：创建模型（指定激光线粗细、最小灰度）。
- `measure_profile_sheet_of_light(Image, SheetOfLightModelID, _, Profile)`：从单张图提取激光线轮廓。

### 4.9 `apply_sheet_of_light_calibration` — 应用光片法标定

- `apply_sheet_of_light_calibration(...)`：把多帧激光线轮廓转换为 3D 坐标 (X/Y/Z)。

### 4.10 `photometric_stereo` — 摄影立体

- `photometric_stereo(Images, HeightField, Gradient, Albedo, ...)`：从 4+ 张不同光照方向的图像反推表面法向和高度。
- 关键参数：`MinGradient`（最小梯度）/ `ReconstructionMethod`（`'poisson'` 高精度 / `'l2'` 快）/ `'num_lights'`（≥4）。

---

## 5. HDevelop 示例代码

### 示例 1：完整双目立体视觉流程

```hdevelop
* 3D Reconstruction - Binocular Stereo Vision
* 适用：电子连接器针脚高度检测

* === 1. 双目标定（一次性） ===
read_cam_par('camera_left.dat', CamParamL)
read_cam_par('camera_right.dat', CamParamR)
Baseline := 100.0
binocular_calibration(CamParamL, CamParamR, [0, Baseline, 0, 0, 0, 0, 0], 'caltab_30mm.descr',
                      [], [], CalibDataID, [], [], [], [], [], [],
                      CamParamLOut, CamParamROut, RelPoseOut, _, Error)
write_cam_par(CamParamLOut, 'camera_left_calib.dat')
write_pose(RelPoseOut, 'stereo_baseline.dat')

* === 2. 实时视差 + 表面重建 ===
grab_image_async(ImageL, AcqL, -1)
grab_image_async(ImageR, AcqR, -1)
create_stereo_model(2, 3, 4, StereoModelID)
set_stereo_model_param(StereoModelID, 'method', 'ncc')
set_stereo_model_param(StereoModelID, 'min_disparity', -30)
set_stereo_model_param(StereoModelID, 'max_disparity', 30)
set_stereo_model_param(StereoModelID, 'num_levels', 5)
reconstruct_surface_stereo(ImageL, ImageR, [], [], StereoModelID, ObjectModel3D, Score)

* === 3. 视差转距离 ===
binocular_disparity_mg(ImageL, ImageR, Disparity, Score, [], 'ncc', -30, 30, 5, 0.5, 'none', 'off')
disparity_to_distance(Disparity, Distance, CamParamLOut)

* === 4. 找针脚平面 + 显示 ===
fit_primitives_object_model_3d(ObjectModel3D, ['primitive_type', 'fitting_algorithm'],
                                ['plane', 'least_squares_tukey'], Plane, _)
dev_open_window(0, 0, 800, 400, 'black', WindowHandle)
dev_display(Disparity)
disp_message(WindowHandle, 'Disparity: ' + min([Disparity])$'.2f' + '~' + max([Disparity])$'.2f',
             'window', 12, 12, 'green', 'false')
clear_stereo_model(StereoModelID)
clear_object_model_3d(ObjectModel3D)
```

### 示例 2：结构光扫描完整流程

```hdevelop
* 3D Reconstruction - Structured Light Scanning
* 适用：手机壳体表面缺陷检测

* === 1. 创建结构光模型 ===
create_structured_light_model('phase_shift', 1920, 1080, SLModelID)
set_structured_light_model_param(SLModelID, 'camera_param', CamParam)
set_structured_light_model_param(SLModelID, 'min_pattern_amplitude', 10)

* === 2. 生成投影图案 ===
gen_structured_light_pattern(SLModelID, [], PatternImage)

* === 3. 相机采集多幅图案 ===
read_image(CamImage1, 'sl_pattern_1.tiff')
read_image(CamImage2, 'sl_pattern_2.tiff')
read_image(CamImage3, 'sl_pattern_3.tiff')
read_image(CamImage4, 'sl_pattern_4.tiff')

* === 4. 解码 + 重建 ===
decode_structured_light_pattern([CamImage1, CamImage2, CamImage3, CamImage4], [], SLModelID, [], DecodedImage, _)
reconstruct_surface_structured_light(DecodedImage, [], SLModelID, [], ObjectModel3D)

* === 5. 后处理 + 与 CAD 对比 ===
remove_noise_object_model_3d(ObjectModel3D, 'neighbor', 'num_neighbors', 20, CleanedModel)
surface_normals_object_model_3d(CleanedModel, 'mls', 'mls_force_outward', 'mls_kNN', 30, NormalModel)
triangulate_object_model_3d(NormalModel, 'greedy', [], TriMesh)

read_object_model_3d('reference.stl', 'mm', [], [], Reference)
register_object_model_3d_pair(CleanedModel, Reference, [0,0,0,0,0,0,0], 'global',
                              ['num_levels', 'inlier_threshold'], [3, 1.0], RefinedPose, Score)
rigid_trans_object_model_3d(CleanedModel, RefinedPose, AlignedModel)

* 计算偏差
distance_object_model_3d(AlignedModel, Reference, [0,0,0,0,0,0,0], 10.0, DistanceHandle, ['max_distance'], [10.0])
get_distance_object_model_3d_result(DistanceHandle, 'distances', Distances)
MeanDist := mean(Distances)
StdDist := deviation(Distances)
DefectMask := Distances > (MeanDist + 3*StdDist)

* === 6. 显示 + 清理 ===
dev_open_window(0, 0, 640, 480, 'black', WindowHandle)
disp_object_model_3d(WindowHandle, [AlignedModel, Reference], [], Pose,
                     ['color_0', 'color_1', 'alpha_1'], ['gray', 'red', 0.4], [], [], [], PoseOut)
clear_structured_light_model(SLModelID)
clear_object_model_3d(ObjectModel3D)
clear_object_model_3d(Reference)
```

### 示例 3：光片法（激光线扫描）

```hdevelop
* 3D Reconstruction - Sheet of Light (Laser Line Scanning)
* 适用：金属零件 3D 轮廓测量

* === 1. 标定（一次性） ===
create_sheet_of_light_calib_object(CamParam, 'caltab_sol.descr', CalibObjID)
grab_image(Image, AcqHandle)
find_caltab(Image, CaltabRegion, 'caltab_sol.descr', 3, 0, 5)
find_marks_and_pose(Image, CaltabRegion, 'caltab_sol.descr', CamParam, 128, 10, 20,
                     CalibCoord, RCoord, CCoord, Pose)
calibrate_sheet_of_light(Image, 'mm', CamParam, Pose, 'mm', CalibObjID,
                          [], 50, MovementPar, _, _, PoseLaserPlane, _, _)

* === 2. 创建测量模型 ===
create_sheet_of_light_model(ProfileRegion, 30, 5, SOLModelID)
set_sheet_of_light_param(SOLModelID, 'calibration_pose', PoseLaserPlane)

* === 3. 实时测量（运动机构带动物体） ===
Profiles := []
for i := 0 to 99 by 1
    grab_image(Image, AcqHandle)
    measure_profile_sheet_of_light(Image, SOLModelID, [], Profile)
    concat_obj(Profiles, Profile, NewProfiles)
    Profiles := NewProfiles
endfor

* === 4. 应用标定 → 3D 坐标 ===
apply_sheet_of_light_calibration(Profiles, [], [], 30, SOLModelID, [], Y, Z, _)

* === 5. 转 ObjectModel3D ===
xyz_to_object_model_3d(XGrid, Y, Z, ScannedModel)

* === 6. 三角化 + 平滑 ===
surface_normals_object_model_3d(ScannedModel, 'mls', 'mls_force_outward', 'mls_kNN', 20, NormalModel)
triangulate_object_model_3d(NormalModel, 'greedy', [], ScannedMesh)
smooth_object_model_3d(ScannedMesh, 'low', 1.0, [], [], SmoothedMesh)

* === 7. 几何尺寸测量（工件最大直径）===
fit_primitives_object_model_3d(ScannedMesh, ['primitive_type', 'fitting_algorithm'],
                                ['cylinder', 'least_squares_tukey'], Cylinder, Errors)
get_object_model_3d_params(Cylinder, 'primitive_parameter', CylParams)
Diameter := 2 * CylParams[6]

* === 8. 显示 + 清理 ===
dev_open_window(0, 0, 800, 600, 'black', WindowHandle)
disp_object_model_3d(WindowHandle, [ScannedMesh], [], Pose, ['color_0'], ['green'], [], [], [], PoseOut)
disp_message(WindowHandle, 'Diameter: ' + Diameter$'.3f' + ' mm', 'window', 12, 12, 'green', 'false')
clear_sheet_of_light_model(SOLModelID)
clear_object_model_3d(ScannedMesh)
```

---

> **提示**：HALCON 还提供 `photometric_stereo`（摄影立体）和 `depth_from_focus`（离焦深度）分别用于多光源反推表面法和单相机多焦距深度估计，更多示例见 `%HALCONEXAMPLES%\hdevelop\3D-Reconstruction\photometric_stereo.hdev`。

## 6. 典型工业流水线

### 流水线 A：电子连接器针脚检测（双目）

```
标定：双目拍 12+ 张 caltab → binocular_calibration → 存内参外参
实时：grab_image(L+R) → 校正 → binocular_disparity_mg → disparity_to_distance
→ depth image → 针脚 ROI → fit_plane → 共面度检测 → 判定 PASS/FAIL
```

### 流水线 B：手机壳体检测（结构光）

```
投影仪+相机固定架 → gen_structured_light_pattern → 投图案 + 相机同步拍图
→ decode → reconstruct_surface_structured_light → ObjectModel3D
→ 简化+平滑+对齐 → distance → 偏差图 → 缺陷判定
```
```

### 流水线 C：金属零件尺寸测量（光片法）

```
运动机构带动物件 → measure_profile_sheet_of_light（每帧）→ apply_sheet_of_light_calibration
→ xyz_to_object_model_3d → 三角化 → fit_primitives → 输出直径/长度/平面度
```

### 流水线 D：硬币浮雕（摄影立体）

```
4 LED 灯方向依次点亮 → 拍 4 张图 → photometric_stereo → 高度场 + 梯度图 → 测量浮雕深度
```

---

## 7. 常见陷阱与最佳实践

### 陷阱 1：双目标定图像不足 / 角度覆盖不全
只拍 5 张全正面图 → 标定误差 > 1 pixel → 测距误差 > 1 mm。
- **最佳实践**：≥ 12 张图，覆盖视野四角 + 不同深度。HALCON 26 推荐 15+ 张。

### 陷阱 2：视差范围设错
`MinDisparity = -10, MaxDisparity = 10` 但实际视差范围 ±50 → 远处物体测不到。
- **最佳实践**：先用全范围（-100, 100）跑一次看实际范围。

### 陷阱 3：低纹理场景匹配失败
白纸、抛光金属 → 找不到同名点 → 视差图全黑。
- **最佳实践**：双目加纹理投影（散斑激光）；结构光换相位偏移/散斑；光片法不受影响。

### 陷阱 4：光片法激光线没对准
激光线未打在标定块 → `calibrate_sheet_of_light` 失败。
- **最佳实践**：标定前用 `disp_cross` 验证激光线落在相机视野中央；工作距离与标定偏差 < 50 mm。

### 陷阱 5：结构光投影与相机未同步
投影图案移动但相机拍静止图 → 解码错乱。
- **最佳实践**：硬件触发同步；多次曝光叠加。

### 陷阱 6：摄影立体光源数量不足
只拍 3 张图 + 3 个光源 → 表面法向有歧义。
- **最佳实践**：至少 4 个光源（推荐 4–6），覆盖半球空间均匀分布。

### 陷阱 7：双目基线选择不当
基线太短（10 mm）→ 远距离精度差；太长（500 mm）→ 近距离盲区。
- **最佳实践**：基线 ≈ 物体距离的 1/3 到 1/2（典型 60–120 mm）。

### 陷阱 8：反射 / 镜面导致高光
高光区域 → 视差 / 高度无解（黑色洞）。
- **最佳实践**：加偏振片 + 同轴光；多曝光 HDR；用 `radiometric_self_calibration`。

---

## 8. 参数调优指南

### 双目视差参数

| 参数 | 调优 |
|------|------|
| `Method` | `'ncc'` 通用；`'census'` 低纹理；`'sad'` 快；`'sobel'` 精度高 |
| `MinDisparity` / `MaxDisparity` | 实测值 ± 20 |
| `NumLevels` | 5（默认）–7（高精度） |
| `ScoreThreshold` / `Filter` | 0.3–0.7；`'none'` / `'weak'` / `'strong'` |

### 结构光 / 光片法 / 摄影立体参数

| 方法 | 关键参数 | 调优 |
|------|---------|------|
| 结构光 | `SymbolType` | `'phase_shift'` 精度高；`'gray_code'` 大范围；`'multigrid'` 平衡 |
| 结构光 | `min_pattern_amplitude` | 10–30 |
| 光片法 | `MinGray` / `MinStrokeWidth` | 灰度 30–80；宽度 1–5 px |
| 摄影立体 | `MinGradient` / `ReconstructionMethod` | 梯度 5–10；`'poisson'` 精度高；`'l2'` 快 |

---

## 9. 相关分类

| 关联分类 | 协作方式 |
|----------|----------|
| **3D Object Model** | 重建输出点云 / 网格 → ObjectModel3D 句柄，用 3D Object Model 处理 |
| **Calibration** | 双目 / 单目必须先 `binocular_calibration` / `camera_calibration` |
| **3D Matching** | 重建的点云可直接喂给 `find_surface_model` 做 6D 匹配 |
| **Inspection** | 重建后的 3D 数据做尺寸测量 / 缺陷检测 |
| **Filters** | 双目匹配前的预处理（`gauss_filter`、`median_image`）提升匹配率 |
| **Matching** | 双目匹配的 SGM/NCC 算法与 `find_shape_model` 共享底层优化 |

---

## 10. 学习小结

3D Reconstruction 是 HALCON 把"2D 像素"变"3D 几何"的算子族，涵盖了工业上几乎所有的 3D 测量方案。

### 学习路线建议

1. **第 1 周**：理解视差 / 深度 / 距离的物理含义；跑通 `binocular_calibration` + `binocular_disparity_mg` + `disparity_to_distance` 标准双目 demo。
2. **第 2 周**：学结构光完整流程（`create_structured_light_model` → `decode_*` → `reconstruct_*`），理解投影图案原理。
3. **第 3 周**：学光片法（`calibrate_sheet_of_light` → `measure_*` → `apply_*`），理解激光三角测量。
4. **第 4 周**：学摄影立体（`photometric_stereo`），理解表面法向反推。
5. **第 5 周**：学多视角立体（`create_stereo_model`），了解 SfM/MVS 在 HALCON 的实现。

### 核心要点回顾

1. **方法选择 = 物理原理 + 硬件 + 精度需求**：
   - 双目（被动，≤0.1 mm）/ 结构光（主动，≤0.01 mm）/ 光片法（连续激光）/ 摄影立体（表面细节）。

2. **任何方法都必须先标定**：双目 → `binocular_calibration`；结构光 → 投影仪/相机内外参；光片法 → `calibrate_sheet_of_light`；摄影立体 → `radiometric_self_calibration`。

3. **重建输出统一为 ObjectModel3D**：所有方法的最终输出都能转 `ObjectModel3D`，进入 3D Object Model 算子链（简化、配准、拟合、可视化）。这是 HALCON 3D 视觉架构的统一性。

4. **误差来源集中在硬件**：双目（镜头畸变）、结构光（DLP 非线性）、光片法（运动机构）、摄影立体（光源方向精度）。

5. **选择 = 像素分辨率 × 测量精度 × 工作距离**：盲选双目；±0.01 mm 选结构光；显微选摄影立体；连续轮廓选光片法。

### 推荐示例程序

`%HALCONEXAMPLES%\hdevelop\3D-Reconstruction\` 30+ demo：必看 `binocular_calibration.hdev`、`binocular_disparity_mg.hdev`、`sheet_of_light.hdev`、`photometric_stereo.hdev`、`radiometric_self_calibration.hdev`。

掌握 3D Reconstruction 是 3D 测量、3D 检测、3D 抓取三大工业应用的核心。配合 3D Object Model、3D Matching 与 Calibration 三类算子，能覆盖工业 3D 视觉的 95% 应用场景。