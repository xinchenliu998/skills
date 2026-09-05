---
name: halcon-3d-vision
description: >-
  HALCON 3D vision: 3D object models (read_object_model_3d, xyz_to_object_model_3d,
  prepare/triangulate/sample/register/union/fuse_object_model_3d), 3D matching &
  pose estimation (create_shape_model_3d / find_shape_model_3d,
  create_surface_model / find_surface_model, deformable surface matching,
  fit_primitives_object_model_3d, segment_object_model_3d, get_circle_pose),
  stereo vision (calibration, gen_binocular_rectification_map, binocular_disparity,
  reconstruct_surface_stereo), laser triangulation / Sheet-of-Light
  (create_sheet_of_light_model, measure_profile_sheet_of_light, calibrate),
  depth-from-focus, and 3D transforms (hom_mat3d, pose). Use this skill whenever a
  HALCON/HDevelop task works with point clouds, 3D reconstruction, 3D pose
  estimation (6D), surface-based matching, stereo or laser line scanning, or CAD
  model matching. Trigger on read_object_model_3d, xyz_to_object_model_3d,
  create_surface_model / find_surface_model, create_shape_model_3d,
  binocular_disparity, reconstruct_surface_stereo,
  create_sheet_of_light_model, depth_from_focus, or when the user needs 6D pose /
  bin picking / 3D measurement.
---

# HALCON 3D 视觉

> 定位：3D 点云、物体模型、3D 匹配与位姿、立体/结构光/DFF 重建、3D 变换。
> 编写规范见 `../_authoring/`（conventions.md 为精简总结；完整规范在 halcon_skill.md；脚本格式/CLI 见同名 *_reference.md）。

---

## 一、一句话选型

| 需求 | 首选 | 说明 |
|---|---|---|
| 表示 3D 点/网格 | `read_object_model_3d` / `xyz_to_object_model_3d` / `gen_box_object_model_3d` | 统一数据对象 |
| 无 3D 场景、硬几何边物体定位 | `create_shape_model_3d` + `find_shape_model_3d` | CAD → 2D 投影视图模型 |
| 点云场景定位 | `create_surface_model` + `find_surface_model` | 点+法线，6D 位姿 |
| 非刚性物体 | `create_deformable_surface_model` | 可变形抓取 |
| 拟合球/圆柱/平面 | `segment_object_model_3d` + `fit_primitives_object_model_3d` | 几何基元 |
| 像素/区域→世界度量 | `image_to_world_plane`/`image_points_to_world_plane` | 见 `halcon-calibration` |
| 双目重建 | `gen_binocular_rectification_map` + `binocular_disparity` + `disparity_image_to_xyz` | 视差→3D |
| 多视重建 | `create_stereo_model` + `reconstruct_surface_stereo` | 全向表面 |
| 激光线扫 | `create_sheet_of_light_model` + `measure_profile_sheet_of_light` | 剖面高度 |
| 焦深重建 | `depth_from_focus` | 显微/小物体，精度高 |
| 位姿/矩阵变换 | `pose_to_hom_mat3d`/`hom_mat3d_*`/`set_origin_pose` | 刚体链 |

---

## 二、3D 物体模型

- 获取：`read_object_model_3d('model.dxf',0.0001,[],[],OM3,Status)`（DXF/STL/OFF/PLY/OM3）；`gen_object_model_3d_from_points`；基元 `gen_box/sphere/cylinder/plane_object_model_3d`；XYZ 图 `xyz_to_object_model_3d(X,Y,Z,OM3)`；立体/光切/DFF 重建结果。
- 查询：`get_object_model_3d_params(OM3,'point_coord_x',...)`，常用 attr `'center'`/`'bounding_box1'`/`'has_primitive_data'`/`'primitive_type'`。
- 修改/点集：`set_object_model_3d_attrib(_mod)`、`surface_normals_object_model_3d`、`triangulate_object_model_3d('greedy'/'implicit')`、`sample_object_model_3d`（均匀点密度）、`smooth_object_model_3d('mls'/'mls_force_inwards')`、`segment_object_model_3d`、`connection_object_model_3d('distance_3d',0.01,..)`、`select_points_object_model_3d`。
- 合并/配准：`union/fuse_object_model_3d`、`register_object_model_3d_pair`/`_global`。
- 特征：`area/distance/moments/volume_object_model_3d`、`smallest_bounding_box_object_model_3d`、`max_diameter_object_model_3d`。
- 准备：`prepare_object_model_3d(OM3,'shape_based_matching_3d','true',[],[])`（或 `'segmentation'`）加速复用。
- 可视化：`disp_object_model_3d`/`visualize_object_model_3d`/`render_object_model_3d`/`project_object_model_3d`。
- **坑**：`union_object_model_3d` 只保留所有输入都含的属性；融合表面用 `fuse_object_model_3d`；2D mapping 能显著提速。

---

## 三、3D 位姿估计（Pose Estimation）

