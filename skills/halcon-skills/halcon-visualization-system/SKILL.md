---
name: halcon-visualization-system
description: >-
  HALCON infrastructure: visualization & HMI graphics (open_window /
  dev_open_window, disp_obj, disp_image, set_color / set_draw / set_part /
  set_lut, set_display_font, dump_window), developer tools (dev_* operators),
  compute device / GPU acceleration (query_available_compute_devices,
  open_compute_device, activate_compute_device), I/O devices
  (open_io_device, open_io_channel, read/write_io_channel), and core data types
  — tuple, matrix, object, control flow, file I/O, and image source. Use this
  skill whenever a HALCON/HDevelop task involves displaying results, building a
  window/visualization layout, GPU acceleration, communicating with PLC/sensors,
  or working with tuples, matrices, object arrays, dictionaries, control flow,
  or reading/writing files and models. Trigger on disp_image / disp_obj /
  dev_display / dev_set_color / set_window_param / open_compute_device /
  activate_compute_device / tuple_* / create_matrix / solve_matrix / concat_obj /
  read_* / write_* / set_system / get_system, or when the user needs to speed up
  a pipeline with a compute device or integrate with external hardware.
---

# HALCON 可视化、系统与集成

> 定位：流水线的"门面与地基"——显示、调试、GPU 加速、I/O 通信、数据结构与文件名项。
> 可视化配色方案见 `../_authoring/halcon_skill.md`（可视化配色方案章节）+ `conventions.md`（§五精简版），本 skill 聚焦算子与"怎么用"。
> 编写规范见 `../_authoring/`（conventions.md 为精简总结；完整规范在 halcon_skill.md；脚本格式/CLI 见同名 *_reference.md）。

---

## 一、一句话选型

| 需求 | 首选 | 说明 |
|---|---|---|
| 开窗显示 | `open_window`/`dev_open_window` | HDevelop 用 `dev_*` |
| 显示任意对象 | `disp_obj` | 自动区分图像/region/XLD |
| 显示指定类型 | `disp_image`/`disp_region`/`disp_xld` | 更可控 |
| 设置坐标系 | `set_part` | 编程环境必须显式设，否则范围未定义 |
| 大图缩略缩放质量 | `set_part_style ('weighted')`+`set_window_param('region_quality','good')` | 提升缩放质量 |
| 窗口无闪烁 | `set_window_param(Win,'flush','false')`+手动 `flush_buffer` | 硬件加速时 |
| 保存窗口图像 | `dump_window (Win, FileName, Device)` | 存证 |
| GPU 加速 | `open_compute_device`+`activate_compute_device` | 部分算子 |
| 与 PLC/传感器通信 | `open_io_device`+`open_io_channel`+`read/write_io_channel` | 触发/同步/控制 |

---

## 二、可视化（Graphics / Develop）

```hdevelop
open_window (0, 0, Width, Height, 'black', WindowHandle)
set_part (WindowHandle, 0, 0, Height-1, Width-1)     * 编程环境必须显式设坐标系
set_display_font (WindowHandle, 14, 'mono', 'true', 'false')
disp_image (Image, WindowHandle)
disp_region (Region, WindowHandle)                   * 或 disp_obj(Region,Win)
set_color (WindowHandle, 'green'); set_draw (WindowHandle, 'margin'); set_line_width (WindowHandle, 2)
disp_cross / disp_text / disp_arrow / disp_message (WindowHandle, Msg, 'window', Row, Col, Color, 'box', 'false')
```
- HDevelop 开发用 `dev_open_window`/`dev_display`/`dev_set_color`/`dev_set_draw`/`dev_set_part`/`dev_disp_text`（自动创建/管理当前窗口）。
- **开发 vs 部署**：HDevEngine 默认抑制 dev_* 提效；导出 C++/C# 时用 `dev_set_window`+`dev_set_part`；MFC/VB 用 FatherWindow 嵌入。
- **配色**：按 `../_authoring/halcon_skill.md`（可视化配色方案章节） / conventions.md（§五精简版） 的表（OK=#85A407、失败=#CA3333、计算=#005F87、低警告=#EACE21、高警告=#E77910；半透明加 `80`）。命名变量按含义（`ColorGoodDetection` 等），勿用 `Green`/`Color1`。
- **鼠标（非事件驱动）**：`get_mposition`/`get_mbutton`（立即返回/等点击）；`draw_*` 画形状。事件驱动需系统级机制。
- **保存窗口**：`dump_window(WindowHandle, FileName, 'png')`。
- **坑**：可视化耗时——只在需要时显示；16 位色深比 32 快；低分辨率也有帮助。

