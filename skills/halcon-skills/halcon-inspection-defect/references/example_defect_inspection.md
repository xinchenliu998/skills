# Halcon 缺陷检测技能手册

> 学习来源: `Inspection/Texture-Inspection/`, `Inspection/Bead-Inspection/`, `Filters/FFT/`, `Morphology/`
> 涵盖12个例程：纹理检测、胶珠检测、FFT划痕检测、形态学缺陷检测

---

## 一、缺陷检测方法分类与对比

| 方法 | 核心算子 | 适用场景 | 精度 | 速度 | 是否需要训练 |
|---|---|---|---|---|---|
| **纹理检测模型** ⭐ | `create/train/apply_texture_inspection_model` | 纹理表面(织物/皮革/塑料) | 高 | 中 | ✅需要好品图 |
| **形态学差分(PCB法)** | `gray_opening/closing + dyn_threshold` | 规则背景+异常缺陷 | 中 | 快 | ❌ |
| **FFT带通滤波** | `rft_generic + bandpass_image` | 周期纹理上的划痕 | 高 | 中 | ❌ |
| **背景减除** | `sub_image + threshold` | 有标准参考图 | 高 | 最快 | ❌(需参考图) |
| **胶珠检测** | `create/apply_bead_inspection_model` | 胶线涂布检测 | 高 | 中 | ✅需要模板 |
| **圆度/面积筛选** | `select_shape(circularity)` | 规则目标异常判断 | 低 | 最快 | ❌ |

---

## 二、纹理检测模型 ⭐

### 完整流程
```
1. create_texture_inspection_model('basic') → 创建模型
2. 添加多张好品图: add_texture_inspection_model_image(GoodImage)
3. 可选调参: set_texture_inspection_model_param('sensitivity', 0.3)
4. train_texture_inspection_model → 训练
5. 可选: write_texture_inspection_model 保存
6. 检测: apply_texture_inspection_model(TestImage) → NoveltyRegion(缺陷区域)
7. 获取结果: get_texture_inspection_result_object → 详细结果
```

### 核心算子
| 算子 | 功能 |
|---|---|
| `create_texture_inspection_model('basic')` | 创建模型 |
| `add_texture_inspection_model_image(Img, Model)` | 添加训练图 |
| `set_texture_inspection_model_param(Model, Name, Val)` | 设置参数 |
| `train_texture_inspection_model(Model)` | 训练 |
| `apply_texture_inspection_model(Img, NoveltyReg, Model)` | 检测→缺陷区域 |

### 关键参数
| 参数 | 默认 | 范围 | 说明 |
|---|---|---|---|
| `'sensitivity'` | 0.3 | 0~1 | 越高越敏感，越多误检 |
| `'patch_type'` | 'novice' | novice/expert | 补丁模式 |
| `'num_levels'` | 3 | 1~5 | 金字塔层数 |

---

## 三、胶珠检测 (Bead Inspection)

### 完整流程
```
1. create_bead_inspection_model → 创建模型
2. 定义参考轮廓(XLD): 胶线理想路径
3. set_bead_inspection_model_param → 设置宽度容差等
4. apply_bead_inspection_model(TestImg) → 检测结果
5. get_bead_inspection_result → 获取OK/NG区域
```

### 核心算子
| 算子 | 功能 |
|---|---|
| `create_bead_inspection_model(Contour, W, H, Model)` | 创建+指定宽度 |
| `apply_bead_inspection_model(Img, Model, LeftContour, RightContour, Error)` | 检测 |
| `get_bead_inspection_result(Result, Model, 'result_type')` | 获取结果 |
| `clear_bead_inspection_model(Model)` | 释放 |

---

## 四、FFT带通划痕检测

### 完整流程
```
1. read_image → 读取待检图
2. rft_generic(Image, FFT, 'to_freq', 'none', 'complex', 'fft') → FFT变换
3. gen_bandpass(BandPass, ...) 或手动构造频域滤波器
4. convol_fft(FFT, BandPass, FilteredFFT) → 频域滤波
5. rft_generic(FilteredFFT, Filtered, 'from_freq', ...) → 逆FFT
6. threshold(Filtered, Scratches, ...) → 阈值提取划痕
```

### 核心算子
| 算子 | 功能 |
|---|---|
| `rft_generic(Img, FFT, 'to_freq', ...)` | 实数FFT |
| `gen_bandpass_image(BP, W, H, Freq)` | 生成带通滤波器 |
| `convol_fft(FFT, Filter, Result)` | 频域卷积 |
| `rft_generic(FFT, Img, 'from_freq', ...)` | 逆FFT |

---

## 五、形态学差分缺陷检测（PCB法）

已在 `skill/morphology_operations.md` 中详述，核心流程：
```
gray_opening_shape(7,7,'octagon') → 消除亮缺陷
gray_closing_shape(7,7,'octagon') → 消除暗缺陷
dyn_threshold(Opening, Closing, 75, 'not_equal') → 缺陷区域
```

