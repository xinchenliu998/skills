---
name: "chessboard_corner_detection"
description: "棋盘格角点多策略检测与焦距计算。当用户需要检测棋盘格角点、角点提取偏差大、低分辨率棋盘格、或涉及焦距三角关系计算时触发。"
---

# 棋盘格角点多策略检测与焦距计算

> 触发场景: "棋盘格角点"、"角点检测"、"角点偏移"、"角点在棋盘格内部"、"低分辨率棋盘格"、"焦距计算"
> 关联代码: ChessboardCorners/Program.cs
> 关联skill: focal_length_triangle.md, libcbdetect_chessboard_corners.md

---

## 一、问题背景

低分辨率棋盘格图像（如2.9μm像元）角点检测面临三大难题：

| 问题 | 原因 | 表现 |
|------|------|------|
| 角点偏移 | 低分辨率下灰度过渡模糊 | 检测角点偏离真实交叉点 |
| 角点在棋盘格内部 | 鞍点/Harris对棋盘格无选择性 | 检测点落在方块中心而非角点 |
| 不连通区域 | 阈值分割后黑白方块断裂 | 连通域过大或过小 |

---

## 二、四策略检测体系（按精度排序）

### 策略A: 边缘线段交叉 ⭐最精确（偏差3.7-4.3px）

**原理**: 提取棋盘格边缘线段，计算近似垂直线段的交叉点

```
EdgesSubPix(canny) → SelectContoursXld(长度筛选) → SegmentContoursXld(直线化)
→ 遍历线段对 → 角度差>20° → 计算交叉点 → 交叉点距两线段<5px
```

**核心代码**:
```csharp
HOperatorSet.EdgesSubPix(ho_Gray, out ho_Edges, "canny", 1.5, 20, 40);
HOperatorSet.SelectContoursXld(ho_Edges, out ho_Selected, "contour_length", 15, imgW+imgH, -1, -1);
HOperatorSet.SegmentContoursXld(ho_Selected, out ho_Lines, "lines", 5, 4, 2);
// 遍历线段对，角度差>0.35rad(≈20°)时计算交叉点
// 交叉点必须距两条线段都<5px
```

**适用场景**: 所有场景，尤其低分辨率图

**踩坑**:
- ❌ `GetContoursXld` 在 HalconDotNet 中不存在，用 `GetContourXld` 逐条获取
- ❌ 线段长度限制太严会丢失短边缘，太松会引入噪声线段。推荐 10-300px
- ❌ 角度差阈值 <0.35rad 会误合并近似平行线段

### 策略B: 梯度方向突变（偏差6.0-7.4px）

**原理**: 在梯度幅值大的区域，检测四象限对角灰度差远大于邻侧灰度差的点

```
SobelAmp → Threshold(>30) → 形态学开闭 → 遍历梯度区域像素
→ 取4象限灰度 → crossContrast = |TL-BR|+|TR-BL|
→ cornerScore = crossContrast - meanAdj×0.5 → 非极大值抑制
```

**核心代码**:
```csharp
// 用 GetImagePointer1 一次性获取像素数组，比逐像素 GetGrayval 快100倍
HOperatorSet.GetImagePointer1(ho_Gray, out HTuple hv_Ptr, out HTuple hv_Type, out HTuple hv_W, out HTuple hv_H);
IntPtr imgPtr = new IntPtr(hv_Ptr.L);
byte[] pixels = new byte[imgW * imgH];
System.Runtime.InteropServices.Marshal.Copy(imgPtr, pixels, 0, pixels.Length);

double tl = pixels[(r - step) * imgW + (c - step)];
double tr = pixels[(r - step) * imgW + (c + step)];
double bl = pixels[(r + step) * imgW + (c - step)];
double br = pixels[(r + step) * imgW + (c + step)];
```

