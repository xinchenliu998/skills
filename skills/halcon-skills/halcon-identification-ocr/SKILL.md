---
name: halcon-identification-ocr
description: >-
  HALCON identification and reading: 1D barcodes (create_bar_code_model,
  find_bar_code, decode_bar_code_rectangle2, set_bar_code_param, quality check
  ISO/IEC 15416), 2D codes (create_data_code_2d_model, find_data_code_2d,
  set_data_code_2d_param, recognition modes standard/enhanced/maximum, print
  quality ISO/IEC 15415 & 29158 for DPM), OCR character classification
  (create_ocr_class_mlp / svm / knn, append_ocr_trainf, trainf_ocr_class_*,
  do_ocr_multi_class_* / do_ocr_word_*, create_text_model_reader / find_text,
  pre-trained fonts), and Deep OCR (create_deep_ocr, apply_deep_ocr). Use this
  skill whenever a HALCON/HDevelop task reads a barcode, Data Matrix / QR / PDF417 /
  Aztec / DotCode, reads or verifies characters/text, or checks print quality.
  Trigger on find_bar_code / find_data_code_2d / do_ocr_multi_class_mlp /
  find_text / create_deep_ocr / read_ocr_class_*, on code-type selection
  (EAN-13, Code 128, QR, Data Matrix ECC 200), on reading difficult codes
  (low contrast, perspective, small modules), or on trading 'auto' 识别 vs
  narrow parameters for speed.
---

# HALCON 识别与读码（条码 / 2D 码 / OCR / Deep OCR）

> 定位：把图像里的符号/文本变成可用字符串，并做打印质量检查。
> 编写规范见 `../_authoring/`（conventions.md 为精简总结；完整规范在 halcon_skill.md；脚本格式/CLI 见同名 *_reference.md）。

---

## 一、一句话选型

| 目标 | 首选 | 说明 |
|---|---|---|
| 1D 条码 | `find_bar_code`（`CodeType='auto'` 或指定） | 任意方向、多码、同类型 |
| 已知位置的条码 | `decode_bar_code_rectangle2` | 更快（直扫矩形） |
| 2D 码（DataMatrix/QR/PDF417/Aztec/DotCode） | `find_data_code_2d` | 一次找+读+解码 |
| 单字符 OCR | `create_ocr_class_mlp/svm` + `do_ocr_multi_class_*` | 离线训/读字体 |
| 整词/区域文本 | `create_text_model_reader ('auto',...)` + `find_text` | 分割+分类一步（须 MLP） |
| 无合适字体/刻字 | `create_text_model_reader ('manual',...)` + 自建 OCR 分类器 | 只分割，再分类 |
| 连写字/多字体/旋转 | `create_deep_ocr` + `apply_deep_ocr` | DL 整词 |

---

## 二、1D 条码

```hdevelop
create_bar_code_model ([], [], BarCodeHandle)     * 多数情况无需调参
find_bar_code (Image, SymbolRegions, BarCodeHandle, 'EAN-13', DecodedDataStrings)
decode_bar_code_rectangle2 (Image, Rectangle2, BarCodeHandle, CodeType, SymbolRegions, DecodedDataStrings)
```
### 关键参数（set_bar_code_param / set_bar_code_param_specific）
| 参数 | 含义 | 备注 |
|---|---|---|
| `'element_size_min'`/`'element_size_max'` | 元素宽度/要素尺寸 | 最常用；`<2.0` 触发 small_elements_robustness |
| `'meas_thresh'` | 相对阈值 | 噪图/堆叠码失效时用绝对阈值 |
| `'meas_thresh_abs'` | 绝对阈值 | 默认 5.0；低对比可设 0 再降 meas_thresh |
| `'check_char'` | 校验符 | 无校验码设 'absent' |
| `'num_scanlines'` | 每条码扫线数（默认10） | 减少显著提速 |
| `'stop_after_result_num'` | 已知码数 | 防误检+提速 |
| `'min_identical_scanlines'`/`'majority_voting'` | 抗噪/防误检 | — |
| `'start_stop_tolerance'` | 'low'/'high'（仅 Code128） | 清晰无噪单一码制用 high |
- **自动判别**：`CodeType='auto'` 或给出预期码制列表；每加一种码制增加时间、降低可靠性——尽量只列实际出现码制。
- **诊断**：`get_bar_code_object`（'candidate_regions'/'scanlines_all'/'scanlines_valid'）、`get_bar_code_result`（'status'/'status_id'）；错误消息以 `edges:`/`decoding:`/`check:` 开头对应阶段。
- **打印质量（ISO/IEC 15416:2016）**：`get_bar_code_result(Handle,0,'quality_isoiec15416_float_grades',Quality)`（9 元组：Overall/Decode/Symbol Contrast/Min Reflectance/Edge Contrast/Modulation/Defects/Decodability/Additional）。
- **读不出处理**：低对比 `scale_image_range`；光照不均关 `meas_thresh_abs`(=0.0)+降 `meas_thresh`(0.02)；太小 `zoom_image_factor`；黑底亮码 `invert_image`；**元素 <2.0px 慎用 emphasize/zoom/mean_image**。圆形码 `polar_trans_image_ext` 展开+读后 `polar_trans_region_inv`。

