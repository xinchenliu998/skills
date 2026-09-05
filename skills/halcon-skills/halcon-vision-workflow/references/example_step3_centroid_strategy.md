# Step 3: 区域重心策略 (策略C — 兜底方案)

## 职责
通过阈值分割提取最大连通域，计算其面积重心作为模组中心。作为兜底方案，始终执行（即使阈值分割异常也输出结果，但标记可信度）。

## 前置条件
- Step 0 已完成
- **始终执行**（不跳过），但根据阈值状态调整可信度标记

## 输入（来自Step 0）
| 字段 | 说明 |
|------|------|
| ImageROI | ReduceDomain后的ROI图像 |
| ROI_Area | ROI面积 |
| ROI_CenterRow/Col | ROI几何中心 |
| DarkRatio / LightRatio | 各模式前景占比 |
| ThresholdFailed | 阈值是否全面失效 |

## 输出
| 字段 | 类型 | 说明 |
|------|------|------|
| Row, Col | double | 最大连通域重心坐标 |
| Area | double | 最大连通域面积 |
| AreaRatio | double | 面积占比 = Area / ROI_Area |
| UsedMode | string | 最终使用的阈值模式 |
| SelfCheck | enum | PASS / WARN / FAIL |
| SelfCheckReason | string | 自反思结论说明 |

## 算子流程

```csharp
// 对dark和light两种模式都执行，选最优
string bestMode = "";
double bestRow = 0, bestCol = 0, bestArea = 0, bestRatio = 0;
double bestScore = -1; // 选择评分

foreach (string mode in new[] { "dark", "light" })
{
    HOperatorSet.BinaryThreshold(ho_ImageROI, out ho_Foreground,
        "max_separability", mode, out _);

    HOperatorSet.Connection(ho_Foreground, out ho_Connected);
    HOperatorSet.SelectShapeStd(ho_Connected, out ho_MaxRegion, "max_area", 0);
    HOperatorSet.AreaCenter(ho_MaxRegion, out HTuple area, out HTuple row, out HTuple col);

    double ratio = area.D / roiArea;
    
    // 评分逻辑：面积占比越接近50%越好，在5%~95%范围内有效
    double score = 0;
    if (ratio >= 0.05 && ratio <= 0.95)
    {
        score = 1.0 - Math.Abs(ratio - 0.5); // 越接近50%分越高
    }
    else
    {
        score = 0.01; // 异常但仍有值
    }

    Console.WriteLine($"策略C [{mode}]: 重心=({row.D:F2}, {col.D:F2}), " +
                      $"面积={area.I}, 占比={ratio:P1}, 评分={score:F3}");

    if (score > bestScore)
    {
        bestScore = score;
        bestMode = mode;
        bestRow = row.D;
        bestCol = col.D;
        bestArea = area.D;
        bestRatio = ratio;
    }

    ho_Foreground.Dispose();
    ho_Connected.Dispose();
    ho_MaxRegion.Dispose();
}
```

## 关键算子参数
| 算子 | 参数 | 说明 |
|------|------|------|
| `binary_threshold` | 'max_separability', 遍历dark/light | 自适应阈值 |
| `connection` | - | 连通域提取 |
| `select_shape_std` | 'max_area', 0 | 选最大连通域 |
| `area_center` | - | 计算面积和重心 |

## 模式选择规则
```
对dark和light两种模式都执行:
  计算面积占比 ratio = maxArea / roiArea
  计算评分 score = (ratio在5%~95%) ? (1.0 - |ratio - 0.5|) : 0.01

选择规则:
  1. 选score最高的模式
  2. 即：优先选面积占比在5%~95%范围内、且更接近50%的模式
  3. 两种模式都异常时，选面积更大的（score=0.01时比较面积）
```

## 自反思规则（Step 3 内部）

### 检查1: 面积占比校验（原反思规则4）
```
IF AreaRatio < 0.05:
    → SelfCheck = WARN
    → 原因: "前景面积过小({AreaRatio:P1})，可能分割不完整"

IF AreaRatio > 0.95:
    → SelfCheck = WARN
    → 原因: "前景面积占比{AreaRatio:P1}，重心可能退化为ROI中心"
    → 补充: 这不一定是错误，可能模组确实填满ROI，需Edge交叉验证
```

### 检查2: 重心与ROI中心距离
```
Dist_C_to_ROI = sqrt((cRow - roiCenterRow)² + (cCol - roiCenterCol)²)

IF AreaRatio > 0.95 AND Dist_C_to_ROI < roiDiagonal * 0.02:
    → SelfCheck升级为 WARN (确认退化)
    → 原因: "重心≈ROI中心(距离={Dist:.2f}px)，且面积占比>{AreaRatio:P1}"
```

### 检查3: 重心是否在ROI内
```
IF cRow < Row1 OR cRow > Row2 OR cCol < Col1 OR cCol > Col2:
    → SelfCheck = FAIL
    → 原因: "重心不在ROI范围内"（理论上不应发生）
```

### 综合判定
```
面积占比5%~95%且重心在ROI内 → SelfCheck = PASS
面积异常(<5%或>95%)但有值 → SelfCheck = WARN
重心越界 → SelfCheck = FAIL
```

## 人类经验先验
- 策略C是最鲁棒的方案，对ROI大小变化有天然免疫力
- `BinaryThreshold('max_separability')` + `SelectShapeStd('max_area')` 组合很稳定
- 但当模组填满ROI时（AreaRatio>95%），重心退化为ROI中心——这时结果可能依然正确（模组确实在ROI中心），需要Edge交叉验证来确认
- **策略C的WARN不等于不可信**，只是提醒需要额外验证

## 输出格式
```
=== Step 3: 区域重心策略 (策略C) ===
dark模式: 重心=(Row, Col), 面积=xxx, 占比=xx.x%, 评分=x.xxx
light模式: 重心=(Row, Col), 面积=xxx, 占比=xx.x%, 评分=x.xxx
选择模式: dark/light (评分: x.xxx)
最终重心: (Row, Col), 面积占比=xx.x%
自反思: PASS/WARN/FAIL — {原因}
=== Step 3 完成 ===
```
