# Halcon 区域特征与选择技能手册

> 学习来源: `Regions/Features/`, `Regions/Creation/`, `Regions/Transformation/`
> 涵盖26个例程：区域特征提取、形状选择、区域创建与变换

---

## 一、区域特征完整参考表

### 形状特征（用于判断形状规则性）

| 特征 | 算子 | 值域 | 含义 | ⭐杂光检测用途 |
|---|---|---|---|---|
| **圆度** | `circularity(R,:,:,C)` | 0~1, 1=完美圆 | 4π·Area/Perimeter² | ⭐**核心指标**：正常孔光斑≈1 |
| **紧凑度** | `compactness(R,:,:,C)` | 1~∞, 1=最紧凑 | Perimeter²/(4π·Area) | ⭐圆度的倒数，杂光>1越多 |
| **凸度** | `convexity(R,:,:,C)` | 0~1, 1=完全凸 | Area/凸包面积 | ⭐杂光有凹陷→凸度低 |
| **矩形度** | `rectangularity(R,:,:,R)` | 0~1, 1=完美矩形 | Area/最小外接矩形面积 | 辅助判断 |
| **圆度2** | `roundness(R,:,:,D,S)` | 多指标 | 最大内切/外接圆比等 | 补充圆度 |
| **离心率** | `eccentricity(R,:,:,A,E)` | 0~1, 0=圆 | 等效椭圆离心率 | ⭐杂光扩散→离心率高 |

### 尺寸特征（用于面积/大小筛选）

| 特征 | 算子 | 值域 | 含义 | 用途 |
|---|---|---|---|---|
| **面积+中心** | `area_center(R,:,:,A,Row,Col)` | 0~∞ | 像素面积+重心坐标 | ⭐基础指标 |
| **孔洞面积** | `area_holes(R,:,:,A)` | 0~∞ | 区域内孔洞总面积 | 内部缺陷 |
| **轮廓长度** | `contlength(R,:,:,L)` | 0~∞ | 外轮廓周长 | 边缘复杂度 |
| **区域直径** | `diameter_region(R,:,:,Row1,Col1,Row2,Col2,D)` | 0~∞ | 最大卡尺距离 | 最大尺寸 |
| **最大内接圆** | `inner_circle(R,:,:,Row,Col,Radius)` | 坐标+半径 | 最大内切圆 | 孔径估计 |
| **最大内接矩形** | `inner_rectangle1(R,:,:,R1,C1,R2,C2)` | 坐标 | 轴对齐最大内接矩形 | 有效区域 |

### 方向/矩特征

| 特征 | 算子 | 值域 | 含义 |
|---|---|---|---|
| **椭圆轴** | `elliptic_axis(R,:,:,Ra,Rb,Phi)` | Ra,Rb>0, Phi弧度 | 等效椭圆长短轴+方向 |
| **方向** | `orientation_region(R,:,:,Phi)` | -π/2~π/2 | 主轴方向角 |
| **二阶矩** | `moments_region_2nd(R,:,:,M20,M02,M11)` | 实数 | 二阶中心矩 |

---

## 二、select_shape 形状筛选 ⭐

```
select_shape(Regions, SelectedRegions, Features, Operation, Min, Max)
```

| 参数 | 说明 |
|---|---|
| `Features` | 特征名数组: `'circularity'`, `'area'`, `'compactness'`等 |
| `Operation` | `'and'`(所有条件满足) 或 `'or'`(任一满足) |
| `Min/Max` | 特征值范围 |

### 常用筛选模式

#### ⭐ 背光小孔杂光检测筛选
```
// 筛选正常光斑: 圆度高 + 面积在范围内
select_shape(Regions, OKRegions, ['circularity','area'], 'and', [0.85, 500], [1.0, 5000])

// 筛选异常光斑(NG): 圆度低 或 面积异常
select_shape(Regions, NGRegions, 'circularity', 'and', 0.0, 0.7)
```

#### 筛选大面积区域
```
select_shape(Regions, LargeRegions, 'area', 'and', 10000, 9999999)
```

#### 多特征组合筛选
```
select_shape(Regions, Selected, ['circularity','convexity','area'], 'and', [0.8, 0.9, 100], [1.0, 1.0, 50000])
```

---

## 三、区域创建与变换

### 创建
| 算子 | 功能 |
|---|---|
| `gen_circle(R, Row, Col, Radius)` | 创建圆形区域 |
| `gen_ellipse(R, Row, Col, Phi, Ra, Rb)` | 创建椭圆 |
| `gen_rectangle1(R, R1, C1, R2, C2)` | 轴对齐矩形 |
| `gen_rectangle2(R, Row, Col, Phi, L1, L2)` | 旋转矩形 |

