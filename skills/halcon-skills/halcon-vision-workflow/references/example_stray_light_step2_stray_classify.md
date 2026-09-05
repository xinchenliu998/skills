# Step 2: 杂光检测 - 逐光源光刺检测（核心步骤）v21

## 目标
对每个光源，在其周围检测"光刺"（放射状亮条），测量径向长度，判定是否超出180px蓝色圈。

## 关键经验总结（110张实测数据，v13→v22迭代）

### v21最优光刺参数
| 参数 | 值 | 说明 |
|------|-----|------|
| MIN_SPIKE_AREA | 80 | 光刺最小面积 |
| MAX_SPIKE_AREA | 1200 | 排除散射光晕 |
| MIN_SPIKE_ANISOMETRY | 4.0 | 光刺必须细长 |
| MIN_SPIKE_GRAY_RATIO | 1.8 | 灰度比背景亮80%+ |
| MIN_RADIAL_SPAN | 50 | 径向跨度≥50px |
| MAX_CORE_GAP | 15 | 最近点距核心≤15px |
| MIN_SPIKE_ABS_GRAY | 55 | 绝对灰度≥55 |
| 角度跨度上限 | 30° | 真光刺角度窄 |

### 反光胶布边缘过滤（v19新增，关键！）
| 参数 | 值 | 说明 |
|------|-----|------|
| EDGE_MARGIN | 80 | 图像边缘80px内 |
| SPECULAR_THRESHOLD | 200 | 高亮灰度阈值 |
| SPECULAR_DILATE | 30 | 反光区域膨胀30px |

算法：在图像边缘80px带状区域检测灰度>200的高亮区域，膨胀30px后作为全局排除掩膜。从光刺候选中Difference掉该掩膜区域，有效过滤反光胶布边缘产生的假光刺。

### 参数调优历史（防止重复踩坑）
| 版本 | 参数变化 | TP | FP | 说明 |
|------|---------|-----|-----|------|
| v13 | aniso=4,ratio=1.8,无反光过滤 | 14 | 3 | 旧最优 |
| v18 | aniso=2.5,ratio=1.3(极松) | 40 | 70 | 全判NG |
| v19 | aniso=3,ratio=1.5+反光过滤 | 39 | 62 | 仍太松 |
| v20 | +异型收紧(circ<0.08) | 16 | 13 | FP仍高 |
| **v21** | **aniso=4,span=50+反光过滤** | **11** | **2** | **精确率84.6%** |
| v22 | aniso=3.5,span=45(微放) | 11 | 4 | 不如v21 |

### 核心教训
1. **反光胶布过滤是FP下降的关键** - v21比v13少1个FP
2. **光刺标准太松FP飙升** - aniso<3.5或ratio<1.6都会大幅增加FP
3. **异型光斑门槛要极严** - circ<0.08才是真异型(0.43/0.72都是正常光斑)
4. **微调放松不一定有效** - v22比v21松一点,FP多2个但TP不变

## 处理流程

### 2.0 反光胶布边缘检测（全局预处理）
```csharp
// 图像边缘80px带状区域
GenRectangle1 → Difference → edgeBand
// 检测高亮+膨胀 → specularExcludeMask
Threshold(edgeImg, edgeBright, 200, 255)
DilationCircle(edgeBright, specularExcludeMask, 30)
```

### 2.1 构建分析ROI（排除邻居光源）
排除所有相邻光源3倍半径区域

### 2.2 动态阈值+形状筛选+反光排除
```csharp
DynThreshold → SelectShape → Difference(specularExcludeMask)
```

### 2.3 多重验证（逐候选检查）
1. 灰度对比度: spikeMean ≥ bgMean×1.8 且 ≥55
2. 径向连续性: 核心间距≤15px, 径向跨度≥50px
3. 角度宽度: <30°

## 输出
- HasSpike = maxRadialDist > 90px
- MaxSpikeLength = 最大径向距离

## 性能基准（v21, 110张）
- TP=11, FP=2, TN=68, FN=29
- 准确率=71.8%, **精确率=84.6%（历史最高）**
