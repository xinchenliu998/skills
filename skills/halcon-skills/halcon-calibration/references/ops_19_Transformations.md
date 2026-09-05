# HALCON 算子分类详解：Transformations（坐标变换）

> **HALCON 版本**：26.05.0.0 Progress
> **算子数量**：约 60 个
> **一级分类目录**：`toc_transformations.html`
> **学习层级**：L1–L3（必学 + 进阶 + 3D 高级）

---

## 1. 概述

Transformations 是 HALCON 几何数学的"**核心**"——所有"位置 → 姿态 → 投影"链路都依赖它。该分类分为 7 个子分类：

1. **2D**：2D 仿射/投影变换链（`hom_mat2d_*` + `vector_to_*`）
2. **3D**：3D 仿射变换链 + Pose 概念（`hom_mat3d_*`）
3. **Dual Quaternions**：对偶四元数（无奇点的 3D 旋转表示）
4. **Poses**：位姿（6D：3 旋转 + 3 平移）
5. **Quaternions**：四元数
6. **Misc**：径向畸变矫正等
7. **Vector Field**：光流场（部分归此处）

HALCON 中"位置"和"姿态"严格区分：
- **Position**（位置）：单点坐标 `(Row, Col)` 或 `(X, Y, Z)`
- **Pose**（位姿）：6D 自由度 `(X, Y, Z, Rx, Ry, Rz)`，描述"对象在世界中的位置和朝向"

理解 2D / 3D 变换链 + Pose 的相互转换 = 掌握 HALCON 几何 90%。

---

## 2. 应用场景

### 场景 1：模板匹配后对齐（3C 元件对位）

`find_shape_model` 返回目标位置 `(Row, Column, Angle)` → `vector_angle_to_rigid` 构造 2D 仿射矩阵 → `affine_trans_image` 把整图对齐到参考位姿 → 在统一坐标系下做后续测量。

### 场景 2：手眼标定（机器人抓取）

机械臂移动相机从多个角度拍摄标定板 → `calibrate_hand_eye` 算出 `HandEyePose` + `CamPose` → 推理阶段 `find_surface_model` 拿到工件位姿 → `pose_compose` 与 `HandEyePose` 组合 → 转换到机器人基坐标系，发送给机械臂。

### 场景 3：图像畸变矫正

广角相机拍摄的桶形畸变 → `change_radial_distortion_cam_par` 修改内参 → `change_radial_distortion_image` 矫正图像 → 后续处理精度提升。

### 场景 4：3D 点云配准（ICP 初值）

多个点云片段需要配准 → `register_object_model_3d_pair` 计算 4×4 变换矩阵 → `pose_compose` 与全局位姿累积 → `affine_trans_object_model_3d` 应用变换。

### 场景 5：旋转的连续插值（相机/工件动画）

需要在两个姿态间平滑过渡 → 四元数 SLERP（`quat_interpolate`）或对偶四元数（`dual_quat_interpolate`）→ 避免欧拉角的万向锁问题。

### 场景 6：多相机协同（双目/多目）

左右相机标定得到双目外参 `RelPose` → 推理时左图像素 → 三角化 → 世界坐标。

---

## 3. 子分类详解

### 3.1 2D 变换 — 约 18 算子

#### 矩阵构造

| 算子 | 用途 |
|------|------|
| `hom_mat2d_identity` | 单位矩阵 |
| `hom_mat2d_translate` | 平移 |
| `hom_mat2d_rotate` | 旋转（绕原点） |
| `hom_mat2d_scale` | 缩放 |
| `hom_mat2d_slant` | 错切 |
| `hom_mat2d_reflect` | 反射 |
| `hom_mat2d_compose` | 矩阵组合（矩阵乘法） |
| `hom_mat2d_invert` | 求逆 |
| `hom_mat2d_determinant` | 行列式 |
| `hom_mat2d_transpose` | 转置 |
| `hom_mat2d_to_affine_par` | 矩阵 → 仿射参数（角度+尺度） |

#### 从其他形式构造

| 算子 | 用途 |
|------|------|
| `vector_angle_to_rigid` | (Row1, Col1, Phi1) → (Row2, Col2, Phi2) 构造刚体变换 |
| `vector_to_rigid` | (Row1, Col1, Row2, Col2) 构造纯平移 |
| `vector_to_similarity` | 相似变换（含缩放） |
| `vector_to_aniso` | 各向异性缩放 |
| `vector_to_hom_mat2d` | 点对构造（需要 ≥ 3 对） |
| `vector_to_proj_hom_mat2d` | 投影变换构造（需要 ≥ 4 对） |
| `hom_vector_to_proj_hom_mat2d` | 同上（齐次坐标版本） |
| `point_line_to_hom_mat2d` | 1 点 + 1 线 → 矩阵 |

