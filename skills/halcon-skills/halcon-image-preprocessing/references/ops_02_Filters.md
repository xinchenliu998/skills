# HALCON 算子分类详解：Filters（图像滤波）

> **分类**：Filters 图像滤波
> **子类数**：19 个（Arithmetic、Bit、Color、Edges、Enhancement、FFT、Geometric Transformations、Inpainting、Lines、Match、Misc、Noise、Optical Flow、Points、Scene Flow、Smoothing、Texture、Wiener、Color Transformation）
> **算子数**：约 280 个（HALCON 中最大的算子家族）
> **学习优先级**：⭐⭐⭐⭐⭐（决定后续算法成败的"预处理砧板"）
> **典型应用场景**：去噪、对比度增强、边缘提取、纹理分析、频域处理、模板匹配图像准备——本质是把"脏"输入变干净、把"看不见"细节变明显。

---

## 1. 概述

**Filters 分类在 HALCON 体系中的定位**

Filters 是 HALCON 中最庞大的算子家族（约 280 个算子，覆盖 19 个子类），承担"预处理砧板"的职责。任何复杂视觉算法的输出质量都取决于前置滤波的成败：

- **去噪**：图像从相机出来总有噪声，必须先 `gauss_filter`/`median_image`/`bilateral_filter` 等。
- **增强**：`equ_histo_image`/`emphasize` 让细节可见，否则下游算法找不到目标。
- **边缘提取**：`edges_image`/`sobel_amp`/`edges_sub_pix` 是工业检测的核心入口。
- **频域分析**：`fft_image`/`convol_fft` 处理周期性纹理、印刷品网点、莫尔条纹。
- **几何变换**：`affine_trans_image`/`polar_trans_image` 解决姿态变化。
- **纹理**：`texture_laws`/`deviation_image` 提取周期性纹理特征。
- **修补**：`inpainting_*` 系列去除划痕/污渍/激光雕刻标记。

**与其他分类的关系**

- **上游**：从 **Image** 接收原图（`read_image` 输出）。
- **下游**：输出给 **Regions**（阈值后转 Region）、**XLD**（亚像素边缘）、**Segmentation**（分割）、**Matching**（模板准备）。
- **并行**：与 **Morphology** 部分功能重叠（如平滑），但 Morphology 偏结构元素方向。

**为什么必须精通 Filters**

一个项目 50% 的调试时间在"换滤波参数"。`median_image` 的核大小、`equ_histo_image` 的灰度区间、`edges_sub_pix` 的 `Sigma`——一个参数错了整条流水线崩盘。Filters 是 HALCON 工程师日常调参最多的家族。

---

## 2. 应用场景

### 场景 A：金属表面划伤检测
- **行业**：汽车零部件
- **问题**：金属表面有随机分布的细小划伤，需要在强反光背景下识别。
- **算法选择**：`gauss_filter`（去相机噪声）→ `emphasize`（边缘增强）→ `bandpass_image`（特定尺度带通）→ `dyn_threshold` 分割。
- **期望产出**：划伤二值区域，按长度分级报警。

### 场景 B：印刷品网点检测
- **行业**：包装印刷
- **问题**：检测网点缺失、堵塞，常规空间域滤波无法识别周期性结构。
- **算法选择**：`fft_image`（前向 FFT）→ `gen_bandpass`（生成带通滤波器）→ `convol_fft` → `fft_image_inv`（反变换）→ `dyn_threshold`。
- **期望产出**：异常区域的二值图。

### 场景 C：医学影像去噪
- **行业**：医学影像
- **问题**：低剂量 X 光图像噪声大，常规 `gauss_filter` 会丢边缘。
- **算法选择**：`bilateral_filter`（保边降噪）或 `guided_filter`（导向滤波）。
- **期望产出**：干净图像保留全部诊断细节。

### 场景 D：纺织品瑕疵检测
- **行业**：纺织
- **问题**：织物纹理周期性，需要检测纹理破坏。
- **算法选择**：`texture_laws`（Laws 纹理能量滤波）→ `deviation_image`（局部方差）→ `threshold`。
- **期望产出**：瑕疵位置热图。

### 场景 E：激光雕刻污渍修补
- **行业**：金属标牌
- **问题**：产品表面有油渍/划痕污染需拍照后去除。
- **算法选择**：`inpainting_texture`（纹理合成填充）或 `inpainting_ct`（曲率扩散）。
- **期望产出**：视觉上"无瑕"的图像。

---

## 3. 子分类详解

