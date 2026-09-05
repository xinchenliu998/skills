---
name: halcon-inspection-defect
description: >-
  HALCON defect/anomaly inspection: Variation Model (create_variation_model,
  train_variation_model, prepare_variation_model, compare_variation_model /
  compare_ext_variation_model for absolute or light/dark differences), texture
  analysis (texture_laws, gen_cooc_matrix, cooc_feature_*, entropy_gray), FFT
  frequency filtering for periodic/scratch defects (fft_generic / rft_generic,
  bandpass 划痕检测), and the Inspection solution models (create_texture/
  bead/variation inspection). Use this skill whenever a HALCON/HDevelop task
  detects defects (scratches, stains, missing parts, surface/texture anomalies,
  blob defects) by comparing against a reference, analyzing texture, or filtering
  frequency domain. Trigger on create_variation_model / train_variation_model /
  compare_variation_model, texture_laws / gen_cooc_matrix / cooc_feature_image,
  fft_generic / rft_generic / bandpass_image, create_texture_inspection_model,
  or when choosing between variation model vs texture analysis vs FFT vs blob
  for a defect-inspection task.
---

# HALCON 缺陷检测 / 表面纹理检

> 定位：从"正常"中检出"异常"——缺陷、划痕、污点、缺件、表面/纹理偏差。
> 四大路线：**Variation Model**（对参考图）、**Texture Analysis**（对参考纹理）、**FFT 频域**（周期性/方向性缺陷）、**Blob/Edge**（局部缺陷，见预处理/边缘 skill）。
> 编写规范见 `../_authoring/`（conventions.md 为精简总结；完整规范在 halcon_skill.md；脚本格式/CLI 见同名 *_reference.md）。

---

## 一、一句话选型

| 缺陷/场景 | 首选 | 说明 |
|---|---|---|
| 与参考图逐像素比（印刷/完整性/表面） | **Variation Model** | 容忍对象边界小瑕疵，对区域内部缺陷敏感 |
| 纹理异常（木材/织物/皮肤） | **Texture Analysis** | 灰度结构复杂，blob 无效时 |
| 周期性/方向性缺陷（划痕/蹭痕/磨痕） | **FFT 频域滤波** | 带通/陷波去掉正常纹理 |
| 局部缺陷（缺口/污点/缺件） | **Blob / Edge / 形态学差分** | 亮度差异明显 |
| 均匀表面缺陷 | **Blob / Contour** | 明显亮暗点 |
| 与参考纹理/颜色比 | **Texture / Color / Classification** | 见 `halcon-classification-dl` |

---

## 二、Variation Model（差异模型）

```hdevelop
* 1 建模（模式 'standard'=多图训练 / 'direct'=单理想图）
create_variation_model (Width, Height, 'byte', 'standard', VariVarModelID)
* 2 对齐（shape-based matching，训练图必须对齐，否则变差图异常大）
* 3 训练（多个好样本 → 得理想图+变差图）
train_variation_model (ImageTrans, VariModelID)
* 4 准备（多图）；或手动建变差图后立即用 prepare_direct_variation_model
prepare_variation_model (VariationModelID, 20, 3)
* 5 比较（'light_dark' 分别返回过亮/过暗区域）
compare_ext_variation_model (ImageScaled, RegionDiff, VarModelID, 'light_dark')
```
- `prepare_variation_model` 的 `AbsThresh=20`、`VarThresh=3`（例）。
- 单理想图：`prepare_direct_variation_model (Image, VarImage, VarModelID, 15, 4)`；变差图可用 `sobel_amp`/`edges_image`/`gray_range_rect`/`edges_sub_pix` 生成。
- 检查质量：`get_variation_model (MeanImage, VarImage, VariModelID)`；阈图 `get_thresh_images_variation_model`。
- **坑**：训练图必须对齐；`clear_train_data_variation_model` 后不能再训练/`get_variation_model`；变光照补偿用 `get_grayval_range`+`scale_image` 后再比（`variation_model_illumination.hdev`）。

---

## 三、Texture Analysis（纹理分析）

