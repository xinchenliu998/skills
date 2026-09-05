# HALCON 算子分类详解：Tuple（元组/数组）

> **分类定位**：HALCON 通用数据结构，承载所有非图像对象的批量数据。
> **算子数量**：约 180 个，覆盖算术、位运算、字符串、集合、容器等 15 个子类。
> **HALCON 版本**：26.05.0.0 Progress
> **官方文档**：`toc_tuple.html`

---

## 1. 概述

Tuple（元组）是 HALCON 中**最通用**的数据结构，类似于 Python 的 list 或 NumPy 的 array，但**元素类型可混合**（int、float、string、handle）。所有非图像/区域/XLD 的批量数据（坐标数组、参数表、测量结果、字符串集合）都以 Tuple 形式传递。

Tuple 算子分为 **15 个子类**：
- **Arithmetic**：数学函数（`tuple_sin/cos/pow/sqrt/...`）
- **Bit**：位运算（`tuple_band/bor/bxor/bnot/lsh/rsh`）
- **Comparison**：逐元素比较（`tuple_equal_elem/less_elem/...`）
- **Containers**：类型判断（`tuple_is_int/real/string/handle_elem/...`）
- **Conversion**：类型转换（`tuple_string/number/real/int/...`）
- **Creation**：创建（`tuple_gen_const/gen_sequence/concat/rand/...`）
- **Element Order**：排序与选择（`tuple_sort/sort_index/select/select_mask/...`）
- **Features**：统计（`tuple_length/mean/deviation/sum/median/...`）
- **Logical**：逻辑（`tuple_and/or/xor/not`）
- **Manipulation**：元素增删改（`tuple_insert/remove/replace/concat/...`）
- **Selection**：同 Element Order
- **Sets**：集合（`tuple_union/intersection/difference/symmdiff/uniq`）
- **String**：字符串操作（`tuple_strlen/strchr/regexp_match/...`）
- **Type**：语义类型（`tuple_type/type_elem/sem_type`）

---

## 2. 应用场景

| 场景 | 说明 |
|------|------|
| **测量结果解析** | `get_metrology_object_result` 返回 `(Row, Column, Phi, Radius1, Radius2)` 五个 Tuple |
| **模板匹配结果** | `find_shape_model` 返回 `(Row, Column, Angle, Score)` 四个 Tuple |
| **批量数据处理** | 循环内累积测量值、特征值做统计分析 |
| **字符串解析** | 从串口/网络协议中提取字段（`tuple_regexp_match`） |
| **参数调优** | 多组参数组合下的批量实验结果聚合 |
| **配置文件 IO** | `read_tuple`/`write_tuple` 存取坐标列表 |
| **跨语言桥接** | 与 C++/C# 集成时 Tuple 是主要数据载体 |

**典型行业**：所有 HALCON 项目都会用到——它是基础数据结构。

---

## 3. 子分类详解

### 3.1 Arithmetic（算术，约 70 算子）

覆盖几乎所有标量数学函数，**逐元素**作用于 Tuple：
- 基础：`tuple_abs/add/sub/mult/div/neg`
- 指数：`tuple_pow/sqrt/exp/log/log2/log10/exp2/exp10/cbrt`
- 三角：`tuple_sin/cos/tan/asin/acos/atan/atan2/sinh/cosh/tanh`
- 取整：`tuple_ceil/floor/round/trunc`
- 转换：`tuple_real/int/deg/rad`
- 特殊：`tuple_hypot/fmod/ldexp/erf/erfc/lgamma/tgamma`
- 复数：`tuple_complex`

### 3.2 Bit（位运算，6 算子）

`tuple_band/bor/bxor/bnot/lsh/rsh`，按位运算整数。

### 3.3 String（字符串，约 25 算子）

- 长度：`tuple_strlen`
- 查找：`tuple_strchr/strrchr/strstr/strrstr`
- 切片：`tuple_str_first_n/str_last_n/substr`
- 替换：`tuple_str_replace`
- 位选：`tuple_str_bit_select`
- 正则：`tuple_regexp_match/replace/select/test`
- 距离：`tuple_str_distance`（Levenshtein 距离）