| 子类 | 算子数 | 代表算子 | 用途速览 |
|------|-------|---------|---------|
| **Arithmetic（算术）** | ~20 | `add_image`, `sub_image`, `mult_image`, `div_image`, `abs_diff_image`, `scale_image`, `abs_image`, `invert_image`, `exp_image`, `log_image`, `pow_image`, `sqrt_image`, `max_image`, `min_image` | 像素级加减乘除、对比度拉伸 |
| **Bit（位操作）** | ~10 | `bit_and`, `bit_or`, `bit_xor`, `bit_not`, `bit_mask`, `bit_slice`, `bit_lshift`, `bit_rshift` | 位级运算（掩膜、特征提取） |
| **Color（颜色变换）** | ~10 | `trans_from_rgb`, `trans_to_rgb`, `apply_color_trans_lut`, `linear_trans_color`, `clear_color_trans_lut`, `get_color_trans_lut` | 色彩空间预计算 LUT |
| **Edges（边缘）** | ~20 | `edges_image`, `edges_color`, `edges_sub_pix`, `edges_color_sub_pix`, `sobel_amp`, `sobel_dir`, `prewitt_amp`, `robinson_amp`, `kirsch_amp`, `frei_amp`, `laplace`, `laplace_of_gauss`, `diff_of_gauss`, `bandpass_image`, `derivate_gauss` | 像素级与亚像素边缘 |
| **Enhancement（增强）** | ~10 | `emphasize`, `illuminate`, `scale_image_max`, `equ_histo_image`, `equ_histo_image_rect`, `gray_range_rect`, `gray_closing_rect`, `gray_opening_rect` | 对比度拉伸、直方图均衡 |
| **FFT（频域）** | ~15 | `fft_generic`, `fft_image`, `fft_image_inv`, `rft_generic`, `convol_fft`, `correlation_fft`, `phase_correlation_fft`, `optimize_fft_speed`, `optimize_rft_speed`, `gen_bandpass`, `gen_highpass`, `gen_lowpass`, `gen_sin_bandpass` | 频域滤波与匹配 |
| **Geometric Transformations** | ~15 | `affine_trans_image`, `affine_trans_image_size`, `projective_trans_image`, `polar_trans_image`, `polar_trans_image_inv`, `mirror_image`, `rotate_image`, `zoom_image_factor`, `zoom_image_size`, `map_image` | 几何变换图像 |
| **Inpainting（修补）** | ~5 | `inpainting_aniso`, `inpainting_ced`, `inpainting_ct`, `inpainting_mcf`, `inpainting_texture` | 区域填充 / 纹理合成 |
| **Lines（线条检测）** | ~5 | `lines_color`, `lines_facet`, `lines_gauss` | 线状结构提取 |
| **Match（匹配）** | ~5 | `exhaustive_match`, `exhaustive_match_mg`, `phase_correlation_fft` | 模板匹配（空间域与频域） |
| **Noise（噪声）** | ~10 | `add_noise_white`, `add_noise_distribution`, `gauss_distribution`, `noise_distribution_mean`, `estimate_noise`, `sp_distribution`, `simulate_defocus` | 噪声注入与估计 |
| **Optical Flow（光流）** | ~5 | `optical_flow_mg`, `unwarp_image_vector_field`, `vector_field_to_real` | 运动场估计 |
| **Points（特征点）** | ~10 | `points_foerstner`, `points_harris`, `points_harris_binomial`, `points_lepetit`, `points_sojka` | 亚像素角点检测 |
| **Scene Flow（场景流）** | ~5 | `scene_flow_calib`, `scene_flow_uncalib` | 多视点运动估计 |
| **Smoothing（平滑）** | ~25 | `gauss_filter`, `mean_image`, `median_image`, `median_rect`, `median_separate`, `median_weighted`, `binomial_filter`, `bilateral_filter`, `guided_filter`, `smooth_image`, `anisotropic_diffusion`, `isotropic_diffusion`, `coherence_enhancing_diff`, `mean_curvature_flow`, `shock_filter` | 各类去噪/平滑 |
| **Texture（纹理）** | ~5 | `texture_laws`, `deviation_image`, `cooc_feature_matrix`, `gen_filter_mask` | 纹理能量/方差/共生矩阵 |
| **Wiener（维纳）** | ~3 | `wiener_filter`, `wiener_filter_ni` | 自适应最小均方误差去噪 |
| **Misc** | ~5 | `bandpass_image`, `gauss_image`, `gamma_image`, `info_smooth` | 杂项 |

---