```hdevelop
* 1 纹理滤波（mask 名 = 两字母 col,row，'l/e/s/r/w/o' 低频→高频；常用 'el'/'le'/'es'/'se'/'ee'）
texture_laws (Image, Texture, 'el', 2, 5)
* 2 滤波后必须用 texel 大小的 mean_image 平滑得到能量图
mean_image (Texture, Energy, 211, 61)
* 3 特征：共生矩阵；或梯度分布；或直接分割
gen_cooc_matrix (Image, Image, 6, 90, Matrix)   ; cooc_feature_matrix (Matrix, Energy, Corr, Homoge, Contrast)
entropy_gray (Image, Entropy, Aniso, Direction)
sobel_amp (Image, EdgeAmp,'thin_sum_abs',3) ; gray_histo_abs (EdgeAmp, EdgeHist, ...)
* 4 分割/分类：binary_threshold/dyn_threshold（先 mean_image mask=2*texel）或 SVM/MLP
```
- **坑**：滤波后必须平滑；规则纹理先旋转对齐更有效；特征增多时**必须重新训练**分类器；彩色纹理先拆通道/转色空间再滤波。

---

## 四、FFT 频域（周期性/划痕）

```hdevelop
* 1 傅里叶变换（大滤波器用 FFT 高效）
fft_generic (Image, ImageFFT, 'to_freq')
* 2 构造带通/陷波滤波（划痕 = 频谱中特定方向的亮线）
gen_bandfilter (Filter, 0.0, 0.9, 'n', 'rft', 'dc_reduced', W, H)
* 3 频域相乘 + 逆变换
convol_fft (ImageFFT, Filter, ImageConvol)
fft_generic (ImageConvol, ImageFiltered, 'from_freq')
* 4 阈值/形态学找缺陷
```
- 相关：`rft_generic`/`fft_image`/`fft_image_inv`；`bandpass_image` 提取细线；`derivate_gauss`+`zero_crossing_sub_pix`。
- 划痕检测常配 `lines_gauss`（见 `halcon-edge-contour`）+ 极坐标展开（`line_detection` 用例）。
- **坑**：FFT 输入需 `real` 或注意 `convert_image_type`；`dc_reduced` 去直流；频谱中心对应低频。

---

## 五、Inspection 专业模型（可选）
- HDevelop 提供 `create_texture_inspection_model`/`create_bead_inspection_model`/`create_variation_model`（封装上述思路的高层模型）；`apply_*_inspection_model` 推理。适合工厂级标准检测方案。
- 印刷/OCR 验证用 OCV（`halcon-identification-ocr` 的打印质量）。

---

## 六、组合流水线范式
1. **对齐**：shape-based matching（`halcon-matching`）对齐后再比，消除位置偏差误报。
2. **参考图**：无参考时用背景估计 `create_bg_esti` + `apply_bg_esti`（Tools），或形态学差分（`gray_opening_shape`/`gray_erosion_shape`）。
3. **判定**：面积/数量阈值 + `select_shape` 过滤噪声，输出 OK/NG + 缺陷坐标。
4. **多策略**：多种方法并行（如 blob + FFT + 纹理）交叉验证，置信度评分——见 `halcon-vision-workflow`。

---

## 七、常见陷阱
1. 训练/参考图必须与检测图对齐、光照一致；先做 `radiometric_self_calibration`+`lut_trans` 线性化。
2. `dyn_threshold` 只适用于缺陷比周围暗/亮的情况；纹理能量图滤波后必须平滑。
3. FFT 周期缺陷要求物体稳定、周期性明显；非周期缺陷用空域方法。
4. 缺陷判定阈值要留裕量，避免把正常工艺差异误判为 NG。

---

## 八、引用
- 中文算子总览：`references/ops_17_Inspection.md`、`ops_18_Tools.md`、`ops_02_Filters.md`（纹理/频域）
- 逐算子签名/默认值：`references/ref_OPERATOR_REFERENCE.md`（Inspection / Tools / Filters 章）。
- 关联：`halcon-image-preprocessing`（预处理/Blob）、`halcon-edge-contour`（细线/边缘缺陷）、`halcon-matching`（对齐）、`halcon-classification-dl`（缺陷分类）。


---

## 用例参考（example_*.md）

本 skill 目录下 `references/` 含以下项目里抽出的真实用例（按主题归档，可直接借鉴实现思路/算子组合）：

- `references/example_defect_inspection.md`
- `references/example_fft_processing.md`
- `references/example_region_features.md`
