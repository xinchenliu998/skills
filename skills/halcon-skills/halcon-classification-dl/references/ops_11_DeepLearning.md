# HALCON 算子分类详解：Deep Learning（深度学习）

> **分类**：Deep Learning / Deep Neural Networks
> **子类数**：10 个（Anomaly Detection、Classification、Continual Learning、Framework、Instance Segmentation、Model、Multi-label、Object Detection、Semantic Segmentation、Data Augmentation）
> **学习优先级**：⭐⭐⭐⭐⭐（⭐ 入门 / ⭐⭐⭐⭐⭐ 必精）
> **典型应用场景**：工业缺陷检测、目标定位与分割、字符识别（端到端）、异常检测、半导体 AOI、电池极片质检、汽车冲压件检测。

---

## 1. 概述

Deep Learning（深度学习）是 HALCON 26 中的**核心热点方向**，约含 **90 个算子**，覆盖工业深度学习全流程：**数据准备 → 模型训练 → 推理部署 → 持续学习**。

HALCON 深度学习的工程特色：

- **5 大网络类型一站式覆盖**：
  - `anomaly_detection`（异常检测）
  - `classification`（图像分类）
  - `detection`（目标检测）
  - `segmentation`（语义分割）
  - `instance_segmentation`（实例分割）
  - `multilabel_classification`（多标签分类）
- **完善的训练工具链**：MVTec Deep Learning Tool（图形化）生成 `*.dict` 数据。
- **硬件自适应**：自动支持 CPU / GPU（`query_available_compute_devices`、`init_compute_device`）。
- **训练优化**：模型量化（`optimize_dl_model_for_inference`）、数据增强（`create_dl_transform_pipeline`）。
- **持续学习**：`init_dl_continual_learning` / `extend_dl_continual_learning` 部署期增量。
- **手写组网**：`create_dl_layer_*` 全套算子可自定义网络结构。

> **HALCON 26 Progress 的新特性**：增强的 Continual Learning（灾难性遗忘防护）、新预训练模型（`last_resnet50.hdl`）、更高效的 `optimize_dl_model_for_inference`。

---

## 2. 应用场景

1. **3C 电子**：PCB AOI（元件缺失/错焊/划伤）、屏幕 Mura 缺陷、芯片激光刻字识别。
2. **汽车与新能源**：冲压件表面缺陷、涂装瑕疵、焊点质量、电池顶盖/极片检测。
3. **半导体**：晶圆颗粒、Mask 缺陷、IC 芯片外观、引脚缺陷。
4. **医药与食品**：药片缺粒/破裂、胶囊色差、包装密封检测、瓶身喷码。
5. **物流与零售**：快递包裹计数、SKU 识别、商品分拣。

---

## 3. 子分类详解

| 子分类 | 核心算子 | 典型用途 |
|--------|----------|----------|
| **Anomaly Detection** | `read_dl_model`（异常）, `apply_dl_model`（异常）, `get_dl_model_param` | 异常检测（仅用 OK 样本训练） |
| **Classification** | `train_dl_model_batch`, `apply_dl_model`, `read/write_dl_model` | 图像分类 |
| **Object Detection** | `create_dl_model_detection`, `train_dl_model_batch`, `apply_dl_model`, `set_dl_model_param` | 目标检测（YOLO / Faster R-CNN） |
| **Semantic Segmentation** | `train_dl_model_batch`, `apply_dl_model`, `transform_dl_sample_batch` | 语义分割（U-Net / DeepLabV3+） |
| **Instance Segmentation** | `train_dl_model_batch`, `apply_dl_model` | 实例分割（Mask R-CNN） |
| **Multi-label Classification** | 同 Classification，标签多任务 | 多标签分类 |
| **Model** | `create_dl_model_detection`, `set_dl_model_param`, `get_dl_model_param`, `optimize_dl_model_for_inference`, `serialize_dl_model` | 模型管理与参数 |
| **Framework** | `query_available_dl_devices`, `init_compute_device`, `activate_compute_device`, `create_dl_layer_*`, `load_dl_model_weights` | 框架（设备、网络层） |
| **Continual Learning** | `init_dl_continual_learning`, `extend_dl_continual_learning`, `set_dl_model_param` | 增量学习 |
| **Data Augmentation** | `create_dl_transform_pipeline`, `create_dl_transform_*`, `read/write_dl_transform_pipeline` | 数据增强 |

