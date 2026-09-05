# HALCON 算子分类详解：3D Matching（三维匹配）

> **HALCON 版本**：26.05.0.0 Progress
> **分类代码**：3D Matching（三维匹配 / 6D 位姿估计）
> **算子规模**：约 80 个
> **一级分类入口**：`C:\Program Files\MVTec\HALCON-26.05-Progress\doc\html\reference\operators\toc_3dmatching.html`
> **学习层级**：L2–L3（进阶到高级）
> **典型应用**：机器人抓取 / Bin Picking / 6D 位姿估计 / 汽车焊接定位 / 半导体晶舟抓取

---

## 1. 概述

3D Matching 是 HALCON 中专门解决 **"找到目标物体 + 给出 6D 位姿（X/Y/Z + Rx/Ry/Rz）"** 的算子族。它和 2D Matching（`create_shape_model` 等）的本质区别在于：2D 匹配输出的是图像平面内的 2D 仿射变换，3D 匹配输出的是空间中的 6 自由度位姿（`Pose` 类型 `[Tx, Ty, Tz, Rx, Ry, Rz, Code]`），可以直接送给机器人控制器用于抓取/装配/焊接。

HALCON 26.05 的 3D Matching 分为 **7 个子分类**：

| 子分类 | 主要功能 | 典型算子数 |
|--------|---------|-----------|
| 3D Box | 长方体目标位姿估计（针对盒子/箱体） | ~5 |
| 3D Gripping Point | 6D 位姿 + 抓取点评估 | ~8 |
| Deep 3D | 基于深度学习的 3D 匹配（杂乱堆叠） | ~6 |
| Deformable Surface | 可变形表面匹配（食品/橡胶） | ~15 |
| Shape Based | 基于 3D 边缘模型的位姿估计 | ~15 |
| Surface Based | 基于点云表面的整体匹配 | ~25 |
| Misc（通用/辅助） | 文件 IO、模型查询、可视化 | ~6 |

核心算法思想：
- **Surface Based**：把 CAD 模型 (`om3d`) 建成表面模型，与场景点云做 ICP 式配准，返回 6D Pose。
- **Shape 3D**：基于物体 3D 边缘 + 相机投影，把 2D 边缘观察与 3D 模型投影边缘对齐。
- **Deformable Surface**：在 Surface Based 之上加入局部形变场（适合食品、布料、橡胶等非刚体）。
- **Deep 3D**：用深度神经网络直接从 RGB-D 图像回归 6D Pose（杂乱堆叠场景最优）。
- **3D Box**：专门针对立方体/长方体容器（如周转箱、料盒）。

---

## 2. 应用场景

### 场景 1：汽车车身焊接引导
- 6 个工件（侧围、前后盖、顶盖）由机器人搬运至焊接工位。
- 相机安装于机械臂末端（eye-in-hand）或固定在工作台（eye-to-hand）。
- 通过 3D 匹配定位工件的 6D 位姿，修正机器人路径。
- 核心算子：`create_surface_model` + `find_surface_model` + `refine_surface_model_pose` + `calibrate_hand_eye`。

### 场景 2：3C 电子件上下料
- 散热片、屏蔽罩、Type-C 端子等小型金属件散乱堆叠在料盘。
- 视觉系统需要找到可抓取的工件并给出抓取点（吸盘/夹爪位置）。
- 使用 Surface-Based 匹配 + Gripping Point Evaluation。
- 核心算子：`find_shape_model_3d` + `find_shape_model_3d_user`。

### 场景 3：半导体晶舟（Wafer Cassette）抓取
- 25 槽晶舟，每槽 1–25 片晶圆。
- 需要精确识别每片晶圆的位置和姿态（容忍 < 0.1 mm）。
- 配合洁净环境、防静电与避光。
- 核心算子：`create_deformable_surface_model`（薄片晶圆的微弯曲补偿）+ `find_deformable_surface_model`。

### 场景 4：物流行业箱子/袋装抓取
- 仓库分拣机器人，识别纸箱、麻袋、周转箱的 6D 位姿。
- 包裹形状多样、堆叠杂乱。
- 核心算子：`find_box_3d`（长方体识别）+ `find_surface_model`（混合）。

