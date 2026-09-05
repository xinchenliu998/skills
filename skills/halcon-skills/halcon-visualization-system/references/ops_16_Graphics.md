# HALCON 算子分类详解：Graphics（图形显示）

> **HALCON 版本**：26.05.0.0 Progress
> **算子数量**：约 120 个
> **一级分类目录**：`toc_graphics.html`
> **学习层级**：L0–L2（必会显示基础 + 进阶交互 + 3D 可视化）

---

## 1. 概述

Graphics 分类是 HALCON 与"用户眼睛"之间的桥梁，几乎所有视觉项目的调试、HMI 看板、检测结果可视化、用户交互标注都依赖它。该分类不仅涵盖传统 2D 图形绘制（点、线、矩形、圆、文字），还包括：

- **窗口管理**：`open_window` / `dev_open_window` / `set_window_extents`
- **基本图形**：`disp_rectangle1/2` / `disp_circle` / `disp_arrow` / `disp_cross` / `disp_polygon` 等
- **文字与字体**：`set_font` / `disp_text` / `get_string_extents` / `query_font`
- **鼠标交互**：`draw_rectangle1/2` / `draw_circle` / `draw_polygon` / `draw_nurbs`
- **3D 场景渲染**：`create_scene_3d` / `add_scene_3d_instance` / `render_scene_3d`
- **Drawing Objects**：`create_drawing_object_*` + `set_drawing_object_callback` 实现高级交互 UI
- **显示参数控制**：`set_color` / `set_draw` / `set_line_width` / `set_paint` / `set_lut` / `set_part`

Graphics 算子只负责"画"——它们不修改图像数据，仅影响显示缓冲（或窗口后台）。理解这一特性对调试和性能优化至关重要：绘制大量图形可能拖慢 HMI 但不影响算法时间。

---

## 2. 应用场景

### 场景 1：自动化产线 HMI 看板（PCB 检测线）

相机实时采集 PCB 图像 → 算法检出缺陷 → 通过 `disp_image` 显示原图 → `disp_rectangle2` 标记所有 NG 位置 → `disp_text` 在每个缺陷上方显示类型/置信度 → `disp_arrow` 指向料盘剔除坐标。窗口通过 `dev_open_window` 创建并按 `set_window_extents` 固定布局。

### 场景 2：用户标注工具（教学/示教）

工程师在 HDevelop 中点击 `draw_rectangle2` 框选训练 ROI；通过 `draw_polygon` 描绘不规则形状；用 `draw_nurbs` 拟合贝塞尔曲线；通过 Drawing Objects 创建可拖拽的圆形/矩形 ROI 绑定回调函数，实现"画完即生效"的交互。

### 场景 3：3D 点云与表面检测可视化（机器人抓取）

相机+激光扫描生成 3D 点云（ObjectModel3D）→ `create_scene_3d` 创建场景 → `add_scene_3d_instance` 添加工件和抓取位姿箭头 → `add_scene_3d_camera` 设置视角 → `render_scene_3d` 渲染到窗口，便于工程师审核抓取策略。

### 场景 4：印刷质量检测结果呈现（包装行业）

检测出字符错误位置 → `disp_image` 显示原图 → `set_color('red')` + `disp_rectangle2` 圈出错误字符 → `set_color('green')` 显示 OK 字符 → `disp_text` 在画面顶部显示整体合格率；通过 `attach_background_to_window` 实现"双视图"（主图 + 缩略图）。

### 场景 5：报告生成与存证

`dump_window` / `dump_window_image` 把当前窗口（含所有叠加图形）保存为 PNG，作为检测报告附图；`new_line` 控制文字自动换行；`query_font` 列出可用字体（不同 HALCON 安装支持不同）。

---

## 3. 子分类详解

### 3.1 Window（窗口管理）— 约 15 算子