---

## 三、2D 码

```hdevelop
create_data_code_2d_model ('Data Matrix ECC 200', [], [], DataCodeHandle)
find_data_code_2d (Image, SymbolXLDs, DataCodeHandle, [], [], ResultHandles, DecodedDataStrings)
if (|DecodedDataStrings| == 0) ... 调整参数 endif
```
### 三种识别模式（对运行时间影响显著）
| 模式 | 特点 | 相对耗时 |
|---|---|---|
| `standard_recognition`(默认) | 范围窄、快；要求暗码亮底、对比度>30、finder 可见 | 1.0x |
| `enhanced_recognition` | 可亮码暗底、对比≥10、模块更小、DataMatrix 可斜至30°、QR 两点 | ~1.7x |
| `maximum_recognition` | 更小模块、强局部对比波动、Aztec 定位变形/缺失 | ~6x |

**建议**：优先 standard 模式 + 训练/手动细调（更快更省内存）。enhanced/maximum 也解不出基本是图像质量问题，应改善采集。
### 关键参数（set_data_code_2d_param）
- 形状/尺寸：`'symbol_size'`(方形码单值)、`'model_type'`(QR)、`'format'`(Aztec `'compact'`/`'full_range'`/`'rune'`)、`'module_size_min/max'`、`'module_aspect_ratio'`(PDF417)。
- 外观：`'polarity'`(`'dark_on_light'`/`'light_on_dark'`/`'any'`)、`'mirrored'`、`'contrast_min'`(标准30/增强10；不适用 DataMatrix/DotCode)、`'module_gap'`(`'no'`/`'small'`/`'big'`)、`'slant_max'`(DataMatrix 0-0.7)、`'module_grid'`(DataMatrix)、`'position_pattern_min'`(QR 2/3)、`'small_modules_robustness'`。
- 模型控制：`'persistence'`(0/1/-1)、`'strict_model'`、`'timeout'`。
- 自动训练：`find_data_code_2d (Image, SymbolXLDs, Handle, 'train', 'all', ...)`（多用几张例图覆盖变化）。
- 模型存取：`write_data_code_2d_model`/`read_data_code_2d_model`。
### 读疑难码
透视/倾斜：`hom_vector_to_proj_hom_mat2d`('normalized_dlt')+`projective_trans_image('bilinear')`；大面积模块间隙：`gray_erosion_shape` 缩间隙；噪声/纹理：`median_image` 或 `gray_opening_shape`。
### 打印质量
- `'quality_isoiec15415'`(ISO/IEC 15415，矩阵码 10 特征)、`'quality_isoiec29158'`(ISO/IEC 29158 DPM，11 元素；'Mean light' 需交互式采集，用 `calibration_isoiec29158.hdev`)；DotCode 不支持。

---

## 四、OCR 字符分类

### 分类器选型
| 分类器 | 创建/训练/读入 | 特点 |
|---|---|---|
| MLP | `create_ocr_class_mlp`/`trainf_ocr_class_mlp`/`read_ocr_class_mlp`(.omc/.fnt) | 分类快；Automatic Text Reader 要求 MLP |
| SVM | `create_ocr_class_svm`/`trainf_ocr_class_svm`/`read_ocr_class_svm`(.osc) | 识别率略好、训练快 |
| kNN | `create_ocr_class_knn` | 样本少时占优 |

