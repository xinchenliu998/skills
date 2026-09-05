# HALCON 算子分类详解：Image（图像核心）

> **分类**：Image 图像核心
> **子类数**：10 个（Access、Acquisition、Channel、Creation、Domain、Features、Format、Manipulation、Type conversion、Image Source）
> **算子数**：约 140 个
> **学习优先级**：⭐⭐⭐⭐⭐（所有项目的"自来水"，必学）
> **典型应用场景**：相机采集、文件读写、ROI 设定、通道分解、灰度/类型转换、图像生成与存档——构成任何视觉流水线最前端的"进水口"和最后端的"出水口"。

---

## 1. 概述

**Image 分类在 HALCON 体系中的定位**

Image 分类是 HALCON 算子体系的基础设施层。它位于"硬件/物理世界"和"算法层"之间，承担四大核心职能：

1. **数据入口**：通过 `grab_image`/`read_image` 把物理光信号转为 `HImage` 对象。
2. **数据整形**：通过 `reduce_domain`/`crop_domain`/`change_domain` 限定 ROI，通过 `decompose3`/`compose3`/`trans_from_rgb` 控制通道布局，通过 `convert_image_type`/`rgb1_to_gray` 控制像素类型。
3. **数据查询**：通过 `get_image_size`/`get_image_pointer1`/`get_image_type`/`min_max_gray` 等算子把图像的关键属性提取为元组，便于后续算法调度。
4. **数据出口**：通过 `write_image`/`dump_window_image` 存档，通过 `tile_images` 拼图供 HMI 浏览。

**与其他分类的关系**

- 与 **Filters**：Image 提供"原材料"，Filters 提供"加工"。
- 与 **Regions**：Image 通过 `threshold`/`dyn_threshold` 过渡到 Region；Region 又通过 `region_to_bin`/`region_to_label` 回到 Image。
- 与 **Graphics**：Image 通过 `disp_image` 显示，由 Graphics 控制显示风格。
- 与 **XLD**：通过 `region_to_bin`/`gen_image_const` 转换。
- 与 **File**：Image 的 `read_image`/`write_image` 是 File 分类在图像层面的具体实现。

**为什么必须精通 Image**

几乎所有 HALCON 项目的"Hello World" 都需要：`read_image → get_image_size → reduce_domain → dev_display`。没有 Image 分类的扎实基础，Filters/Regions/Segmentation 等下游分类都是空中楼阁。

---

## 2. 应用场景

### 场景 A：手机壳体 PCB 在线检测
- **行业**：3C 电子
- **问题**：手机壳体上 6 颗螺丝孔需要逐个测量，每个 ROI 都需要独立的图像子集。
- **算法选择**：相机抓全图 → `reduce_domain` 把每个螺丝孔限定到独立 ROI → 内部二值化 → 测量。
- **期望产出**：6 个孔的位置、圆度、像素直径，判定 OK/NG 后写日志。

### 场景 B：彩色印刷品色差检测
- **行业**：印刷包装
- **问题**：客户要求对比 L*a*b* 色彩空间的 ΔE，而非 RGB 距离。
- **算法选择**：`trans_from_rgb(Image, ImageL, ImageA, ImageB, 'cielab')` 把 RGB 拆为 L/a/b 三通道 → 计算两图 ΔE。
- **期望产出**：每个像素的色差热图，按 ΔE > 3 判定 NG。

### 场景 C：多相机异步采集
- **行业**：汽车整车厂
- **问题**：4 个相机同步触发，但图像大小不同（左侧全局 + 右侧局部）。
- **算法选择**：4 路 `open_framegrabber` + `grab_image_async` 异步拉取 → 通过 `get_image_size` 适配不同 ROI。
- **期望产出**：4 路图像拼接为整车俯视图。

### 场景 D：医疗显微 Bayer 相机
- **行业**：医学影像
- **问题**：RAW Bayer 格式需还原为 RGB。
- **算法选择**：`cfa_to_rgb(ImageBayer, ImageRGB, 'bilinear')` 或 `'hamilton'` 高质量插值。
- **期望产出**：标准 RGB 彩色图像，进入下游细胞分割。