| 算子 | 用途 |
|------|------|
| `open_window` | 编程式打开窗口（指定父窗口 HWnd + 行列范围） |
| `dev_open_window` | HDevelop 调试用的窗口（自动布局） |
| `close_window` / `dev_close_window` | 关闭窗口 |
| `set_window_extents` | 调整窗口位置/尺寸 |
| `set_window_dc` / `set_window_attr` | 高级属性（仅 Windows） |
| `set_window_type` / `query_window_type` | 切换窗口类型（如 OpenGL） |
| `update_window_pose` | OpenGL 窗口的姿态更新 |
| `get_window_*` | 查询窗口参数（位置、句柄等） |
| `attach_background_to_window` | 多窗口叠加（背景/前景） |

### 3.2 Parameters（显示参数）— 约 25 算子

- **颜色**：`set_color` / `set_rgb` / `set_rgba` / `set_hsi` / `set_gray` / `set_colored`
- **填充**：`set_draw` ('margin'/'fill') / `set_shape` / `set_icon`
- **线宽**：`set_line_width` / `set_line_style` / `set_line_approx`
- **绘制模式**：`set_paint` ('default'/'invert') / `set_comprise`
- **区域范围**：`set_part` / `set_part_style` / `set_fix`（锁定显示区域）
- **LUT**：`set_lut` / `set_lut_style` / `set_fixed_lut`
- **像素**：`set_pixel` / `set_mshape` / `set_tshape`

> 注：所有 `dev_set_*` 是 HDevelop 的快捷方式，导出 C++/C# 后需替换为 `set_*`。

### 3.3 Object（图形对象显示）— 约 15 算子

| 算子 | 用途 |
|------|------|
| `disp_image` | 显示图像 |
| `disp_region` | 显示区域 |
| `disp_xld` | 显示亚像素轮廓 |
| `disp_object_model_3d` | 显示 3D 对象模型 |
| `disp_circle` / `disp_ellipse` | 显示圆/椭圆 |
| `disp_rectangle1/2` | 显示轴对齐/任意矩形 |
| `disp_line` / `disp_arrow` | 显示直线/箭头 |
| `disp_cross` | 显示十字标 |
| `disp_polygon` | 显示多边形 |
| `disp_arc` | 显示圆弧 |
| `disp_text` | 显示文字（支持框/阴影） |
| `disp_channel` / `disp_color` / `disp_distribution` | 多通道/彩色显示 |
| `disp_caltab` | 显示标定板 |

### 3.4 Text（文字处理）— 约 10 算子

- `set_font` / `query_font` / `get_font`
- `disp_text`（最常用，支持背景框和阴影）
- `set_tposition` / `get_tposition`（设置/查询文字位置）
- `set_tshape`（文字风格：粗体等）
- `get_string_extents` / `get_font_extents`（测量字符串尺寸，便于布局）
- `new_line` / `fnew_line`（自动/强制换行）
- `open_textwindow`（打开独立文本窗口）

### 3.5 Drawing（鼠标交互绘制）— 约 15 算子

| 算子 | 用途 |
|------|------|
| `draw_rectangle1` / `draw_rectangle2` | 拖拽画轴对齐/任意矩形 |
| `draw_circle` | 拖拽画圆 |
| `draw_ellipse` | 拖拽画椭圆 |
| `draw_line` | 拖拽画线 |
| `draw_point` | 单击取点 |
| `draw_polygon` | 多段折线 |
| `draw_nurbs` | NURBS 曲线 |
| `draw_xld` | 已有 XLD 编辑 |
| `draw_region` | 任意区域 |
| `draw_*_mod` | 带模态（已有初值）的版本 |
| `drag_region1/2/3` | 拖动已有区域 |

### 3.6 Mouse（鼠标查询）— 约 5 算子

`get_mbutton` / `get_mbutton_sub_pix`（等待任意键按下）/ `get_mposition` / `get_mposition_sub_pix`（查询当前位置）/ `send_mouse_*_event`（程序化注入事件）。

### 3.7 3D Scene（三维场景）— 约 20 算子

