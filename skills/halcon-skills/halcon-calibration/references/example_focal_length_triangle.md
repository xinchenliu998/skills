# 焦距三角关系计算 — 相似三角形法

> 触发场景: "焦距"、"focal length"、"三角关系"、"相似三角形"、"计算焦距"、"标定焦距"
> 无需 Halcon 标定板描述文件，仅需已知尺寸的标定物 + 工作距离 + 像元尺寸即可计算

---

## 一、核心公式：相似三角形

```
              镜头平面         传感器平面
                │                 │
    ┌───────────┼─────────────────┼──┐
    │           │ ←──── f ──────→ │  │
    │           │                 │  │
    │           │                 │──┤ ← L5 (传感器上成像长度)
    │           │                 │  │
    │←─ L2 ───→│                 │  │
    │           │                 │  │
    │           │                 │  │
    └───────────┼─────────────────┼──┘
                │
                │
    ┌───────────┼─────────────────────┐
    │           │                     │
    │           │                     │
    │←──────── L1 ──────────────────→│ ← 标定板实际长度
    │           │                     │
    └───────────┼─────────────────────┘
                │
              标定板
```

### 三角关系公式

```
  f      L5
 ───  =  ───
  L2     L1

  →  f = L5 × L2 / L1
```

### 变量定义

| 符号 | 含义 | 获取方式 | 单位 |
|------|------|----------|------|
| **L1** | 标定板实际测量长度 | 已知（如棋盘格 N 格 × 单格尺寸） | mm |
| **L2** | 镜头到标定板的实际距离 | 实测（工作距离） | mm |
| **L3** | 图像中标定板像素长度 | 从图像中测量 | px |
| **L4** | 单个像素的实际长度（像元尺寸） | 相机规格书 | mm/px (μm→mm) |
| **L5** | 传感器上成像长度 | L3 × L4（计算得出） | mm |
| **f** | 焦距 | **计算结果** | mm |

### 计算链路

```
L4 (像元尺寸, 已知)  ─┐
                      ├──→ L5 = L3 × L4
L3 (像素长度, 测量)  ─┘         │
                                ├──→ f = L5 × L2 / L1
L2 (工作距离, 实测)  ──────────┘
L1 (实际长度, 已知)  ──────────┘
```

---

## 二、完整计算步骤

### Step 1: 确定标定板实际长度 L1

```
L1 = 棋盘格方格数 × 单格实际尺寸

示例: 10格 × 20mm/格 = 200mm
      5格  × 20mm/格 = 100mm
```

### Step 2: 测量工作距离 L2

```
L2 = 镜头前端（或传感器平面）到标定板表面的距离

7485相机: 500mm (50cm)
7451相机: 640mm (64cm)
```

### Step 3: 从图像中测量像素长度 L3

```
在图像上找到标定板的两个端点：
  (row1, col1)  →  左端角点
  (row2, col2)  →  右端角点

L3 = √((row2-row1)² + (col2-col1)²)   (欧氏距离, 单位: px)
```

### Step 4: 获取像元尺寸 L4

```
L4 = 相机像元尺寸 (μm) / 1000

7485相机: 2.0μm → L4 = 0.002 mm/px
7451相机: 2.9μm → L4 = 0.0029 mm/px
```

### Step 5: 计算传感器上成像长度 L5

```
L5 = L3 × L4    (单位: mm)
```

### Step 6: 计算焦距 f

```
f = L5 × L2 / L1    (单位: mm)
```

---

## 三、HalconDotNet C# 代码模板

```csharp
using HalconDotNet;

record FocalCalcResult
{
    public double PixelLength { get; init; }      // L3 (px)
    public double SensorLength { get; init; }     // L5 (mm)
    public double FocalLength { get; init; }      // f (mm)
}

/// <summary>
/// 相似三角形法计算焦距
/// </summary>
/// <param name="pixelDist">图像上标定板端点像素距离 L3 (px)</param>
/// <param name="realLength">标定板实际长度 L1 (mm)</param>
/// <param name="workDist">工作距离 L2 (mm)</param>
/// <param name="pixelSizeUm">像元尺寸 (μm)</param>
static FocalCalcResult CalcFocalByTriangle(
    double pixelDist, double realLength, double workDist, double pixelSizeUm)
{
    double L3 = pixelDist;
    double L1 = realLength;
    double L2 = workDist;
    double L4 = pixelSizeUm / 1000.0;    // μm → mm

    double L5 = L3 * L4;                 // 传感器上成像长度 (mm)
    double f = L5 * L2 / L1;             // 焦距 (mm)

    Console.WriteLine($"=== 焦距三角关系计算 ===");
    Console.WriteLine($"L1 (实际长度):    {L1:F1} mm");
    Console.WriteLine($"L2 (工作距离):    {L2:F1} mm");
    Console.WriteLine($"L3 (像素长度):    {L3:F2} px");
    Console.WriteLine($"L4 (像元尺寸):    {L4:F4} mm/px ({pixelSizeUm}μm)");
    Console.WriteLine($"L5 (传感器长度):  {L5:F4} mm");
    Console.WriteLine($"f  (焦距):        {f:F4} mm");
    Console.WriteLine($"验证: f/L5={f/L5:F4}  L2/L1={L2/L1:F4}  比值一致={Math.Abs(f/L5 - L2/L1) < 0.001}");

    return new FocalCalcResult
    {
        PixelLength = L3,
        SensorLength = L5,
        FocalLength = f
    };
}

// 使用示例
var result = CalcFocalByTriangle(
    pixelDist: 532.09,      // 图像上10格距离 (px)
    realLength: 200.0,      // 10格 × 20mm = 200mm
    workDist: 500.0,        // 工作距离 500mm
    pixelSizeUm: 2.0);      // 像元 2μm
// 输出: f ≈ 2.66mm
```

