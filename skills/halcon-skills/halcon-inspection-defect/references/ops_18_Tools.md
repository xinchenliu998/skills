# HALCON 算子分类详解：Tools（通用工具）

> **HALCON 版本**：26.05.0.0 Progress
> **算子数量**：约 90 个
> **一级分类目录**：`toc_tools.html`
> **学习层级**：L1–L2（杂而精，按需查阅）

---

## 1. 概述

Tools 分类是 HALCON 的"**瑞士军刀**"——把一些不能归入主线分类（图像/区域/XLD/匹配等）但又广泛使用的通用工具收纳在一起。它包含 9 大子分类：

1. **Background Estimator（背景估计）**：从图像序列估计静态背景（监控、产线空闲状态）。
2. **Function（1D 函数处理）**：1D 信号处理（波形、边缘轮廓的函数化处理）。
3. **Geometry（几何运算）**：点/线/圆的距离、交点、角度。
4. **Grid Rectification（网格校正）**：棋盘格/文档校正。
5. **Hough（霍夫变换）**：圆/直线检测（备用算法）。
6. **Interpolation（散点插值）**：从散点生成连续图（深度图修复、采样）。
7. **Lines（线扫描处理）**：线扫描相机图像拼接。
8. **Mosaicking（图像镶嵌）**：多图拼接成大图。
9. **Misc（杂项）**：其他工具。

Tools 子分类的共同特点是**"按需查阅"**——每种子工具都有明确的适用场景，但都不需要长期深入学习。

---

## 2. 应用场景

### 场景 1：监控视频背景提取（安防/产线空闲检测）

固定相机拍摄产线空闲时段 → **Background Estimator** 估计静态背景 → 当有产品通过时差分即可识别 → 用于"异常停留"、"工人闯入"等检测。

### 场景 2：一维边缘轮廓函数化（橡胶密封圈截面分析）

相机拍橡胶截面 → `gen_measure_rectangle2` 沿轮廓提取边缘 → 灰度序列转 1D 函数 → **`funct_1d_*`** 平滑、求导、找峰谷 → 输出截面尺寸。

### 场景 3：圆孔/直线几何测量（机械零件）

需要在没有 1D Measuring 卡尺的场景下检测圆/直线 → **`hough_circles`** / **`hough_lines`** 快速找到大致位置 → 配合 `gen_measure_*` 精确测量。

### 场景 4：超大视场拼接（卫星图、PCB AOI、墙纸印刷）

单相机视场有限 → 多张图依次拍摄 + 重叠区 → **`gen_projective_mosaic`** + **`adjust_mosaic_images`** 拼接成大图 → 后续整图分析。

### 场景 5：散点数据可视化（3D 重建中间步骤）

双目视觉生成稀疏视差点云 → **`interpolate_scattered_data_image`** 插值成连续深度图 → 便于图像化处理。

### 场景 6：文档扫描矫正

手机拍照文档 → 文档有透视畸变 → **`create_rectification_grid`** + **`gen_grid_rectification_map`** 自动校正成正面矩形。

---

## 3. 子分类详解

### 3.1 Background Estimator（背景估计）— 约 8 算子

| 算子 | 用途 |
|------|------|
| `create_bg_esti` | 创建背景估计模型 |
| `close_bg_esti` | 关闭 |
| `run_bg_esti` | 用单帧更新背景估计 |
| `update_bg_esti` | 增量更新 |
| `give_bg_esti` | 拿当前估计的背景图 |
| `set_bg_esti_params` | 设置参数（如学习率） |
| `get_bg_esti_params` | 查询参数 |
| `read/write_bg_esti` | 保存/读取 |

**关键参数**：
- `'learning_rate'`：背景更新速度（0–1，越大越快适应变化）
- `'min_diff'`：判定为"前景"的最小差异

### 3.2 Function（1D 函数）— 约 20 算子