#### 矩阵应用

| 算子 | 用途 |
|------|------|
| `affine_trans_point_2d` | 单点变换 |
| `affine_trans_pixel` | 像素坐标（含半像素偏移校正） |
| `projective_trans_pixel` | 投影变换像素 |
| `affine_trans_image` / `affine_trans_image_size` | 图像变换 |
| `affine_trans_region` | 区域变换 |
| `affine_trans_contour_xld` | XLD 变换 |

### 3.2 3D 变换 — 约 25 算子

类似 2D 全套，加 3D 专属：

| 算子 | 用途 |
|------|------|
| `hom_mat3d_identity` / `translate` / `rotate` / `scale` / `slant` / `reflect` | 同 2D |
| `hom_mat3d_compose` / `invert` / `determinant` / `transpose` | 矩阵操作 |
| `hom_mat3d_axis_angle` / `hom_mat3d_axis_angle_pose` | 旋转向量构造 |
| `hom_mat3d_rotate_x` / `rotate_y` / `rotate_z` | 绕单轴旋转 |
| `vector_to_hom_mat3d` | 通用点对构造 |
| `vector_to_pose` | 通用 6D Pose 构造 |
| `pose_to_hom_mat3d` / `hom_mat3d_to_pose` | 互转 |
| `cam_par_pose_to_hom_mat3d` | 相机参数 + Pose → 矩阵 |
| `point_pluecker_line_to_hom_mat3d` | Plücker 线 → 矩阵 |
| `affine_trans_point_3d` | 3D 点变换 |
| `projective_trans_point_3d` | 透视 3D 点 |
| `projective_trans_hom_point_3d` | 齐次 3D 点 |
| `project_hom_point_hom_mat3d` | 矩阵上 3D 投影 |
| `project_point_hom_mat3d` | 矩阵上点投影 |
| `project_3d_point` | 3D 点 → 图像像素 |
| `convert_point_3d_cart_to_spher` / `spher_to_cart` | 笛卡尔 ↔ 球坐标 |
| `affine_trans_object_model_3d` / `projective_trans_object_model_3d` | 3D 对象模型变换 |
| `project_object_model_3d` | 3D 模型投影到图像 |

### 3.3 Poses — 约 12 算子

| 算子 | 用途 |
|------|------|
| `create_pose` | 创建 Pose |
| `pose_compose` | Pose 组合（矩阵乘法） |
| `pose_invert` | 求逆 |
| `pose_average` | 多个 Pose 求平均 |
| `pose_to_hom_mat3d` / `hom_mat3d_to_pose` | 与矩阵互转 |
| `pose_to_quat` / `quat_to_pose` | 与四元数互转 |
| `pose_to_dual_quat` / `dual_quat_to_pose` | 与对偶四元数互转 |
| `convert_pose_type` | 旋转表示转换（RPY/ABG/Rodrigues） |
| `get_pose_type` | 查询类型 |
| `read/write_pose` | 持久化 |
| `serialize/deserialize_pose` | 序列化 |
| `trans_pose_shape_model_3d` | 3D Shape Model 位姿变换 |
| `set_origin_pose` | 设置 Pose 原点 |

### 3.4 Quaternions — 约 10 算子

| 算子 | 用途 |
|------|------|
| `axis_angle_to_quat` | 旋转向量 → 四元数 |
| `quat_compose` | 四元数乘法 |
| `quat_conjugate` | 共轭 |
| `quat_interpolate` | SLERP 插值 |
| `quat_normalize` | 归一化 |
| `quat_to_hom_mat3d` / `quat_to_pose` | 与其他形式互转 |
| `quat_rotate_point_3d` | 四元数旋转点 |
| `serialize/deserialize_quat` | 序列化 |

### 3.5 Dual Quaternions — 约 12 算子

