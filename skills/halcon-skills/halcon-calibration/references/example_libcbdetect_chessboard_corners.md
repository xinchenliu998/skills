# libcbdetect — 棋盘格角点检测算法库深度解析

> 来源: `libcbdetect/` (MATLAB源码)
> 论文: *"Automatic Camera and Range Sensor Calibration using a single Shot"*, Andreas Geiger (KIT/MRT), ICRA 2012
> 许可证: GPL v3 ⚠️

---

## 一、库概述

**libcbdetect** 是一个纯 MATLAB 实现的棋盘格角点自动检测库，核心思想是使用**多尺度相关模板滤波**来检测棋盘格角点特有的四象限对称亮暗模式，并采用**种子生长+能量最小化**的贪心策略恢复棋盘格拓扑结构。

### 与传统方法的区别

| 方法 | 原理 | 棋盘格适应性 |
|---|---|---|
| Harris 角点 | 灰度梯度协方差特征值 | 通用角点，棋盘格上有大量误检 |
| `saddle_points_sub_pix` (Halcon) | 鞍点检测 | 专为棋盘格设计，但依赖灰度平滑 |
| **libcbdetect** (本库) | 四象限相关模板卷积 | ⭐专为棋盘格设计，抗噪声、抗畸变 |

### 三个核心模块

```
libcbdetect/
├── Phase 1: 角点检测 (findCorners + 附属函数)
│    使用6个多尺度多角度模板卷积 + 非极大值抑制 + 亚像素精炼 + 评分
│
├── Phase 2: 棋盘格结构恢复 (chessboardsFromCorners + 附属函数)
│    种子初始化3×3 → 贪心4方向生长 → 能量最小化 → 去重
│
└── Phase 3: 多图匹配 (matchChessboards + 附属函数, 可选)
      相似变换估计 → 跨图像棋盘格匹配 → 标定观测提取
```

---

## 二、算法流水线详析

### Phase 1: 角点检测 (findCorners.m)

```
输入: 灰度图像 I (uint8)
  │
  ▼
┌────────────────────────────────────────────────┐
│  Step 1.1: 梯度计算                            │
│  ├─ img_du, img_dv = Sobel(I)                 │
│  ├─ img_angle = atan2(dv, du) ∈ [0, π]        │
│  └─ img_weight = sqrt(du²+dv²) → [0,1]        │
└────────────────────┬───────────────────────────┘
                     │
                     ▼
┌────────────────────────────────────────────────┐
│  Step 1.2: 创建6个相关模板 (createCorrelationPatch)│
│                                                │
│  template_props = [                            │
│    angle1  angle2  radius                      │
│    0       π/2     4       % 水平+垂直 r=4    │
│    π/4    -π/4     4       % 对角45°  r=4     │
│    0       π/2     8       % 水平+垂直 r=8    │
│    π/4    -π/4     8       % 对角45°  r=8     │
│    0       π/2    12       % 水平+垂直 r=12   │
│    π/4    -π/4    12       % 对角45°  r=12    │
│  ];                                            │
│                                                │
│  每个模板 (2r+1)×(2r+1) 按两条法线划分4象限:    │
│  ┌─────┬─────┐                                │
│  │ a1  │ a2  │  法线1- → a1, 法线1+ → a2     │
│  ├─────┼─────┤  法线2- → a1, 法线2+ → b1     │
│  │ b1  │ b2  │  各象限内高斯核加权 (σ=r/2)   │
│  └─────┴─────┘                                │
└────────────────────┬───────────────────────────┘
                     │
                     ▼
┌────────────────────────────────────────────────┐
│  Step 1.3: 模板卷积 → 角点响应图                │
│                                                │
│  对每个模板 (k = 1..6):                        │
│    a1,a2,b1,b2 = 模板4个象限与图像卷积         │
│                                                │
│    case1 (a白b黑):                              │
│      corner1 = min(a1-μ, a2-μ, μ-b1, μ-b2)    │
│    case2 (b白a黑):                              │
│      corner2 = min(μ-a1, μ-a2, b1-μ, b2-μ)    │
│                                                │
│    img_corners_a = max(corner1, corner2, 0)    │
│    img_corners = max(all 6 templates)          │
└────────────────────┬───────────────────────────┘
                     │
                     ▼
┌────────────────────────────────────────────────┐
│  Step 1.4: 非极大值抑制 (nonMaximumSuppression) │
│  ├─ 窗口 n=3, 阈值 tau=0.025                   │
│  ├─ 边距 margin=4 → 滤除图像边缘附近候选点     │
│  └─ 输出: 候选角点坐标                          │
└────────────────────┬───────────────────────────┘
                     │
                     ▼
┌────────────────────────────────────────────────┐
│  Step 1.5: 亚像素精炼 (refineCorners, 可选)     │
│                                                │
│  方向精炼 (结构张量法):                          │
│  ├─ A1 = [Gx², GxGy; GxGy, Gy²] 高斯平滑      │
│  ├─ 特征分解 → v1, v2 (2个主方向)              │
│  └─ edgeOrientations: MeanShift找梯度方向模态  │
│                                                │
│  位置精炼 (最小二乘):                            │
│  ├─ G = [dx₁ dy₁; ...; dxₙ dyₙ]               │
│  ├─ b = [ΔI₁; ...; ΔIₙ]                       │
│  ├─ 求解 Gx = b → 亚像素位移 Δx, Δy            │
│  └─ IF ‖Δ‖ ≥ 4px → 标记为无效                  │
└────────────────────┬───────────────────────────┘
                     │
                     ▼
┌────────────────────────────────────────────────┐
│  Step 1.6: 角点评分 (scoreCorners)              │
│  ├─ 3个半径 [4,8,12] 上分别评分                 │
│  ├─ score = gradient_score × intensity_score   │
│  ├─ 梯度分: 归一化互相关, bandwidth=1.5px      │
│  ├─ 强度分: 复用模板评估棋盘格亮暗对比度         │
│  └─ 取3半径中的最高分 + 低分过滤 (score < τ)    │
└────────────────────┬───────────────────────────┘
                     │
                     ▼
┌────────────────────────────────────────────────┐
│  Step 1.7: 规范化输出                           │
│  ├─ 统一坐标系为右手系 (v1 × v2 > 0)            │
│  └─ 坐标转为 0-based                            │
│                                                │
│  输出: corners.p, .v1, .v2, .score             │
└────────────────────────────────────────────────┘
```

