# Step 4: Edge直接边缘检测策略 (策略Edge — 补救/交叉验证)

## 职责
跳过阈值分割，直接对ROI图像进行边缘检测，通过矩形拟合获取模组中心。作为不依赖阈值的补救策略，**始终执行**。

## 前置条件
- Step 0 已完成
- **Step 3b 已完成（如果存在）**：优先使用CleanImageROI
- **始终执行**：不依赖阈值分割结果，可在ThresholdFailed时作为唯一补救手段

## 输入（来自Step 0 和 Step 3b）
| 字段 | 来源 | 说明 |
|------|------|------|
| ImageROI | Step 0 | ReduceDomain后的ROI图像（原始） |
| CleanImageROI | Step 3b | 去除光斑后的ROI图像（如有光斑） |
| SpecularDetected | Step 3b | 是否检测到镜面反光 |
| SpecularRegion | Step 3b | 光斑区域（掩膜用） |
| ROI_Area | Step 0 | ROI面积 |
| ROI_Width / Height | Step 0 | ROI宽高 |
| ROI_CenterRow/Col | Step 0 | ROI几何中心 |

## ⚠️ 镜面反光处理规则（新增）
```
IF SpecularDetected == true:
    → 使用 CleanImageROI 替代 ImageROI 进行边缘检测
    → 覆盖度计算使用 CleanROI面积（去除光斑后的有效面积）
    → 方法2(整体包围)中自动排除光斑区域的轮廓
    → 日志中标注"[光斑过滤模式]"
ELSE:
    → 正常使用 ImageROI
```

## 输出
| 字段 | 类型 | 说明 |
|------|------|------|
| Valid | bool | 是否获得有效结果 |
| Row, Col | double | Edge策略计算的中心坐标 |
| Method | int | 使用的方法(1=逐轮廓拟合, 2=整体包围) |
| Coverage | double | 方法1的覆盖度(矩形面积/ROI面积) |
| SelfCheck | enum | PASS / WARN / FAIL |
| SelfCheckReason | string | 自反思结论说明 |

## 设计原理
```
传统策略: 阈值分割 → 区域提取 → 在区域边界做边缘检测
  → 阈值失效时，区域提取失败，后续全部失败

Edge策略: 直接对ROI图像做边缘检测 → 从边缘重建几何形状
  → 不依赖阈值，只依赖灰度梯度（物理边缘信息）
```

## 算子流程

```csharp
// Step 0.5: 选择输入图像（光斑过滤模式判断）
// 如果Step 3b检测到镜面反光，使用CleanImageROI；否则使用原始ImageROI
HObject ho_EdgeInput = specularDetected ? ho_CleanImageROI : ho_ImageROI;
double effectiveArea = specularDetected ? (roiArea * (1.0 - specularAreaRatio)) : roiArea;
if (specularDetected)
    Console.WriteLine($"  [光斑过滤模式] 使用CleanImageROI, 有效面积={effectiveArea:F0}");

// Step 1: 对比度增强
HOperatorSet.Emphasize(ho_EdgeInput, out ho_Enhanced, 7, 7, 1.5);

// Step 2: 直接亚像素边缘检测（不需要先做阈值分割）
HOperatorSet.EdgesSubPix(ho_Enhanced, out ho_Edges, "canny", 1.5, 15, 35);

// Step 3: 筛选有意义的边缘轮廓
double minLen = Math.Min(roiHeight, roiWidth) * 0.2;
HOperatorSet.SelectShapeXld(ho_Edges, out ho_EdgesFiltered,
    "contlength", "and", minLen, 99999);

// 如果筛选结果为空，降低阈值重试
HOperatorSet.CountObj(ho_EdgesFiltered, out HTuple filteredCount);
if (filteredCount.I == 0)
{
    minLen = Math.Min(roiHeight, roiWidth) * 0.1;
    HOperatorSet.SelectShapeXld(ho_Edges, out ho_EdgesFiltered,
        "contlength", "and", minLen, 99999);
}

// Step 4: 合并相邻轮廓
HOperatorSet.UnionAdjacentContoursXld(ho_EdgesFiltered, out ho_United, 10, 1);

// ========== 方法1: 逐轮廓FitRectangle2（精确但可能局部） ==========
HOperatorSet.CountObj(ho_United, out HTuple unitedCount);
double maxRectArea = 0;
double method1Row = 0, method1Col = 0;

for (int i = 1; i <= unitedCount.I; i++)
{
    HOperatorSet.SelectObj(ho_United, out ho_Single, i);
    try
    {
        HOperatorSet.FitRectangle2ContourXld(ho_Single, "tukey", -1,
            out HTuple rRow, out HTuple rCol, out HTuple rPhi,
            out HTuple rL1, out HTuple rL2, out _);
        double rectArea = rL1.D * rL2.D * 4;
        if (rectArea > maxRectArea)
        {
            maxRectArea = rectArea;
            method1Row = rRow.D;
            method1Col = rCol.D;
        }
    }
    catch { /* HALCON #3266: 部分轮廓拟合会失败，必须catch */ }
    ho_Single.Dispose();
}

double coverage1 = maxRectArea / roiArea;
bool method1Valid = coverage1 > 0.5; // 覆盖度>50%才可信

// ========== 方法2: 整体SmallestRectangle2（更鲁棒） ==========
double method2Row = 0, method2Col = 0;
bool method2Valid = false;

try
{
    HOperatorSet.GenRegionContourXld(ho_United, out ho_Regions, "filled");
    HOperatorSet.Union1(ho_Regions, out ho_Union);
    HOperatorSet.ShapeTrans(ho_Union, out ho_Convex, "convex");
    HOperatorSet.SmallestRectangle2(ho_Convex,
        out HTuple sRow, out HTuple sCol, out _, out HTuple sL1, out HTuple sL2);
    method2Row = sRow.D;
    method2Col = sCol.D;
    method2Valid = true;
}
catch { /* 转区域失败 */ }

// ========== 选择最终方法 ==========
if (method1Valid)
{
    // 方法1覆盖度>50%，优先使用
    edgeRow = method1Row; edgeCol = method1Col;
    usedMethod = 1;
}
else if (method2Valid)
{
    // 方法2备选
    edgeRow = method2Row; edgeCol = method2Col;
    usedMethod = 2;
}
else
{
    // 两种方法都失败
    edgeValid = false;
}
```

