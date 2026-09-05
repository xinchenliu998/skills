# Step 1: 圆策略 (策略A — 同心圆圆心法)

## 职责
探测ROI区域内的圆特征，判断是否存在近似同心圆，若存在则通过圆心加权平均计算模组中心。

## 前置条件
- Step 0 已完成
- `ThresholdFailed == false`（至少有一个有效阈值模式）
- 若 `ThresholdFailed == true`，本step直接输出 `Valid=false, SelfCheck=N/A`

## 输入（来自Step 0）
| 字段 | 说明 |
|------|------|
| ImageROI | ReduceDomain后的ROI图像 |
| ValidModes | 有效阈值模式列表 |
| ROI_Diagonal | ROI对角线长度（用于同心性判断阈值） |

## 输出
| 字段 | 类型 | 说明 |
|------|------|------|
| Valid | bool | 是否检测到有效同心圆 |
| Row, Col | double | 加权平均圆心坐标 |
| Radii | double[] | 各拟合圆的半径 |
| CircleCount | int | 有效拟合圆数量 |
| IsConcentric | bool | 是否判定为近似同心 |
| SelfCheck | enum | PASS / WARN / FAIL / N_A |
| SelfCheckReason | string | 自反思结论说明 |

## 算子流程

```csharp
// 遍历每个有效阈值模式
foreach (string mode in validModes)
{
    // 1. 阈值分割
    HOperatorSet.BinaryThreshold(ho_ImageROI, out ho_Foreground,
        "max_separability", mode, out _);

    // 2. 提取边界 → 膨胀构建边缘ROI
    HOperatorSet.Boundary(ho_Foreground, out ho_Boundary, "inner");
    HOperatorSet.DilationCircle(ho_Boundary, out ho_BoundaryDilated, 3.5);

    // 3. 在边缘ROI上做亚像素边缘检测
    HOperatorSet.ReduceDomain(ho_ImageROI, ho_BoundaryDilated, out ho_ImageEdge);
    HOperatorSet.EdgesSubPix(ho_ImageEdge, out ho_Edges, "canny", 1, 20, 40);

    // 4. 按轮廓长度筛选
    double minLen = roiDiagonal * 0.1;
    HOperatorSet.SelectShapeXld(ho_Edges, out ho_EdgesFiltered,
        "contlength", "and", minLen, 99999);

    // 5. 逐轮廓拟合圆
    HOperatorSet.CountObj(ho_EdgesFiltered, out HTuple edgeCount);
    List<(double row, double col, double radius)> circles = new();

    for (int i = 1; i <= edgeCount.I; i++)
    {
        HOperatorSet.SelectObj(ho_EdgesFiltered, out ho_SingleEdge, i);
        try
        {
            HOperatorSet.FitCircleContourXld(ho_SingleEdge, "geohuber", -1,
                out HTuple cRow, out HTuple cCol, out HTuple cRadius,
                out _, out _, out _);

            // 过滤无效圆：半径 > 3px 且 < ROI对角线的50%
            if (cRadius.D > 3 && cRadius.D < roiDiagonal * 0.5)
            {
                circles.Add((cRow.D, cCol.D, cRadius.D));
            }
        }
        catch { /* 拟合失败，跳过 */ }
        ho_SingleEdge.Dispose();
    }

    // 6. 同心性判断
    if (circles.Count >= 2)
    {
        double maxRadius = circles.Max(c => c.radius);
        double threshold = Math.Max(maxRadius * 0.1, 10);
        bool concentric = true;

        for (int i = 0; i < circles.Count && concentric; i++)
            for (int j = i + 1; j < circles.Count && concentric; j++)
            {
                double dist = Math.Sqrt(
                    Math.Pow(circles[i].row - circles[j].row, 2) +
                    Math.Pow(circles[i].col - circles[j].col, 2));
                if (dist > threshold) concentric = false;
            }

        if (concentric)
        {
            // 加权平均圆心（权重 = 1/半径，小圆更精确）
            double wSum = circles.Sum(c => 1.0 / c.radius);
            double finalRow = circles.Sum(c => c.row / c.radius) / wSum;
            double finalCol = circles.Sum(c => c.col / c.radius) / wSum;
            // → 输出 Valid=true
        }
    }
}
```

## 关键算子参数
| 算子 | 参数 | 说明 |
|------|------|------|
| `binary_threshold` | 'max_separability', mode | 自适应阈值 |
| `boundary` | 'inner' | 内边界 |
| `dilation_circle` | 半径=3.5 | 边界膨胀 |
| `edges_sub_pix` | 'canny', Alpha=1, Low=20, High=40 | 亚像素边缘 |
| `select_shape_xld` | 'contlength', min=对角线*0.1 | 长度筛选 |
| `fit_circle_contour_xld` | 'geohuber' | 鲁棒圆拟合 |

## 同心性判断逻辑
```
输入: N个拟合圆 (Row_i, Col_i, Radius_i)
有效圆筛选: Radius > 3px AND Radius < ROI_Diagonal * 0.5
同心阈值: max(Radius_max * 0.1, 10px)
判定: 所有圆心两两距离 < 同心阈值 → 近似同心
输出: 加权平均圆心（权重 = 1/Radius）
```

## 自反思规则（Step 1 内部）

### 检查1: 有效圆数量
```
IF circles.Count == 0 → SelfCheck = FAIL, 原因: "未检测到有效圆"
IF circles.Count == 1 → SelfCheck = WARN, 原因: "仅1个圆，无法验证同心性"
IF circles.Count >= 2 → 继续检查2
```

### 检查2: 伪圆检测（原反思规则3）
```
Radius_Max = max(Radii)
Radius_Min = min(Radii)

IF Radius_Max / Radius_Min > 100:
    → SelfCheck = FAIL, 原因: "半径差异过大(>{Ratio}倍)，存在伪拟合"

有效圆 = [r for r in Radii if 3 < r < ROI_Diagonal * 0.5]
IF 有效圆.Count < 2:
    → SelfCheck = FAIL, 原因: "有效圆不足2个"
```

### 检查3: 同心性
```
IF !IsConcentric:
    → SelfCheck = WARN, 原因: "圆心分散，不构成同心圆结构"
    → Valid = false
```

### 检查4: 圆心是否在ROI内
```
IF FinalRow < Row1 OR FinalRow > Row2 OR FinalCol < Col1 OR FinalCol > Col2:
    → SelfCheck = FAIL, 原因: "圆心不在ROI范围内"
```

### 综合判定
```
所有检查通过 → SelfCheck = PASS, Valid = true
任一检查WARN → SelfCheck = WARN, Valid = false（记录但不采信）
任一检查FAIL → SelfCheck = FAIL, Valid = false
```

## 输出格式
```
=== Step 1: 圆策略 (策略A) ===
使用模式: dark/light
检测到圆: N个 (有效: M个)
半径范围: [min_r ~ max_r]
同心性: 是/否 (最大圆心距: xx px, 阈值: xx px)
圆心坐标: (Row, Col)  [仅同心时输出]
自反思: PASS/WARN/FAIL — {原因}
=== Step 1 完成 ===
```
