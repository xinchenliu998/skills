# Halcon 完整性检查技能手册

> 学习来源: `Applications/Completeness-Check/`, `Applications/Position-Recognition/`
> 涵盖Task17：产品完整性检测、缺件检测、位置识别

---

## 一、完整性检查方法对比

| 方法 | 原理 | 速度 | 适用 |
|---|---|---|---|
| **Blob分析** ⭐ | 阈值→连通→计数/特征 | 最快 | ⭐简单计数/缺件检测 |
| **形状匹配定位** | 模板匹配→位置 | 快 | 有固定模板的检测 |
| **差分检测** | 标准图-待检图 | 中 | 与标准品比对 |
| **区域特征** | 面积/圆度/长宽比 | 快 | 零件属性判断 |

---

## 二、标准完整性检查流程 ⭐

```
1. 图像预处理(增强/去噪)
2. 定位基准(形状匹配/特征点)
3. 仿射变换对齐(消除位移/旋转)
4. ROI区域检查:
   a. 阈值分割 → 连通域
   b. 特征筛选(面积/形状)
   c. 计数/比较
5. 判定OK/NG
```

### 核心模式

#### 模式1: 计数检测
```
Threshold → Connection → CountObj → 比较期望数量
```

#### 模式2: 面积检测
```
Threshold → RegionArea → 比较面积范围
```

#### 模式3: 位置检测
```
ShapeMatch定位 → 检查各ROI中目标是否存在
```

---

## 三、对齐与定位

### 基于形状匹配的对齐
```
1. CreateShapeModel(模板) → ModelID
2. FindShapeModel(待检图) → Row, Col, Angle
3. HomMat2dIdentity → HomMat2dRotate(Angle) → HomMat2dTranslate(Row,Col)
4. AffineTransImage → 对齐图像
5. 在对齐图像上做ROI检查
```

### 基于区域重心的简易对齐
```
1. Threshold → 找主体区域
2. AreaCenter → 获取重心(Row, Col)
3. 以重心为基准定义各ROI偏移
```

---

## 四、C# HalconDotNet 代码模板

### 模板1: 元件计数检测 ⭐
```csharp
HObject image, region, connected, selected;
HTuple count;

HOperatorSet.ReadImage(out image, imagePath);
// 阈值分割
HOperatorSet.Threshold(image, out region, 0, 128);
HOperatorSet.Connection(region, out connected);
// 按面积筛选有效目标
HOperatorSet.SelectShape(connected, out selected, "area", "and", 500, 99999);
HOperatorSet.CountObj(selected, out count);

int expectedCount = 10;
bool isOK = count.I == expectedCount;
Console.WriteLine($"检测到 {count.I} 个元件, 期望 {expectedCount}, 结果: {(isOK ? "OK" : "NG")}");

selected.Dispose(); connected.Dispose(); region.Dispose(); image.Dispose();
```

### 模板2: 多ROI区域逐一检查
```csharp
// 预定义各检查区域的ROI
double[][] roiList = {
    new double[]{100, 200, 150, 250}, // ROI1: r1,c1,r2,c2
    new double[]{300, 400, 350, 450}, // ROI2
};

bool allOK = true;
foreach (var roi in roiList)
{
    HObject roiRegion, reduced, thresh;
    HOperatorSet.GenRectangle1(out roiRegion, roi[0], roi[1], roi[2], roi[3]);
    HOperatorSet.ReduceDomain(image, roiRegion, out reduced);
    HOperatorSet.Threshold(reduced, out thresh, 0, 128);
    
    HTuple area, row, col;
    HOperatorSet.AreaCenter(thresh, out area, out row, out col);
    
    if (area.I < 100) { allOK = false; Console.WriteLine($"ROI缺件!"); }
    
    thresh.Dispose(); reduced.Dispose(); roiRegion.Dispose();
}
Console.WriteLine($"最终结果: {(allOK ? "OK" : "NG")}");
```

### 模板3: 差分检测
```csharp
HObject refImage, testImage, diffImage, defects;

HOperatorSet.ReadImage(out refImage, refPath);
HOperatorSet.ReadImage(out testImage, testPath);
// 差分
HOperatorSet.AbsDiffImage(refImage, testImage, out diffImage, 1);
// 阈值提取差异区域
HOperatorSet.Threshold(diffImage, out defects, 30, 255);

HTuple area, r, c;
HOperatorSet.AreaCenter(defects, out area, out r, out c);
Console.WriteLine($"差异面积: {area.I}px, {(area.I > 500 ? "NG" : "OK")}");

defects.Dispose(); diffImage.Dispose(); testImage.Dispose(); refImage.Dispose();
```