### 场景 5：食品分拣（鸡翅、生鲜、糕点）
- 物体非刚性、易变形，形状不规则。
- 传统刚性匹配精度差。
- 核心算子：`create_deformable_surface_model` + `add_deformable_surface_model_sample`。

---

## 3. 子分类详解

### 3.1 3D Box（立方体匹配）
HALCON 26 引入的 `find_box_3d` 专门识别长方体（纸箱、料盒）：`find_box_3d(Image, BoxDimension, ScoreMethod, MinScore, ...)`，免去对每种尺寸建模。
- 配套：`set_shape_model_3d_metric` / `trans_pose_shape_model_3d`。

### 3.2 3D Gripping Point（抓取点评估）
评估位姿的"可抓取性"（夹爪边缘、吸盘平面）。
- `find_shape_model_3d` / `project_shape_model_3d` / `get_shape_model_3d_*`。

### 3.3 Deep 3D（深度学习 3D 匹配）
针对杂乱堆叠（bin picking）训练的深度网络：`create_deep_matching_3d` + `apply_deep_matching_3d` + `prepare_deep_matching_3d` + `read/write_deep_matching_3d`。
- HALCON 自带预训练权重：`universal_bin_picking.hdl`。

### 3.4 Deformable Surface（可变形表面）
在 Surface-Based 之上允许局部变形（食品、橡胶、布料）。
- `create_deformable_surface_model` / `add_deformable_surface_model_sample` / `prepare_deformable_surface_model`
- `find_deformable_surface_model` / `refine_deformable_surface_model`
- `get_deformable_surface_model_param` / `get_deformable_surface_matching_result`。

### 3.5 Shape Based（基于 3D 边缘）
用 3D 模型边缘与 2D 边缘对齐（适合简单几何、边缘清晰场景）。
- `create_shape_model_3d(..., CamParam, ...)` / `find_shape_model_3d` / `project_shape_model_3d` / `get_shape_model_3d_*`。

### 3.6 Surface Based（基于表面 / ICP 整体匹配）
**最核心的子分类**：把 CAD 或扫描点云建成表面模型，场景点云与之配准。
- `create_surface_model` / `set_surface_model_param`
- `find_surface_model`（粗匹配） / `find_surface_model_image`（图像型）
- `refine_surface_model_pose`（精炼 ICP） / `get_surface_model_param` / `get_surface_matching_result`。

### 3.7 Misc（辅助算子）
- `read/write_surface_model`：模型存档。
- `clear_surface_model` / `clear_shape_model_3d`：释放模型。
- `deserialize_surface_model` / `serialize_surface_model`：跨进程。

---

## 4. 核心算子详解

### 4.1 `create_surface_model` — 表面模型创建

```
create_surface_model(ObjectModel3D : : RelSamplingDistance, GenParamName, GenParamValue : SurfaceModelID)
```

**功能**：从 3D 对象模型（CAD 或点云）创建表面模型，是后续 `find_surface_model` 的基础。

**关键参数**：
- `RelSamplingDistance`：相对采样距离（0.0–1.0），决定采样点密度。**越小越精细越慢**。典型值 0.03–0.1。
- `'model_normal_computation_mode'`：法向量计算方式（`'auto'` / `'accurate'` / `'fast'`）。
- `'feat_step_size'` / `'feat_angle_step'`：特征提取步长。

**返回值**：`SurfaceModelID` 句柄。

### 4.2 `find_surface_model` — 表面匹配核心

```
find_surface_model(SurfaceModelID, ObjectModel3DScene, RelSamplingDistance, KeyPointFraction, MinScore, Pose, Score, SurfaceMatchingResultID)
```

**功能**：在场景点云中搜索与模型最匹配的位姿。

**关键参数**：
- `RelSamplingDistance`：场景点云下采样距离（通常与模型一致）。
- `KeyPointFraction`：0.0–1.0 关键点比例，影响速度和精度（典型 0.5）。
- `MinScore`：最小得分（0–1），过滤低质量匹配（典型 0.3–0.5）。

**返回值**：
- `Pose`：6D 位姿数组（多实例）。
- `Score`：每个匹配的得分。
- `SurfaceMatchingResultID`：详细结果（含 inliers、法向对齐误差等）。

### 4.3 `refine_surface_model_pose` — 位姿精炼