## 4. 核心算子详解

1. **gauss_filter** — 高斯平滑 / 输入：`Image, MaskSize, Sigma → ImageGauss`；最常用去噪，默认 MaskSize=5。
2. **mean_image** — 均值平滑 / 比 `gauss_filter` 快；适合大图粗去噪。
3. **median_image** — 中值滤波 / 输入：`Image, MaskType, MaskSize → ImageMedian`；保边，去椒盐噪声最佳。
4. **bilateral_filter** — 双边滤波 / 输入：`Image, MaskSize, SigmaSpatial, SigmaRange → ImageBilateral`；保边降噪。
5. **guided_filter** — 导向滤波 / 输入：`Image, ImageGuide, Radius, Amplitude → ImageFiltered`；纹理保留最强。
6. **binomial_filter** — 二项式滤波 / 类似高斯但更接近离散；速度快。
7. **anisotropic_diffusion** — 各向异性扩散 / 非线性保边滤波；处理医学/遥感图像。
8. **equ_histo_image** — 全局直方图均衡 / 输出对比度拉伸图。
9. **equ_histo_image_rect** — 局部直方图均衡 / 处理光照不均场景。
10. **emphasize** — 边缘增强 / Sharpen 效果。
11. **illuminate** — 局部亮度调节 / 输入：`Image, MaskWidth, MaskHeight, Factor → ImageIllum`。
12. **scale_image** — 对比度缩放 / `g' = g * Mult + Add`；最常用对比度调整。
13. **scale_image_max** — 最大对比度拉伸到 0-255。
14. **abs_diff_image** — 图像绝对差 / 用于背景差分、缺陷对比。
15. **sub_image** / **add_image** / **mult_image** — 像素加减乘。
16. **edges_image** — Canny 边缘 / 输入：`Image, Filter, Alpha, Low, High → Edges`。
17. **edges_sub_pix** — Canny 亚像素边缘 / 输出 `XLDContours`。
18. **sobel_amp** / **sobel_dir** — Sobel 幅度与方向 / 经典梯度算子。
19. **prewitt_amp** / **roberts** / **kirsch_amp** / **frei_amp** — 各类梯度算子。
20. **laplace** / **laplace_of_gauss** — 拉普拉斯 / 高斯-拉普拉斯。
21. **diff_of_gauss** — 高斯差分（DoG）/ 类似 LoG，常用于 blob 检测。
22. **fft_image** / **fft_image_inv** — 前向/反向 FFT。
23. **convol_fft** — 频域卷积 / 输入：`ImageFFT, FilterFFT → ImageConvolved`。
24. **correlation_fft** — 频域相关 / 用于模板匹配。
25. **phase_correlation_fft** — 相位相关 / 频域平移估计。
26. **affine_trans_image** — 仿射变换图像 / 输入：`Image, HomMat2D, Interpolation, AdaptSize → ImageTrans`。
27. **rotate_image** — 任意角度旋转。
28. **zoom_image_factor** / **zoom_image_size** — 缩放。
29. **polar_trans_image** — 笛卡尔→极坐标变换 / OCR 前置。
30. **texture_laws** — Laws 纹理滤波 / 输入：`Image, Filter, Shift, Size → ImageLaws`。
31. **inpainting_ct** — 曲率扩散修补 / 输入：`Image, Region, Epsilon, Kappa, Mode → ImageInpainted`。
32. **points_harris** — Harris 角点 / 输出 `Region`。
33. **points_foerstner** — Forstner 角点 / 更精确的角点检测。

---

## 5. HDevelop 示例代码

### 示例 1：金属表面划伤增强 + 边缘提取流水线

**场景**：铝制零件表面有微小划伤。
**功能**：高斯去噪 → 直方图均衡 → 边缘增强 → Canny 边缘提取 → 形态学清理。
**预期输出**：划伤边缘叠加显示。