**5 大网络类型对比**：

| 类型 | 训练样本量 | 推理速度 | 输出 | 典型应用 |
|------|------|------|------|----------|
| **anomaly_detection** | OK≥100 | 极快 | OK/NG + 异常热图 + 分数 | 缺陷检测 |
| **classification** | 每类 ≥ 100 | 快 | N 类概率 | 等级分选 |
| **detection** | 每类 ≥ 50 | 中 | bbox + 类别 + 置信度 | 目标定位 |
| **segmentation** | 每类 ≥ 50 | 慢 | 像素级 mask | 缺陷分割 |
| **instance_segmentation** | 每类 ≥ 100 | 慢 | pixel + instance ID | 物体计数 |

---

## 4. 核心算子详解

### 4.1 模型创建与训练

| 算子 | 作用 |
|------|------|
| `read_dl_model(FileName, DLModelHandle)` | 加载预训练模型（`.hdl`） |
| `create_dl_model_detection(NumClasses, DLModelDetectionParam)` | 创建检测模型（自定义架构） |
| `set_dl_model_param(DLModelHandle, GenParamName, GenParamValue)` | 设置参数（超参） |
| `get_dl_model_param(DLModelHandle, GenParamName)` | 取参数 |
| `train_dl_model_batch(DLDataset, DLModelHandle, TrainResults, TrainTimeout, TrainParam)` | 训练 |
| `apply_dl_model(Image, DLModelHandle, DLResultHandle)` | 推理 |
| `write_dl_model(DLModelHandle, FileName)` | 持久化 |

### 4.2 数据增强

| 算子 | 作用 |
|------|------|
| `create_dl_transform_pipeline(GenParamNames, GenParamValues, DLTransformPipelineHandle)` | 创建增强 pipeline |
| `create_dl_transform_random_crop` / `random_hsv` / `random_geometric` | 随机裁剪/HSV/几何 |
| `create_dl_transform_flip` / `resize` / `blur` / `normalize` | 翻转/缩放/模糊/归一化 |
| `read_dl_transform_pipeline` / `write_dl_transform_pipeline` | 持久化 |

### 4.3 设备管理（GPU / CPU）

| 算子 | 作用 |
|------|------|
| `query_available_compute_devices(GenParamName, DeviceIDs)` | 枚举可用设备 |
| `init_compute_device(DeviceHandle, GenParamName, GenParamValue)` | 初始化设备 |
| `activate_compute_device(DeviceHandle)` / `deactivate_compute_device` | 激活/关闭 |
| `get_compute_device_info` / `set_compute_device_param` / `get_compute_device_param` | 设备参数管理 |
| `open_compute_device` / `release_compute_device` | 生命周期 |

### 4.4 推理优化

| 算子 | 作用 |
|------|------|
| `optimize_dl_model_for_inference(DLModelHandle, OptimizationMethod)` | 量化加速（OpenVINO / TensorRT / pure GPU） |
| `set_dl_model_param(DLModelHandle, 'batch_size', N)` | 批推理 |
| `set_dl_model_param(DLModelHandle, 'runtime', 'gpu')` | 设备切换 |

### 4.5 持续学习（Continual Learning）

| 算子 | 作用 |
|------|------|
| `init_dl_continual_learning(DLModelHandle, ContinualLearningHandle)` | 初始化增量学习 |
| `extend_dl_continual_learning(ContinualLearningHandle, DLDataset)` | 用新数据扩展 |
| `set_dl_continual_learning_param(ContinualLearningHandle, GenParamName, GenParamValue)` | `'rehearsal_ratio'` 等 |

