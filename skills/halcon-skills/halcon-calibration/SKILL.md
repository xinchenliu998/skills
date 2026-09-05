---
name: halcon-calibration
description: >-
  HALCON camera calibration and geometry: single-camera calibration
  (create_calib_data, set_calib_data_cam_param, set_calib_data_calib_object,
  find_calib_object, calibrate_cameras, get_calib_data), camera model & parameters
  (gen_cam_par_area_scan_division / polynomial / telecentric, change_radial_distortion_*),
  image-to-world / world-to-image transforms (image_points_to_world_plane,
  contour_to_world_plane_xld, image_to_world_plane, gen_image_to_world_plane_map,
  project_3d_point), stereo and hand-eye calibration (calibrate_hand_eye,
  set_calib_data_observ_pose), and pose/hom_mat3d transforms. Use this skill whenever
  a HALCON/HDevelop task converts pixels to real-world coordinates, calibrates a
  camera, corrects lens distortion, rectifies an image, estimates a pose from points
  (vector_to_pose), does hand-eye / robot vision, or works with hom_mat3d / pose
  transforms. Trigger on camera_calibration, find_calib_object, calibrate_cameras,
  gen_cam_par_*, image_points_to_world_plane, set_origin_pose, pose_to_hom_mat3d,
  change_radial_distortion_*, or when a measurement must be in millimeters/units.
---

# HALCON 相机标定与几何变换

> 定位：把"像素坐标"与"真实世界坐标"之间的桥接——相机内参、镜头畸变、像素↔世界平面、位姿变换、手眼标定。
> 编写规范见 `../_authoring/`（conventions.md 为精简总结；完整规范在 halcon_skill.md；脚本格式/CLI 见同名 *_reference.md）。

---

## 一、一句话选型

| 需求 | 手段 | 说明 |
|---|---|---|
| 求相机内参 | `create_calib_data`+`find_calib_object`+`calibrate_cameras` | 标定板 + 多角度图 |
| 像素点→世界坐标 | `image_points_to_world_plane` | 需内参+测量平面位姿 |
| 轮廓→世界坐标 | `contour_to_world_plane_xld` | 亚像素 |
| 图像矩形化（正交投影） | `image_to_world_plane` / `gen_image_to_world_plane_map`+`map_image` | 去透视/畸变 |
| 只去镜头畸变 | `change_radial_distortion_*` | `'adaptive'` 略缩防未定义 |
| 已知内参+≥3点求外参 | `vector_to_pose` | 控制点对 |
| 位姿/矩阵转换 | `pose_to_hom_mat3d`/`hom_mat3d_to_pose`/`set_origin_pose` | 刚体链 |
| 手眼标定 | `calibrate_hand_eye` | 机械手引导 |

---

## 二、相机模型与内参

相机类型（`CameraType`）决定内参元组：
- `'area_scan_division'`: [Focus, Kappa, Sx, Sy, Cx, Cy, W, H]（**默认**，division 单参数畸变，快、可解析逆、标定图少更稳）。
- `'area_scan_polynomial'`: [Focus, K1,K2,K3,P1,P2, Sx, Sy, Cx, Cy, W, H]（5 参数畸变，精度高但需迭代逆，要求板覆盖整个测量区）。
- `'area_scan_telecentric_division'`: [Magnification, Kappa, Sx, Sy, Cx, Cy, W, H]（**用放大率代替焦距**）。
- 远心带倾斜/超中心/线扫变体：`'*_tilt_*'`、`'*_hypercentric_*'`、`'line_scan_*'`（尾加 Vx,Vy,Vz m/scanline）。

初始值建议：Focus=名义焦距(如 0.008m)、Magnification=标称放大率(如 0.2)、Kappa=0.0、K1..P2=0、Sx/Sy=芯片像元(如 7e-6m)、Cx=W/2、Cy=H/2。
生成内参惯例算子：`gen_cam_par_area_scan_division` / `_polynomial` / `_telecentric_*`（每个相机类型一个）；`set_cam_par_data`/`write_cam_par`/`read_cam_par` 存取。