| 类别 | 算子 |
|------|------|
| **创建** | `create_funct_1d_pairs`、`create_funct_1d_array` |
| **访问** | `funct_1d_to_pairs`、`x_range_funct_1d`、`y_range_funct_1d`、`get_pair_funct_1d`、`get_y_value_funct_1d`、`distance_funct_1d` |
| **变换** | `sample_funct_1d`、`transform_funct_1d`、`scale_y_funct_1d`、`invert_funct_1d`、`negate_funct_1d`、`compose_funct_1d` |
| **平滑** | `smooth_funct_1d_gauss`、`smooth_funct_1d_mean`、`smooth_funct_1d_deriv_gauss` |
| **导数/积分** | `derivate_funct_1d`、`integrate_funct_1d` |
| **特征** | `local_min_max_funct_1d`、`zero_crossings_funct_1d` |
| **匹配** | `match_funct_1d_trans`（平移匹配）|
| **文件** | `read_funct_1d`、`write_funct_1d` |

### 3.3 Geometry（几何运算）— 约 25 算子

| 类型 | 算子 |
|------|------|
| **距离** | `distance_pp`（点-点）、`distance_pl`（点-线）、`distance_ps`（点-段）、`distance_lr`（线-线）、`distance_cc`（圆-圆）、`distance_sc`（段-圆）、`distance_sr`（段-矩形）、`distance_ss`（段-段）、`distance_pr`（点-矩形） |
| **角度** | `angle_ll`（线-线）、`angle_lx`（线-XLD）|
| **最小值** | `distance_cc_min`（圆-圆最小距离）、`distance_lr_min`（线-线最短距离）|
| **交点** | `intersection_lines`、`intersection_line_circle`、`intersection_line_contour_xld`、`intersection_circle_circle`、`intersection_contours_xld`、`intersection_segment_line`、`intersection_segment_contour_xld` |
| **投影** | `projection_pl`（点投影到线） |
| **XLD 几何** | `smallest_circle_xld`、`smallest_rectangle1_xld`、`smallest_rectangle2_xld` |

### 3.4 Grid Rectification（网格校正）— 约 5 算子

| 算子 | 用途 |
|------|------|
| `create_rectification_grid` | 创建校正网格描述符 |
| `find_rectification_grid` | 在图像中找到网格 |
| `gen_grid_rectification_map` | 生成校正映射 |
| `map_image` | 应用映射校正图像 |
| `apply_bead_inspection_model` | （无关）|

**典型应用**：棋盘格文档校正、手机拍的 A4 纸正面化。

### 3.5 Hough（霍夫变换）— 约 6 算子

| 算子 | 用途 |
|------|------|
| `hough_circles` | Hough 圆检测（Region 输入） |
| `hough_circle_trans` | Hough 圆检测（XLD 输入） |
| `hough_lines` | Hough 直线检测（Region 输入） |
| `hough_line_trans` | Hough 直线检测（XLD 输入） |
| `hough_lines_dir` | 带方向的直线检测 |
| `hough_line_trans_dir` | 带方向的直线（XLD） |

**注意**：Hough 变换在 HALCON 中是**备用方案**——优先用 `edges_sub_pix` + `fit_*_contour_xld`，因为精度更高。Hough 用于"快速粗定位"。

### 3.6 Interpolation（散点插值）— 约 8 算子

| 算子 | 用途 |
|------|------|
| `interpolate_scattered_data` | 基础散点插值（1D/2D/3D） |
| `interpolate_scattered_data_image` | 散点 → 图像（带 Value 字段） |
| `interpolate_scattered_data_points_to_image` | 散点 → 像素图（带 Value） |
| `harmonic_interpolation` | 调和插值（带边界约束） |
| `create_scattered_data_interpolator` | 创建插值器（可复用） |
| `clear_scattered_data_interpolator` | 清除 |
| `interpolate_scattered_data_algo` | 插值算法选择 |
| `set_scattered_data_interpolator_param` | 参数 |

**典型应用**：稀疏 3D 点云 → 深度图、缺失像素修复。