### Phase 2: 棋盘格结构恢复 (chessboardsFromCorners.m)

```
输入: corners 结构体
  │
  ▼
    对每个角点 i = 1..N 作为种子:
  │
  ├──→ ┌─────────────────────────────────────────┐
  │    │ initChessboard(corners, i)               │
  │    │  沿 v1+/v1-/v2+/v2- 4方向搜索邻居:       │
  │    │  ├─ directionalNeighbor 准则:             │
  │    │  │  dist = dist_point + 5×dist_edge      │
  │    │  │  (惩罚偏离方向线的点)                  │
  │    │  └─ 筛选出 3×3 = 9个角点                 │
  │    │                                          │
  │    │  验证均匀性:                              │
  │    │  └─ 两方向上间距 std/mean ≤ 0.3          │
  │    └─────────────────────────────────────────┘
  │
  ├──→ IF chessboardEnergy(chessboard) < 0:  // 有效
  │    │
  │    └──→ 循环生长 (直到能量不再降低):
  │          │
  │          ├─ 对4个方向各尝试 growChessboard:
  │          │  ├─ predictCorners: 角度+尺度外推
  │          │  │  a₃ = 2×a₂ - a₁  (角加速度模型)
  │          │  │  乘以因子 0.75 (偏好较近预测, 防畸变)
  │          │  ├─ assignClosestCorners: 贪心最近邻
  │          │  └─ 新增一行/列角点
  │          │
  │          ├─ 计算4个候选的 chessboardEnergy
  │          │  E = E_corners + size×E_structure
  │          │  E_corners = -(行×列)  鼓励大棋盘格
  │          │  E_structure = max(‖x₁+x₃-2x₂‖/‖x₁-x₃‖)
  │          │                 (惩罚共线性偏差)
  │          │
  │          ├─ IF 最优候选能量 < 当前能量:
  │          │    接受 → 继续循环
  │          └─ ELSE: 退出循环
  │
  └──→ IF 最终能量 < -10:
         ├─ 去重 (与已有棋盘格重叠 → 保留能量更低者)
         └─ 加入结果

  输出: chessboards{1..K}  每个是 M×N 角点索引矩阵
```

### Phase 3: 多图匹配 (matchChessboards.m, 可选)

```
对参考图/目标图中每对棋盘格组:
  ├─ 计算中心均值
  ├─ 通过两对棋盘格估计相似变换 (s, r, A, b)
  ├─ 投影目标棋盘格到参考坐标 + 贪心匹配
  ├─ 要求 ≥3 个棋盘格匹配成功
  └─ 对所有假设去重+排序+评分 → 最优匹配

observationsFromMatching:
  ├─ 生成 3D 坐标 (X × cornerdist 间隔)
  └─ 提取每相机 2D 观测 + 旋转矫正
```