### 场景 E：流水图像批量回放
- **行业**：质量复检/数据回放
- **问题**：硬盘有 10 万张历史图像需要按 OK/NG 回放归档。
- **算法选择**：`list_files` + `read_image` 批量 + `tile_images_offset` 拼图 + `write_image` 二次存档。
- **期望产出**：N×M 网格缩略图。

---

## 3. 子分类详解

| 子类 | 算子数 | 代表算子 | 用途速览 |
|------|-------|---------|---------|
| **Access** | ~15 | `get_image_pointer1`, `get_image_pointer3`, `get_image_size`, `get_image_type`, `get_image_time`, `get_image_domain` | 提取图像指针、尺寸、类型、像素域 |
| **Acquisition** | ~10 | `grab_image`, `grab_image_async`, `grab_data`, `open_framegrabber`, `info_framegrabber`, `close_framegrabber`, `set_framegrabber_param` | 相机采集（同步/异步） |
| **Channel** | ~15 | `access_channel`, `append_channel`, `channels_to_image`, `compose3`, `compose5`, `compose6`, `compose7`, `decompose3`, `decompose4`, `decompose5`, `decompose6`, `decompose7` | 多通道拆分/合成 |
| **Creation** | ~15 | `gen_image_const`, `gen_image1`, `gen_image1_rect`, `gen_image3`, `gen_image_surface_first_order`, `gen_image_surface_second_order`, `read_image` | 程序化生成图像 |
| **Domain** | ~15 | `change_domain`, `crop_domain`, `crop_rectangle1`, `full_domain`, `reduce_domain`, `rectangle1_domain`, `expand_domain`, `get_domain` | ROI / 域管理 |
| **Features** | ~20 | `gray_histo`, `gray_histo_abs`, `histo_to_thresh`, `min_max_gray`, `intensity`, `entropy_gray`, `entropy_image`, `fuzzy_entropy`, `fuzzy_histogram` | 灰度统计 / 直方图 / 熵 |
| **Format** | ~10 | `crop_rectangle1`, `mirror_image`, `rotate_image`, `zoom_image_factor`, `zoom_image_size`, `map_image` | 几何格式变换 |
| **Manipulation** | ~15 | `concat_obj`, `tile_images`, `tile_images_offset`, `tile_channels`, `overpaint_gray`, `overpaint_region`, `paint_gray`, `paint_region`, `set_grayval` | 拼接 / 涂绘 / 像素值写入 |
| **Type conversion** | ~15 | `convert_image_type`, `rgb1_to_gray`, `rgb3_to_gray`, `gray_to_rgb`, `cfa_to_rgb`, `trans_from_rgb`, `trans_to_rgb`, `real_to_abs`, `abs_to_real`, `region_to_bin`, `region_to_label`, `region_to_mean` | 类型 / 色彩空间转换 |
| **Image Source** | ~10 | `connect_image_source`, `control_image_source`, `fetch_from_image_source`, `start_image_source`, `stop_image_source`, `set_image_source_param`, `get_image_source_param` | 统一图像源抽象 |

---

## 4. 核心算子详解

下面列出本分类下 25 个最高频算子，按"使用频率"递减：