---

## 三、Compute Devices（GPU 加速）

```hdevelop
query_available_compute_devices (DeviceIdentifier)          * 1 查询
open_compute_device (DeviceIdentifier, DeviceHandle)        * 2 打开
init_compute_device (DeviceHandle, 'derive_gauss')          * 3 初始化编译 kernel
activate_compute_device (DeviceHandle)                      * 4 激活
* 5 计算（如 derivate_gauss）
deactivate_compute_device (DeviceHandle)                    * 6 停用
```
- 支持算子（示例）：`binomial_filter`/`convol_image`/`derivate_gauss`/`median_image`/`sobel_amp`/`lines_gauss`/`edges_image`/`edges_sub_pix`/`affine_trans_image`/`trans_from_rgb`/`trans_to_rgb`/`cfa_to_rgb`/`lut_trans`/`min_image`/`max_image`/`sub_image` 等。用 `get_operator_info(op,'compute_device',Info)` 查单个。
- 参数：`get/set_compute_device_param`（`'asynchronous_execution'`、`'buffer_cache_capacity'` 等，缓存默认各占可用内存 1/3）。
- **坑**：
  1. **区域(domain)处理在 GPU 无效**（整图传送）——需 `crop_domain` 裁剪；用灰度形态学模拟 region 形态学（`threshold`→`lut_trans`、`intersection`→`min_image`、`dilation_rectangle1`→`gray_dilation_rect`）。
  2. GPU 只支持子集：`median_image` 仅 3×3/5×5；`derivate_gauss` sigma 上限 ~20.7；`trans_from_rgb` 仅 `'cielab'/'hsv'/'hsi'`。
  3. **是否提速必须实测**（benchmark：`count_seconds`+强制传图）；CPU 已快/算子很快/传送慢时不划算。
  4. GPU 高功耗、未必工业级、可能单精度、无 ECC、怕热/振动。

---

## 四、I/O Devices（PLC / 传感器）

```hdevelop
open_io_device (IOInterfaceName, DeviceName, [], [], IoDeviceHandle)
query_io_device (Handle, [], 'io_channel_names.digital_input', ChannelsInput)
open_io_channel (IoDeviceHandle, ChannelName, [], [], IoHandle)
read_io_channel (IoHandle, Value, Status)   * 或 write_io_channel
close_io_channel ([IoHandle0,IoHandle1]); close_io_device (IoDeviceHandle)
```
- 查询接口：`query_io_interface`；`control_io_interface`（如 OPC UA 证书）；`set/get_io_device_param` 特殊参数。
- **坑**：不支持设备自写 interface（MVTec 提供模板）。

---

## 五、核心数据类型与文件

| 类型 | 代表算子 | 一句话 |
|---|---|---|
| 元组 | `tuple_*`（数学/字符串/集合/选择） | 180+ 函数，HALCON 通用数据结构 |
| 矩阵 | `create_matrix`/`solve_matrix`/`svd_matrix`/`principal_comp`/`inv_matrix` | 数值底层 |
| 对象数组 | `concat_obj`/`copy_obj`/`select_obj`/`remove_obj` | 多对象管理；图标元组从 1 起，控制元组从 0 起 |
| 字典 | `create_dict`/`set_dict_tuple`/`get_dict_*` | 键值数据 |
| 文件 I/O | `read_image`/`write_image`/`read_region`/`write_region`/`read_*_model`/`write_*_model` | 图像/区域/模型/字典存档 |
| 系统 | `set_system`/`get_system` | 全局设置（`'clip_region'`/`'init_new_image'`/`'do_low_error'`） |
| 控制流 | `if/for/while/switch/try-catch` | 脚本流程 |
| 图像源 | `open_image_source`/`grab_image`/`set_image_source_param` | 统一图像源抽象 |

- **坑**：`set_system('clip_region','true')` 时若未 `read_image` 直接 `gen_rectangle1` 会**静默产生空 region**；`count_obj` 从 1 开始。

---

## 六、引用
- 中文算子总览：`references/ops_16_Graphics.md`、`ops_22_System.md`、`ops_23_File.md`、`ops_20_Matrix.md`、`ops_21_Tuple.md`、`ops_24_Object.md`、`ops_25_Control.md`、`ops_27_ImageSource.md`、`ops_30_Legacy.md`
- 逐算子签名/默认值：`references/ref_OPERATOR_REFERENCE.md`（Graphics / System / File / Matrix / Tuple / Object / Control / Image_Source / Legacy 章）。
- 关联：所有领域 skill 的显示/集成基建；`halcon-vision-workflow`（编排）。
