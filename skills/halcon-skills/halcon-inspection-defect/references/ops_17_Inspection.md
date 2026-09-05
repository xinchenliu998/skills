# HALCON 算子分类详解：Inspection（专用检测）

> **HALCON 版本**：26.05.0.0 Progress
> **算子数量**：约 60 个
> **一级分类目录**：`toc_inspection.html`
> **学习层级**：L1–L2（行业级检测方案的核心）

---

## 1. 概述

Inspection 分类提供了 HALCON 的**高端、行业专属的检测方案**。与基于通用阈值/Blob 的检测不同，Inspection 提供"开箱即用"的封装：训练 + 推理一体化，特别适合标准化程度高的工业场景。

HALCON 26 提供 4 大核心专用检测器：

1. **Bead Inspection**：连续焊缝/胶水的形状/断裂检测（汽车电子、家电）。
2. **Texture Inspection**：周期性纹理（如纺织品、皮革、木纹）的异常检测。
3. **Variation Model**：基于参考图的"金标准比对"（包装印刷、电子屏幕）。
4. **OCV (Optical Character Verification)**：字符内容验证（与参考字符串比对）。

每个检测器都遵循"训练 + 推理"两阶段模式，训练阶段用正常样本构建模型，推理阶段输出缺陷位置 + 严重度。

---

## 2. 应用场景

### 场景 1：汽车焊缝连续检测（白车身车间）

车身焊接后沿焊缝涂密封胶（Bead）→ 相机沿 Bead 路径拍摄 → **Bead Inspection** 检测胶水是否连续、有无断胶/溢胶/缺失。检测速度可达 5 m/s，精度 ±0.3 mm。

### 场景 2：印刷包装质量（食品/医药/烟草）

高速印刷机生产包装盒 → 相机拍印刷面 → **Variation Model** 比对与"金标准"（标准图）的差异 → 输出颜色失真、漏印、错印、字符错误等缺陷。

### 场景 3：纺织品/皮革瑕疵检测（服装/家具）

布料表面有重复纹理 → **Texture Inspection** 学习纹理统计特征 → 推理时输出划痕、污渍、破洞等异常区域。

### 场景 4：药盒批号验证（医药追溯）

药盒喷码的批号必须与包装清单一致 → OCR 识别字符 → **OCV** 与参考字符串比对 → 不一致则 NG。

### 场景 5：TFT-LCD 屏幕缺陷（Mura 缺陷检测）

显示屏 Mura 缺陷是低对比度异常 → 通过多张正常样本训练 **Variation Model**，检测亮度不均区域。

---

## 3. 子分类详解

### 3.1 Bead Inspection（焊缝/胶水检测）— 约 8 算子

| 算子 | 用途 |
|------|------|
| `create_bead_inspection_model` | 创建 Bead 检测模型 |
| `add_bead_inspection_model_image` | 添加训练图（可选） |
| `train_bead_inspection_model` | 训练（若添加了样本） |
| `apply_bead_inspection_model` | 推理（返回位置 + 缺陷） |
| `set_bead_inspection_param` | 设置参数（位置容差、宽度等） |
| `get_bead_inspection_param` | 查询参数 |
| `get_bead_inspection_result_object` | 拿结果对象（缺陷区域） |
| `read/write_bead_inspection_model` | 模型保存/读取 |

**典型工作流**：
1. 设置 Bead 路径（由轨迹系统或前道定位给出）
2. `create_bead_inspection_model` + `set_bead_inspection_param`
3. `apply_bead_inspection_model` → 推理
4. `get_bead_inspection_result_object(..., 'missing_parts', ...)` 拿缺失区域

### 3.2 Texture Inspection（纹理检测）— 约 10 算子

| 算子 | 用途 |
|------|------|
| `create_texture_inspection_model` | 创建（`'basic'` / `'hierarchical'` 两种） |
| `add_texture_inspection_model_image` | 添加正常样本 |
| `train_texture_inspection_model` | 训练 |
| `apply_texture_inspection_model` | 推理 |
| `get_texture_inspection_result_object` | 拿结果（`'novelty_regions'`） |
| `get_texture_inspection_score` | 拿异常分数 |
| `set_texture_inspection_param` | 设置参数 |
| `read/write_texture_inspection_model` | 保存/加载 |

