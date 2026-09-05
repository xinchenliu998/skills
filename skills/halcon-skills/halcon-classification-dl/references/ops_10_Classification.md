# HALCON 算子分类详解：Classification（经典机器学习分类）

> **分类**：Classification / Classic Machine Learning Classification
> **子类数**：7 个（Gaussian Mixture、KNN、Look-up Table、Misc、MLP、SVM、Box）
> **学习优先级**：⭐⭐⭐（⭐ 入门 / ⭐⭐⭐⭐⭐ 必精）
> **典型应用场景**：少样本工业图像分类、纹理/缺陷分级、零件多类分拣、颜色/形状判别、轻量级异常检测。

---

## 1. 概述

Classification（经典机器学习分类）是 HALCON 中面向**少样本、非深度学习**分类任务的算子家族，约含 **70 个算子**。它不专门针对字符（那是 OCR），而是通用的二维特征分类器——给定一个图像 Region，输出对应的类别。

HALCON Classification 的核心特点：

- **多种经典算法**：MLP（神经网络）、SVM（支持向量机）、KNN（K 近邻）、GMM（高斯混合模型），覆盖工业分类主流。
- **手工特征 + 训练数据分离**：用户先提取特征（用 `gen_feature_vectors_for_class_train_data` 或自定义），再用分类器训练。
- **训练数据结构 `ClassTrainDataHandle`**：抽象训练数据集容器，统一管理特征向量与标签。
- **LUT 加速**：`create_class_lut` 把训练结果做成查找表，推理速度提升 10–100 倍。
- **可与 Region 算子无缝组合**：典型用法是 `area_center` + `moments_*` + `gray_features` → 特征向量 → 分类。

> **何时用 Classification**：样本数 < 5000；特征维度 < 100；训练时间 < 1 小时；不需要 GPU。**否则建议直接上 Deep Learning**。

---

## 2. 应用场景

1. **木材与纺织品**：木纹/布纹分级、缺陷分类（划伤、污渍、破洞）。
2. **食品与农业**：水果分级（颜色 + 形状 + 表面纹理）、坚果合格判定。
3. **金属与机械**：零件表面缺陷类型分类（划痕、氧化、凹坑、麻点）。
4. **电池与新能源**：电池极片涂层缺陷（漏箔、划痕、颗粒）、电芯外观分级。
5. **3C 装配**：PCB 元件分类（电阻/电容/IC）、焊接质量分级。
6. **多类计数与分拣**：包装产品按颜色/大小分拣。

---

## 3. 子分类详解

| 子分类 | 核心算子 | 典型用途 |
|--------|----------|----------|
| **MLP (Neural Nets)** | `create_class_mlp`, `add_class_train_data_mlp`, `train_class_mlp`, `classify_class_mlp`, `classify_image_class_mlp`, `read/write_class_mlp` | 通用非线性，工业首选 |
| **SVM** | `create_class_svm`, `add_class_train_data_svm`, `train_class_svm`, `classify_class_svm`, `classify_image_class_svm`, `reduce_class_svm`, `read/write_class_svm` | 小样本高维特征 |
| **KNN** | `create_class_knn`, `add_class_train_data_knn`, `train_class_knn`, `classify_class_knn`, `classify_image_class_knn`, `read/write_class_knn` | 极小样本、特征可分 |
| **Gaussian Mixture** | `create_class_gmm`, `add_class_train_data_gmm`, `train_class_gmm`, `classify_class_gmm`, `classify_image_class_gmm`, `read/write_class_gmm` | 概率输出、异常检测 |
| **Look-up Table (LUT)** | `create_class_lut_gmm/knn/mlp/svm`, `classify_image_class_lut`, `clear_class_lut`, `set_class_lut_*` | 训练结果查表加速 |
| **Box (legacy)** | `create_class_box`, `classify_class_box`, `learn_class_box`, `learn_class_box_ndim`, `set_class_box_*` | 特征空间矩形分类（已不推荐） |
| **Misc** | `create_class_train_data`, `add_class_train_data_*`, `get_class_train_data_*`, `get_sample_class_*`, `select_feature_set_*`, `deserialize_class_train_data` | 训练数据管理 |