```
refine_surface_model_pose(SurfaceModelID, ObjectModel3DScene, InitialPose, MinScore, GenParamName, GenParamValue, RefinedPose, Score, SurfaceMatchingResultID)
```

**功能**：在初始位姿基础上做 ICP 精炼，提升精度（典型从 ±1° 提升到 ±0.1°）。

### 4.4 `create_shape_model_3d` — 3D 形状模型

```
create_shape_model_3d(Contours, CamParam, RefPose, ..., Reduction, MinContrast, GenParamName, GenParamValue, ShapeModel3DID)
```

**功能**：从 3D 轮廓 + 相机参数构造 3D 形状模型。**注意：必须先有 `CamParam`（已标定）**。

### 4.5 `find_shape_model_3d` — 3D 形状匹配

```
find_shape_model_3d(Image, ShapeModel3DID, MinScore, Greediness, NumMatches, Pose, Score, ...)
```

**功能**：在图像中找 3D 形状模型的位姿。

### 4.6 `calibrate_hand_eye` — 手眼标定

```
calibrate_hand_eye(CameraParam, CalibDataID, ToolTCP, ToolNo, HandEyePose, EyeInHandPose)
```

**功能**：计算相机与机器人末端（TCP）的相对位姿，**任何机器人视觉项目必经环节**。

### 4.7 `find_deformable_surface_model` — 变形表面匹配

```
find_deformable_surface_model(DSurfaceModel, ObjectModel3DScene, RelSamplingDistance, MinScore, Pose, Score, DSurfaceMatchingResultID)
```

**功能**：在允许局部变形的情况下匹配非刚性目标（食品、布料、皮革）。

### 4.8 `apply_deep_matching_3d` — 深度 3D 匹配推理

```
apply_deep_matching_3d(DLMHandle, Images, Score, Pose, Overlap, Time)
```

**功能**：用深度网络从 RGB-D 图像直接推断 6D Pose，是 bin picking 最新方案。

---

## 5. HDevelop 示例代码

### 示例 1：完整的 6D 位姿估计流水线

```hdevelop
* 3D Matching - 6D Pose Estimation Pipeline
* 适用：从 RGB-D 相机读取场景，识别 CAD 模型的目标

* === 1. 加载 CAD 模型 ===
read_object_model_3d('engine_block.om3', 'mm', [], [], ObjectModel3D, Status)

* 简化 + 计算法向量（加速后续匹配）
simplify_object_model_3d(ObjectModel3D, 'preserve_general', 0.5, [], [], SimplifiedModel)
surface_normals_object_model_3d(SimplifiedModel, 'mls', 'mls_force_outward', 'mls_kNN', 30, NormalModel)

* === 2. 创建表面模型 ===
create_surface_model(NormalModel, 0.05, [], [], SurfaceModelID)

* === 3. 读场景（RGB-D 相机 / 扫描仪）===
xyz_to_object_model_3d(X, Y, Z, SceneModel)

* 下采样（场景通常比模型更密）
simplify_object_model_3d(SceneModel, 'preserve_general', 1.0, [], [], SceneModelReduced)

* === 4. 匹配 ===
find_surface_model(SurfaceModelID, SceneModelReduced, 0.03, 0.5, 0.3, Pose, Score, SurfaceMatchingResultID)

* === 5. 精炼位姿 ===
refine_surface_model_pose(SurfaceModelID, SceneModelReduced, Pose, 0.5, [], [], RefinedPose, RefinedScore, SurfaceMatchingResultID2)

* === 6. 可视化与机器人指令 ===
pose_to_hom_mat3d(RefinedPose, HomMat3D)
affine_trans_object_model_3d(NormalModel, HomMat3D, TransformedModel)

* 在场景窗口显示对齐结果
dev_open_window(0, 0, 512, 512, 'black', WindowHandle)
disp_object_model_3d(WindowHandle, [SceneModelReduced, TransformedModel], [], [], ['color_0','color_1'], ['gray','green'], [], [], [], PoseOut)

* === 7. 清理 ===
clear_surface_model(SurfaceModelID)
```

### 示例 2：手眼标定完整流程

