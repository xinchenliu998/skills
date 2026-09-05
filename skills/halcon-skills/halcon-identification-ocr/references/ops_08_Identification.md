# HALCON 算子分类详解：Identification

> **分类**：Identification（识别，条码/二维码）
> **子类数**：3（Barcode / Data Code / 3D & Generic）
> **学习优先级**：⭐⭐⭐（工业追溯、批次管理、防伪的必备能力）
> **典型应用场景**：从图像中定位、提取并解码 1D 条码、2D 矩阵码（DataMatrix、QR、PDF417、Aztec 等），并对 DPM（直接部件标识）激光雕刻码进行可靠识别。

---

## 1. 概述

Identification 是 HALCON 在工业追溯与产品识别方向的核心模块。它与 OCR 的"字符识别"不同——关注的是**码符号**（1D 条码、2D 矩阵码、堆叠码、DPM 码）的检测、定位与解码。

HALCON 26 的 Identification 模块覆盖：

- **1D 条码**（Barcode）：EAN/UPC/Code 39/93/128/GS1-128/Codabar/PDF417 等。
- **2D 矩阵码**（Data Code 2D）：DataMatrix、QR、Micro QR、Aztec、MaxiCode、DotCode、PDF417、GS1 DataMatrix、GS1 QR。
- **3D & Generic**：`find_box_3d`（箱体尺寸检测）、`find_marks_and_pose`（标定标志识别与位姿）。

它与 OCR 共享"读取字符串"的接口，但**解码算法完全不同**：OCR 走字符切分 + 分类器，Identification 走码字定位 + RS 纠错 + 解码。

---

## 2. 应用场景

1. **物流分拣与零售**：EAN-13/UPC/QR 扫码，配送线。
2. **医药与食品追溯**：GS1 DataMatrix（监管码）、GS1-128（批次）。
3. **汽车 VIN 识别**：DataMatrix 标牌、QR 二维码。
4. **电子元器件批次**：PCB 板 DataMatrix、QR（追溯 IC 批次）。
5. **DPM 激光雕刻码**：金属/塑料件直接打码（点刻、激光蚀刻），需高分辨率相机+特殊照明。

---

## 3. 子分类详解

| 子分类 | 职责 | 代表算子 |
|--------|------|----------|
| **Barcode (1D)** | 一维条码 + 堆叠码 | `create_bar_code_model`、`find_bar_code`、`decode_bar_code_rectangle2`、`set_bar_code_param`、`get_bar_code_*`、`read/write_bar_code_model` |
| **Data Code (2D)** | 二维矩阵码 | `create_data_code_2d_model`、`find_data_code_2d`、`get_data_code_2d_*`、`set_data_code_2d_param`、`read/write_data_code_2d_model` |
| **3D / Generic** | 三维 / 通用 | `find_box_3d`、`find_marks_and_pose` |

---

## 4. HALCON 支持的码制（完整列表）

### 4.1 一维条码 (1D Barcode)

| 码制 | 典型应用 | 是否支持 EAN/UPC 校验 |
|------|----------|------------------------|
| **EAN-13** | 零售商品 | ✓ |
| **EAN-8** | 小商品 | ✓ |
| **UPC-A** | 美国零售 | ✓ |
| **UPC-E** | 美国小商品 | ✓ |
| **Code 39** | 工业、军工、汽车 | — |
| **Code 93** | 物流 | — |
| **Code 128** | 物流、库存 | — |
| **GS1-128 (UCC/EAN-128)** | 供应链追溯 | — |
| **Codabar** | 图书馆、血库 | — |
| **2/5 Interleaved** | 工业、仓储 | — |
| **MSI** | 库存 | — |
| **Pharmacode** | 药品包装 | — |
| **PDF417** | 堆叠码（驾照、票务） | — |

### 4.2 二维矩阵码 (2D Data Code)