```hdevelop
* 示例 1：金属表面划伤检测预处理链
* 场景：铝件表面检测

dev_update_window ('off')
dev_update_pc ('off')
dev_update_var ('off')

* 1. 读取原图（灰度）
read_image (MetalImage, 'scratch_metal_01')
get_image_size (MetalImage, ImageWidth, ImageHeight)

* 2. 高斯去噪（去相机噪声）
gauss_filter (MetalImage, ImageGauss, 5, 1.0)

* 3. 全局直方图均衡
equ_histo_image (ImageGauss, ImageEqu)

* 4. 边缘增强（让划伤更突出）
emphasize (ImageEqu, ImageEmph, 7, 1.0, 'weighted')

* 5. Canny 边缘提取
edges_image (ImageEmph, EdgesAmp, EdgesDir, 'canny', 1.0, 'nms', 20, 40)

* 6. 边缘二值化（筛选弱边缘）
threshold (EdgesAmp, StrongEdges, 30, 255)

* 7. 显示对比图（4 子图）
dev_open_window (0, 0, ImageWidth * 2 + 30, ImageHeight * 2 + 30, 'black', MainWindow)
dev_set_part (0, 0, ImageHeight * 2 + 29, ImageWidth * 2 + 29)

* 子图 1：原图
dev_display (MetalImage)
dev_disp_text ('Original', 'window', 12, 12, 'yellow', 'box', 'true')

* 子图 2：高斯去噪 + 直方图均衡
dev_set_part (0, ImageWidth + 30, ImageHeight - 1, ImageWidth * 2 + 29)
dev_display (ImageEqu)
dev_disp_text ('Gauss + EquHisto', 'window', 12, 12, 'yellow', 'box', 'true')

* 子图 3：边缘增强
dev_set_part (ImageHeight + 30, 0, ImageHeight * 2 + 29, ImageWidth - 1)
dev_display (ImageEmph)
dev_disp_text ('Emphasize', 'window', 12, 12, 'yellow', 'box', 'true')

* 子图 4：Canny 边缘叠加在原图
dev_set_part (ImageHeight + 30, ImageWidth + 30, ImageHeight * 2 + 29, ImageWidth * 2 + 29)
dev_set_color ('red')
dev_display (MetalImage)
dev_set_draw ('margin')
dev_set_line_width (2)
dev_display (StrongEdges)
dev_disp_text ('Canny edges', 'window', 12, 12, 'yellow', 'box', 'true')

dev_update_pc ('on')
dev_update_var ('on')
dev_update_window ('on')
```

### 示例 2：FFT 频域带通滤波（印刷品网点检测）

**场景**：包装印刷品上的网点结构需检测异常。
**功能**：原图 → FFT → 带通滤波 → 反 FFT → 差分 → 阈值。
**预期输出**：异常网点区域。

```hdevelop
* 示例 2：FFT 频域带通滤波
* 场景：印刷网点周期性检测

dev_update_window ('off')
dev_update_pc ('off')
dev_update_var ('off')

* 1. 读取原图
read_image (PrintImage, 'print_pattern_01')
get_image_size (PrintImage, PWidth, PHeight)
convert_image_type (PrintImage, PrintImageReal, 'real')

* 2. 前向 FFT
fft_image (PrintImageReal, ImageFFT)

* 3. 生成带通滤波器（特定尺度）
gen_sin_bandpass (ImageFFT, FilterBandpass, 0.1, 'low', 'none', 0.4, 'high', 'none', PWidth, PHeight)

* 4. 应用滤波器
convol_fft (ImageFFT, FilterBandpass, FilteredFFT)

* 5. 反 FFT
fft_image_inv (FilteredFFT, FilteredImage)

* 6. 计算能量谱（取绝对值）
abs_image (FilteredImage, FilteredAbs)

* 7. 归一化对比度（频域图通常数值小）
scale_image (FilteredAbs, FilteredScaled, 255.0, 0)

* 8. 取原图与滤波图的差异作为异常
abs_diff_image (PrintImage, FilteredScaled, DiffImage, 1.0)

* 9. 阈值分割异常
threshold (DiffImage, AnomalyRegion, 50, 255)
connection (AnomalyRegion, ConnectedAnomalies)
select_shape (ConnectedAnomalies, SelectedAnomalies, 'area', 'and', 100, 99999)

* 10. 显示频域图 + 异常
dev_open_window (0, 0, PWidth * 2 + 30, PHeight * 2 + 30, 'black', FFTWindow)
dev_set_part (0, 0, PHeight * 2 + 29, PWidth * 2 + 29)
dev_display (PrintImage)
dev_disp_text ('Original', 'window', 12, 12, 'yellow', 'box', 'true')

dev_set_part (0, PWidth + 30, PHeight - 1, PWidth * 2 + 29)
dev_display (FilteredScaled)
dev_disp_text ('FFT bandpass', 'window', 12, 12, 'yellow', 'box', 'true')

dev_set_part (PHeight + 30, 0, PHeight * 2 + 29, PWidth - 1)
dev_display (DiffImage)
dev_disp_text ('Diff (anomaly)', 'window', 12, 12, 'yellow', 'box', 'true')

dev_set_part (PHeight + 30, PWidth + 30, PHeight * 2 + 29, PWidth * 2 + 29)
dev_display (PrintImage)
dev_set_colored (6)
dev_set_draw ('margin')
dev_set_line_width (2)
dev_display (SelectedAnomalies)
dev_disp_text ('Detected anomalies', 'window', 12, 12, 'yellow', 'box', 'true')

dev_update_pc ('on')
dev_update_var ('on')
dev_update_window ('on')
```

