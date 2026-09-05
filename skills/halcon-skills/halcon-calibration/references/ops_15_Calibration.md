# HALCON 算子分类详解：Calibration（相机标定）

> **HALCON 版本**：26.05.0.0 Progress
> **分类代码**：Calibration（相机标定 / 像素到世界坐标）
> **算子规模**：约 100 个
> **一级分类入口**：`C:\Program Files\MVTec\HALCON-26.05-Progress\doc\html\reference\operators\toc_calibration.html`
> **学习层级**：L1–L2（核心到进阶）
> **典型应用**：单目标定 / 双目标定 / 手眼标定 / 畸变校正 / 像素→世界坐标

---

## 1. 概述

Camera Calibration（相机标定）是 HALCON 中**连接 2D 像素坐标与 3D 物理世界**的桥梁。任何需要"像素→毫米"映射的项目（测量、抓取、定位）都必须先做标定。

HALCON 26.05 的 Calibration 分为 **11 个子分类**：

| 子分类 | 主要功能 | 算子数 |
|--------|---------|--------|
| Binocular | 双目标定 | ~5 |
| Calibration Object | 标定板生成与查找 | ~10 |
| Camera Parameters | 相机参数查询/转换 | ~12 |
| Hand-Eye | 手眼标定 | ~8 |
| Inverse Projection | 像素 ↔ 世界 | ~12 |
| Monocular | 单目标定 + 找标定板 | ~10 |
| Multi-view | 多相机联合标定 | ~6 |
| Projection | 3D → 2D 投影 | ~5 |
| Rectification | 极线校正 / 畸变校正 | ~12 |
| Self-calibration | 自标定（无标定板） | ~8 |
| Misc | 标定数据管理 | ~10 |

**标定类型选择**：

| 类型 | 适用 | 关键算子 |
|------|------|---------|
| **单目** | 固定单相机测距 | `camera_calibration` |
| **双目** | 双目立体视差 | `binocular_calibration` |
| **多视图** | 多相机协同 | `calibrate_cameras` |
| **手眼** | 机械臂 + 相机 | `calibrate_hand_eye` |
| **自标定** | 现场无标定板 | `radial_distortion_self_calibration` |
| **畸变校正** | 广角/鱼眼镜头 | `change_radial_distortion_image` |

---

## 2. 应用场景

### 场景 1：工厂自动光学测量（AOI）
- 检测 PCB 元件位置、焊点尺寸、字符；像素→毫米映射精度要求 ±0.05 mm。
- 核心：`camera_calibration` + `image_to_world_plane` + `gen_caltab`。

### 场景 2：机器人抓取（Eye-in-Hand）
- 相机装在机械臂末端；抓取时相机移动 → 必须先标定相机相对 TCP 的位姿。
- 核心：`calibrate_hand_eye` + `calibrate_cameras`（手眼联合）。

### 场景 3：物流体积量测（DWS）
- 称重+量方一体机；包裹体积测量；单目+大视场畸变校正。
- 核心：`camera_calibration` + `change_radial_distortion_image` + `image_to_world_plane`。

### 场景 4：医疗影像处理
- 内窥镜、显微镜下的 3D 测量；广角镜头畸变严重，必须校正。
- 核心：`radial_distortion_self_calibration`（现场无标定板）+ `change_radial_distortion_image`。

### 场景 5：智能驾驶辅助
- 车载摄像头标定（车道线检测、目标测距）；现场不便用标定板 → 自标定。
- 核心：`radial_distortion_self_calibration` + `stationary_camera_self_calibration`。

---

## 3. 子分类详解

### 3.1 Calibration Object（标定板）

- **生成**：`gen_caltab(NumRow, NumCol, PolygonShape, Diameter, CalTabFile)` / `create_caltab`（HALCON 26 推荐）。形状：`'circle'` / `'square'` / `'hexagon'`。
- **查找**：`find_caltab`（粗定位）/ `find_marks_and_pose`（**精定位 + 估计 Pose**）。
- **辅助**：`caltab_points`（读点坐标）/ `disp_caltab`（3D 显示）/ `sim_caltab`（模拟生成标定图）。

### 3.2 Camera Parameters（相机参数操作）