### 4.6 结果解析

| 算子 | 作用 |
|------|------|
| `get_dict_object(Object, DictHandle, Key)` | 从字典取 Region/XLD |
| `get_dict_tuple(Tuple, DictHandle, Key)` | 从字典取 Tuple |
| `get_dict_param(DictHandle, GenParamName)` | 查字典元信息 |
| `serialize_dl_model_results` | 序列化结果 |

### 4.7 网络层（手写组网）

| 算子 | 作用 |
|------|------|
| `create_dl_layer_input` / `create_dl_layer_convolution` / `create_dl_layer_pooling` | 输入/卷积/池化层 |
| `create_dl_layer_batch_norm` / `create_dl_layer_activation` | BN / 激活层 |
| `create_dl_layer_fully_connected` / `create_dl_layer_loss_*` | 全连 / 损失层 |
| `get_dl_model_layer*` | 取层结构 |

---

## 5. HDevelop 示例代码

### 5.1 示例一：异常检测完整训练 + 推理

```hdevelop
* ============================================================
* 异常检测：仅用 OK 图像训练，推理时输出异常分数
* 场景：金属零件表面缺陷检测
* ============================================================
dev_update_off ()
dev_close_window ()

* --- 1. 准备数据集（MVTec Deep Learning Tool 生成） ---
read_dict ('metal_part_dataset.dict', [], [], DLDataset)

* --- 2. 加载预训练模型 ---
read_dl_model ('last_anomaly_detection.hdl', DLModelHandle)

* --- 3. 设置训练参数 ---
set_dl_model_param (DLModelHandle, 'batch_size', 4)
set_dl_model_param (DLModelHandle, 'learning_rate', 0.001)
set_dl_model_param (DLModelHandle, 'num_epochs', 30)
set_dl_model_param (DLModelHandle, 'image_width', 256)
set_dl_model_param (DLModelHandle, 'image_height', 256)

* --- 4. 切换 GPU（失败回退 CPU） ---
try
    query_available_compute_devices ('runtime', DeviceIDs)
    for i := 0 to |DeviceIDs| - 1 by 1
        if (DeviceIDs[i] == 'gpu')
            init_compute_device ('gpu', DeviceHandle)
            activate_compute_device (DeviceHandle)
            set_dl_model_param (DLModelHandle, 'runtime', 'gpu')
            break
        endif
    endfor
catch (Exception)
    set_dl_model_param (DLModelHandle, 'runtime', 'cpu')
endtry

* --- 5. 训练 + 保存 ---
create_dict (TrainParam)
set_dict_tuple (TrainParam, 'display', 'iter')
train_dl_model_batch (DLDataset, DLModelHandle, TrainResults, [], TrainParam)
write_dl_model (DLModelHandle, 'metal_anomaly_model.hdl')

* --- 6. 推理 ---
read_image (TestImage, 'metal_part_test_01')
get_image_size (TestImage, W, H)
dev_open_window (0, 0, W, H, 'black', WindowHandle)
dev_display (TestImage)
apply_dl_model (TestImage, DLModelHandle, DLResultHandle)
get_dict_tuple (DLResultHandle, 'anomaly_score', AnomalyScore)
get_dict_object (AnomalyImage, DLResultHandle, 'anomaly_image')

if (AnomalyScore > 0.5)
    dev_set_color ('red')
    dev_display (AnomalyImage)
    disp_message (WindowHandle, 'NG! Score: ' + AnomalyScore, 'window', 10, 10, 'red', 'true')
else
    disp_message (WindowHandle, 'OK! Score: ' + AnomalyScore, 'window', 10, 10, 'green', 'true')
endif
```

### 5.2 示例二：目标检测（PCB元件）