**算法选择对比表**：

| 算法 | 适用样本量 | 训练速度 | 推理速度 | 特征维度 | 概率输出 | 可解释 | 异常检测 |
|------|------|------|------|------|------|------|------|
| **MLP** | 50–5000 | 中 | 快 | < 100 | 软输出 | 难 | 弱 |
| **SVM** | 20–2000 | 快 | 快 | < 1000 | 需概率校准 | 中 | 弱 |
| **KNN** | < 500 | 极快 | 慢 | < 50 | 否 | 强 | 弱 |
| **GMM** | 100–5000 | 快 | 快 | < 50 | 是 | 强 | 强 |
| **LUT** | 任意 | — | 极快 | 量化后 | 否 | 强 | 弱 |

---

## 4. 核心算子详解

### 4.1 训练数据管理

| 算子 | 作用 |
|------|------|
| `create_class_train_data(NumFeatures, ClassTrainDataHandle)` | 创建训练数据容器（指定特征维度） |
| `add_class_train_data_mlp(ClassTrainDataHandle, Features, Class)` | 向 MLP 训练数据添加样本 |
| `add_class_train_data_svm` / `add_class_train_data_knn` / `add_class_train_data_gmm` | 同上 |
| `get_class_train_data_mlp(ClassTrainDataHandle, Class, Features)` | 取出数据样本 |
| `get_sample_class_*` | 按索引取样本 |
| `select_feature_set_knn` / `select_feature_set_mlp` / `select_feature_set_svm` | 自动特征筛选 |

### 4.2 MLP 分类器

| 算子 | 作用 |
|------|------|
| `create_class_mlp(NumInput, NumHidden, NumOutput, OutputFunction, Preprocessing, NumComponents, RandSeed, MLPHandle)` | 创建 MLP 句柄 |
| `train_class_mlp(MLPHandle, MaxIterations, WeightTolerance, ErrorTolerance, Error, ErrorLog)` | 训练 |
| `classify_class_mlp(Features, MLPHandle, Num, Class, Confidence)` | 单样本分类 |
| `classify_image_class_mlp(Image, Region, MLPHandle, ClassRegions)` | 像素级分类（语义分割用） |
| `read_class_mlp` / `write_class_mlp` | 持久化 |

### 4.3 SVM 分类器

| 算子 | 作用 |
|------|------|
| `create_class_svm(NumFeatures, KernelType, KernelParam, Nu, NumClasses, Mode, Preprocessing, NumComponents, SVMHandle)` | 创建 SVM |
| `train_class_svm(SVMHandle, Epsilon, TrainMode)` | 训练 |
| `classify_class_svm(Features, SVMHandle, Num, Class)` | 分类 |
| `reduce_class_svm(SVMHandle, Method, MinRemainingSV, MaxIterations, SVMHandleReduced)` | 减少支持向量提速 |
| `classify_image_class_svm` | 像素级分类 |

> `KernelType` ∈ `'linear'`, `'rbf'`, `'polynomial'`, `'sigmoid'`；`Nu` ∈ (0, 1] 控制误判率。

### 4.4 KNN 分类器

| 算子 | 作用 |
|------|------|
| `create_class_knn(NumFeatures, K, DistanceMethod, NumClasses, KNNHandle)` | 创建 KNN |
| `train_class_knn(KNNHandle, ...)` | "训练"（仅存储） |
| `classify_class_knn(Features, KNNHandle, Num, Class, Rating)` | 分类 |

> `DistanceMethod` ∈ `'euclidean'`, `'sublinear'`, `'max'`, `'min'`, `'mean'`, `'min-min'`。

### 4.5 GMM 分类器

| 算子 | 作用 |
|------|------|
| `create_class_gmm(NumDim, NumClasses, CovarType, Preprocessing, NumComponents, RandSeed, GMMHandle)` | 创建 GMM |
| `train_class_gmm(GMMHandle, MaxIterations, Regularization, Epsilon, ClassPriors)` | 训练 |
| `classify_class_gmm(Features, GMMHandle, Num, Class, Probability)` | 分类（输出概率） |
| `classify_image_class_gmm` | 像素级分类 |