### 示例 3：保边滤波对比（医学影像去噪）

**场景**：低剂量医学影像需要去噪但保留边缘。
**功能**：原图 → 三种滤波（高斯、双边、导向）→ 对比。
**预期输出**：三种滤波结果并排显示。

```hdevelop
* 示例 3：保边滤波对比
* 场景：医学影像去噪

dev_update_window ('off')
dev_update_pc ('off')
dev_update_var ('off')

* 1. 读取医学图像
read_image (MedicalImage, 'medical_xray_01')
get_image_size (MedicalImage, MWidth, MHeight)

* 2. 模拟噪声注入（用于演示对比效果）
add_noise_white (MedicalImage, NoisyImage, 20)

* 3. 滤波对比
* 3.1 高斯滤波（基准，可能丢边缘）
gauss_filter (NoisyImage, GaussFiltered, 5, 1.5)

* 3.2 中值滤波（保边，去椒盐噪声好）
median_image (NoisyImage, MedianFiltered, 'circle', 3, 'mirrored')

* 3.3 双边滤波（保边降噪）
* 注：双边滤波要求 'byte' 类型
convert_image_type (NoisyImage, NoisyByte, 'byte')
bilateral_filter (NoisyByte, BilateralFiltered, ImageBilateralAmplitude, 5, 1.5, 1.5, 'mirrored')

* 4. 评估：边缘保留度（用 sobel 算子计算）
sobel_amp (GaussFiltered, GaussEdge, 'sum_abs', 3)
sobel_amp (MedianFiltered, MedianEdge, 'sum_abs', 3)
sobel_amp (BilateralFiltered, BilateralEdge, 'sum_abs', 3)

intensity (GaussEdge, GaussEdge, GaussEdgeMean, Deviation1)
intensity (MedianEdge, MedianEdge, MedianEdgeMean, Deviation2)
intensity (BilateralEdge, BilateralEdge, BilateralEdgeMean, Deviation3)

* 5. 显示对比
dev_open_window (0, 0, MWidth * 2 + 30, MHeight * 2 + 30, 'black', MedWindow)
dev_set_part (0, 0, MHeight * 2 + 29, MWidth * 2 + 29)

* 子图 1：含噪原图
dev_display (NoisyImage)
dev_disp_text ('Noisy input', 'window', 12, 12, 'yellow', 'box', 'true')

* 子图 2：高斯
dev_set_part (0, MWidth + 30, MHeight - 1, MWidth * 2 + 29)
dev_display (GaussFiltered)
dev_disp_text ('Gauss (Edge=' + GaussEdgeMean$'.1f' + ')', 'window', 12, 12, 'yellow', 'box', 'true')

* 子图 3：中值
dev_set_part (MHeight + 30, 0, MHeight * 2 + 29, MWidth - 1)
dev_display (MedianFiltered)
dev_disp_text ('Median (Edge=' + MedianEdgeMean$'.1f' + ')', 'window', 12, 12, 'yellow', 'box', 'true')

* 子图 4：双边
dev_set_part (MHeight + 30, MWidth + 30, MHeight * 2 + 29, MWidth * 2 + 29)
dev_display (BilateralFiltered)
dev_disp_text ('Bilateral (Edge=' + BilateralEdgeMean$'.1f' + ')', 'window', 12, 12, 'yellow', 'box', 'true')

dev_update_pc ('on')
dev_update_var ('on')
dev_update_window ('on')
```

---

## 6. 典型工业流水线

### 流水线 1：标准去噪 + 增强 + 边缘 + 分割链

```
read_image (原始图) → gauss_filter (5, 1.0) → equ_histo_image → emphasize → edges_sub_pix (Sigma=1.0) → segment_contours_xld → select_contours_xld (按长度过滤) → fit_*_contour_xld
```

### 流水线 2：频域周期性检测链

```
read_image
   ↓
convert_image_type → real
   ↓
fft_image
   ↓
gen_sin_bandpass (特定频率带通)
   ↓
convol_fft
   ↓
fft_image_inv
   ↓
abs_diff_image 与原图差分
   ↓
threshold 异常区域
```

