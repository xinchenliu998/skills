# HALCON 算子分类详解：1D Measuring（一维卡尺）

> **分类定位**：简单边缘对距离、边缘位置、毫米级测量——HALCON 经典卡尺工具。
> **算子数量**：约 20 个。
> **HALCON 版本**：26.05.0.0 Progress
> **官方文档**：`toc_1dmeasuring.html`

---

## 1. 概述

1D Measuring 是 HALCON 历史最悠久的测量工具集，基于"一维卡尺"原理：
- 在图像上指定一条**测量矩形**（卡尺 ROI）
- 沿矩形长边方向扫描像素灰度
- 提取边缘（基于灰度梯度）
- 返回边缘位置和距离

适合**简单边缘对**（如引脚宽度、零件对边距离、台阶高度）测量，速度快、精度高。

### 与 2D Metrology 对比

| 维度 | 1D Measuring | 2D Metrology |
|------|--------------|---------------|
| ROI | 一维矩形 | 二维任意形状 |
| 几何复杂度 | 边/对边 | 圆/矩形/椭圆/通用 |
| 多对象 | 手动循环 | 自动批量 |
| 速度 | 极快 | 中等 |
| 适用 | 简单边缘对 | 复杂尺寸 |

---

## 2. 应用场景

| 场景 | 说明 |
|------|------|
| **IC 引脚间距** | `measure_pairs` 一次拿两脚距离 |
| **零件对边距离** | 卡尺 + `distance_*` |
| **台阶高度** | 阈值法 `measure_thresh` |
| **多边形角点** | 循环 `measure_pos` |
| **通用距离计算** | `distance_pp` / `distance_lr` / `distance_ps` |

**典型行业**：电子（PCB/SMT 引脚）、机加工（尺寸）、通用卡尺替代。

---

## 3. 子分类详解

### 3.1 模型管理（5 算子）

- `gen_measure_rectangle2(Row, Col, Phi, L1, L2, W, H, Interp → MeasureHandle)`
- `gen_measure_arc(Row, Col, R, AStart, AEnd, W, H, Interp → MeasureHandle)`
- `translate_measure(MeasureHandle, Row, Col)` — 移动卡尺
- `close_measure(MeasureHandle)`
- `read_measure` / `write_measure`

### 3.2 测量执行（5 算子）

- `measure_pairs` — 提取**边缘对**（最常用）
- `measure_pos` — 提取**所有边缘点**
- `measure_thresh` — 提取**阈值跨越**点
- `measure_projection` — 灰度投影到一维函数
- `fuzzy_measure_pos` — 模糊测量（边缘不齐）

### 3.3 参数设置（4 算子）

- `set_measure_param` / `get_measure_param`
- `serialize_measure` / `deserialize_measure`

### 3.4 距离计算（10 算子，在 Tools / Geometry）

- `distance_pp` — 点-点
- `distance_pl` — 点-线
- `distance_pr` — 点-区域
- `distance_ps` — 点-XLD
- `distance_lr` — 线-线
- `distance_cc` — 圆-圆
- `distance_sc` — 段-圆
- `angle_ll` — 线-线夹角
- `angle_lx` — 线-XLD 夹角
- `intersection_*` — 求交点

---

## 4. 核心算子详解

### 4.1 创建测量对象（3 个）

| 算子 | 签名 | 用途 |
|------|------|------|
| `gen_measure_rectangle2` | `gen_measure_rectangle2(Row, Col, Phi, L1, L2, W, H, Interp → Handle)` | 矩形卡尺 |
| `gen_measure_arc` | `gen_measure_arc(Row, Col, R, AStart, AEnd, W, H, Interp → Handle)` | 弧形卡尺 |
| `translate_measure` | `translate_measure(Handle, Row, Col)` | 移动卡尺 |

### 4.2 测量执行（4 个）

| 算子 | 用途 |
|------|------|
| `measure_pairs` | 提取**边缘对**（亮-暗或暗-亮），返回 4 组坐标 |
| `measure_pos` | 提取**所有边缘点**，返回 1 组坐标 |
| `measure_thresh` | 提取**阈值跨越点**，返回 1 组坐标 |
| `measure_projection` | 返回一维函数（灰度投影），用于自定义分析 |

### 4.3 距离计算（6 个常用）

