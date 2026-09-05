# Halcon 几何变换与仿射技能手册

> 学习来源: `Filters/Geometric-Transformations/`, `Transformations/`
> 涵盖Task18：仿射变换、投影变换、图像校正、坐标变换
> 基础几何变换算子见 `skill/line_detection.md`

---

## 一、变换类型对比

| 类型 | 自由度 | 保持 | 算子 | ⭐场景 |
|---|---|---|---|---|
| **刚体变换** | 3(旋转+平移) | 形状+大小 | `vector_angle_to_rigid` | ⭐匹配后对齐 |
| **相似变换** | 4(+等比缩放) | 形状 | `hom_mat2d_*` | 缩放对齐 |
| **仿射变换** ⭐ | 6(+非等比缩放+剪切) | 平行线 | `hom_mat2d_*` | ⭐通用图像校正 |
| **投影变换** | 8 | 直线 | `projective_trans_*` | 透视校正 |

---

## 二、仿射变换矩阵构建 ⭐

### 基本构建流程
```
HomMat2dIdentity → 单位矩阵
→ HomMat2dRotate(Angle, CenterRow, CenterCol) → 旋转
→ HomMat2dScale(ScaleRow, ScaleCol, CenterRow, CenterCol) → 缩放
→ HomMat2dTranslate(TransRow, TransCol) → 平移
→ HomMat2dSlant(Theta, Axis, CenterRow, CenterCol) → 剪切
```

### 核心算子
| 算子 | 功能 | 参数 |
|---|---|---|
| `hom_mat2d_identity` | 单位矩阵 | → HomMat |
| `hom_mat2d_rotate` | 旋转 | Angle(rad), Pr, Pc |
| `hom_mat2d_scale` | 缩放 | Sx, Sy, Pr, Pc |
| `hom_mat2d_translate` | 平移 | Tx, Ty |
| `hom_mat2d_slant` | 剪切 | Theta, Axis('x'/'y'), Pr, Pc |
| `hom_mat2d_reflect` | 反射 | Pr, Pc, Angle |
| `hom_mat2d_compose` | 矩阵复合 | HomMat1, HomMat2 → HomMat |
| `hom_mat2d_invert` | 矩阵求逆 | HomMat → InvMat |

### 应用算子
| 算子 | 变换对象 |
|---|---|
| `affine_trans_image` ⭐ | 图像 |
| `affine_trans_region` | 区域 |
| `affine_trans_contour_xld` | XLD轮廓 |
| `affine_trans_point_2d` | 点坐标 |
| `affine_trans_pixel` | 像素坐标 |

---

## 三、快捷变换算子

| 算子 | 功能 | 参数 |
|---|---|---|
| `rotate_image` | 旋转图像 | Angle(°), Interpolation |
| `mirror_image` | 镜像 | Mode('row'/'column'/'diagonal') |
| `zoom_image_factor` | 缩放 | ScaleWidth, ScaleHeight, Interpolation |
| `zoom_image_size` | 缩放到指定尺寸 | Width, Height, Interpolation |
| `crop_part` | 裁剪 | Row, Col, Width, Height |
| `crop_rectangle1` | 矩形裁剪 | Row1, Col1, Row2, Col2 |

---

## 四、刚体变换(匹配对齐专用) ⭐

### vector_angle_to_rigid — 从匹配结果构建刚体矩阵
```
vector_angle_to_rigid(Row1, Col1, Angle1, Row2, Col2, Angle2, HomMat2D)
```
- (Row1,Col1,Angle1): 模板位姿
- (Row2,Col2,Angle2): 匹配位姿
- ⭐形状匹配后用此对齐！

### hom_mat2d_translate_local — 局部平移
```
hom_mat2d_translate_local(HomMat, Tx, Ty, HomMatTranslate)
```

---

## 五、投影变换(透视校正)

### 完整流程
```
1. 获取4对对应点(源→目标)
2. hom_vector_to_proj_hom_mat2d → 计算投影矩阵
3. projective_trans_image → 透视校正
```

### 核心算子
```
hom_vector_to_proj_hom_mat2d(Px, Py, Pw, Qx, Qy, Qw, Method, HomMat2D)
projective_trans_image(Image, TransImage, HomMat2D, Interpolation, AdaptImageSize, TransformRegion)
projective_trans_point_2d(HomMat2D, Px, Py, Qx, Qy)
projective_trans_region(Region, TransRegion, HomMat2D, Interpolation)
```

---

## 六、极坐标变换(详见line_detection.md)

```
polar_trans_image_ext → 环形展开为矩形
polar_trans_image_inv → 矩形恢复为环形
```

---

## 七、C# HalconDotNet 代码模板

### 模板1: 形状匹配后仿射对齐 ⭐⭐
```csharp
// 匹配结果: matchRow, matchCol, matchAngle
// 模板参考: refRow, refCol, refAngle(通常0)
HTuple homMat;
HOperatorSet.VectorAngleToRigid(refRow, refCol, 0, matchRow, matchCol, matchAngle, out homMat);

// 变换ROI区域到实际位置
HObject roiTemplate, roiActual;
HOperatorSet.GenRectangle1(out roiTemplate, 50, 50, 150, 200);
HOperatorSet.AffineTransRegion(roiTemplate, out roiActual, homMat, "nearest_neighbor");

roiActual.Dispose(); roiTemplate.Dispose();
```

### 模板2: 透视校正(4点)
```csharp
HObject image, corrected;
// 源图4个角点(梯形)
HTuple px = new HTuple(100, 500, 520, 80);
HTuple py = new HTuple(100, 120, 480, 460);
HTuple pw = new HTuple(1, 1, 1, 1);
// 目标矩形4角
HTuple qx = new HTuple(0, 600, 600, 0);
HTuple qy = new HTuple(0, 0, 400, 400);
HTuple qw = new HTuple(1, 1, 1, 1);

HTuple homMat;
HOperatorSet.HomVectorToProjHomMat2d(px, py, pw, qx, qy, qw, "normalized_dlt", out homMat);
HOperatorSet.ProjectiveTransImage(image, out corrected, homMat, "bilinear", "false", "false");

corrected.Dispose();
```

### 模板3: 图像旋转+缩放
```csharp
HObject image, rotated, zoomed;
HOperatorSet.ReadImage(out image, imagePath);
// 旋转45度
HOperatorSet.RotateImage(image, out rotated, 45, "constant");
// 缩放50%
HOperatorSet.ZoomImageFactor(image, out zoomed, 0.5, 0.5, "bilinear");

zoomed.Dispose(); rotated.Dispose(); image.Dispose();
```