```hdevelop
* ============================================================
* 目标检测：PCB 元件（电阻/电容/IC）
* ============================================================
dev_update_off ()
read_dict ('pcb_components_dataset.dict', [], [], DLDataset)

* --- 加载预训练模型 ---
read_dl_model ('last_rcnn.hdl', DLModelHandle)

* --- 设置参数 ---
set_dl_model_param (DLModelHandle, 'class_ids', [0, 1, 2])
set_dl_model_param (DLModelHandle, 'class_names', ['resistor', 'capacitor', 'ic'])
set_dl_model_param (DLModelHandle, 'batch_size', 8)
set_dl_model_param (DLModelHandle, 'learning_rate', 0.0001)
set_dl_model_param (DLModelHandle, 'num_epochs', 50)
set_dl_model_param (DLModelHandle, 'image_width', 640)
set_dl_model_param (DLModelHandle, 'image_height', 640)
set_dl_model_param (DLModelHandle, 'min_confidence', 0.7)
set_dl_model_param (DLModelHandle, 'max_overlap', 0.5)

* --- 数据增强 pipeline ---
create_dl_transform_pipeline ([], [], PipelineHandle)
create_dl_transform_random_crop (['mode', 'percentage'], ['scale', 0.9], T1)
create_dl_transform_random_hsv (['saturation', 'brightness'], [0.1, 0.1], T2)
create_dl_transform_random_geometric (['rotation', 'scaling'], [0.1, 0.1], T3)
create_dl_transform_flip (['direction'], ['horizontal'], T4)
set_dl_transform_pipeline_param (PipelineHandle, 'transforms', [T1, T2, T3, T4])
set_dl_model_param (DLModelHandle, 'transform_pipeline', PipelineHandle)

* --- 训练 ---
train_dl_model_batch (DLDataset, DLModelHandle, TrainResults, [], ['display','iter'])
write_dl_model (DLModelHandle, 'pcb_detector.hdl')

* --- 推理 ---
read_image (TestImage, 'pcb_board_01')
get_image_size (TestImage, W, H)
dev_open_window (0, 0, W, H, 'black', WindowHandle)
dev_display (TestImage)
apply_dl_model (TestImage, DLModelHandle, DLResultHandle)
get_dict_tuple (DLResultHandle, 'bbox_row', BBoxRows)
get_dict_tuple (DLResultHandle, 'bbox_col', BBoxCols)
get_dict_tuple (DLResultHandle, 'bbox_length1', BBoxL1)
get_dict_tuple (DLResultHandle, 'bbox_length2', BBoxL2)
get_dict_tuple (DLResultHandle, 'bbox_phi', BBoxPhi)
get_dict_tuple (DLResultHandle, 'bbox_class_id', ClassIDs)
get_dict_tuple (DLResultHandle, 'bbox_confidence', Confidences)

dev_set_color ('red')
for i := 0 to |BBoxRows| - 1 by 1
    gen_rectangle2 (Rect, BBoxRows[i], BBoxCols[i], BBoxPhi[i], BBoxL1[i], BBoxL2[i])
    dev_display (Rect)
endfor

* --- 优化部署 ---
optimize_dl_model_for_inference (DLModelHandle, 'tensorrt')
write_dl_model (DLModelHandle, 'pcb_detector_optimized.hdl')
```

### 5.3 示例三：完整训练工作流（数据 → 训练 → 部署）