### 变换
| 算子 | 功能 | 用途 |
|---|---|---|
| `fill_up(R, Filled)` | 填充区域内孔洞 | 孔洞内部填充 |
| `shape_trans(R, Trans, Type)` | 形状变换(凸包/外接矩形等) | 外形简化 |
| `dilation_circle(R, Dilated, Radius)` | 圆形膨胀 | 扩大区域 |
| `erosion_circle(R, Eroded, Radius)` | 圆形腐蚀 | 缩小区域 |
| `closing_circle(R, Closed, Radius)` | 圆形闭运算 | 填补缺口 |

---

## 四、杂光检测特征选择决策树

```
光斑区域已分割(来自Task09)
├─ 第一步: 面积筛选
│   └─ select_shape('area') → 过滤过小噪声和过大异常
├─ 第二步: 圆度判断 ⭐核心
│   ├─ circularity > 0.85 → 可能OK
│   └─ circularity < 0.7 → 高度疑似NG(杂光)
├─ 第三步: 凸度验证
│   ├─ convexity > 0.9 → OK确认
│   └─ convexity < 0.8 → 有凹陷→杂光
├─ 第四步: 紧凑度/离心率
│   ├─ compactness < 1.5 且 eccentricity < 0.3 → OK
│   └─ compactness > 2.0 或 eccentricity > 0.6 → NG
└─ 综合判定: 多特征加权评分
```

---

## 五、C# HalconDotNet 代码模板

### 模板1: 背光小孔杂光检测完整流程 ⭐
```csharp
HObject image, region, connected, okRegions, ngRegions;
HTuple area, row, col, circularity, count;

// 1. 读图+二值化
HOperatorSet.ReadImage(out image, imagePath);
HOperatorSet.BinaryThreshold(image, out region, "max_separability", "light", out _);
HOperatorSet.Connection(region, out connected);

// 2. 面积过滤(去噪)
HOperatorSet.SelectShape(connected, out var filtered, "area", "and", 200, 99999);

// 3. 计算圆度
HOperatorSet.Circularity(filtered, out circularity);

// 4. 按圆度筛选OK/NG
HOperatorSet.SelectShape(filtered, out okRegions, 
    new HTuple("circularity"), "and", new HTuple(0.85), new HTuple(1.0));
HOperatorSet.SelectShape(filtered, out ngRegions,
    new HTuple("circularity"), "and", new HTuple(0.0), new HTuple(0.7));

HOperatorSet.CountObj(ngRegions, out count);
Console.WriteLine($"NG光斑数: {count.I}");

// 5. 获取每个NG区域的详细特征
HTuple ngCount;
HOperatorSet.CountObj(ngRegions, out ngCount);
for (int i = 1; i <= ngCount.I; i++)
{
    HObject singleRegion;
    HOperatorSet.SelectObj(ngRegions, out singleRegion, i);
    HOperatorSet.AreaCenter(singleRegion, out area, out row, out col);
    HTuple circ, conv, comp;
    HOperatorSet.Circularity(singleRegion, out circ);
    HOperatorSet.Convexity(singleRegion, out conv);
    HOperatorSet.Compactness(singleRegion, out comp);
    Console.WriteLine($"NG#{i}: Area={area.I}, Circularity={circ.D:F3}, Convexity={conv.D:F3}, Compactness={comp.D:F3}");
    singleRegion.Dispose();
}

ngRegions.Dispose();
okRegions.Dispose();
filtered.Dispose();
connected.Dispose();
region.Dispose();
image.Dispose();
```

### 模板2: 多特征综合评分
```csharp
// 综合评分：多特征加权判断OK/NG
double ScoreRegion(HObject region)
{
    HTuple circ, conv, comp, ecc;
    HOperatorSet.Circularity(region, out circ);
    HOperatorSet.Convexity(region, out conv);
    HOperatorSet.Compactness(region, out comp);
    HOperatorSet.Eccentricity(region, out _, out ecc);
    
    // 评分: 越高越像正常圆孔 (0~100)
    double score = 0;
    score += circ.D * 40;           // 圆度权重40%
    score += conv.D * 25;           // 凸度权重25%
    score += (1.0 / comp.D) * 20;   // 紧凑度倒数权重20%
    score += (1 - ecc.D) * 15;      // 离心率反转权重15%
    
    return score;
}

// score > 80: OK
// score 50~80: 可疑
// score < 50: NG
```

### 模板3: select_shape多条件筛选
```csharp
HObject selected;
// 同时满足: 圆度>0.8, 凸度>0.85, 面积100~10000
HOperatorSet.SelectShape(regions, out selected,
    new HTuple("circularity", "convexity", "area"),
    "and",
    new HTuple(0.8, 0.85, 100),
    new HTuple(1.0, 1.0, 10000));
```
