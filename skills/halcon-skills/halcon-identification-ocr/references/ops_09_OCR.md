# HALCON 算子分类详解：OCR（光学字符识别）

> **分类**：OCR / Optical Character Recognition
> **子类数**：9 个（Convolutional NN、Deep OCR、KNN、Lexica、MLP、Segmentation、SVM、Training Files、Box Legacy）
> **学习优先级**：⭐⭐⭐⭐（⭐ 入门 / ⭐⭐⭐⭐⭐ 必精）
> **典型应用场景**：工业字符检测、批次号读取、零件号识别、票据与证照数字化、半导体激光刻字识别。

---

## 1. 概述

OCR（Optical Character Recognition，光学字符识别）是 HALCON 中面向**工业字符识别**的核心类别，覆盖从"传统字符分割 + 分类器"到"端到端深度学习 OCR"的全栈方案。在 HALCON 26 中，OCR 家族大约包含 **120 个算子**，分布在 9 个子分类下。

HALCON OCR 的工程价值在于：

- **生产可用的可靠性**：MVTec 官方提供的预训练 CNN/Deep OCR 模型在工业场景（点阵、丝印、激光刻字）上已经过亿级图像训练。
- **多算法可选**：从最简单的 Box（投影法）到 MLP / SVM / KNN / CNN / Deep OCR，可根据样本量、字符集、运行速度按需选择。
- **训练闭环完整**：`segment_characters` → `trainf_ocr_class_*` → `do_ocr_*_class_*` → `read/write_ocr_class_*`，训练-推理-持久化形成闭环。
- **词典（Lexica）支持**：对易混淆字符 (`O/0`、`I/1`、`Z/2`、`S/5`) 的语言模型约束由 `create_lexicon` 提供。

> **经验法则**：OCR 项目 80% 的时间花在**字符切分**上，而非识别本身。切分失败，再好的分类器也救不了。

---

## 2. 应用场景

1. **汽车制造**：VIN 码识别、发动机编号、轮胎 DOT 标识、仪表盘读数。
2. **电池与新能源**：电池顶盖批次号、模组二维码附近的小字符、极片涂层边缘字符。
3. **食品与医药包装**：药盒批号与有效期、罐头喷码、瓶身日期码、保健品溯源码。
4. **3C 电子**：PCB 丝印字符（电阻/电容标号）、芯片激光刻字、连接器铭牌。
5. **物流与零售**：集装箱号、快递面单、烟酒追溯码、票据 OCR。
6. **金属与塑料件**：铭牌、压铸件、注塑件、橡胶件上的模压字符。

---

## 3. 子分类详解

| 子分类 | 核心算子 | 典型用途 |
|--------|----------|----------|
| **Segmentation** | `segment_characters`, `select_characters`, `text_line_orientation`, `text_line_slant`, `sort_region` | 字符切分、倾斜校正、行排序 |
| **MLP（Neural Nets）** | `create_ocr_class_mlp`, `trainf_ocr_class_mlp`, `do_ocr_single_class_mlp`, `do_ocr_multi_class_mlp`, `read/write_ocr_class_mlp`, `get_prep_info_ocr_class_mlp` | 工业最常用，需训练，准确率高 |
| **SVM** | `create_ocr_class_svm`, `trainf_ocr_class_svm`, `do_ocr_single_class_svm`, `do_ocr_multi_class_svm`, `read/write_ocr_class_svm` | 小样本、二分类/多分类 |
| **KNN** | `create_ocr_class_knn`, `trainf_ocr_class_knn`, `do_ocr_single_class_knn`, `do_ocr_multi_class_knn`, `read/write_ocr_class_knn` | 极小样本、特征可分时 |
| **Convolutional NN** | `create_ocr_class_cnn`, `do_ocr_single_class_cnn`, `do_ocr_multi_class_cnn`, `do_ocr_word_cnn`, `read/write_ocr_class_cnn` | HALCON 内置 CNN OCR 库 |
| **Deep OCR** | `create_deep_ocr`, `apply_deep_ocr`, `read/write_deep_ocr`, `get_deep_ocr_param`, `set_deep_ocr_param`, `get_deep_ocr_result` | 端到端 OCR（含定位 + 识别） |
| **Lexica** | `create_lexicon`, `import_lexicon`, `lookup_lexicon`, `suggest_lexicon`, `inspect_lexicon`, `clear_lexicon` | 词典约束、语言模型 |
| **Training Files** | `append_ocr_trainf`, `concat_ocr_trainf`, `read_ocr_trainf`, `write_ocr_trainf`, `protect_ocr_trainf` | 训练文件 `.trf` / `.ocrf` 的管理 |
| **Box (legacy)** | `create_ocr_class_box`, `traind_ocr_class_box`, `trainf_ocr_class_box`, `do_ocr_single`, `do_ocr_multi`, `testd_ocr_class_box`, `info_ocr_class_box` | 字符投影法（旧版），仅限极规则字符 |

