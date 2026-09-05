# HALCON 算子分类详解：Legacy（过时算子）

> **分类定位**：HALCON 5.x–12.x 的旧算子集，仅用于维护老项目代码。
> **算子数量**：约 200 个，分散在 13 个 `toc_legacy_*.html` 子目录。
> **HALCON 版本**：26.05.0.0 Progress
> **官方文档**：`toc_legacy.html`（入口），子目录见各分类

---

## 1. 概述

Legacy 分类是 HALCON 保留的**向后兼容算子**，每个 `toc_legacy_*.html` 列出旧算子及对应的新版替代。**新项目严禁使用**——这些算子在最新版本中：
- 性能较低
- 接口不一致
- 文档/示例较少
- 可能在新版本中移除（虽然通常会保留兼容）

### 13 个 Legacy 子目录

| 子目录 | 涵盖 | 代表旧算子 |
|--------|------|-----------|
| `toc_legacy_2dmetrology.html` | 2D 量具旧版 | 旧版 `measure_*` |
| `toc_legacy_control.html` | 控制流旧版 | `dev_*` 早期版本 |
| `toc_legacy_develop.html` | 开发旧版 | 早期 dev_* |
| `toc_legacy_filters.html` | 滤波旧版 | `convol_image`（被 `convol_*` 替代） |
| `toc_legacy_graphics.html` | 显示旧版 | `disp_image_mode` |
| `toc_legacy_legmatchcomp.html` | 组件匹配旧版 | `find_component_model` 旧版 |
| `toc_legacy_morphology.html` | 形态学旧版 | `minkowski_*` 旧版 |
| `toc_legacy_ocr.html` | OCR 旧版 | `do_ocr_single`（被 `do_ocr_single_class_*` 替代） |
| `toc_legacy_regions.html` | 区域旧版 | 旧版 `select_*` |
| `toc_legacy_segmentation.html` | 分割旧版 | `auto_threshold` 旧版 |
| `toc_legacy_tools.html` | 工具旧版 | 早期几何工具 |
| `toc_legacy_xld.html` | XLD 旧版 | 早期 XLD 函数 |

---

## 2. 应用场景

| 场景 | 建议 |
|------|------|
| **新项目开发** | **禁止使用**——用对应的新算子 |
| **老项目维护** | 仅在已运行代码中使用，不要扩展 |
| **代码迁移** | 找到 Legacy → 新算子的映射，逐步替换 |
| **阅读老代码** | 知道这些是 Legacy，能识别并查阅替代 |

**典型行业**：维护 2010 年前后的 HALCON 5/6/7/8/9/10/11/12 项目。

---

## 3. 典型 Legacy 算子与替代

### 3.1 形态学（Legacy Morphology）

| 旧算子 | 新算子 |
|--------|--------|
| `minkowski_add1` / `minkowski_sub1` | `dilation1` / `erosion1` |
| `minkowski_add2` / `minkowski_sub2` | `dilation2` / `erosion2` |
| `golay_elements` (旧用法) | `gen_struct_elements` + Golay |

### 3.2 区域（Legacy Regions）

| 旧算子 | 新算子 |
|--------|--------|
| 旧版 `connection` | 新版（参数化） |
| 旧版 `select_shape` | 新版 `select_shape` |
| 旧版 `regiongrowing` | `regiongrowing`（参数重整） |

### 3.3 滤波（Legacy Filters）

| 旧算子 | 新算子 |
|--------|--------|
| `convol_image` | `convol_image` 新版 / `convol_fft` |
| 旧版 `rank_image` | `median_image` / `mean_image` |
| `gauss_image` | `gauss_filter` |

### 3.4 OCR（Legacy OCR）

| 旧算子 | 新算子 |
|--------|--------|
| `do_ocr_single` | `do_ocr_single_class_mlp` / `do_ocr_single_class_knn` / `do_ocr_single_class_svm` |
| `do_ocr_multi` | `do_ocr_multi_class_*` |
| `traind_ocr_class_box` | `traind_ocr_class_mlp` |
| `testd_ocr_class_box` | `testd_ocr_class_mlp` |
| `info_ocr_class_box` | `get_train_data_ocr_class_*` |

### 3.5 组件匹配（Legacy Component Matching）

| 旧算子 | 新算子 |
|--------|--------|
| 旧版 `find_component_model` | 新版（参数重整） |
| 旧版 `create_component_model` | 新版（参数重整） |
| 旧版 `train_model_components` | 新版 |

### 3.6 XLD（Legacy XLD）

| 旧算子 | 新算子 |
|--------|--------|
| 旧版 `gen_contours_skeleton_xld` | 新版（参数重整） |
| 旧版 `segment_contours_xld` | 新版（参数细化） |

### 3.7 工具（Legacy Tools）

| 旧算子 | 新算子 |
|--------|--------|
| `hough_lines`（旧） | `hough_lines` 新版 / `hough_line_trans` |
| 旧版 `fit_line_contour_xld` | 新版（更多拟合算法） |

### 3.8 2D Metrology（Legacy）

| 旧算子 | 新算子 |
|--------|--------|
| 旧版 `measure_pairs` | 新版（参数化 `Sigma`/`Threshold`） |
| 旧版 `gen_measure_rectangle2` | 新版（参数细化） |
| 旧版 `set_measure_param` | 新版 |

### 3.9 显示（Legacy Graphics）

| 旧算子 | 新算子 |
|--------|--------|
| 旧版 `disp_image` | 新版（参数重整） |
| 旧版 `set_color` | 新版 |

---

## 4. 如何识别 Legacy 算子

### 方法 1：查阅 `toc_legacy_*.html`

