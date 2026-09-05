# Halcon 3D视觉基础技能手册

> 学习来源: `3D-Object-Model/`, `3D-Reconstruction/`, `Calibration/`
> 涵盖Task19：3D点云处理、表面匹配、高度图、立体视觉

---

## 一、3D视觉方法对比

| 方法 | 数据源 | 算子前缀 | ⭐场景 |
|---|---|---|---|
| **结构光** | 条纹投影 | `decode_structured_light_pattern` | 高精度3D重建 |
| **双目立体** | 双目相机 | `binocular_*` | 深度估计 |
| **Sheet-of-Light** ⭐ | 线激光 | `sheet_of_light_*` | ⭐工业3D扫描 |
| **3D点云** | 点云数据 | `xyz_to_object_model_3d` | 通用3D处理 |
| **Surface Matching** ⭐ | 3D模型 | `create/find_surface_model` | ⭐3D定位/分拣 |

---

## 二、3D对象模型(Object Model 3D)

### 核心算子
| 算子 | 功能 |
|---|---|
| `xyz_to_object_model_3d` ⭐ | XYZ图像→3D模型 |
| `read_object_model_3d` | 读取3D文件(PLY/STL/OBJ) |
| `write_object_model_3d` | 写入3D文件 |
| `object_model_3d_to_xyz` | 3D模型→XYZ图像 |
| `get_object_model_3d_params` | 获取3D模型参数 |
| `select_points_object_model_3d` | 筛选3D点 |
| `sample_object_model_3d` | 采样(降点) |
| `smooth_object_model_3d` | 平滑 |
| `surface_normals_object_model_3d` | 计算法线 |
| `distance_object_model_3d` | 两模型距离 |
| `intersect_plane_object_model_3d` | 平面截取 |
| `connection_object_model_3d` | 3D连通域 |
| `clear_object_model_3d` | 释放 |

---

## 三、Surface Matching 3D表面匹配 ⭐

### 完整流程
```
1. read_object_model_3d → 读取参考3D模型
2. create_surface_model → 创建表面模型
3. find_surface_model → 在场景3D数据中搜索
4. get_surface_matching_result → 获取匹配位姿
5. clear_surface_model → 释放
```

### 核心算子
```
create_surface_model(ObjectModel3D, RelSamplingDistance, GenParamName, GenParamValue, SurfaceModelID)
find_surface_model(SurfaceModelID, ObjectModel3DScene, RelSamplingDistance, KeyPointFraction,
                    MinScore, ReturnResultHandle, GenParamName, GenParamValue, Pose, Score, SurfaceMatchingResultID)
```
| 参数 | 典型值 | 说明 |
|---|---|---|
| RelSamplingDistance | 0.03 | 相对采样距离 |
| KeyPointFraction | 0.2 | 关键点比例 |
| MinScore | 0.5 | 最小匹配分数 |

---

## 四、高度图处理

| 算子 | 功能 |
|---|---|
| `gen_image_surface_first_order` | 生成一阶平面 |
| `gen_image_surface_second_order` | 生成二阶曲面 |
| `sub_image` | 高度图差分→缺陷 |
| `threshold` | 高度阈值→区域 |

### 高度图缺陷检测流程
```
1. 获取高度图(Z图像)
2. 拟合参考平面: gen_image_surface_first_order
3. 差分: sub_image(实际高度, 参考平面)
4. 阈值: threshold → 凸起/凹陷缺陷
```

---

## 五、Sheet-of-Light (线激光扫描) ⭐

### 完整流程
```
1. create_sheet_of_light_model → 创建模型
2. set_sheet_of_light_param → 设置参数(标定等)
3. 循环: measure_profile_sheet_of_light → 逐帧提取轮廓
4. get_sheet_of_light_result → 获取3D结果(高度图/点云)
5. clear_sheet_of_light_model → 释放
```

---

## 六、C# HalconDotNet 代码模板

### 模板1: 读取和处理3D点云
```csharp
HTuple objectModel3D;
// 读取PLY文件
HOperatorSet.ReadObjectModel3d("model.ply", "mm", new HTuple(), new HTuple(), out objectModel3D, out _);

// 获取点数
HTuple numPoints;
HOperatorSet.GetObjectModel3dParams(objectModel3D, "num_points", out numPoints);
Console.WriteLine($"点云包含 {numPoints.I} 个点");

// 采样降点
HTuple sampled;
HOperatorSet.SampleObjectModel3d(objectModel3D, "fast", 0.01, new HTuple(), new HTuple(), out sampled);

// 计算法线
HOperatorSet.SurfaceNormalsObjectModel3d(sampled, "mls", new HTuple(), new HTuple());

HOperatorSet.ClearObjectModel3d(objectModel3D);
HOperatorSet.ClearObjectModel3d(sampled);
```

### 模板2: 3D表面匹配 ⭐
```csharp
HTuple refModel, surfaceModel, sceneModel;
HTuple pose, score, resultID;

// 读取参考模型
HOperatorSet.ReadObjectModel3d("reference.ply", "mm", new HTuple(), new HTuple(), out refModel, out _);
// 创建表面匹配模型
HOperatorSet.CreateSurfaceModel(refModel, 0.03, new HTuple(), new HTuple(), out surfaceModel);

// 读取场景点云
HOperatorSet.ReadObjectModel3d("scene.ply", "mm", new HTuple(), new HTuple(), out sceneModel, out _);
// 搜索匹配
HOperatorSet.FindSurfaceModel(surfaceModel, sceneModel, 0.05, 0.2, 0.5, "true",
    new HTuple(), new HTuple(), out pose, out score, out resultID);

Console.WriteLine($"3D匹配分数: {score[0].D:F3}");
Console.WriteLine($"位姿: Tx={pose[0].D:F2}, Ty={pose[1].D:F2}, Tz={pose[2].D:F2}");

HOperatorSet.ClearSurfaceModel(surfaceModel);
HOperatorSet.ClearObjectModel3d(refModel);
HOperatorSet.ClearObjectModel3d(sceneModel);
```

### 模板3: XYZ图像→3D模型
```csharp
HObject xImage, yImage, zImage;
HTuple objectModel3D;

// 假设已有XYZ图像(来自结构光/深度相机)
HOperatorSet.XyzToObjectModel3d(xImage, yImage, zImage, out objectModel3D);
// 后续处理...
HOperatorSet.ClearObjectModel3d(objectModel3D);
```