| 算子 | 用途 |
|------|------|
| `dual_quat_compose` | 对偶四元数乘法 |
| `dual_quat_conjugate` | 共轭 |
| `dual_quat_interpolate` | 双四元数插值（SCLERP） |
| `dual_quat_normalize` | 归一化 |
| `dual_quat_to_hom_mat3d` / `dual_quat_to_pose` / `dual_quat_to_screw` | 互转 |
| `dual_quat_trans_line_3d` / `trans_point_3d` | 变换线/点 |
| `screw_to_dual_quat` | 螺旋运动 → 对偶四元数 |
| `pose_to_dual_quat` | Pose → 对偶四元数 |
| `serialize/deserialize_dual_quat` | 序列化 |

### 3.6 Misc — 约 5 算子

| 算子 | 用途 |
|------|------|
| `change_radial_distortion_cam_par` | 修改相机内参 |
| `change_radial_distortion_image` | 图像畸变矫正 |
| `change_radial_distortion_contours_xld` | XLD 畸变矫正 |
| `change_radial_distortion_points` | 点畸变矫正 |
| `vector_field_to_hom_mat2d` | 光流场 → 2D 变换 |

---

## 4. 核心算子详解

### 4.1 `vector_angle_to_rigid`

```hdevelop
* 2D 刚体变换（最常用）
* 把 (Row1, Col1, Phi1) → (Row2, Col2, Phi2) 构造为 3×3 矩阵
vector_angle_to_rigid(Row1, Col1, Phi1, Row2, Col2, Phi2, HomMat2D)

* 应用
affine_trans_image(Image, ImageAligned, HomMat2D, 'constant', 'false')
affine_trans_region(Region, RegionAligned, HomMat2D, 'nearest_neighbor')
```

### 4.2 `hom_mat2d_compose`

```hdevelop
* 矩阵组合：先 T1 后 T2 = T2 * T1
hom_mat2d_compose(HomMat2D1, HomMat2D2, HomMat2DCombined)

* 注意：HALCON 中矩阵乘法顺序与数学相反（矩阵右乘新变换）
```

### 4.3 `hom_mat2d_invert`

```hdevelop
hom_mat2d_invert(HomMat2D, HomMat2DInv)
* 用于"取消对齐"：把对齐后的坐标变换回原图坐标
```

### 4.4 `vector_to_hom_mat2d`

```hdevelop
* 从 ≥ 3 个点对构造 2D 仿射矩阵
vector_to_hom_mat2d(SourceRows, SourceCols, TargetRows, TargetCols, HomMat2D)
* Source → Target 的变换矩阵
```

### 4.5 `vector_to_proj_hom_mat2d`

```hdevelop
* 从 ≥ 4 个点对构造投影（透视）变换矩阵
vector_to_proj_hom_mat2d(SourceRows, SourceCols, TargetRows, TargetCols, HomMat2D)
```

### 4.6 `affine_trans_point_2d`

```hdevelop
affine_trans_point_2d(HomMat2D, Row, Col, RowTrans, ColTrans)
* 单点变换
```

### 4.7 `affine_trans_pixel`

```hdevelop
* 与 affine_trans_point_2d 类似，但含半像素偏移校正
* 用法：当像素中心在 (0.5, 0.5) 而非 (0, 0) 时，输出更准
affine_trans_pixel(HomMat2D, Row, Col, RowTrans, ColTrans)
```

### 4.8 `create_pose`

```hdevelop
* 创建 6D 位姿：X, Y, Z 平移 + Rx, Ry, Rz 旋转（任意欧拉角顺序）
create_pose(100.0, 50.0, 200.0, 0.0, 0.0, 1.5708, 'Rp+T', 'ordered', Pose)
* OrderOfRotation：'ordered'（按 Rx→Ry→Rz 顺序） / 'gba'（ZYX intrinsic） / ...
* OrderOfTranslation：'Rp+T'（先转后平移） / 'Rp+T'（HALCON 默认）
```

### 4.9 `pose_compose`

```hdevelop
pose_compose(Pose1, Pose2, PoseResult)
* PoseResult = Pose2 * Pose1（先应用 Pose1，再应用 Pose2）
* 注意与矩阵乘法的方向
```

### 4.10 `pose_invert`

```hdevelop
pose_invert(Pose, PoseInv)
* 用于"撤销"姿态
```

### 4.11 `pose_average`

```hdevelop
* 多个 Pose 加权平均（用于多传感器融合）
pose_average(Poses, Weights, 'iterative', 0.001, AveragePose)
```

### 4.12 `convert_pose_type`