### 4.6 LUT 查找表加速

| 算子 | 作用 |
|------|------|
| `create_class_lut_mlp(MLPHandle, NumIntervals, ClassLUTHandle)` | MLP → LUT |
| `create_class_lut_svm` / `create_class_lut_knn` / `create_class_lut_gmm` | 同上 |
| `classify_image_class_lut(Image, ClassRegions, ClassLUTHandle, Classes)` | LUT 推理（极快） |
| `clear_class_lut(ClassLUTHandle)` | 释放 LUT |

---

## 5. HDevelop 示例代码

### 5.1 示例一：SVM 工业零件缺陷分类（完整流程）

```hdevelop
* ============================================================
* 经典 SVM 分类：3 类缺陷（划伤、凹坑、正常）
* 场景：金属零件表面分类
* ============================================================
dev_update_off ()
dev_close_window ()

* --- 1. 准备训练数据（特征 = 区域 + 灰度特征） ---
* 假设已用 Region 算子提取每个 ROI 的特征向量
* 特征维度：12（面积、圆度、紧凑度、3 个灰度统计、3 个纹理、3 个形状）
* 类别：0=正常, 1=划伤, 2=凹坑

create_class_train_data (12, TrainDataHandle)

* 模拟添加 60 个样本
FeaturesNormal := [1200.0, 0.85, 0.80, 110.0, 12.0, 0.30, 0.50, 0.40, 0.20, 0.10, 5.0, 1.2]
FeaturesScratch := [800.0, 0.40, 0.30, 95.0, 25.0, 0.85, 0.20, 0.10, 0.05, 0.60, 20.0, 3.5]
FeaturesDent := [2000.0, 0.65, 0.55, 105.0, 18.0, 0.55, 0.35, 0.25, 0.15, 0.40, 12.0, 2.1]

for i := 1 to 20 by 1
    * 添加噪声模拟真实样本
    FNormal := FeaturesNormal + tuple_rand(12) * 5.0
    FScratch := FeaturesScratch + tuple_rand(12) * 5.0
    FDent := FeaturesDent + tuple_rand(12) * 5.0
    add_class_train_data_svm (TrainDataHandle, FNormal, 0)
    add_class_train_data_svm (TrainDataHandle, FScratch, 1)
    add_class_train_data_svm (TrainDataHandle, FDent, 2)
endfor

* --- 2. 训练 SVM ---
create_class_svm (12, 'rbf', 0.02, 0.05, 3, 'one-versus-all', 'normalization', 5, 42, SVMHandle)
train_class_svm (SVMHandle, 0.001, 'default')
write_class_svm (SVMHandle, 'defect_svm_model.csm')

* --- 3. 推理（推理一张新图） ---
read_image (NewImage, 'metal_part_01')
dev_open_window_fit_image (NewImage, 0, 0, -1, -1, WindowHandle)
dev_display (NewImage)

* 提取特征（假设已通过预处理得到）
TestFeatures := [1150.0, 0.83, 0.78, 112.0, 13.0, 0.32, 0.48, 0.42, 0.21, 0.12, 5.5, 1.3]

classify_class_svm (TestFeatures, SVMHandle, 1, Class, Score)
ClassNames := ['正常', '划伤', '凹坑']
set_display_font (WindowHandle, 24, 'mono', 'true', 'false')
disp_message (WindowHandle, '结果: ' + ClassNames[Class], 'window', 10, 10, 'green', 'true')
```

### 5.2 示例二：MLP 像素级语义分割（classify_image_class_mlp）