### 3.4 Sets（集合，5 算子）

`tuple_intersection/union/difference/symmdiff/uniq`，将 Tuple 视为多重集。

### 3.5 Containers（类型判断，约 12 算子）

`tuple_is_int/int_elem/real/real_elem/string/string_elem/handle/handle_elem/mixed/nan_elem/serializable/valid_handle` + `tuple_environment`。

---

## 4. 核心算子详解

### 4.1 数学函数（10 个）

| 算子 | 签名 | 用途 |
|------|------|------|
| `tuple_sin` | `tuple_sin(Tuple → Sin)` | 弧度正弦，**输入弧度** |
| `tuple_cos` | `tuple_cos(Tuple → Cos)` | 弧度余弦 |
| `tuple_pow` | `tuple_pow(Tuple1, Tuple2 → Pow)` | 元素幂次，Tuple1^Tuple2 |
| `tuple_sqrt` | `tuple_sqrt(Tuple → Sqrt)` | 平方根 |
| `tuple_hypot` | `tuple_hypot(Tuple1, Tuple2 → Hypot)` | `sqrt(x^2 + y^2)`，防溢出 |
| `tuple_atan2` | `tuple_atan2(TupleY, TupleX → Angle)` | 四象限 atan，结果弧度 |
| `tuple_deg` | `tuple_deg(Tuple → Deg)` | 弧度 → 度 |
| `tuple_rad` | `tuple_rad(Tuple → Rad)` | 度 → 弧度 |
| `tuple_round` | `tuple_round(Tuple → Round)` | 四舍五入 |
| `tuple_floor` | `tuple_floor(Tuple → Floor)` | 下取整 |

### 4.2 字符串（8 个）

| 算子 | 签名 | 用途 |
|------|------|------|
| `tuple_regexp_match` | `tuple_regexp_match(String, Expression → Matches)` | 正则匹配 |
| `tuple_regexp_replace` | `tuple_regexp_replace(String, Expression, Replace → Result)` | 正则替换 |
| `tuple_regexp_test` | `tuple_regexp_test(String, Expression → IsMatch)` | 正则判定 |
| `tuple_string` | `tuple_string(Tuple, Format → String)` | 数字 → 字符串（'$.2f' 等） |
| `tuple_number` | `tuple_number(String → Number)` | 字符串 → 数字 |
| `tuple_strlen` | `tuple_strlen(String → Length)` | 字符串长度 |
| `tuple_strchr` | `tuple_strchr(String, Character → Position)` | 字符首次位置 |
| `tuple_substr` | `tuple_substr(String, Position1, Position2 → Substring)` | 子串切片 |

### 4.3 集合（5 个）

| 算子 | 签名 | 用途 |
|------|------|------|
| `tuple_union` | `tuple_union(Set1, Set2 → Union)` | 并集 |
| `tuple_intersection` | `tuple_intersection(Set1, Set2 → Intersection)` | 交集 |
| `tuple_difference` | `tuple_difference(Set1, Set2 → Difference)` | 差集 |
| `tuple_symmdiff` | `tuple_symmdiff(Set1, Set2 → Symmdiff)` | 对称差 |
| `tuple_uniq` | `tuple_uniq(Tuple → Uniq)` | 去重（保留首次出现顺序） |

### 4.4 容器与排序（7 个）

| 算子 | 签名 | 用途 |
|------|------|------|
| `tuple_sort` | `tuple_sort(Tuple → Sorted)` | 升序排序 |
| `tuple_sort_index` | `tuple_sort_index(Tuple → Indices)` | 返回排序下标 |
| `tuple_select` | `tuple_select(Tuple, Index → Selected)` | 按下标取元素 |
| `tuple_select_range` | `tuple_select_range(Tuple, Min, Max → Selected)` | 取范围 [Min, Max] |
| `tuple_select_mask` | `tuple_select_mask(Tuple, Mask → Selected)` | 按布尔掩码选 |
| `tuple_length` | `tuple_length(Tuple → Length)` | 元素个数 |
| `tuple_gen_const` | `tuple_gen_const(Length, Type, Value → Tuple)` | 生成常量元组 |

