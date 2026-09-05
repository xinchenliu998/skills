# HALCON 算子分类详解：Control（HDevelop 控制流）

> **分类定位**：HDevelop 脚本语言的控制流保留字/伪算子。
> **算子数量**：约 25 个。
> **HALCON 版本**：26.05.0.0 Progress
> **官方文档**：`toc_control.html`

---

## 1. 概述

Control 分类是 **HDevelop 脚本语言**（`.hdev` 或 `.hscript`）的控制流原语，包括：
- **循环**：`for` / `while` / `repeat ... until`
- **分支**：`if` / `ifelse` / `switch ... case`
- **异常**：`try ... catch ... throw`
- **退出**：`break` / `continue` / `return` / `exit` / `stop`
- **赋值**：`:=` / `+=` / `-=` 等
- **作用域**：`global` / `assign`

> **重要**：这些"算子"**仅 HDevelop IDE 有效**，导出为 C++/C# 时不会编译——需要用对应宿主语言的控制流语句（`if` / `for` / `while` / `try` 等）替代。

---

## 2. 应用场景

| 场景 | 说明 |
|------|------|
| **图像批次处理** | `for` 循环遍历图像列表 |
| **条件分支** | `if` 判断检测结果是否合格 |
| **多分支处理** | `switch` 根据产品类型选择不同 pipeline |
| **异常恢复** | `try/catch` 捕获 `read_image` 找不到文件的错误 |
| **调试中断** | `stop` 让程序暂停 |
| **早退** | `return` 从子程序返回 |

---

## 3. 子分类详解

### 3.1 循环控制

- `for Index := Start to End by Step` ... `endfor`
- `while (Condition)` ... `endwhile`
- `repeat` ... `until (Condition)`
- `break` — 跳出循环
- `continue` — 跳过本轮剩余代码

### 3.2 分支控制

- `if (Condition)` ... `endif`
- `ifelse (Condition)` ... `else` ... `endif`
- `switch (Expression)` ... `case Value:` ... `default:` ... `endswitch`

### 3.3 异常处理

- `try` ... `catch (Exception)` ... `endtry`
- `throw (Exception)` — 主动抛出异常

### 3.4 程序控制

- `return` — 从子程序返回（带返回值）
- `exit` — 退出 HDevelop
- `stop` — 暂停执行（调试）
- `halt` — 终止

### 3.5 赋值与作用域

- `:=` — 赋值
- `+=`, `-=`, `*=`, `/=` — 复合赋值
- `global var := value` — 全局变量
- `assign` — 静态变量（跨调用）

---

## 4. 核心算子详解

### 4.1 for 循环

```hdevelop
for i := 0 to 10 by 1
    * 循环体
endfor

* 步长为负
for i := 10 to 0 by -1
    * 反向
endfor

* Tuple 遍历
tuple := [1, 2, 3, 4, 5]
for i := 0 to |tuple| - 1 by 1
    val := tuple[i]
endfor
```

### 4.2 while 循环

```hdevelop
while (counter < 100 and not_quit)
    * 循环体
    counter := counter + 1
endwhile
```

### 4.3 repeat-until（先执行后判断）

```hdevelop
repeat
    grab_image(Image, AcqHandle)
    threshold(Image, Region, 128, 255)
    count_obj(Region, N)
until (N > 5)
```

### 4.4 if 分支

```hdevelop
if (MeanD > 12.5 or MeanD < 11.5)
    dev_disp_text('NG: 直径超差', 'window', 'top', 'left', 'red', [], [])
elseif (MeanD > 12.2 and MeanD < 12.3)
    dev_disp_text('OK: 中心值', 'window', 'top', 'left', 'green', [], [])
else
    dev_disp_text('OK', 'window', 'top', 'left', 'black', [], [])
endif
```

### 4.5 switch 多分支