**算法选择摘要**：

| 算法 | 样本量 | 速度 | 抗噪 | 适用场景 |
|------|--------|------|------|----------|
| Box (legacy) | 0 | 极快 | 差 | 已不推荐 |
| KNN | 极小 | 慢 | 中 | 调试 / 演示 |
| MLP | 中 | 快 | 好 | **工业首选** |
| SVM | 小 | 快 | 好 | 特征可分时 |
| CNN | 0 | 中 | 极好 | HALCON `Industrial` 库 |
| Deep OCR | 0 | 慢 | 极好 | 端到端、复杂背景 |

---

## 4. 核心算子详解

> 以下 28 个算子覆盖 OCR 90% 的工业场景。

### 4.1 切分与预处理

| 算子 | 作用 | 关键参数 |
|------|------|----------|
| `segment_characters(Image, CharacterRegions, Foreground, Method)` | 字符切分 | `Method` ∈ `'local_contrast'`, `'contrast'`, `'simple'` |
| `select_characters(Region, Selected, MinCharWidth, MaxCharWidth, MinCharHeight, MaxCharHeight, MinStrokeWidth, MaxStrokeWidth, ...)` | 过滤非字符 | 按宽/高/笔画宽度 |
| `text_line_orientation(Image, TextLine, OrientationAngle, Confidence)` | 文本行倾斜检测 | 旋转范围 ±45° |
| `text_line_slant(Image, TextLine, SlantAngle, Confidence)` | 文本斜体角度 | 用于斜体校正 |
| `sort_region(Regions, SortedRegions, SortMode, Order, RowOrCol)` | 区域排序 | `'character'`, `'row'`, `'column'` |
| `partition_lines(Region, Partitioned, Partition, Distance, Mode)` | 文本行切分 | 用于多行识别 |
| `closing_rectangle1(Region, Closed, Width, Height)` | 修复断裂字符 | 结构元素宽度 = 笔画间距 |

### 4.2 训练与持久化

| 算子 | 作用 |
|------|------|
| `create_ocr_class_mlp(WidthCharacter, HeightCharacter, Interpolation, Features, Character, NumHidden, Preprocessing, NumComponents, RandSeed, OcrHandle)` | 创建 MLP 分类器 |
| `trainf_ocr_class_mlp(TrainFile, OcrHandle, OcrTrainFile, Password)` | 从训练文件训练 |
| `traind_ocr_class_mlp(CharacterImages, CharacterNames, OcrHandle, GenParamNames, GenParamValues)` | 从内存图像训练 |
| `read_ocr_class_mlp(FileName, OcrHandle)` / `write_ocr_class_mlp(OcrHandle, FileName)` | 模型读写 |
| `concat_ocr_trainf(TrainFile1, TrainFile2, MergedTrainFile)` | 合并训练文件 |
| `append_ocr_trainf(Character, Class, OcrTrainFile)` | 追加单样本 |
| `protect_ocr_trainf(TrainFile, Password)` | 加密训练文件 |

### 4.3 推理

| 算子 | 作用 |
|------|------|
| `do_ocr_single_class_mlp(Character, Image, OcrHandle, Result, Confidence)` | 单字符识别 |
| `do_ocr_multi_class_mlp(Character, Image, OcrHandle, Result, Confidence)` | 多字符批量识别 |
| `do_ocr_word_cnn(Image, Character, OcrHandle, Expression, Word, Score)` | 单词级 CNN 识别 |
| `do_ocr_single_class_svm` / `do_ocr_multi_class_svm` | SVM 推理 |
| `do_ocr_single_class_knn` / `do_ocr_multi_class_knn` | KNN 推理 |
| `do_ocr_single_class_cnn` / `do_ocr_multi_class_cnn` | CNN 推理 |
| `get_prep_info_ocr_class_mlp(OcrHandle, Preprocessing, Information)` | 查询预处理特征 |

### 4.4 Deep OCR