打开 `C:\Program Files\MVTec\HALCON-26.05-Progress\doc\html\reference\operators\toc_legacy.html`，点击对应分类。

### 方法 2：算子页"Alternatives" 部分

每个算子官方页都有 `Alternatives` / `See also` / `Successor` 字段，说明替代算子。

### 方法 3：HDevelop 运行时检查

```hdevelop
* 查询算子元信息
query_operator_info('legacy_op_name', Info)
```

---

## 5. 迁移策略

### 5.1 识别 → 替换 → 测试

```hdevelop
* 旧代码：
do_ocr_single(Character, Image, OcrHandle, Class, Confidence)

* 新代码（明确分类器）：
do_ocr_single_class_mlp(Character, Image, OcrHandle, Class, Confidence)
```

### 5.2 批量替换建议

1. **列出旧算子**：用 `grep` 搜索老代码中的 Legacy 算子
2. **逐一映射**：根据 `toc_legacy_*.html` 找到替代
3. **参数适配**：旧算子参数可能少或语义不同
4. **回归测试**：保证结果一致

### 5.3 何时保留 Legacy

- **生产环境已稳定的代码**：不值得为替换而重新测试
- **短期维护项目**：迁移成本高于收益
- **不支持升级的项目**：HALCON 版本受限于硬件

---

## 6. 常见 Legacy 算子（按出现频率排序）

### 高频出现

1. `do_ocr_single` → `do_ocr_single_class_mlp`
2. `do_ocr_multi` → `do_ocr_multi_class_mlp`
3. `convol_image`（旧） → `convol_image` 新版
4. `minkowski_add1/sub1` → `dilation1/erosion1`
5. `traind_ocr_class_box` → `traind_ocr_class_mlp`
6. `find_component_model`（旧） → 新版
7. `auto_threshold`（旧参数） → 新版

### 低频出现

- 旧版 `connection`、`select_shape`、`regiongrowing`
- 旧版 `fit_line_contour_xld`、`fit_circle_contour_xld`
- 旧版 `disp_image`、`disp_region`
- 旧版 `gen_measure_rectangle2`

---

## 7. 最佳实践

### 7.1 新项目原则

```hdevelop
* 错误用法（新项目）：
do_ocr_single(...)   * Legacy

* 正确用法：
do_ocr_single_class_mlp(...)
```

### 7.2 老项目维护原则

- **能用则不换**：稳定代码不轻易动
- **修复 bug 时顺手升级**：在确认安全的局部替换
- **重大重构前评估**：制定完整迁移计划

### 7.3 升级到新版本前

1. **列出所有 Legacy 算子**：`grep -rE 'do_ocr_single\b|minkowski_add1\b' *.hdev`
2. **检查替代算子**：查阅 `toc_legacy_*.html`
3. **准备回归测试**：保存原始输出，对比新结果
4. **逐个替换**：分阶段上线

---

## 8. 参数调优指南

| 场景 | 建议 |
|------|------|
| **新项目** | 100% 使用新算子 |
| **老项目** | 保留 Legacy，加注释 `// Legacy - replaced by xxx in new code` |
| **升级迁移** | 优先替换高频出现的 Legacy 算子（OCR、滤波、形态学） |

---

## 9. 相关分类

- **OCR**：Legacy OCR 主要被 `ocr_class_mlp` 系列替代。
- **Matching**：Legacy Component Matching 被新参数化版本替代。
- **Filters / Morphology**：Legacy 卷积与形态学算子被新框架替代。
- **2D Metrology**：Legacy 测量算子被新参数化版本替代。

---

## 10. 学习小结

Legacy 分类是"向后兼容层"。**学习优先级**：
1. **必知**：知道 Legacy 存在、知道去哪里查（`toc_legacy_*.html`）。
2. **重要**：识别 Legacy 算子（特别是 OCR、滤波、形态学）。
3. **专项**：维护老项目时，掌握对应 Legacy → 新算子的映射。

**核心要点**：
- **新项目严禁使用 Legacy 算子**——它们性能差、文档少、未来可能移除。
- **Legacy 算子主要用于老项目维护**——识别它们能正确阅读老代码。
- **每个 Legacy 算子都有官方替代**——查阅 `toc_legacy_*.html` 找到映射。
- **升级 HALCON 版本前先扫一遍 Legacy 算子**——避免升级后代码崩溃。

### 快速参考：Legacy → 新算子速查

```
do_ocr_single → do_ocr_single_class_mlp
do_ocr_multi → do_ocr_multi_class_mlp
traind_ocr_class_box → traind_ocr_class_mlp
convol_image (旧) → convol_image (新)
minkowski_add1 → dilation1
minkowski_sub1 → erosion1
```

> **后续阅读**：详见 `C:\Program Files\MVTec\HALCON-26.05-Progress\doc\html\reference\operators\toc_legacy.html` 及 13 个子目录。

---

**附录**：以下是 HALCON 26 中各 Legacy 子目录的官方入口：

- `toc_legacy_2dmetrology.html` — 2D 量具
- `toc_legacy_control.html` — 控制流
- `toc_legacy_develop.html` — 开发辅助
- `toc_legacy_filters.html` — 滤波
- `toc_legacy_graphics.html` — 显示
- `toc_legacy_legmatchcomp.html` — 组件匹配
- `toc_legacy_morphology.html` — 形态学
- `toc_legacy_ocr.html` — OCR
- `toc_legacy_regions.html` — 区域
- `toc_legacy_segmentation.html` — 分割
- `toc_legacy_tools.html` — 工具
- `toc_legacy_xld.html` — XLD
- `toc_legacy.html`（入口索引）