### 流水线 3：纹理瑕疵检测链

```
read_image
   ↓
median_image 去椒盐噪声
   ↓
texture_laws (L5S5) 提取纹理能量
   ↓
deviation_image 局部方差
   ↓
dyn_threshold 动态阈值
   ↓
select_shape 过滤小区域
```

---

## 7. 常见陷阱与最佳实践

1. **陷阱：`median_image` 对细线特征不友好**——中值滤波把小于核尺寸的细线压缩成空心或消失。细线检测前不要用中值。
2. **陷阱：`bilateral_filter` 参数敏感**——`SigmaSpatial`/`SigmaRange` 严重依赖图像噪声类型，先用默认 `1.5, 1.5` 跑一遍。
3. **陷阱：`edges_image` 的 `Low`/`High` 阈值**——典型比例约 1:2（如 20/40），Canny 默认。低阈值小 → 多边缘（含噪）。
4. **陷阱：FFT 必须 `real` 类型**——`fft_image` 输入必须 `'real'`，否则 `convert_image_type(Image, ImageReal, 'real')`。
5. **陷阱：`affine_trans_image` 不自动调窗口**——输出图像大小由输入决定，必要时用 `affine_trans_image_size` 调整输出大小。
6. **最佳实践：滤波核大小按图像分辨率比例**——1MP 图像核 `5–7`；4MP 图像核 `7–11`；12MP 图像核 `11–15`。

---

## 8. 参数调优指南

| 算子 | 关键参数 | 推荐值 | 调整策略 |
|------|---------|--------|----------|
| `gauss_filter` | `MaskSize, Sigma` | 5, 1.0 | MaskSize 必为奇数；Sigma 大→更模糊 |
| `median_image` | `MaskType, MaskSize` | 'circle', 3 | 'circle' 各向同性最强 |
| `bilateral_filter` | `MaskSize, SigS, SigR` | 5, 1.5, 1.5 | SigR 决定边缘保留 |
| `equ_histo_image` | （无） | - | 全局均衡；局部用 `equ_histo_image_rect` |
| `emphasize` | `MaskSize, Factor` | 7, 1.0 | Factor 大→强锐化 |
| `scale_image` | `Mult, Add` | 按像素范围调 | `g' = g * Mult + Add` |
| `edges_image` | `Alpha, Low, High` | 1.0, 20, 40 | Low:High ≈ 1:2 |
| `edges_sub_pix` | `Filter, Alpha, Low, High` | 'canny', 1.0, 20, 40 | Sigma 与 `Low/High` 联动 |
| `sobel_amp` | `FilterType, Size` | 'sum_abs', 3 | 'sum_abs'/'sum_sqrt'/'abs' |
| `fft_image` | （无） | - | 输入必须 `real` 类型 |
| `texture_laws` | `Filter, Shift, Size` | 'l5s5', 2, 5 | 'l5s5' 检测斑点 |
| `affine_trans_image` | `Interpolation, AdaptSize` | 'bilinear', 'false' | 精确用 'bicubic' |
| `zoom_image_factor` | `Scale, Interpolation` | 0.5, 'constant' | 'none'/'constant' |

---

## 9. 相关分类

- **Image**：滤波的输入输出对象。
- **Morphology**：二值形态学（`opening`/`closing`）是滤波的简化版；灰度形态学（`gray_*`）与滤波部分重叠。
- **Regions**：滤波后常用 `threshold` 转 Region。
- **XLD**：亚像素边缘（`edges_sub_pix`）→ XLD 拟合（`fit_*_contour_xld`）。
- **Matching**：模板匹配（`create_shape_model`）前的滤波至关重要。

---

## 10. 学习小结

1. **Filters 是"预处理砧板"**：50% 的项目调试时间花在这里——换滤波参数、调核大小、试不同增强方法。
2. **`median_image` 是工业去噪首选**：椒盐噪声（CCD 坏点、电磁干扰）专用；高斯噪声用 `gauss_filter`；保边用 `bilateral_filter`。
3. **`edges_image` / `edges_sub_pix` 是核心入口**：Canny 边缘 + 适当 `Low/High` 阈值能解决 80% 边缘问题。
4. **FFT 解决周期性问题**：网点、莫尔条纹、纹理周期性破坏都用 FFT。
5. **滤波核大小是经验值**：按图像分辨率（1MP/5/7，4MP/7/11）粗调，再用 `emphasize` 看效果微调。