---

## 三、单相机标定 workflow

```hdevelop
create_calib_data ('calibration_object', 1, 1, CalibDataID)
set_calib_data_cam_param (CalibDataID, 0, [], StartCamPar)
set_calib_data_calib_object (CalibDataID, 0, 'calplate_80mm.cpd')
for I := 1 to NumImages
    find_calib_object (Image, CalibDataID, 0, 0, I, [], [])
endfor
calibrate_cameras (CalibDataID, Errors)          * Errors < 0.1px 为成功
get_calib_data (CalibDataID, 'camera', 0, 'params', CamParam)
get_calib_data (CalibDataID, 'calib_obj_pose', [0,1], 'pose', Pose)
set_origin_pose (Pose, 0, 0, 0.002, Pose)        * 补偿标定板厚度
```
- **标定板**：推荐 **HEX 排列**（`.cpd`）可部分遮挡/伸出图像；旧矩形板（`.descr`）须完整可见。
- **测量平面位姿** 3 种来源：①标定板直接放测量平面：`get_calib_data(...,'pose')`+`set_origin_pose` 补偿板厚；②标定后另拍板贴测量平面：再 `find_calib_object`；③已知 ≥3 不共线世界点及像素坐标：`vector_to_pose`。
- **坑**：失焦等价于改焦距，**标定后不可改焦点**；单张图只能测标定板平面内坐标；只用一个 pose 且板方位不变时无法同时定出焦距与相机位姿。

---

## 四、像素 ↔ 世界坐标
```hdevelop
* 点 (Scale 可送 'm'/1.0、'cm'/0.01、'mm'/0.001、'microns'/1e-6)
image_points_to_world_plane (CamParam, Pose, Row, Col, 'mm', X, Y)
* 轮廓
contour_to_world_plane_xld (Contours, CT, CamParam, Pose, 1)
* 区域 → 先转轮廓 (有孔用 'border_holes')
gen_contour_region_xld (Region, ..., 'border')
* 世界 → 图像
pose_to_hom_mat3d (Pose, HomMat3D)
affine_trans_point_3d (HomMat3D, X, Y, Z, Xt, Yt, Zt)
project_3d_point (CamParam, Xt, Yt, Zt, Row, Col)
```

**图像矩形化（高效：一次生成 map 多次用）**
```hdevelop
gen_image_to_world_plane_map (Map, CamParam, PoseForCentered, W, H, Wm, Hm, Scale, 'bilinear')
map_image (Image, Map, ImageMapped)
```
- `Scale`：使 ROI 中心处原图像素与校正图像素**大小相近**；过大差异锯齿/平滑。
- 常用过程：`parameters_image_to_world_plane_centered`（中心点居中+等比）、`parameters_image_to_world_plane_entire`（全图可见，取 max(ScaleX,ScaleY)）。

**仅去镜头畸变**
```hdevelop
change_radial_distortion_cam_par ('adaptive', CamPar, 0, CamParVirtual)   * 'fixed'/'fullsize'/'adaptive'/'preserve_resolution'
change_radial_distortion_image (Image, ROI, ImgRect, CamParOrig, CamParVirtual)
change_radial_distortion_contours_xld / change_radial_distortion_points
gen_radial_distortion_map (Map, Orig, Virtual, 'bilinear')
```
- 默认 `'adaptive'`；`'fixed'`(κ=0,可见场景变小)/`'fullsize'`(全图,边缘未定义)/`'preserve_resolution'`(放大保分辨率)。

**精度坑**：测量只对平面成立——物体偏离测量平面产生位移 `Δr = Δz·r/z`，越靠近边缘、平面越倾斜、r 越大偏差越大；多平面用 `set_origin_pose` 为每层建 pose；严重倾斜+厚物会看到侧壁，通常让光轴垂直测量平面。

---

