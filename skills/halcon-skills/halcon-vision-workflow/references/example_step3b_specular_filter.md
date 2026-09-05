# Step 3b: 镜面反光(Specular)边缘过滤策略

## 职责
检测并过滤因镜头/玻璃表面反光（Specular Reflection）产生的异常高亮区域及其边缘，为后续Step4(Edge策略)提供"干净"的边缘集合。

## 问题背景
镜头类模组（如摄像头模组、光学元件）表面常因环境光或拍摄光源产生**镜面反光光斑**（Specular Highlight），其特征：
- 灰度值极高（接近或达到饱和255）
- 形状不规则，通常为椭圆形或不定形
- 位置随光源角度变化，**不具有结构特征**
- 产生强烈的灰度梯度，导致边缘检测器将其检测为"假边缘"
- 这些假边缘会严重干扰矩形拟合、圆拟合等几何策略的精度

### 典型失效案例
```
实际中心: (1855.02, 1527.64)  ← 人工标定
策略结果: (1852.00, 1567.00)  ← Edge策略(被光斑干扰)
偏差: ΔRow≈39.4px (主要在Y方向)
原因: 光斑在镜头下半区域产生假边缘，拉偏了矩形拟合中心
```

## 前置条件
- Step 0 已完成（有ImageROI）
- Step 3 已完成（有区域重心参考）
- 在Step 4之前执行

## 输入
| 字段 | 来源 | 说明 |
|------|------|------|
| ImageROI | Step 0 | ReduceDomain后的ROI图像 |
| ROI信息 | Step 0 | Row1/Col1/Row2/Col2, Area, Diagonal等 |
| ValidModes | Step 0 | 有效阈值模式列表 |

## 输出
| 字段 | 类型 | 说明 |
|------|------|------|
| SpecularDetected | bool | 是否检测到镜面反光 |
| SpecularRegion | HObject | 反光区域（用于掩膜） |
| SpecularCount | int | 反光区域数量 |
| SpecularAreaRatio | double | 反光区域占ROI面积的比例 |
| CleanImageROI | HObject | 去除反光区域后的ROI图像(用于后续Edge) |
| SpecularEdgeCount | int | 被过滤掉的光斑边缘数 |
| SelfCheck | enum | PASS / WARN / FAIL |
| SelfCheckReason | string | 说明 |

## 算法流程

### Phase 1: 高亮区域检测（Specular Region Detection）

```csharp
// === Phase 1: 检测高亮饱和区域 ===
Console.WriteLine("=== Step 3b: 镜面反光过滤 ===");

bool specularDetected = false;
HObject ho_SpecularRegion = null;
HObject ho_CleanImageROI = null;
int specularCount = 0;
double specularAreaRatio = 0;

// 方法1: 固定高阈值检测近饱和区域
// 镜面反光的核心特征：灰度值极高，接近或达到饱和(255)
HOperatorSet.Threshold(ho_ImageROI, out HObject ho_Bright, 230, 255);
HOperatorSet.Connection(ho_Bright, out HObject ho_BrightConn);

// 过滤噪点级的小高亮（面积太小的不是光斑）
double minSpecularArea = roiArea * 0.001; // 至少占ROI面积0.1%
HOperatorSet.SelectShape(ho_BrightConn, out HObject ho_SpecularCand, 
    "area", "and", minSpecularArea, roiArea * 0.3);
HOperatorSet.CountObj(ho_SpecularCand, out HTuple specCnt);

Console.WriteLine($"  高亮区域(>230): {specCnt.I}个 (最小面积阈值: {minSpecularArea:F0})");

ho_Bright.Dispose();
ho_BrightConn.Dispose();
```

### Phase 2: 光斑验证与聚类分析

```csharp
// === Phase 2: 验证是否为真正的镜面反光 ===
// 光斑特征验证：形状紧凑性、灰度梯度、位置分布

if (specCnt.I > 0)
{
    // 2.1 膨胀光斑区域（光斑边缘附近的边缘也不可信）
    double dilateRadius = Math.Max(5, roiDiagonal * 0.01); // 至少5px，或对角线1%
    HOperatorSet.DilationCircle(ho_SpecularCand, out HObject ho_SpecularDilated, dilateRadius);
    HOperatorSet.Union1(ho_SpecularDilated, out ho_SpecularRegion);
    
    // 2.2 计算光斑总面积占比
    HOperatorSet.AreaCenter(ho_SpecularRegion, out HTuple specArea, out _, out _);
    specularAreaRatio = specArea.D / roiArea;
    specularCount = specCnt.I;
    
    Console.WriteLine($"  光斑区域(膨胀后): 面积占比={specularAreaRatio:P2}, 膨胀半径={dilateRadius:F1}px");
    
    // 2.3 验证：检查每个光斑的灰度均值是否确实很高
    int confirmedCount = 0;
    for (int i = 1; i <= specCnt.I; i++)
    {
        HOperatorSet.SelectObj(ho_SpecularCand, out HObject ho_Spec, i);
        HOperatorSet.Intensity(ho_Spec, ho_ImageROI, out HTuple meanVal, out HTuple devVal);
        HOperatorSet.AreaCenter(ho_Spec, out HTuple sa, out HTuple sr, out HTuple sc);
        
        // 光斑确认条件：均值>220 且 标准差<30（光斑内部灰度比较均匀）
        bool isSpecular = meanVal.D > 220 && devVal.D < 30;
        if (isSpecular) confirmedCount++;
        
        Console.WriteLine($"    光斑{i}: 位置=({sr.D:F1},{sc.D:F1}), 面积={sa.I}, " +
                         $"均值={meanVal.D:F1}, 标准差={devVal.D:F1} → {(isSpecular ? "确认" : "排除")}");
        ho_Spec.Dispose();
    }
    
    specularDetected = confirmedCount > 0;
    Console.WriteLine($"  确认光斑: {confirmedCount}/{specCnt.I}个");
    
    ho_SpecularDilated.Dispose();
}
```