### 3.7 Lines（线扫描处理）— 约 5 算子

| 算子 | 用途 |
|------|------|
| `partition_lines` | 按属性拆分线段 |
| `select_lines` | 按属性选线 |
| `select_lines_longest` | 选最长 N 条线 |
| `merge_regions_line_scan` | 线扫描多帧区域合并 |
| `info_parallels_xld` / `max_parallels_xld` / `mod_parallels_xld` | XLD 平行线操作 |

### 3.8 Mosaicking（图像镶嵌）— 约 8 算子

| 算子 | 用途 |
|------|------|
| `gen_projective_mosaic` | 生成投影镶嵌（最常用） |
| `gen_bundle_adjusted_mosaic` | 生成光束法平差镶嵌（精度最高） |
| `gen_spherical_mosaic` | 球面镶嵌（360° 拼接） |
| `gen_cube_map_mosaic` | 立方体贴图镶嵌（VR） |
| `adjust_mosaic_images` | 调整镶嵌图（修正单张偏移） |
| `bundle_adjust_mosaic` | 光束法平差（全局优化） |
| `tile_images_offset` | 按偏移拼图（无变换） |
| `image_to_world_plane` | 像素坐标 → 世界坐标（基础操作） |

### 3.9 Misc（杂项）— 约 5 算子

如 `poursnow`（雪花特效演示）等小工具。

---

## 4. 核心算子详解

### 4.1 `create_bg_esti` + `run_bg_esti`

```hdevelop
* 创建背景估计器
create_bg_esti(Width, Height, 'fixed', 0.02, 'on', BgEstiHandle)
* 'fixed'：固定学习率
* 0.02：学习率（每帧更新 2%）
* 'on'：开启自动估计

* 喂多帧空场景（产线空闲）
for i := 1 to 30 by 1
    grab_image(Img, AcqHandle)
    run_bg_esti(Img, BgEstiHandle)
endfor

* 拿估计的背景
give_bg_esti(BgImage, BgEstiHandle)

* 之后每帧用 abs_diff_image 检前景
abs_diff_image(LiveImg, BgImage, Diff, 1)
threshold(Diff, Foreground, 30, 255)
```

### 4.2 `create_funct_1d_pairs`

```hdevelop
* 把 X / Y 数组转成 1D 函数对象
X := [0.0, 1.0, 2.0, 3.0, 4.0]
Y := [0.0, 1.0, 4.0, 9.0, 16.0]
create_funct_1d_pairs(X, Y, Function)

* 高斯平滑
smooth_funct_1d_gauss(Function, Sigma, Smoothed)

* 求导
derivate_funct_1d(Smoothed, 'first', Derivative)

* 找局部极值
local_min_max_funct_1d(Smoothed, 'strict_min_min', Minima, Maxima)
```

### 4.3 `smooth_funct_1d_gauss` / `smooth_funct_1d_mean`

```hdevelop
smooth_funct_1d_gauss(Function, 2.0, Smoothed)
* Sigma = 2.0：高斯核半径
```

### 4.4 `derivate_funct_1d`

```hdevelop
derivate_funct_1d(Function, 'first', FirstDeriv)
derivate_funct_1d(Function, 'second', SecondDeriv)
* 'first' / 'second'
```

### 4.5 `integrate_funct_1d`

```hdevelop
integrate_funct_1d(Function, 'positive', 'zero', Integral)
* 计算曲线下面积
```

### 4.6 `distance_pp` / `distance_pl` / `distance_ps`

```hdevelop
* 点-点
distance_pp(Row1, Col1, Row2, Col2, Dist)

* 点-直线
RowLStart := 0; ColLStart := 0; RowLEnd := 100; ColLEnd := 100
distance_pl(Row, Col, RowLStart, ColLStart, RowLEnd, ColLEnd, Dist)

* 点-线段
distance_ps(Row, Col, RowS, ColS, RowE, ColE, Dist)
```

### 4.7 `angle_ll`

