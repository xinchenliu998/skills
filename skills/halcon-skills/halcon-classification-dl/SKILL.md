---
name: halcon-classification-dl
description: >-
  HALCON classification and deep learning: classic classifiers MLP / SVM / GMM /
  k-NN (create_class_mlp / svm / gmm / knn, add_sample_class_*, train_class_*,
  classify_class_*, evaluate_class_*), image pixel classification
  (add_samples_image_class_*, classify_image_class_*, class_2dim_sup,
  class_ndim_norm, LUT acceleration create_class_lut_*), OCR classification
  (create_ocr_class_mlp/svm/knn, trainf_ocr_class_*, do_ocr_*), and Deep
  Learning/CNN (transfer learning with dl_model operator prefix, deep OCR with
  the cnn prefix). Use this skill whenever a HALCON/HDevelop task classifies an
  object, region or pixel into categories, does defect/OK-NG classification,
  novelty detection (rejection of unknown classes), or trains a deep learning
  model. Trigger on create_class_mlp / svm / gmm / knn, add_sample_class_* /
  train_class_* / classify_class_*, classify_image_class_*, select_shape /
  area / texture features for classification, novelty detection, k-NN parameter
  tuning, or choosing between MLP / SVM / GMM / k-NN / DL for a classification
  task.
---

# HALCON 分类与深度学习

> 定位：把对象/像素按特征向量分到预定义类（分类），或按已知类标记分割图像；涵盖经典分类器与深度学习。
> 两大类：**手工特征组**（MLP/SVM/GMM/kNN，用户提取特征向量）+ **DL 组**（CNN，特征自动学）。
> 编写规范见 `../_authoring/`（conventions.md 为精简总结；完整规范在 halcon_skill.md；脚本格式/CLI 见同名 *_reference.md）。

---

## 一、选型（核心表）

| 维度 | DL | MLP | SVM | GMM | kNN |
|---|---|---|---|---|---|
| 训练速度 | 慢 | 慢 | 中 | 快 | 快 |
| 分类速度 | 视系统 | 中→快 | 快 | 中 | 快/中 |
| 自动特征 | **是** | 否 | 否 | 否 | 否 |
| 增量学习 | 是 | 否 | 不推荐 | 不推荐 | **是** |
| 高维特征 | 是 | 是 | 是 | **否** | 是 |
| Novelty 检测 | 否 | 否 | 是(仅二分类) | **是** | **是** |
| 内存 | 中→高 | 低 | 中 | 低 | **高**(样本不可删) |

**一句话建议**：很高精度/难定义特征/大量标注图→**DL/CNN**；快速在线、数据一次性齐→**MLP**（不支持 novelty）；要高质+训练中等→**SVM**（`rbf`+`principal_components` 提速）；低维(≤15)+要 novelty→**GMM**；快速试特征/可增量/无维度限→**k-NN**（慢、内存大）；2D 特征→`class_2dim_sup`；紧簇低维→`class_ndim_norm`；OCR→预训练 **Universal**(CNN)。

---

## 二、通用工作流（MLP/SVM/GMM/kNN 统一）

```
create_class_*  →  提取特征向量 Feature(必须 real)  →  add_sample_class_*(Features, ClassID)
  →  train_class_*   →  (可选) write_samples_class_* / write_class_* 存盘
  →  对未知对象再取同一组特征 → classify_class_* → ClassID
```
- 算子结尾替换即可换方法：`_mlp`/`_svm`/`_gmm`/`_knn`。
- **特征向量必须是 real**（integer 特征如 `area` 需 `real([...])`）。
- 分类结果 ClassID；`classify_class_*(...,Num=1)` 最优点，`Num=2` 看次优（类重叠时判可靠）。
- 文件扩展名：MLP `.gmc`、SVM `.gsc`、GMM `.ggc`、kNN `.gnc`。

### 各分类器关键参数
| 分类器 | create | 关键参数 | train |
|---|---|---|---|
| **MLP** | `create_class_mlp(NumInput, NumHidden, NumOutput, 'softmax', 'normalization', NumComp, RandSeed, Handle)` | `NumHidden` 最重要（与输入/输出同量级，太小欠拟合太大过拟合）；`Preprocessing` `'normalization'`(默认)/`'principal_components'`(PCA 降维) | `train_class_mlp(Handle, 200, 1, 0.01, Error, ErrorLog)` |
| **SVM** | `create_class_svm(NumFeat, 'rbf', Gamma, Nu, NumClasses, 'one-versus-one', 'principal_components', NumComp, Handle)` | `KernelParam`(rbf 的 γ)与 `Nu`(0~1，≈期望错误率)成对调；`Mode` `'one-versus-one'`/`'one-versus-all'`/`'novelty-detection'`(仅 rbf) | `train_class_svm(Handle, 0.001, 'default')` |
| **GMM** | `create_class_gmm(NumDim, NumClasses, NumCenters, 'spherical', 'normalization', NumComp, RandSeed, Handle)` | `NumCenters` 每类基元数（单值或 `[min,max]` 范围；训练报错 3335 多为不佳）；**NumDim ≤15** | `train_class_gmm(Handle, 100, 0.001, 'training', 0.001, Centers, Iter)` |
| **kNN** | `create_class_knn(NumDim, Handle)` | `set_params_class_knn`：`'k'`(近邻数)、`'method'`(`'classes_distance'`默认)、`'num_checks'`(0=精确)、`'epsilon'` | `train_class_knn(Handle, ['normalization'], [true])` |

