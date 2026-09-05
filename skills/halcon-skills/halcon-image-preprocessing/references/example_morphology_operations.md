# Halcon 形态学处理技能手册

> 学习来源: `Morphology/Gray-Values/`, `Morphology/Region/`, `Filters/Misc/`
> 涵盖18个例程：灰度形态学、区域形态学、骨架化、PCB检测案例

---

## 一、形态学基础四操作

| 操作 | 定义 | 灰度效果 | 区域效果 | 典型用途 |
|---|---|---|---|---|
| **腐蚀(Erosion)** | 局部最小值 | 暗化、缩小亮区 | 缩小区域 | 去除小亮噪点 |
| **膨胀(Dilation)** | 局部最大值 | 亮化、扩大亮区 | 扩大区域 | 填补小暗孔 |
| **开运算(Opening)** | 先腐蚀后膨胀 | 去除亮噪声/小突起 | 平滑边缘、分离粘连 | ⭐去噪+分离 |
| **闭运算(Closing)** | 先膨胀后腐蚀 | 填补暗凹陷/小孔 | 填充缺口、连接断裂 | ⭐填孔+连接 |

---

## 二、灰度形态学算子

### 矩形结构元素（_rect）
| 算子 | 签名 | 参数 |
|---|---|---|
| `gray_erosion_rect` | `(Image, ImageMin, MaskH, MaskW)` | MaskH/W: 矩形大小 |
| `gray_dilation_rect` | `(Image, ImageMax, MaskH, MaskW)` | 同上 |
| `gray_opening_rect` | `(Image, ImageOpening, MaskH, MaskW)` | 同上 |
| `gray_closing_rect` | `(Image, ImageClosing, MaskH, MaskW)` | 同上 |

### 形状结构元素（_shape）⭐更灵活
| 算子 | 签名 | 参数 |
|---|---|---|
| `gray_erosion_shape` | `(Image, ImageMin, MaskH, MaskW, Shape)` | Shape: `'octagon'`/`'diamond'`/`'rhombus'` |
| `gray_dilation_shape` | `(Image, ImageMax, MaskH, MaskW, Shape)` | 同上 |
| `gray_opening_shape` | `(Image, ImageOpening, MaskH, MaskW, Shape)` | 同上 |
| `gray_closing_shape` | `(Image, ImageClosing, MaskH, MaskW, Shape)` | 同上 |

### 结构元素选择指南
| 形状 | 参数 | 适用场景 |
|---|---|---|
| `矩形(rect)` | MaskH, MaskW | 方形/矩形特征、快速处理 |
| `'octagon'` | MaskH, MaskW, Shape | ⭐通用首选，近似圆形 |
| `'diamond'` | 同上 | 菱形特征 |
| `'rhombus'` | 同上 | 同diamond |

**Mask大小选择**: 应略大于要去除的噪声、略小于要保留的目标

---

## 三、区域形态学算子

| 算子 | 功能 | 用途 |
|---|---|---|
| `opening_circle(R, Opened, Radius)` | 圆形开运算 | 分离粘连圆形目标 |
| `closing_circle(R, Closed, Radius)` | 圆形闭运算 | 填补区域缺口 |
| `erosion_circle(R, Eroded, Radius)` | 圆形腐蚀 | 缩小区域 |
| `dilation_circle(R, Dilated, Radius)` | 圆形膨胀 | 扩大区域 |
| `fill_up(R, Filled)` | 填充内部孔洞 | 获取实心区域 |

---

## 四、高级形态学

### gray_skeleton — 灰度骨架
- **算子:** `gray_skeleton(Image, GraySkeleton)`
- 提取灰度图像的骨架（脊线）
- 适用: 线状结构提取、纹理分析

### topographic_sketch — 地形草图
- **算子:** `topographic_sketch(Image, Sketch)`
- 基于地形分析提取图像的关键结构
- 适用: 图像简化、特征提取

---

## 五、工业应用案例

### 案例1: PCB缺陷检测 ⭐
```
流程:
1. 读取PCB图像
2. gray_opening_shape(7,7,'octagon') → 去除小亮缺陷
3. gray_closing_shape(7,7,'octagon') → 填补小暗缺陷
4. dyn_threshold(Opening, Closing, 75, 'not_equal') → 差异区=缺陷
```
**原理**: 开运算消除亮缺陷，闭运算消除暗缺陷。两者差异大的区域=缺陷