1. **read_image** — 从文件读图 / 输入：`Image : out`、`FileName : in`；支持 BMP/PNG/JPEG/TIFF/HEIC 等；最常用的"开始"。
2. **write_image** — 存图 / 输入：`Image`、`Format`、`Quality`、`FileName`；存证必备。
3. **get_image_size** — 查尺寸 / 输出：`Width, Height`；所有 `*_model_image_size` 类调用都需要。
4. **get_image_pointer1** — 拿单字节通道像素指针 / 输出：`Pointer, Type, Width, Height`；C++/C# 集成必用。
5. **get_image_pointer3** — 多通道 RGB 像素指针 / 输出：`PointerRed, PointerGreen, PointerBlue, Type, Width, Height`。
6. **get_image_type** — 查像素类型（byte/uint2/int2/real/int4）；分支处理必需。
7. **dev_open_window** — 调试窗口 / 输入：`Row, Column, Width, Height, Background`；HDevelop 起点。
8. **dev_display** — 显示对象（图像/区域/XLD）到当前 dev 窗口；HDevelop 显示主力。
9. **disp_image** — 显式 `disp_image(Image, WindowHandle)`；C++/C# 部署版。
10. **dev_close_window** — 关闭 dev 窗口，清理资源。
11. **reduce_domain** — 限定 ROI（任意形状） / 输入：`Image, Region → ImageReduced`；下游算法只在这块域内计算。
12. **crop_domain** — 把图像裁剪到域边界 / 输出更小的 `Image`；后续算法对全图计算但内存更省。
13. **full_domain** — 恢复 ROI 到整图；与 `reduce_domain` 反向。
14. **change_domain** — 仅替换图像的域指针，不裁像素；做坐标对齐时常用。
15. **rectangle1_domain** — 把域裁到矩形框；做标准化 ROI。
16. **decompose3** — RGB 三通道拆分 / 输出：`ImageR, ImageG, ImageB`；颜色处理第一步。
17. **compose3** — 三通道合 RGB；颜色合成最后一步。
18. **trans_from_rgb** — RGB → HSV/HSI/YUV/CIELab/CIELuv/YCbCr；色彩分析核心。
19. **trans_to_rgb** — 各种色彩空间 → RGB；用于回显。
20. **cfa_to_rgb** — Bayer RAW → RGB；高分辨率彩色相机第一站。
21. **rgb1_to_gray** — RGB 三通道按 BT.601 公式合成单通道灰度图（输出还是 `HImage`）；视觉算法主力。
22. **rgb3_to_gray** — RGB 三通道独立灰度化（输出 3 个灰度 `HImage`）；通道独立分析用。
23. **convert_image_type** — 像素类型转换 / `byte ↔ uint2 ↔ int2 ↔ real`；FFT/算术运算常需 `real`。
24. **min_max_gray** — 求 ROI 内灰度最小最大；自动阈值前置。
25. **gray_histo** — 求灰度直方图 / 输出：`AbsoluteHisto, RelativeHisto`；阈值选取辅助。
26. **grab_image** / **grab_image_async** — 同步/异步相机抓图；在线项目生命线。
27. **open_framegrabber** — 打开相机句柄；采集链路第一步。

---

## 5. HDevelop 示例代码

### 示例 1：图像读取 + 多色彩空间转换 + ROI 处理

**场景**：某包装印刷产线，需要把彩色印刷图转为 L*a*b* 后做色差。
**功能**：读图 → 通道分解 → 色彩空间转换 → 多窗口对比显示。
**预期输出**：原图、HSV 三通道、Lab 三通道并排显示。

```hdevelop
* 示例 1：色彩空间转换 + ROI 限定
* 场景：印刷色差分析流程
dev_update_window ('off')
dev_update_pc ('off')
dev_update_var ('off')

* 1. 读取彩色图像
read_image (ColorImage, 'color_pieces_01')
get_image_size (ColorImage, ImageWidth, ImageHeight)
get_image_type (ColorImage, ImageType)

* 2. 拆分为 RGB 三通道
decompose3 (ColorImage, ImageR, ImageG, ImageB)

* 3. 创建主窗口
dev_open_window (0, 0, ImageWidth / 2, ImageHeight / 2, 'black', WindowHandle1)
dev_set_part (0, 0, ImageHeight - 1, ImageWidth - 1)
dev_display (ColorImage)
dev_disp_text ('Original RGB', 'window', 12, 12, 'black', 'box', 'true')

* 4. 创建第二个窗口显示 HSV 拆分结果
dev_open_window (0, ImageWidth / 2 + 10, ImageWidth / 2, ImageHeight / 2, 'black', WindowHandle2)
trans_from_rgb (ColorImage, ImageH, ImageS, ImageV, 'hsv')
compose3 (ImageH, ImageS, ImageV, ImageHSV)
dev_display (ImageHSV)
dev_disp_text ('HSV composite', 'window', 12, 12, 'black', 'box', 'true')

* 5. 创建第三个窗口：Lab 空间
dev_open_window (ImageHeight / 2 + 60, 0, ImageWidth / 2, ImageHeight / 2, 'black', WindowHandle3)
trans_from_rgb (ColorImage, ImageL, ImageA, ImageB, 'cielab')
compose3 (ImageL, ImageA, ImageB, ImageLab)
dev_display (ImageLab)
dev_disp_text ('CIELab composite', 'window', 12, 12, 'black', 'box', 'true')

* 6. 限定 ROI（圆形区域：仅看中心区域）
gen_circle (ROICircle, ImageHeight / 2, ImageWidth / 2, min([ImageWidth, ImageHeight]) / 4)
reduce_domain (ColorImage, ROICircle, ImageReduced)

* 7. 在 ROI 内做灰度直方图
rgb1_to_gray (ImageReduced, GrayReduced)
gray_histo (GrayReduced, ROICircle, AbsoluteHisto, RelativeHisto)
MinGray := 0
MaxGray := 255
PeakGray := 0
PeakVal := 0
for i := 0 to 255 by 1
    if (AbsoluteHisto[i] > PeakVal)
        PeakVal := AbsoluteHisto[i]
        PeakGray := i
    endif
endfor

* 8. 在第一个窗口显示直方图统计
dev_set_window (WindowHandle1)
dev_disp_text ('Peak gray = ' + PeakGray$'.0' + ', Count = ' + PeakVal$'.0', 'window', 40, 12, 'yellow', 'box', 'true')

dev_update_pc ('on')
dev_update_var ('on')
dev_update_window ('on')
```