- **IO**：`read_cam_par` / `write_cam_par`。
- **转换**：`cam_par_to_cam_mat` / `cam_mat_to_cam_par`（与 3×3 内参矩阵互转）/ `cam_par_pose_to_hom_mat3d`（构造 4×4 矩阵）。
- **畸变修正**：`change_radial_distortion_cam_par`（调整畸变参数）/ `get/set_line_of_sight`（调整主光轴）。
- **查询**：`get_calib_data(..., 'params', CameraParam)`。

### 3.3 Monocular（单目）

- **核心流程**：`create_calib_data('calibration_object', 1, 1, ...)` → `set_calib_data_calib_object` → `set_calib_data('init_params')` → `find_caltab` + `find_marks_and_pose` + `set_calib_data_observ_points`（多次采集）→ `camera_calibration`（**求解**）→ `get_calib_data('params')`（取出）。
- **辅助**：`gen_caltab` / `find_caltab` / `find_marks_and_pose` / `set_calib_data('init_pose', ...)`。

### 3.4 Binocular（双目）

- `binocular_calibration(...)`：同时标定双相机内外参（基线 + 旋转）。
- `calibrate_cameras(...)`：多相机联合标定。

### 3.5 Hand-Eye（手眼）

- **核心**：`calibrate_hand_eye`（最常用）/ `hand_eye_calibration`（旧版向后兼容）。
- **辅助**：`get/set_calib_data('tool', ...)` / `create_calib_data('hand_eye', 1, 1, ...)` / `query_calib_data_observ`。
- **类型**：Eye-in-Hand（相机在末端）/ Eye-to-Hand（相机固定）；`calibrate_hand_eye` 自动识别。

### 3.6 Inverse Projection（像素 ↔ 世界）

- **像素 → 世界**：`image_to_world_plane`（整图）/ `image_points_to_world_plane`（点级）。
- **世界 → 像素**：`project_3d_point`（3D 点→像素）/ `project_point_hom_mat3d`（4×4 矩阵投影）。
- **辅助**：`get_circle_pose` / `get_rectangle_pose` / `convert_pose_type`（'Rp+T' / 'abg' / 'rpy' / 'rodriguez'）。

### 3.7 Multi-view（多视图）

- `calibrate_cameras`（联合优化多相机参数）/ `bundle_adjust_mosaic`（光束平差 + 镶嵌）。

### 3.8 Projection（3D → 2D）

- `project_hom_point_hom_mat3d` / `project_point_hom_mat3d` / `project_object_model_3d`。

### 3.9 Rectification（校正）

- **畸变校正**：`change_radial_distortion_image`（去除 / 增加径向畸变）/ `change_radial_distortion_cam_par`（同步更新参数）/ `change_radial_distortion_contours_xld` / `change_radial_distortion_points`。
- **极线校正**：`gen_binocular_rectification_map`（**核心**）/ `gen_binocular_proj_rectification`（投影校正，保留原始分辨率）/ `gen_grid_rectification_map` / `create/find_rectification_grid`。
- **应用**：`map_image(Image, Map, ImageMapped)`。

### 3.10 Self-calibration（自标定）

- **径向畸变自标定**：`radial_distortion_self_calibration(Image, Region, ..., CameraParam, ...)`（无标定板）。
- **辐射自标定**：`radiometric_self_calibration(Images, ...)`（估计相机响应函数）。
- **固定相机自标定**：`stationary_camera_self_calibration(ImageSeq, _, _, _, _, _, _)`（固定相机场景运动时自标定）。

### 3.11 Misc（标定数据管理）

- `create_calib_data` / `clear_calib_data`：创建/清除标定数据模型。
- `set_calib_data` / `get_calib_data`：通用读写。
- `set/get_calib_data_observ_points`：管理观测点。
- `set_calib_data_calib_object`：设置标定板描述。
- `query_calib_data_observ` / `read/write_calib_data` / `serialize/deserialize_calib_data`：查询、存档、序列化。

---

## 4. 核心算子详解

### 4.1 `create_calib_data` — 创建标定数据模型

- `create_calib_data(Type, NumCameras, NumCalibObjects, CalibDataID)`
- **Type**：`'calibration_object'`（标准）/ `'hand_eye'` / `'calibration_object_3d'` / `'line_scan'` / `'binocular'`（HALCON 26 引入）。

### 4.2 `camera_calibration` — 单目标定求解

