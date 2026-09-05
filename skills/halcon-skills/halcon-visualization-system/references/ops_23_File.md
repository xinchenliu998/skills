# HALCON 算子分类详解：File（文件 I/O）

> **分类定位**：HALCON 与本地文件系统的接口，覆盖图像、区域、XLD、元组、模型、字典、序列化数据。
> **算子数量**：约 70 个。
> **HALCON 版本**：26.05.0.0 Progress
> **官方文档**：`toc_file.html`

---

## 1. 概述

File 分类提供**全类型 HALCON 句柄**的本地持久化能力。从简单的图像读写到复杂的深度学习模型、3D 表面模型、序列化对象的存取，本分类覆盖了工业项目几乎所有的"存档/读档"需求。

### 子分类概览

| 子类 | 覆盖句柄 |
|------|----------|
| **Access** | 目录、路径、文件系统操作 |
| **Images** | Image（多通道/单通道/元数据） |
| **Region** | Region（含 XLD 多边形） |
| **XLD** | XLD 轮廓 |
| **Tuple** | Tuple / String |
| **Object** | 通用 Object + 整数-句柄转换 |
| **Misc** | 底层二进制读写（`fread_*` / `fwrite_*`） |
| **Model Files** | 各分类模型文件（`read_*_model` / `write_*_model`） |

---

## 2. 应用场景

| 场景 | 关键算子 |
|------|----------|
| **图像存档（证据图）** | `read_image` + `write_image` |
| **批量图像回放** | `read_sequence` |
| **图像元数据** | `read_image_metadata` + `write_image_metadata` |
| **模板匹配模型存档** | `write_shape_model` + `read_shape_model` |
| **深度学习模型存档** | `write_dl_model` + `read_dl_model` |
| **字典存档** | `read_dict` + `write_dict`（HALCON 通用 KV 存储） |
| **坐标/参数存档** | `read_tuple` + `write_tuple` |
| **目录扫描** | `list_files` |
| **跨域打包** | `serialize_*` + `deserialize_*` |
| **底层二进制** | `open_file` + `fread_*` + `fwrite_*` |

---

## 3. 子分类详解

### 3.1 Access（文件系统操作，10 算子）

- 路径：`get_current_dir` / `set_current_dir`
- 目录：`make_dir` / `remove_dir`
- 文件：`file_exists` / `delete_file` / `copy_file`
- 扫描：`list_files`

### 3.2 Images（图像读写，6 算子）

- `read_image(Image, FileName)` — 支持 BMP/JPEG/PNG/TIFF/EXR/HDR 等
- `write_image(Image, Format, FillColor, FileName)`
- `read_sequence(ImageDir, ImageList, ...)` — 批量读图
- `read_image_metadata` / `write_image_metadata` — EXIF/GPS

### 3.3 Region（区域存档，4 算子）

- `read_region(Region, FileName)` — 读 `*.reg`
- `write_region(Region, FileName)` — 写 `*.reg`
- `read_polygon_xld_*` / `write_polygon_xld_*` — DXF 等多边形格式

### 3.4 XLD（轮廓存档，6 算子）

- `read_contour_xld_dxf` / `write_contour_xld_dxf`
- `read_contour_xld_arc_info` / `write_contour_xld_arc_info`
- `read_polygon_xld_*` / `write_polygon_xld_*`

### 3.5 Tuple（4 算子）

- `read_tuple(Tuple, FileName)` — 读 `*.tup`
- `write_tuple(Tuple, FileName)` — 写 `*.tup`
- `read_string` / `write_string`

### 3.6 Object（3 算子）

- `read_object` / `write_object` — 任意对象
- `serialize_object` / `deserialize_object` — 通用序列化

### 3.7 Misc（底层二进制，10 算子）

- `open_file(FileName, Mode, FileHandle)`
- `close_file(FileHandle)`
- `fread_char/line/string/bytes/serialized_item`
- `fwrite_string/bytes/serialized_item`

### 3.8 Model Files（模型文件，分散在各分类）

每个分类的模型都有自己的 `read_*_model` / `write_*_model`：
- **Matching**：`read_shape_model` / `write_shape_model`
- **OCR**：`read_ocr_class_mlp` / `write_ocr_class_mlp`
- **DL**：`read_dl_model` / `write_dl_model`
- **3D**：`read_surface_model` / `write_surface_model`
- **Metrology**：`read_metrology_model` / `write_metrology_model`
- **Barcode**：`read_bar_code_model` / `write_bar_code_model`
- **Inspection**：`read_variation_model` / `write_texture_inspection_model`
- 等等。

