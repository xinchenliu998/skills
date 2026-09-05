# Step 1: 杂光检测 - 光源定位与特征提取

## 目标
准确定位图像中所有31个光源的中心坐标，提取每个光源的形状特征，为后续逐光源光刺检测提供基础数据。

## 输入
- `image`: Step0输出的灰度图像

## 处理流程

### 1.1 光斑提取
```csharp
// 阈值分割提取光斑区域（光源核心区域灰度较高）
HOperatorSet.Threshold(image, out HObject spotRegion, 150, 255);
HOperatorSet.Connection(spotRegion, out HObject connectedSpots);
spotRegion.Dispose();

// 按面积筛选正常光斑（排除噪点和大面积伪区域）
// 正常光斑面积范围约1500-8000像素
HOperatorSet.SelectShape(connectedSpots, out HObject validSpots,
    "area", "and", 1000, 10000);
connectedSpots.Dispose();
HOperatorSet.CountObj(validSpots, out HTuple spotCount);
```

### 1.2 逐光源特征提取
```csharp
var spots = new List<SpotInfo>();
for (int i = 1; i <= spotCount.I; i++)
{
    HOperatorSet.SelectObj(validSpots, out HObject spot, i);
    
    // 中心坐标
    HOperatorSet.AreaCenter(spot, out HTuple area, out HTuple row, out HTuple col);
    
    // 圆度 (1.0=完美圆, 越低越不规则)
    HOperatorSet.Circularity(spot, out HTuple circularity);
    
    // 凸度 (1.0=完美凸, 低凸度表示形状有凹陷/不规则)
    HOperatorSet.Convexity(spot, out HTuple convexity);
    
    // 矩形度
    HOperatorSet.Rectangularity(spot, out HTuple rectangularity);
    
    // 最小外接圆半径（用于确定光源核心区域大小）
    HOperatorSet.SmallestCircle(spot, out HTuple scRow, out HTuple scCol, out HTuple scRadius);
    
    spots.Add(new SpotInfo
    {
        Id = i,
        CenterRow = row.D,
        CenterCol = col.D,
        Area = area.D,
        Circularity = circularity.D,
        Convexity = convexity.D,
        Rectangularity = rectangularity.D,
        CoreRadius = scRadius.D  // 光源核心半径
    });
    
    spot.Dispose();
}
```

### 1.3 光源数量验证
```csharp
// 预期31个光源，允许一定偏差
if (spots.Count < 20 || spots.Count > 45)
{
    Console.WriteLine($"警告: 检测到{spots.Count}个光源，预期约31个");
    // 可能需要调整阈值重试
}
```

### 1.4 按视场分组（可选，用于报告）
```csharp
// 根据到图像中心的距离分组
int imgCx = 2624 / 2, imgCy = 2624 / 2;
foreach (var spot in spots)
{
    double distToCenter = Math.Sqrt(
        Math.Pow(spot.CenterRow - imgCy, 2) + 
        Math.Pow(spot.CenterCol - imgCx, 2));
    
    if (distToCenter < 100) spot.FieldGroup = "中心";
    else if (distToCenter < 500) spot.FieldGroup = "0.3视场";
    else if (distToCenter < 800) spot.FieldGroup = "0.5视场";
    else spot.FieldGroup = "0.85视场";
}
```

## 数据结构
```csharp
public class SpotInfo
{
    public int Id;
    public double CenterRow, CenterCol;  // 光源中心坐标
    public double Area;                   // 光斑面积
    public double Circularity;            // 圆度 (0-1)
    public double Convexity;              // 凸度 (0-1)
    public double Rectangularity;         // 矩形度
    public double CoreRadius;             // 最小外接圆半径
    public string FieldGroup = "";        // 视场分组
    // Step2填充:
    public bool HasSpike = false;         // 是否有光刺
    public double MaxSpikeLength = 0;     // 最大光刺长度(径向距离)
    public bool IsAbnormalShape = false;  // 是否异型光斑
}
```

## 输出
- `spots`: List<SpotInfo> 包含所有光源信息
- `spotMask`: 所有光源的合并掩膜（用于后续步骤）

## 自反思
- 光源数量是否接近31个？偏差过大需要调整阈值
- 光源分布是否合理（应在图像各处均匀分布）？
- 是否有遗漏的光源（被噪声或光刺遮挡）？