```hdevelop
* 旋转表示转换
convert_pose_type(Pose, 'Rp+T', 'abg', 'gfixed', PoseNew)
* OrderOfRotation：'Rp+T'（旋转向量）/ 'abg'（欧拉角）/ 'rpy'（Roll-Pitch-Yaw）
* ViewOfTransform：'gfixed'（固定坐标轴） / 'omfixed'（固定原点）
```

### 4.13 `axis_angle_to_quat`

```hdevelop
* 旋转向量 → 四元数
* 旋转向量：axis × angle 打包成一个 3D 向量（方向 = 轴，模长 = 角度）
axis_angle_to_quat(0.0, 0.0, 1.5708, Quat)
```

### 4.14 `quat_interpolate`

```hdevelop
* 四元数 SLERP（球面线性插值）
quat_interpolate(Quat1, Quat2, 0.5, 'SLERP', QuatMid)
* t=0 时为 Quat1，t=1 时为 Quat2
```

### 4.15 `dual_quat_compose` / `dual_quat_interpolate`

```hdevelop
* 对偶四元数 = 普通四元数 + 平移部分的对偶四元数
* 用于：同时旋转+平移的连续插值（无奇点）

dual_quat_compose(DQ1, DQ2, DQResult)
dual_quat_interpolate(DQ1, DQ2, 0.5, 'SCPLERP', DQMid)
```

### 4.16 `hom_mat3d_compose` / `hom_mat3d_invert`

```hdevelop
* 与 2D 同名算子相同语义，但矩阵维度 4×4
hom_mat3d_compose(HomMat3D1, HomMat3D2, HomMat3DCombined)
hom_mat3d_invert(HomMat3D, HomMat3DInv)
```

### 4.17 `pose_to_hom_mat3d` / `hom_mat3d_to_pose`

```hdevelop
* Pose ↔ 4×4 矩阵互转
pose_to_hom_mat3d(Pose, HomMat3D)
hom_mat3d_to_pose(HomMat3D, Pose)
```

### 4.18 `change_radial_distortion_cam_par` / `change_radial_distortion_image`

```hdevelop
* 修改相机内参（去除/添加径向畸变）
change_radial_distortion_cam_par(CamParIn, CamParOut, 0.0)
* 'CamParOut' = 内参，畸变系数 0 = 无畸变

* 应用：矫正图像
change_radial_distortion_image(Image, ImageRectified, CamParIn, CamParOut)
```

### 4.19 `vector_field_to_hom_mat2d`

```hdevelop
* 光流场 → 2D 变换矩阵（每像素一个）
vector_field_to_hom_mat2d(VectorField, HomMat2Ds)
* 用于：拼接对齐（光流法）、形变校正
```

---

## 5. HDevelop 示例代码

### 示例 1：模板匹配后对齐

```hdevelop
* Transformations_Align.hdev
* 找到模板位置，把当前图对齐到参考位姿

read_image(Image, 'ic_pin')
dev_open_window(0, 0, 512, 512, 'black', WindowHandle)
dev_display(Image)

* 假设参考位姿：(300, 300, 0°) —— 模板中心
RefRow := 300
RefCol := 300
RefPhi := 0.0

* 模板匹配
find_shape_model(Image, ShapeModelID, 0, 6.28, 0.7, 1, 0.5, 'least_squares', 0, 0.9, Row, Column, Angle, Score)

* 构造对齐矩阵
vector_angle_to_rigid(Row, Column, Angle, RefRow, RefCol, RefPhi, HomMat2D)

* 应用对齐
affine_trans_image(Image, ImageAligned, HomMat2D, 'constant', 'false')

* 显示
dev_clear_window()
dev_display(ImageAligned)
set_color(WindowHandle, 'red')
disp_cross(WindowHandle, RefRow, RefCol, 12, 0)
```

### 示例 2：3D 旋转表示互转