- `open_scene_engine`（初始化 OpenGL 引擎）
- `create_scene_3d` / `clear_scene_3d` / `display_scene_3d`
- `add_scene_3d_camera` / `set_scene_3d_camera_pose` / `set_scene_3d_camera_interactive` / `remove_scene_3d_camera`
- `add_scene_3d_instance` / `remove_scene_3d_instance` / `set_scene_3d_instance_pose`
- `add_scene_3d_light` / `set_scene_3d_light_param`
- `render_scene_3d` / `ray_intersect_scene_3d`
- `add_scene_3d_label` / `set_scene_3d_label_param`

### 3.8 Drawing Objects（高级交互对象）— 约 15 算子

支持鼠标拖拽 + 回调的"活"对象：
- 创建：`create_drawing_object_circle` / `rectangle1/2` / `ellipse` / `line` / `polygon` / `xld` / `text` / `spline`
- 关联窗口：`attach_drawing_object_to_window` / `detach_drawing_object_from_window`
- 回调：`set_drawing_object_callback`（事件包括拖动、点击、创建）
- 参数：`set_drawing_object_*` / `get_drawing_object_*`
- 清除：`clear_drawing_object`

### 3.9 Output（窗口输出）— 约 5 算子

`dump_window`（保存窗口为文件）/ `dump_window_image`（返回图像对象）/ `attach_background_to_window` / `detach_background_from_window`。

### 3.10 LUT（颜色查找表）— 约 5 算子

`set_lut` / `get_lut` / `query_lut` / `set_fixed_lut` / `get_fixed_lut` / `lut_trans` / `set_lut_style` / `disp_lut` / `map_image`。

### 3.11 Misc（杂项）— 约 10 算子

窗口事件回调、消息显示等。

---

## 4. 核心算子详解

### 4.1 `open_window` / `dev_open_window`

```hdevelop
* 编程式打开窗口（HALCON C++/C# 中）
open_window(0, 0, Width, Height, WinHandle, WindowHandle, 'visible', '')

* HDevelop 调试用（自动布局）
dev_open_window(0, 0, Width, Height, 'black', WindowHandle)
```

**关键参数**：
- `Row` / `Column`：窗口左上角在屏幕的位置
- `Width` / `Height`：宽高
- `FatherWindow`：父窗口（嵌入到主窗口时）
- `'visible'` / `'invisible'` / `'buffer'`：显示模式
- `Background`：背景色

### 4.2 `disp_rectangle1` / `disp_rectangle2`

```hdevelop
set_color(WindowHandle, 'red')
disp_rectangle1(WindowHandle, Row1, Column1, Row2, Column2)  * 轴对齐
disp_rectangle2(WindowHandle, Row, Column, Phi, Length1, Length2)  * 任意角度
```

**注意**：`Length1`/`Length2` 是半长，不是全长。`disp_*` 只画图形，不修改底层 region；适合调试时叠加显示。

### 4.3 `disp_arrow`

```hdevelop
disp_arrow(WindowHandle, Row1, Column1, Row2, Column2, ArrowSize)
* ArrowSize 默认 2，越大箭头越粗
```

### 4.4 `disp_cross`

```hdevelop
disp_cross(WindowHandle, Row, Column, Size, 0)
* 0 = '+'，1 = 'x'，2 = '+'（带框）
```

### 4.5 `disp_text`（最常用的文字显示）

```hdevelop
disp_text(WindowHandle, 'NG: 3 defects', 'window', 12, 12, 'red', [], [])
```

**参数详解**：
- `CoordSystem`：`'window'`（相对窗口像素）/ `'image'`（相对图像坐标，跨缩放仍可见）
- `Row` / `Column`：位置
- `Color`：颜色
- `Box`：`['false']` / `['true']` 或 `['color', 'shade_color', 'alpha']`（带半透明背景框）
- `BoxColor`：背景框颜色

### 4.6 `set_font`

```hdevelop
set_font(WindowHandle, '-Arial-Bold-14-')
* 格式：-Family-Weight-Size-（家族-字重-大小）
query_font(WindowHandle, AvailableFonts)  * 查询可用字体
```