| 算子 | 作用 |
|------|------|
| `create_deep_ocr(Preprocessor, Recognition, DeepOCRHandle, Device)` | 创建端到端 OCR |
| `apply_deep_ocr(Image, DeepOCRHandle, DetectionResult, RecognitionResult)` | 一次性识别 |
| `set_deep_ocr_param(DeepOCRHandle, GenParamName, GenParamValue)` | `'detection_threshold'` / `'recognition_threshold'` |
| `get_deep_ocr_result(RecognitionResult, Candidate, Score, Word)` | 解析候选词 |
| `read_deep_ocr` / `write_deep_ocr` | 持久化 |

### 4.5 词典

| 算子 | 作用 |
|------|------|
| `create_lexicon(TextFile, LexiconHandle, IgnoreCase, Language, AddWords)` | 从文本文件创建词典 |
| `import_lexicon(LexiconHandle, WordList, Score)` | 运行时增加词 |
| `lookup_lexicon(LexiconHandle, Word, Found)` | 查词 |
| `suggest_lexicon(LexiconHandle, Word, MaxNumCorrections, SuggestionList)` | 模糊纠错 |
| `inspect_lexicon(LexiconHandle, Words, WordInDictionary)` | 批量校验 |

---

## 5. HDevelop 示例代码

### 5.1 示例一：传统 MLP 字符识别全流程

```hdevelop
* ============================================================
* OCR 完整示例：字符切分 → 训练 → 识别
* 场景：印刷数字 0-9，单行，多字体
* ============================================================
dev_update_off ()
dev_close_window ()
read_image (Image, 'ocr/eco_numbers_01')
get_image_size (Image, Width, Height)
dev_open_window (0, 0, Width * 2, Height * 2, 'black', WindowHandle)
dev_display (Image)

* --- 1. 字符切分 ---
* 缩小 ROI 到字符区域
gen_rectangle1 (ROI, 50, 100, 200, 700)
reduce_domain (Image, ROI, ImageReduced)
* 阈值切出黑色字符
threshold (ImageReduced, Region, 0, 100)
* 连通域拆分
connection (Region, ConnectedRegions)
* 选字符（按面积）
select_shape (ConnectedRegions, CharCandidates, 'area', 'and', 30, 600)
* 排序（左 → 右）
sort_region (CharCandidates, SortedRegions, 'character', 'true', 'row')
dev_set_color ('red')
dev_set_draw ('margin')
dev_display (SortedRegions)
stop ()

* --- 2. 训练样本采集（用 trf 文件格式） ---
* 实际生产中由程序员标注：append_ocr_trainf(Char, '0', 'train.trf')
* 这里用 HALCON 自带训练文件演示
TrainFile := 'ocr/training_words.trf'
WordNames := '0123456789ABCDEF'
* 训练 MLP
create_ocr_class_mlp (8, 10, 'constant', 'default', \
                      WordNames, 80, 'normalization', 5, 42, OCRHandle)
trainf_ocr_class_mlp (TrainFile, OCRHandle, 'ocr_train.otf', 300)
write_ocr_class_mlp (OCRHandle, 'ocr_model.omc')

* --- 3. 推理 ---
read_ocr_class_mlp ('ocr_model.omc', OCRHandle)
do_ocr_multi_class_mlp (SortedRegions, ImageReduced, OCRHandle, Class, Confidence)
* 显示结果
dev_set_color ('green')
set_display_font (WindowHandle, 16, 'mono', 'true', 'false')
for i := 0 to |Class| - 1 by 1
    select_obj (SortedRegions, SingleChar, i + 1)
    area_center (SingleChar, _, Row, Column)
    disp_message (WindowHandle, Class[i], 'image', Row - 30, Column - 10, 'green', 'false')
endfor
```

### 5.2 示例二：Deep OCR 端到端识别