```hdevelop
* ============================================================
* 端到端深度学习：自定义数据集 + 训练 + 优化 + 部署
* ============================================================
dev_update_off ()
dev_close_window ()

* === 阶段 1：加载数据字典 ===
read_dict ('my_defect_dataset.dict', [], [], DLDataset)

* === 阶段 2：加载预训练模型（ResNet50 backbone） ===
read_dl_model ('pretrained_resnet50_classification.hdl', DLModelHandle)

* === 阶段 3：换 head（适配 2 类） ===
set_dl_model_param (DLModelHandle, 'class_ids', [0, 1])
set_dl_model_param (DLModelHandle, 'class_names', ['good', 'bad'])
set_dl_model_param (DLModelHandle, 'image_width', 224)
set_dl_model_param (DLModelHandle, 'image_height', 224)

* === 阶段 4：训练超参 ===
set_dl_model_param (DLModelHandle, 'batch_size', 16)
set_dl_model_param (DLModelHandle, 'learning_rate', 0.0001)
set_dl_model_param (DLModelHandle, 'num_epochs', 100)
set_dl_model_param (DLModelHandle, 'optimizer', 'adam')
set_dl_model_param (DLModelHandle, 'regularization', 0.0001)
set_dl_model_param (DLModelHandle, 'class_weights', [1.0, 3.0])

* === 阶段 5：设备切换到 GPU ===
query_available_compute_devices ('runtime', DeviceList)
for i := 0 to |DeviceList| - 1 by 1
    if (DeviceList[i] == 'gpu')
        init_compute_device ('gpu', DeviceHandle)
        activate_compute_device (DeviceHandle)
        set_dl_model_param (DLModelHandle, 'runtime', 'gpu')
        break
    endif
endfor

* === 阶段 6：训练（带超时） ===
create_dict (TrainParam)
set_dict_tuple (TrainParam, 'display', 'iter')
set_dict_tuple (TrainParam, 'save_best', 'true')
train_dl_model_batch (DLDataset, DLModelHandle, TrainResults, 7200, TrainParam)

* === 阶段 7：保存与优化 ===
write_dl_model (DLModelHandle, 'defect_classifier.hdl')
optimize_dl_model_for_inference (DLModelHandle, 'pure_gpu')
write_dl_model (DLModelHandle, 'defect_classifier_optimized.hdl')

* === 阶段 8：推理验证 ===
read_image (TestImage, 'test_samples/case_001.png')
get_image_size (TestImage, W, H)
dev_open_window (0, 0, W, H, 'black', WindowHandle)
dev_display (TestImage)
apply_dl_model (TestImage, DLModelHandle, DLResultHandle)
get_dict_tuple (DLResultHandle, 'classification', ClassID)
get_dict_tuple (DLResultHandle, 'confidence', Confidence)
ClassNames := ['good', 'bad']
Color := if(ClassID == 1, 'red', 'green')
disp_message (WindowHandle, ClassNames[ClassID] + ' (' + Confidence{0:4} + ')', \
              'window', 10, 10, Color, 'true')
```

### 5.4 示例四：持续学习（增量训练）

```hdevelop
* ============================================================
* 持续学习：已部署模型新增缺陷类型
* ============================================================
read_dl_model ('defect_classifier_v1.hdl', DLModelHandle)

* --- 初始化持续学习（防止灾难性遗忘） ---
init_dl_continual_learning (DLModelHandle, ContinualLearningHandle)
set_dl_continual_learning_param (ContinualLearningHandle, 'rehearsal_ratio', 0.2)
set_dl_continual_learning_param (ContinualLearningHandle, 'learning_rate', 0.0001)

* --- 加载新数据集 + 扩展学习 ---
read_dict ('dataset_v2_with_new_classes.dict', [], [], NewDataset)
extend_dl_continual_learning (ContinualLearningHandle, NewDataset)
* 模型现在能识别：原来 2 类 + 新增 3 类

write_dl_model (DLModelHandle, 'defect_classifier_v2.hdl')
```

---

## 6. 典型工业流水线

### 6.1 异常检测（缺陷检测，无监督）

```
1. 采集 OK 样本 ≥ 100 张
2. MVTec Deep Learning Tool 标注 → 生成 .dict
3. read_dl_model('last_anomaly_detection.hdl')
4. set_dl_model_param (image_width=256, image_height=256)
5. train_dl_model_batch (数据集, 模型, ...)
6. 推理：apply_dl_model → anomaly_score + anomaly_image
7. 阈值 0.5 → OK / NG
8. optimize_dl_model_for_inference → 部署
```

### 6.2 目标检测（缺陷定位）

```
1. 标注工具生成 bbox 标签
2. 训练 Faster R-CNN / YOLO
3. 推理：apply_dl_model → bbox_row, bbox_col, bbox_length1, bbox_length2, bbox_phi
4. 可视化：gen_rectangle2 + dev_display
5. 后处理：NMS（max_overlap 参数）
6. 优化部署 → 生产环境
```