---

## 4. 核心算子详解

### 4.1 图像读写（4 个）

| 算子 | 签名 | 用途 |
|------|------|------|
| `read_image` | `read_image(Image, FileName)` | 读图；FileName 不带格式默认按扩展名 |
| `write_image` | `write_image(Image, Format, FillColor, FileName)` | 写图；Format='bmp'/'jpeg'/'png'/'tiff' |
| `read_sequence` | `read_sequence(DirName, FileName, Start, End, Decimation, Image)` | 批量读图序列 |
| `read_image_metadata` | `read_image_metadata(Metadata, Image)` | 读 EXIF/GPS 信息到字典 |

### 4.2 目录与文件操作（5 个）

| 算子 | 签名 | 用途 |
|------|------|------|
| `list_files` | `list_files(Directory, Options, Files)` | 扫描目录 |
| `file_exists` | `file_exists(FileName, Exists)` | 检查文件存在 |
| `make_dir` | `make_dir(DirectoryPath)` | 建目录 |
| `copy_file` | `copy_file(SourceFile, DestFile)` | 复制 |
| `delete_file` | `delete_file(FileName)` | 删除 |

### 4.3 模型读写（4 个代表）

| 算子 | 用途 |
|------|------|
| `read_shape_model` | 读 `*.shm` 形状模型 |
| `write_shape_model` | 写 `*.shm` |
| `read_dl_model` | 读 `*.hdl` DL 模型 |
| `write_dl_model` | 写 `*.hdl` |

### 4.4 序列化（跨域打包）

| 算子 | 用途 |
|------|------|
| `serialize_image` | 图像 → `SerializedItemHandle` |
| `serialize_tuple` | 元组 → 序列化项 |
| `serialize_shape_model` | 模型 → 序列化项 |
| `deserialize_*` | 反序列化（对应每种类型） |

### 4.5 字典（HDict）

| 算子 | 用途 |
|------|------|
| `read_dict` | 读 `*.hdict` 字典文件 |
| `write_dict` | 写 `*.hdict` |
| `create_dict` | 新建空字典 |

---

## 5. HDevelop 示例代码

### 示例 1：批量图像读取与存档

```hdevelop
* 1. 列出目录下所有 PNG
list_files('images/', 'files', Files)
tuple_regexp_select(Files, '\\.png$', PngFiles)

* 2. 循环处理并另存为 TIFF
for i := 0 to |PngFiles| - 1 by 1
    read_image(Image, PngFiles[i])
    
    * 处理（示例：高斯滤波）
    gauss_filter(Image, Smoothed, 3.0)
    
    * 存为高质量 TIFF
    OutName := 'processed/' + i$'04.tiff'
    write_image(Smoothed, 'tiff', 0, OutName)
endfor

dev_disp_text('处理完成，共 ' + |PngFiles| + ' 张', 'window', 'top', 'left', 'green', [], [])
```

### 示例 2：模板匹配模型的存档与读取

```hdevelop
* 训练
read_image(TrainImg, 'template.png')
reduce_domain(TrainImg, RegionOfInterest, ModelDomain)
create_shape_model(ModelDomain, 'auto', rad(-10), rad(20), 'auto', \
                   'none', 'use_polarity', 30, 10, ModelID)

* 存档
write_shape_model(ModelID, 'model.shm')
clear_shape_model(ModelID)

* 读回（程序重启后）
read_shape_model('model.shm', ModelID2)
find_shape_model(QueryImg, ModelID2, rad(-10), rad(20), 0.7, \
                 1, 0.5, 'least_squares', 0, 0.8, Row, Col, Angle, Score)
```

### 示例 3：字典存档 + 元数据

```hdevelop
* 创建字典存结果
create_dict(ResultDict)
set_dict_tuple(ResultDict, 'timestamp', '2026-08-01 14:30:00')
set_dict_tuple(ResultDict, 'mean_diameter', 12.345)
set_dict_tuple(ResultDict, 'defect_count', 5)

* 写入磁盘
write_dict(ResultDict, 'result_001.hdict', [], [])

* 读回
read_dict('result_001.hdict', [], [], LoadedDict)
get_dict_tuple(LoadedDict, 'mean_diameter', MeanD)
get_dict_tuple(LoadedDict, 'defect_count', NDefects)
```

