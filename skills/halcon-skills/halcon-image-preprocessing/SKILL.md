---
name: halcon-image-preprocessing
description: >-
  HALCON image acquisition and preprocessing: reading/writing images, channel
  handling and decomposition, domain/ROI setup, pixel-type conversion,
  color-space transforms (HSV/HSI/CIELab), gray-value filters (denoise/enhance),
  thresholding and segmentation, and binary morphology. Use this skill whenever a
  HALCON/HDevelop task starts with loading or preparing an image before
  detection or measurement — camera acquisition (open_framegrabber /
  grab_image / grab_image_async), read_image / write_image, reduce_domain /
  crop_domain ROI setup, decompose3 / compose3 / trans_from_rgb color work,
  convert_image_type / rgb1_to_gray type handling, or choosing between
  gauss_filter / median_image / emphasize / median_image / dyn_threshold /
  binary_threshold, and morphology opening/closing. It covers the "front end" of
  any vision pipeline. Also use it when the user asks how to set up a camera, how
  to reduce a region of interest, or how to clean up an image before matching,
  measuring, or OCR.
---

# HALCON 图像采集与预处理

> 适用：任何视觉流水线的"前端"——把物理世界变成可交给下游算法的干净图像。
> 范围涵盖：相机采集、图像读写、通道/域/类型处理、颜色空间、灰度滤波、阈值分割、形态学。
> 编写规范（格式/配色/编码规则）见 `../_authoring/`（conventions.md 为精简总结；halcon_skill.md 为完整元 skill；hdev_format_reference.md / hscript_format_reference.md / hrun_reference.md / hscriptengine_reference.md 为脚本格式与 CLI 详解），本 skill 只讲领域知识与选型。

---

## 一、一句话选型

| 你想干什么 | 首选手段 | 一句话 |
|---|---|---|
| 从相机/文件拿图 | `grab_image`/`grab_image_async`/`read_image` | 一步到位，产线用异步 |
| 只处理图像某块 | `reduce_domain`（+`crop_domain` 释放内存） | 提速度、聚焦算法 |
| 拆分 RGB / 合回 | `decompose3`/`compose3`/`append_channel` | 颜色处理第一步 |
| 转颜色空间 | `trans_from_rgb`/`trans_to_rgb`（`'hsv'`/`'hsi'`/`'cielab'`） | 抗光照变化、接近人眼 |
| Bayer RAW 还原 | `cfa_to_rgb` | 高分辨率彩机第一站 |
| 灰度/类型转换 | `rgb1_to_gray`/`convert_image_type` | FFT/DL 常需 `real` |
| 去噪 | `gauss_filter`/`median_image`/`binomial_filter` | 均值/中值/高斯按噪声类型选 |
| 增强 | `emphasize`/`scale_image_range` | 低对比、细节强化 |
| 找前景 blob | `threshold`/`binary_threshold`/`dyn_threshold` → `connection` | 分割的起点 |
| 清理区域 | `opening_circle`/`closing_circle`/`fill_up` | 去噪点/填隙 |

---

## 二、图像采集（相机/文件）

### 标准三步流程
```hdevelop
* 连接
open_framegrabber (AcqName, 1, 1, 0, 0, 0, 0, 'default', -1, 'default', -1, \
                   'false', CameraType, Board, Port, -1, AcqHandle)
* 抓单帧 / 异步流水
grab_image (Image, AcqHandle)                    * 阻塞
grab_image_async (Image, AcqHandle, MaxDelay)    * 非阻塞，满帧率（推荐产线）
* 释放
close_framegrabber (AcqHandle)
```
从文件读图：`read_image (Image, 'particle')`（按 `%HALCONIMAGES%` 搜索）。

### open_framegrabber 参数（16 个，未用处填 `'default'`/`-1`）
| 参数 | 含义 |
|---|---|
| `AcqName` | 采集接口名（主参数） |
| `HorizontalResolution`/`VerticalResolution` | 空间分辨率（1=原图） |
| `ImageWidth/Height`,`StartRow/Column` | 裁剪（0=全幅） |
| `Field` | 模拟相机场模式；`BitsPerChannel` | 每通道位数（>8 得 uint2） |
| `ColorSpace` | `'gray'`/`'rgb'`；`ExternalTrigger` | `'false'` 默认 |
| `CameraType`,`Device`,`Port`,`LineIn`,`Generic` | 设备/端口选择 |