```hdevelop
* 两条线的角度（弧度，[-π, π]）
angle_ll(RowL1Start, ColL1Start, RowL1End, ColL1End, RowL2Start, ColL2Start, RowL2End, ColL2End, Angle)
```

### 4.8 `intersection_lines`

```hdevelop
* 两条直线交点
intersection_lines(RowL1Start, ColL1Start, RowL1End, ColL1End, RowL2Start, ColL2Start, RowL2End, ColL2End, Row, Col, IsParallel)
* IsParallel = TRUE 时两条线平行（无交点）
```

### 4.9 `hough_circles`

```hdevelop
* 输入：Region（如 edges_image 的输出）
* 输出：圆心 (Row, Col) + 半径 Radius
hough_circles(EdgeRegion, HoughImage, 30, 100, 10, Row, Col, Radius)
* 参数：最小/最大半径、累加器阈值
```

### 4.10 `hough_lines`

```hdevelop
hough_lines(EdgeRegion, HoughImage, 5, 50, 5, Angle, Dist)
* Angle：直线的法向角度
* Dist：从原点到直线的距离
```

### 4.11 `interpolate_scattered_data_image`

```hdevelop
* 把 (Row, Col, Value) 散点 → 图像
interpolate_scattered_data_image(Rows, Cols, Values, 'bicubic', [], [], Width, Height, Image)
* 第二个参数为插值方法：'nearest' / 'bilinear' / 'bicubic'
```

### 4.12 `harmonic_interpolation`

```hdevelop
* 带边界约束的调和插值（适合深度图修复）
harmonic_interpolation(Image, MaskRegion, Iterations, Smoothness, Result)
* Iterations：迭代次数（默认 100）
* Smoothness：平滑度
```

### 4.13 `gen_projective_mosaic`

```hdevelop
* 多图镶嵌成大图
gen_projective_mosaic(Image, MosaicImage, StartRow, StartCol, [], [], [], [], MosaicMat2D)
* Image：当前帧
* MosaicImage：累积的镶嵌结果
* MosaicMat2D：当前帧到世界坐标的投影矩阵
```

### 4.14 `adjust_mosaic_images`

```hdevelop
* 调整镶嵌中的单张图（修正偏移）
adjust_mosaic_images(Images, MosaicImage, HomMatrices, AdjustedImages)
```

### 4.15 `tile_images_offset`

```hdevelop
* 按指定偏移拼图（无变换）
tile_images_offset(Images, TiledImage, OffsetRow, OffsetCol, [], [], [], [], [])
```

### 4.16 `image_to_world_plane`

```hdevelop
* 把整张图变换到世界平面（消除透视畸变）
image_to_world_plane(Image, WorldImage, CameraParam, WorldPose, Width, Height, Scale, Interpolation)
```

### 4.17 `partition_lines`

```hdevelop
* 按长度/曲率拆分线段
partition_lines(Contour, PartContours, 'distance', MinLength)
```

### 4.18 `merge_regions_line_scan`

```hdevelop
* 线扫描相机的多帧区域合并
merge_regions_line_scan(Regions, ImageHeight, ImageWidth, MergedRegions)
```

---

## 5. HDevelop 示例代码

### 示例 1：背景估计（产线空闲检测）

```hdevelop
* Tools_Background_Estimator.hdev
* 学习产线空闲背景，检测停留物

dev_close_window()
open_framegrabber('File', 1, 1, 0, 0, 0, 0, 'default', -1, 'default', -1, 'default', 'raw_image', -1, -1, AcqHandle)
grab_image_size(AcqHandle, Width, Height)
dev_open_window(0, 0, Width, Height, 'black', WindowHandle)

* 创建背景估计器（学习率 0.02）
create_bg_esti(Width, Height, 'fixed', 0.02, 'on', BgEsti)

* 学习 30 帧空场景
for i := 1 to 30 by 1
    grab_image_async(Img, AcqHandle, -1)
    run_bg_esti(Img, BgEsti)
endfor

* 拿背景
give_bg_esti(Bg, BgEsti)

* 实时差分
while (true)
    grab_image_async(Img, AcqHandle, -1)
    abs_diff_image(Img, Bg, Diff, 1)
    threshold(Diff, FG, 30, 255)
    connection(FG, FGConn)
    select_shape(FGConn, FGSel, 'area', 'and', 500, 999999)
    
    dev_clear_window()
    dev_display(Img)
    dev_display(FGSel)
    
    count_obj(FGSel, Num)
    disp_text(WindowHandle, 'Foreground: ' + Num, 'window', 12, 12, 'red', 'box', 'black')
endwhile
```