### 4.7 `get_string_extents` / `get_font_extents`

```hdevelop
get_string_extents(WindowHandle, 'Hello', Ascent, Descent, Width, Height)
* 用于布局计算：知道文字宽高才能精确摆放
```

### 4.8 `draw_rectangle2`（带模态版本）

```hdevelop
draw_rectangle2(WindowHandle, RowIn, ColumnIn, PhiIn, Length1In, Length2In, Row, Column, Phi, Length1, Length2)
* 用户点击拖拽，返回最终参数
* _mod 版本：传入初值，用户可调整
```

### 4.9 `draw_circle` / `draw_ellipse`

```hdevelop
draw_circle(WindowHandle, Row, Column, Radius)
draw_ellipse(WindowHandle, Row, Column, Phi, Radius1, Radius2)
```

### 4.10 `draw_polygon`

```hdevelop
draw_polygon(WindowHandle, Rows, Columns)
* 用户左键逐点添加，右键双击结束
```

### 4.11 `draw_nurbs`

```hdevelop
draw_nurbs(WindowHandle, Contour, Rows, Cols, Tangents, 'auto', 'true', Row, Column)
* NURBS 曲线绘制（高级用户交互）
```

### 4.12 `set_color` / `set_colored`

```hdevelop
set_color(WindowHandle, 'red')         * 所有后续 disp_* 用红色
set_colored(WindowHandle, 12)           * 12 种循环色（用于多目标）
```

### 4.13 `set_draw`

```hdevelop
set_draw(WindowHandle, 'margin')  * 区域只画轮廓
set_draw(WindowHandle, 'fill')    * 区域填充实心
```

### 4.14 `set_line_width`

```hdevelop
set_line_width(WindowHandle, 3)  * 3 像素宽线
```

### 4.15 `set_part`（锁定显示区域）

```hdevelop
set_part(WindowHandle, 100, 200, 500, 800)  * 只显示这个矩形区域
```

### 4.16 `create_scene_3d` + `render_scene_3d`

```hdevelop
create_scene_3d(Scene3D)
add_scene_3d_instance(Scene3D, ObjectModel3D, 'outlines', [], [])
add_scene_3d_camera(Scene3D, [0,0,-2], [0,0,0], [0,1,0], 640, 480)
render_scene_3d(WindowHandle, Scene3D)
```

### 4.17 `add_scene_3d_light`

```hdevelop
add_scene_3d_light(Scene3D, [1,1,1], 'point', [0,0,1,0,0,0,1])
* 设置光源位置、类型、姿态
```

### 4.18 `create_drawing_object_circle` + `set_drawing_object_callback`

```hdevelop
* 高级交互：可拖拽的 ROI，拖动时自动调用回调
gen_rectangle1(Rect, 100, 100, 200, 200)
create_drawing_object_circle(150, 150, 30, DrawID)
set_drawing_object_callback(DrawID, 'on_drag', 'callback_proc')
attach_drawing_object_to_window(WindowHandle, DrawID)
```

回调函数签名（独立过程）：
```hdevelop
procedure callback_proc(DrawID, WindowHandle, Row, Column)
    * 用户拖拽时被调用，可在此更新 ROI
endproc
```

### 4.19 `dump_window_image`

```hdevelop
dump_window_image(Image, WindowHandle)
* 把窗口内容（含所有 disp_* 叠加）抓成图像对象
* 用于报告存证
```

### 4.20 `attach_background_to_window`

```hdevelop
attach_background_to_window(WindowHandle, BackgroundImage)
* 主窗口显示：背景图 + 算法叠加结果
```

---

## 5. HDevelop 示例代码

### 示例 1：检测结果 HMI 可视化