---

## 三、关键数据结构

### corners 结构体（角点检测结果）

| 字段 | 维度 | 说明 |
|---|---|---|
| `.p` | N×2 double | 角点亚像素位置 (0-based) |
| `.v1` | N×2 double | 棋盘格第一主方向单位向量 |
| `.v2` | N×2 double | 棋盘格第二主方向单位向量 |
| `.score` | N×1 double | 角点质量评分 |

### chessboards（棋盘格拓扑）

```
chessboards : cell(1, K)
  chessboards{i} : M×N int32
    每个元素 = corners.p 中的索引
    0 = 该位置无角点（生长不完整）
```

### template 结构体（相关模板）

```
template.a1, .a2, .b1, .b2 : (2r+1)×(2r+1)
  4个象限, 按两条法线 v1/v2 划分, 高斯核加权
```

### BoardObservation（标定观测）

```
BoardObservation{cam}{board}
  .x      : 2×N   2D角点坐标
  .active : 1×N   角点有效性标记
  .size   : 1×2   棋盘格行列数 [rows, cols]
```

---

## 四、API 完整索引

### 主入口

| 函数 | 签名 | 说明 |
|---|---|---|
| `findCorners` ⭐ | `corners = findCorners(I, tau, refine_corners)` | 单图角点检测。`I`: uint8图像; `tau`: 评分阈值(0.01~0.02); `refine_corners`: 1=亚像素精炼, 0=不精炼 |
| `chessboardsFromCorners` ⭐ | `chessboards = chessboardsFromCorners(corners)` | 从角点恢复棋盘格拓扑结构 |
| `startMatching` | `[corners, chessboards, matching] = startMatching(I)` | 多相机完整流水线。`I`: cell array of images |

### 模板相关

| 函数 | 说明 |
|---|---|
| `createCorrelationPatch` | 创建棋盘格角点相关模板。`[a1,a2,b1,b2] = create(angle1, angle2, radius)` |
| `nonMaximumSuppression` | 非极大值抑制。`cands = nms(img_corners, n, tau, margin)` |

### 精炼与评分

| 函数 | 说明 |
|---|---|
| `refineCorners` | 亚像素精炼。`[p, v1, v2] = refine(Iu, Iv, I_angle, I_weight, p, r)` |
| `cornerCorrelationScore` | 单角点评分。`score = corrScore(Iu, Iv, I_angle, I_weight, p, v1, v2, r)` |
| `scoreCorners` | 批量角点评分（3半径取最优） |
| `cornerStatistics` | 角点统计（旧版，已弃用） |

### 棋盘格结构

| 函数 | 说明 |
|---|---|
| `initChessboard` ⭐ | 初始化3×3棋盘格。`cb = init(corners, seedIdx)` |
| `growChessboard` ⭐ | 向指定方向生长。`cb = grow(cb, corners, border_type)` border_type: 1=右, 2=下, 3=左, 4=上 |
| `chessboardEnergy` ⭐ | 能量评估。`E = energy(cb, corners)` E<0有效, E<-10高质量 |

### 多图匹配

| 函数 | 说明 |
|---|---|
| `matchChessboards` | 跨图像棋盘格匹配 |
| `observationsFromMatching` | 从匹配提取标定观测 |

### 可视化

| 函数 | 说明 |
|---|---|
| `plotChessboards` | 绘制棋盘格（粗红线+细白线双层连线） |
| `plotChessboardMatching` | 绘制多图匹配（多图垂直拼接+跨图对应关系） |
| `colorFromIndex` | 索引→18色映射（多棋盘格区分） |

---

## 五、MATLAB 使用示例

### 示例1: 单图棋盘格检测

```matlab
% demo.m 的完整流程
I = imread('data/04.png');                    % 读取图像
corners = findCorners(I, 0.01, 1);           % 角点检测 (阈值0.01, 亚像素)
chessboards = chessboardsFromCorners(corners); % 恢复棋盘格结构
plotChessboards(chessboards, corners);        % 可视化

% 查看结果
fprintf('检测到 %d 个角点\n', size(corners.p, 1));
fprintf('恢复出 %d 个棋盘格\n', numel(chessboards));
for k = 1:numel(chessboards)
    [rows, cols] = size(chessboards{k});
    E = chessboardEnergy(chessboards{k}, corners);
    fprintf('  棋盘格%d: %d×%d, 能量=%.2f\n', k, rows, cols, E);
end
```