### 示例 2：相机异步采集 + 多 ROI 抓图

**场景**：双相机同步触发抓图，左右两个不同尺寸 ROI。
**功能**：相机初始化 → 异步抓图 → 提取元数据 → 拼图存证。
**预期输出**：左右两图拼接为一张证据图。

```hdevelop
* 示例 2：模拟相机异步采集流程
* 场景：双相机同步触发（实际项目用 open_framegrabber 替换 read_image）

* 关闭自动更新，提升抓图效率
dev_update_window ('off')
dev_update_pc ('off')
dev_update_var ('off')

* 1. 模拟相机 1（左相机，全局）
read_image (LeftImage, 'bottles/bottle_mono_01')
get_image_size (LeftImage, LeftWidth, LeftHeight)
get_image_type (LeftImage, LeftType)

* 2. 模拟相机 2（右相机，局部）
read_image (RightImage, 'bottles/bottle_mono_02')
get_image_size (RightImage, RightWidth, RightHeight)

* 3. 拆解相机 1：找中心 ROI
gen_rectangle1 (LeftROI, LeftHeight * 0.3, LeftWidth * 0.3, LeftHeight * 0.7, LeftWidth * 0.7)
reduce_domain (LeftImage, LeftROI, LeftReduced)
crop_domain (LeftReduced, LeftCropped)
get_image_size (LeftCropped, CropWidth, CropHeight)

* 4. 拆解相机 2：找右侧 ROI
gen_rectangle1 (RightROI, RightHeight * 0.2, RightWidth * 0.5, RightHeight * 0.8, RightWidth * 0.9)
reduce_domain (RightImage, RightROI, RightReduced)
crop_domain (RightReduced, RightCropped)

* 5. 拼图显示
dev_open_window (0, 0, CropWidth * 2 + 20, CropHeight, 'black', WindowHandle)
dev_set_part (0, 0, CropHeight - 1, CropWidth * 2 + 19)

* 把两张图横向拼接（用 concat_obj）
concat_obj (LeftCropped, RightCropped, CombinedImages)
tile_images_offset (CombinedImages, TiledImage, [0, 0], [0, CropWidth + 20], [-1, -1], [-1, -1], [-1, -1], [-1, -1], max(CropWidth, CropWidth) * 2 + 20, CropHeight)
dev_display (TiledImage)

* 6. 显示元数据
dev_disp_text ('Left cam: ' + LeftWidth$'.0' + 'x' + LeftHeight$'.0', 'window', 12, 12, 'white', 'box', 'true')
dev_disp_text ('Right cam: ' + RightWidth$'.0' + 'x' + RightHeight$'.0', 'window', 30, 12, 'white', 'box', 'true')

* 7. 存证
write_image (TiledImage, 'png', 0, 'evidence_combined.png')

dev_update_pc ('on')
dev_update_var ('on')
dev_update_window ('on')
```