## 关键算子参数
| 算子 | 参数 | 说明 |
|------|------|------|
| `emphasize` | MaskW=7, MaskH=7, Factor=1.5 | 局部对比度增强 |
| `edges_sub_pix` | 'canny', Alpha=1.5, Low=15, High=35 | 低阈值捕获微弱边缘 |
| `select_shape_xld` | 'contlength', min=ROI短边*0.2 | 长度筛选 |
| `union_adjacent_contours_xld` | MaxDist=10, MaxAngle=1 | 合并相邻轮廓 |
| `fit_rectangle2_contour_xld` | 'tukey' | 逐轮廓矩形拟合(需try/catch) |
| `gen_region_contour_xld` | 'filled' | XLD转区域 |
| `smallest_rectangle2` | - | 整体最小外接矩形 |

## 自反思规则（Step 4 内部）

### 检查1: 是否有有效边缘
```
IF filteredCount == 0 (降低阈值后仍为空):
    → SelfCheck = FAIL
    → 原因: "未检测到有效边缘轮廓"
```

### 检查2: 方法1覆盖度
```
IF method1Valid AND coverage1 < 0.5:
    → 方法1不可信，记录但不采用
    → 原因: "方法1覆盖度仅{coverage:P1}，矩形中心可能偏向局部边缘"
```

### 检查3: 中心是否在ROI内
```
IF edgeRow < Row1 OR edgeRow > Row2 OR edgeCol < Col1 OR edgeCol > Col2:
    → SelfCheck = FAIL
    → 原因: "Edge中心不在ROI范围内"
```

### 检查4: 两种方法一致性（如果都有效）
```
IF method1Valid AND method2Valid:
    dist_m1_m2 = Distance(method1, method2)
    IF dist_m1_m2 < 5.0:
        → 互相印证，可信度提升
    ELSE:
        → SelfCheck = WARN
        → 原因: "方法1和方法2偏差较大({dist:.2f}px)"
```

### 综合判定
```
有效边缘 + 中心在ROI内 + 覆盖度合理 → SelfCheck = PASS
有效边缘但覆盖度不足 / 方法不一致 → SelfCheck = WARN
无有效边缘 / 中心越界 → SelfCheck = FAIL
```

## 关键注意事项
1. **FitRectangle2ContourXld必须try/catch**：HALCON #3266异常
2. **方法1覆盖度验证关键**：单轮廓矩形可能只覆盖40%，中心偏向该边缘
3. **方法2通常更可靠**：利用所有有效边缘的空间分布
4. **Emphasize的Factor=1.5**：适中值，边缘太弱可增大到2.0
5. **⚠️ 镜面反光是主要干扰源**：光斑产生的"假边缘"灰度梯度很强，但不代表物体结构。必须先通过Step 3b过滤光斑区域后再做边缘检测，否则矩形拟合中心会被光斑边缘拉偏（典型偏差30~50px）
6. **覆盖度计算需用有效面积**：当存在光斑过滤时，`coverage = maxRectArea / effectiveArea`，而非 `roiArea`

## 适用场景
| 场景 | 阈值分割状态 | Edge效果 |
|------|-------------|----------|
| 模组填满ROI，灰度均匀 | ❌ 失效 | ✅ 能检测模组物理边缘 |
| 低对比度图像 | ❌ 不准确 | ✅ Emphasize增强后有效 |
| 多层透明/半透明结构 | ❌ 多阈值干扰 | ✅ 直接检测物理边缘 |
| 镜头有反光光斑 | ⚠️ 光斑干扰 | ✅ 配合Step3b过滤后有效 |

## 输出格式
```
=== Step 4: Edge直接边缘策略 ===
Emphasize增强: Factor=1.5
检测到边缘: N条 (筛选后: M条, 合并后: K条)
方法1(逐轮廓): 中心=(Row, Col), 覆盖度=xx.x% → 有效/无效
方法2(整体包围): 中心=(Row, Col) → 有效/无效
选择方法: 方法1/方法2
最终中心: (Row, Col)
自反思: PASS/WARN/FAIL — {原因}
=== Step 4 完成 ===
```