---

## 六、缺陷检测策略决策树

```
表面类型
├─ 规则纹理(织物/编织物)？
│   └─ 纹理检测模型 ⭐ (train+apply)
├─ 周期性纹理+划痕？
│   └─ FFT带通滤波
├─ 均匀背景+随机缺陷？
│   ├─ 有参考图 → sub_image背景减除
│   └─ 无参考图 → 形态学差分(PCB法)
├─ 胶线/涂布检测？
│   └─ 胶珠检测模型
├─ 规则目标(圆孔/矩形)异常？
│   └─ select_shape(circularity等) ⭐背光小孔
└─ 背光小孔杂光检测？
    └─ 综合方案:
        1. illuminate → emphasize (预处理, Task02)
        2. binary_threshold (分割, Task09)
        3. opening_circle + fill_up (清理, Task08)
        4. select_shape(circularity, convexity, area) (筛选, Task10)
        5. 多特征评分 → OK/NG判定
```

---

## 七、C# HalconDotNet 代码模板

### 模板1: 纹理检测完整流程 ⭐
```csharp
HTuple model;
HObject noveltyRegion;

// 1. 创建模型
HOperatorSet.CreateTextureInspectionModel("basic", out model);

// 2. 添加好品训练图(多张)
for (int i = 1; i <= 5; i++)
{
    HObject trainImg;
    HOperatorSet.ReadImage(out trainImg, $"good_{i}.png");
    HTuple indices;
    HOperatorSet.AddTextureInspectionModelImage(trainImg, model, out indices);
    trainImg.Dispose();
}

// 3. 设置敏感度
HOperatorSet.SetTextureInspectionModelParam(model, "sensitivity", 0.3);

// 4. 训练
HOperatorSet.TrainTextureInspectionModel(model);

// 5. 检测
HObject testImg;
HOperatorSet.ReadImage(out testImg, "test.png");
HTuple resultID;
HOperatorSet.ApplyTextureInspectionModel(testImg, out noveltyRegion, model, out resultID);

HTuple area, row, col;
HOperatorSet.AreaCenter(noveltyRegion, out area, out row, out col);
Console.WriteLine(area.I > 100 ? $"NG: 缺陷面积={area.I}" : "OK");

noveltyRegion.Dispose();
testImg.Dispose();
HOperatorSet.ClearTextureInspectionModel(model);
```

### 模板2: 背光小孔杂光综合检测 ⭐⭐
```csharp
// 完整流程：预处理→分割→清理→特征筛选→判定
HObject image, corrected, enhanced, region, cleaned, connected;
HObject okRegions, ngRegions;

// 预处理(Task02)
HOperatorSet.ReadImage(out image, imagePath);
HOperatorSet.Illuminate(image, out corrected, 51, 51, 0.7);
HOperatorSet.Emphasize(corrected, out enhanced, 7, 7, 2.0);

// 分割(Task09)
HOperatorSet.BinaryThreshold(enhanced, out region, "max_separability", "light", out _);

// 形态学清理(Task08)
HOperatorSet.FillUp(region, out var filled);
HOperatorSet.OpeningCircle(filled, out cleaned, 2.5);
HOperatorSet.Connection(cleaned, out connected);

// 面积过滤
HObject filtered;
HOperatorSet.SelectShape(connected, out filtered, "area", "and", 200, 99999);

// 特征筛选(Task10)
HOperatorSet.SelectShape(filtered, out okRegions,
    new HTuple("circularity", "convexity"), "and",
    new HTuple(0.85, 0.9), new HTuple(1.0, 1.0));
HOperatorSet.SelectShape(filtered, out ngRegions,
    "circularity", "and", 0.0, 0.7);

HTuple ngCount;
HOperatorSet.CountObj(ngRegions, out ngCount);
Console.WriteLine($"检测结果: NG光斑数={ngCount.I}");

// 释放资源
ngRegions.Dispose(); okRegions.Dispose(); filtered.Dispose();
connected.Dispose(); cleaned.Dispose(); filled.Dispose();
region.Dispose(); enhanced.Dispose(); corrected.Dispose(); image.Dispose();
```

### 模板3: 形态学差分缺陷检测
```csharp
HObject image, imgOpening, imgClosing, defects;

HOperatorSet.ReadImage(out image, imagePath);
HOperatorSet.GrayOpeningShape(image, out imgOpening, 7, 7, "octagon");
HOperatorSet.GrayClosingShape(image, out imgClosing, 7, 7, "octagon");
HOperatorSet.DynThreshold(imgOpening, imgClosing, out defects, 75, "not_equal");

HTuple area, row, col;
HOperatorSet.AreaCenter(defects, out area, out row, out col);
Console.WriteLine(area.I > 50 ? $"NG: 缺陷面积={area.I}" : "OK: 无缺陷");

defects.Dispose(); imgClosing.Dispose(); imgOpening.Dispose(); image.Dispose();
```