```hdevelop
* ============================================================
* 像素级 MLP 着色：把二值 mask 分类为 3 类（红/绿/蓝）
* ============================================================
dev_update_off ()
read_image (Image, 'color_blobs_01')
get_image_size (Image, Width, Height)
dev_open_window (0, 0, Width, Height, 'black', WindowHandle)
dev_display (Image)

* --- 1. 提取 ROI 区域 ---
decompose3 (Image, R, G, B)
threshold (R, MaskR, 200, 255)
threshold (G, MaskG, 200, 255)
threshold (B, MaskB, 200, 255)
union1 (MaskR, MaskR)
union1 (MaskG, MaskG)
union1 (MaskB, MaskB)

* 把所有目标区域合并
union1 (MaskR, RegionRed)
union1 (MaskG, RegionGreen)
union1 (MaskB, RegionBlue)
concat_obj (RegionRed, RegionGreen, Tmp)
concat_obj (Tmp, RegionBlue, AllRegions)

* --- 2. 训练 MLP（3 类：0=红, 1=绿, 2=蓝） ---
create_class_mlp (3, 20, 3, 'softmax', 'normalization', 3, 42, MLPHandle)
* 训练数据：R/G/B 像素值
for i := 1 to 100 by 1
    rand_xyz := tuple_rand(3) * 255.0
    add_class_train_data_mlp (TrainDataHandle, rand_xyz, 0)
endfor
* 实际训练代码...
train_class_mlp (MLPHandle, 200, 1.0, 0.01, Error, ErrorLog)

* --- 3. 像素级分类 ---
classify_image_class_mlp (Image, AllRegions, MLPHandle, ClassRegions)
count_obj (ClassRegions, NumClasses)
num_features (ClassRegions, Features)
* 给每个区域染不同颜色
Colors := ['red', 'green', 'blue']
for c := 0 to NumClasses - 1 by 1
    select_obj (ClassRegions, ClassRegion, c + 1)
    dev_set_color (Colors[c])
    dev_display (ClassRegion)
endfor
```

### 5.3 示例三：GMM 异常检测（训练只用正常样本）

```hdevelop
* ============================================================
* GMM 单类异常检测：训练只用 OK 样本，推理时输出概率
* ============================================================
dev_update_off ()
read_image (Image, 'pcb_01')
get_image_size (Image, W, H)
dev_open_window (0, 0, W, H, 'black', WindowHandle)
dev_display (Image)

* --- 1. 准备训练数据（只用 OK 样本的特征） ---
create_class_train_data (5, TrainData)
* 假设：5 维特征 = 面积、灰度均值、灰度方差、纹理、紧凑度
for i := 1 to 50 by 1
    Feature := [800.0 + tuple_rand(1) * 50, 120.0 + tuple_rand(1) * 10, \
                15.0 + tuple_rand(1) * 3, 0.3 + tuple_rand(1) * 0.05, \
                0.7 + tuple_rand(1) * 0.05]
    add_class_train_data_gmm (TrainData, Feature, 0)
endfor

* --- 2. 训练 GMM ---
create_class_gmm (5, 1, 'spherical', 'normalization', 5, 42, GMMHandle)
train_class_gmm (GMMHandle, 100, 0.001, 0.001, [1.0])

* --- 3. 推理 ---
TestFeature := [800.0, 120.0, 15.0, 0.3, 0.7]
classify_class_gmm (TestFeature, GMMHandle, 1, Class, Probability)
* Probability < 0.01 视为异常
if (Probability < 0.01)
    disp_message (WindowHandle, '异常!', 'window', 10, 10, 'red', 'true')
else
    disp_message (WindowHandle, 'OK', 'window', 10, 10, 'green', 'true')
endif
```

### 5.4 示例四：LUT 加速推理（实时产线）

```hdevelop
* ============================================================
* 把 SVM 转 LUT，推理速度提升 10-100 倍
* ============================================================
* 训练 SVM 后...
read_class_svm ('defect_svm.csm', SVMHandle)

* --- 转换为 LUT ---
NumIntervals := 10
create_class_lut_svm (SVMHandle, NumIntervals, ClassLUTHandle)

* --- 处理实时图（批量 pixel 级） ---
* acquire_image (Image, AcqHandle)  <- 实时相机
* classify_image_class_lut (Image, RegionMask, ClassLUTHandle, ClassImage)
* 推理速度：LUT ≈ 0.5ms / 帧，SVM 原生 ≈ 20ms / 帧

write_class_lut (ClassLUTHandle, 'defect_lut.clt')
```