### 示例 2：1D 信号处理（边缘轮廓分析）

```hdevelop
* Tools_1D_Function.hdev
* 提取图像中的灰度序列，做 1D 信号处理

* 创建测试图：黑底白条
gen_image_const(Image, 'byte', 256, 512)
gen_rectangle1(Rect, 100, 100, 150, 400)
paint_region(Rect, Image, Image, 255, 'fill')

* 提取第 256 列的灰度序列作为 1D 函数
Rows := [0:255]
Cols := gen_tuple_const(256, 256)
get_grayval(Image, Rows, Cols, GrayValues)

* 转为 1D 函数
create_funct_1d_pairs(tuple_real(Rows), tuple_real(GrayValues), Function)

* 高斯平滑
smooth_funct_1d_gauss(Function, 3.0, Smoothed)

* 求导（找边缘）
derivate_funct_1d(Smoothed, 'first', Derivative)

* 找极值（边缘位置）
local_min_max_funct_1d(Smoothed, 'strict_min', MinPos, MaxPos)
* MinPos 是白条上下边缘位置

* 可视化
dev_clear_window()
plot_funct_1d(WindowHandle, Smoothed, [], 'green', ['x_axis','y_axis'])
```

### 示例 3：Hough 圆检测（备份方案）

```hdevelop
* Tools_Hough_Circles.hdev
* 用 Hough 找硬币（备用方案，主要还是推荐 1D Measuring）

read_image(Image, 'coins')
* 预处理
gauss_filter(Image, ImageGauss, 5)
* 边缘
edges_sub_pix(ImageGauss, Edges, 'canny', 1, 20, 40)
* 转 Region（hough_circles 要 Region 输入）
gen_region_contour_xld(Edges, EdgeRegion, 'filled')

* Hough 圆检测
hough_circles(EdgeRegion, HoughSpace, 30, 60, 12, Rows, Cols, Radii)

* 可视化
dev_clear_window()
dev_display(Image)
for i := 0 to |Rows|-1 by 1
    gen_circle(Circle, Rows[i], Cols[i], Radii[i])
    dev_display(Circle)
endfor
```

### 示例 4：超大图镶嵌（Mosaicking）

```hdevelop
* Tools_Mosaicking.hdev
* 把多张小图拼接成大图（无相机标定场景）

* 加载 5 张有重叠的图
gen_empty_obj(Images)
for i := 1 to 5 by 1
    read_image(Img, 'mosaic/part_' + i$'.2')
    concat_obj(Images, Img, Images)
endfor

* 简单拼图（无变换，按偏移）
OffsetRows := [0, 0, 100, 200, 300]
OffsetCols := [0, 200, 100, 0, 100]
tile_images_offset(Images, Tiled, OffsetRows, OffsetCols, [], [], [], [], [])

dev_clear_window()
dev_display(Tiled)

* 高级：自动估算偏移（gen_projective_mosaic）
* 自动从图像重叠区估计单应性矩阵
gen_projective_mosaic(Image1, MosaicImage1, 0, 0, [], [], [], [], HomMat1)
for i := 2 to 5 by 1
    select_obj(Images, ImageI, i)
    gen_projective_mosaic(ImageI, MosaicImage1, 0, 0, [], [], HomMat1, [], HomMatI)
endfor
```

### 示例 5：散点 → 深度图（Interpolation）