```hdevelop
* Transformations_Pose_Convert.hdev
* 在不同旋转表示间互转

* 1. 用欧拉角创建 Pose
create_pose(100.0, 200.0, 300.0, 0.1, 0.2, 0.3, 'Rp+T', 'ordered', Pose)

* 2. 转换为欧拉角表示 (RPY)
convert_pose_type(Pose, 'Rp+T', 'abg', 'gfixed', PoseEuler)

* 3. 转换为四元数
pose_to_quat(Pose, Quat)
* Quat = [qw, qx, qy, qz]

* 4. 转换为对偶四元数
pose_to_dual_quat(Pose, DualQuat)

* 5. 转换为 4×4 矩阵
pose_to_hom_mat3d(Pose, HomMat3D)

* 6. 显示各种表示
disp_text(WindowHandle, 'Original (Rp+T):', 'window', 12, 12, 'yellow', 'box', 'black')
disp_text(WindowHandle, '  X=' + Pose[0]$'.2f', 'window', 30, 12, 'white', [], [])
disp_text(WindowHandle, '  Y=' + Pose[1]$'.2f', 'window', 50, 12, 'white', [], [])
disp_text(WindowHandle, '  Z=' + Pose[2]$'.2f', 'window', 70, 12, 'white', [], [])
disp_text(WindowHandle, 'Euler (abg):', 'window', 100, 12, 'yellow', 'box', 'black')
disp_text(WindowHandle, '  a=' + PoseEuler[3]$'.2f rad', 'window', 120, 12, 'white', [], [])
```

### 示例 3：手眼标定结果应用（机器人抓取）

```hdevelop
* Transformations_Hand_Eye.hdev
* 把相机检测到的工件 Pose 转换为机械臂基坐标系

* 假设：
* HandEyePose = 手眼关系（提前标定好）
* WorkPose = find_surface_model 返回的工件位姿（相机坐标系）

HandEyePose := [-0.05, -0.02, 0.10, 0.0, 0.0, 1.5708, 0]
*   X=-0.05, Y=-0.02, Z=0.10 m（相机相对于机械臂末端）
*   Rx=0, Ry=0, Rz=π/2（相机相对机械臂的朝向）

* 相机检测到工件位姿
WorkPose := [0.012, -0.005, 0.350, 0.0, 0.0, 0.5]

* 转换为机械臂基坐标系
* BasePose = HandEyePose * WorkPose（先应用 WorkPose，再应用 HandEyePose）
pose_compose(HandEyePose, WorkPose, BasePose)

disp_text(WindowHandle, 'Target Pose for Robot:', 'window', 12, 12, 'yellow', 'box', 'black')
disp_text(WindowHandle, '  X=' + BasePose[0]$'.3f' + ' m', 'window', 30, 12, 'white', [], [])
disp_text(WindowHandle, '  Y=' + BasePose[1]$'.3f' + ' m', 'window', 50, 12, 'white', [], [])
disp_text(WindowHandle, '  Z=' + BasePose[2]$'.3f' + ' m', 'window', 70, 12, 'white', [], [])
```

### 示例 4：图像畸变矫正

```hdevelop
* Transformations_Distortion.hdev
* 矫正广角相机的桶形畸变

* 加载相机内参（提前标定）
read_cam_par('wide_angle_campar.dat', CamParIn)

* 1. 矫正内参（去除径向畸变）
change_radial_distortion_cam_par(CamParIn, CamParRectified, 0.0)

* 2. 应用到图像
read_image(Image, 'wide_angle/building')
change_radial_distortion_image(Image, ImageRectified, CamParIn, CamParRectified)

* 显示对比
dev_open_window(0, 0, 1024, 512, 'black', WindowHandle)
dev_display(Image)
disp_text(WindowHandle, 'Original (distorted)', 'window', 12, 12, 'red', 'box', 'black')

dev_open_window(0, 512, 1024, 512, 'black', WindowHandle2)
dev_display(ImageRectified)
disp_text(WindowHandle2, 'Rectified', 'window', 12, 12, 'green', 'box', 'black')
```

### 示例 5：四元数 SLERP 插值（相机动画）

```hdevelop
* Transformations_Quaternion_Interp.hdev
* 用 SLERP 在两个姿态间平滑过渡

* 起始姿态：朝向 +X
QuatStart := [1, 0, 0, 0]

* 终止姿态：绕 Z 旋转 90°
axis_angle_to_quat(0, 0, 1.5708, QuatEnd)

* 在两者间均匀插值 11 帧
NumSteps := 11
gen_empty_obj(Poses)
for i := 0 to NumSteps-1 by 1
    t := i / (NumSteps - 1.0)
    quat_interpolate(QuatStart, QuatEnd, t, 'SLERP', QuatMid)
    
    * 转 Pose（位置假设为 0）
    create_pose(0, 0, 0, 0, 0, 0, 'Rp+T', 'ordered', PoseTmp)
    quat_to_pose(QuatMid, PoseTmp, PoseMid)
    
    * 显示
    dev_display(...)
endfor
```