- 查询接口：`info_framegrabber(AcqName,'general',Info,Value)`（也可 `'revision'`/`'info_boards'`/`'camera_type'`/`'defaults'`/`'parameters'`）。
- 固定 vs 动态参数：固定（如 `CameraType`）只在 open 时设；动态（小写下划线，如 `'image_width'`/`'port'`/`'external_trigger'`）连接期间用 `set_framegrabber_param`/`get_framegrabber_param` 改。
- **外部触发**：`ExternalTrigger='true'` 或动态 `set_framegrabber_param(AcqHandle,'external_trigger','true')`；**必须设 `'grab_timeout'`（毫秒，如 2000），否则无触发时挂死**。
- **异步坑**：`grab_image_async` 返回的图可能比调用"早"曝光（延迟为负）；对"下一次"调用改动态参数不生效，"再下一次"才生效。
- 板卡/多相机：多板卡每板 `open_framegrabber`（仅 `Device` 不同）；端口切换只 open 一次，用 `set_framegrabber_param(Handle,'port',Port)` 切（所有相机须兼容）；同时抓取用单次 `grab_image` 返回多通道图 + `count_channels` + `decompose2/3` 拆。
- 非标准设备：`gen_image1`/`gen_image3`（拷贝）或 `_extern` 变体（不拷贝，可 volatile）；标准接口如 GenICam/GigE 为 generic 接口，设备特定参数向设备查询。
- **照明（采集前务必重视）**：镜面/低粗糙度用漫射光；测轮廓用背光；光场/暗场用于方向；正交视图配远心镜头精度最高，斜视须标定校正透视。

---

## 三、域 / ROI

- 创建：`gen_circle`/`gen_rectangle1`/`gen_region_polygon_filled` 标准形状；`draw_region` 交互；由分割/XLD 转。
- 合并：`reduce_domain (Image, ROI, ImageReduced)`（**推荐**）；`rectangle1_domain` 快捷；`change_domain` 更快但**不检查越界**（越界崩溃）。
- 取出域：`get_domain`。
- **ROI 用 runlength 编码，水平长条比垂直高效**；ROI 越小越快。
- 区域后处理：`fill_up`/`shape_trans('convex'/'rectangle2')`/`erosion_circle`/`closing_circle`。
- 对象移动时用 shape-based matching 结果对齐 ROI（`hom_mat2d_compose`+`affine_trans_region`）。
- **注意**：measure 工具（`gen_measure_arc`/`gen_measure_rectangle2`）**忽略图像 domain**，ROI 由数值坐标定义。

---

## 四、通道与颜色空间

- 拆分：`decompose3 (Image, ImageR, ImageG, ImageB)`（顺序固定 R,G,B，勿按名重排）；`access_channel`。
- 合成：`compose3`/`compose2`~`compose7`/`append_channel`/`channels_to_image`。
- 颜色空间：`trans_from_rgb (R,G,B,H,S,V,'hsv')` / `'hsi'` / `'i1i2i3'` / `'cielab'`；`trans_to_rgb` 回显；快版 `create_color_trans_lut`+`apply_color_trans_lut`。
- HSV 按 hue 选色最抗光照：`threshold(Saturation,HighSat,100,255)`+`reduce_domain(Hue,HighSat,...)`+`threshold(HueHighSat,Yellow,20,50)`。Hue 参考：yellow 20~50、red 0~10、orange 10~30。
- Bayer：`cfa_to_rgb (BayerRaw, RGB, CFAType, Interpolation)`，HALCON 26.05 合法 `Interpolation` ∈ `{'bilinear'`（默认）, `'bilinear_dir'`, `'bilinear_enhanced'`}；`'bilinear_enhanced'` 梯度感知、质量最高（去锯齿/伪色），离线单帧推荐。`CFAType` ∈ `{'bayer_gb'`（默认）, `'bayer_bg'`, `'bayer_gr'`, `'bayer_rg'}`，须与传感器布局匹配。宏文件 `MVTecCol` 提供标准配色。

---

## 五、灰度/类型转换

| 算子 | 作用 | 备注 |
|---|---|---|
| `convert_image_type` | `byte↔uint2↔int2↔real` | 显示转 `byte`；FFT/算术转 `real` |
| `rgb1_to_gray` | 单通道灰度（BT.601） | 输出**1 个** HImage |
| `rgb3_to_gray` | 三通道独立灰度 | 输出**3 个** HImage |
| `real_to_abs`/`abs_to_real` | 实数↔绝对值 | 归一化显示 |
| `region_to_bin`/`region_to_label`/`region_to_mean` | 区域↔图像 | 交换用 |
| `min_max_gray`/`gray_histo` | 灰度统计 | 自动阈值前置 |