**踩坑**:
- ❌ **绝对不要用 `GetGrayval` 逐像素读取**！2688×1520图像逐2px采样约100万次调用，耗时>60秒
- ✅ 用 `GetImagePointer1` + `Marshal.Copy` 一次性拷贝到byte[]，耗时<10ms
- ❌ step=3太小对低分辨率图噪声敏感，step=4-5更稳定
- ❌ `GetImagePointer1` 返回的指针是 `IntPtr`，不能直接当byte[]用

### 策略C: 局部象限灰度棋盘格模式（偏差5.9-8.1px）

**原理**: 全图逐像素（间隔2px）计算四象限棋盘格对比度分数

```
MedianImage(平滑) → 全图扫描 → 4象限灰度
→ score1 = |avg(上)-avg(下)|, score2 = |avg(左)-avg(右)|
→ checkerScore = diagContrast - sameContrast×0.3
→ totalScore = (score1+score2)×0.5 + checkerScore×0.5
→ 非极大值抑制(最小间距10px)
```

**踩坑**:
- ❌ 同样不能用 `GetGrayval`，必须用像素数组
- ❌ 阈值 totalScore>25 太低会引入大量噪声点，>35又可能漏检
- ✅ 非极大值抑制用最小间距10px（100平方）效果较好

### 策略D: 改进鞍点检测（偏差5.6-10.8px，最差但数量最多）

**原理**: 多尺度预处理 + 多参数SaddlePointsSubPix

```
Emphasize(7,7,1.5) + MedianImage(circle,1) → AddImage(0.5,0)融合
→ 遍历 sigma×thresh 组合 → 选角点数100-8000中最多的一组
```

**踩坑**:
- ❌ **GaussFilter sigma=1.0 会报错**！Halcon要求滤波器尺寸不超过图像尺寸，sigma太小导致滤波器核尺寸异常
- ✅ 用 MedianImage 替代 GaussFilter，更稳定
- ❌ 鞍点在低分辨率图上产生大量虚假角点（6000+），真正的角点被淹没
- ❌ 鞍点检测对"角点在棋盘格内部"问题无能为力——方块中心也是鞍点

---

## 三、策略融合优先级

```
优先级: 边缘交叉(A) > 梯度突变(B) > 象限棋盘(C) > 鞍点(D)

融合流程:
1. 融合A+B+C → 去重(3px) → 估计间距 → RANSAC网格 → 追踪
2. 若追踪不足11点 → 融合鞍点(D)重试
3. 若仍不足 → 返回null
```

**踩坑**:
- ❌ **不要把所有策略一次性融合**！鞍点6000+个会严重拉低间距估计
- ✅ 先用A+B+C建立基准，鞍点仅作补充
- ❌ 去重间距太小(1-2px)导致角点堆积，太大(>5px)导致真实角点被误删

---

## 四、RANSAC网格拟合

**原理**: 将角点投影到不同角度/间距的网格坐标系，找最佳匹配

```
遍历: 6种间距 × 62种角度(30°-60°, 120°-150°)
→ 每组参数: 投影所有角点到网格 → 统计填充率
→ score = cells × fillRate² × (1-overlapPenalty)
→ 选最高分的参数组
```

**踩坑**:
- ❌ 角度搜索范围30°-60°+120°-150°是关键！棋盘格对角线方向约45°/135°
- ❌ fillRate的平方权重很重要——稀疏但规则的网格比密集但混乱的网格得分高
- ✅ overlapPenalty惩罚每个网格格内平均点数>1.5的情况

---

## 五、角点追踪链

**原理**: 从中心角点向左右各追踪5步，形成11点链

```
1. 找距图像中心最近的网格角点作为起点
2. 向左/右方向搜索: 步距在expectedStep±40%内, 行偏移<expectedStep×0.6
3. 评分: distErr + rowErr×4 + vecConsistencyPenalty + (非网格点+5)
4. 自适应步距: 已追踪2步后用实际平均步距替代理论步距
5. 方向向量一致性: 点积惩罚偏离初始方向的候选点
```

