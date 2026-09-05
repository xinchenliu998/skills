# Halcon OCR与条码/二维码识别技能手册

> 学习来源: `OCR/`, `Identification/`, `Applications/Bar-Codes/`, `Applications/Data-Codes/`
> 涵盖Task16：OCR字符识别、条码识别、二维码识别

---

## 一、识别方法总览

| 类型 | 算子前缀 | 码制 | ⭐场景 |
|---|---|---|---|
| **条码(1D)** | `create/find_bar_code` | EAN-13,Code128,Code39等 | 商品/物流条码 |
| **DataMatrix** ⭐ | `create/find_data_code_2d` | ECC200 | ⭐工业零件标记(最常用) |
| **QR码** | `create/find_data_code_2d` | QR Code | 通用二维码 |
| **PDF417** | `create/find_data_code_2d` | PDF417 | 证件/票据 |
| **OCR** | `find_text/do_ocr_*` | 文字 | 日期/批号/序列号 |

---

## 二、条码识别(1D Bar Code)

### 完整流程
```
1. create_bar_code_model → 创建条码模型
2. set_bar_code_param → 设置参数(可选)
3. find_bar_code → 识别条码
4. get_bar_code_result → 获取结果
5. clear_bar_code_model → 释放
```

### 核心算子

#### create_bar_code_model
```
create_bar_code_model(GenParamName, GenParamValue, BarCodeHandle)
```

#### find_bar_code ⭐
```
find_bar_code(Image, SymbolRegions, BarCodeHandle, CodeType, DecodedDataStrings)
```
| CodeType | 码制 |
|---|---|
| `'EAN-13'` | EAN-13 |
| `'Code 128'` | Code 128 |
| `'Code 39'` | Code 39 |
| `'2/5 Industrial'` | 2/5工业码 |
| `'auto'` | 自动识别 |

#### set_bar_code_param — 优化参数
```
set_bar_code_param(BarCodeHandle, GenParamName, GenParamValue)
```
| 参数 | 值 | 说明 |
|---|---|---|
| `'element_size_min'` | 1.5 | 最小元素尺寸 |
| `'element_size_max'` | 5.0 | 最大元素尺寸 |
| `'meas_thresh'` | 0.5 | 测量阈值 |
| `'num_scanlines'` | 10~30 | 扫描线数(越多越鲁棒) |

---

## 三、二维码识别(2D Data Code) ⭐

### 完整流程
```
1. create_data_code_2d_model → 创建2D码模型
2. set_data_code_2d_param → 设置参数(可选)
3. find_data_code_2d → 识别二维码
4. get_data_code_2d_results → 获取详细结果
5. clear_data_code_2d_model → 释放
```

### 核心算子

#### create_data_code_2d_model ⭐
```
create_data_code_2d_model(CodeType, GenParamName, GenParamValue, DataCodeHandle)
```
| CodeType | 码制 |
|---|---|
| `'Data Matrix ECC 200'` ⭐ | DataMatrix(工业最常用) |
| `'QR Code'` | QR码 |
| `'Micro QR Code'` | Micro QR |
| `'PDF417'` | PDF417 |
| `'Aztec Code'` | Aztec |
| `'DotCode'` | DotCode |

#### find_data_code_2d ⭐
```
find_data_code_2d(Image, SymbolXLDs, DataCodeHandle, GenParamName, GenParamValue, 
                   ResultHandles, DecodedDataStrings)
```

#### 低质量码优化参数
```
set_data_code_2d_param(Handle, 'default_parameters', 'enhanced_recognition')
set_data_code_2d_param(Handle, 'symbol_size_min', 10)
set_data_code_2d_param(Handle, 'symbol_size_max', 200)
set_data_code_2d_param(Handle, 'module_size_min', 3)
set_data_code_2d_param(Handle, 'module_size_max', 20)
set_data_code_2d_param(Handle, 'contrast_min', 10)  // 低对比度
set_data_code_2d_param(Handle, 'polarity', 'any')    // 极性不定
```

---

## 四、OCR文字识别

### 方法对比
| 方法 | 算子 | 训练 | 适用 |
|---|---|---|---|
| **find_text** ⭐ | 自动文本查找 | 需OCR分类器 | 通用文本 |
| **do_ocr_single_class_mlp** | MLP分类 | 需训练 | 工业打印字符 |
| **do_ocr_single_class_svm** | SVM分类 | 需训练 | 复杂场景 |

