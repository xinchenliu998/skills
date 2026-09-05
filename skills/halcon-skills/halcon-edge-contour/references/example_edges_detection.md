# Halcon 边缘检测算子技能手册

> 学习来源: `C:\Users\Public\Documents\MVTec\HALCON-20.11-Steady\examples\hdevelop\Filters\Edges\`
> 涵盖19个例程，共计19个边缘检测相关算子

---

## 一、算子总览对比表

| 算子 | 类型 | 精度 | 速度 | 抗噪 | 输出 | 适用场景 |
|---|---|---|---|---|---|---|
| **edges_sub_pix** ⭐ | 综合 | 亚像素 | 中 | 高 | XLD轮廓 | 高精度测量首选 |
| **edges_image** | 综合 | 像素 | 中 | 高 | 幅值+方向图 | 需要边缘方向信息 |
| **edges_color** | 综合(彩色) | 像素 | 慢 | 高 | 幅值+方向图 | 彩色图颜色边界 |
| **edges_color_sub_pix** | 综合(彩色) | 亚像素 | 慢 | 高 | XLD轮廓 | 彩色图高精度 |
| **sobel_amp** | 一阶梯度 | 像素 | 快 | 中 | 幅值图 | 通用边缘强度 |
| **sobel_dir** | 一阶梯度 | 像素 | 快 | 中 | 幅值+方向图 | 需方向+NMS |
| **prewitt_amp** | 一阶梯度 | 像素 | 最快 | 低 | 幅值图 | 快速粗检测 |
| **roberts** | 一阶梯度 | 像素 | 最快 | 最低 | 幅值图 | 细线条/低噪声 |
| **frei_amp** | 一阶梯度 | 像素 | 快 | 中 | 幅值图 | Sobel改进版 |
| **kirsch_amp** | 一阶梯度 | 像素 | 中 | 中 | 幅值图 | 全方向均匀响应 |
| **robinson_amp** | 一阶梯度 | 像素 | 中 | 中 | 幅值图 | 全方向边缘 |
| **derivate_gauss** | 多功能 | 像素 | 中 | 高 | 多种 | 万能算子 |
| **laplace_of_gauss** | 二阶 | 像素 | 中 | 高 | 零交叉 | 封闭轮廓 |
| **laplace** | 二阶 | 像素 | 快 | 低 | 零交叉 | 简单快速 |
| **diff_of_gauss** | 带通 | 像素 | 中 | 中 | 近似LoG | LoG快速替代 |
| **highpass_image** | 高通 | 像素 | 快 | 最低 | 高频图 | 预处理增强 |
| **close_edges** | 后处理 | — | 快 | — | 闭合区域 | 边缘补全 |
| **close_edges_length** | 后处理 | — | 快 | — | 闭合区域 | 限距边缘补全 |
| **info_edges** | 辅助 | — | — | — | 滤波器信息 | 调试查询 |

---

## 二、边缘检测策略选择决策树

```
开始
├─ 需要亚像素精度？
│   ├─ 是 → 灰度图？
│   │   ├─ 是 → edges_sub_pix ⭐（首选）
│   │   └─ 否 → edges_color_sub_pix
│   └─ 否 → 继续↓
├─ 彩色图像？
│   ├─ 是 → edges_color
│   └─ 否 → 继续↓
├─ 需要边缘方向信息？
│   ├─ 是 → sobel_dir + nonmax_suppression_dir
│   └─ 否 → 继续↓
├─ 需要尺度可调/多功能？
│   ├─ 是 → derivate_gauss（Sigma调尺度）
│   └─ 否 → 继续↓
├─ 需要封闭轮廓？
│   ├─ 是 → laplace_of_gauss + zero_crossing
│   └─ 否 → 继续↓
├─ 速度优先？
│   ├─ 是 → prewitt_amp 或 roberts
│   └─ 否 → sobel_amp（默认选择）
└─ 边缘有断裂？
    ├─ 小间隙 → close_edges
    └─ 需限距 → close_edges_length