- `camera_calibration(CalibDataID, ..., Error)`：从标定数据模型求解相机内参 + 标定板姿态。
- **关键参数**：`'area_threshold_polynomial'`（高阶畸变阈值，默认 0.1）/ `'optimize_pose'` / `'num_startup_funcs'`。
- **返回值**：`Error` 平均投影误差（pixel，< 0.1 为优）。

### 4.3 `find_marks_and_pose` — 找标定板 + 求 Pose

- `find_marks_and_pose(Image, CaltabRegion, CaltabFile, CameraParam, _, _, _, WorldPose, Rows, Cols, _)`：从图像中精确定位标定板特征点 + 估计相机 Pose。
- **关键参数**：`CameraParam`（内参）/ `Sigma`（高斯平滑，默认 1.0）/ `Threshold`（边缘阈值，默认 100）。
- **返回值**：`WorldPose`（相机相对标定板的 Pose）+ `Rows` / `Cols`（特征点像素坐标）。
- `Rows` / `Cols`：特征点像素坐标。

### 4.4 `calibrate_hand_eye` — 手眼标定

- `calibrate_hand_eye(CameraParam, CalibDataID, ToolTCP, ToolNo, HandEyePose, EyeInHandPose)`：解算相机与机械臂工具坐标系的相对位姿。
- **关键参数**：`CameraParam` / `CalibDataID` / `ToolTCP`（工具中心点相对法兰）/ `ToolNo`（工具编号）。
- **返回值**：`HandEyePose`（手→眼）/ `EyeInHandPose`（眼在手上），或 Eye-to-Hand 相反。

### 4.5 `image_to_world_plane` — 整图 → 世界平面

- `image_to_world_plane(Image, WorldPlaneImage, CameraParam, WorldPose, Width, Height, Scale, Interpolation)`：把畸变图像投影到世界平面，输出"鸟瞰图"。
- **关键参数**：`CameraParam`（内参 + 畸变）/ `WorldPose`（相机在世界平面上的 Pose）/ `Scale`（mm/pixel）/ `Interpolation`（`'nearest_neighbor'` / `'bilinear'` / `'bicubic'`）。

### 4.6 `image_points_to_world_plane` — 点级转换

- `image_points_to_world_plane(WorldPose, CameraParam, Rows, Cols, _, _, WorldX, WorldY)`：点级像素 → 世界坐标。

### 4.7 `change_radial_distortion_image` — 畸变校正

- `change_radial_distortion_image(Image, ImageRectified, Region, CameraParam, Mode, CamParamOut)`：去除或增加径向畸变。**Mode**：`'fixed'` / `'full'` / `'grid'` / `'adaptive'`。

### 4.8 `gen_binocular_rectification_map` — 双目极线校正

- `gen_binocular_rectification_map(MapL, MapR, CamParamL, CamParamR, RelPose, SubSampling, Method, MapLOut, MapROut)`：生成左右图校正映射。**Method**：`'geometric'`（默认）/ `'adaptive'`。

### 4.9 `radial_distortion_self_calibration` — 径向畸变自标定

- `radial_distortion_self_calibration(...)`：现场无标定板自动估计径向畸变系数。**适用**：监控、广角、嵌入式；自然场景中含可见直线。

### 4.10 `convert_pose_type` — Pose 表示转换

- `convert_pose_type(PoseIn, Order, PoseOut)`：在 'Rp+T' / 'abg' / 'rpy' / 'rodriguez' 等之间转换。

---

## 5. HDevelop 示例代码

### 示例 1：完整单目标定流水线