```hdevelop
* ============================================================
* Deep OCR 一行流：不需要切分，自动定位 + 识别
* ============================================================
dev_update_off ()
dev_close_window ()
read_image (Image, 'ocr/serial_numbers_01')
get_image_size (Image, W, H)
dev_open_window_fit_image (Image, 0, 0, -1, -1, WindowHandle)
dev_display (Image)

* --- 创建 Deep OCR（HALCON 26 自带预训练模型） ---
Preprocessor := 'last_ocr_detection.hdl'
Recognition := 'last_ocr_recognition.hdl'
* 设备选择：'gpu' / 'cpu'
try
    query_available_compute_devices ('runtime', DeviceIDs)
    create_deep_ocr (Preprocessor, Recognition, DeepOCRHandle, 'gpu')
catch (Exception)
    create_deep_ocr (Preprocessor, Recognition, DeepOCRHandle, 'cpu')
endtry

* --- 参数调节 ---
set_deep_ocr_param (DeepOCRHandle, 'detection_threshold', 0.7)
set_deep_ocr_param (DeepOCRHandle, 'recognition_threshold', 0.5)
set_deep_ocr_param (DeepOCRHandle, 'decoding', 'greedy')

* --- 推理 ---
apply_deep_ocr (Image, DeepOCRHandle, DetectionResult, RecognitionResult)

* --- 解析结果 ---
* RecognitionResult 是字典，包含 'words'、'scores'、'boxes'
get_dict_tuple (RecognitionResult, 'words', Words)
get_dict_tuple (RecognitionResult, 'scores', Scores)
get_dict_object (Boxes, RecognitionResult, 'boxes')

dev_set_color ('red')
set_display_font (WindowHandle, 18, 'mono', 'true', 'false')
for i := 0 to |Words| - 1 by 1
    dev_display (Boxes)
    disp_message (WindowHandle, Words[i] + ' (' + Scores[i]{0:5} + ')', \
                  'window', 30 + i * 40, 10, 'black', 'true')
endfor
```

### 5.3 示例三：词典纠错 + 整句识别

```hdevelop
* ============================================================
* OCR + 词典：识别易混淆字符 O/0、I/1 后用词典约束
* ============================================================
dev_update_off ()
read_image (Image, 'ocr/serial_no_03')
get_image_size (Image, Width, Height)
dev_open_window (0, 0, Width, Height, 'black', WindowHandle)
dev_display (Image)

* --- 1. 切分字符 ---
gen_rectangle1 (ROI, 60, 200, 130, 800)
reduce_domain (Image, ROI, ImageROI)
binary_threshold (ImageROI, _, 'max_separability', 'light', UsedThreshold)
connection (UsedThreshold, ConnectedRegions)
select_shape (ConnectedRegions, Characters, 'area', 'and', 30, 500)
sort_region (Characters, Sorted, 'character', 'true', 'row')

* --- 2. 加载预训练 MLP ---
read_ocr_class_mlp ('Industrial_0-9A-Z.omc', OCRHandle)

* --- 3. 单字符识别 ---
ConfidenceMin := 0.7
Result := ''
for i := 0 to |Sorted| - 1 by 1
    select_obj (Sorted, Char, i + 1)
    do_ocr_single_class_mlp (Char, ImageROI, OCRHandle, Class, Confidence)
    if (Confidence > ConfidenceMin)
        Result := Result + Class
    else
        Result := Result + '_'
    endif
endfor

* --- 4. 词典纠错 ---
* 假设合法的产品序列号格式：12 位，前 3 位为产品代号
create_lexicon ('valid_serial_codes.txt', LexiconHandle, 'true', 'utf8', [])
suggest_lexicon (LexiconHandle, Result, 2, Suggestions)
ResultCorrected := Suggestions[0]

* --- 5. 显示 ---
dev_set_color ('green')
set_display_font (WindowHandle, 24, 'mono', 'true', 'false')
disp_message (WindowHandle, '原始: ' + Result, 'window', 10, 10, 'black', 'true')
disp_message (WindowHandle, '纠正: ' + ResultCorrected, 'window', 50, 10, 'green', 'true')
clear_lexicon (LexiconHandle)
```

### 5.4 示例四：训练数据采集与 CNN 库调用

```hdevelop
* ============================================================
* 调用 HALCON 自带 OCR CNN 库（无需训练）
* ============================================================
dev_update_off ()
read_image (Image, 'ocr/printed_text_01')
get_image_size (Image, W, H)
dev_open_window (0, 0, W, H, 'black', WindowHandle)
dev_display (Image)

* --- 加载 HALCON 预训练 CNN OCR ---
* Industrial_0-9_NoRej.omc / Industrial_0-9A-Z.omc / Industrial_0-9A-Z+_NoRej.omc
read_ocr_class_cnn ('Industrial_0-9A-Z_NoRej.omc', OcrHandle)

* --- 切分 ---
threshold (Image, Region, 0, 80)
connection (Region, ConnectedRegions)
select_shape (ConnectedRegions, Characters, 'area', 'and', 50, 800)
sort_region (Characters, Sorted, 'character', 'true', 'row')

* --- 批量识别 ---
do_ocr_multi_class_cnn (Sorted, Image, OcrHandle, Class, Confidence)

* --- 渲染结果 ---
set_display_font (WindowHandle, 24, 'mono', 'true', 'false')
Result := ''
for i := 0 to |Class| - 1 by 1
    Result := Result + Class[i]
endfor
dev_set_color ('red')
dev_display (Sorted)
disp_message (WindowHandle, 'Result: ' + Result, 'window', 10, 10, 'black', 'true')
```