**两种模式**：
- `'basic'`：单尺度纹理特征，速度快，适合周期纹理（布纹）。
- `'hierarchical'`：多尺度纹理金字塔，检测多尺度异常，速度较慢。

### 3.3 Variation Model（金标准比对）— 约 8 算子

| 算子 | 用途 |
|------|------|
| `create_variation_model` | 创建模型（`'variation'` / `'mean'`） |
| `prepare_direct_variation_model` | 直接用图像集准备（推荐） |
| `prepare_variation_model` | 用单图 + 算子准备（灵活） |
| `train_variation_model` | 训练 |
| `compare_variation_model` | 比对（输出二值 + 灰度差异） |
| `compare_ext_variation_model` | 扩展比对（带分级） |
| `get_thresh_images_variation_model` | 拿阈值图（用于调试） |
| `get_variation_model` | 拿模型内部图像（mean/var） |
| `read/write_variation_model` | 保存/读取 |

**两种类型**：
- `'variation'`：每像素训练一个标准差（适合光照变化小但位置变化大的场景）。
- `'mean'`：只训练均值（适合完全对齐场景）。

### 3.4 OCV（光学字符验证）— 约 6 算子

| 算子 | 用途 |
|------|------|
| `create_ocv_proj` | 创建 OCV 投影模型（基于字符图像的灰度投影） |
| `traind_ocv_proj` | 训练（用参考字符串图） |
| `do_ocv_simple` | 简单比对（与训练图整体比对） |
| `do_ocv` | 详细比对（返回每个字符的通过/失败） |
| `close_ocv` | 释放 |
| `read/write_ocv` | 保存/读取 |

**OCV 适用场景**：字符内容已知且稳定（如喷码），只需验证是否一致。**不适用**：手写体、字符形变大、印刷质量差。

### 3.5 Structured Light（结构光检测）— 引用自 3D Reconstruction

此处指的是结构光检测项目中的"专用检测器"，算子实质归属 `toc_reconstruction.html`。

---

## 4. 核心算子详解

### 4.1 `create_bead_inspection_model`

```hdevelop
create_bead_inspection_model('overlap', 'manual', [], [], BeadInspectionModel)
* 模式：'auto' / 'overlap' / 'manual'
*   'auto'：自动定位 Bead
*   'overlap'：已知 Bead 路径，相机视野重叠
*   'manual'：完全手动指定 Bead 位置
```

### 4.2 `apply_bead_inspection_model`

```hdevelop
apply_bead_inspection_model(Image, BeadInspectionModel, Pose, Row, Column, RowTolerance, ColTolerance, ResultRow, ResultColumn, Orientation, BeadInspectionResult)
* Pose：当前 Bead 段在世界坐标的位姿（从轨迹系统来）
* Row/ColumnTolerance：允许的位姿偏差
```

### 4.3 `get_bead_inspection_result_object`

```hdevelop
get_bead_inspection_result_object(Regions, BeadInspectionResult, 'missing_parts')
* 拿缺陷区域（缺失/断裂）
* 其他选项：'too_thin' / 'too_thick' / 'position_out_of_tolerance'
```

### 4.4 `create_texture_inspection_model`

```hdevelop
create_texture_inspection_model('basic', TextureInspectionModelID)
* 'basic'：适合单尺度周期纹理
* 'hierarchical'：多尺度
```

### 4.5 `train_texture_inspection_model`

```hdevelop
* 通常需要 5–20 张正常样本
for i := 1 to 10 by 1
    read_image(Img, 'good_' + i$'.2')
    add_texture_inspection_model_image(Img, TextureInspectionModelID)
endfor
train_texture_inspection_model(TextureInspectionModelID)
```

### 4.6 `apply_texture_inspection_model`

```hdevelop
apply_texture_inspection_model(QueryImage, TextureInspectionModelID, TextureInspectionResultID)
get_texture_inspection_result_object(DefectRegions, TextureInspectionResultID, 'novelty_regions')
get_texture_inspection_score(TextureInspectionResultID, AnomalyScore)
```

### 4.7 `create_variation_model`

