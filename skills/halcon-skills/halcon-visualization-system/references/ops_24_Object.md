# HALCON 算子分类详解：Object（通用对象操作）

> **分类定位**：处理多对象数组（多图像、多区域、多 XLD 等）的统一接口。
> **算子数量**：约 30 个。
> **HALCON 版本**：26.05.0.0 Progress
> **官方文档**：`toc_object.html`

---

## 1. 概述

HALCON 中所有"对象"（Image、Region、XLD、Tuple 数组等）都可以视为**对象数组**。Object 分类提供了管理这些数组的通用算子——插入、删除、复制、计数、对比，与 Python list 高度类似。

虽然 Object 分类的算子数量不多，但几乎所有需要批量处理的项目都会用到，是基础工具集。

### 子分类

| 子类 | 说明 |
|------|------|
| **Information** | 查询对象数组信息（个数、类型、相等性） |
| **Manipulation** | 对象数组增删改（合并、选择、插入、替换） |
| **Generic** | 空对象、整数-对象互转 |

---

## 2. 应用场景

| 场景 | 说明 |
|------|------|
| **多 ROI 处理** | `select_obj` 选 ROI 后分别处理 |
| **批量读图合并** | `concat_obj` 把多张图合并成一个对象数组 |
| **结果过滤** | `select_obj` 按索引选符合条件的 |
| **多对象调试** | `count_obj` 知道当前有多少对象 |
| **句柄存档** | `integer_to_obj` / `obj_to_integer` 用于跨进程传递 |

**典型行业**：任何需要批量处理的视觉项目。

---

## 3. 子分类详解

### 3.1 Information（信息查询，5 算子）

- `count_obj(Objects, Num)` — 对象个数
- `get_obj_class(Objects, Class)` — 单个对象的类名（'image'/'region'/'xld'/'xld_cont'/'xld_poly'/'tuple'/'object'）
- `test_equal_obj(Objects1, Objects2, IsEqual)` — 逐元素相等性
- `obj_diff(Objects1, Objects2, DiffObjects)` — 算两个对象数组的差集（按索引）
- `compare_obj(Objects1, Objects2, IsEqual, Type, Elem)` — 细粒度比较

### 3.2 Manipulation（管理，7 算子）

- `concat_obj(Objects1, Objects2, Concatenated)` — 末尾追加
- `copy_obj(Objects, ObjectsSelected, Index, NumCopy)` — 按索引复制
- `select_obj(Objects, ObjectSelected, Index)` — 按索引选
- `remove_obj(Objects, ObjectsRemoved, Index)` — 按索引删
- `insert_obj(Objects1, Objects2, Index, ObjectsInserted)` — 插入
- `replace_obj(Objects1, Objects2, Index, ObjectsReplaced)` — 替换
- （旧）`clear_obj` — 释放（已废弃，建议 `dev_clear_obj` 或变量重赋）

### 3.3 Generic（通用，5 算子）

- `gen_empty_obj(EmptyObject)` — 空对象
- `integer_to_obj(Integer, Object)` — 整数 → 对象（1→空图像、2→空区域等）
- `obj_to_integer(Object, Integer)` — 反向
- `generic_object` — 创建指定类的空对象
- `copy_object`（部分类型）

---

## 4. 核心算子详解

### 4.1 信息查询（4 个）

| 算子 | 签名 | 用途 |
|------|------|------|
| `count_obj` | `count_obj(Objects → Num)` | 对象数组长度 |
| `get_obj_class` | `get_obj_class(Object → Class)` | 单对象类型字符串 |
| `test_equal_obj` | `test_equal_obj(O1, O2 → IsEqual)` | 元素一一对应相等 |
| `obj_diff` | `obj_diff(O1, O2 → Diff)` | 按索引差集 |

### 4.2 管理操作（6 个）

| 算子 | 签名 | 用途 |
|------|------|------|
| `concat_obj` | `concat_obj(O1, O2 → Concatenated)` | 末尾追加 |
| `copy_obj` | `copy_obj(Objects, Out, Index, Num)` | 按索引复制 N 次 |
| `select_obj` | `select_obj(Objects, Out, Index)` | 索引取值 |
| `remove_obj` | `remove_obj(Objects, Out, Index)` | 索引删除 |
| `insert_obj` | `insert_obj(O1, O2, Index → Out)` | 插入 |
| `replace_obj` | `replace_obj(O1, O2, Index → Out)` | 替换 |

### 4.3 通用（3 个）

| 算子 | 签名 | 用途 |
|------|------|------|
| `gen_empty_obj` | `gen_empty_obj(EmptyObject)` | 空对象（任何类型） |
| `integer_to_obj` | `integer_to_obj(Int → Object)` | Int → Obj（1=image, 2=region...） |
| `obj_to_integer` | `obj_to_integer(Object → Int)` | Obj → Int |

---

## 5. HDevelop 示例代码

### 示例 1：批量读图 + 合并对象数组

```hdevelop
* 批量读图
list_files('images/', 'files', Files)
tuple_length(Files, N)
gen_empty_obj(ImageStack)

for i := 0 to N - 1 by 1
    read_image(Img, Files[i])
    concat_obj(ImageStack, Img, ImageStack)
endfor

* 现在 ImageStack 包含所有图像
count_obj(ImageStack, TotalN)
dev_disp_text('共合并 ' + TotalN + ' 张图像', 'window', 'top', 'left', 'green', [], [])

* 单独处理某一张
select_obj(ImageStack, SingleImg, 3)   * 第 4 张
gauss_filter(SingleImg, Smoothed, 3.0)
```