```hdevelop
* Hand-Eye Calibration
* Eye-in-Hand: 相机装在机械臂末端

dev_close_window()
dev_open_window(0, 0, 800, 600, 'black', WindowHandle)

* === 1. 创建标定数据模型 ===
create_calib_data('calibration_object', 1, 1, CalibDataID)
set_calib_data_calib_object(CalibDataID, 0, 'caltab_30mm.descr')

* === 2. 加载相机参数（已有内参） ===
read_cam_par('camera_parameters.dat', CameraParam)

* === 3. 设置初始姿态与工具 ===
set_calib_data(CalibDataID, 'camera', 0, 'params', CameraParam)
set_calib_data(CalibDataID, 'camera', 0, 'init_pose', [0,0,500,0,0,0,0])
set_calib_data(CalibDataID, 'calib_obj', 0, 'init_pose', [0,0,0,0,0,0,0])

* 假设机械手工具中心点 (TCP) 已知
ToolTCP := [0, 0, 50, 0, 0, 0, 0]

* === 4. 采集标定图像（循环）===
for I := 1 to 15 by 1
    * 移动机械臂到新位姿
    RobotPose[I] := [I*30.0, 0, 500, 0, 0, 30*I*deg_to_rad(1)]
    * 抓取图像
    grab_image(Image, AcqHandle)
    * 找标定板
    find_caltab(Image, CaltabRegion, 'caltab_30mm.descr', 3, 0, 5)
    find_marks_and_pose(Image, CaltabRegion, 'caltab_30mm.descr', CameraParam, 128, 10, 20, CalibCoord, RCoord, CCoord, PoseCalib)
    * 添加到标定数据
    set_calib_data_observ_points(CalibDataID, 0, 0, I, RCoord, CCoord, RobotPose[I], 'tool')
    dev_display(Image)
    dev_display(CaltabRegion)
endfor

* === 5. 手眼标定求解 ===
calibrate_hand_eye(CameraParam, CalibDataID, ToolTCP, 15, HandEyePose, EyeInHandPose)

* === 6. 验证 ===
write_pose(HandEyePose, 'hand_eye_pose.dat')
disp_message(WindowHandle, 'Hand-Eye Calibration Done', 'window', 12, 12, 'black', 'true')
disp_message(WindowHandle, 'Hand-Eye Pose: ' + HandEyePose$'.3f', 'window', 40, 12, 'white', 'false')
```

### 示例 3：杂乱堆叠 Bin Picking（深度 3D 匹配）

```hdevelop
* Bin Picking with Deep 3D Matching
* 适用：散乱工件抓取

* === 1. 加载深度 3D 模型（HALCON 自带预训练权重）===
read_deep_matching_3d('universal_bin_picking.hdl', DLMHandle)

* === 2. 读相机（RGB-D） ===
open_framegrabber('GigEVision2', 1, 1, 0, 0, 0, 0, 'default', -1, 'default', 'default', 'default', 'default', CameraType, 'default', 'default', 0, 0, AcqHandle)
grab_image_async(ImageRGB, AcqHandle, -1)
grab_image_async(ImageDepth, AcqHandle, -1)
close_framegrabber(AcqHandle)

* === 3. 转 3D 场景（需相机参数） ===
xyz_to_object_model_3d(X, Y, Z, Scene3D)

* === 4. 准备输入并推理 ===
prepare_deep_matching_3d(DLMHandle, [ImageRGB, ImageDepth, Scene3D])
apply_deep_matching_3d(DLMHandle, [ImageRGB, ImageDepth, Scene3D], Score, Pose, Overlap, InferenceTime)

* === 5. 选最优位姿（取分数最高）===
MaxIdx := sort_index(-Score)[0]
BestPose := Pose[MaxIdx]

* === 6. 转机器人坐标（手眼标定结果） ===
pose_compose(HandEyePose, BestPose, RobotTargetPose)

* === 7. 输出给机器人控制器 ===
write_pose(RobotTargetPose, 'tcp_target_pose.dat')
```

---

## 6. 典型工业流水线

### 流水线 A：发动机缸体上料

```
工位触发 → RGB-D 采集 → xyz_to_object_model_3d 转点云 → simplify + surface_normals
→ create_surface_model（CAD 离线）→ find_surface_model 粗匹配（MinScore = 0.4）
→ refine_surface_model_pose ICP 精炼 → pose_compose(HandEyePose, Pose, RobotPose)
→ send socket / PROFINET → 机器人控制器 → 抓取 → 下一循环
```