---

## 6. 典型工业流水线

### 6.1 印刷字符在线检测（标准流程）

```
1. 图像采集  → grab_image_async (实时)
2. 镜头畸变校正 → change_radial_distortion_image (可选)
3. ROI 定位  → reduce_domain (基于模板匹配 find_shape_model)
4. 字符切分  → segment_characters (Method='local_contrast')
5. 过滤      → select_characters (按 height/width/stroke)
6. 排序      → sort_region (按行/列)
7. 识别      → do_ocr_multi_class_mlp
8. 词典校验  → lookup_lexicon (业务规则)
9. 置信度过滤 → 丢弃 Confidence < 0.7 的字符
10. 字符串组装 → tuple_concat
11. 数据库写回 → tuple_string + DB 写入
```

### 6.2 激光刻字字符识别（高难度）

```
1. 二维码预定位 → find_data_code_2d_model (作为字符 ROI 锚点)
2. 仿射纠正 → vector_angle_to_rigid + affine_trans_image (旋转到水平)
3. 高对比度增强 → emphasize / scale_image_max
4. 字符切分 → segment_characters (Method='simple')
5. 笔画断裂修复 → closing_rectangle1 (Width=3)
6. 训练 MLP  → 收集 50+ 张字体变化样本
7. 训练完成后固化  → write_ocr_class_mlp → 加载
8. 推理 → do_ocr_multi_class_mlp
9. 规则校验: 是否为合法批次号
```

### 6.3 Deep OCR 流水线（无需切分）

```
1. 图像采集  → read_image / grab_image
2. ROI 截取（可选）→ reduce_domain
3. apply_deep_ocr (内置检测 + 识别)
4. 解析 Results → 提取 words + scores
5. 业务校验 → 序列号格式 / 字典
6. 记录到日志
```

---

## 7. 常见陷阱与最佳实践

### 7.1 切分失败（80% 的痛点）

- **永远先看切分结果再训练**：`dev_display(ConnectedRegions)` 后人眼逐行检查。
- **字符粘连**：用 `opening_rectangle1`（结构元素宽度 = 字符间距 × 1.5）做轻度腐蚀。
- **字符断裂**：用 `closing_rectangle1` 缝合（结构元素宽度 = 笔画宽度 × 1.2）。
- **字符与边框粘连**：`reduce_domain` 把 ROI 内外用 `border` + `difference` 剥离边框 2-3 px。
- **多行混切分**：先 `partition_lines` 拆行，再按行 `segment_characters`。

### 7.2 训练数据质量

- **每类样本 ≥ 30 张**，繁体字符建议 ≥ 100 张。
- **样本必须覆盖光照、对比度、字体、位置**的全部变化。
- **字符旋转容忍度**：用 `rotate_image` 主动生成 ±10° 增强样本。
- **噪声样本**：用 `add_noise_white` 主动合成（噪声 σ ≤ 5）。
- **训练集与推理集严格隔离**（防数据泄露）。

### 7.3 易混淆字符

- **`O` 与 `0`**、`I` 与 `1`、`Z` 与 `2`、`S` 与 `5`、`B` 与 `8`。
- **置信度阈值**：低于 0.7 的字符视为不可靠，整句置位 "复检"。
- **词典约束**：业务级白名单（如合法批次号前缀）。
- **CNN 库**：`'Industrial_0-9A-Z_NoRej.omc'` 含拒识模式，自动丢弃低置信度。

### 7.4 Deep OCR 的额外注意

- **GPU 必须 ≥ 8 GB** 显存；不足时切回 CPU。
- **图片分辨率**：建议 1280×1024 以上，太小检测率掉。
- **倾斜容忍**：±30° 之内可用，更大需 `text_line_orientation` 先校正。
- **多语言支持**：HALCON 26 支持中英日韩，需更换 `'last_ocr_recognition.hdl'`。

### 7.5 其他常见错误