```hdevelop
create_variation_model(Width, Height, 'byte', 'variation', VariationModelID)
* 'variation'：每像素统计标准差（推荐用于位置有偏差的场景）
* 'mean'：只统计均值（用于严格对齐场景）
```

### 4.8 `prepare_direct_variation_model`

```hdevelop
* 准备多张训练图（必须对齐或使用同一位置）
prepare_direct_variation_model(GoodImages, VariationModelID, AbsThreshold, AbsVariation, LightDark)
* AbsThreshold：绝对灰度阈值（如 30）
* AbsVariation：绝对变化阈值（如 5）
* LightDark：'light_on_dark' / 'dark_on_light' / 'all'
train_variation_model(VariationModelID)
```

### 4.9 `compare_variation_model`

```hdevelop
compare_variation_model(QueryImage, VariationModelID, RegionDiff)
* RegionDiff：缺陷区域（绝对值超出阈值的像素）
```

### 4.10 `compare_ext_variation_model`（推荐）

```hdevelop
compare_ext_variation_model(QueryImage, VariationModelID, Mode, ThresholdOffset, RegionDiff, AvgDiff, RangeDiff)
* Mode：'absolute' / 'relative' / 'diff_gray' / 'diff_var' / 'diff_fg'
* 输出更多诊断信息（平均差异、变化范围）
```

### 4.11 `get_thresh_images_variation_model`

```hdevelop
get_thresh_images_variation_model(VarImage, ThreshLow, ThreshHigh, VariationModelID)
* 调试用：拿阈值边界图（超出则 NG）
```

### 4.12 `create_ocv_proj`

```hdevelop
create_ocv_proj('real_val', 0, OCVHandle)
* 'real_val'：连续值投影
* 'byte'：离散值投影
```

### 4.13 `traind_ocv_proj`

```hdevelop
traind_ocv_proj(Image, OCVHandle, Name, Mode)
* 用一张训练图 + 期望字符串训练
* Mode：'single' / 'multi' / 'stroboscopic'
```

### 4.14 `do_ocv_simple`

```hdevelop
do_ocv_simple(Image, OCVHandle, Name, Pattern, OcvcScore)
* 简单比对：只返回整体得分
* OcvcScore：0–1 之间的相似度（> 0.5 通常 OK）
```

### 4.15 `do_ocv`（详细）

```hdevelop
do_ocv(Image, OCVHandle, Name, Pattern, OcvcClass, OcvcScore)
* OcvcClass：每个字符的通过/失败列表
* OcvcScore：每个字符的得分
```

---

## 5. HDevelop 示例代码

### 示例 1：Bead Inspection（焊缝检测）完整流程

```hdevelop
* Inspection_Bead.hdev
* 检测连续 Bead（胶水/焊缝）有无缺失

* 加载模型
read_image(Image, 'bead/bead_01')

* 创建 Bead 检测模型
create_bead_inspection_model('auto', 'manual', [], [], BeadInspectionModel)

* 设置 Bead 路径（实际项目中从 CAD/轨迹系统获取）
RowBeadStart := 200
ColBeadStart := 100
RowBeadEnd := 200
ColBeadEnd := 900

* 训练（这里假设直接用同一张图训练——实际应该用多张正常样本）
* 注意：auto 模式下不需要训练

* 推理
PoseIn := [0,0,0,0,0,0,0]
RowIn := RowBeadStart
ColIn := ColBeadStart

apply_bead_inspection_model(Image, BeadInspectionModel, PoseIn, RowIn, ColIn, 50, 50, ResultRow, ResultCol, Orientation, BeadResult)

* 提取缺陷
get_bead_inspection_result_object(MissingRegions, BeadResult, 'missing_parts')
get_bead_inspection_result_object(TooThinRegions, BeadResult, 'too_thin')

* 可视化
dev_clear_window()
dev_display(Image)
set_color(WindowHandle, 'red')
dev_display(MissingRegions)
set_color(WindowHandle, 'yellow')
dev_display(TooThinRegions)

count_obj(MissingRegions, NumMissing)
disp_text(WindowHandle, 'Missing: ' + NumMissing, 'window', 12, 12, 'red', 'box', 'black')
```

### 示例 2：Texture Inspection（布匹瑕疵检测）完整流程

