# Halcon 图像平滑与降噪技能手册

> 学习来源: `Filters/Smoothing/`, `Filters/Inpainting/`
> 涵盖21个例程：均值/高斯/中值/双边/引导滤波、各向异性扩散、图像修复

---

## 一、平滑滤波器总览对比表

| 算子 | 保边性 | 速度 | 适用噪声 | 参数 | ⭐推荐场景 |
|---|---|---|---|---|---|
| **mean_image** | ❌差 | 最快 | 高斯噪声 | MaskW/H | 简单预处理、背景估算 |
| **gauss_filter** | ❌差 | 快 | 高斯噪声 | Size(3~11) | 边缘检测前预滤波 |
| **gauss_image** | ❌差 | 快 | 高斯噪声 | Sigma | 连续Sigma控制 |
| **smooth_image** | 中等 | 快 | 高斯噪声 | Filter,Alpha | 通用平滑(多算法选择) |
| **binomial_filter** | ❌差 | 最快 | 高斯噪声 | MaskW/H | gauss_filter的快速近似 |
| **median_image** ⭐ | ✅好 | 中 | **椒盐噪声** | MaskType,Radius | ⭐椒盐噪声首选 |
| **median_rect** | ✅好 | 中 | 椒盐噪声 | MaskW/H | 矩形中值 |
| **median_weighted** | ✅好 | 中 | 椒盐噪声 | MaskType | 加权中值(中心权重大) |
| **sigma_image** | ✅好 | 中 | 混合噪声 | MaskW/H,Sigma | 自适应均值(仅平滑相似像素) |
| **bilateral_filter** ⭐ | ✅很好 | 慢 | 高斯噪声 | SigmaS,SigmaR | ⭐保边降噪首选 |
| **guided_filter** ⭐ | ✅很好 | 中 | 高斯噪声 | Radius,Eps | ⭐快速保边(替代bilateral) |
| **anisotropic_diffusion** | ✅很好 | 最慢 | 各类噪声 | Mode,Contrast,Theta,Iter | 强保边但慢 |
| **trimmed_mean** | ✅中等 | 中 | 混合噪声 | MaskW/H,Number | 排序后截断取均值 |
| **midrange_image** | ❌差 | 快 | — | MaskW/H | (max+min)/2 |

---

## 二、核心算子详解

### mean_image — 均值滤波
```
mean_image(Image, Smoothed, MaskWidth, MaskHeight)
```
- 最简单最快，但会模糊边缘
- 常用于 `dyn_threshold` 前的背景估算

### gauss_filter — 高斯滤波
```
gauss_filter(Image, Smoothed, Size)
```
- Size: 3/5/7/9/11（奇数）
- 边缘检测前标准预处理

### median_image ⭐ — 中值滤波
```
median_image(Image, Smoothed, MaskType, Radius, Margin)
```
- **MaskType**: `'circle'`/`'square'`
- **Radius**: 1~10
- ⭐椒盐噪声(salt-and-pepper)的最佳选择
- 保边效果好，但对高斯噪声效果一般

### bilateral_filter ⭐ — 双边滤波
```
bilateral_filter(Image, ImageJoint, Smoothed, SigmaSpatial, SigmaRange, GenParamName, GenParamValue)
```
- **SigmaSpatial**: 空间权重(3~10), 越大越平滑
- **SigmaRange**: 灰度权重(10~50), 越大越模糊边缘
- ⭐同时考虑空间距离和灰度差异→保边降噪

### guided_filter ⭐ — 引导滤波
```
guided_filter(Image, ImageGuide, Smoothed, Radius, Epsilon)
```
- **Radius**: 窗口半径(5~20)
- **Epsilon**: 正则化(0.01~0.1), 越小越保边
- 速度比bilateral快，效果接近
- 可用于去纹理: 以原图为引导滤波自身

### anisotropic_diffusion — 各向异性扩散
```
anisotropic_diffusion(Image, Smoothed, Mode, Contrast, Theta, Iterations)
```
- **Mode**: `'perona-malik'`/`'weickert'`
- **Contrast**: 对比度阈值(10~50)
- **Theta**: 时间步长(0.5)
- **Iterations**: 迭代次数(5~20)
- 最强保边但最慢