### 案例2: 颗粒计数（分离粘连）
```
流程:
1. threshold → 二值化
2. opening_circle(Region, 3.5) → 分离粘连颗粒
3. connection → 连通域分离
4. select_shape('area') → 面积过滤
5. count_obj → 计数
```

---

## 六、形态学策略决策树

```
目标
├─ 去除噪声？
│   ├─ 亮噪声(小亮点) → 开运算(opening)
│   └─ 暗噪声(小暗点) → 闭运算(closing)
├─ 分离粘连目标？
│   └─ opening_circle(半径略小于目标间距)
├─ 填补区域缺口？
│   └─ closing_circle(半径略大于缺口)
├─ 灰度图缺陷检测？
│   └─ opening vs closing + dyn_threshold(PCB方法)
├─ 结构元素选择？
│   ├─ 目标是圆形 → circle/octagon
│   ├─ 目标是矩形 → rect
│   └─ 通用 → octagon ⭐
└─ 灰度形态学 vs 区域形态学？
    ├─ 直接在灰度图上处理 → gray_xxx (保留灰度信息)
    └─ 已有二值区域 → opening/closing_circle (更快)
```

---

## 七、C# HalconDotNet 代码模板

### 模板1: 背光小孔检测预处理（开闭运算清理）⭐
```csharp
HObject image, opened, closed, cleaned;

HOperatorSet.ReadImage(out image, imagePath);
// 开运算去除小亮噪点
HOperatorSet.GrayOpeningShape(image, out opened, 5, 5, "octagon");
// 闭运算填补小暗孔
HOperatorSet.GrayClosingShape(opened, out closed, 5, 5, "octagon");

closed.Dispose();
opened.Dispose();
image.Dispose();
```

### 模板2: PCB式缺陷检测
```csharp
HObject image, imgOpening, imgClosing, defects;

HOperatorSet.ReadImage(out image, imagePath);
HOperatorSet.GrayOpeningShape(image, out imgOpening, 7, 7, "octagon");
HOperatorSet.GrayClosingShape(image, out imgClosing, 7, 7, "octagon");
// 差异检测：开闭差异大的区域=缺陷
HOperatorSet.DynThreshold(imgOpening, imgClosing, out defects, 75, "not_equal");

HTuple area, row, col;
HOperatorSet.AreaCenter(defects, out area, out row, out col);
Console.WriteLine($"缺陷面积: {area.I}");

defects.Dispose();
imgClosing.Dispose();
imgOpening.Dispose();
image.Dispose();
```

### 模板3: 粘连目标分离计数
```csharp
HObject image, region, opened, connected, selected;
HTuple count;

HOperatorSet.ReadImage(out image, imagePath);
HOperatorSet.BinaryThreshold(image, out region, "max_separability", "light", out _);
// 开运算分离粘连
HOperatorSet.OpeningCircle(region, out opened, 3.5);
HOperatorSet.Connection(opened, out connected);
// 面积过滤
HOperatorSet.SelectShape(connected, out selected, "area", "and", 100, 99999);
HOperatorSet.CountObj(selected, out count);
Console.WriteLine($"目标数: {count.I}");

selected.Dispose();
connected.Dispose();
opened.Dispose();
region.Dispose();
image.Dispose();
```

### 模板4: 区域清理流水线
```csharp
// 标准区域清理流程：填孔 → 开运算 → 闭运算
HObject region, filled, opened, closed;

HOperatorSet.FillUp(rawRegion, out filled);           // 填内部孔洞
HOperatorSet.OpeningCircle(filled, out opened, 2.5);  // 去毛刺
HOperatorSet.ClosingCircle(opened, out closed, 3.0);  // 补缺口

closed.Dispose();
opened.Dispose();
filled.Dispose();
```

---

## 八、背光杂光检测中的形态学应用

1. **预处理**: `gray_opening_shape` 去除背景小亮噪点
2. **二值化后清理**: `opening_circle` 分离粘连光斑 + `fill_up` 填充
3. **缺陷检测辅助**: 开闭差异法可检测异常灰度区域
4. **结构元素大小**: 根据小孔直径选择，通常为孔径的1/3~1/2