```hdevelop
* Inspection_Texture.hdev
* 检测布料上的瑕疵

* 训练阶段
create_texture_inspection_model('basic', TextureModel)

* 读取 10 张正常样本
for i := 1 to 10 by 1
    read_image(GoodImg, 'fabric/good_' + i$'.2')
    add_texture_inspection_model_image(GoodImg, TextureModel)
endfor

* 训练
train_texture_inspection_model(TextureModel)
* 训练时间：取决于图像大小和样本数（秒到分钟级）

* 保存模型
write_texture_inspection_model(TextureModel, 'fabric_model')

* 推理阶段
read_image(QueryImg, 'fabric/test_01')

apply_texture_inspection_model(QueryImg, TextureModel, TextureResult)
get_texture_inspection_result_object(DefectRegions, TextureResult, 'novelty_regions')
get_texture_inspection_score(TextureResult, AnomalyScore)

* 可视化
dev_clear_window()
dev_display(QueryImg)
set_color(WindowHandle, 'red')
dev_display(DefectRegions)

area_center(DefectRegions, Area, Row, Column)
disp_text(WindowHandle, 'Anomaly: ' + AnomalyScore$'.3f' + ', Area: ' + |Area|, 'window', 12, 12, 'red', 'box', 'black')
```

### 示例 3：Variation Model（包装印刷缺陷）完整流程

```hdevelop
* Inspection_Variation_Model.hdev
* 检测包装印刷的颜色失真/漏印

* 创建模型（图像大小需确定）
read_image(RefImg, 'package/good_01')
get_image_size(RefImg, Width, Height)
create_variation_model(Width, Height, 'byte', 'variation', VarModel)

* 收集 5–20 张正常样本（必须位置对齐）
prepare_direct_variation_model(GoodImages, VarModel, 30, 5, 'all')
* AbsThreshold=30：绝对灰度差阈值
* AbsVariation=5：标准差阈值

* 训练
train_variation_model(VarModel)

* 推理
read_image(TestImg, 'package/test_with_defect')
compare_ext_variation_model(TestImg, VarModel, 'absolute', 0, DefectRegions, AvgDiff, RangeDiff)

* 可视化
dev_clear_window()
dev_display(TestImg)
set_color(WindowHandle, 'red')
dev_display(DefectRegions)

* 输出严重度
disp_text(WindowHandle, 'Avg Diff: ' + AvgDiff$'.2f', 'window', 12, 12, 'yellow', 'box', 'black')
```

### 示例 4：OCV（字符验证）完整流程

```hdevelop
* Inspection_OCV.hdev
* 验证药盒喷码是否与参考字符串一致

* 训练阶段
read_image(TrainImg, 'pharma/good_batch_BX20240601')
create_ocv_proj('real_val', 0.0, OCVHandle)
traind_ocv_proj(TrainImg, OCVHandle, 'BX20240601', 'single')

* 推理阶段
read_image(TestImg, 'pharma/test_01')

* 简单比对
do_ocv_simple(TestImg, OCVHandle, 'BX20240601', Pattern, Score)
* Score 越接近 1 越好；< 0.5 通常 NG

if (Score > 0.5)
    disp_text(WindowHandle, 'PASS', 'window', 12, 12, 'green', 'box', 'black')
else
    disp_text(WindowHandle, 'FAIL', 'window', 12, 12, 'red', 'box', 'black')
endif

* 详细比对（找出哪个字符错）
do_ocv(TestImg, OCVHandle, 'BX20240601', Pattern, OcvcClass, OcvcScore)
* OcvcClass 数组：每个字符的 [0/1] 通过标记
* OcvcScore 数组：每个字符的 [0–1] 得分
```

---

## 6. 典型工业流水线

### 流水线 A：电池极片涂布缺陷检测（Variation Model）