```hdevelop
* Calibration - Monocular Calibration Pipeline
* 适用：AOI 检测 PCB 元件

* === 1. 生成标定板 + 标定模型 ===
create_caltab(7, 7, 'circle', 1.5, 'caltab_custom_30mm.descr')
create_calib_data('calibration_object', 1, 1, CalibDataID)
set_calib_data_calib_object(CalibDataID, 0, 'caltab_30mm.descr')

* === 2. 设置初始相机参数 ===
InitCamParam := [0.012, 0, 4.0e-6, 4.0e-6, 1280, 960, 0, 0, 0, 0, 0, 0, 0, 0]
set_calib_data(CalibDataID, 'camera', 0, 'init_params', InitCamParam)

* === 3. 采集标定图像（≥ 12 张） ===
for I := 0 to 14 by 1
    read_image(Image, 'calib_image_' + (I+1)$'.2d' + '.tiff')
    find_caltab(Image, CaltabRegion, 'caltab_30mm.descr', 3, 0, 5)
    find_marks_and_pose(Image, CaltabRegion, 'caltab_30mm.descr', InitCamParam, 128, 10, 20, Pose, RCoord, CCoord, _)
    set_calib_data_observ_points(CalibDataID, 0, 0, I, RCoord, CCoord, 'all', Pose)
endfor

* === 4. 求解标定 + 取出参数 ===
camera_calibration(CalibDataID, [], Error)
get_calib_data(CalibDataID, 'camera', 0, 'params', CameraParam)
write_cam_par(CameraParam, 'camera_calibrated.dat')
disp_message(WindowHandle, 'Calibration Error: ' + Error$'.4f' + ' pixel', 'window', 12, 12, 'green', 'false')

* === 5. 像素 → 毫米验证 ===
WorldPose := [0, 0, 500, 0, 0, 0, 0]
read_image(TestImage, 'test_part.tiff')
image_to_world_plane(TestImage, WorldImage, CameraParam, WorldPose, 1280, 960, 0.05, 'bilinear')

Rows := [100, 200, 300]
Cols := [150, 250, 350]
image_points_to_world_plane(WorldPose, CameraParam, Rows, Cols, 'mm', _, WorldX, WorldY)

clear_calib_data(CalibDataID)
```

### 示例 2：手眼标定（Eye-in-Hand）

```hdevelop
* Calibration - Hand-Eye Calibration (Eye-in-Hand)
* 适用：相机装在机械臂末端

* === 1. 加载相机参数（已有） ===
read_cam_par('camera_calibrated.dat', CameraParam)

* === 2. 创建标定数据模型（手眼） ===
create_calib_data('hand_eye', 1, 1, CalibDataID)
set_calib_data_calib_object(CalibDataID, 0, 'caltab_30mm.descr')

* === 3. 加载机器人位姿（从控制器或文件） ===
NumPoses := 15
RobotPoses := []
for I := 0 to NumPoses-1 by 1
    RobotPoses[I] := ReadRobotPose(I)
endfor

* === 4. 采集图像 + 记录机器人 Pose ===
for I := 0 to NumPoses-1 by 1
    MoveRobotToPose(RobotPoses[I])
    grab_image(Image, AcqHandle)
    find_caltab(Image, CaltabRegion, 'caltab_30mm.descr', 3, 0, 5)
    find_marks_and_pose(Image, CaltabRegion, 'caltab_30mm.descr', CameraParam, 128, 10, 20, Pose, RCoord, CCoord, _)
    set_calib_data_observ_points(CalibDataID, 0, 0, I, RCoord, CCoord, 'all', Pose)
    set_calib_data(CalibDataID, 'tool', I, 'tool_pose', RobotPoses[I])
endfor

* === 5. 手眼标定求解 ===
* ToolTCP: TCP 相对法兰的位姿（已知）
ToolTCP := [0, 0, 65, 0, 0, 0, 0]
ToolNo := 0
calibrate_hand_eye(CameraParam, CalibDataID, ToolTCP, ToolNo, HandEyePose, EyeInHandPose)
write_pose(HandEyePose, 'hand_eye_pose.dat')

* === 6. 验证：用 Pose 转机器人坐标 ===
TargetInCamera := [100, 50, 200, 30, 0, 0, 0]
pose_compose(HandEyePose, TargetInCamera, TargetInBase)
clear_calib_data(CalibDataID)
```

### 示例 3：畸变校正 + 像素 → 世界

```hdevelop
* Calibration - Distortion Correction & World Coordinates
* 适用：广角镜头下的物流体积测量

* === 1. 标定 + 校正图像 ===
read_cam_par('wide_angle_camera.dat', CameraParam)
read_image(Image, 'logistics_scene.tiff')
change_radial_distortion_image(Image, RectifiedImage, [], CameraParam, 'adaptive', _)

* === 2. 定义工作平面（运输带面 Z = 0，相机俯视） ===
WorldPose := [0, 0, 0, 90, 0, 0, 0]

* === 3. 转换到世界坐标 ===
image_to_world_plane(Image, WorldImage, CameraParam, WorldPose, 2048, 1536, 1.0, 'bilinear')
* WorldImage 每个像素 = 1.0 mm

* === 4. 检测包裹并量方 ===
threshold(WorldImage, Region, 80, 255)
connection(Region, ConnectedRegions)
select_shape(ConnectedRegions, ['area', 'width', 'height'], 'and', [500, 100, 100], [1e6, 2048, 1536], Packages)

* 对每个包裹测尺寸（Length1, Length2 已经是 mm）
count_obj(Packages, NumPackages)
for I := 1 to NumPackages by 1
    select_obj(Packages, Package, I)
    smallest_rectangle2(Package, Row, Col, Phi, Length1, Length2)
    disp_message(WindowHandle, 'Package ' + I$'.0f' + ': ' + (2*Length1)$'.0f' + 'x' + (2*Length2)$'.0f' + ' mm',
                  'window', 30*I + 20, 12, 'green', 'false')
endfor
clear_calib_data(CalibDataID)
```