### smooth_image — 通用平滑
```
smooth_image(Image, Smoothed, Filter, Alpha)
```
- **Filter**: `'gauss'`/`'deriche1'`/`'deriche2'`/`'shen'`
- **Alpha**: 平滑强度
- 统一接口选择不同算法

---

## 三、噪声类型→滤波器选择决策树

```
噪声类型
├─ 椒盐噪声(黑白随机点)？
│   └─ median_image ⭐ (Radius=1~3)
├─ 高斯噪声(均匀模糊)？
│   ├─ 不需要保边 → gauss_filter/mean_image (快)
│   ├─ 需要保边 → bilateral_filter ⭐ 或 guided_filter ⭐
│   └─ 强保边+慢OK → anisotropic_diffusion
├─ 混合噪声？
│   ├─ median先去椒盐 → bilateral再去高斯
│   └─ sigma_image (自适应)
├─ 纹理噪声(周期性)？
│   └─ FFT滤波(Task04)
└─ 图像有缺损/孔洞？
    └─ Inpainting修复
```

---

## 四、Inpainting 图像修复

| 算子 | 方法 | 适用场景 |
|---|---|---|
| `harmonic_interpolation` | 谐波插值 | 小区域平滑填充 |
| `inpainting_aniso` | 各向异性扩散 | 保边修复 |
| `inpainting_ced` | CED扩散 | 沿边缘方向修复 |
| `inpainting_ct` | 曲率传输 | 线条延续 |
| `inpainting_mcf` | 均值曲率流 | 平滑修复 |
| `inpainting_texture` | 纹理合成 | ⭐大面积纹理修复 |

通用修复流程:
```
1. 创建mask区域(标记缺陷位置)
2. inpainting_xxx(Image, Region, Repaired, ...)
3. 修复后图像用于后续分析
```

---

## 五、参数调优指南

### bilateral_filter
| SigmaSpatial | SigmaRange | 效果 |
|---|---|---|
| 3, 20 | 轻微平滑，强保边 | 精细检测 |
| 5, 30 | ⭐中等平滑 | 一般工业场景 |
| 10, 50 | 强平滑，边缘略模糊 | 强噪声 |

### median_image
| Radius | 效果 |
|---|---|
| 1 | 轻微去椒盐 |
| 2~3 | ⭐标准去噪 |
| 5+ | 强去噪但丢失细节 |

---

## 六、C# HalconDotNet 代码模板

### 模板1: 保边降噪（bilateral）⭐
```csharp
HObject image, smoothed;
HOperatorSet.ReadImage(out image, imagePath);
HOperatorSet.BilateralFilter(image, image, out smoothed, 5, 30, new HTuple(), new HTuple());
smoothed.Dispose();
image.Dispose();
```

### 模板2: 椒盐噪声去除（median）⭐
```csharp
HObject image, smoothed;
HOperatorSet.ReadImage(out image, imagePath);
HOperatorSet.MedianImage(image, out smoothed, "circle", 2, "mirrored");
smoothed.Dispose();
image.Dispose();
```

### 模板3: 快速保边降噪（guided_filter）
```csharp
HObject image, smoothed;
HOperatorSet.ReadImage(out image, imagePath);
HOperatorSet.GuidedFilter(image, image, out smoothed, 10, 0.04);
smoothed.Dispose();
image.Dispose();
```

### 模板4: 降噪→增强→分割流水线
```csharp
HObject img, denoised, enhanced, region;

HOperatorSet.ReadImage(out img, path);
// 1. 保边降噪
HOperatorSet.BilateralFilter(img, img, out denoised, 5, 30, new HTuple(), new HTuple());
// 2. 增强(Task02)
HOperatorSet.Emphasize(denoised, out enhanced, 7, 7, 2.0);
// 3. 分割(Task09)
HOperatorSet.BinaryThreshold(enhanced, out region, "max_separability", "light", out _);

region.Dispose(); enhanced.Dispose(); denoised.Dispose(); img.Dispose();
```

### 模板5: 图像修复
```csharp
HObject image, region, repaired;
// region = 缺陷区域mask
HOperatorSet.InpaintingTexture(image, region, out repaired, 5, 3, 1, "border");
repaired.Dispose(); image.Dispose();
```