### 流水线 B：晶圆盒 (FOUP) 抓取

```
读 FOUP → 找 25 槽位 → 每槽：
    create_deformable_surface_model（考虑晶圆微弯曲 0.5 mm）
    → find_deformable_surface_model → refine → 真空吸盘坐标
```

### 流水线 C：基于深度学习的 Bin Picking

```
训练：仿真 + 真实标注 → create_deep_matching_3d → 训练 → 导出 .hdl
推理：实时 RGB-D → prepare_deep_matching_3d → apply_deep_matching_3d（GPU 50–200 ms）
→ 选最优 → 机器人抓取
```

---

## 7. 常见陷阱与最佳实践

### 陷阱 1：模型单位不一致
CAD 模型是 mm，相机点云是 m → 匹配彻底失败。
- **最佳实践**：**统一单位**（用 `gen_box_object_model_3d` 时明确 LengthUnit = `'m'` / `'mm'` / `'km'`）；加载 CAD 时用 `read_object_model_3d(..., Scale, 'mm', ...)`。

### 陷阱 2：法向量方向错乱导致 ICP 失效
点云没有良好法向量 → 表面匹配 `Score` 始终 < 0.3。
- **最佳实践**：
  - 先 `surface_normals_object_model_3d(Model, 'mls', 'mls_force_outward', ...)`。
  - 对于激光扫描点云，用 `'estimate_local_planar'`；CAD 网格用 `'triangulation'`。

### 陷阱 3：场景点云太密导致速度爆炸
百万级点直接送 `find_surface_model` → 几秒/次 → 产线超时。
- **最佳实践**：`simplify_object_model_3d(SceneModel, 'preserve_general', 1.0, ...)`，密度匹配模型。

### 陷阱 4：手眼标定精度不足
手眼标定误差 > 1 mm → 抓取成功率 50%。
- **最佳实践**：
  - 工作距离 ≥ 30 cm。
  - 至少 12 张标定图（HALCON 官方推荐）。
  - 标定板覆盖视野四角 + 不同深度。
  - 用 `calibrate_hand_eye` 后看误差统计：`get_calib_data('calib_obj_pose')`。

### 陷阱 5：MinScore 设过低导致误匹配
`MinScore = 0.1` → 把相似工件当成目标。
- **最佳实践**：先在 50 张图上调 MinScore，找到 Precision = 95% 处的阈值。

### 陷阱 6：姿态精炼初值不准
粗匹配 Pose 误差 > 5° → ICP refine 收敛到局部最优。
- **最佳实践**：先用 `find_surface_model` 粗匹配（KeyPointFraction = 0.5），再用 `refine_surface_model_pose` 精炼（步长从粗到细）。

### 陷阱 7：模型简化过度丢失关键特征
`simplify_object_model_3d(Model, 'preserve_normal', 0.3, ...)` → 小特征丢失 → 匹配率下降。
- **最佳实践**：用 `'preserve_general'` + RelSamplingDistance（0.03–0.1）。

### 陷阱 8：多目标场景未指定数量
`find_surface_model` 返回所有候选 → 解析混乱。
- **最佳实践**：用 `'num_matches'` 参数限制返回数。

---

## 8. 参数调优指南

### Surface-Based 关键参数

| 参数 | 含义 | 默认 | 调优 |
|------|------|------|------|
| `RelSamplingDistance` | 模型采样距离 | 0.05 | 模型精细→小值；速度→大值（0.02–0.2） |
| `KeyPointFraction` | 关键点比例 | 0.5 | 速度→0.2；鲁棒→0.8 |
| `MinScore` | 最小得分 | 0.5 | 严苛场景→0.3；标准→0.5 |

### 其他算法关键参数

| 算子 | 关键参数 | 调优 |
|------|---------|------|
| `find_shape_model_3d` | `MinContrast`, `Greediness`, `NumMatches` | MinContrast 10–40；Greediness 0.7（默认 0.9）→ 速度↑；多目标设 NumMatches |
| `find_deformable_surface_model` | `DefMode`, `MinClusterRadius`, `DeformationLimit` | `'global'` 缩放；`'local'` 局部；食品 5–15 mm |
| `apply_deep_matching_3d` | `min_score`, `overlap`, `device` | score 0.3；overlap 0.5；GPU 推荐 |