### 示例2: 多相机标定流程

```matlab
% startMatching.m 的完整流程
I = {imread('cam0.png'), imread('cam1.png')};  % 多相机图像
[corners, chessboards, matching] = startMatching(I);

% 提取标定观测
[Board, BoardObservation, BoardCorner, ...
    points2d, points3d, camIdx] = ...
    observationsFromMatching(I, chessboards, corners, ...
        BoardObservation, Board, BoardCorner, [], matching);
```

### 示例3: 调整参数

```matlab
% 降低阈值 → 更多候选角点 (但更多误检)
corners = findCorners(I, 0.005, 1);

% 提高阈值 → 更严格 (但可能漏检)
corners = findCorners(I, 0.03, 1);

% 禁用亚像素 (更快, 但精度下降)
corners = findCorners(I, 0.01, 0);
```

---

## 六、HalconDotNet (C#) 迁移对照

### 核心算子映射

| libcbdetect (MATLAB) | Halcon (HalconDotNet) | 等价性 |
|---|---|---|
| `findCorners(I)` 模板卷积 | **无直接等价** | 需自行实现模板卷积 |
| `nonMaximumSuppression` | `nonmax_suppression_amp` | ~近似 |
| `refineCorners` 方向精炼 | `saddle_points_sub_pix` | ~近似 |
| `refineCorners` 位置精炼 | 无直接等价 | 需最小二乘 |
| `chessboardsFromCorners` | **无直接等价** | 需自行实现生长算法 |
| `initChessboard` (3×3) | `find_caltab` + `find_marks_and_pose` | 功能近似 |
| `matchChessboards` | 无直接等价 | 需估计相似变换 |

### Halcon 标准替代方案

```csharp
// Halcon 标准标定板角点检测 (需描述文件 .descr)
HOperatorSet.CreateCalibData("calibration_object", 1, 1, out HTuple calibID);
HOperatorSet.SetCalibDataCalibObject(calibID, 0, "caltab_30mm.descr");
HOperatorSet.FindCalibObject(ho_Image, calibID, 0, 0, 0, new HTuple(), new HTuple());

// 或使用 saddle_points_sub_pix (无描述文件)
HOperatorSet.SaddlePointsSubPix(ho_Image, "facet", 1.5, 20,
    out HTuple rows, out HTuple cols);
```

### 迁移建议：何时移植 libcbdetect 算法

| 场景 | 是否移植 |
|---|---|
| 有 Halcon 标定板描述文件 | ❌ 用 Halcon 原生 API 即可 |
| **无法获取描述文件**的自定义棋盘格 | ✅ 移植 `findCorners` 核心算法 |
| 棋盘格有**严重畸变或遮挡** | ✅ 移植生长算法 (Halcon 原生不够鲁棒) |
| 棋盘格角度未知、多尺度 | ✅ 移植多尺度多角度模板策略 |
| 只需简单角点坐标 | ❌ `saddle_points_sub_pix` 足够 |

### 移植核心算法到 C# 的骨架

```csharp
// 移植 findCorners 到 HalconDotNet 的概要骨架
static (double[] rows, double[] cols, double[] scores) FindCheckerCorners(
    HObject ho_Image, double tau, bool refine)
{
    // 1. 梯度计算
    HObject ho_Gray = null, ho_Du = null, ho_Dv = null;
    try
    {
        HOperatorSet.Rgb1ToGray(ho_Image, out ho_Gray);
        HOperatorSet.SobelAmp(ho_Gray, out ho_Du, out ho_Dv, "sum_abs", 3);
        // TODO: 计算 img_angle, img_weight
        // TODO: 6个模板卷积 (需逐像素实现4象限min操作)
    }
    finally { ho_Gray?.Dispose(); ho_Du?.Dispose(); ho_Dv?.Dispose(); }

    // 2. 非极大值抑制
    //    → nonmax_suppression_amp / 或手写滑窗

    // 3. 亚像素精炼
    //    → 结构张量法 / saddle_points_sub_pix

    // 4. 评分 + 过滤
    //    → 复用模板评估梯度一致性+强度对比度
}
```

---

## 七、关键技术细节

### 7.1 模板设计的数学原理

棋盘格角点本质是四条边交汇处，形成交替的亮暗象限。模板将 (2r+1)² 区域按两条法线 angle1/angle2 划分为4个理想象限：