### 4.5 统计（6 个）

| 算子 | 签名 | 用途 |
|------|------|------|
| `tuple_mean` | `tuple_mean(Tuple → Mean)` | 均值 |
| `tuple_deviation` | `tuple_deviation(Tuple → Deviation)` | 标准差 |
| `tuple_sum` | `tuple_sum(Tuple → Sum)` | 总和 |
| `tuple_median` | `tuple_median(Tuple → Median)` | 中位数 |
| `tuple_min/max` | `tuple_min(Tuple → Min)` | 最小/最大值 |
| `tuple_min2/max2` | `tuple_min2(T1, T2 → Min)` | 逐元素 min/max |

---

## 5. HDevelop 示例代码

### 示例 1：测量结果批量统计

```hdevelop
* 模拟 5 次圆孔测量的直径序列
Diameters := [12.05, 12.08, 12.03, 12.07, 12.06]

* 统计指标
tuple_mean(Diameters, MeanD)
tuple_deviation(Diameters, StdD)
tuple_min(Diameters, MinD)
tuple_max(Diameters, MaxD)

* 输出带格式字符串
MeanStr := tuple_string(MeanD, '$.3f')
disp_text(WindowHandle, '平均直径: ' + MeanStr + ' mm', 'window', 'top', 'left', 'black', [], [])

* 标准差判断（>0.05 mm 告警）
if (StdD > 0.05)
    disp_text(WindowHandle, '警告: 测量波动过大!', 'window', 50, 'left', 'red', [], [])
endif
```

### 示例 2：坐标字符串解析（正则）

```hdevelop
* 从串口协议字符串中解析坐标
LogLine := 'X=123.45 Y=678.90 Z=12.34'

* 匹配 X=数字
tuple_regexp_match(LogLine, 'X=([0-9.]+)', XMatch)
tuple_regexp_match(LogLine, 'Y=([0-9.]+)', YMatch)
tuple_regexp_match(LogLine, 'Z=([0-9.]+)', ZMatch)

* 转浮点
tuple_number(XMatch, X)
tuple_number(YMatch, Y)
tuple_number(ZMatch, Z)

* 计算距离
tuple_hypot(X, Y, DistXY)
disp_text(WindowHandle, 'XY 距离: ' + tuple_string(DistXY, '$.2f'), 'window', 'top', 'left', 'black', [], [])
```

### 示例 3：集合运算

```hdevelop
* 检测引脚编号匹配
Detected := [3, 7, 12, 15, 18]
Expected := [3, 7, 11, 15, 19, 21]

* 缺失引脚
tuple_difference(Expected, Detected, Missing)

* 多余引脚
tuple_difference(Detected, Expected, Extra)

* 共有引脚
tuple_intersection(Detected, Expected, Common)

* 全部去重
tuple_concat(Detected, Expected, AllRaw)
tuple_uniq(AllRaw, AllUnique)

dev_disp_text('缺失: ' + tuple_string(Missing, '.0f'), 'window', 'top', 'left', 'black', [], [])
```

### 示例 4：批量参数扫描

```hdevelop
* 扫描阈值，统计连通域数量
ThresholdList := [50, 80, 110, 140, 170, 200]
tuple_gen_const(|ThresholdList|, 0, Counts)

read_image(Image, 'pcb')

for i := 0 to |ThresholdList| - 1 by 1
    threshold(Image, Region, ThresholdList[i], 255)
    connection(Region, Connected)
    count_obj(Connected, NumBlobs)
    Counts[i] := NumBlobs
endfor

* 找最优阈值（连通域数 = 目标值）
TargetN := 12
tuple_abs(Counts - TargetN, Diff)
tuple_min(Diff, MinDiff)
tuple_find(Diff, MinDiff, BestIdx)
BestThresh := ThresholdList[BestIdx]
```

---

## 6. 典型工业流水线

### 流水线 A：模板匹配结果解析

```
find_shape_model(Image, ModelID, ..., Row, Column, Angle, Score)
        ↓
   tuple_length(Row, N)             ← N 个匹配
        ↓
   for i := 0 to N-1
       tuple_select(Row, i, Ri)
       tuple_select(Column, i, Ci)
       tuple_select(Angle, i, Ai)
       * 用 Ri/Ci/Ai 做后续 ROI 计算
   endfor
```

