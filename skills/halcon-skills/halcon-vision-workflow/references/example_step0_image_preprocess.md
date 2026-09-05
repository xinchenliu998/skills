# Step 0: 图像预处理与阈值分割预检

## 职责
本step是所有策略的前置步骤，负责图像读取、ROI限定、阈值分割有效性预检。

## 输入
| 参数 | 类型 | 说明 |
|------|------|------|
| ImagePath | string | 图像文件完整路径 |
| Row1, Col1 | double | ROI左上角坐标 |
| Row2, Col2 | double | ROI右下角坐标 |

## 输出
| 字段 | 类型 | 说明 |
|------|------|------|
| ImageROI | HObject | ReduceDomain后的ROI图像 |
| ROI_Row1/Col1/Row2/Col2 | double | ROI坐标 |
| ROI_CenterRow/CenterCol | double | ROI几何中心 |
| ROI_Area | double | ROI面积(像素) |
| ROI_Diagonal | double | ROI对角线长度 |
| ROI_Width/Height | double | ROI宽高 |
| DarkRatio | double | dark模式前景占比 |
| LightRatio | double | light模式前景占比 |
| ValidModes | string[] | 有效阈值模式列表 |
| ThresholdFailed | bool | 阈值分割是否全面失效 |

## 算子流程

### Phase 1: 图像读取与ROI限定
```csharp
HOperatorSet.ReadImage(out ho_Image, imagePath);
HOperatorSet.GetImageSize(ho_Image, out hv_Width, out hv_Height);
Console.WriteLine($"图像尺寸: {hv_Width.I}×{hv_Height.I}");

HOperatorSet.GenRectangle1(out ho_ROI, row1, col1, row2, col2);
HOperatorSet.ReduceDomain(ho_Image, ho_ROI, out ho_ImageROI);

// 计算ROI基本信息
double roiCenterRow = (row1 + row2) / 2.0;
double roiCenterCol = (col1 + col2) / 2.0;
double roiHeight = row2 - row1;
double roiWidth = col2 - col1;
double roiArea = roiHeight * roiWidth;
double roiDiagonal = Math.Sqrt(roiHeight * roiHeight + roiWidth * roiWidth);
```

### Phase 2: 阈值分割有效性预检
```csharp
// 对dark和light两种模式分别检查
string[] modes = { "dark", "light" };
List<string> validModes = new List<string>();
double darkRatio = 0, lightRatio = 0;

foreach (string mode in modes)
{
    HOperatorSet.BinaryThreshold(ho_ImageROI, out HObject ho_Fg,
        "max_separability", mode, out HTuple hv_Threshold);
    HOperatorSet.AreaCenter(ho_Fg, out HTuple fgArea, out _, out _);
    HOperatorSet.AreaCenter(ho_ROI, out HTuple domArea, out _, out _);

    double ratio = fgArea.D / domArea.D;
    if (mode == "dark") darkRatio = ratio;
    else lightRatio = ratio;

    Console.WriteLine($"阈值预检 [{mode}]: 前景占比={ratio:P1}, 阈值={hv_Threshold.I}");

    if (ratio >= 0.05 && ratio <= 0.95)
    {
        validModes.Add(mode);
        Console.WriteLine($"  → {mode}模式有效");
    }
    else
    {
        Console.WriteLine($"  → {mode}模式无效（前景占比异常）");
    }
    ho_Fg.Dispose();
}

bool thresholdFailed = validModes.Count == 0;
if (thresholdFailed)
{
    Console.WriteLine("⚠️ 阈值分割全面失效！将依赖Edge策略补救");
}
```

## 自反思规则（Step 0 级别）
本step的反思很简单：检查预检结果的合理性

| 检查项 | 条件 | 动作 |
|--------|------|------|
| ROI尺寸过小 | ROI_Area < 100 px² | 告警：ROI可能太小，结果可能不可靠 |
| ROI超出图像边界 | Row2>Height 或 Col2>Width | 自动裁剪到图像边界 |
| 阈值全面失效 | ThresholdFailed=true | 标记，后续Step 1/2跳过，Step 3标记低可信度 |
| dark和light结果互补 | darkRatio + lightRatio ≈ 1.0 | 正常现象，说明BinaryThreshold工作正常 |

## 输出格式
```
=== Step 0: 图像预处理 ===
图像: xxx.bmp (W×H)
ROI: (Row1, Col1) - (Row2, Col2)
ROI面积: xxx px², 对角线: xxx px
ROI中心: (CenterRow, CenterCol)
阈值预检 [dark]: 前景占比=xx.x%, 阈值=xxx → 有效/无效
阈值预检 [light]: 前景占比=xx.x%, 阈值=xxx → 有效/无效
有效模式: [dark, light] / [dark] / [light] / []
ThresholdFailed: false/true
=== Step 0 完成 ===
```