### 手眼标定参数

- 标定图像数：≥ 12 张（HALCON 26 推荐 15+）。
- 工具编号（ToolNo）：机械臂工具坐标系编号（多数 = 1）。
- 工作距离：相机到标定板 ≥ 30 cm。

---

## 9. 相关分类

| 关联分类 | 协作方式 |
|----------|----------|
| **3D Object Model** | 所有 3D Matching 的输入都是 `ObjectModel3D`（点云 / 网格），3D Matching 本质是 3D Object Model 的"匹配功能" |
| **Calibration** | 必须先做 `camera_calibration` / `calibrate_hand_eye` 才能用于 3D Matching |
| **3D Reconstruction** | 双目/光片等重建的点云是 3D Matching 的常见输入 |
| **Deep Learning** | Deep 3D Matching 本质就是深度学习的一个分支 |
| **Transformations** | Pose 转换（`pose_to_hom_mat3d`、`pose_compose`、`convert_pose_type`）是 3D Matching 输出给机器人的桥梁 |
| **Graphics → 3D Scene** | `add_scene_3d_instance` / `render_scene_3d` 可视化匹配结果 |

---

## 10. 学习小结

3D Matching 是 HALCON 的"工业 AI"核心 —— 它把视觉系统从"看见"升级到"理解并决策"。

### 学习路线建议

1. **第 1 周**：理解 Pose 表示（`create_pose` / `pose_compose` / `pose_to_hom_mat3d`），跑通 `find_surface_model` 单实例 demo。
2. **第 2 周**：完整做一次单目 + 手眼标定（用 HALCON 自带 `caltab_30mm.descr`），理解 `calibrate_hand_eye`。
3. **第 3 周**：学 `find_shape_model_3d`（基于边缘的 3D 匹配），与 `find_surface_model` 对比。
4. **第 4 周**：引入可变形表面匹配（食品/橡胶场景）。
5. **第 5–6 周**：深度 3D 匹配（Deep Matching 3D），准备 GPU 推理环境。

### 核心要点回顾

1. **算法选择 = 精度需求 × 速度需求 × 训练数据量**：
   - **Surface-Based**（CAD + ICP）：精度高、需 CAD 模型、刚性件。
   - **Shape 3D**：精度中、边缘可见、简单几何。
   - **Deformable Surface**：非刚性（食品/布料）。
   - **Deep 3D**：杂乱堆叠，需 GPU 训练数据。

2. **任何 3D Matching 项目必经两步**：① `camera_calibration`（相机内参）；② `calibrate_hand_eye`（机器人-相机关系）。跳过这步就是"盲人摸象"。

3. **精度瓶颈不在匹配，而在标定**：1 像素标定误差 = 1 mm 世界误差（焦距 50 mm）。投入时间做标定质量评估（`get_calib_data` / `calibrate_cameras` 的 error 统计）远比优化匹配算法回报高。

4. **单位、法向量、采样距离** 三大"看不见"的坑：CAD 单位、点云单位必须统一；法向量方向必须正确；模型与场景采样密度必须匹配。

5. **6D Pose 是"接口"**：拿到 Pose 后必须做 `pose_compose(HandEyePose, ObjectPose, RobotTCP)` 转机器人坐标，再通过 Socket / PROFINET / Modbus 送给控制器。

### 推荐示例程序

HALCON 自带 `%HALCONEXAMPLES%\hdevelop\3DMatching\` 目录下有 20+ 个完整 demo，必看：
- `surface_matching.hdev`（表面匹配基础）
- `surface_matching_with_3d_scenes.hdev`（真实 3D 场景）
- `deformable_surface_matching.hdev`（变形匹配）
- `shape_matching_3d.hdev`（3D 形状匹配）
- `deep_matching_3d_*.hdev`（深度 3D 匹配）

掌握 3D Matching 是从"视觉工程师"到"机器人视觉工程师"的关键一步。结合 Calibration、3D Object Model 与 Transformations 三类算子，能完成 90% 工业机器人视觉项目。