| 算子 | 用途 |
|------|------|
| `distance_pp` | 点-点距离 |
| `distance_pl` | 点-线距离 |
| `distance_lr` | 线-线距离 |
| `distance_ps` | 点-XLD 距离 |
| `distance_pr` | 点-区域距离 |
| `distance_cc` | 圆-圆距离 |

---

## 5. HDevelop 示例代码

### 示例 1：IC 引脚宽度测量

```hdevelop
* 读图
read_image(Image, 'ic_pins.png')
get_image_size(Image, W, H)

* 垂直卡尺（横向测引脚宽度）
gen_measure_rectangle2(256, 256, rad(0),   * 中心
                       200, 10,           * 卡尺长 200、宽 10
                       W, H, 'bilinear', MeasureHandle)

* 提取所有边缘对（亮→暗）
measure_pairs(Image, MeasureHandle, 1.0, 30, 'positive', 'all', \
              RowEdgeFirst, ColEdgeFirst, AmpFirst, \
              RowEdgeSecond, ColEdgeSecond, AmpSecond, \
              IntraDistance, InterDistance)

* 计算每个引脚的宽度
tuple_length(IntraDistance, NumPairs)
dev_disp_text('共 ' + NumPairs + ' 对边缘', 'window', 'top', 'left', 'green', [], [])

for i := 0 to NumPairs - 1 by 1
    Width := IntraDistance[i]
    dev_disp_text('引脚 ' + (i+1) + ' 宽: ' + tuple_string(Width, '$.2f'), \
                  'window', 20 + i*15, 'left', 'black', [], [])
endfor

close_measure(MeasureHandle)
```

### 示例 2：卡尺测圆孔直径

```hdevelop
read_image(Image, 'hole.png')
get_image_size(Image, W, H)

* 水平卡尺穿过圆心
gen_measure_rectangle2(256, 256, rad(0), 200, 8, W, H, 'bilinear', MHandle)

* 测量亮→暗→亮的边缘（直径）
measure_pairs(Image, MHandle, 1.0, 30, 'all', 'all', \
              R1, C1, _, R2, C2, _, _, Diameter)

* 显示
for i := 0 to |Diameter| - 1 by 1
    DiameterAvg := tuple_mean([Diameter[i]])
    dev_disp_text('孔 ' + (i+1) + ' 直径: ' + tuple_string(DiameterAvg, '$.3f'), \
                  'window', 20 + i*15, 'left', 'black', [], [])
endfor

close_measure(MHandle)
```

### 示例 3：提取所有边缘点（连续边缘）

```hdevelop
read_image(Image, 'gear.png')
get_image_size(Image, W, H)

* 沿齿轮边缘取多条卡尺
gen_measure_rectangle2(256, 256, rad(0), 200, 8, W, H, 'bilinear', MHandle)

* 提取所有边缘位置（不要求成对）
measure_pos(Image, MHandle, 1.0, 30, 'all', 'all', \
            Rows, Cols, Amps, Distances)

* 用距离信息过滤（如每 10 px 一点）
tuple_length(Rows, N)
gen_empty_obj(Contours)
for i := 0 to N - 1 by 1
    gen_contour_polygon_xld(Contour, Rows[i], Cols[i])
    concat_obj(Contours, Contour, Contours)
endfor

dev_display(Contours)
close_measure(MHandle)
```

### 示例 4：阈值法测台阶

```hdevelop
read_image(Image, 'step.png')
get_image_size(Image, W, H)

* 横向卡尺穿越台阶
gen_measure_rectangle2(256, 256, rad(90), 200, 5, W, H, 'bilinear', MHandle)

* 阈值 128 跨越位置
measure_thresh(Image, MHandle, 1.0, 128, 'all', 'all', \
               Row1, Col1, Row2, Col2)

* 计算台阶水平距离
distance_pp(0, Col1[0], 0, Col1[1], StepWidth)

* 显示
dev_set_color('red')
gen_cross_contour_xld(Cross1, Row1[0], Col1[0], 15)
gen_cross_contour_xld(Cross2, Row1[1], Col1[1], 15)
dev_display(Cross1)
dev_display(Cross2)

close_measure(MHandle)
```

### 示例 5：距离计算综合