- **SVM** `KernelType='rbf'`(默认推荐)；`reduce_class_svm` 减少支持向量提速。
- **GMM** 特征为整数时 `add_sample_class_gmm` 要设 `Randomize`（≈1.5~2，处理整数特征必需）；novelty 用 `KSigmaProb` 阈值拒绝（如 0.0001）。
- **kNN** 样本不可删、内存大；`num_trees` 默认 4。

---

## 三、图像分割 / 逐像素分类

特征 = 像素在多通道图的灰度（颜色/纹理），自动提取；样本 = 已知类别的区域（ROI）。
```hdevelop
create_class_*  →  add_samples_image_class_gmm (Image, ClassRegions, Handle, 2.0)   * GMM 多一个 Randomize
  →  train_class_*  →  classify_image_class_gmm (Image, ClassRegions, Handle, 0.0001)  * 最后=rejection 阈值
```
- **ClassRegions**：一个元组，每类一个 region，类号=索引（第一个=类0）。多图缺某类用 `gen_empty_region`/`gen_empty_obj` 补。
- 后处理：`closing_circle` → `connection` → `select_shape(...,'area',...)` → `fill_up` → `shape_trans('convex')`。
- **LUT 加速（仅 ≤3 通道）**：`create_class_lut_mlp/svm/gmm/knn(Handle, ['bit_depth','rejection_threshold'], [6,0.03], ClassLUTHandle)` + `classify_image_class_lut`；**无法存盘**，在线极快。
- **双通道**：`trans_from_rgb`(`'hsi'` 取 hue+saturation 抗光照) + `histo_2dim` + `threshold` + `class_2dim_sup`。
- **欧氏/超盒**：`learn_ndim_norm` + `class_ndim_norm`（比 GMM 快~3 倍，可可视化）。

---

## 四、特征与样本选择
- 特征：region 特征（`area_center`/`circularity`/`roundness`/`compactness`/`convexity`/`moments_region_*`）、颜色（`trans_from_rgb`）、纹理（`texture_laws`+`mean_image`、`cooc_feature_image`、`entropy_gray`）。便捷 `calculate_features`；**自动选特征** `select_feature_set_mlp/svm/gmm/knn`。
- **样本选择**：须代表类+覆盖允许偏差（噪声/尺寸/方向）。样本不足技巧：①人造样本（复制后加噪声/erode/dilate/小旋转）；②分两阶段（类数不均→先合并为拒识二分类→对拒识细分）。
- **质量差的根因多半是特征/样本，不是分类器**——别急着换算法。
- **过拟合**：MLP `NumHidden` 过大、SVM `γ` 过大、kNN `k` 过小都会过拟。

---

## 五、OCR 分类
```hdevelop
create_ocr_class_mlp (8, 10, 'constant', 'default', CharacterNames, NumHidden, 'none', 1, 42, OCRHandle)
trainf_ocr_class_mlp (OCRHandle, 'xx.trf', 200, 1, 0.01, Error, ErrorLog)
do_ocr_multi_class_mlp (SortedRegions, Image, OCRHandle, Classes)
```
- 特征可用集见文档（`pixel`/`ratio`/`projection_*`/`moments_*`/`num_holes`/...）。
- **注意多数 OCR 特征非旋转不变**，需先对齐（`classify_metal_parts_ocr.hdev` 用 `moments_central`）。

---

## 六、深度学习 / CNN
- 两类任务：**通用分类**（算子带 `dl_model` 前缀，Deep Learning ▷Model/Classification）+ **OCR 分类**（带 `cnn` 前缀）。
- 通用分类：**不能从头建网络/自定义架构**，只能 **transfer learning**（用预训练网络，改输出层、重训隐藏层）；需每类大量标注图；输出为每类 confidence。参数/模型参数列表用 `get_dl_model_param`。
- **OCR 深度**：只能用预训练字体 **Universal**（`read_ocr_class_cnn`），无法训练自己的 CNN OCR。
- 关键概念：分层（卷积→ReLU→池化→全连接）、端到端、transfer learning、loss 函数优化（`train_dl_model_batch`），inference 阶段网络不变。
- **DL 不支持 novelty detection**。

---

## 七、常见陷阱
1. 特征向量必须 real；训练与分类特征必须一致（同集合、同顺序、同维度）。
2. `classify_class_mlp` 只能在 `'softmax'` 下调用；MLP 不支持 novelty。
3. SVM novelty 仅二分类且必须 `rbf`+`'novelty-detection'`；GMM/kNN novelty 可多类。
4. GMM 维度 ≤15；`CovarType` 按 spherical→diag→full 复杂度递增。
5. 交叉验证调优（数据分 5 子集，4 训 1 测）：MLP `NumHidden`、SVM `Nu`-γ 对、GMM `NumCenters`。
6. 样本用 `write_samples_class_*`+`write_class_*` 存盘，`read_*` 读回；`clear_samples_class_*` 后不可再访问。

---

## 八、引用
- 中文算子总览：`references/ops_10_Classification.md`、`ops_11_DeepLearning.md`
- 逐算子签名/默认值：`references/ref_OPERATOR_REFERENCE.md`（Classification / Deep_Learning 章）。
- 关联：`halcon-image-preprocessing`（颜色/纹理特征）、`halcon-inspection-defect`（缺陷分类）、`halcon-3d-vision`（DL 3D）、`halcon-identification-ocr`（OCR 分类）。