- **字符高度 < 10 像素**：识别率急剧下降，建议提升相机分辨率或加放大镜头。
- **图像对比度 < 30**：`emphasize` 或 `scale_image` 增强。
- **斜体字符**：用 `text_line_slant` + `hom_mat2d_slant` 校正后才能识别。
- **OCR 模型版本与库版本不匹配**：务必使用同版本 HALCON 自带的 `*.omc`。

---

## 8. 参数调优指南

### 8.1 `create_ocr_class_mlp` 关键参数

| 参数 | 推荐值 | 说明 |
|------|--------|------|
| `WidthCharacter` / `HeightCharacter` | 8 / 10 | 字符归一化尺寸（像素） |
| `Interpolation` | `'constant'` | 缩放插值 |
| `Features` | `'default'` | `'default'`/`'pixel'`/`'horizontal'`/`'vertical'`/`'up_ho'` |
| `NumHidden` | 80 | 隐藏神经元数（样本量小减半） |
| `Preprocessing` | `'normalization'` | `'none'`/`'normalization'`/`'contrast'`/`'canonical'` |
| `NumComponents` | 5 | PCA 降维数（越大越精确但慢） |

### 8.2 `segment_characters` 关键参数

| 参数 | 推荐值 | 适用 |
|------|--------|------|
| `Method` | `'local_contrast'` | **绝大多数工业场景** |
| `Method` | `'simple'` | 极规则字符 |
| `Method` | `'contrast'` | 高对比度 |
| `UseForeground` | `'true'` | 字体为白底黑字时 false |

### 8.3 `apply_dl_model` / `apply_deep_ocr`

| 参数 | 推荐值 | 说明 |
|------|--------|------|
| `detection_threshold` | 0.7 | 字符区域概率阈值 |
| `recognition_threshold` | 0.5 | 字符/单词置信度阈值 |
| `decoding` | `'greedy'` / `'beam_search'` | 前者快，后者准 |
| `Device` | `'gpu'` | 显存不足时 `'cpu'` |

### 8.4 训练参数

| 参数 | 推荐值 | 说明 |
|------|--------|------|
| `MaxIterations` | 200 | MLP 训练最大迭代 |
| `WeightTolerance` | 0.01 | 早停阈值 |
| `ErrorTolerance` | 0.01 | 早停阈值 |
| `Regularization` | 0.001 | L2 正则 |

---

## 9. 相关分类

- **Classification（经典分类）**：传统机器学习分类，提供 SVM/MLP/KNN/GMM 通用分类器，但**不针对字符**。OCR 是其字符专用版本。
- **Deep Learning（深度学习）**：Deep OCR 归属 Deep Learning 范畴，共享 GPU/CPU 设备管理（`query_available_compute_devices`、`init_compute_device`）。
- **Matching（模板匹配）**：常用于先定位字符区域，再调用 OCR。
- **Segmentation（分割）**：阈值函数、区域生长、分水岭是字符切分的基础。
- **Identification（识别）**：条码（`find_bar_code`）与字符（OCR）是不同识别分支，二维码（`find_data_code_2d_model`）与字符识别常组合使用。
- **Region（区域）**：`select_shape` 在字符过滤阶段频繁使用。

---

## 10. 学习小结

OCR 是工业视觉中最常见的"识别"任务之一。HALCON OCR 的设计在 **"传统字符分割 + 分类器"** 与 **"端到端 Deep OCR"** 之间提供了完整的演进路径。

**学习路线建议**：

1. **第 1 周**：跑通 `segment_characters` + `do_ocr_multi_class_mlp` 完整流程，理解切分与识别的边界。
2. **第 2 周**：尝试 `create_ocr_class_cnn` 调用 HALCON 预训练库（最快上手）。
3. **第 3 周**：实战 `select_characters` 调参、`trainf_ocr_class_mlp` 自训练。
4. **第 4 周**：掌握 `create_deep_ocr` + `apply_deep_ocr` 端到端方案。
5. **第 5 周**：结合 Lexica、Sort_region、partition_lines 处理复杂业务场景。

**关键能力**：

- **看懂切分结果**：判断粘连 / 断裂 / 多行干扰。
- **训练样本组织**：保证覆盖度，避免过拟合。
- **混淆字符处理**：置信度 + 词典 + 业务规则三层防护。
- **Deep OCR 部署**：GPU 加速、模型加载、批处理。

**一句话总结**：OCR 项目的成败，**80% 取决于切分**，20% 取决于分类器。掌握切分，即掌握 OCR 工业落地。