---

## 6. 典型工业流水线

### 流水线 A：模板匹配 → 对齐 → 测量

```hdevelop
* 1. 加载模板
read_shape_model('ic_pin_model.shm', ShapeModelID)

* 2. 推理 + 对齐
find_shape_model(Image, ShapeModelID, ..., Row, Column, Angle, Score)
vector_angle_to_rigid(Row, Column, Angle, RefRow, RefCol, 0.0, HomMat2D)
affine_trans_image(Image, ImageAligned, HomMat2D, 'constant', 'false')

* 3. 在统一坐标系下测量
add_metrology_object_circle_measure(MetrologyHandle, 300, 300, 50, 20, 20, 5)
apply_metrology_model(ImageAligned, MetrologyHandle)
```

### 流水线 B：3D 抓取位姿转换

```hdevelop
* 1. 标定（一次性）
calibrate_hand_eye(CamParam, CalibDataID, ToolTCP, ToolNo, HandEyePose, EyeInHandPose)

* 2. 推理时
find_surface_model(SceneOM3D, SurfaceModelID, ..., CamPose, Score, SurfaceResult)

* 3. 转机器人坐标系
* BasePose = HandEyePose * CamPose
pose_compose(HandEyePose, CamPose, TargetBasePose)

* 4. 发送给机械臂（通过 socket）
serialize_pose(TargetBasePose, SerializedItem)
send_serialized_item(Socket, SerializedItem)
```

### 流水线 C：多目相机协同

```hdevelop
* 左相机检测到目标
find_shape_model(ImageL, ModelID, ..., RowL, ColL, AngleL, Score)
create_pose(XL, YL, 0, 0, 0, AngleL, 'Rp+T', 'ordered', PoseL)

* 构造左相机的世界位姿（已知）
CamLWorldPose := [0, 0, 1000, 0, 0, 0]  * 假设世界坐标

* 转世界坐标
pose_compose(CamLWorldPose, PoseL, WorldPose)

* 右相机同时检测（验证一致性）
find_shape_model(ImageR, ModelID, ..., RowR, ColR, AngleR, Score)
create_pose(XR, YR, 0, 0, 0, AngleR, 'Rp+T', 'ordered', PoseR)
pose_compose(CamRWorldPose, PoseR, WorldPoseR)

* 检查一致性（误差 < 阈值）
```

---

## 7. 常见陷阱与最佳实践

### 陷阱 1：`hom_mat2d_compose` 与数学相反

```hdevelop
* 数学：T2 * T1 表示"先 T1 后 T2"
* HALCON：hom_mat2d_compose(T1, T2, T) 中 T = T2 * T1
* 阅读代码时容易混淆，建议统一语义："应用顺序从右到左"
```

### 陷阱 2：`vector_angle_to_rigid` 的旋转中心

```hdevelop
* vector_angle_to_rigid(Row1, Col1, Phi1, Row2, Col2, Phi2, ...)
* 等价于：
* 1. 平移到 (-Row1, -Col1)
* 2. 旋转 Phi2 - Phi1
* 3. 平移到 (Row2, Col2)
* 顺序是：先平移到原点 → 旋转 → 平移到目标
```

### 陷阱 3：Pose 类型混淆

HALCON 有 4 种 Pose 类型表示：
- `'Rp+T'`：旋转向量（axis-angle），HALCON 默认
- `'abg'`：欧拉角（ZYX 顺序）
- `'rpy'`：Roll-Pitch-Yaw
- `'rodriguez'`：罗德里格向量

**最佳实践**：始终明确指定 OrderOfRotation（如 `'ordered'`），避免跨 HALCON 版本不一致。

### 陷阱 4：`pose_compose` 的方向

```hdevelop
* pose_compose(A, B, C)：C = B * A
* 应用顺序：先 A 后 B
* 等价于："A 在最里面，B 在最外面"
```

### 陷阱 5：欧拉角的万向锁（Gimbal Lock）

欧拉角在某些特定姿态（如 Pitch = ±90°）会失去一个自由度，导致连续插值出错。

**最佳实践**：涉及连续插值时，用四元数（`quat_interpolate`）或对偶四元数（`dual_quat_interpolate`）。

### 陷阱 6：`affine_trans_pixel` vs `affine_trans_point_2d`

两者数学等价，但 `affine_trans_pixel` 多 +0.5 偏移校正（适配 HALCON 像素中心在 (0.5, 0.5) 而非 (0, 0) 的约定）。

