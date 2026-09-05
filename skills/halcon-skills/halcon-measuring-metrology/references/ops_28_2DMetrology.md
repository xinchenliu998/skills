# HALCON 算子分类详解：2D Metrology（二维量具）

> **分类定位**：复杂几何量（圆、矩形、椭圆、直线、通用）的快速测量；适合一张图测量多个目标尺寸。
> **算子数量**：约 50 个。
> **HALCON 版本**：26.05.0.0 Progress
> **官方文档**：`toc_2dmetrology.html`

---

## 1. 概述

2D Metrology 是 HALCON 用于**多尺寸同步测量**的高级框架，比传统的 `measure_pairs` 强大得多：
- 一个 `MetrologyHandle` 可包含**任意数量**的几何对象（圆/直线/矩形/椭圆/通用）
- 支持**模糊测量**（`fuzzy`）抗边缘不齐
- 支持**对齐**（`align_metrology_model`）把量具匹配到初始位置
- 支持**多次实例**（multi-instance）：一个量具对象可匹配图像中多个相同形状
- 可**持久化**（`write_metrology_model` / `read_metrology_model`）

### 与 1D Measuring 对比

| 维度 | 1D Measuring | 2D Metrology |
|------|--------------|---------------|
| 几何复杂度 | 边/对边 | 圆/矩形/椭圆/通用 |
| 多对象 | 手动循环 | 一键批量 |
| 模糊测量 | 无 | 有（`set_metrology_object_fuzzy_param`） |
| 对齐 | 无 | 有（`align_metrology_model`） |
| 适用 | 简单边缘对 | 复杂尺寸量 |

---

## 2. 应用场景

| 场景 | 说明 |
|------|------|
| **多尺寸同步测量** | 一张图测几十个尺寸（卡尺替代） |
| **柔性件定位** | `align_metrology_model` 把量具贴到当前工件 |
| **多目标圆形孔** | `add_metrology_object_circle_measure` + `instances='multiple'` |
| **通用形状** | `add_metrology_object_generic` 支持任意曲线 |
| **边缘不齐场景** | `set_metrology_object_fuzzy_param` 启用模糊测量 |

**典型行业**：精密机加工、CMM 嵌入、SPC 统计过程控制、零件出厂检验、汽车零部件形位公差。

---

## 3. 子分类详解

### 3.1 模型管理（约 15 算子）

- 创建：`create_metrology_model(MetHandle)`
- 配置：`set_metrology_model_image_size` / `set_metrology_model_param`
- 查询：`get_metrology_model_param` / `get_metrology_model_info`
- 复制：`copy_metrology_model`
- 释放：`clear_metrology_model`
- 持久化：`read_metrology_model` / `write_metrology_model`
- 对齐：`align_metrology_model`
- 序列化：`serialize_metrology_model` / `deserialize_metrology_model`

### 3.2 几何对象添加（约 12 算子）

- `add_metrology_object_circle_measure` — 圆
- `add_metrology_object_ellipse_measure` — 椭圆
- `add_metrology_object_line_measure` — 直线
- `add_metrology_object_rectangle2_measure` — 矩形
- `add_metrology_object_generic` — 通用曲线
- `add_metrology_object_fuzzy_image` — 模糊图像
- 复制：`copy_metrology_object`
- 释放：`clear_metrology_object`
- 变换：`transform_metrology_object`
- 属性：`set_metrology_object_param` / `get_metrology_object_param`

### 3.3 测量执行

- `apply_metrology_model(Image, MetHandle)` — 主测量函数

### 3.4 结果查询（约 10 算子）

- `get_metrology_object_result` — 几何参数（Row/Col/Phi/Radius）
- `get_metrology_object_result_contour` — 可视化轮廓
- `get_metrology_object_measures` — 测量点位置
- `get_metrology_object_indices` — 找到的实例索引
- `get_metrology_object_num_instances` — 实例数量
- `get_metrology_object_model_contour` — 模型轮廓

### 3.5 模糊测量（约 10 算子）

- `set_metrology_object_fuzzy_param` / `get_metrology_object_fuzzy_param`
- `reset_metrology_object_fuzzy_param`
- `set_fuzzy_measure` / `reset_fuzzy_measure`
- `set_fuzzy_measure_norm_pair`
- `fuzzy_measure_pairing` / `fuzzy_measure_pairs` / `fuzzy_measure_pos`
- `fuzzy_perimeter` / `fuzzy_entropy`

---

## 4. 核心算子详解

### 4.1 模型生命周期（5 个）

```hdevelop
* 1. 创建
create_metrology_model(MetHandle)

* 2. 配置图像尺寸
set_metrology_model_image_size(MetHandle, Width, Height)

* 3. 添加几何对象
add_metrology_object_circle_measure(MetHandle, Row, Column, Radius, \
                                     MeasureLength1, MeasureLength2, \
                                     DistanceThreshold, Index)

* 4. 测量
apply_metrology_model(Image, MetHandle)

* 5. 释放
clear_metrology_model(MetHandle)
```