### 示例 3：Bayer RAW → RGB 还原 + 像素类型转换

**场景**：显微医学相机输出 Bayer 格式的 `uint2` 图像，需要还原彩色。
**功能**：Bayer 去马赛克 → 像素类型归一化 → ROI 限定 → 灰度直方图分析。
**预期输出**：还原后的 RGB 图像与原 Bayer 缩略图并排。

```hdevelop
* 示例 3：Bayer RAW → RGB
* 场景：医学显微相机

dev_update_window ('off')
dev_update_pc ('off')
dev_update_var ('off')

* 1. 模拟 Bayer RAW（uint2 灰度）
read_image (BayerRaw, 'bayer_image_simulated')
get_image_size (BayerRaw, BWidth, BHeight)
get_image_type (BayerRaw, BayerType)

* 2. 去马赛克为 RGB（hamilton 算法精度高）
cfa_to_rgb (BayerRaw, RGBImage, 'hamilton')

* 3. 像素类型归一化（uint2 → byte，便于显示）
convert_image_type (RGBImage, RGBImageByte, 'byte')

* 4. 通道拆分以便检查 Bayer 模式正确性
decompose3 (RGBImageByte, ImgR, ImgG, ImgB)

* 5. 创建对比窗口
dev_open_window (0, 0, BWidth * 2 + 20, BHeight, 'black', WinHandle)
dev_set_part (0, 0, BHeight - 1, BWidth * 2 + 19)
dev_display (BayerRaw)
dev_disp_text ('Bayer RAW', 'window', 12, 12, 'yellow', 'box', 'true')

* 6. 在右侧显示还原后的 RGB
dev_set_part (0, BWidth + 20, BHeight - 1, BWidth * 2 + 19)
dev_display (RGBImageByte)
dev_disp_text ('Demosaiced RGB', 'window', 12, 12, 'yellow', 'box', 'true')

* 7. ROI 内灰度统计
gen_circle (CenterROI, BHeight / 2, BWidth / 2, min([BWidth, BHeight]) / 4)
reduce_domain (RGBImageByte, CenterROI, ROIImage)
rgb1_to_gray (ROIImage, ROIGray)
min_max_gray (ROIGray, CenterROI, 0.0, MinGray, MaxGray, RangeGray)
intensity (ROIGray, CenterROI, MeanGray, DeviationGray)

* 8. 输出统计结果
dev_disp_text ('Min=' + MinGray$'.2f' + ' Max=' + MaxGray$'.2f', 'window', 30, 12, 'cyan', 'box', 'true')
dev_disp_text ('Mean=' + MeanGray$'.2f' + ' Std=' + DeviationGray$'.2f', 'window', 48, 12, 'cyan', 'box', 'true')

dev_update_pc ('on')
dev_update_var ('on')
dev_update_window ('on')
```

---

## 6. 典型工业流水线

### 流水线 1：多相机在线采集 + 标准化 ROI

```
[相机 1..N] → open_framegrabber (N 路)
   ↓
grab_image_async (N 路并行触发)
   ↓
get_image_size (获取每路尺寸)
   ↓
reduce_domain (限定到产品 ROI)
   ↓
tile_images (拼图)
   ↓
write_image (存证 + 上传)
```

### 流水线 2：Bayer 相机完整色彩还原链

```
Bayer RAW (uint2)
   ↓
cfa_to_rgb → RGB uint2
   ↓
convert_image_type → RGB byte
   ↓
trans_from_rgb → Lab 三通道
   ↓
[后续色彩分析算法]
   ↓
trans_to_rgb → 还原 RGB 用于显示
```

### 流水线 3：批量图像回放与归档

```
list_files (扫描目录)
   ↓
for each file:
  read_image → Image
  ↓
  get_image_size → Width, Height
  ↓
  (内部算法 OK/NG 判定)
  ↓
  write_image → result_ok/result_ng 目录
endfor
```

---

## 7. 常见陷阱与最佳实践