```hdevelop
* Graphics_Detection_HMI.hdev
* 模拟 PCB 缺陷检测结果的 HMI 显示

dev_close_window()
read_image(Image, 'pcb/pcb_01')
get_image_size(Image, Width, Height)
dev_open_window(0, 0, Width, Height, 'black', WindowHandle)
dev_display(Image)

* 模拟检测结果：3 个缺陷区域
NumDefects := 3
DefectRows := [120, 340, 510]
DefectCols := [200, 450, 600]
DefectTypes := ['Missing', 'Short', 'Open']
DefectConfidences := [0.92, 0.87, 0.95]

* 绘制检测结果
set_color(WindowHandle, 'red')
set_line_width(WindowHandle, 2)
for i := 0 to NumDefects-1 by 1
    disp_rectangle2(WindowHandle, DefectRows[i], DefectCols[i], 0, 30, 15)
    disp_cross(WindowHandle, DefectRows[i], DefectCols[i], 12, 0)
    set_tposition(WindowHandle, DefectRows[i]-25, DefectCols[i]-40)
    write_string(WindowHandle, DefectTypes[i] + ' (' + DefectConfidences[i]$'.2f' + ')')
endfor

* 顶部统计信息
set_color(WindowHandle, 'yellow')
set_tposition(WindowHandle, 12, 12)
write_string(WindowHandle, 'Total: ' + NumDefects + ' | FAIL')
disp_arrow(WindowHandle, 600, 50, 700, 150, 2)
```

### 示例 2：用户交互标注工具

```hdevelop
* Graphics_Draw_Tool.hdev
* 让用户用鼠标画矩形 ROI

dev_close_window()
read_image(Image, 'fabrik')
get_image_size(Image, Width, Height)
dev_open_window(0, 0, Width/2, Height/2, 'black', WindowHandle)
dev_display(Image)

set_color(WindowHandle, 'green')
set_line_width(WindowHandle, 2)

* 画 3 个矩形
for i := 1 to 3 by 1
    draw_rectangle1(WindowHandle, Row1, Column1, Row2, Column2)
    * 高亮显示
    disp_rectangle1(WindowHandle, Row1, Column1, Row2, Column2)
    * 询问用户确认（点击继续）
    get_mbutton(WindowHandle, Button, Row, Column)
endfor

* 画多边形（不规则 ROI）
set_color(WindowHandle, 'cyan')
draw_polygon(WindowHandle, Rows, Columns)
disp_polygon(WindowHandle, Rows, Columns)
```

### 示例 3：3D 点云 + 抓取位姿可视化

```hdevelop
* Graphics_3D_Scene.hdev
* 创建 3D 场景显示工件 + 抓取位姿箭头

dev_close_window()
read_object_model_3d('pipe wrench', 'mm', [], [], ObjectModel3D, Status)

* 创建 OpenGL 窗口（必须 set_window_type('opengl')）
dev_open_window(0, 0, 640, 480, 'black', WindowHandle)
set_window_type(WindowHandle, 'opengl')

* 场景
create_scene_3d(Scene3D)

* 添加工件
add_scene_3d_instance(Scene3D, ObjectModel3D, [], [], [])
set_scene_3d_instance_pose(Scene3D, 0, [0,0,0,0,0,0,0])

* 添加光源
add_scene_3d_light(Scene3D, [1,1,1], 'point', [0,0,1,0,0,0,1])
add_scene_3d_light(Scene3D, [-1,-1,-1], 'point', [0,0,-1,0,0,0,1])

* 添加相机
add_scene_3d_camera(Scene3D, [0,0,-3], [0,0,0], [0,1,0], 640, 480)

* 渲染
render_scene_3d(WindowHandle, Scene3D)
```

### 示例 4：Drawing Object 交互式 ROI