```hdevelop
switch (ProductType)
    case 1:
        dev_disp_text('A 型产品', 'window', 'top', 'left', 'blue', [], [])
        break
    case 2:
        dev_disp_text('B 型产品', 'window', 'top', 'left', 'green', [], [])
        break
    case 3:
    case 4:
        dev_disp_text('C/D 型产品', 'window', 'top', 'left', 'magenta', [], [])
        break
    default:
        dev_disp_text('未知型号', 'window', 'top', 'left', 'red', [], [])
endswitch
```

### 4.6 try-catch 异常处理

```hdevelop
set_check('~give_error')

try
    read_image(Image, FileName)
    threshold(Image, Region, 128, 255)
catch (Exception)
    get_error_text(Exception, ErrorText)
    dev_disp_text('错误: ' + ErrorText, 'window', 'top', 'left', 'red', [], [])
    Image := 0   * 空图像占位
endtry
```

### 4.7 子程序与返回

```hdevelop
* 子程序定义
proc MeasurePart(Image : Row, Col, Radius : MeanR)
    threshold(Image, Region, 128, 255)
    connection(Region, Connected)
    select_shape(Connected, Selected, 'area', 'and', 1000, 99999)
    area_center(Selected, _, Row, Col)
    fit_circle_contour_xld(...)
    ...
    return ()
endproc
```

---

## 5. HDevelop 示例代码

### 示例 1：批量图像 + 累计统计

```hdevelop
* 初始化累加变量
TotalArea := 0
NumImgs := 0

list_files('images/', 'files', Files)
for i := 0 to |Files| - 1 by 1
    try
        read_image(Img, Files[i])
        threshold(Img, Region, 128, 255)
        connection(Region, Connected)
        area_center(Connected, Area, _, _)
        TotalArea := TotalArea + Area
        NumImgs := NumImgs + 1
    catch (Exception)
        continue    * 跳过错误图
    endtry
endfor

if (NumImgs > 0)
    AvgArea := TotalArea / NumImgs
    dev_disp_text('平均面积: ' + tuple_string(AvgArea, '$.2f'), 'window', 'top', 'left', 'black', [], [])
endif
```

### 示例 2：多阶段条件分支

```hdevelop
find_shape_model(Image, ModelID, rad(-10), rad(20), 0.7, 1, 0.5, \
                 'least_squares', 0, 0.8, Row, Col, Angle, Score)

if (|Score| = 0)
    dev_disp_text('NG: 未找到目标', 'window', 'top', 'left', 'red', [], [])
    return ()
endif

if (Score[0] < 0.85)
    dev_disp_text('NG: 匹配分数过低', 'window', 'top', 'left', 'red', [], [])
    return ()
endif

* 匹配成功
dev_disp_text('OK: ' + tuple_string(Score[0], '$.2f'), 'window', 'top', 'left', 'green', [], [])

* 仿射对齐
vector_angle_to_rigid(RefRow, RefCol, 0, Row[0], Col[0], Angle[0], HomMat2D)
affine_trans_image(Image, Aligned, HomMat2D, 'constant', 'false')
```

### 示例 3：while 实现查找最优阈值

```hdevelop
BestN := 0
BestT := 128
T := 50

while (T < 200)
    threshold(Image, Region, T, 255)
    connection(Region, Connected)
    count_obj(Connected, N)
    
    if (abs(N - TargetN) < abs(BestN - TargetN))
        BestN := N
        BestT := T
    endif
    
    T := T + 1
endwhile

dev_disp_text('最优阈值: ' + BestT + ' (N=' + BestN + ')', 'window', 'top', 'left', 'black', [], [])
```

### 示例 4：嵌套异常处理