**踩坑**:
- ❌ **rowTol = gp.Spacing×0.8 太严格**！当网格角度接近45°时，实际步距≈Spacing×1.41，行偏移可达Spacing×0.7
- ✅ rowTol = expectedStep×0.6 更合理
- ❌ 不用自适应步距会导致追踪后期跳点——理论步距和实际步距可能有20%偏差
- ✅ 方向向量一致性惩罚(点积)是防止追踪跳到错误行的关键

---

## 六、亚像素精化

**原理**: 在追踪角点周围10px窗口内用SaddlePointsSubPix精确定位

```
对每个追踪角点:
1. GenRectangle1(10px窗口) → ReduceDomain → SaddlePointsSubPix(facet,1.0,3.0)
2. 选距原始点最近的鞍点
3. 若无鞍点 → 用棋盘格对比度局部搜索(±3px)找最佳位置
```

**踩坑**:
- ❌ SaddlePointsSubPix阈值太高(>5.0)会漏掉真实角点
- ✅ 阈值3.0比5.0更敏感，能找到更多真实角点
- ❌ 窗口太大(>15px)可能引入邻近角点的鞍点
- ✅ 棋盘格对比度局部搜索是关键兜底——当鞍点检测失败时，在±3px范围内找对角灰度差最大的点

---

## 七、性能优化要点

| 优化 | 效果 | 说明 |
|------|------|------|
| GetImagePointer1+Marshal.Copy | 100x→<10ms | 替代GetGrayval逐像素读取 |
| 像素数组索引 pixels[r*W+c] | O(1)访问 | 替代Halcon算子逐像素操作 |
| 空间哈希去重 | O(N)→O(N/k) | 网格化分桶避免全量比较 |
| 间距估计采样300点 | 稳定且快速 | 不需要遍历所有点对 |

---

## 八、实测偏差数据

| 策略 | 7451-2.9um | 7485-2um | 推荐度 |
|------|-----------|---------|--------|
| 边缘线段交叉 | 3.7-4.3px | 3.7-4.3px | ⭐⭐⭐ |
| 梯度方向突变 | 7.1-7.4px | 6.0-7.2px | ⭐⭐ |
| 象限棋盘格 | 7.1-8.1px | 5.9-6.8px | ⭐⭐ |
| 鞍点检测 | 9.1-10.8px | 5.6-10.8px | ⭐ |

### 焦距一致性验证

| 相机 | 旧版焦距(3图) | 新版焦距(3图) | 改进 |
|------|-------------|-------------|------|
| 7451-2.9um | 5.035/4.534/4.773 (σ=0.26) | 5.040/5.062/5.019 (σ=0.022) | σ降低92% |
| 7485-2um | 失败/2.568/2.547 | 2.568/2.568/2.562 (σ=0.003) | 全部成功 |

---

## 九、Halcon API 踩坑速查

| 错误写法 | 正确写法 | 说明 |
|---------|---------|------|
| `JunctionsSkel` | `JunctionsSkeleton` | HalconDotNet中骨架算子命名 |
| `GetPointsSkel` | `GetRegionPoints` | 获取区域像素坐标 |
| `Corners` | 不存在 | HalconDotNet无此算子，用PointsHarris替代 |
| `GetContoursXld` | `GetContourXld` | 单数形式，逐条轮廓获取 |
| `BinaryThreshold(..., "dark")` | `BinaryThreshold(..., "dark", out _)` | 需要out参数接收阈值 |
| `GaussFilter(img, out, 1.0)` | 避免sigma=1.0 | 可能报滤波器尺寸错误 |
| `GetGrayval`逐像素 | `GetImagePointer1`+Marshal.Copy | 性能差100倍 |
| `hv_Ptr.L`当byte[] | `new IntPtr(hv_Ptr.L)` | 指针类型转换 |

---

*更新时间: 2026-05-20*
*关联代码: ChessboardCorners/Program.cs*