```hdevelop
* Graphics_Drawing_Object.hdev
* 创建可拖拽的 ROI，拖动时自动更新底层 region

dev_close_window()
read_image(Image, 'mreut')
get_image_size(Image, Width, Height)
dev_open_window(0, 0, Width, Height, 'black', WindowHandle)
dev_display(Image)

* 初始 ROI
Row := 300
Column := 300
Radius := 50

* 创建可拖拽的圆
create_drawing_object_circle(Row, Column, Radius, DrawID)
set_drawing_object_params(DrawID, ['color','line_width'], ['green',2])
attach_drawing_object_to_window(WindowHandle, DrawID)

* 设置回调：拖拽时实时更新底层 region
set_drawing_object_callback(DrawID, 'on_drag', 'update_roi')

* 等待用户交互（这里用 stop 模拟事件循环）
stop()

* 清理
detach_drawing_object_from_window(WindowHandle, DrawID)
clear_drawing_object(DrawID)

procedure update_roi(DrawID, WindowHandle, Row, Column)
    get_drawing_object_params(DrawID, 'radius', Radius)
    gen_circle(Circle, Row, Column, Radius)
    dev_clear_window()
    dev_display(Image)
    dev_display(Circle)
endproc
```

---

## 6. 典型工业流水线

### 流水线 A：PCB 缺陷 HMI 看板

```hdevelop
read_image(PCBImage, 'pcb_01')
find_shape_model(PCBImage, ModelID, ..., Row, Column, Angle, Score)
* 找到 IC 元件位置

threshold(PCBImage, Region, 100, 200)
connection(Region, ConnectedRegions)
select_shape(ConnectedRegions, Defects, 'area', 'and', 50, 99999)
count_obj(Defects, NumDefects)

* HMI 显示
dev_display(PCBImage)
set_color(WindowHandle, 'red')
set_line_width(WindowHandle, 2)
area_center(Defects, Area, Row, Column)  * 计算每个缺陷中心
disp_rectangle2(WindowHandle, Row, Column, 0, Area/2, Area/2)  * 按面积画框

* 文字标签
set_color(WindowHandle, 'yellow')
set_tposition(WindowHandle, 12, 12)
write_string(WindowHandle, 'NG: ' + NumDefects)

* 报告存证
dump_window_image(Screenshot, WindowHandle)
write_image(Screenshot, 'png', 0, 'report_pcb_01')
```

### 流水线 B：3D 抓取位姿审核 HMI

```hdevelop
* 加载抓取点云
xyz_to_object_model_3d(X, Y, Z, SceneOM3D)

* 创建 3D 场景
create_scene_3d(Scene3D)
add_scene_3d_instance(Scene3D, SceneOM3D, 'points', 'color', 'red')
add_scene_3d_camera(Scene3D, CamPos, Target, Up, 800, 600)

* 添加多个候选抓取位姿
for i := 0 to |GripPoses|-1 by 1
    create_pose(0, 0, 0, 0, 0, GripAngles[i], 'Rp+T', 'ordered', GripPose)
    * 用箭头表示 TCP 方向
    gen_arrow_object_model_3d(GripPose, 0.1, 0.02, 0.02, ArrowOM3D)
    add_scene_3d_instance(Scene3D, ArrowOM3D, [], [], [])
    set_scene_3d_instance_pose(Scene3D, i+1, GripPose)
endfor

render_scene_3d(WindowHandle, Scene3D)
```

---

## 7. 常见陷阱与最佳实践

### 陷阱 1：`set_color` vs `set_colored` 混用

```hdevelop
set_color(WindowHandle, 'red')  * 后续所有 disp_* 都用红色
* ...
set_colored(WindowHandle, 12)   * 切换到 12 色循环（不同区域不同颜色）
* 多目标场景必须用 set_colored(N)
```

### 陷阱 2：`set_draw('margin')` vs `'fill'` 视觉差异

- `'margin'`：只画区域轮廓，便于看底层图像。
- `'fill'`：实心填充，遮盖底层。当叠加图像时容易"看不见"目标，需谨慎。

### 陷阱 3：`disp_text` 的坐标系混淆

```hdevelop
disp_text(WindowHandle, 'NG', 'window', 12, 12, 'red', [], [])  * 像素坐标
disp_text(WindowHandle, 'NG', 'image', 100, 200, 'red', [], [])  * 图像坐标
* 切换缩放时，'window' 位置不动，'image' 跟随缩放
```

### 陷阱 4：字体大小在不同 DPI 下表现不一