## 五、位姿与 3D 变换

```hdevelop
* 链式搭刚体：identity → translate_local/rotate_local（绕新轴）
hom_mat3d_identity (H)
hom_mat3d_translate_local (H, Tx,Ty,Tz, H)
hom_mat3d_rotate_local (H, Angle, Ax, Ay, Az, H)
* ↔ pose
hom_mat3d_to_pose (H, 'Rp+T', 'gba', 'point', Pose)
pose_to_hom_mat3d (Pose, H)
set_origin_pose (Pose, X, Y, Z, NewPose)
pose_invert / pose_compose / convert_pose_type
```
- `create_pose(Rx,Ry,Rz,...)` 角度用**度**；`hom_mat3d_rotate`/**rotate_local 用弧度**。
- 机器人旋转顺序常为 `'abg'`（R=Rz·Ry·Rx）；HALCON 默认 `'gba'`。矩阵链从左向右读=绕"新"轴，从右向左=绕"旧"轴。

---

## 六、手眼标定（Robot Vision）

```hdevelop
create_calib_data ('hand_eye_stationary_cam', 1, 1, CalibDataID)   * 或 moving_cam / scara_moving_cam
set_calib_data (CalibDataID, 'model', 'general', 'optimization_method', 'nonlinear')
set_calib_data_cam_param + set_calib_data_calib_object
for I: find_calib_object (Image, CalibDataID, 0, 0, I, [], [])     * 板→相机位姿; 3D传感器用 set_calib_data_observ_pose
* 机器人工具位姿（每观测）：read_pose → set_calib_data (CalibDataID,'tool',I,'tool_in_base_pose',ToolInBasePose)
calibrate_hand_eye (CalibDataID, Errors)   * Errors=[平移RMS,旋转RMS,平移最大,旋转最大]
get_calib_data (CalibDataID, 'camera', 0, 'base_in_cam_pose', baseHcam)
```
- 支持配置：**Moving camera**（装工具端）/ **Stationary camera**（外置固定）；Articulated（6DOF）vs SCARA（4DOF，**必须先标定相机**+手动解 Z 方向歧义）。
- **坐标链**：moving `camHcal = camHtool·toolHbase·baseHcal`；stationary `camHcal = camHbase·baseHtool·toolHcal`。
- **用标定抓取**：stationary `baseHobj = baseHcam·camHobj`（gripper 姿态 `baseHtool(grip)=baseHobj·(toolHgripper)^-1`）；moving `baseHobj = baseHtool(acq)·toolHcam·camHobj`。
- **坑**：工具坐标系若不在夹爪（tool center point）需加 tool↔gripper 变换（无法由手眼标定得到，须测量/CAD）；强烈建议 HEX 标定板；机器人位姿顺序须与 `create_pose` 匹配。

---

## 七、圆形/矩形位姿估计
- 圆：提取 2D 椭圆 + 内参 + 已知半径 → `get_circle_pose`（返回两个相反朝向可能位姿）。
- 矩形：轮廓分 4 直线段求交点成四边形 + 已知尺寸 → `get_rectangle_pose`。

---

## 八、引用
- 中文算子总览：`references/ops_15_Calibration.md`、`ops_19_Transformations.md`
- 逐算子签名/默认值：`references/ref_OPERATOR_REFERENCE.md`（Calibration / Transformations 章）。
- 关联：`halcon-measuring-metrology`（世界坐标测量）、`halcon-3d-vision`（立体/位姿）、`halcon-matching`（标定版匹配、perspective/descriptor）、`halcon-vision-workflow`（机器人抓取）。


---

## 用例参考（example_*.md）

本 skill 目录下 `references/` 含以下项目里抽出的真实用例（按主题归档，可直接借鉴实现思路/算子组合）：

- `references/example_camera_calibration.md`
- `references/example_chessboard_corner_detection.md`
- `references/example_focal_length_triangle.md`
- `references/example_libcbdetect_chessboard_corners.md`