### 训练 workflow
```hdevelop
* 1 分割字符 → 写 .trf
threshold(...); closing_rectangle1(...); connection(...); sort_region(...)
for i:=1 to 10: select_obj(...); append_ocr_trainf (Char, Image, Chars[i-1], 'numbers.trf')
* 2 建分类器（Width/Height 归一化尺寸，典型 6x8~10x14）
read_ocr_trainf_names ('numbers.trf', CharacterNames, Num)
create_ocr_class_mlp (8, 10, 'constant', 'default', CharacterNames, 20, 'none', 1, 42, OCRHandle)
* 3 训练 + 存
trainf_ocr_class_mlp (OCRHandle, 'numbers.trf', 200, 1, 0.01, Error, ErrorLog)
write_ocr_class_mlp (OCRHandle, 'numbers.omc')
```
- `Width/Height`=字符归一化尺寸；`Interpolation`=`'constant'`(默认推荐)/`'weighted'`/`'bilinear'`(勿用大字符)/`'nearest_neighbor'`；`Features`=`'default'`(=`['ratio','pixel_invar']`)，背景不可用换 `['pixel_binary','ratio','anisometry']`。
- **预训练字体**（`%HALCONROOT%/ocr/`）：Document / DotPrint / HandWritten_0-9 / Industrial / OCRA / OCRB / Pharma / SEMI / **Universal**(CNN)。命名 `前缀_字符集_NoRej/Rej`（`_Rej` 有拒识类，拒识返回 ASCII 26 SUB）。
- **读字符**：`do_ocr_multi_class_mlp`(每 region 一名+confidence)/`do_ocr_single_class_mlp`/`do_ocr_word_mlp`(正则/词典纠错)。
- **坑**：预训练字体假设**暗码亮底**；亮码暗底先 `invert_image`（或 `gen_image_proto`+`overpaint_region`）。

### Automatic / Manual Text Reader
```hdevelop
* Automatic（推荐，分割+分类一步，须 MLP）
create_text_model_reader ('auto', 'Document_0-9_NoRej', TextModel)
set_text_model_param (TextModel, 'text_line_structure', '2 2 2')
find_text (Image, TextModel, TextResultID)
get_text_result (TextResultID, 'class', Classes); get_text_object (CharRegions, TextResultID, 'char')
* Manual（只分割，用于刻字/无合适分类器）
create_text_model_reader ('manual', [], TextModel)
set_text_model_param (TextModel, 'manual_char_width', 24)   * 'manual_' 前缀
find_text (Image, TextModel, TextResultID)   * 再用 OCR 分类器分类
```
- 假设文字近似水平；斜的用 `text_line_orientation`+`rotate_image`。

---

## 五、Deep OCR（DL 整词）
```hdevelop
create_deep_ocr (DeepOCRHandle)                     * detection+recognition 双组件
write_deep_ocr (DeepOCRHandle, 'model.dlocr')       * 离线建/写
read_deep_ocr ('model.dlocr', DeepOCRHandle)
set_deep_ocr_param (DeepOCRHandle, 'detection_tiling', ...)   * 大图自动分块
apply_deep_ocr (Image, DeepOCRHandle, ResultDict)   * 从字典取检测/识别结果
```
- **recognition 组件单独用**（更快更小）：只读单词且位置已知时，带自动文本对齐，运行时间显著低于用 detection 组件。多词必须用 detection。
- **坑**：模型已学字体集有限；未学到的字符/字体大概率读不出甚至测不到；**不能**通过追加训练单个字符/字体增强——需完整重训（`deep_ocr_recognition/detection_training_workflow.hdev`）。

---

## 六、引用
- 中文算子总览：`references/ops_08_Identification.md`、`ops_09_OCR.md`
- 逐算子签名/默认值：`references/ref_OPERATOR_REFERENCE.md`（Identification / OCR 章）。
- 关联：`halcon-image-preprocessing`（预处理）、`halcon-matching`（码定位/对齐）、`halcon-inspection-defect`（打印质量/验证）。


---

## 用例参考（example_*.md）

本 skill 目录下 `references/` 含以下项目里抽出的真实用例（按主题归档，可直接借鉴实现思路/算子组合）：

- `references/example_completeness_check.md`
- `references/example_ocr_barcode.md`