1. **陷阱：`reduce_domain` 不节省内存**——`reduce_domain` 仅设定 ROI 标志，图像像素数据并未裁剪。如果后续要做 `crop_domain` 释放内存，记得二次调用。
2. **陷阱：`rgb1_to_gray` vs `rgb3_to_gray` 区别**——`rgb1_to_gray` 输出**一个**灰度 `HImage`（按 BT.601 公式）；`rgb3_to_gray` 输出**三个**独立灰度 `HImage`，对应 R/G/B 单通道分别灰度。
3. **陷阱：`decompose3` 后通道顺序**——输出顺序固定为 `(R, G, B)`，不要依赖通道名重排。
4. **陷阱：`get_image_pointer1` 与 `get_image_pointer3` 的内存布局**——前者是连续单字节；后者是 3 个独立指针指向 RGB 三个平面。集成 C++/C# 时必须区分。
5. **陷阱：图像域 vs 像素矩阵**——`change_domain` 不改变像素矩阵，仅改域指针；做坐标变换时要明确这一点。
6. **陷阱：`grab_image` 与 `grab_image_async`**——同步阻塞，调试用；异步非阻塞，产线用，但要处理缓冲溢出。
7. **最佳实践：所有 ROI 都先可视化**——先 `dev_set_draw('margin')` + `dev_set_color('red')` 显示 `reduce_domain` 用的 `Region`，确认无误后再传算法。
8. **最佳实践：图像类型提前判定**——`get_image_type` 后用 `if (Type == 'byte') ...`，避免 FFT 等算子因 `real` vs `byte` 报错。

---

## 8. 参数调优指南

| 算子 | 关键参数 | 推荐值 | 调整策略 |
|------|---------|--------|----------|
| `read_image` | `FileName` | 绝对路径或 HALCON 图像目录 | 使用 HALCON 自带 `%HALCONIMAGES%` 环境变量 |
| `write_image` | `Quality` | 80–95（JPEG） | 高保真选 PNG/TIFF；存档选 JPEG 80 |
| `reduce_domain` | `Image, Region` | Region 用 `gen_*` 精确生成 | 大区域建议后续 `crop_domain` 进一步压缩 |
| `crop_rectangle1` | `Row1, Col1, Row2, Col2` | 严格 ROI 边界 | 务必 +1/-1 避免越界 |
| `trans_from_rgb` | `ColorSpace` | `'cielab'`（色差）、`'hsv'`（照明无关） | 包装/印刷首选 Lab，户外光照选 HSV |
| `cfa_to_rgb` | `CFAType` | `'bilinear'`（快）、`'hamilton'`（精） | 高分辨率优先 `'hamilton'` |
| `convert_image_type` | `NewType` | `'byte'`（显示）、`'real'`（FFT） | 算术后建议转 `byte` |
| `rgb1_to_gray` | （无参数） | 默认 BT.601 公式 | 旧项目用 BT.709 需手动加权 |

---

## 9. 相关分类

- **Filters**：图像的"加工车间"——所有滤波都依赖 Image 的输入输出。
- **Regions**：通过 `threshold` 过渡到区域；用 `region_to_bin`/`region_to_label` 回流到图像。
- **Graphics**：所有 `disp_*` 操作显示 Image；Image 是显示的常见对象。
- **File**：`read_image`/`write_image` 是 File 分类在图像层面的实例。
- **Calibration**：`image_to_world_plane` 把 Image 转换为世界坐标系下的图。
- **XLD**：通过 `region_to_bin` 间接关联。

---

## 10. 学习小结

1. **Image 是"自来水"**：所有项目都从 `read_image` 开始，到 `write_image` 结束；ROI 处理 (`reduce_domain` + `crop_domain`) 是性能与精度平衡的关键。
2. **域管理是 HALCON 的精髓**：`reduce_domain`/`crop_domain`/`full_domain`/`change_domain`/`rectangle1_domain` 各有用途，混合使用可同时优化性能与代码可读性。
3. **色彩空间不是装饰**：`trans_from_rgb` 到 Lab/HSV 后，许多"看似 RGB 处理不好"的算法突然变好。
4. **类型转换决定算法可用性**：`byte ↔ real ↔ int2` 的转换是滤波器（FFT、深度学习）的前置条件。
5. **指针操作是集成核心**：`get_image_pointer1`/`get_image_pointer3` 是 HALCON 与 C++/C# 交互的必经桥梁。