### Phase 3: 边缘聚类与过滤

```csharp
// === Phase 3: 基于光斑掩膜的边缘过滤 ===
if (specularDetected && ho_SpecularRegion != null)
{
    // 3.1 创建"干净"的ROI：原ROI减去光斑区域
    HOperatorSet.Difference(ho_ROI, ho_SpecularRegion, out HObject ho_CleanROI);
    HOperatorSet.ReduceDomain(ho_Image, ho_CleanROI, out ho_CleanImageROI);
    
    // 3.2 验证：在干净区域做边缘检测，对比过滤前后
    HOperatorSet.Emphasize(ho_ImageROI, out HObject ho_EnhOrig, 7, 7, 1.5);
    HOperatorSet.EdgesSubPix(ho_EnhOrig, out HObject ho_EdgesOrig, "canny", 1.5, 15, 35);
    double eMinLen = Math.Min(roiHeight, roiWidth) * 0.2;
    HOperatorSet.SelectShapeXld(ho_EdgesOrig, out HObject ho_EdgesOrigF, "contlength", "and", eMinLen, 99999);
    HOperatorSet.CountObj(ho_EdgesOrigF, out HTuple origCount);
    
    HOperatorSet.Emphasize(ho_CleanImageROI, out HObject ho_EnhClean, 7, 7, 1.5);
    HOperatorSet.EdgesSubPix(ho_EnhClean, out HObject ho_EdgesClean, "canny", 1.5, 15, 35);
    HOperatorSet.SelectShapeXld(ho_EdgesClean, out HObject ho_EdgesCleanF, "contlength", "and", eMinLen, 99999);
    HOperatorSet.CountObj(ho_EdgesCleanF, out HTuple cleanCount);
    
    int filteredEdgeCount = origCount.I - cleanCount.I;
    Console.WriteLine($"  边缘过滤: 原始{origCount.I}条 → 过滤后{cleanCount.I}条, 去除{filteredEdgeCount}条光斑边缘");
    
    ho_EnhOrig.Dispose(); ho_EdgesOrig.Dispose(); ho_EdgesOrigF.Dispose();
    ho_EnhClean.Dispose(); ho_EdgesClean.Dispose(); ho_EdgesCleanF.Dispose();
    ho_CleanROI.Dispose();
}
else
{
    // 无光斑，CleanImageROI就是原始ImageROI
    ho_CleanImageROI = ho_ImageROI; // 直接引用，不Dispose
    Console.WriteLine("  未检测到镜面反光，使用原始ROI图像");
}
```

### Phase 4: 补充检测 — 灰度梯度聚类法

当Phase 1的简单阈值不够时，使用梯度分析来发现"灰度急变区域"：

```csharp
// === Phase 4(可选): 灰度梯度聚类辅助检测 ===
// 当光斑灰度不到230但仍产生局部亮区时使用
if (!specularDetected)
{
    // 计算局部灰度均值图
    HOperatorSet.MeanImage(ho_ImageROI, out HObject ho_Mean, 31, 31);
    
    // 提取"比局部均值亮很多"的区域
    HOperatorSet.DynThreshold(ho_ImageROI, ho_Mean, out HObject ho_DynBright, 30, "light");
    HOperatorSet.Connection(ho_DynBright, out HObject ho_DynConn);
    HOperatorSet.SelectShape(ho_DynConn, out HObject ho_DynSel, "area", "and", 
        minSpecularArea, roiArea * 0.2);
    HOperatorSet.CountObj(ho_DynSel, out HTuple dynCnt);
    
    if (dynCnt.I > 0)
    {
        Console.WriteLine($"  梯度聚类法检测到 {dynCnt.I} 个局部异常亮区");
        // 使用与Phase 2同样的验证逻辑...
    }
    
    ho_Mean.Dispose(); ho_DynBright.Dispose(); ho_DynConn.Dispose(); ho_DynSel.Dispose();
}
```

## 自反思规则（Step 3b 内部）