---

## 6. 典型工业流水线

### 6.1 通用分类流程（以 SVM 为例）

```
1. 图像采集 → grab_image
2. 预处理 → median_image → emphasize
3. 区域分割 → threshold → connection
4. 特征提取 → area_center, gray_features, moments_*
5. 归一化 → (Feature - Mean) / Std
6. 分类 → classify_class_svm
7. 业务规则 → 类别 → 决策
8. 控制输出 → 串口 / 网口 / PLC
```

### 6.2 多类计数与分拣流水线

```
1. 采集图像 → read_image
2. 颜色分割 → trans_from_rgb → threshold
3. 形态学清理 → opening_circle, fill_up
4. 多类分割 → connection + select_shape (按颜色 + 形状)
5. 逐 ROI 特征提取 → 12 维特征向量
6. 分类 → classify_class_mlp
7. 决策表 → 类别 → 喷阀信号 / 推送指令
```

### 6.3 异常检测流程（仅 OK 样本）

```
1. 采集 OK 样本图（≥ 100 张）
2. 提取 ROI + 特征
3. 训练 GMM（单类） / KNN / Box
4. 推理：输出概率，与阈值比较
5. 概率 < 阈值 → NG
```

---

## 7. 常见陷阱与最佳实践

### 7.1 特征工程

- **特征归一化是必需品**：`Preprocessing='normalization'` 或 `Preprocessing='principal_components'`。
- **特征维度** ≥ 样本数时 → 必用 `'principal_components'` 降维。
- **冗余特征反而拉低精度**：用 `select_feature_set_svm` 自动筛选。
- **特征维度不要超过 50**（SVM）/ 100（MLP），否则速度慢、过拟合。

### 7.2 样本不均衡

- **类别样本数差异 > 10 倍** → 模型偏向大样本。
- **解决方案**：
  - `set_class_mlp('class_weights', [w1, w2, ...])` 调整权重。
  - SVM `Nu` 参数调节误判率。
  - 自定义 `class_priors`（GMM）。
  - **过采样 SMOTE**（自实现，需要借助 `gen_feature_vectors_for_class_train_data`）。
- **类别 < 3 个**：考虑二分类或一分类异常检测。

### 7.3 训练 / 推理一致性

- **归一化参数需在同一流程中计算并存盘**：`Mean` / `Std` 在训练时计算，推理时复用。
- **降维模型**（PCA）必须保存同样的 `NumComponents` 与 `TransformationMatrix`。
- **特征提取顺序**：必须严格一致，否则根本性错误。

### 7.4 模型选择陷阱

- **小样本 ≤ 30/类**：KNN、SVM 优先；MLP 易过拟合。
- **大样本 ≥ 1000/类**：MLP 性能更好。
- **需要概率输出**：用 GMM 或 SVM + `classify_class_svm` 的 `Score`。
- **需要异常检测**：GMM 单类、KNN 距离、SVM `Nu` 调节。

### 7.5 模型部署

- **LUT 加速**：训练完成后必转 LUT，推理速度提升 10–100 倍。
- **模型大小**：SVM 在样本多时支持向量爆炸，用 `reduce_class_svm` 压缩。
- **跨平台**：训练和部署用同一 HALCON 版本，避免模型不兼容。
- **GPU 加速**：经典分类器不支持 GPU，建议升级到 Deep Learning。

### 7.6 验证与评估

- **必须 K 折交叉验证**：训练集准确率 ≠ 真实精度。
- **混淆矩阵**：用 `get_class_train_data_*` 统计每类召回率。
- **ROC 曲线**：输出 `Score` 时画 `tuple_chi_square` 拟合。
- **置信度阈值**：业务侧设定 Low / High 阈值，对应"OK / 复检 / NG"。

---

## 8. 参数调优指南

### 8.1 SVM 关键参数