```
        法线2+
          ↑
    ┌─────┼─────┐
    │ a1  │ a2  │
    │ - - │ + + │
法线1-←──────┼──────→ 法线1+
    │ b1  │ b2  │
    │ - + │ + - │
    └─────┼─────┘
          ↓
        法线2-
```

- `a1`: 法线1(-) ∩ 法线2(-) → 黑
- `a2`: 法线1(+) ∩ 法线2(+) → 黑
- `b1`: 法线1(+) ∩ 法线2(-) → 白
- `b2`: 法线1(-) ∩ 法线2(+) → 白

卷积后：
- case1 `min(a-μ, μ-b)`: a象限暗、b象限亮 → 角点响应
- case2 `min(μ-a, b-μ)`: a象限亮、b象限暗 → 角点响应（旋转180°）

### 7.2 多尺度策略的必要性

- `r=4`: 检测小棋盘格（远距离/高分辨率下的低分辨率棋盘格）
- `r=8`: 检测中等大小棋盘格（主流场景）
- `r=12`: 检测大棋盘格（近距离拍摄）

3个尺度×2个角度方向对=6个模板，覆盖所有旋转情况。

### 7.3 生长预测中的 replica prediction

```
predictCorners 不是简单的线性外推:
  x₃ = x₂ + (x₂ - x₁)  // 简单线性

而是:
  a₃ = 2×a₂ - a₁   // 角度加速度
  s₃ = 2×s₂ - s₁   // 尺度加速度
  乘以 0.75          // 在畸变时偏好较近预测
```

这使得算法能适应**镜头畸变导致的网格变形**。

### 7.4 能量函数的物理意义

```
E = E_corners + E_structure × size

E_corners = -(rows × cols)  负值, 棋盘格越大值越小(越好)
                            解释: 更多角点 = 更强的棋盘格证据

E_structure = max(‖x₁+x₃-2x₂‖ / ‖x₁-x₃‖)
             共线性偏差比率, 越小越好
             解释: 完美共线 → deviation=0 → 完美结构

size = max(rows, cols)  权值, 棋盘格越大对结构一致性要求越高
```

- E < 0: 棋盘格假设有效
- E < -10: 高质量棋盘格（保留标准）
- E 越负越好

### 7.5 directionalNeighbor 距离度量

```
dist = dist_point + 5 × dist_edge

dist_point: 候选角点到目标位置的欧氏距离
dist_edge:  候选角点到方向线的垂直距离

权重 5:1 意味着偏离方向线1px的惩罚 = 偏离目标点5px的惩罚
→ 强烈偏好沿方向线排列的角点
```

---

## 八、已知局限与注意事项

| 局限 | 说明 | 补救 |
|---|---|---|
| **GPL v3 许可证** ⚠️ | 代码有 copyleft 传染性，商用需注意 | 仅学习算法原理，独立实现 |
| **纯 MATLAB** | 无法直接在 .NET 项目中使用 | 移植算法到 C#/HalconDotNet |
| **无 Halcon 描述文件支持** | 输出棋盘格拓扑，非 Halcon 原生 calib_object | 转换坐标到 Halcon 格式 |
| **对极暗/极亮图像敏感** | Sobel 梯度在低对比度区域质量差 | 预处理增强对比度 |
| **棋盘格必须完整可见** | 算法假设能找到至少3×3的初始种子 | 可降低 initChessboard 均匀性阈值 |
| **计算量大** | 6个模板×全图卷积 ≈ 较大开销 | 缩小图像或减少半径 |

---

## 九、与本项目中 FocalCalib 的关系

本项目的 `FocalCalib/Program.cs` 已经实现了简易版棋盘格检测，方法路径为：

```
FocalCalib (当前实现):
  BinThreshold → SelectShape → BuildGrid → avgLen×2间距 → Harris回退

libcbdetect (本文件内容):
  多尺度模板卷积 → 亚像素精炼 → 评分 → 种子生长+能量最小化
```

**建议融合方向**：
1. 保留 `FocalCalib` 的 `BinThreshold` 快速二值化作为预处理
2. 在二值化结果上移植 libcbdetect 的**生长策略** (`growChessboard`, `chessboardEnergy`)
3. 用 `chessboardEnergy` 替代当前 `EstimateGridParams` 中的启发式评分
4. 保留 Harris 回退作为最终 fallback

---

*分析时间: 2026-05-19*
*文件数: 19个 (.m × 17, .m × 1(demo), .txt × 1)*