---

> **提示**：现场无标定板时可用 `radial_distortion_self_calibration` 自动估计畸变（要求场景含明显直线）。

## 6. 典型工业流水线

### 流水线 A：AOI 元件检测

```
固定相机 + 标定板（每 6 个月重标定）→ camera_calibration（≥ 15 张图）→ 存 CameraParam
实时：grab_image → image_to_world_plane → find_shape_model / select_shape
→ fit_circle_contour_xld → image_points_to_world_plane → 输出 mm 单位尺寸
```

### 流水线 B：机器人抓取（手眼）

```
标定台放 caltab（固定）→ 移动机械臂到 15+ Pose → 每 Pose grab_image + find_caltab
→ calibrate_hand_eye → 存 HandEyePose
实时：视觉找目标 Pose → pose_compose(HandEyePose, TargetInCamera, TargetInBase)
→ send socket → 机器人控制器
```

### 流水线 C：广角镜头体积测量

```
广角镜头 → change_radial_distortion_image → image_to_world_plane（俯视运输带）
→ 阈值 + 连通域 + select_shape（包裹）→ smallest_rectangle2（mm）→ 输出尺寸
```

### 流水线 D：现场免标定畸变校正

```
车载/监控相机 → radial_distortion_self_calibration（场景含直线）→ 校正 → 车道线/距离
```

---

## 7. 常见陷阱与最佳实践

### 陷阱 1：标定板图像不够多 / 角度不全
5 张全正面图 → 标定误差 > 0.5 pixel → 测距误差 > 0.5 mm。
- **最佳实践**：≥ 15 张图，覆盖视野四角 + 不同深度 + 不同姿态（30°/60°）。

### 陷阱 2：标定板厚度未设置
30 mm 厚的 caltab 但工作距离 100 mm → 误差。
- **最佳实践**：`gen_caltab` / `disp_caltab` 中 `CaltabThickness` 对应实际标定板厚度。

### 陷阱 3：焦距变化后未重新标定
调焦（zoom/focus）后 → 相机参数全错。
- **最佳实践**：焦距调整后**必须重新标定**；锁定镜头。

### 陷阱 4：图像畸变校正后未更新相机参数
`change_radial_distortion_image` 输出校正图，但相机参数未更新。
- **最佳实践**：用 `change_radial_distortion_cam_par` 同步更新。

### 陷阱 5：手眼标定图像数量不足
仅 5 张图 → 误差大。
- **最佳实践**：**至少 12 张**（HALCON 推荐 15+）；机械臂必须显著移动（>10 cm + >30° 旋转）。

### 陷阱 6：手眼类型搞错
相机装在末端但按 eye-to-hand 算 → Pose 全反。
- **最佳实践**：`calibrate_hand_eye` 自动识别类型；验证时取一个目标 `pose_compose` 看是否合理。

### 陷阱 7：自标定失败
`radial_distortion_self_calibration` 在白墙 / 纯色场景下找不到直线 → 失败。
- **最佳实践**：场景必须含明显直线（建筑、门框、栏杆）；否则必须用标定板。

### 陷阱 8：单位混用
相机焦距 8 mm、像素 5 µm、目标 0.5 m → 算出来 0.06 mm/pixel。
- **最佳实践**：`image_to_world_plane` 时显式声明 `Scale` = mm/pixel。

### 陷阱 9：双目校正时未先做内参畸变校正
`gen_binocular_rectification_map` 内部会校正，但**前提是相机参数已经包含畸变**。
- **最佳实践**：先 `binocular_calibration` 得到精确畸变参数，再做校正。

