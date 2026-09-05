# Halcon 阈值分割与区域处理技能手册

> 学习来源: `C:\Users\Public\Documents\MVTec\HALCON-20.11-Steady\examples\hdevelop\Segmentation\`
> 涵盖18个例程，涉及阈值分割、区域生长、分水岭、地形分析

---

## 一、算子总览对比表

| 算子 | 类别 | 自动 | 速度 | 适用场景 |
|---|---|---|---|---|
| **binary_threshold** ⭐ | 全局阈值 | ✅ | 快 | 背光二值化首选(Otsu) |
| **auto_threshold** | 全局阈值 | ✅ | 中 | 多灰度层次自动分类 |
| **fast_threshold** | 全局阈值 | ❌ | 最快 | 大图快速+面积过滤 |
| **char_threshold** | 全局阈值 | ✅ | 中 | OCR字符分割 |
| **dual_threshold** | 全局阈值 | 半 | 中 | 均匀背景亮/暗缺陷 |
| **dyn_threshold** ⭐⭐ | 局部阈值 | ✅ | 中 | 光照不均匀场景 |
| **var_threshold** | 局部阈值 | ✅ | 中 | 纹理区域分割 |
| **local_threshold** | 局部阈值 | ✅ | 中 | 通用自适应分割 |
| **hysteresis_threshold** | 局部阈值 | 半 | 快 | 弱信号连续性检测 |
| **watersheds_threshold** | 分水岭 | ✅ | 中 | 控制过分割 |
| **regiongrowing** | 区域生长 | ❌ | 慢 | 灰度均匀区域 |
| **regiongrowing_n** | 区域生长 | ❌ | 慢 | 彩色图像区域 |
| **watersheds** | 分水岭 | ✅ | 中 | 粘连对象(易过分割) |
| **watersheds_marker** ⭐ | 分水岭 | 半 | 中 | 粘连分离首选 |
| **local_max** | 地形 | ✅ | 快 | 亮点/峰值检测 |
| **local_min** | 地形 | ✅ | 快 | 暗点/缺陷检测 |
| **plateaus** | 地形 | ✅ | 快 | 平坦亮区检测 |
| **saddle_points** | 地形 | ✅ | 快 | 特征点分析 |

---

## 二、分割策略选择决策树

```
开始
├─ 光照均匀？
│   ├─ 是 → 需要自动阈值？
│   │   ├─ 是 → binary_threshold ⭐(Otsu，背光检测最佳)
│   │   └─ 否 → fast_threshold(已知阈值范围)
│   └─ 否 → dyn_threshold ⭐⭐(动态阈值，光照不均首选)
├─ 多个灰度类别？
│   ├─ 是 → auto_threshold(自动多类)
│   └─ 否 → 继续↓
├─ 目标粘连？
│   ├─ 是 → watersheds_marker ⭐(标记分水岭)
│   └─ 否 → 继续↓
├─ 需要检测亮/暗点？
│   ├─ 亮点 → local_max 或 plateaus
│   ├─ 暗点 → local_min
│   └─ 两者 → dual_threshold
├─ 纹理分割？
│   ├─ 是 → var_threshold
│   └─ 否 → 继续↓
└─ 弱边缘连接？
    └─ hysteresis_threshold