### OCR完整流程
```
1. 预处理: 二值化/增强
2. 文本分割: find_text 或 手动分割(threshold+connection+select_shape)
3. 排序: sort_region(left_to_right/top_to_bottom)
4. 识别: do_ocr_single_class_mlp / do_ocr_multi_class_mlp
5. 结果拼接
```

### 核心算子
```
// 自动文本查找
create_text_model_reader('auto', OcrHandle, TextModel)
find_text(Image, TextModel, TextResult)
get_text_result(TextResult, 'class', RecognizedText)

// 手动OCR
read_ocr_class_mlp('Industrial_0-9A-Z_NoRej.omc', OcrHandle)
do_ocr_multi_class_mlp(SortedRegions, Image, OcrHandle, Class, Confidence)
```

### 常用OCR分类器文件
| 文件 | 字符集 |
|---|---|
| `'Industrial_0-9A-Z_NoRej.omc'` ⭐ | 工业字符(数字+大写字母) |
| `'Industrial_0-9_NoRej.omc'` | 仅数字 |
| `'Document_0-9A-Z_NoRej.omc'` | 文档字符 |
| `'DotPrint_0-9A-Z.omc'` | 点阵打印 |
| `'SEMI_font.omc'` | 半导体字符 |

---

## 五、C# HalconDotNet 代码模板

### 模板1: 条码识别 ⭐
```csharp
HObject image, symbolRegions;
HTuple barCodeHandle, decodedStrings;

HOperatorSet.ReadImage(out image, imagePath);
HOperatorSet.CreateBarCodeModel(new HTuple(), new HTuple(), out barCodeHandle);
// 识别(自动类型)
HOperatorSet.FindBarCode(image, out symbolRegions, barCodeHandle, "auto", out decodedStrings);

for (int i = 0; i < decodedStrings.Length; i++)
    Console.WriteLine($"条码{i+1}: {decodedStrings[i].S}");

HOperatorSet.ClearBarCodeModel(barCodeHandle);
symbolRegions.Dispose(); image.Dispose();
```

### 模板2: DataMatrix二维码识别 ⭐⭐
```csharp
HObject image, symbolXLDs;
HTuple dataCodeHandle, resultHandles, decodedStrings;

HOperatorSet.ReadImage(out image, imagePath);
HOperatorSet.CreateDataCode2dModel("Data Matrix ECC 200", new HTuple(), new HTuple(), out dataCodeHandle);

// 低质量优化(可选)
HOperatorSet.SetDataCode2dParam(dataCodeHandle, "default_parameters", "enhanced_recognition");

// 识别
HOperatorSet.FindDataCode2d(image, out symbolXLDs, dataCodeHandle, 
    new HTuple(), new HTuple(), out resultHandles, out decodedStrings);

for (int i = 0; i < decodedStrings.Length; i++)
    Console.WriteLine($"DataMatrix{i+1}: {decodedStrings[i].S}");

HOperatorSet.ClearDataCode2dModel(dataCodeHandle);
symbolXLDs.Dispose(); image.Dispose();
```

### 模板3: QR码识别
```csharp
HTuple dataCodeHandle, resultHandles, decodedStrings;
HObject symbolXLDs;

HOperatorSet.CreateDataCode2dModel("QR Code", new HTuple(), new HTuple(), out dataCodeHandle);
HOperatorSet.FindDataCode2d(image, out symbolXLDs, dataCodeHandle,
    new HTuple(), new HTuple(), out resultHandles, out decodedStrings);
```

### 模板4: OCR字符识别
```csharp
HObject image, region, connected, sorted;
HTuple ocrHandle, charClass, confidence;

HOperatorSet.ReadImage(out image, imagePath);
// 二值化分割字符
HOperatorSet.Threshold(image, out region, 0, 128);
HOperatorSet.Connection(region, out connected);
HOperatorSet.SelectShape(connected, out var chars, "area", "and", 100, 99999);
// 排序(从左到右)
HOperatorSet.SortRegion(chars, out sorted, "character", "true", "row");
// OCR识别
HOperatorSet.ReadOcrClassMlp("Industrial_0-9A-Z_NoRej.omc", out ocrHandle);
HOperatorSet.DoOcrMultiClassMlp(sorted, image, ocrHandle, out charClass, out confidence);

string result = "";
for (int i = 0; i < charClass.Length; i++)
    result += charClass[i].S;
Console.WriteLine($"识别结果: {result}");

HOperatorSet.ClearOcrClassMlp(ocrHandle);
sorted.Dispose(); chars.Dispose(); connected.Dispose(); region.Dispose(); image.Dispose();
```