```hdevelop
* 标准工艺：电池极片涂布必须均匀
* 通过 Variation Model 检测涂布缺失/堆积/气泡

read_image(RefImg, 'battery/good_001')
get_image_size(RefImg, Width, Height)
create_variation_model(Width, Height, 'byte', 'variation', VarModel)

* 多张正常样本
for i := 1 to 20 by 1
    read_image(GoodImg, 'battery/good_' + i$'.3')
    concat_obj(GoodImages, GoodImg, GoodImages)
endfor

prepare_direct_variation_model(GoodImages, VarModel, 25, 3, 'all')
train_variation_model(VarModel)

* 实时检测
while (true)
    grab_image_async(LiveImg, AcqHandle, -1)
    compare_ext_variation_model(LiveImg, VarModel, 'absolute', 0, Defects, AvgD, RangeD)
    
    if (AvgD > 10)
        * NG 报警
        set_color(WindowHandle, 'red')
        dev_display(Defects)
        control_io_device(IODev, 'output', 1)  * 触发剔除
    endif
endwhile
```

### 流水线 B：PCB 焊点检测（Bead Inspection）

```hdevelop
* PCB 通孔焊点（Bead）检测
* 焊点必须饱满、连续

create_bead_inspection_model('auto', 'manual', [], [], BeadModel)

* 从运动控制获取 Bead 路径
get_bead_path_from_plc(PathRows, PathCols, PathAngles)

* 检测
for i := 0 to |PathRows|-1 by 1
    apply_bead_inspection_model(PCBImg, BeadModel, Pose, PathRows[i], PathCols[i], 5, 5, R, C, Ang, Result)
    get_bead_inspection_result_object(Missing, Result, 'missing_parts')
    
    area_center(Missing, MissingArea, _, _)
    if (MissingArea > 100)
        * 报告 NG
    endif
endfor
```

### 流水线 C：服装布料瑕疵（Texture Inspection）

```hdevelop
* 训练
create_texture_inspection_model('basic', TexModel)
list_files('fabric/good', 'files', Files)
for i := 0 to |Files|-1 by 1
    read_image(Img, Files[i])
    add_texture_inspection_model_image(Img, TexModel)
endfor
train_texture_inspection_model(TexModel)

* 推理
while (true)
    grab_image(Img, AcqHandle)
    apply_texture_inspection_model(Img, TexModel, Result)
    get_texture_inspection_result_object(Defects, Result, 'novelty_regions')
    get_texture_inspection_score(Result, Score)
    
    if (Score > 0.7)
        * 标记瑕疵位置
    endif
endwhile
```

---

## 7. 常见陷阱与最佳实践

### 陷阱 1：训练样本不覆盖全部"正常"情况

每个检测器都对训练样本分布敏感——光照、位置、相机参数变化必须全覆盖。否则会出现"训练集过拟合到过窄分布"，推理时假阳率高。

**最佳实践**：训练样本 ≥ 10 张，覆盖白天/夜晚、不同批次、不同相机参数。

### 陷阱 2：Texture Inspection 对齐要求

**Texture Inspection** 对位置和光照敏感，推理时若目标有偏移，假阳率会急剧上升。

**最佳实践**：用模板匹配（`find_shape_model`）做粗定位后，再用 `affine_trans_image` 对齐。

### 陷阱 3：Variation Model 训练样本必须严格对齐

**Variation Model** 默认假设所有样本同一位置。若实际生产中目标会偏移 ±5 px，需：
- 先对齐再训练（用 `find_shape_model` + `affine_trans_image`）
- 或增大 `AbsVariation` 参数

### 陷阱 4：OCV 对字符形变极敏感

OCV 基于字符图像的灰度投影比对。若字符粗细、字体、对比度变化大，OCV 分数会骤降。

**最佳实践**：先 OCR 识别，再用 OCV 验证识别结果是否与期望一致（即"双保险"）。

### 陷阱 5：Bead Inspection 的路径必须准确

焊缝检测严重依赖"路径"——若路径与实际 Bead 偏差 > 10 px，所有检测结果都会失效。

**最佳实践**：路径从 CAD 直接获取，运动控制系统保证 ±1 mm 精度。

### 陷阱 6：训练模型与推理模型的 HALCON 版本不一致

低版本训练的模型在高版本可能读不出，或反之。

**最佳实践**：用 `read_*_model` 时显式指定兼容模式；保持训练/推理环境版本一致。

### 陷阱 7：选择错误的检测器