### 4.2 几何对象添加（5 个）

| 算子 | 用途 |
|------|------|
| `add_metrology_object_circle_measure` | 添加圆测量（中心 + 半径） |
| `add_metrology_object_line_measure` | 添加直线测量 |
| `add_metrology_object_rectangle2_measure` | 添加矩形测量 |
| `add_metrology_object_ellipse_measure` | 添加椭圆测量 |
| `add_metrology_object_generic` | 添加通用曲线 |

### 4.3 测量执行与结果

```hdevelop
* 应用测量
apply_metrology_model(Image, MetHandle)

* 取结果（圆：Row, Column, Radius）
get_metrology_object_result(MetHandle, Index, Row, Column, _, Radius, _)

* 取结果轮廓（用于显示）
get_metrology_object_result_contour(Contour, MetHandle, Index, 'all')

* 取测量点（卡尺位置）
get_metrology_object_measures(MeasureConts, MetHandle, Index, 'all')
```

### 4.4 对齐（柔件贴位）

```hdevelop
* 把量具贴到当前工件位置（基于模板匹配等结果）
vector_angle_to_rigid(RefRow, RefCol, RefAngle, CurrRow, CurrCol, CurrAngle, HomMat2D)
align_metrology_model(MetHandle, HomMat2D)
```

### 4.5 模糊测量（边缘不齐）

```hdevelop
* 启用模糊测量（对边缘不齐/反光更鲁棒）
set_metrology_object_fuzzy_param(MetHandle, Index, ['measure_type', 'sigma', 'threshold'], \
                                  ['fuzzy', 1.0, 30])
```

---

## 5. HDevelop 示例代码

### 示例 1：多圆孔批量测量

```hdevelop
* 读图
read_image(Image, 'multi_holes.png')
get_image_size(Image, Width, Height)

* 创建量具模型
create_metrology_model(MetHandle)
set_metrology_model_image_size(MetHandle, Width, Height)

* 添加 4 个圆孔（手动指定初始位置）
add_metrology_object_circle_measure(MetHandle, 100, 100, 30, \
                                     60, 60, 10, Idx1)
add_metrology_object_circle_measure(MetHandle, 200, 100, 30, \
                                     60, 60, 10, Idx2)
add_metrology_object_circle_measure(MetHandle, 100, 300, 30, \
                                     60, 60, 10, Idx3)
add_metrology_object_circle_measure(MetHandle, 200, 300, 30, \
                                     60, 60, 10, Idx4)

* 执行测量
apply_metrology_model(Image, MetHandle)

* 取所有圆的中心和半径
for i := Idx1 to Idx4 by 1
    get_metrology_object_result(MetHandle, i, Row, Col, _, R, _)
    dev_disp_text('圆 ' + i + ': (' + tuple_string(Row, '$.1f') + \
                  ', ' + tuple_string(Col, '$.1f') + ') R=' + \
                  tuple_string(R, '$.3f'), 'window', i*20, 'left', 'black', [], [])
    
    * 显示结果轮廓
    get_metrology_object_result_contour(Contour, MetHandle, i, 'all')
    dev_set_color('green')
    dev_display(Contour)
endfor

clear_metrology_model(MetHandle)
```

### 示例 2：自动多实例（每类找多个相同形状）

```hdevelop
* 创建一个圆量具
create_metrology_model(MetHandle)
add_metrology_object_circle_measure(MetHandle, 250, 250, 30, \
                                     80, 80, 10, Idx)

* 允许找到多个相同圆
set_metrology_object_param(MetHandle, Idx, 'instances_outside_measure_regions', 'true')
set_metrology_object_param(MetHandle, Idx, 'num_instances', 10)   * 最多 10 个

* 执行测量
apply_metrology_model(Image, MetHandle)

* 拿到所有找到的实例
get_metrology_object_indices(MetHandle, 'all', Indices)
get_metrology_object_num_instances(MetHandle, Idx, NumFound)

dev_disp_text('找到 ' + NumFound + ' 个圆孔', 'window', 'top', 'left', 'green', [], [])
```

### 示例 3：柔性件对齐 + 量具

```hdevelop
* 1. 模板匹配找位姿
find_shape_model(Image, ShapeModelID, rad(-30), rad(60), 0.7, 1, 0.5, \
                 'least_squares', 0, 0.8, MatchRow, MatchCol, MatchAngle, Score)

if (|Score| > 0)
    * 2. 建立变换
    vector_angle_to_rigid(RefRow, RefCol, RefAngle, MatchRow, MatchCol, \
                          MatchAngle, HomMat2D)
    
    * 3. 创建量具模型（在参考位置创建）
    create_metrology_model(MetHandle)
    add_metrology_object_circle_measure(MetHandle, 200, 200, 30, 60, 60, 10, Idx)
    
    * 4. 对齐量具到当前工件
    align_metrology_model(MetHandle, HomMat2D)
    
    * 5. 测量
    apply_metrology_model(Image, MetHandle)
    get_metrology_object_result(MetHandle, Idx, R, C, _, Radius, _)
    
    dev_disp_text('测量 R: ' + tuple_string(Radius, '$.3f'), 'window', 'top', 'left', 'black', [], [])
    
    clear_metrology_model(MetHandle)
endif
```