| 码制 | 典型应用 | 备注 |
|------|----------|------|
| **DataMatrix (ECC 200)** | 电子、汽车、医药、邮政 | 最常用 |
| **QR Code (Model 1/2)** | 移动支付、追溯 | 支持中文/日文模式 |
| **Micro QR** | 小尺寸电子 | 单角定位 |
| **Aztec Code** | 票务、运输 | 中心定位 |
| **MaxiCode** | 物流（UPS） | 牛眼中心 |
| **PDF417** | 驾照、登机牌 | 堆叠码 |
| **DotCode** | 高速喷码 | 工业喷墨 |
| **GS1 DataMatrix** | 医药追溯 | GS1 应用标识符 |
| **GS1 QR** | GS1 零售 | GS1 应用标识符 |
| **GS1 Aztec** | 医疗保健 | GS1 应用标识符 |

### 4.3 DPM（直接部件标识）码

DPM 码是直接用激光/点刻/喷墨在金属、塑料、玻璃上打的码。HALCON 通过以下手段提高识别率：

- 更高对比度算子（`emphasize`、`scale_image_max`）
- `'strict_recognition'` 参数调松
- 多种 `polarity` 兼容（`'light_on_dark'` / `'dark_on_light'` / `'any'`）
- 通过 `'module_size_min'` / `'module_size_max'` 限制模块尺寸

---

## 5. 核心算子详解

| 算子 | 用途 | 输入 | 输出 | 典型用法 |
|------|------|------|------|----------|
| `create_bar_code_model` | 创建条码模型 | CodeType, GenParamNames, GenParamValues | BarCodeHandle | 1D 条码入口 |
| `find_bar_code` | 检测并解码 1D 条码 | Image, SymbolRegions, BarCodeHandle, CodeType, Timeout | BarCodeStrings, BarCodeCandidates, DecodedStrings | 核心识别算子 |
| `decode_bar_code_rectangle2` | 在指定 ROI 中解码 | Image, BarCodeHandle, Rect2Row, Rect2Col, Rect2Phi, Rect2Length1, Rect2Length2, CodeType | DecodedDataStrings | 已知 ROI 区域解码 |
| `set_bar_code_param` | 设置条码参数 | BarCodeHandle, GenParamName, GenParamValue |  | 调优识别 |
| `get_bar_code_param` | 读取参数 | BarCodeHandle, GenParamName | GenParamValue | 调试 |
| `get_bar_code_result` | 取结果（区域、方向等） | BarCodeHandle, CandidateHandle, ResultName | ResultValue | 取 `decoded_string`、`orientation`、`element_size_*` 等 |
| `get_bar_code_object` | 取对象 | BarCodeHandle, CandidateHandle, ObjectName | Object | 取 SymbolRegions 等 |
| `clear_bar_code_model` | 释放模型 | BarCodeHandle |  | 清理 |
| `read_bar_code_model` / `write_bar_code_model` | 序列化 | FileName, BarCodeHandle | BarCodeHandle | 跨进程使用 |
| `create_data_code_2d_model` | 创建 2D 码模型 | SymbolType, GenParamNames, GenParamValues | DataCodeHandle | 2D 码入口 |
| `find_data_code_2d` | 检测并解码 2D 码 | Image, SymbolXLDs, DataCodeHandle, Timeout, GenParamNames, GenParamValues | ResultHandles, DecodedDataStrings | 核心识别算子 |
| `get_data_code_2d_results` | 取结果字符串 | BarCodeHandle, CandidateHandle, ResultName | ResultValue | 取 `decoded_string` / `decoded_data_*` |
| `get_data_code_2d_objects` | 取对象 | DataCodeHandle, CandidateHandle, ObjectName | Object | 取 SymbolXLDs / SearchResults |
| `set_data_code_2d_param` | 设置参数 | DataCodeHandle, GenParamName, GenParamValue |  | 调优 |
| `get_data_code_2d_param` | 读取参数 | DataCodeHandle, GenParamName | GenParamValue | 调试 |
| `clear_data_code_2d_model` | 释放 | DataCodeHandle |  | 清理 |
| `read_data_code_2d_model` / `write_data_code_2d_model` | 序列化 | FileName, DataCodeHandle | DataCodeHandle | 跨进程使用 |
| `query_bar_code_parameters` | 查询支持的参数 | (none) | Names, Defaults, Restrictions, Tooltips | 查文档 |
| `query_data_code_2d_parameters` | 同上 | (none) | Names, Defaults, Restrictions, Tooltips | 查文档 |