```

---

## 三、各类算子详解

### A. 全局阈值（光照均匀时使用）

#### binary_threshold ⭐ Otsu自动二值化
```
binary_threshold(Image, Region, 'max_separability', 'light', UsedThreshold)
```
- **Method**: `'max_separability'`(Otsu法), `'smooth_histo'`
- **LightDark**: `'light'`提取亮区, `'dark'`提取暗区
- **⭐背光小孔检测首选**: 自动找最佳阈值分离光斑与背景

#### auto_threshold 自动多类阈值
```
auto_threshold(Image, Regions, Sigma)
```
- **Sigma**: 直方图平滑参数(4)，越大类别越少

#### fast_threshold 快速阈值
```
fast_threshold(Image, Region, MinGray, MaxGray, MinSize)
```
- 比threshold快，自带面积过滤

#### dual_threshold 双阈值
```
dual_threshold(Image, RegionCrossings, MinSize, MinGray, MaxGray)
```
- 检测比均值偏亮/偏暗的区域

### B. 局部/自适应阈值（光照不均时使用）

#### dyn_threshold ⭐⭐ 动态阈值
```
mean_image(Image, MeanImage, 25, 25)   // 先生成平滑参考图
dyn_threshold(Image, MeanImage, Region, 15, 'light')
```
- **Offset**: 灰度差阈值(15)
- **关键**: 必须先生成参考图(mean_image/gauss_filter)
- **⭐光照不均匀场景首选**

#### var_threshold 方差阈值
```
var_threshold(Image, Region, MaskWidth, MaskHeight, StdDevScale, AbsThreshold, 'light')
```
- 基于局部均值±标准差×缩放因子

#### hysteresis_threshold 滞后阈值
```
hysteresis_threshold(Image, Region, Low, High, MaxLength)
```
- 高阈值种子+低阈值扩展

### C. 区域分割

#### regiongrowing 灰度区域生长
```
regiongrowing(Image, Regions, 1, 1, Tolerance, MinSize)
```
- **Tolerance**: 灰度差容忍度(2)

#### watersheds_marker ⭐ 标记分水岭
```
// 1.先获取种子(如二值化+腐蚀)
// 2.计算梯度图
// 3.标记分水岭
watersheds_marker(GradientImage, Markers, Basins)
```

### D. 地形算子（点/区域特征检测）
```
local_max(Image, LocalMaxima)     -- 亮峰
local_min(Image, LocalMinima)     -- 暗谷
plateaus(Image, Plateaus)         -- 平坦亮区
saddle_points(Image, SaddlePoints) -- 鞍点
```

---

## 四、参数调优指南

### binary_threshold
- `Method='max_separability'`(Otsu)是默认最佳选择
- `LightDark`根据目标是亮是暗选择

### dyn_threshold
| Offset值 | 效果 | 场景 |
|---|---|---|
| 5~10 | 低差异也检出 | 弱对比度目标 |
| 15~25 | 平衡 | 一般工业场景 |
| 30~50 | 只检高对比 | 强边缘/高对比 |

平滑核大小建议：目标尺寸的2~3倍

### var_threshold
- `MaskWidth/Height`: 应覆盖目标+部分背景
- `StdDevScale`: 0.2~2.0，越大越严格
- `AbsThreshold`: 绝对灰度差下限

### regiongrowing
- `Tolerance`: 越小区域越细碎，越大区域越合并
- 建议先中值滤波平滑

---

## 五、C# HalconDotNet 代码模板

### 模板1: 背光小孔检测（binary_threshold）⭐
```csharp
HObject image, region, connectedRegions;
HTuple usedThreshold;

HOperatorSet.ReadImage(out image, "backlit_holes.png");
// Otsu自动二值化，提取亮光斑
HOperatorSet.BinaryThreshold(image, out region, "max_separability", "light", out usedThreshold);
Console.WriteLine($"自动阈值: {usedThreshold.D}");
// 分离各个独立光斑
HOperatorSet.Connection(region, out connectedRegions);
// 统计数量
HTuple count;
HOperatorSet.CountObj(connectedRegions, out count);
Console.WriteLine($"检测到光斑数: {count.I}");

connectedRegions.Dispose();
region.Dispose();
image.Dispose();
```

### 模板2: 光照不均匀场景（dyn_threshold）⭐⭐
```csharp
HObject image, meanImage, region;

HOperatorSet.ReadImage(out image, "uneven_light.png");
// 生成平滑参考图
HOperatorSet.MeanImage(image, out meanImage, 25, 25);
// 动态阈值：比参考图亮15以上的区域
HOperatorSet.DynThreshold(image, meanImage, out region, 15, "light");
// 分离连通域
HObject connected;
HOperatorSet.Connection(region, out connected);

connected.Dispose();
region.Dispose();
meanImage.Dispose();
image.Dispose();
```

### 模板3: 粘连目标分离（watersheds_marker）
```csharp
HObject image, region, distImage, markers, basins;

HOperatorSet.ReadImage(out image, "touching_objects.png");
// 二值化
HOperatorSet.BinaryThreshold(image, out region, "max_separability", "light", out _);
// 距离变换
HOperatorSet.DistanceTransform(region, out distImage, "city-block", "foreground", 0, 0);
// 局部最大值作为种子
HOperatorSet.LocalMax(distImage, out markers);
// 标记分水岭
HOperatorSet.WatershedsMarker(distImage, markers, out basins);

basins.Dispose();
markers.Dispose();
distImage.Dispose();
region.Dispose();
image.Dispose();
```

### 模板4: 亮点检测（local_max）
```csharp
HObject image, smoothed, maxRegions;

HOperatorSet.ReadImage(out image, "spots.png");
// 先平滑减少噪声
HOperatorSet.GaussFilter(image, out smoothed, 5);
// 提取局部最大值
HOperatorSet.LocalMax(smoothed, out maxRegions);

maxRegions.Dispose();
smoothed.Dispose();
image.Dispose();
```

---

## 六、背光小孔杂光检测应用建议

针对圆形模组背光小孔检测场景：

1. **首选 `binary_threshold`**: Otsu自动分割光斑区域
2. **光照不均时用 `dyn_threshold`**: 如果背光不完全均匀
3. **`connection` 分离各个光斑**: 获取独立区域后逐个分析
4. **结合 Task10 区域特征**: 用 circularity/compactness 判断形状规则性
5. **`local_max` 辅助定位**: 快速找到光斑中心位置
