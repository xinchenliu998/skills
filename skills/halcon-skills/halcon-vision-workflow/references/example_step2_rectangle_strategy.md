# Step 2: 矩形/平行线策略 (策略B — 外轮廓边缘中心法)

## 职责
探测ROI区域内的直线/矩形特征，判断是否存在平行线结构，通过最小外接矩形中心计算模组中心。

## 前置条件
- Step 0 已完成
- `ThresholdFailed == false`（至少有一个有效阈值模式）
- 若 `ThresholdFailed == true`，本step直接输出 `Valid=false, SelfCheck=N/A`

## 输入（来自Step 0）
| 字段 | 说明 |
|------|------|
| ImageROI | ReduceDomain后的ROI图像 |
| ValidModes | 有效阈值模式列表 |
| ROI_Area | ROI面积 |
| ROI_CenterRow/Col | ROI几何中心 |
| ROI_Diagonal | ROI对角线长度 |

## 输出
| 字段 | 类型 | 说明 |
|------|------|------|
| Valid | bool | 是否检测到有效矩形中心 |
| Row, Col | double | 最小外接矩形中心坐标 |
| HasParallelLines | bool | 是否存在平行线结构 |
| ParallelPairs | int | 平行线对数 |
| Dist_B_to_ROICenter | double | B结果到ROI中心距离 |
| SelfCheck | enum | PASS / WARN / FAIL / N_A |
| SelfCheckReason | string | 自反思结论说明 |

## 算子流程

```csharp
foreach (string mode in validModes)
{
    // 1. 阈值分割
    HOperatorSet.BinaryThreshold(ho_ImageROI, out ho_Foreground,
        "max_separability", mode, out _);

    // 2. 连通域分析 → 面积筛选
    HOperatorSet.Connection(ho_Foreground, out ho_Connected);
    HOperatorSet.SelectShape(ho_Connected, out ho_Selected,
        "area", "and", roiArea * 0.05, roiArea * 1.5);

    // 3. 填充 → 凸包变换
    HOperatorSet.FillUp(ho_Selected, out ho_Filled);
    HOperatorSet.ShapeTrans(ho_Filled, out ho_Convex, "convex");

    // 4. 提取边界 → 膨胀 → 边缘检测
    HOperatorSet.Boundary(ho_Convex, out ho_Boundary, "inner");
    HOperatorSet.DilationCircle(ho_Boundary, out ho_BoundaryDilated, 3.5);
    HOperatorSet.ReduceDomain(ho_ImageROI, ho_BoundaryDilated, out ho_ImageEdge);
    HOperatorSet.EdgesSubPix(ho_ImageEdge, out ho_Edges, "canny", 1, 20, 40);

    // 5. 筛选 + 合并相邻轮廓
    double minLen = roiDiagonal * 0.1;
    HOperatorSet.SelectShapeXld(ho_Edges, out ho_EdgesFiltered,
        "contlength", "and", minLen, 99999);
    HOperatorSet.UnionAdjacentContoursXld(ho_EdgesFiltered, out ho_United, 5, 1);

    // 6. 直线拟合 → 平行性判断
    HOperatorSet.CountObj(ho_United, out HTuple contCount);
    List<(double row, double col, double phi)> lines = new();

    for (int i = 1; i <= contCount.I; i++)
    {
        HOperatorSet.SelectObj(ho_United, out ho_Single, i);
        try
        {
            HOperatorSet.FitLineContourXld(ho_Single, "tukey", -1,
                out HTuple lRow, out HTuple lCol, out _, out _,
                out HTuple lPhi, out _);
            lines.Add((lRow.D, lCol.D, lPhi.D));
        }
        catch { }
        ho_Single.Dispose();
    }

    // 平行线判断
    int parallelPairs = 0;
    for (int i = 0; i < lines.Count; i++)
        for (int j = i + 1; j < lines.Count; j++)
        {
            double angleDiff = Math.Abs(lines[i].phi - lines[j].phi);
            // 考虑角度周期性（0°和180°等价）
            if (angleDiff > Math.PI / 2) angleDiff = Math.PI - angleDiff;
            double angleDiffDeg = angleDiff * 180.0 / Math.PI;
            if (angleDiffDeg < 5.0) parallelPairs++;
        }

    bool hasParallel = parallelPairs >= 2;

    // 7. 最小外接矩形中心
    HOperatorSet.SmallestRectangle2(ho_Convex,
        out HTuple rectRow, out HTuple rectCol,
        out HTuple rectPhi, out HTuple rectL1, out HTuple rectL2);

    // 输出中心坐标
    double bRow = rectRow.D, bCol = rectCol.D;
}
```