```hdevelop
* 已知两条线 L1, L2（来自 XLD 拟合）
fit_line_contour_xld(Contour1, 'tukey', -1, 0, 5, 2, R1a, C1a, R1b, C1b)
fit_line_contour_xld(Contour2, 'tukey', -1, 0, 5, 2, R2a, C2a, R2b, C2b)

* 点到点距离
distance_pp(R1a, C1a, R2a, C2a, Dpp)

* 线到线距离
distance_lr(R1a, C1a, R1b, C1b, R2a, C2a, R2b, C2b, Dlr)

* 线到线夹角
angle_ll(R1a, C1a, R1b, C1b, R2a, C2a, R2b, C2b, Angle)

* 显示
dev_disp_text('点距=' + tuple_string(Dpp, '$.2f'), 'window', 'top', 'left', 'black', [], [])
dev_disp_text('线距=' + tuple_string(Dlr, '$.2f'), 'window', 20, 'left', 'black', [], [])
dev_disp_text('夹角=' + tuple_string(deg(Angle), '$.2f') + '°', 'window', 40, 'left', 'black', [], [])
```

---

## 6. 典型工业流水线

### 流水线 A：IC 引脚间距测量

```
read_image
   ↓
get_image_size
   ↓
gen_measure_rectangle2 (指定 ROI)
   ↓
measure_pairs (提取亮-暗-亮对)
   ↓
取 IntraDistance (对内距离 = 引脚宽度)
   ↓
取 InterDistance (对间距离 = 间距)
   ↓
close_measure
   ↓
统计/上传
```

### 流水线 B：通用尺寸测量

```
read_image
   ↓
edges_sub_pix → 提取亚像素轮廓
   ↓
fit_line_contour_xld / fit_circle_contour_xld
   ↓
distance_lr / distance_cc → 计算尺寸
   ↓
disp_* → 显示
```

---

## 7. 常见陷阱与最佳实践

1. **卡尺长度 `L1` 必须够长**：穿过目标 + 一定余量（一般目标宽 2–3 倍）。
2. **卡尺宽度 `L2`**：决定亚像素精度（5–20 px 通常足够）。
3. **`Sigma` 默认 1.0**：抗噪声；噪点多时增大到 1.5–2.0。
4. **`Threshold` 取决于对比度**：低对比度用小值（如 10）；高对比度用大值（30+）。
5. **`Transition`**：`'all'` 全方向；`'positive'` 亮→暗；`'negative'` 暗→亮。
6. **`measure_pairs` 返回 4 组坐标**：2 组暗-亮、2 组亮-暗；按对索引取 `IntraDistance[i]`。
7. **`Interpolation`**：`'bilinear'` 精确；`'nearest_neighbor'` 快。
8. **卡尺 ROI 与图像边界相交**：会自动截断，可能导致结果不准。

---

## 8. 参数调优指南

| 场景 | 建议 |
|------|------|
| 高噪声 | `Sigma=1.5–2.0` + `Threshold` 提高 |
| 边缘不齐 | 用 `fuzzy_measure_pos` 或 2D Metrology 模糊模式 |
| 高精度 | `'bilinear'` 插值 |
| 多边缘 | 用 `measure_pos` + 自定义配对逻辑 |
| 卡尺移动 | `translate_measure` 不重建（性能提升 10x） |

---

## 9. 相关分类

- **2D Metrology**：复杂尺寸测量的替代方案。
- **XLD**：`fit_circle_contour_xld` / `fit_line_contour_xld` 配合 `distance_*` 做拟合测距。
- **Tools / Geometry**：`distance_*` 距离计算全家族。

---

## 10. 学习小结

1D Measuring 是"经典卡尺测量层"。**学习优先级**：
1. **必学**：`gen_measure_rectangle2` + `measure_pairs` + `distance_pp/lr`。
2. **重要**：`measure_pos`、`measure_thresh`、`translate_measure`。
3. **专项**：`fuzzy_measure_pos`（边缘不齐）、`measure_projection`（自定义分析）。

**核心要点**：
- **`measure_pairs` 是最常用的卡尺函数**——一次拿亮-暗对的数量与距离。
- **`Sigma` + `Threshold`** 是两个核心调参旋钮——前者控平滑度，后者控灵敏度。
- 卡尺 ROI 长度必须**穿过目标 + 余量**，否则找不到边缘。
- 复杂形状测量请升级到 **2D Metrology**。

> **后续阅读**：详见 `C:\Program Files\MVTec\HALCON-26.05-Progress\doc\html\reference\operators\toc_1dmeasuring.html`。