### 示例 2：多 ROI 选择性处理

```hdevelop
* 从轮廓检测得到多个 XLD
edges_sub_pix(Image, Edges, 'canny', 1.0, 20, 40)
segment_contours_xld(Edges, Segmented, 'lines_circles', 5, 4, 2)
select_contours_xld(Segmented, Selected, 'contour_length', 50, 1000, -0.5, 0.5)

* 统计 + 选择
count_obj(Selected, NSeg)
dev_disp_text('共 ' + NSeg + ' 段轮廓', 'window', 'top', 'left', 'black', [], [])

* 按索引遍历所有
for i := 1 to NSeg by 1
    select_obj(Selected, OneSeg, i - 1)
    fit_line_contour_xld(OneSeg, 'tukey', -1, 0, 5, 2, Row1, Col1, Row2, Col2, ...)
    * 处理每段...
endfor
```

### 示例 3：删除不需要的对象

```hdevelop
* 创建 10 个测试对象
gen_empty_obj(TestSet)
for i := 1 to 10 by 1
    gen_circle(Circle, i * 50, i * 50, 20)
    concat_obj(TestSet, Circle, TestSet)
endfor

count_obj(TestSet, N)
* 删除第 3 和第 7 个（从后往前删避免索引偏移）
remove_obj(TestSet, Tmp, 6)   * 先删第 7 个
remove_obj(Tmp, Result, 2)    * 再删第 3 个

count_obj(Result, NewN)        * NewN = 8
```

### 示例 4：对象类型查询与跨进程传递

```hdevelop
* 创建不同类型对象
read_image(Img, 'test.png')
threshold(Img, Region, 128, 255)

* 查询类型
get_obj_class(Img, Class1)    * 'image'
get_obj_class(Region, Class2) * 'region'

* 整数-对象互转（用于跨进程 ID 映射）
obj_to_integer(Img, ImgID)    * ImgID 是 int
* 传递 ImgID 到另一进程...
integer_to_obj(ImgID, Img2)   * 还原（同一进程有效）
```

---

## 6. 典型工业流水线

### 流水线 A：多 ROI 区域分别检测

```
read_image
   ↓
threshold → ConnectedRegions（多个连通域）
   ↓
select_shape 过滤有效目标
   ↓
count_obj → NumBlobs
   ↓
for i := 0 to NumBlobs-1
    select_obj → SingleBlob
    area_center(SingleBlob) → 输出
endfor
```

### 流水线 B：批量模型匹配结果

```
find_shape_models (返回多匹配)
   ↓
Row[], Column[], Angle[], Score[]  ← Tuple 数组
   ↓
count_obj(Models, N)   ← （如果返回对象形式）
   ↓
for i := 0 to N-1
    select_obj(Models, M_i, i)
    affine_trans_* 仿射变换
endfor
```

---

## 7. 常见陷阱与最佳实践

1. **`concat_obj` 是引用追加**：原对象数组不会被清空，会共享内存。
2. **`remove_obj` 的索引偏移**：从后往前删或先 `count_obj` 重新计算索引。
3. **`select_obj` 索引从 0 开始**（与 HDevelop 习惯的 1-based 不同）。
4. **跨进程 `obj_to_integer`**：仅在同 HALCON 版本同进程中有效，**不要用于跨版本**。
5. **`gen_empty_obj` 的类型**：默认创建空对象，可装任意类型（image/region/xld），用 `integer_to_obj` 显式指定类型更稳。
6. **对象释放**：HALCON 自动 GC（garbage collection），无需手动 `clear_obj`，但大对象尽早释放避免内存峰值。
7. **多对象选择性能**：`select_obj` 按索引是 O(1)，但循环批量选择建议用 `gen_empty_obj` + `concat_obj`。

---

## 8. 参数调优指南

| 场景 | 建议 |
|------|------|
| 大批量对象 | 用 `copy_obj` + `select_obj` 比手写循环快 |
| 删除多个对象 | 从后往前删，避免索引失效 |
| 跨进程对象 | 改用 `serialize_*` / `deserialize_*` 而非 `integer_to_obj` |
| 对象池化 | 对临时结果用 `gen_empty_obj` + `concat_obj` 构造对象数组 |

---

## 9. 相关分类

- **Region / Manipulation**：Region 自带 `concat_obj` 等，但 Object 提供统一接口。
- **Tuple**：`tuple_concat` 用于元数组合并；`obj` 更通用。
- **System / Serialized Item**：跨进程对象传递用 `serialize_*`。

---

## 10. 学习小结

Object 分类是"多对象容器层"。**学习优先级**：
1. **必学**：`count_obj`、`concat_obj`、`select_obj`、`copy_obj`。
2. **重要**：`remove_obj`、`insert_obj`、`replace_obj`、`get_obj_class`。
3. **专项**：`integer_to_obj` / `obj_to_integer`（跨进程 ID 传递）。

**核心要点**：
- `select_obj` / `remove_obj` 等索引从 **0 开始**（与 HDevelop 1-based 计数不同）。
- `concat_obj` 不复制内存，是引用追加——修改原数组会影响合并结果。
- 对象释放由 HALCON 自动 GC 控制，无需手动 `clear_obj`。

> **后续阅读**：详见 `C:\Program Files\MVTec\HALCON-26.05-Progress\doc\html\reference\operators\toc_object.html`。