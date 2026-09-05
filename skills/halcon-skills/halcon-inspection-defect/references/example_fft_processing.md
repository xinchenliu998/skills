# Halcon FFT频域处理与纹理分析技能手册

> 学习来源: `Filters/FFT/`, `Filters/Texture/`, `Filters/Points/`
> 涵盖15个例程：FFT变换、频域滤波、纹理分析、角点检测

---

## 一、FFT处理核心算子

| 算子 | 功能 | 签名 |
|---|---|---|
| `rft_generic` | 实数FFT(正/逆) | `(Image, FFT, Direction, Norm, ResultType, Width)` |
| `fft_generic` | 复数FFT | `(Image, FFT, Direction, Exponent, Norm, Mode, Width)` |
| `fft_image` | 简化FFT | `(Image, FFT)` |
| `convol_fft` | 频域卷积 | `(ImageFFT, ImageFilter, ImageConvol)` |
| `gen_bandpass` | 生成带通滤波器 | `(ImageBandpass, Freq1, Freq2, Norm, Mode, W, H)` |
| `gen_lowpass` | 生成低通滤波器 | `(ImageLowpass, Freq, Norm, Mode, W, H)` |
| `gen_highpass` | 生成高通滤波器 | `(ImageHighpass, Freq, Norm, Mode, W, H)` |
| `gen_sin_bandpass` | 正弦带通 | `(Filter, Freq, Norm, Mode, W, H)` |
| `gen_gauss_filter` | 高斯频域滤波 | `(Filter, Sigma1, Sigma2, Phi, Norm, Mode, W, H)` |
| `optimize_rft_speed` | 优化FFT速度 | `(Width, Height, Mode)` |
| `phase_correlation_fft` | 相位相关配准 | `(Image1FFT, Image2FFT, EnergyFFT)` |
| `power_byte/power_real` | 功率谱显示 | `(FFT, PowerSpectrum)` |

---

## 二、FFT标准处理流程

```
1. read_image → 读取图像
2. optimize_rft_speed → 优化FFT速度(可选)
3. rft_generic(Image, FFT, 'to_freq', 'none', 'complex', 'fft') → 正向FFT
4. 构造滤波器:
   - gen_bandpass / gen_lowpass / gen_highpass
   - 或手动gen_gauss_filter
5. convol_fft(FFT, Filter, FilteredFFT) → 频域卷积
6. rft_generic(FilteredFFT, Result, 'from_freq', 'n', 'real', 'fft') → 逆FFT
7. threshold / dyn_threshold → 提取目标区域
```

### Direction参数
| 值 | 含义 |
|---|---|
| `'to_freq'` | 空间域→频率域(正变换) |
| `'from_freq'` | 频率域→空间域(逆变换) |

---

## 三、频域滤波器设计

### 低通滤波器（去噪/平滑）
```
gen_lowpass(Filter, CutoffFreq, 'none', 'dc_center', Width, Height)
```
- CutoffFreq: 截止频率(0~0.5), 越小越平滑

### 高通滤波器（边缘增强）
```
gen_highpass(Filter, CutoffFreq, 'none', 'dc_center', Width, Height)
```
- 保留高频=边缘

### 带通滤波器（划痕/纹理检测）⭐
```
gen_bandpass(Filter, FreqLow, FreqHigh, 'none', 'dc_center', Width, Height)
```
- 保留特定频率范围，去除低频背景和高频噪声
- ⭐周期纹理上的划痕检测

### 方向性高斯滤波器
```
gen_gauss_filter(Filter, Sigma1, Sigma2, Phi, 'none', 'dc_center', W, H)
```
- Sigma1/2: 两轴方向高斯宽度
- Phi: 方向角 → 提取特定方向纹理

---

## 四、纹理分析算子

| 算子 | 功能 | 参数 | 适用场景 |
|---|---|---|---|
| `texture_laws` | Laws纹理特征 | FilterTypes,Shift,FilterSize | 纹理分类/分割 |
| `deviation_image` | 局部标准差 | Width,Height | ⭐纹理复杂度评估 |
| `entropy_image` | 局部熵 | Width,Height | 信息量/纹理丰富度 |

### texture_laws — Laws纹理能量
```
texture_laws(Image, Result, FilterTypes, Shift, FilterSize)
```
- **FilterTypes**: `'el'`/`'es'`/`'ll'`/`'ss'`/`'le'`等 (L=Level, E=Edge, S=Spot)
- **FilterSize**: 3/5/7
- 用于纹理分类和分割

### deviation_image — 局部标准差
```
deviation_image(Image, Deviation, Width, Height)
```
- 输出每个像素邻域的标准差
- ⭐均匀表面上的缺陷检测(高标准差=异常)

---

## 五、角点/特征点检测

| 算子 | 方法 | 精度 | 速度 |
|---|---|---|---|
| `points_harris` | Harris角点 | 像素级 | 快 |
| `points_harris_binomial` | 二项式Harris | 像素级 | 更快 |
| `points_sojka` | Sojka | 像素级 | 中 |
| `critical_points_sub_pix` | 亚像素关键点 | 亚像素 | 慢 |
| `corner_response` | 角点响应图 | 像素级 | 快 |
| `dots_image` | 点检测 | 像素级 | 快 |

### points_harris
```
points_harris(Image, SigmaGrad, SigmaSmooth, Alpha, Threshold, Row, Col)
```
- **SigmaGrad**: 梯度平滑(0.7~1.5)
- **SigmaSmooth**: 响应平滑(2~5)
- **Alpha**: Harris系数(0.04)
- **Threshold**: 角点阈值(100~1000)

---

## 六、C# HalconDotNet 代码模板

### 模板1: FFT带通划痕检测 ⭐
```csharp
HObject image, fft, filter, filteredFFT, result, scratches;
HTuple width, height;

HOperatorSet.ReadImage(out image, imagePath);
HOperatorSet.GetImageSize(image, out width, out height);

// 正向FFT
HOperatorSet.RftGeneric(image, out fft, "to_freq", "none", "complex", width);

// 生成带通滤波器
HOperatorSet.GenBandpass(out filter, 0.02, 0.4, "none", "dc_center", width, height);

// 频域滤波
HOperatorSet.ConvolFft(fft, filter, out filteredFFT);

// 逆FFT
HOperatorSet.RftGeneric(filteredFFT, out result, "from_freq", "n", "real", width);

// 阈值提取划痕
HOperatorSet.Threshold(result, out scratches, 30, 255);

scratches.Dispose(); result.Dispose();
filteredFFT.Dispose(); filter.Dispose(); fft.Dispose(); image.Dispose();
```

### 模板2: 局部标准差缺陷检测
```csharp
HObject image, deviation, defects;

HOperatorSet.ReadImage(out image, imagePath);
HOperatorSet.DeviationImage(image, out deviation, 11, 11);
// 标准差高的区域=纹理异常
HOperatorSet.Threshold(deviation, out defects, 30, 255);

defects.Dispose(); deviation.Dispose(); image.Dispose();
```

### 模板3: Harris角点检测
```csharp
HObject image;
HTuple rows, cols;

HOperatorSet.ReadImage(out image, imagePath);
HOperatorSet.PointsHarris(image, 0.7, 3, 0.04, 500, out rows, out cols);
Console.WriteLine($"检测到 {rows.Length} 个角点");

image.Dispose();
```