```hdevelop
* Tools_Scattered_Interpolation.hdev
* 把稀疏视差点云插值为连续深度图

* 模拟散点：每个 (Row, Col) 有个深度值
NumPoints := 1000
tuple_rand(2 * NumPoints, Rand)
Rows := Rand[0:NumPoints-1] * 256
Cols := Rand[NumPoints:2*NumPoints-1] * 256
Values := sin(Rows / 50.0) + cos(Cols / 50.0)  * 50 + 128  * (合成深度)

* 插值成图像
interpolate_scattered_data_image(Rows, Cols, Values, 'bicubic', [], [], 256, 256, DepthImage)

dev_clear_window()
dev_display(DepthImage)
```

---

## 6. 典型工业流水线

### 流水线 A：PCB AOI 大图拼接（Mosaicking）

```hdevelop
* 多个视野拍摄 PCB 各区域，拼接成完整 PCB 图

gen_empty_obj(PCBTiles)
TileCount := 16
for i := 1 to TileCount by 1
    read_image(Tile, 'pcb_tile_' + i$'.2')
    concat_obj(PCBTiles, Tile, PCBTiles)
endfor

* 简单按行列拼图（无变换）
RowsPerCol := 4
ColsPerRow := 4
OffsetRows := []
OffsetCols := []
for r := 0 to RowsPerCol-1 by 1
    for c := 0 to ColsPerRow-1 by 1
        OffsetRows := [OffsetRows, r * 500]
        OffsetCols := [OffsetCols, c * 500]
    endfor
endfor

tile_images_offset(PCBTiles, PCBFull, OffsetRows, OffsetCols, [], [], [], [], [])

* 后续整图分析
* find_shape_model(PCBFull, ...)
```

### 流水线 B：监控视频分析（Background Estimator）

```hdevelop
* 见示例 1
* 关键：背景更新速度（learning_rate）匹配场景变化速度
```

### 流水线 C：橡胶密封圈截面 1D 分析

```hdevelop
* 沿密封圈截面提取灰度轮廓
gen_measure_rectangle2(MeasRow, MeasCol, MeasPhi, 100, 5, 5, Width, Height, 'bilinear', MeasureHandle)

* 提取轮廓点
measure_pairs(Image, MeasureHandle, 1.0, 30, 'all', 'all', RowE1, ColE1, Amp1, RowE2, ColE2, Amp2, IntraDist, InterDist)

* 把轮廓点作为 1D 函数
Distances := sqrt((RowE1 - RowE2)^2 + (ColE1 - ColE2)^2)
Position := tuple_cumul(0.0 || IntraDist[0:(|IntraDist|-2)])

create_funct_1d_pairs(Position, Distances, WidthFunc)

* 平滑 + 求导 → 分析密封圈尺寸
smooth_funct_1d_gauss(WidthFunc, 5.0, Smoothed)
local_min_max_funct_1d(Smoothed, 'strict_min_min', Bottoms, Tops)
```

---

## 7. 常见陷阱与最佳实践

### 陷阱 1：背景估计学习率选择

- 学习率太高：背景更新过快 → 静止前景物（如停留产品）会被"吸收"为背景。
- 学习率太低：背景适应慢 → 光照变化会误检为前景。

**最佳实践**：学习率初值 0.02（保守），现场根据实际调整。产线空闲时段用 0 学习率（手动触发）。

### 陷阱 2：Hough 检测精度低

Hough 变换的精度受累加器分辨率限制，通常 ±2-5 px。对高精度场景用 `edges_sub_pix` + `fit_circle_contour_xld`。

### 陷阱 3：`gen_projective_mosaic` 需要图像有足够重叠

投影镶嵌依赖图像间特征匹配。重叠区域必须 > 30%，否则匹配失败。

**最佳实践**：拍摄时保证 50%+ 重叠，或加标记点（fiducial）。

### 陷阱 4：散点插值在数据缺失区域行为

