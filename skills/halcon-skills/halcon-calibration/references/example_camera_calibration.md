# Halcon 相机标定技能手册

> 学习来源: `Calibration/`, `3D-Object-Model/`
> 涵盖Task14：相机内参标定、手眼标定、像素→世界坐标转换

---

## 一、标定方法对比

| 方法 | 算子 | 需要 | 精度 | ⭐场景 |
|---|---|---|---|---|
| **标定板标定** ⭐ | `calibrate_cameras` | 标定板图像 | 高 | ⭐精确测量 |
| **手眼标定** | `calibrate_hand_eye` | 机器人位姿+标定板 | 高 | 机器人引导 |
| **简易标定** | `cam_par_*` | 已知内参 | 中 | 快速转换 |

---

## 二、标定核心流程 ⭐

```
1. 准备标定板（caltab）
2. 采集多角度标定图像(10-20张)
3. find_caltab → 找标定板区域
4. find_marks_and_pose → 找标记点+估计位姿
5. calibrate_cameras → 执行标定(输出内参+外参)
6. 像素→世界坐标转换
```

### 核心算子

#### create_calib_data — 创建标定数据
```
create_calib_data(CalibSetup, NumCameras, NumCalibObjects, CalibDataID)
```
- CalibSetup: `'calibration_object'`

#### set_calib_data_cam_param — 设置初始内参
```
set_calib_data_cam_param(CalibDataID, CamIdx, CamType, StartCamParam)
```
- CamType: `'area_scan_division'` / `'area_scan_polynomial'` / `'area_scan_telecentric_division'`

#### set_calib_data_calib_object — 设置标定板
```
set_calib_data_calib_object(CalibDataID, CalibObjIdx, CalibObjDescr)
```
- CalibObjDescr: 标定板描述文件路径(.cpd/.descr)

#### find_calib_object — 查找标定板
```
find_calib_object(Image, CalibDataID, CamIdx, CalibObjIdx, GenParamName, GenParamValue)
```

#### calibrate_cameras — 执行标定
```
calibrate_cameras(CalibDataID, Error)
```
- 输出Error: 反投影误差(像素)，<0.3为优秀

#### get_calib_data — 获取标定结果
```
get_calib_data(CalibDataID, ItemType, ItemIdx, DataName, DataValue)
```
- ItemType: `'camera'`→内参, `'calib_obj_pose'`→外参

---

## 三、相机模型参数

### area_scan_division（面阵除法模型）⭐最常用
```
[Focus, Kappa, Sx, Sy, Cx, Cy, ImageWidth, ImageHeight]
```
| 参数 | 说明 |
|---|---|
| Focus | 焦距(m) |
| Kappa | 径向畸变系数 |
| Sx, Sy | 像元尺寸(m) |
| Cx, Cy | 主点(像素) |

### area_scan_telecentric_division（远心镜头）
- 工业测量常用远心镜头

---

## 四、坐标转换

| 算子 | 功能 |
|---|---|
| `image_points_to_world_plane` ⭐ | 像素→世界平面坐标 |
| `project_3d_point` | 3D点→像素 |
| `set_origin_pose` | 设置世界坐标原点 |
| `pose_to_hom_mat3d` | 位姿→齐次矩阵 |
| `hom_mat3d_to_pose` | 齐次矩阵→位姿 |

### image_points_to_world_plane ⭐
```
image_points_to_world_plane(CamParam, WorldPose, Rows, Cols, Scale, X, Y)
```
- Scale: `'m'`/`'mm'`/`'um'` 输出单位

---

## 五、C# HalconDotNet 代码模板

### 模板1: 标定板标定完整流程 ⭐
```csharp
HTuple calibDataID, error;

// 1. 创建标定数据
HOperatorSet.CreateCalibData("calibration_object", 1, 1, out calibDataID);

// 2. 设置初始相机参数(面阵除法模型)
HTuple startCamParam = new HTuple();
startCamParam = startCamParam.TupleConcat(0.016);    // Focus 16mm
startCamParam = startCamParam.TupleConcat(0);         // Kappa
startCamParam = startCamParam.TupleConcat(4.65e-6);   // Sx
startCamParam = startCamParam.TupleConcat(4.65e-6);   // Sy
startCamParam = startCamParam.TupleConcat(640);        // Cx
startCamParam = startCamParam.TupleConcat(480);        // Cy
startCamParam = startCamParam.TupleConcat(1280);       // Width
startCamParam = startCamParam.TupleConcat(960);        // Height
HOperatorSet.SetCalibDataCamParam(calibDataID, 0, "area_scan_division", startCamParam);

// 3. 设置标定板
HOperatorSet.SetCalibDataCalibObject(calibDataID, 0, "caltab_30mm.descr");

// 4. 采集标定图像并查找标定板
for (int i = 0; i < numImages; i++)
{
    HObject calImage;
    HOperatorSet.ReadImage(out calImage, $"calib_{i:D2}.png");
    HOperatorSet.FindCalibObject(calImage, calibDataID, 0, 0, i, new HTuple(), new HTuple());
    calImage.Dispose();
}

// 5. 执行标定
HOperatorSet.CalibrateCamera(calibDataID, out error);
Console.WriteLine($"标定误差: {error.D:F4} 像素");

// 6. 获取标定后的内参
HTuple camParam;
HOperatorSet.GetCalibData(calibDataID, "camera", 0, "params", out camParam);

HOperatorSet.ClearCalibData(calibDataID);
```

### 模板2: 像素→世界坐标转换
```csharp
HTuple worldX, worldY;
// camParam: 标定后内参, worldPose: 标定后外参
HOperatorSet.ImagePointsToWorldPlane(camParam, worldPose, 
    pixelRow, pixelCol, "mm", out worldX, out worldY);
Console.WriteLine($"世界坐标: ({worldX.D:F3},{worldY.D:F3}) mm");
```