### 检查1: 光斑覆盖面积
```
IF specularAreaRatio > 0.3:
    → SelfCheck = FAIL
    → 原因: "光斑面积过大(>30%)，可能是整体过曝而非局部反光"
    → CleanImageROI可能丢失太多信息

IF specularAreaRatio > 0.15:
    → SelfCheck = WARN
    → 原因: "光斑面积较大(>15%)，过滤后信息可能不足"
```

### 检查2: 光斑位置是否偏向一侧
```
IF 所有光斑中心Row的均值偏离ROI中心超过ROI高度*0.3:
    → SelfCheck = WARN
    → 原因: "光斑偏向ROI一侧，可能导致边缘过滤不对称"
    → 记录偏向方向，供Step 5参考
```

### 检查3: 无光斑时的状态
```
IF specularDetected == false:
    → SelfCheck = PASS
    → 原因: "无镜面反光检测，边缘可直接使用"
    → CleanImageROI == ImageROI
```

### 检查4: 过滤后剩余边缘数量
```
IF filteredEdgeCount / origEdgeCount > 0.5:
    → SelfCheck = WARN
    → 原因: "过滤掉超过50%的边缘，可能过度过滤"
```

### 综合判定
```
无光斑 → PASS
有光斑 + 面积合理(<15%) + 过滤后边缘充足 → PASS
有光斑 + 面积较大(15%~30%) 或 位置偏侧 → WARN
有光斑 + 面积过大(>30%) 或 过滤后边缘不足 → FAIL
```

## 关键参数一览

| 参数 | 默认值 | 说明 |
|------|--------|------|
| 高亮阈值 | 230 | 灰度>230视为潜在光斑 |
| 最小光斑面积 | ROI面积 * 0.001 | 太小的高亮点是噪点 |
| 最大光斑面积 | ROI面积 * 0.3 | 太大说明是整体过曝 |
| 光斑膨胀半径 | max(5, 对角线*0.01) | 光斑边缘附近也不可信 |
| 光斑均值确认阈值 | >220 | 灰度均值需>220才确认为光斑 |
| 光斑标准差上限 | <30 | 光斑内部灰度应较均匀 |
| 动态阈值偏移 | 30 | DynThreshold的Offset参数 |

## 与其他Step的关系

```
Step 0 (预处理)
  ↓ ImageROI
Step 3b (镜面反光过滤) ← 本文件
  ↓ CleanImageROI (或原始ImageROI如无光斑)
  ↓ SpecularDetected, SpecularRegion
Step 4 (Edge策略) ← 使用CleanImageROI而非ImageROI
  ↓
Step 5 (全局反思) ← 参考SpecularDetected进行置信度调整
```

## 对Step 4的影响
当 `SpecularDetected == true` 时，Step 4应该：
1. 使用 `CleanImageROI` 替代 `ImageROI` 做边缘检测
2. 在方法2(整体包围)中，排除光斑区域的轮廓
3. 对覆盖度计算使用 `CleanROI面积` 而非 `原ROI面积`

## 对Step 5的影响
当 `SpecularDetected == true` 时，Step 5应该：
1. 记录 `光斑检测: 已检测到{N}个光斑, 面积占比{ratio}`
2. 如果Edge策略使用了CleanImageROI，置信度可加分（已排除干扰）
3. 如果光斑偏向一侧且Edge结果也偏向对侧，标记为 WARN

## 输出格式
```
=== Step 3b: 镜面反光过滤 ===
  高亮区域(>230): N个 (最小面积阈值: xxx)
  光斑区域(膨胀后): 面积占比=x.xx%, 膨胀半径=x.xpx
    光斑1: 位置=(r,c), 面积=xxx, 均值=xxx, 标准差=xxx → 确认/排除
    光斑2: ...
  确认光斑: M/N个
  边缘过滤: 原始X条 → 过滤后Y条, 去除Z条光斑边缘
  自反思: PASS/WARN/FAIL — {原因}
=== Step 3b 完成 ===
```

## 适用场景
| 场景 | 效果 |
|------|------|
| 镜头模组(摄像头)有反光 | ✅ 主要目标场景 |
| 玻璃盖板/保护片反光 | ✅ 有效 |
| 金属表面高光 | ✅ 有效 |
| 均匀过曝图像 | ⚠️ FAIL（面积过大，非局部光斑） |
| 无反光的正常图像 | ✅ PASS（不影响后续流程） |

## 核心教训
1. **镜面反光产生的边缘是"假边缘"**：灰度梯度很强但不代表物体结构
2. **光斑需要膨胀处理**：光斑边缘附近的渐变区也会产生干扰边缘
3. **灰度聚类比空间聚类更有效**：光斑的本质是灰度异常，不是空间异常
4. **过滤而非忽略**：不是跳过有光斑的区域，而是用掩膜排除后仍使用剩余边缘
5. **验证很重要**：不是所有高亮区域都是光斑，需要用均值+标准差确认