---

## 6. HDevelop 示例代码

### 示例 1：EAN-13 零售商品条码识别

**场景**：超市结账/物流入库，EAN-13 条码。
**功能**：`create_bar_code_model` 创建模型 → `find_bar_code` 检测 + 解码 → 可视化结果。
**预期输出**：解码字符串（如 `'4006381333931'`），条码区域叠加显示。

```hdevelop
* ============================================================
* 示例1：EAN-13 条码识别
* ============================================================
dev_update_off ()
dev_close_window ()
read_image (Image, 'barcode/ean13/ean13_01')
get_image_size (Image, Width, Height)
dev_open_window (0, 0, Width / 2, Height / 2, 'black', WindowHandle)
dev_display (Image)

* 1) 创建条码模型
create_bar_code_model ('element_size_min', 3, BarCodeHandle)
set_bar_code_param (BarCodeHandle, 'check_checksum', 'true')
set_bar_code_param (BarCodeHandle, 'persistence', 1)

* 2) 检测并解码
find_bar_code (Image, SymbolRegions, BarCodeHandle, 'EAN-13', \
               DecodedStrings)

* 3) 显示结果
dev_set_color ('green')
dev_set_line_width (2)
dev_display (SymbolRegions)
dev_set_color ('yellow')
for i := 0 to |DecodedStrings| - 1 by 1
    disp_text (WindowHandle, DecodedStrings[i], 'window', 10, 10 + 200 * i, \
               'black', 'box', 'false')
endfor
dev_set_line_width (1)

clear_bar_code_model (BarCodeHandle)
dev_update_on ()
stop ()
```

### 示例 2：DataMatrix 工业码识别

**场景**：电子元器件 PCB 上的 DataMatrix。
**功能**：`create_data_code_2d_model` → `find_data_code_2d` → 取所有结果。
**预期输出**：解码内容（含 GS1 AI 段如 `0100012345678905`）、位置、模块尺寸、QR 质量等。

```hdevelop
* ============================================================
* 示例2：DataMatrix 工业码识别
* ============================================================
dev_update_off ()
dev_close_window ()
read_image (Image, 'datacode/datacode_01')
get_image_size (Image, Width, Height)
dev_open_window (0, 0, Width / 2, Height / 2, 'black', WindowHandle)
dev_display (Image)

* 1) 创建 2D 码模型
create_data_code_2d_model ('Data Matrix ECC 200', \
                            ['default_parameters', 'polarity'], \
                            ['standard_recognition', 'dark_on_light'], \
                            DataCodeHandle)

* 2) 检测 + 解码
find_data_code_2d (Image, SymbolXLDs, DataCodeHandle, \
                    [], [], ResultHandles, DecodedStrings)

* 3) 取每个码的详细信息
for i := 0 to |DecodedStrings| - 1 by 1
    get_data_code_2d_results (DataCodeHandle, ResultHandles[i], \
                              'decoded_string', DecodedData)
    get_data_code_2d_results (DataCodeHandle, ResultHandles[i], \
                              'symbol_size', SymbolSize)
    get_data_code_2d_results (DataCodeHandle, ResultHandles[i], \
                              'module_size', ModuleSize)
    * 显示
    dev_set_color ('green')
    dev_set_line_width (2)
    dev_display (SymbolXLDs)
    dev_set_color ('yellow')
    Message := 'Code: ' + DecodedData + '  Size: ' + SymbolSize + \
               '  Module: ' + ModuleSize$'.2f'
    disp_text (WindowHandle, Message, 'window', 10, 10 + 180 * i, \
               'black', 'box', 'false')
endfor
dev_set_line_width (1)

clear_data_code_2d_model (DataCodeHandle)
dev_update_on ()
stop ()
```

### 示例 3：QR Code + GS1 解析