---

## 六、常见预处理滤波

| 算子 | 用途 | 典型参数 |
|---|---|---|
| `gauss_filter`/`binomial_filter` | 高斯/二项去噪 | `Sigma`≈1~2 |
| `median_image` | 中值（抑制小点/细线） | `'circle'`,3~7 |
| `mean_image` | 均值（平滑、算动态阈值背景） | mask 大小 |
| `smooth_image`/`anisotropic_diffusion` | 保边平滑 | — |
| `emphasize` | 低频增强（细节强化） | mask/系数 |
| `scale_image`/`scale_image_range` | 对比度缩放/拉伸 | 低对比图用 |
| `sub_image`/`gray_opening_shape` | 背景不均校正/底背景 | — |
| `gray_range_rect` | 灰值形态学（刻字增强） | 7x7 |

---

## 七、分割与形态学（产生 blob 的起点）

### 阈值分割选型
| 算子 | 适用 | 备注 |
|---|---|---|
| `threshold` | 固定阈值 | 最常用；`threshold(Image,R,120,255)` |
| `binary_threshold` | 自动找全局阈值 | 自动，简单图首选 |
| `auto_threshold` | 多阈值 | 灰度分布多峰 |
| `dyn_threshold` | 光照不均 | 配 `mean_image` 作背景参考（如 `dyn_threshold(Image,ImageMean,R,5,'dark'/'light'/'not_equal')`） |
| `fast_threshold` | 实时加速 | 需已知大致范围 |
| `local_threshold` | 局部自适应 | — |
| `gray_histo`+`histo_to_thresh` | 由直方图定阈值 | 自动阈值辅助 |

### 关键后处理顺序
`threshold` → `connection`（**必须调用才分连通域**）→ `select_shape`/`select_gray`（按 `'area'`/`'circularity'`/`'moments_i1'` 等）→ `fill_up` → 形态学清理：
- 去噪点：`opening_circle`/`opening_rectangle1`
- 填隙/桥接：`closing_circle`/`closing_rectangle1`
- 补洞：`fill_up`
- 集合运算：`union1`/`union2`/`intersection`/`difference`
- 形状近似：`shape_trans ('convex'/'outer_circle'/'rectangle2'/'inner_rectangle1'/'ellipse')`

### 常见陷阱
1. **`reduce_domain` 不省内存**——只设 ROI 标志，像素未裁剪；再 `crop_domain` 才释放。
2. **`connection` 漏掉会"合并"**——`threshold` 默认只出一个 region，必须先 `connection`。
3. `decompose3` 通道顺序固定 (R,G,B)，勿按名重排；`get_image_pointer1` 是连续单字节，`get_image_pointer3` 是 3 个独立指针（RGB 平面）。
4. `rgb1_to_gray`（1 个 HImage）vs `rgb3_to_gray`（3 个 HImage）别混。
5. `change_domain` 不改像素矩阵只改域指针；越界不检查，会崩。
6. 提精度：`area_center` 质心本身是亚像素的；更高用 `area_center_gray` 灰度加权或亚像素边缘（见 `halcon-edge-contour`）。
7. HSV 法在低饱和度时失效，须保证一定饱和度。
8. 提速通用手段：`set_check('~give_error')`、`set_system('init_new_image','false')`。

---

## 八、引用

- 中文算子总览：`references/ops_01_Image.md`、`ops_02_Filters.md`、`ops_05_Segmentation.md`、`ops_16_Graphics.md`、`ops_27_ImageSource.md`
- 逐算子精确签名/默认值（官方 `reference_hdevelop.pdf` 抽取）：见 `references/ref_OPERATOR_REFERENCE.md` 中的文件路径。
- 关联 skill：`halcon-edge-contour`（亚像素边缘）、`halcon-matching`（定位）、`halcon-inspection-defect`（Blob 缺陷）、`halcon-visualization-system`（显示）。


---

## 用例参考（example_*.md）

本 skill 目录下 `references/` 含以下项目里抽出的真实用例（按主题归档，可直接借鉴实现思路/算子组合）：

- `references/example_image_enhancement.md`
- `references/example_image_smoothing.md`
- `references/example_morphology_operations.md`
- `references/example_roi_emphasize_enhance.md`
- `references/example_segmentation_threshold.md`
