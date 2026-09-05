# Halcon 图像增强与预处理技能手册

> 学习来源: `Filters/Enhancement/`, `Filters/Arithmetic/`, `Filters/Color/`, `Applications/General/`
> 涵盖20个例程：对比度增强、光照校正、图像算术、颜色空间

---

## 一、增强算子总览对比表

| 算子 | 自动 | 参数 | 速度 | 适用场景 |
|---|---|---|---|---|
| **emphasize** ⭐ | 半 | MaskW/H, Factor | 快 | ⭐局部对比度增强、锐化 |
| **equ_histo_image** | ✅ | 无 | 最快 | 全局对比度均衡 |
| **illuminate** ⭐ | 半 | MaskW/H, Factor | 快 | ⭐光照不均匀校正 |
| **scale_image_max** | ✅ | 无 | 最快 | 灰度拉伸到0-255 |
| **shock_filter** | ❌ | Alpha,Theta,Iter | 慢 | 边缘锐化+平滑 |
| **mean_curvature_flow** | ❌ | Sigma,Theta,Iter | 慢 | 保边平滑 |
| **coherence_enhancing_diff** | ❌ | Sigma,Rho,Theta,Iter | 慢 | 纹理增强 |
| **sub_image** | ❌ | Mult,Add | 快 | 图像差分/背景减除 |
| **add_image** | ❌ | Mult1,Mult2,Add | 快 | 图像叠加/亮度调整 |

---

## 二、核心增强算子详解

### emphasize ⭐ 局部对比度增强（非锐化掩模）
```
emphasize(Image, Enhanced, MaskWidth, MaskHeight, Factor)
```
- **MaskW/H**: 平滑窗口大小(7), 越大越平滑
- **Factor**: 增强系数(1.5), >1增强, =1无效果
- **原理**: 放大原图与平滑图的差异 → 增强细节
- **⭐背光检测用途**: 增强小孔光斑的边缘清晰度

### equ_histo_image — 直方图均衡化
```
equ_histo_image(Image, Equalized)
```
- 无参数，全自动
- 将灰度重新分布到0-255全范围
- 适用: 低对比度图像快速增强

### illuminate ⭐ 光照校正
```
illuminate(Image, Corrected, MaskWidth, MaskHeight, Factor)
```
- **MaskW/H**: 窗口大小(51,51), 应大于光照变化周期
- **Factor**: 校正强度(0.7)
- **原理**: 估算背景光照分布并消除
- **⭐背光检测**: 消除背光不均匀性

### scale_image_max — 灰度拉伸
```
scale_image_max(Image, Scaled)
```
- 无参数，自动将灰度映射到0-255

### shock_filter — 冲击滤波锐化
```
shock_filter(Image, Sharpened, Alpha, Theta, Iterations)
```
- **Alpha**: 扩散系数(0.5)
- **Theta**: 时间步长
- **Iterations**: 迭代次数(10)

### sub_image — 图像减法（背景减除）⭐
```
sub_image(Image1, Image2, Result, Mult, Add)
```
- Result = (Image1 - Image2) * Mult + Add
- **⭐背景减除**: 参考图减去当前图 → 差异=缺陷

### add_image — 图像加法
```
add_image(Image1, Image2, Result, Mult1, Mult2, Add)
```
- Result = Image1*Mult1 + Image2*Mult2 + Add

---

## 三、增强策略决策树

```
图像质量问题
├─ 对比度太低(灰暗)？
│   ├─ 全局低对比度 → equ_histo_image 或 scale_image_max
│   └─ 局部细节不清 → emphasize ⭐(Factor=1.5~3.0)
├─ 光照不均匀？
│   ├─ 渐变背景 → illuminate ⭐(大窗口)
│   └─ 已有参考图 → sub_image(背景减除)
├─ 图像模糊？
│   ├─ 轻微模糊 → emphasize(Factor=2.0+)
│   └─ 严重模糊 → shock_filter
├─ 需要背景减除？
│   └─ sub_image(当前图 - 参考图)
└─ 背光小孔场景？
    └─ illuminate → emphasize → binary_threshold
```

---

## 四、参数调优指南

### emphasize
| Factor | 效果 | 场景 |
|---|---|---|
| 1.0~1.5 | 轻微增强 | 清晰图像微调 |
| 1.5~3.0 | 中等增强 | ⭐一般工业场景 |
| 3.0~5.0 | 强增强 | 低对比度/模糊图像 |

MaskW/H建议: 目标特征尺寸的1~2倍

### illuminate
| MaskW/H | 效果 | 场景 |
|---|---|---|
| 21~31 | 局部校正 | 小范围光照变化 |
| 51~101 | 中等校正 | ⭐一般渐晕 |
| 151~301 | 全局校正 | 大面积光照渐变 |

---

## 五、C# HalconDotNet 代码模板

### 模板1: 背光小孔检测预增强 ⭐
```csharp
HObject image, corrected, enhanced;

HOperatorSet.ReadImage(out image, imagePath);
// 1. 光照校正
HOperatorSet.Illuminate(image, out corrected, 51, 51, 0.7);
// 2. 局部对比度增强
HOperatorSet.Emphasize(corrected, out enhanced, 7, 7, 2.0);
// 3. 后续接阈值分割...

enhanced.Dispose();
corrected.Dispose();
image.Dispose();
```

### 模板2: 全局对比度增强
```csharp
HObject image, enhanced;

HOperatorSet.ReadImage(out image, imagePath);
// 方法1: 直方图均衡化
HOperatorSet.EquHistoImage(image, out enhanced);
// 方法2: 灰度拉伸
// HOperatorSet.ScaleImageMax(image, out enhanced);

enhanced.Dispose();
image.Dispose();
```

### 模板3: 背景减除缺陷检测
```csharp
HObject image, reference, diff, defects;

HOperatorSet.ReadImage(out image, imagePath);
HOperatorSet.ReadImage(out reference, refPath);
// 差分：参考图-当前图
HOperatorSet.SubImage(reference, image, out diff, 1, 128);
// 阈值提取差异区域
HOperatorSet.Threshold(diff, out defects, 148, 255);

defects.Dispose();
diff.Dispose();
reference.Dispose();
image.Dispose();
```

### 模板4: 完整预处理流水线
```csharp
// 标准预处理: 光照校正 → 增强 → 二值化 → 形态学清理
HObject img, corrected, enhanced, region, cleaned;

HOperatorSet.ReadImage(out img, path);
HOperatorSet.Illuminate(img, out corrected, 51, 51, 0.7);
HOperatorSet.Emphasize(corrected, out enhanced, 7, 7, 2.0);
HOperatorSet.BinaryThreshold(enhanced, out region, "max_separability", "light", out _);
HOperatorSet.OpeningCircle(region, out cleaned, 2.5);

cleaned.Dispose(); region.Dispose();
enhanced.Dispose(); corrected.Dispose(); img.Dispose();
```