**场景**：商品包装上的 GS1 QR（含应用标识符 `01` 制品编码 + `17` 有效期 + `10` 批号）。
**功能**：识别 QR 并解析 GS1 AI 段。
**预期输出**：原始串 + GS1 解析后的 `(AI, Value)` 列表。

```hdevelop
* ============================================================
* 示例3：GS1 QR Code 识别 + AI 解析
* ============================================================
dev_update_off ()
dev_close_window ()
read_image (Image, 'datacode/qr_gs1_01')
get_image_size (Image, Width, Height)
dev_open_window (0, 0, Width / 2, Height / 2, 'black', WindowHandle)
dev_display (Image)

* 1) 创建 QR 模型（允许多种模式）
create_data_code_2d_model ('QR Code', 'default_parameters', 'enhanced_recognition', \
                            DataCodeHandle)
* 启用 GS1 AI 解析
set_data_code_2d_param (DataCodeHandle, 'enable_gs1', 'true')

* 2) 识别
find_data_code_2d (Image, SymbolXLDs, DataCodeHandle, [], [], \
                    ResultHandles, DecodedStrings)

* 3) 取 GS1 解析结果
for i := 0 to |DecodedStrings| - 1 by 1
    get_data_code_2d_results (DataCodeHandle, ResultHandles[i], \
                              'decoded_string', RawString)
    get_data_code_2d_results (DataCodeHandle, ResultHandles[i], \
                              'gs1_ai', Gs1AI)
    dev_set_color ('green')
    dev_set_line_width (2)
    dev_display (SymbolXLDs)
    dev_set_color ('yellow')
    disp_text (WindowHandle, 'Raw: ' + RawString, 'window', 10, 10, \
               'black', 'box', 'false')
    disp_text (WindowHandle, 'GS1: ' + Gs1AI, 'window', 30, 10, \
               'black', 'box', 'false')
endfor
dev_set_line_width (1)

clear_data_code_2d_model (DataCodeHandle)
dev_update_on ()
stop ()
```

---

## 7. 典型工业流水线

### 流水线 A：在线扫码与追溯

```
grab_image (产线)
  → reduce_domain (裁剪到扫码工位)
  → emphasize (提升对比度)
  → find_data_code_2d
  → get_data_code_2d_results ('decoded_string')
  → MES 系统写入批次
```

### 流水线 B：DPM 激光雕刻码

```
grab_image (高分辨率相机 5MP+ + 同轴光)
  → median_image (去椒盐噪声)
  → scale_image_max (拉伸对比度)
  → create_data_code_2d_model ('Data Matrix ECC 200', 'enhanced_recognition')
  → set_data_code_2d_param ('polarity', 'any')
  → set_data_code_2d_param ('module_size_min', 4)
  → find_data_code_2d
```

### 流水线 C：多码批量识别

```
grab_image
  → find_bar_code (一次多种码型)
  → get_bar_code_result ('decoded_string')
  → concat_obj (聚合)
  → 写入数据库
```

---

## 8. 常见陷阱与最佳实践

1. **`element_size_min` 偏小导致误检**：必须用 `'element_size_min'` + `'element_size_max'` 双阈值框定码元尺寸。
2. **`polarity` 设置错误**：激光雕刻码通常是 `light_on_dark`、印刷码是 `dark_on_light`，不确定时用 `'any'`。
3. **多码场景的 ROI 拆分**：若需分别读不同区域，先 `reduce_domain` 再 `find_*`，否则多码互相干扰。
4. **倾斜码的预校正**：低分辨率下码严重倾斜 → 先用 `image_to_world_plane` 校平。
5. **GS1 解析依赖 `enable_gs1`**：默认 `false`，必须显式开启才能拿 `gs1_ai` 字段。
6. **超时控制**：用 `find_data_code_2d(Image, ..., Timeout, ...)` 防止长尾拖累产线节拍。
7. **`strict_recognition` 严格度**：质量好时用 `standard_recognition`、噪声大用 `enhanced_recognition`、极端差用 `maximum_recognition`（最慢但最稳）。
8. **DPM 一定要高分辨率**：模块尺寸 < 3 px 的码必须使用 5MP+ 相机 + 远心/同轴光。
9. **跨域使用模型**：训练/识别不同机器时用 `read_bar_code_model` / `write_bar_code_model` 序列化。
10. **PDF417 是堆叠码**：在 HALCON 中既属于 1D Barcode，也属于 2D DataCode（`PDF417`）；按需选择 `find_bar_code` 或 `find_data_code_2d`。