`interpolate_scattered_data_image` 在数据稀疏区域会做外推，可能出现明显伪影。

**最佳实践**：插值后用 `mask` 标记未覆盖区域，或结合 `harmonic_interpolation` 加约束。

### 陷阱 5：1D 函数操作在不等距采样下失真

如果 X 值不是等距（如 `0, 1, 2, 5, 10`），平滑和求导会失真。

**最佳实践**：用 `sample_funct_1d` 重采样为等距 X。

### 陷阱 6：`tile_images_offset` 只能拼轴对齐图

如果图像间有旋转，必须用 `gen_projective_mosaic` 而非 `tile_images_offset`。

### 陷阱 7：`distance_*` 的输入约定混淆

`distance_pl` 的线是无限延伸直线，`distance_ps` 的线是有限段。两者结果在点离线段延长线时差异显著。

### 陷阱 8：`image_to_world_plane` 的 Width/Height 是输出图像尺寸

不是输入图像尺寸！它由 `Width, Height` 参数决定。常见错误：写成原图大小导致输出图被裁剪。

---

## 8. 参数调优指南

### 8.1 Background Estimator

| 参数 | 推荐值 | 说明 |
|------|--------|------|
| `learning_rate` | 0.01–0.05 | 慢场景 0.01；快变化 0.05 |
| `min_diff` | 20–50 | 越小越敏感 |
| `'threshold'` | 30 | 差分阈值 |

### 8.2 Hough

| 参数 | 推荐值 | 说明 |
|------|--------|------|
| 累加器阈值 | 5–20 | 越大抑制假阳，但漏检增加 |
| 角度分辨率 | 0.5° | 默认够用 |
| 半径范围 | 真实 ±20% | 缩小可提速 |

### 8.3 Mosaicking

| 参数 | 推荐值 | 说明 |
|------|--------|------|
| 重叠率 | 50%+ | 太低匹配失败 |
| `bundle_adjust_mosaic` | 永远开启 | 全局优化精度提升 30% |

### 8.4 1D Function

| 参数 | 推荐值 | 说明 |
|------|--------|------|
| `Sigma`（高斯平滑） | 1–5 | 越大越平滑 |
| 插值方法 | `'bicubic'` | 精度高；`'nearest'` 速度 |

---

## 9. 相关分类

- **Image**：散点插值的输出是图像。
- **Region / XLD**：Hough 检测输入来自 Region/XLD。
- **Calibration**：`image_to_world_plane` 依赖相机标定。
- **1D Measuring**：1D Function 与卡尺测量结果集成。
- **Develop**：`dev_disp_text` 是 Mosaicking 调试常用工具。

---

## 10. 学习小结

Tools 是"**按需查阅**"的分类——不要试图全部记忆，按场景需要时再查：

1. **Background Estimator**：监控视频、产线空闲检测 → 必学。
2. **1D Function**：边缘轮廓、灰度序列信号处理 → 按需学。
3. **Geometry**：点线圆距离、交点 → 测量项目常用。
4. **Hough**：备用方案（精度不如 fit_*） → 了解即可。
5. **Interpolation**：3D 重建、深度图修复 → 按需学。
6. **Mosaicking**：超大图拼接 → 学一次即可。
7. **Grid Rectification**：文档校正 → 学一次即可。

**学习路径建议**：
- **第 1 周**：背景估计（监控/空闲检测项目）。
- **第 2 周**：1D Function（橡胶/密封圈截面分析）。
- **第 3 周**：Geometry + Mosaicking。
- **持续**：其他按需查阅。

**核心心法**：
1. **优先用专业分类算子**：Hough < fit_circle_contour；Background Estimator < 一致的固定背景方案。
2. **Tools 是"瑞士军刀"**：日常挂在腰上，但绝大多数时候用不到。
3. **小项目组合大威力**：背景估计 + 几何 + 1D Function 三个工具就能做很多创新项目。
4. **不要重复造轮子**：Tools 已经封装好通用方法，直接用即可。