| 参数 | 推荐值 | 说明 |
|------|--------|------|
| `KernelType` | `'rbf'` | 工业首选 |
| `KernelParam` (γ) | `1.0 / NumFeatures` | RBF 核宽 |
| `Nu` | 0.05–0.1 | 误判上界 |
| `Mode` | `'one-versus-all'` | 多分类 |
| `Preprocessing` | `'normalization'` 或 `'principal_components'` | 必做 |
| `NumComponents` | 保留 95% 方差 | PCA 降维 |

### 8.2 MLP 关键参数

| 参数 | 推荐值 | 说明 |
|------|--------|------|
| `NumHidden` | `(NumInput + NumOutput) * 2` | 隐藏神经元数 |
| `OutputFunction` | `'softmax'` | 多类互斥 |
| `MaxIterations` | 200–500 | 训练最大迭代 |
| `WeightTolerance` | 1.0 | 早停阈值 |
| `ErrorTolerance` | 0.01 | 早停阈值 |

### 8.3 KNN 关键参数

| 参数 | 推荐值 | 说明 |
|------|--------|------|
| `K` | `sqrt(NumSamples)` | K 值选择 |
| `DistanceMethod` | `'euclidean'` | 距离度量 |
| 投票权重 | `'uniform'` / `'distance'` | 加权投票 |

### 8.4 GMM 关键参数

| 参数 | 推荐值 | 说明 |
|------|--------|------|
| `NumComponents` | 5–10 | 高斯分量数 |
| `CovarType` | `'spherical'` | 协方差类型 |
| `Regularization` | 0.001 | 防止奇异 |
| `ClassPriors` | `[balanced] / [actual]` | 类别先验 |

### 8.5 LUT 加速参数

| 参数 | 推荐值 | 说明 |
|------|--------|------|
| `NumIntervals` | 8–16 | 量化层级 |
| `BitDepth` | 8 / 16 | LUT 数据位宽 |

---

## 9. 相关分类

- **Deep Learning（深度学习）**：当样本量 > 5000 或特征复杂时，分类应迁移到 `create_dl_model_classification`。
- **OCR（光学字符识别）**：`create_ocr_class_mlp` / `create_ocr_class_svm` 是分类器的字符专用版本。
- **Identification（识别）**：条码与二维码走专用识别，不走分类。
- **Regions（区域）**：特征提取（`area_center`、`moments_*`、`gray_features`）是分类的前置。
- **Filters（滤波）**：图像预处理（`median_image`、`emphasize`）影响分类精度。
- **Segmentation（分割）**：阈值、区域生长常常是分类的预处理步骤。

---

## 10. 学习小结

HALCON Classification 是工业视觉的"轻量级分类利器"，在不依赖 GPU、样本量适中的场景下，提供了从特征提取到分类推理的完整能力栈。

**学习路线建议**：

1. **第 1 周**：理解 `ClassTrainDataHandle` 概念，跑通 SVM / MLP 完整流程。
2. **第 2 周**：特征工程实战（区域特征 + 灰度特征 + 纹理特征）。
3. **第 3 周**：掌握 4 种分类器的参数调优与适用场景。
4. **第 4 周**：LUT 加速部署，K 折交叉验证，混淆矩阵评估。
5. **第 5 周**：异常检测（GMM 单类、KNN 距离）。

**关键能力**：

- **特征工程**：合理选择与归一化。
- **算法选择**：依样本量、特征维度、概率需求选择 SVM/MLP/KNN/GMM。
- **不均衡处理**：类别权重、SMOTE、阈值调节。
- **部署能力**：LUT 加速、模型压缩、跨平台一致性。

**迁移路径**：当样本量过大或特征复杂时，**直接迁移到 Deep Learning**（`create_dl_model_classification`）。Classification 与 Deep Learning 是工业视觉分类的"两阶进化"。

**一句话总结**：小样本玩 SVM/GMM，中样本用 MLP/LUT，大样本上 Deep Learning。HALCON 三个分类器家族覆盖了 0–10000 样本的全场景。