### 流水线 B：批量测量结果统计

```
for i := 1 to N
    apply_metrology_model(Image, MetroHandle)
    get_metrology_object_result(..., R, C, Phi, Radius1)
    tuple_concat(AllRadii, Radius1, AllRadii)   ← 累积
endfor

tuple_mean(AllRadii, MeanR)
tuple_deviation(AllRadii, StdR)
tuple_min(AllRadii, MinR)
tuple_max(AllRadii, MaxR)
```

---

## 7. 常见陷阱与最佳实践

1. **字符串必须用单引号**：HALCON 字符串字面量 `'foo'`，双引号会报错。
2. **`tuple_select` 与 `tuple_select_mask` 区别**：前者按下标（int），后者按布尔掩码（0/1）。
3. **`tuple_sin` 输入弧度**：角度要先 `tuple_rad` 转换，或用 `tuple_sin(tuple_rad(...))`。
4. **`tuple_string` 的格式符**：`'$.3f'`（3 位小数浮点）、`'.5d'`（5 位整数补零）、`'x'`（十六进制）。
5. **`tuple_regexp_match` 默认贪婪**：用 `'subexpression'` 或 `'ignore_case'` 等参数调整。
6. **`tuple_gen_const` 创建整型**：若需浮点，写 `tuple_real(tuple_gen_const(10, 0), RealConst)`。
7. **Tuple 类型混合**：HALCON 允许 `[1, 2.5, 'hello']`，但算术运算前需统一类型。
8. **大 Tuple 性能**：超过 100 万元素的 Tuple 处理慢，考虑分块或改用 Region/XLD。

---

## 8. 参数调优指南

| 场景 | 建议 |
|------|------|
| 大量重复值 | `tuple_gen_const(N, Type, Val)` 比循环快 10–100 倍 |
| 数值精度 | 优先用 `real`，避免过早 `int` 截断 |
| 字符串拼接 | `s := A + B + C` 直接拼接，等价 `tuple_concat` |
| 正则匹配 | 锚定 `^...$` 可提速；非贪婪用 `.*?` |
| 排序 | `tuple_sort` 升序；降序用 `tuple_inverse(tuple_sort(T))` |
| 类型判断 | 优先 `tuple_is_int_elem`（逐元素）而非 `tuple_is_int`（全部相同才返 1） |

---

## 9. 相关分类

- **System / Serial**：跨进程传递 Tuple 用 `serialize_tuple`。
- **File / Tuple**：`read_tuple` / `write_tuple` 直接存读。
- **Region**：区域特征返回多值 Tuple（`area_center` → `(Area, Row, Column)`）。
- **XLD**：XLD 拟合返回 Tuple 数组。
- **Matrix**：元组可转为矩阵（`tuple_to_matrix_*`，部分通过 `create_matrix`）。

---

## 10. 学习小结

Tuple 是 HALCON 的"瑞士军刀"——每个项目都离不开它。**学习优先级**：
1. **必须掌握**：算术（`add/sub/mult/div/pow/sqrt`）、字符串（`string/number/regexp_match`）、集合（`union/intersection`）、容器（`length/sort`）。
2. **常用**：`tuple_mean/deviation/sum/min/max`、`tuple_select/select_mask`、`tuple_concat`。
3. **进阶**：`tuple_at_tuple`、`tuple_environment`、`tuple_str_distance`（Levenshtein）。

**核心要点**：
- HALCON Tuple 是**类型混合**的（int/float/string/handle 可共存），但算术会强制类型提升。
- 字符串字面量必须用单引号 `'foo'`。
- 集合运算将 Tuple 视为**多重集**（不去重），要唯一化需先 `tuple_uniq`。
- `tuple_regexp_match` 返回**整段匹配**；提取子组用 `'subexpression'` 参数。

> **后续阅读**：详情见 `C:\Program Files\MVTec\HALCON-26.05-Progress\doc\html\reference\operators\toc_tuple.html`。