---

## 9. 参数调优指南

| 算子 | 关键参数 | 推荐值 | 调整策略 |
|------|----------|--------|----------|
| `create_bar_code_model` | `'element_size_min'` | 2–5 | 视实际码元尺寸调 |
| `create_bar_code_model` | `'element_size_max'` | 50–200 | 大条码上调 |
| `set_bar_code_param` | `'check_checksum'` | `'true'` | 启用校验防错 |
| `set_bar_code_param` | `'persistence'` | 0/1 | 1=同一区域多次读取择优 |
| `set_bar_code_param` | `'meas_thresh'` | 0.01–0.1 | 边缘对比度阈值 |
| `set_bar_code_param` | `'num_scanlines'` | 5–30 | 扫描线数，多=慢但稳 |
| `create_data_code_2d_model` | `'default_parameters'` | `'enhanced_recognition'` | 推荐 |
| `set_data_code_2d_param` | `'polarity'` | `'any'` | 未知极性时用 any |
| `set_data_code_2d_param` | `'module_size_min'` | 3–6 | 物理最小码元像素数 |
| `set_data_code_2d_param` | `'module_size_max'` | 30–100 | 物理最大码元像素数 |
| `set_data_code_2d_param` | `'module_gap'` | `'auto'` | 模块间距 |
| `set_data_code_2d_param` | `'mirror'` | `'any'` | 镜像兼容 |
| `set_data_code_2d_param` | `'contrast_min'` | 5–20 | 最低对比度 |
| `set_data_code_2d_param` | `'sl_angle_max'` | 0.1–0.3 | 最大倾斜角（rad） |
| `set_data_code_2d_param` | `'enable_gs1'` | `'true'` | GS1 解析 |
| `set_data_code_2d_param` | `'quality_isoiec15415_*'` | `'true'` | ISO/IEC 15415 质量分 |
| `find_data_code_2d` | `Timeout` | 0.0–1.0 | 产线节拍约束 |
| `find_data_code_2d` | `'min_score'` | 0.3–0.6 | 最低码质量分 |

---

## 10. 相关分类

- **OCR**：字符识别的"同胞"模块，原理不同但读取流程相似。
- **Image**：`reduce_domain`、`emphasize` 是预处理关键。
- **Filters**：`median_image`、`gauss_filter` 改善信噪比。
- **Matching**：基于模板的码定位可作 ROI 提取。
- **Calibration**：`image_to_world_plane` 用于倾斜校正。
- **File**：`read_image` / `write_image` 离线扫码存档。

---

## 11. 学习小结

Identification 是工业追溯的"身份证"读取器。核心要点：

1. **1D vs 2D 选型**：先看客户码制，再决定 `create_bar_code_model` 还是 `create_data_code_2d_model`。
2. **码元尺寸（`element_size_min` / `module_size_min`）** 是识别的成败关键——必须先用标定板/直尺量出实际像素尺寸。
3. **`'enhanced_recognition'` 是首选**：比 `'standard_recognition'` 慢 1.5×，但漏读率显著降低。
4. **`polarity = 'any'`** 是默认安全的兼容性选择，但牺牲少量速度。
5. **DPM 码**需要高分辨率相机 + 远心/同轴光 + `enhanced_recognition` + `'any'` 极性 + `median_image` 预处理。
6. **GS1 解析**在医药、食品、汽车强制要求——记得 `set_data_code_2d_param('enable_gs1', 'true')`。
7. **超时控制（`Timeout`）** 是产线节拍保障，常见 0.5–1.0 秒。
8. **质量评分**（`get_data_code_2d_results('quality_*')`）可用于工艺反馈——分级淘汰低质量码。