### 示例 4：模糊测量（边缘不齐场景）

```hdevelop
* 创建量具
create_metrology_model(MetHandle)
add_metrology_object_line_measure(MetHandle, 100, 100, 100, 500, \
                                   30, 30, 'nearest_neighbor', Idx)

* 配置模糊测量（抗边缘不齐/反光）
set_metrology_object_fuzzy_param(MetHandle, Idx, \
    ['measure_type', 'fuzzy_thresh', 'sigma', 'invisibility'], \
    ['fuzzy', 0.5, 1.0, 'medium'])

* 执行
apply_metrology_model(Image, MetHandle)
get_metrology_object_result(MetHandle, Idx, R1, C1, R2, C2, _)

* 显示
get_metrology_object_result_contour(Contour, MetHandle, Idx, 'all')
dev_display(Contour)
clear_metrology_model(MetHandle)
```

---

## 6. 典型工业流水线

### 流水线 A：零件全尺寸测量

```
read_image
   ↓
create_metrology_model
   ↓
set_metrology_model_image_size(W, H)
   ↓
循环添加（圆/直线/矩形/椭圆）
   ↓
apply_metrology_model
   ↓
get_metrology_object_result × N → 写数据库/统计过程
   ↓
clear_metrology_model
```

### 流水线 B：柔件对齐 + 全尺寸测量

```
grab_image
   ↓
find_shape_model → 6DOF 位姿
   ↓
vector_angle_to_rigid → HomMat2D
   ↓
create_metrology_model + add_*
   ↓
align_metrology_model (将量具贴到当前件)
   ↓
apply_metrology_model
   ↓
get_metrology_object_result (实际尺寸)
   ↓
SPC 统计 / 上传 MES
```

---

## 7. 常见陷阱与最佳实践

1. **`set_metrology_model_image_size` 必填**：未设置图像尺寸可能测量失败。
2. **Index 是 1-based**：从 1 开始递增，按添加顺序。
3. **`MeasureLength1/2` 卡尺长度**：一般 20–50 px，太短不稳，太长不精。
4. **`DistanceThreshold` 决定搜索半径**：典型 10–30 px。
5. **多实例 `num_instances`**：默认 1；要找多个显式设置。
6. **模糊测量只在边缘不齐时启用**：正常场景用普通模式更准。
7. **柔件必须 `align_metrology_model`**：否则量具在错误位置测量。
8. **持久化用 `write_metrology_model`**：跨 HALCON 版本可能不兼容，用 `serialize_metrology_model` 更稳。

---

## 8. 参数调优指南

| 场景 | 建议 |
|------|------|
| 卡尺长度 | `MeasureLength1 = 2 * MeasureLength2`（对称） |
| 搜索半径 | `DistanceThreshold` = 5% 直径 |
| 多实例 | `'num_instances', N` 显式指定 |
| 边缘不齐 | `set_metrology_object_fuzzy_param(..., 'measure_type', 'fuzzy')` |
| 柔件 | 模板匹配 + `align_metrology_model` 贴位 |

---

## 9. 相关分类

- **1D Measuring**：`gen_measure_rectangle2` + `measure_pairs` 适合简单边缘对。
- **XLD**：`fit_circle_contour_xld` / `fit_line_contour_xld` 也能做拟合，但需先提取轮廓。
- **Matching**：`align_metrology_model` 需要匹配提供位姿。

---

## 10. 学习小结

2D Metrology 是"复杂尺寸量测层"。**学习优先级**：
1. **必学**：`create_metrology_model` + `add_metrology_object_circle_measure` + `apply_metrology_model` + `get_metrology_object_result`。
2. **重要**：`align_metrology_model`（柔件）、`set_metrology_object_fuzzy_param`（模糊测量）、`get_metrology_object_result_contour`（可视化）。
3. **专项**：`add_metrology_object_generic`（通用曲线）、`serialize_metrology_model`（跨进程）。

**核心要点**：
- `MetrologyHandle` 是**容器**——一个模型可装多个几何对象，按 `Index`（1-based）访问。
- **柔件必须 `align_metrology_model`**——量具贴到当前工件位置才能测准。
- 模糊测量用 `set_metrology_object_fuzzy_param`——适合边缘不齐/反光场景。
- 多实例（`'num_instances'`）让单个量具对象自动找图像中所有相同形状。

> **后续阅读**：详见 `C:\Program Files\MVTec\HALCON-26.05-Progress\doc\html\reference\operators\toc_2dmetrology.html`。