### 从点估计（mono 3D）
`vector_to_pose(ControlX,Y,Z, Row,Col, CamParam, 'iterative','error', Pose, Errors)`；要求 ≥3 个已知 3D 控制点及其像素坐标（顺序一一对应，用 `'iterative'`/`'error'`）。

### Shape-Based 3D Matching（CAD→2D 投影）
```hdevelop
read_object_model_3d ('tile_spacer.dxf', 0.0001, [], [], OM3, Status)
prepare_object_model_3d (OM3, 'shape_based_matching_3d', 'true', [], [])
create_shape_model_3d (OM3, CamParam, RefRotX,Y,Z, 'gba', PhiMin,PhiMax,ThetaMin,ThetaMax,
                       DistMin,DistMax, RelSamplingDistance, RelSamplingAngle, NumLevels,
                       'min_face_angle', MinFaceAngle, ShapeModel3DID)
find_shape_model_3d (Image, ShapeModel3DID, MinScore, NumMatches, MaxOverlap,
                     ['num_matches','max_overlap','border_model'], [...,0.75,'true'],
                     Pose, CovPose, Score)
```
- 位姿范围：虚拟相机绕物体包围盒中心的球面；`RefRotX/Y/Z` 使参考视图居中；`MinFaceAngle` 过滤不可见边（太小含不可见边，太大丢可见边）；`NumLevels` 金字塔。
- `find_shape_model_3d`：`MinScore`(越大快但漏检)、`Greediness`、`MinContrast`、`border_model`、`pose_refinement`(`'none'`/`'least_squares_high'`)。
- **坑**：模型生成时间随面数**平方**增长——CAD 过复杂极慢，去无关细节或用更大 `'lowest_model_level'`/更高 `'min_face_angle'`；退化视图（正方体正对面/侧视）大量误匹配，限制位姿范围；对称物体把 φ 范围缩为单值大幅加速；降分辨率须同步改 Sx,Sy,Cx,Cy,W/H。
- 复用：`write_shape_model_3d`/`read_shape_model_3d`(.sm3)；检查 `get_shape_model_3d_params`/`get_shape_model_3d_contours`。

### Surface-Based 3D Matching ★
```hdevelop
create_surface_model (ObjectModel3DModel, RelSamplingDistance, [], [], SFM)
find_surface_model (SFM, SceneOM3D, RelSamplingDistance, KeyPointFraction, MinScore,
                    'false', 'num_matches', Integer, Pose, Score, SurfaceMatchingResultID)
```
- **数据要求**：模型与场景是 3D object model（点+法线；无法线自动补但朝向有歧义）。**必须 XYZ-mapping 与法线**；场景点云先去背景（blob 分析/Z 阈值/参考场景相减）。
- **三阶段机制**：①近似匹配（需物体上 ≥150 点）②稀疏位姿精炼（大杂波关 `'sparse_pose_refinement'`）③稠密位姿精炼（`'pose_ref_sub_sampling'`）。
- 关键参数：`RelSamplingDistance`（小→慢稳；细长物体取最小延伸的 1/4 内）、`KeyPointFraction`、`'model_invert_normals'`（模型与场景法线必须同向）、`'max_overlap_dist_rel/_abs'`（细长物体须设最小延伸量级）、`'train_self_similar_poses'`（近对称防误检）、`num_matches`、`MinScore`。
- **Edge-Supported 变体**：表面+3D 边 / +2D 边（追求速度或抑制边副作用）；`find_surface_model_image` 额外用 2D 强度图。
- **最高频失败原因**：法线朝向不一致、重复无效点 (0,0,0)、模型原点距场景过远（>100 倍直径丢精度）、缩放不正确。用 `debug_find_surface_model` 诊断。

### 基元拟合 / 圆 / 矩形位姿
- `segment_object_model_3d` + `fit_primitives_object_model_3d(OM3, ['primitive_type','fitting_algorithm','output_xyz_mapping'], ['cylinder','least_squares_huber','true'], OM3Out)`；查 `get_object_model_3d_params(...,'primitive_parameter',...)`。
- 圆：`get_circle_pose`；矩形：`get_rectangle_pose`。

---

## 四、立体视觉（Stereo）

### 双目
```hdevelop
* 校正
gen_binocular_rectification_map (MapL,MapR, CamParamL,CamParamR, cLPcR, SubSampling,
                                 'viewing_direction', 'bilinear', RectCamParL,RectCamParR,
                                 CamPoseRectL,CamPoseRectR, RectLPosRectR)
map_image (ImageL, MapL, RectL); map_image (ImageR, MapR, RectR)
* 视差/距离（'ncc'/'sad'/'ssd'）
binocular_disparity (RectL, RectR, Disparity, Score, 'ncc', MaskWidth, MaskHeight,
                     TextureThresh, MinDisparity, MaxDisparity, NumLevels,
                     ScoreThresh, 'left_right_check', 'interpolation')
binocular_distance (...)
* 3D 坐标
disparity_image_to_xyz (DisparityImage, X, Y, Z, RectCamParL, RectCamParR, RectLPosRectR)
```
- 三种立体匹配：`binocular_disparity`(correlation，快、需纹理)、`_mg`(multigrid，无纹理也回视差、边缘更准)、`_ms`(multi-scanline，留不连续、内存大)。
- 分辨率：Δz = z²/(f·b)·Δd；高分辨率→长大基线/长焦距/贴近物体。
- **标定**：`create_calib_data('calibration_object',2,1,..)`+`find_calib_object`×2+`calibrate_cameras`；标定板须在相邻相机重叠区可见；`get_calib_data(...,'camera',idx,'params'/'pose')`。
- **坑**：无论纹理丢区域用 multigrid；重复图案对齐校正图行方向；校正后共轭点行坐标应一致。