| 场景 | 选错会怎样 | 推荐 |
|------|------------|------|
| 周期纹理异常 | 用 Variation Model → 需每像素训练，样本不够会失败 | Texture Inspection |
| 完全对齐对比 | 用 Texture Inspection → 不需要纹理特征 | Variation Model |
| 连续路径缺陷 | 用 Texture Inspection → 不能指定路径 | Bead Inspection |
| 字符内容验证 | 用 OCR 替代 → OCR 会识别错字，仍判 OK | OCV |

### 陷阱 8：参数调节过拟合

`AbsThreshold`、`AbsVariation` 等参数调到刚好训练集 100% 通过 = 一定过拟合。

**最佳实践**：留 20% 样本做验证集；用验证集调节阈值，确保训练集 99% 通过 + 验证集 95% 通过。

---

## 8. 参数调优指南

### 8.1 Bead Inspection 关键参数

| 参数 | 默认 | 调整建议 |
|------|------|---------|
| `position_tolerance` | 5 px | 与相机分辨率 + 运动精度匹配 |
| `width_tolerance` | 3 px | 实际 Bead 宽度的 10% |
| `min_thickness` | 0.5 mm | 最小可接受厚度 |
| `max_thickness` | 5.0 mm | 最大可接受厚度 |

### 8.2 Texture Inspection 关键参数

| 参数 | 默认 | 调整建议 |
|------|------|---------|
| `'patch_size'` | 35 px | 纹理周期的 2 倍 |
| `'min_anomaly_score'` | 0.5 | 越低越敏感，但假阳多 |
| `'num_levels'` | 'auto' | 周期跨度大时增加 |
| `'novelty_threshold'` | 0.5 | 缺陷严重度阈值 |

### 8.3 Variation Model 关键参数

| 参数 | 默认 | 调整建议 |
|------|------|---------|
| `AbsThreshold` | 30 | 训练样本灰度差的 P95 |
| `AbsVariation` | 5 | 训练样本标准差的 P95 |
| `LightDark` | 'all' | 已知目标更亮/更暗时可缩小范围 |
| `Mode` | 'absolute' | 'absolute' 严格；'relative' 适应光照 |

### 8.4 OCV 关键参数

| 参数 | 默认 | 调整建议 |
|------|------|---------|
| `'pattern'` | - | 期望字符串（如 `'BX20240601'`） |
| `Threshold` | 0.5 | 越低越严格 |
| `Polarity` | 'dark_on_light' | 与字符颜色一致 |

---

## 9. 相关分类

- **Image / Filters**：Inspection 内部大量调用 `gauss_filter`、`emphasize` 做预处理。
- **Region / XLD**：检测结果以 region 或 XLD 形式输出。
- **Matching**：检测前必须先用 `find_shape_model` 定位。
- **Variation Model** 是 Inspection 子类，但 `compare_variation_model` 也被 OCR、Bead 等内部使用。
- **Deep Learning**：当传统 Inspection 不够用时（如布匹自然瑕疵变化大），切换到 `apply_dl_model` 异常检测。

---

## 10. 学习小结

Inspection 是 HALCON 的"**杀手锏**"——把行业经验封装成"训练 + 推理"两阶段，特别适合：

1. **Bead Inspection**：连续路径缺陷（汽车、电子封装）。
2. **Texture Inspection**：周期纹理（纺织、皮革、木纹）。
3. **Variation Model**：金标准比对（印刷、包装、屏幕）。
4. **OCV**：字符内容验证（医药、电池批号）。

**学习路径建议**：
- **第 1–2 周**：掌握 Variation Model（最通用），应用到 1 个印刷/包装项目。
- **第 3 周**：学 Texture Inspection，做布匹/皮革项目。
- **第 4 周**：学 Bead Inspection，做焊缝项目。
- **第 5 周**：学 OCV，做字符验证项目。

**核心心法**：
1. **检测器选对 = 80% 成功**：纹理用 Texture，对比用 Variation，路径用 Bead，字符用 OCV。
2. **训练样本决定上限**：样本覆盖全部正常情况 = 检测器上线。
3. **不要试图调参拯救选错的检测器**：如果 Texture Inspection 一直假阳，换 Variation Model。
4. **检测器 + 深度学习组合**：传统检测器出"大致 NG 区域" → 深度学习出"精确类别"。

最后：**专用检测器 = 行业经验，深度学习 = 通用方法**。两者结合使用，是工业视觉项目最高效的路径。