**最佳实践**：用于 HALCON 内部坐标系时用 `affine_trans_pixel`；用户自定义点变换用 `affine_trans_point_2d`。

### 陷阱 7：`change_radial_distortion_image` 的输出图像尺寸变化

去除径向畸变后，输出图像可能比输入大（畸变扩展了像素范围）。需要指定 `'border_type'` 决定边界填充。

### 陷阱 8：单位混淆（米 vs 毫米 vs 像素）

3D Pose 的单位必须一致：
- HALCON 默认 3D Pose 单位是 **米**（m）
- CAD 模型常是 **毫米**（mm）
- 像素是 **像素**（px）

**最佳实践**：项目开始前明确定义单位，避免 `camera_calibration` 输入错误单位。

---

## 8. 参数调优指南

### 8.1 2D 变换

| 场景 | 推荐做法 |
|------|---------|
| 模板对齐 | `vector_angle_to_rigid` + `affine_trans_image('constant', 'false')` |
| 像素精确测量 | 用 `affine_trans_pixel` 而非 `affine_trans_point_2d` |
| 透视校正 | `vector_to_proj_hom_mat2d`（需要 ≥ 4 点对） |
| 高精度对齐 | 用 `'least_squares'` 而非 `'nearest_neighbor'` 插值 |

### 8.2 Pose 类型

| 场景 | 推荐表示 |
|------|---------|
| HALCON 内部 | `'Rp+T'`（默认，无歧义） |
| 发送给机械臂 | 通常是 `'rpy'` |
| 跨平台交换 | 四元数（无奇点、紧凑） |
| 连续插值 | 四元数 / 对偶四元数 |

### 8.3 3D 变换链

| 场景 | 推荐做法 |
|------|---------|
| 单一变换 | 直接 `affine_trans_object_model_3d` |
| 多次变换 | 先用 `hom_mat3d_compose` 累积，再 `affine_trans_object_model_3d` |
| 逆变换 | `hom_mat3d_invert` 而非手动取负 |

### 8.4 畸变矫正

| 参数 | 推荐值 | 说明 |
|------|--------|------|
| `Smoothing` | 0.5–1.0 | 矫正后图像可能需轻微平滑 |
| `border_type` | 'constant' | 黑色背景 |
| 目标畸变系数 | 0.0 | 完全去除径向畸变 |

---

## 9. 相关分类

- **Calibration**：相机标定提供 `CamPar` + 世界位姿。
- **3D Object Model**：3D 点云变换用 `affine_trans_object_model_3d`。
- **3D Matching**：返回的 Pose 在此处转换。
- **Matching**：模板匹配返回的位置用此处变换矩阵对齐。
- **Develop**：调试时用 `disp_3d_coord_system` 可视化 3D 坐标轴。

---

## 10. 学习小结

Transformations 是"**几何的基石**"——所有涉及位置的算法都依赖它：

1. **2D 仿射链**：`vector_angle_to_rigid` + `hom_mat2d_compose` + `affine_trans_*` 是 80% 项目的核心。
2. **3D Pose 链**：`create_pose` + `pose_compose` + `pose_invert` + `pose_average` 是手眼标定、机器人抓取的必备。
3. **四元数**：连续插值时唯一选择，避免欧拉角万向锁。
4. **畸变矫正**：广角相机项目必备。

**学习路径建议**：
- **第 1 周**：掌握 2D 仿射链，能完成模板匹配对齐。
- **第 2 周**：掌握 3D Pose 链 + `pose_compose`，能完成简单手眼应用。
- **第 3 周**：学四元数与对偶四元数（连续插值）。
- **第 4 周**：学畸变矫正（广角/鱼眼项目）。
- **持续**：根据具体项目深入。

**核心心法**：
1. **明确单位**：开始前定义米/毫米/像素，避免错误。
2. **矩阵方向**：始终记住"应用顺序从右到左"。
3. **Pose 类型**：HALCON 用 `'Rp+T'`，发送机械臂用 `'rpy'`，插值用四元数。
4. **手眼标定核心**：找到 `BasePose = HandEyePose * WorkPose` 即可。
5. **能不用 Pose 就不用 Pose**：2D 仿射链够用时别升级到 3D（简单 = 可靠）。

最后：**Transformations 是机器视觉的"心脏"**——掌握它就掌握了 90% 的几何问题。
