# Halcon 线检测与几何变换技能手册

> 学习来源: `Filters/Lines/`, `Filters/Geometric-Transformations/`
> 涵盖12个例程：线检测、边缘段检测、极坐标变换、仿射变换

---

## 一、线检测算子对比表

| 算子 | 原理 | 精度 | 速度 | 适用场景 |
|---|---|---|---|---|
| **lines_gauss** ⭐ | 高斯二阶导数 | 亚像素 | 中 | ⭐通用线/裂纹检测(最常用) |
| **lines_facet** | Facet模型 | 亚像素 | 慢 | 宽线/管道检测 |
| **lines_color** | 彩色线检测 | 亚像素 | 慢 | 彩色图像中的线 |
| **detect_edge_segments** | 边缘段 | 像素级 | 快 | 边缘段→直线拟合 |

---

## 二、核心算子详解

### lines_gauss ⭐ — 高斯线检测（最常用）
```
lines_gauss(Image, Lines, Sigma, Low, High, LightDark, ExtractWidth, LineModel, CompleteJunctions)
```
- **Sigma**: 高斯平滑(1.0~3.0), 需匹配线宽
- **Low/High**: 滞后阈值(低/高), 用 `calculate_lines_gauss_parameters` 自动计算
- **LightDark**: `'light'`亮线 / `'dark'`暗线 / `'light_dark'`两者
- **ExtractWidth**: `'true'`提取线宽
- **LineModel**: `'bar-shaped'`条形 / `'parabolic'`抛物线
- **输出**: XLD轮廓，附带属性(angle, width_left, width_right)

### calculate_lines_gauss_parameters — 自动计算参数
```
calculate_lines_gauss_parameters(MaxLineWidth, Contrast, Sigma, Low, High)
```
- **MaxLineWidth**: 最大线宽(像素)
- **Contrast**: [对比度, 0]

### detect_edge_segments — 边缘段检测
```
detect_edge_segments(Image, Edges, SobelSize, MinAmplitude, MaxDistance, MinLength)
```
- 输出边缘XLD段，可后续拟合为直线/圆弧

### lines_facet — Facet线检测
```
lines_facet(Image, Lines, MaskSize, Low, High, LightDark)
```
- MaskSize越大检测越宽的线

---

## 三、几何变换算子

| 算子 | 功能 | 典型场景 |
|---|---|---|
| `affine_trans_image` | 仿射变换 | 旋转+缩放+平移 |
| `rotate_image` | 简单旋转 | 角度校正 |
| `mirror_image` | 镜像翻转 | 左右/上下翻转 |
| `zoom_image_factor` | 缩放 | 分辨率调整 |
| `polar_trans_image_ext` ⭐ | 极坐标变换 | ⭐环形→矩形展开 |
| `projective_trans_image` | 投影变换 | 透视校正 |

### polar_trans_image_ext ⭐ — 极坐标变换
```
polar_trans_image_ext(Image, PolarImage, Row, Col, AngleStart, AngleEnd, RadiusStart, RadiusEnd, Width, Height, Interpolation)
```
- **Row, Col**: 圆心坐标
- **AngleStart/End**: 角度范围(0~6.28=完整圆)
- **RadiusStart/End**: 半径范围
- ⭐将环形区域展开为矩形 → 方便检测环形缺陷

### affine_trans_image — 仿射变换
```
// 构建仿射矩阵
hom_mat2d_identity(HomMat)
hom_mat2d_rotate(HomMat, Angle, Row, Col, HomMat2)
hom_mat2d_translate(HomMat2, Tx, Ty, HomMat3)
// 应用变换
affine_trans_image(Image, Transformed, HomMat3, 'constant', 'false')
```

---

## 四、线检测策略决策树

```
线检测需求
├─ 检测细线/裂纹(宽度<20px)？
│   └─ lines_gauss ⭐ (Sigma=MaxWidth/sqrt(3))
├─ 检测宽线/管道？
│   └─ lines_facet (大MaskSize)
├─ 彩色图像？
│   └─ lines_color
├─ 需要直线段而非曲线？
│   └─ detect_edge_segments → fit_line_contour_xld
├─ 环形目标检测？
│   └─ polar_trans_image_ext展开 → lines_gauss
└─ 需要精确线宽测量？
    └─ lines_gauss(ExtractWidth='true') → get_contour_attrib_xld('width_left/right')
```

---

## 五、C# HalconDotNet 代码模板

### 模板1: lines_gauss线检测 ⭐
```csharp
HObject image, lines;
HTuple sigma, low, high;

HOperatorSet.ReadImage(out image, imagePath);
// 自动计算参数: 最大线宽10px, 对比度20
HOperatorSet.CalculateLinesGaussParameters(10, new HTuple(20, 0), out sigma, out low, out high);
// 线检测
HOperatorSet.LinesGauss(image, out lines, sigma, low, high, "dark", "true", "parabolic", "true");

HTuple count;
HOperatorSet.CountObj(lines, out count);
Console.WriteLine($"检测到 {count.I} 条线");

// 获取线宽属性
for (int i = 1; i <= count.I; i++)
{
    HObject line;
    HOperatorSet.SelectObj(lines, out line, i);
    HTuple widthL, widthR;
    HOperatorSet.GetContourAttribXld(line, "width_left", out widthL);
    HOperatorSet.GetContourAttribXld(line, "width_right", out widthR);
    Console.WriteLine($"线{i}: 宽度={widthL.D + widthR.D:F1}px");
    line.Dispose();
}

lines.Dispose(); image.Dispose();
```

### 模板2: 极坐标展开环形检测 ⭐
```csharp
HObject image, polarImage, lines;
double centerRow = 300, centerCol = 400;
double rStart = 100, rEnd = 200;

HOperatorSet.ReadImage(out image, imagePath);
// 极坐标展开
HOperatorSet.PolarTransImageExt(image, out polarImage,
    centerRow, centerCol, 0, 6.28318, rStart, rEnd, 720, 200, "bilinear");
// 在展开图上检测线(环形缺陷变成直线)
HOperatorSet.LinesGauss(polarImage, out lines, 1.5, 3, 8, "dark", "true", "parabolic", "true");

lines.Dispose(); polarImage.Dispose(); image.Dispose();
```

### 模板3: 仿射变换图像校正
```csharp
HObject image, transformed;
HTuple homMat;

HOperatorSet.ReadImage(out image, imagePath);
HOperatorSet.HomMat2dIdentity(out homMat);
HOperatorSet.HomMat2dRotate(homMat, 0.1, 300, 400, out homMat); // 旋转0.1rad
HOperatorSet.AffineTransImage(image, out transformed, homMat, "constant", "false");

transformed.Dispose(); image.Dispose();
```