### 陷阱 10：`image_to_world_plane` 输出坐标系与机器人坐标系未对齐
`WorldPose` 与机器人基座方向不一致 → 转机器人时错位 90°。
- **最佳实践**：标定前先把 caltab 朝向与机器人坐标系对齐（X+ / Y+ 方向明确）。

---

## 8. 参数调优指南

### 单目 / 双目标定

| 方法 | 参数 | 调优 |
|------|------|------|
| 单目 | `Sigma` / `Threshold` | 1.0（默认）；噪声大 → 1.5–2.0；阈值 50–200 |
| 单目 | `'area_threshold_polynomial'` | 0.1（启用 K3）；1.0（不启用） |
| 双目 | 标定图数量 | ≥ 15 张（含深度变化） |
| 双目 | `Method`（校正） | `'geometric'` 默认；`'adaptive'` 高保真 |

### 手眼 / 畸变校正 / 自标定

| 方法 | 调优 |
|------|------|
| 手眼 | ≥ 15 张（HALCON 26 推荐 20）；≥ 10 cm 平移 + ≥ 30° 旋转；TCP 精度 ±0.1 mm |
| 畸变校正 | `Mode`：`'fixed'` / `'adaptive'` / `'grid'`；`'number_subpixel'`：1–5 |
| 自标定 | 场景必须含明显直线；≥ 5 张不同角度图 |

---

## 9. 相关分类

| 关联分类 | 协作方式 |
|----------|----------|
| **3D Matching** | 手眼标定 + 6D Pose → 机器人引导 |
| **3D Reconstruction** | 双目标定 `RelPose` 是视差测距基础 |
| **Image / Domain** | `image_to_world_plane` 输出图像可用 Image 类算子处理 |
| **Matching** | 世界坐标下的模板匹配精度远高于像素级 |
| **1D / 2D Metrology** | 世界坐标可直接作为测量坐标 |
| **Transformations** | `convert_pose_type` / `pose_compose` 是输出桥梁 |
| **Graphics → 3D Scene** | `disp_caltab` 可视化标定板 |

---

## 10. 学习小结

Calibration 是 HALCON 中**所有"像素→物理世界"映射**的算子族，是任何精度相关项目的必经环节。

### 学习路线建议

1. **第 1 周**：理解 CameraParam 数据结构（焦距 / 主点 / 畸变系数 / 内外参）；跑通标准单目标定（`gen_caltab` + `camera_calibration` + `image_to_world_plane`）。
2. **第 2 周**：掌握畸变校正（`change_radial_distortion_image`）、像素 ↔ 世界坐标（`image_points_to_world_plane` / `project_3d_point`）。
3. **第 3 周**：学手眼标定（`calibrate_hand_eye`）。
4. **第 4 周**：学双目 / 多视图联合标定（`binocular_calibration` / `calibrate_cameras`）。
5. **第 5 周**：学自标定（`radial_distortion_self_calibration`）。

### 核心要点回顾

1. **标定是精度的源头**：标定误差 0.1 pixel ≈ 工作距离的 0.1 × 像素物理尺寸。投入时间做标定质量评估远比优化后续算法回报高。
2. **CameraParam 是通用接口**：所有 2D↔3D 转换算子都需要 CameraParam；学好其生命周期和更新机制是基础。
3. **三种标定层次**：单目（基础）/ 双目（同时定内参+外参）/ 手眼（机器人视觉核心）。
4. **畸变校正是预处理标配**：广角/鱼眼镜头必须先 `change_radial_distortion_image`；校正后必须更新 CameraParam。
5. **自标定有场景限制**：要求场景含明显直线；纯色/模糊场景必须用标定板。
6. **单位/坐标系/旋转顺序** 是隐形陷阱：mm vs m、机器人基座方向、'abg' vs 'rpy' 都需明确。HALCON 默认 `'Rp+T'`（即 `'abg'`）。

### 推荐示例程序

`%HALCONEXAMPLES%\hdevelop\Calibration\` 30+ demo，必看：
- `camera_calibration.hdev` / `monocular_calibration_rectification.hdev` / `binocular_calibration.hdev` / `binocular_calibration_rectification.hdev`
- `calibrate_hand_eye_scara_*.hdev` / `radial_distortion_self_calibration.hdev`

掌握 Calibration 是从"视觉测试"到"工业视觉产品"的必经环节。任何精度 > 0.1 mm 的项目，必须从 Calibration 开始。