### 集成到完整流程（从图像到焦距）

```csharp
static FocalCalcResult CalcFocalFromImage(
    string imagePath, string outputDir,
    double squareSizeMm, int gridCount,
    double workDistMm, double pixelSizeUm)
{
    HObject ho_Image = null;
    try
    {
        HOperatorSet.ReadImage(out ho_Image, imagePath);
        HOperatorSet.GetImageSize(ho_Image, out HTuple hv_Width, out HTuple hv_Height);
        int width = hv_Width.I, height = hv_Height.I;

        // Step A: 检测角点 (使用已有方法)
        var (corners, _) = DetectCheckerCorners(ho_Image, width, height, Log);

        // Step B: 找最接近中心的角点
        int centerIdx = FindNearestPoint(cornerRows, cornerCols, height / 2.0, width / 2.0);

        // Step C: 向左右各追踪 gridCount/2 个角点
        // ... 追踪逻辑 ...

        // Step D: 计算最左到最右像素距离 L3
        double L3 = Math.Sqrt(
            Math.Pow(rightMost.row - leftMost.row, 2) +
            Math.Pow(rightMost.col - leftMost.col, 2));

        // Step E: 三角关系计算焦距
        double L1 = gridCount * squareSizeMm;
        double f = (L3 * pixelSizeUm / 1000.0) * workDistMm / L1;

        return new FocalCalcResult
        {
            PixelLength = L3,
            SensorLength = L3 * pixelSizeUm / 1000.0,
            FocalLength = f
        };
    }
    finally { ho_Image?.Dispose(); }
}
```

---

## 四、公式验证：三种计算方式的一致性

对于同一组数据，三种计算方式得出的 f 应当一致：

### 方式1：使用 5格（单侧）
```
L1 = 5 × 20 = 100mm
L5 = leftDist × L4
f = L5 × L2 / L1
```

### 方式2：使用 10格（全跨）
```
L1 = 10 × 20 = 200mm
L5 = totalDist × L4
f = L5 × L2 / L1
```

### 方式3：使用 5格（另一侧）
```
L1 = 5 × 20 = 100mm
L5 = rightDist × L4
f = L5 × L2 / L1
```

**三者应当一致**（在测量误差范围内）。如果不一致，说明：
- 左右角点不对称（畸变或追踪方向偏差）
- 中心角点不在标定板几何中心
- 像元尺寸或工作距离参数有误

---

## 五、多图像融合：降低随机误差

```
对同一相机拍摄的 N 张标定板图像分别计算 f₁, f₂, ..., fₙ

均值: μ = Σfᵢ / N
标准差: σ = √(Σ(fᵢ-μ)² / N)
变异系数: CV = σ / μ × 100%

CV < 5%   → 测量稳定，焦距可信
5% < CV < 10% → 存在一定波动，检查角点检测
CV > 10%  → 测量不稳定，需要排查
```

### 示例（基于实际数据）

```
7485-2um (D=500mm, L4=2μm):
  f₁=2.660mm, f₂=2.619mm, f₃=2.997mm
  μ=2.759mm, CV=6.14%

7451-2.9um (D=640mm, L4=2.9μm):
  f₁=5.168mm, f₂=5.290mm, f₃=4.979mm
  μ=5.146mm, CV=2.48%
```

---

## 六、与 Halcon 原生标定的对比

| 特性 | 三角关系法 (本skill) | Halcon calibrate_cameras |
|------|---------------------|--------------------------|
| 需要标定板描述文件 | ❌ 不需要 | ✅ 需要 .descr |
| 需要多角度图像 | ❌ 单张即可 | ✅ 需要10-20张 |
| 输出畸变系数 | ❌ 不输出 | ✅ Kappa, K1/K2/K3 |
| 输出主点 | ❌ 不输出 | ✅ Cx, Cy |
| 焦距精度 | 中（受单次测量误差影响） | 高（多图最小二乘优化） |
| 适用场景 | 快速估算焦距、无描述文件时 | 精确标定、机器人视觉 |

---

## 七、关键注意事项

| 要点 | 说明 |
|------|------|
| **L1 必须准确** | 棋盘格方格尺寸误差直接影响焦距精度 |
| **L2 测量基准** | 从传感器平面量起（非镜头前端），但近似可用镜头前端 |
| **L3 方向对齐** | 测量方向应与标定板网格方向对齐，否则引入角度误差 |
| **L4 单位转换** | μm → mm 除以1000，常见遗漏 |
| **镜头畸变** | 本方法忽略畸变，畸变较大时焦距有系统偏差 |
| **多图平均** | 推荐≥3张不同距离/角度图片取平均 |

---

## 八、三角函数视角（等价公式）

当标定板不垂直于光轴时：

```
f = L5 × L2 × cos(θ) / L1

其中 θ = 标定板法线与光轴的夹角
cos(θ) 修正了透视缩短效应

垂直拍摄时 θ=0°, cos(0)=1, 退化为基本公式
```

---

*关联代码: FocalCalib/Program.cs*
*关联skill: camera_calibration.md (Halcon标准标定), libcbdetect_chessboard_corners.md (角点检测)*