```hdevelop
set_check('~give_error')

try
    open_framegrabber('GigEVision', 1, 1, 0, 0, 0, 0, 'default', \
                      -1, 'default', 'default', 'default', 'camera1', \
                      -1, -1, AcqHandle)
    
    try
        grab_image(Image, AcqHandle)
    catch (GrabException)
        dev_disp_text('采集失败', 'window', 'top', 'left', 'red', [], [])
        return ()
    endtry
    
catch (OpenException)
    dev_disp_text('相机初始化失败，使用文件替代', 'window', 'top', 'left', 'orange', [], [])
    read_image(Image, 'fallback.png')
endtry
```

---

## 6. 典型工业流水线

### 流水线 A：批量产品检测

```
for i := 0 to NumProducts - 1
    grab_image(Image, AcqHandle)              ← 采集
    apply_metrology_model(Image, MetroH)      ← 测量
    
    get_metrology_object_result(..., Radius)
    
    if (|Radius| = 0 or abs(Radius[0] - 12.0) > 0.05)
        NG_count := NG_count + 1
        disp_text('NG')
        continue
    endif
    
    OK_count := OK_count + 1
endfor

disp_text('OK=' + OK_count + ', NG=' + NG_count)
```

### 流水线 B：状态机式流程控制

```
state := 'INIT'
while (state <> 'QUIT')
    switch (state)
        case 'INIT':
            init_system()
            state := 'IDLE'
            break
        case 'IDLE':
            wait_for_trigger()
            state := 'INSPECT'
            break
        case 'INSPECT':
            inspect_one()
            state := 'IDLE'
            break
    endswitch
endwhile
```

---

## 7. 常见陷阱与最佳实践

1. **HDevelop 索引 1-based vs Tuple 0-based**：`for i := 1 to N` 遍历对象用 `select_obj(Objects, X, i-1)`。
2. **`set_check('~give_error')` 必须**：否则算子错误会**直接终止程序**，无法 catch。
3. **`try` 块粒度**：太粗会吞掉真实错误；太细会重复。
4. **`break` vs `continue`**：前者退出整个循环；后者跳过本轮剩余。
5. **`switch` 必须 `break` 否则 fall-through**：与 C 默认 fall-through 不同。
6. **全局变量 `global`**：仅 HDevelop 调试时方便，生产代码建议用参数传递。
7. **`stop` / `halt` / `exit` 区别**：`stop` 暂停（继续执行）；`halt` 终止 HDevelop；`exit` 退出程序。
8. **导出后不可用**：导出 C++/C# 工程时所有 Control 算子被丢弃，需手写循环和异常处理。

---

## 8. 参数调优指南

| 场景 | 建议 |
|------|------|
| 大循环性能 | 避免循环内 `read_image`，用 `read_sequence` 一次读 |
| 嵌套异常 | 内层 catch 处理特定错误，外层 catch 处理全局错误 |
| 调试 | 大量用 `dev_disp_text` 输出中间值，配合 `stop` 暂停 |
| 状态机 | `switch` + `state` 变量实现清晰的状态机 |
| 多条件 | `if (A and B) or (C and not D)` 用括号明确优先级 |

---

## 9. 相关分类

- **System / Error Handling**：`try/catch` 配合 `set_check`。
- **System / OS**：`wait_seconds` 用于循环中延时。
- **Develop**：`dev_error_var` / `dev_get_exception_data` 调试异常。

---

## 10. 学习小结

Control 分类是"脚本语言层"。**学习优先级**：
1. **必学**：`for`、`if`、`while`、`try/catch`。
2. **重要**：`switch`、`repeat-until`、`break`/`continue`。
3. **专项**：`global`、`throw`、异常嵌套。

**核心要点**：
- HDevelop 索引从 **1 开始**（与 C/Python 的 0-based 不同）。
- **`set_check('~give_error')` 是 try/catch 的前提**。
- `switch` 必须显式 `break`，否则 fall-through。
- 导出为 C++/C# 时**所有 Control 算子被丢弃**，需手动重写为宿主语言的控制流。

> **后续阅读**：详见 `C:\Program Files\MVTec\HALCON-26.05-Progress\doc\html\reference\operators\toc_control.html`。