### 6.3 语义分割（像素级缺陷）

```
1. 标注工具按像素类别标注
2. 训练 U-Net / DeepLabV3+
3. 推理：apply_dl_model → segmentation_image
4. threshold 各类 → 区域提取
5. area_center → 缺陷尺寸判定
```

### 6.4 持续学习（部署期增量）

```
1. 部署 v1 模型（含类别 A、B）
2. 现场出现新类别 C
3. 收集 C 的训练样本（50+）
4. init_dl_continual_learning（保留 A、B 知识）
5. extend_dl_continual_learning（新增 C）
6. 验证 A、B、C 全部识别
7. write_dl_model → v2 部署
```

---

## 7. 常见陷阱与最佳实践

## 7. 常见陷阱与最佳实践

### 7.1 训练样本数量

| 任务 | 最小样本量 | 推荐样本量 |
|------|------|------|
| 异常检测 | 100 OK | 200+ OK |
| 分类 | 100/类 | 500+/类 |
| 检测 | 50/类 | 200+/类 |
| 语义分割 | 50/类 | 200+/类 |
| 实例分割 | 100/类 | 300+/类 |

- **样本不均衡**：用 `set_dl_model_param('class_weights', [w1, w2, ...])` 调整。
- **样本过少**：用数据增强（`create_dl_transform_pipeline`）扩充。

### 7.2 训练 / 推理一致性

- **图像尺寸**：训练和推理必须一致（`image_width/image_height`）。
- **数据归一化**：训练时和推理时必须使用同一种 transformation。
- **类别 ID 顺序**：`class_ids` 顺序需与训练数据严格一致。

### 7.3 GPU 内存管理

- **GPU OOM** → 减小 `batch_size` 或 `image_width/height`。
- **多卡情况**：用 `query_available_compute_devices` 枚举。
- **CPU 备用**：GPU 故障时务必写 `try-catch` 切回 CPU。

### 7.4 模型选择

- **ResNet50 backbone**：通用，imagenet 预训练。
- **MobileNet**：轻量，嵌入式部署。
- **EfficientNet**：性价比最优。
- **HALCON 26 自带**：`last_resnet50.hdl`、`last_*.hdl` 系列。

### 7.5 推理优化

- **优化前**：先测 baseline 速度。
- **优化后**：注意精度损失（`optimize_dl_model_for_inference` 可能掉 0.5–1%）。
- **批推理**：`batch_size` 越大 GPU 越饱和，但延时变高。
- **多线程**：推理可在多线程中并行。

### 7.6 持续学习

- **灾难性遗忘**：必须用 `init_dl_continual_learning` 而非直接 retrain。
- **rehearsal_ratio**：典型 0.1–0.3（旧类别样本比例）。
- **新类别 ≠ 旧类别**：增加 ID 即可，原分类 head 自动扩展。

### 7.7 部署注意

- **版本兼容性**：训练和部署用同一 HALCON 版本。
- **加密需求**：`write_dl_model(pwd, ...)` 加密防止反编译。
- **数据预加载**：用 `create_dl_preprocess_from_dict` 预加载图像到 RAM。

---

## 8. 参数调优指南

### 8.1 训练参数

| 参数 | 推荐值 | 说明 |
|------|--------|------|
| `batch_size` | 8–64 | GPU 显存决定，越大越稳 |
| `learning_rate` | 0.001–0.0001 | Adam 优化器 |
| `num_epochs` | 30–100 | 早停依数据量 |
| `optimizer` | `'adam'` | `'sgd'` / `'adam'` / `'adamw'` |
| `class_weights` | `[w1, w2, ...]` | 应对方差不均衡 |
| `image_width/height` | 256 / 512 | 显存有限时 256 |

### 8.2 推理参数