```

---

## 三、各类算子详解

### A. 综合边缘检测（推荐优先使用）

#### edges_sub_pix ⭐ 亚像素边缘（最常用）
```
edges_sub_pix(Image, Edges, Filter, Alpha, Low, High)
```
- **Filter**: `'canny'`（最常用）, `'lanser2'`, `'deriche2'`
- **Alpha**: 平滑参数，典型值2（越大越平滑）
- **Low/High**: 滞后阈值，如12/22
- **直接输出XLD轮廓**，无需后处理

#### edges_image 像素级边缘
```
edges_image(Image, ImaAmp, ImaDir, Filter, Alpha, NMS, Low, High)
```
- **NMS**: `'nms'`(非极大值抑制) 或 `'none'`
- **输出**: 幅值图+方向图
- **后处理**: threshold → skeleton → gen_contours_skeleton_xld

#### edges_color / edges_color_sub_pix 彩色边缘
- 参数同灰度版，输入为多通道图像
- 利用颜色通道差异，灰度相近但颜色不同的区域也能检出

### B. 经典梯度算子

#### sobel_amp / sobel_dir
```
sobel_amp(Image, EdgeAmplitude, FilterType, Size)
sobel_dir(Image, EdgeAmplitude, EdgeDirection, FilterType, Size)
```
- **FilterType**: `'sum_abs'`(快) / `'sum_sqrt'`(精确)
- **Size**: 3/5/7

#### prewitt_amp / roberts
```
prewitt_amp(Image, ImageEdgeAmp)        -- 无参数，固定3×3
roberts(Image, ImageRoberts, FilterType) -- FilterType='roberts_max'
```

#### frei_amp / kirsch_amp / robinson_amp
```
frei_amp(Image, ImageEdgeAmp)      -- Sobel优化版
kirsch_amp(Image, ImageEdgeAmp)    -- 8方向最大响应
robinson_amp(Image, ImageEdgeAmp)  -- 8方向Robinson系数
```

### C. 二阶导数/高斯系列

#### derivate_gauss 万能高斯导数
```
derivate_gauss(Image, Result, Sigma, Component)
```
- **Sigma**: 1.5~3.0（尺度控制）
- **Component**: `'gradient'`=边缘, `'det'`=角点, `'laplace'`=拉普拉斯, `'none'`=平滑

#### laplace_of_gauss (LoG)
```
laplace_of_gauss(Image, ImageLaplace, Sigma)  -- Sigma典型值5
→ zero_crossing(ImageLaplace, RegionCrossing)  -- 提取边缘
```

#### laplace
```
laplace(Image, ImageLaplace, 'signed', MaskSize, 'n_8_isotropic')
→ zero_crossing(...)
```

#### diff_of_gauss (DoG)
```
diff_of_gauss(Image, DiffOfGauss, Sigma, SigFactor)  -- LoG快速近似
```

#### highpass_image
```
highpass_image(Image, Highpass, Width, Height)  -- 高通=原图-均值
```

### D. 边缘后处理

#### close_edges / close_edges_length
```
close_edges(Edges, EdgeAmplitude, EdgesExtended, MinAmplitude)
close_edges_length(Edges, EdgeAmplitude, ClosedEdges, MinAmplitude, MaxGapLength)
```
- `MinAmplitude`: 闭合处最低边缘强度
- `MaxGapLength`: 最大允许闭合间隙

---

## 四、参数调优指南

### Alpha（平滑参数）
| 值范围 | 效果 | 场景 |
|---|---|---|
| 0.1~0.5 | 弱平滑，保留细节 | 高质量低噪声图像 |
| 1.0~2.0 | 中等平滑 | 一般工业场景 |
| 3.0~5.0 | 强平滑，抑制噪声 | 噪声较大的图像 |

### Low/High（滞后阈值）
- **High**: 强边缘阈值，越高越只保留明显边缘
- **Low**: 弱边缘阈值，与强边缘相连的弱边缘也保留
- **经验值**: Low=8~15, High=20~30
- **调优**: 先调High确定主要边缘，再调Low补充细节

### Sigma（高斯尺度）
- **小Sigma(1~2)**: 检测细小边缘
- **大Sigma(3~10)**: 检测大尺度结构边缘，忽略小细节

---

## 五、C# HalconDotNet 代码模板

### 模板1: 亚像素边缘检测（最常用）
```csharp
// edges_sub_pix — 亚像素边缘检测
HObject image, edges;
HOperatorSet.ReadImage(out image, "input.png");
HOperatorSet.EdgesSubPix(image, out edges, "canny", 2.0, 12, 22);

// 获取轮廓信息
HTuple rows, cols;
HOperatorSet.GetContourXld(edges, out rows, out cols);
Console.WriteLine($"检测到边缘点数: {rows.Length}");

edges.Dispose();
image.Dispose();
```

### 模板2: Sobel + NMS 精细边缘
```csharp
// sobel_dir + 非极大值抑制
HObject image, edgeAmp, edgeDir, nmsResult, region;
HOperatorSet.ReadImage(out image, "input.png");
HOperatorSet.SobelDir(image, out edgeAmp, out edgeDir, "sum_abs", 3);
HOperatorSet.NonmaxSuppressionDir(edgeAmp, edgeDir, out nmsResult, "nms");
HOperatorSet.Threshold(nmsResult, out region, 10, 255);

region.Dispose();
nmsResult.Dispose();
edgeDir.Dispose();
edgeAmp.Dispose();
image.Dispose();
```

### 模板3: LoG + 零交叉封闭边缘
```csharp
// laplace_of_gauss + zero_crossing
HObject image, imgLaplace, regionCrossing;
HOperatorSet.ReadImage(out image, "input.png");
HOperatorSet.LaplaceOfGauss(image, out imgLaplace, 5.0);
HOperatorSet.ZeroCrossing(imgLaplace, out regionCrossing);

regionCrossing.Dispose();
imgLaplace.Dispose();
image.Dispose();
```

### 模板4: 边缘闭合
```csharp
// edges_image + close_edges_length
HObject image, imaAmp, imaDir, edges, closedEdges;
HOperatorSet.ReadImage(out image, "input.png");
HOperatorSet.EdgesImage(image, out imaAmp, out imaDir, "canny", 1.0, "nms", 12, 22);
HOperatorSet.Threshold(imaAmp, out edges, 1, 255);
HOperatorSet.CloseEdgesLength(edges, imaAmp, out closedEdges, 8, 100);

closedEdges.Dispose();
edges.Dispose();
imaDir.Dispose();
imaAmp.Dispose();
image.Dispose();
```

---

## 六、工业应用最佳实践

1. **首选 `edges_sub_pix`**: 90%的工业测量场景都应首选，直接获取亚像素XLD轮廓
2. **噪声大时**: 先 `gauss_filter` 平滑，或使用 `derivate_gauss` 内建平滑
3. **需要封闭区域**: 用 `laplace_of_gauss` + `zero_crossing`
4. **边缘断裂**: 先检测再用 `close_edges_length` 补全
5. **调参顺序**: Alpha → High → Low → 检查结果
6. **资源释放**: 所有 HObject 必须 Dispose()