### 多视
`create_stereo_model(CameraSetupModelID, 'surface_pairwise'/'surface_fusion'/'points_3d', [], [], StereoModelID)` + `set_stereo_model_image_pairs` + `set_stereo_model_param` (rectif/bounding_box/binocular_filter/point_meshing) + `reconstruct_surface_stereo(Images, StereoModelID, OM3)`。

---

## 五、激光三角测量 / Sheet of Light（光切法）

```hdevelop
create_sheet_of_light_model (ProfileRegion, ['min_gray','num_profiles','ambiguity_solving'], [70,290,'first'], SILModel)
set_sheet_of_light_param (..., 'calibration', 'xyz'); set_sheet_of_light_param (..., 'camera_parameter', CamParam)
set_sheet_of_light_param (..., 'camera_pose', CamPose); set_sheet_of_light_param (..., 'lightplane_pose', LightplanePose)
set_sheet_of_light_param (..., 'movement_pose', MovementPose)
measure_profile_sheet_of_light (ProfileImage, SILModel, [])
get_sheet_of_light_result (X,...,'x'); (Y,'y'); (Z,'z'); (Disparity,...'disparity'); (Score,...'score')
get_sheet_of_light_result_object_model_3d (SILModel, OM3)
```
- **标定**：标准标定板（相机标定 + 光平面取向 `compute_3d_coordinates_of_light_line`+`fit_3d_plane_xyz`，至少 3 对应点含 1 个 z 显著不同）或**特殊 3D 标定物**（`calibrate_sheet_of_light`，RMS 距离）。
- **测量/判定**：三角测量角 α 推荐 30–60°（太小精度降、太大遮挡/阴影多）；`'num_profiles'` 默认 512、ROI 宽=物体宽+余量、高=最大预期视差。
- **Score Image**：`'score_type'=>'width'`，阈值剔除伪影（弯曲/大斜度面光带变宽）；speckle 噪声用更高光圈或低 speckle 投影器（常为精度瓶颈）。
- **坑**：视差图每行存一个剖面的亚像元值，与立体不同；未标定测量只出视差+score，后标定用 `apply_sheet_of_light_calibration`。

---

## 六、深度聚焦（DFF）
```hdevelop
read_image (Img, 'dff/focus_pcb_'+Seq$'02'); channels_to_image (Img, Image)
depth_from_focus (Image, Depth, Confidence, 'bandpass', 'next_maximum')
select_grayvalues_from_channels (Image, Depth, SharpenedImage)
```
- **需远心镜头**或显微光学（保证不同聚焦距离下相同视场/像素可比）；小景深→高精度；移动须**平行于光轴**；约 5 张图模糊→清晰→模糊；受噪声最多 ~150 张，最低建议 10。
- 高度值是**图像索引**（未标定），需知相邻图 z 间距。
- 标定像差：用平面纹理参考面做一次 DFF 测"表面弯曲"，抛物面近似做参考，后续 `sub_image` 减掉。

---

## 七、常见陷阱与最佳实践
1. 法线朝向（surface-based 需模型与场景大致同向，edge 需都朝内）——最高频失败原因。
2. 模型原点距场景过远丢精度；尺度（`read_object_model_3d` 的单位）错则相似度/分数异常。
3. CAD 过复杂致 shape-based-3d 建模型平方级耗时。
4. 重建用 `'point_meshing'` 才能做 3D primitives fitting。
5. 去背景是 surface-based 匹配前置（普通/倾斜/任意形状三种方式）。

---

## 八、引用
- 中文算子总览：`references/ops_12_3DMatching.md`、`ops_13_3DObjectModel.md`、`ops_14_3DReconstruction.md`
- 逐算子签名/默认值：`references/ref_OPERATOR_REFERENCE.md`（3D_Matching / 3D_Object_Model / 3D_Reconstruction 章）。
- 关联：`halcon-calibration`（相机/手眼标定、位姿）、`halcon-measuring-metrology`（3D 尺寸）、`halcon-matching`（2D→3D）、`halcon-vision-workflow`（机器视觉抓取）。


---

## 用例参考（example_*.md）

本 skill 目录下 `references/` 含以下项目里抽出的真实用例（按主题归档，可直接借鉴实现思路/算子组合）：

- `references/example_3d_vision.md`