| 参数 | 推荐值 | 说明 |
|------|--------|------|
| `min_confidence` | 0.5–0.7 | 检测阈值 |
| `max_overlap` | 0.5 | NMS 阈值 |
| `batch_size` | 1 / 8 / 16 | 实时性 vs 吞吐 |
| `runtime` | `'gpu'` | 显存不足时 `'cpu'` |

### 8.3 数据增强参数

| 算子 | 参数 | 推荐值 |
|------|------|--------|
| `random_crop` | `percentage` | 0.8–1.0 |
| `random_hsv` | `saturation, brightness` | 0.1 |
| `random_geometric` | `rotation, scaling` | 0.1, 0.1 |
| `flip` | `direction` | `'horizontal'` |
| `blur` | `sigma` | 0.5–1.0 |

### 8.4 优化方法

| 方法 | 适用 | 加速比 |
|------|------|--------|
| `'pure_gpu'` | 单 GPU 部署 | 1.5–2x |
| `'tensorrt'` | NVIDIA GPU | 2–5x |
| `'openvino'` | Intel CPU/GPU | 2–3x |
| `'onnx'` | 跨平台 | 1.5–2x |

### 8.5 持续学习参数

| 参数 | 推荐值 | 说明 |
|------|--------|------|
| `rehearsal_ratio` | 0.1–0.3 | 旧类别样本比例 |
| `learning_rate` | 0.0001 | 增量训练，越小越稳 |
| `epochs` | 20–30 | 增量训练 |

---

## 9. 相关分类

- **Classification（经典分类）**：样本量 < 5000 时优先用 ML 分类器。
- **OCR（光学字符识别）**：Deep OCR 是 Deep Learning 在 OCR 上的特化。
- **Matching（模板匹配）**：用 `find_shape_model` 先定位，再 `apply_dl_model` 识别。
- **Identification（识别）**：条码 / 二维码走专用识别，不走 DL。
- **Image（图像）**：图像读取、预处理为 DL 服务的最前端。
- **System（系统）**：GPU / CPU 设备管理（`init_compute_device`）的底层。

---

## 10. 学习小结

Deep Learning 是 HALCON 26 中**最核心、最活跃**的家族。它不仅提供了 5 种主流网络类型，更围绕"**数据 → 训练 → 部署 → 增量**"的完整工业闭环，构建了从 MVTec Deep Learning Tool 图形化工具到 HALCON 26 Progress 持续学习的完整链路。

**学习路线建议**：

1. **第 1 周**：理解 5 大网络类型差异，跑通异常检测（最简单的无监督任务）。
2. **第 2 周**：分类任务，掌握 `train_dl_model_batch` + `apply_dl_model` 完整流程。
3. **第 3 周**：目标检测，Faster R-CNN / YOLO 训练与推理。
4. **第 4 周**：语义分割，U-Net + 像素级 mask 后处理。
5. **第 5 周**：数据增强 pipeline，GPU 性能调优。
6. **第 6 周**：持续学习（增量部署），灾难性遗忘防护。
7. **第 7 周**：手写组网（`create_dl_layer_*`），自定义架构。
8. **第 8 周**：模型优化（`optimize_dl_model_for_inference`），部署到产线。

**关键能力**：

- **网络类型选择**：依任务复杂度、样本量、推理速度选择。
- **数据增强**：提高泛化能力。
- **GPU/CPU 切换**：跨平台部署能力。
- **优化部署**：从研究模型到工业可用的最后一公里。
- **持续学习**：模型全生命周期管理。

**HALCON 26 Progress 新特性**：

- 增强的 `optimize_dl_model_for_inference`（更多 backend 支持）。
- `init_dl_continual_learning` + `extend_dl_continual_learning` 的灾难性遗忘防护。
- 新的预训练 backbone（`last_efficientnet_b3.hdl`）。
- 改进的 `get_dl_model_param` 接口。

**一句话总结**：深度学习是工业视觉的"现代利器"。HALCON 把 5 大网络 + 完整数据增强 + 持续学习 + 推理优化打包成了一套"工业级 AI 工厂"——用好它，从 0 到 1 的 AI 视觉应用就能打通。