### 示例 4：底层二进制文件（自定义格式）

```hdevelop
* 写入二进制
open_file('data.bin', 'output_binary', FileID)
NumArray := [1.23, 4.56, 7.89, 10.11]
fwrite_bytes(FileID, NumArray)
close_file(FileID)

* 读取
open_file('data.bin', 'input_binary', FileID2)
fread_bytes(FileID2, 4, ReadArray)
close_file(FileID2)

* 验证
tuple_sum(NumArray, SumOrig)
tuple_sum(ReadArray, SumRead)
```

---

## 6. 典型工业流水线

### 流水线 A：模型训练-部署-推理

```
[训练环境]                              [生产环境]
read_image(TrainImg)                    
        ↓                               
create_shape_model(...)                 
        ↓                               
write_shape_model('model.shm') ──→→→→→  read_shape_model('model.shm')
                                       ↓
                                  find_shape_model(...)
```

### 流水线 B：证据图 + 元数据存档

```
read_image(SrcImg)
        ↓
threshold / measurement (业务逻辑)
        ↓
write_image(ResultImg, 'jpeg', 0, 'evidence/case_001.jpg')
        ↓
set_dict_tuple(MetaDict, 'case_id', 'C001')
set_dict_tuple(MetaDict, 'inspector', 'AI')
write_dict(MetaDict, 'evidence/case_001.hdict', [], [])
```

---

## 7. 常见陷阱与最佳实践

1. **路径分隔符**：Windows 写 `'C:\\Work\\img.png'` 或用 `'/'`（HALCON 自动转换）。
2. **图像格式不支持**：HALCON 默认支持 BMP/JPEG/PNG/TIFF；EXR/HDR 需 progressive 版。
3. **`write_image` 的 FillColor**：对 alpha 通道或多通道图像，FillColor 是背景填充色。
4. **`read_sequence` 自动排序**：按文件名数字顺序读，需保证零填充（`001, 002, ...`）。
5. **模型文件版本兼容**：`*.shm` / `*.hdl` 等**跨 HALCON 版本**可能不兼容——升级时需重新训练。
6. **`read_object` vs `read_image`**：`read_object` 读 HALCON 通用 `.obj` 文件，可读图像/区域/XLD。
7. **大文件读取性能**：用 `set_check('~input')` 跳过签名检查可加速（不推荐生产环境）。
8. **路径含中文**：HALCON 内部 UTF-8，需要系统语言与编码一致。

---

## 8. 参数调优指南

| 场景 | 建议 |
|------|------|
| 批量读图慢 | 用 `read_sequence` 一次性读序列，比循环 `read_image` 快 |
| 证据图质量 | 用 `'tiff'` 或 `'bmp'` 无损格式；JPEG 仅作展示 |
| 模型兼容性 | 训练用与推理用同一 HALCON 版本；或用 `serialize_*` 跨域传递 |
| 大二进制读写 | `fread_bytes` / `fwrite_bytes` 比 `read_tuple` / `write_tuple` 快 |
| 文件不存在 | `file_exists` 先判再读，避免异常 |

---

## 9. 相关分类

- **System / OS**：`make_dir`、`list_files` 等与 OS 算子重叠。
- **Tuple**：序列化用 `serialize_tuple`。
- **Matching**：模型文件 `read_*_model` / `write_*_model`。
- **Deep Learning**：`read_dl_model` / `write_dl_model`。

---

## 10. 学习小结

File 分类是"所有项目必经存档层"。**学习优先级**：
1. **必学**：`read_image` / `write_image`、`list_files`、`read_tuple` / `write_tuple`。
2. **重要**：`read_*_model` / `write_*_model`（模型存档）、`read_dict` / `write_dict`（字典存档）。
3. **进阶**：`read_sequence`（批量读图）、`read_image_metadata`（EXIF）、底层 `fread_*` / `fwrite_*`。

**核心要点**：
- HALCON 模型文件**版本敏感**——同一模型文件跨版本可能不兼容，建议用 `serialize_*` 传递。
- `read_sequence` 适合按编号批量读图，自动按数字排序。
- 字典（HDict）是 HALCON 通用 KV 存储，可存任意类型——是 DL 项目配置的事实标准。

> **后续阅读**：详见 `C:\Program Files\MVTec\HALCON-26.05-Progress\doc\html\reference\operators\toc_file.html`。