- 高 DPI 屏幕下 `set_font(...'-14-')` 看起来偏小。
- 解决：查询 `query_font` 看实际可用字体；用 `get_string_extents` 自适应布局。

### 陷阱 5：`draw_*` 阻塞调用会卡死程序

`draw_*` 算子会同步阻塞等待用户输入——如果忘了让用户点击，按下"Stop"前程序会一直挂起。生产环境应改用 Drawing Objects（事件驱动）。

### 陷阱 6：多窗口 `attach_background_to_window` 后渲染顺序

- 背景窗口先渲染 → 前景窗口叠加。
- `dev_display` 在前景窗口时不会影响背景（互不干扰）。

### 陷阱 7：3D 场景渲染速度

- `render_scene_3d` 是 GPU 加速的 OpenGL 调用，但每次修改 `add_scene_3d_instance` 都需重新渲染。
- 大点云（> 1M 点）建议先 `sample_object_model_3d` 降采样。

### 陷阱 8：Drawing Object 回调中调用耗时长算子会卡顿

回调函数（`on_drag`、`on_click` 等）应只做轻量操作（如更新变量、画图）。如需复杂计算，把数据存到全局变量中，由主线程读取。

---

## 8. 参数调优指南

### 8.1 显示性能优化

| 场景 | 推荐做法 |
|------|---------|
| 高频更新（> 30 Hz） | 用 `set_part` 缩小显示区域；用 `set_line_width(1)` |
| 大量文字 | 用 `disp_text` 一次性多行（数组参数），而非多次单行 |
| 3D 大场景 | 用 `set_scene_3d_param(..., 'quality', 'low')`；减少点数 |
| 多窗口 | 用 `attach_background_to_window` 复用底层 |

### 8.2 文字与字体

| 参数 | 推荐值 | 说明 |
|------|--------|------|
| 字体家族 | `-Arial-`、`-Courier-` | 跨平台稳定 |
| 大小 | `14–18` | 调试用 14，HMI 用 16–24 |
| 字重 | `Bold` | 关键信息加粗 |

### 8.3 颜色方案

- 单目标：`set_color('red')`
- 多目标：`set_colored(6)` 或 `set_colored(12)`（HALCON 自动循环 12 种对比色）
- 严重程度分级：`red` (NG) / `yellow` (Warning) / `green` (OK)
- 透明叠加：`set_rgba(WindowHandle, 255, 0, 0, 128)`

---

## 9. 相关分类

- **Develop**：HDevelop IDE 专用，所有 `dev_*` 都是 Graphics 在 IDE 中的快捷方式。
- **Image / Regions / XLD**：被显示的数据源。
- **Tuple**：文字拼接、数值格式化（`tuple_string`、`tuple_chr`）。
- **System**：`set_system` 控制底层图形系统（如 OpenGL 启用）。
- **3D Object Model**：`disp_object_model_3d` / `render_object_model_3d` 显示 3D 数据。
- **File**：`dump_window_image` 输出的存证归 File 分类。

---

## 10. 学习小结

Graphics 是"看得见的部分"，但常被低估。它的核心价值在于：

1. **调试效率**：`disp_*` 叠加原图 → 一眼看算法哪里出问题，比 `inspect_ctrl` 直观。
2. **HMI 集成**：所有客户看到的看板都是 Graphics。
3. **用户交互**：`draw_*` / Drawing Objects 实现"傻瓜式"标注工具。
4. **3D 可视化**：`scene_3d` 系列是 3D 项目必备。

**学习路径建议**：
- **第 1 周**：掌握 `dev_open_window` + `disp_image` + `set_color` + `disp_rectangle2` + `disp_arrow` + `disp_text`（调试六件套）。
- **第 2 周**：学 `draw_*` 系列 + Drawing Objects，写一个标注工具。
- **第 3 周**：学 3D 场景，结合 3D Object Model 项目实战。
- **持续**：HMI 项目中根据客户需求加交互（鼠标拖拽、滑块、按钮）。

记住：**好的可视化 = 90% 项目成功**。HALCON 算法再强，工程师看不懂结果 = 失败。