## 关键算子参数
| 算子 | 参数 | 说明 |
|------|------|------|
| `binary_threshold` | 'max_separability', mode | 自适应阈值 |
| `connection` | - | 连通域提取 |
| `select_shape` | 'area', ROI面积5%~150% | 面积筛选 |
| `fill_up` | - | 填充孔洞 |
| `shape_trans` | 'convex' | 凸包变换 |
| `edges_sub_pix` | 'canny', Alpha=1, Low=20, High=40 | 亚像素边缘 |
| `union_adjacent_contours_xld` | MaxDist=5, MaxAngle=1 | 合并相邻轮廓 |
| `fit_line_contour_xld` | 'tukey' | 鲁棒直线拟合 |
| `smallest_rectangle2` | - | 最小外接矩形 |

## 平行线判断逻辑
```
输入: N条拟合直线 (Row_i, Col_i, Phi_i)
计算: 所有直线对的角度差（考虑周期性）
判定: 角度差 < 5° 算一对平行线
      若 ≥ 2对 → HasParallelLines = true
意义: 有平行线说明存在矩形结构，SmallestRectangle2更可信
```

## 自反思规则（Step 2 内部）

### 检查1: B是否退化为ROI几何中心（原反思规则1）
```
Dist_B_to_ROI = sqrt((bRow - roiCenterRow)² + (bCol - roiCenterCol)²)

IF Dist_B_to_ROI < roiDiagonal * 0.02:
    → SelfCheck = FAIL
    → 原因: "策略B退化为ROI几何中心(距离={Dist:.2f}px, 阈值={threshold:.2f}px)"
    → 说明: 矩形拟合退化为ROI本身的外接矩形，而非目标模组
```

### 检查2: 是否检测到有效连通域
```
IF selectedCount == 0:
    → SelfCheck = FAIL
    → 原因: "未检测到有效连通域（面积筛选后为空）"
```

### 检查3: 平行线结构判断
```
IF !HasParallelLines:
    → SelfCheck = WARN
    → 原因: "未检测到平行线结构，矩形拟合可信度降低"
    → 注意: 这不是FAIL，SmallestRectangle2仍然输出结果
```

### 检查4: 矩形中心是否在ROI内
```
IF bRow < Row1 OR bRow > Row2 OR bCol < Col1 OR bCol > Col2:
    → SelfCheck = FAIL
    → 原因: "矩形中心不在ROI范围内"
```

### 综合判定
```
检查1 FAIL → SelfCheck = FAIL（B退化，最严重）
检查2 FAIL → SelfCheck = FAIL（无连通域）
检查4 FAIL → SelfCheck = FAIL（结果越界）
仅检查3 WARN → SelfCheck = WARN（无平行线但有结果）
全部通过 → SelfCheck = PASS
```

## 人类经验先验
- 策略B最容易受ROI大小影响：ROI越大，背景干扰越多，SmallestRectangle2越容易退化
- **检查1是最关键的**：当B结果 ≈ ROI中心时，几乎可以确定B已退化
- 有平行线时B的可信度显著提升（说明确实检测到了矩形结构的边缘）
- 无平行线时B的结果仍可参考，但应降低权重

## 输出格式
```
=== Step 2: 矩形/平行线策略 (策略B) ===
使用模式: dark/light
连通域: N个 (筛选后: M个)
拟合直线: K条
平行线: 有/无 (N对, 角度差<5°)
矩形中心: (Row, Col)
B到ROI中心距离: xx px (ROI对角线的x.x%)
自反思: PASS/WARN/FAIL — {原因}
=== Step 2 完成 ===
```
