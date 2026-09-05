# HALCON 算子分类详解：Image Source（图像源）

> **分类定位**：通用化的图像输入流接口，支持多路相机、虚拟相机、文件集模拟相机输入。
> **算子数量**：约 10 个。
> **HALCON 版本**：26.05.0.0 Progress
> **官方文档**：`toc_imagesource.html`

---

## 1. 概述

Image Source 分类提供了**统一**的图像输入接口——无论数据来自真实相机、文件集、还是虚拟生成，都通过同一套算子（`connect_image_source` / `fetch_from_image_source` 等）操作。

### 核心思想

```
[真实相机] ──┐
[图像文件] ──┼──→ connect_image_source → fetch_from_image_source → Image
[网络流]  ──┤
[虚拟生成] ──┘
```

这让上层业务代码**与具体数据源无关**，是离线调试（用文件模拟相机）和多相机协同项目的关键。

---

## 2. 应用场景

| 场景 | 说明 |
|------|------|
| **离线调试** | 把一批图像作为"虚拟相机流"，模拟真实采集环境 |
| **多相机管理** | 统一接口同时管理 GigE / USB3 / 文件相机 |
| **图像批量回放** | 顺序读取目录中的图像 |
| **网络相机** | 通过 RTP/RTSP 流拉取图像 |
| **嵌入式集成** | 相机 SDK 通过 Image Source 适配 HALCON |

---

## 3. 子分类详解

### 3.1 连接管理

- `connect_image_source(SourceName, SourceParamNames, SourceParamValues → SourceHandle)`
- `disconnect_image_source(SourceHandle)`

### 3.2 控制

- `start_image_source(SourceHandle → SourceStatus)`
- `stop_image_source(SourceHandle → SourceStatus)`
- `control_image_source(SourceHandle, CtrlParamName, CtrlParamValue → SourceStatus)`
- `set_image_source_param(SourceHandle, ParamName, ParamValue)`
- `get_image_source_param(SourceHandle, ParamName, ParamValue)`

### 3.3 抓取

- `fetch_from_image_source(SourceHandle, Mode → Image)`
- `snap_from_image_source(SourceHandle → Image)`

### 3.4 状态

- `get_image_source_state(SourceHandle → State)`
- `is_image_source_alive(SourceHandle → IsAlive)`
- `image_source_available(SourceHandle, TimeOut → IsAvailable)`

---

## 4. 核心算子详解

### 4.1 连接与释放（2 个）

| 算子 | 签名 | 用途 |
|------|------|------|
| `connect_image_source` | `connect_image_source(SourceName, ParamNames, ParamValues → SourceHandle)` | 打开图像源 |
| `disconnect_image_source` | `disconnect_image_source(SourceHandle)` | 关闭 |

### 4.2 控制（3 个）

| 算子 | 签名 | 用途 |
|------|------|------|
| `start_image_source` | `start_image_source(SourceHandle → Status)` | 启动抓取 |
| `stop_image_source` | `stop_image_source(SourceHandle → Status)` | 停止 |
| `control_image_source` | `control_image_source(SourceHandle, Name, Value → Status)` | 发送控制命令 |

### 4.3 抓取（2 个）

| 算子 | 签名 | 用途 |
|------|------|------|
| `fetch_from_image_source` | `fetch_from_image_source(SourceHandle, Mode → Image)` | 拉取一帧（同步/异步） |
| `snap_from_image_source` | `snap_from_image_source(SourceHandle → Image)` | 单帧触发 |

### 4.4 参数查询（2 个）

| 算子 | 签名 | 用途 |
|------|------|------|
| `set_image_source_param` | `set_image_source_param(SourceHandle, Name, Value)` | 设置参数 |
| `get_image_source_param` | `get_image_source_param(SourceHandle, Name, Value)` | 读取参数 |

### 4.5 状态（3 个）

| 算子 | 签名 | 用途 |
|------|------|------|
| `get_image_source_state` | `get_image_source_state(SourceHandle → State)` | 当前状态 |
| `is_image_source_alive` | `is_image_source_alive(SourceHandle → IsAlive)` | 是否在线 |
| `image_source_available` | `image_source_available(SourceHandle, Timeout → IsAvailable)` | 数据是否就绪 |

---

## 5. HDevelop 示例代码

### 示例 1：用文件模拟相机流

```hdevelop
* 1. 连接文件型图像源
connect_image_source('FileImageSource', ['directory', 'pattern'], \
                     ['images/', '*.png'], SourceHandle)

* 2. 启动
start_image_source(SourceHandle, Status)
dev_disp_text('图像源已启动', 'window', 'top', 'left', 'green', [], [])

* 3. 循环抓取（每按一次空格取一帧）
count := 0
while (count < 100)
    try
        fetch_from_image_source(SourceHandle, 'sync', Image)
        count := count + 1
        
        * 处理
        threshold(Image, Region, 128, 255)
        area_center(Region, Area, _, _)
        
        dev_disp_text('帧 ' + count + ', 面积: ' + Area, 'window', count*20, 'left', 'black', [], [])
    catch (Exception)
        break   * 流结束
    endtry
endwhile

* 4. 关闭
stop_image_source(SourceHandle, _)
disconnect_image_source(SourceHandle)
```

### 示例 2：异步抓取（高性能）

```hdevelop
connect_image_source('GigEVision', ['name', 'timeout'], ['cam1', 5000], Src)
start_image_source(Src, _)

* 异步抓取（不等返回）
fetch_from_image_source(Src, 'async', _)

* 同时做其他处理（重叠 IO 与 CPU）
process_previous_frame()

* 同步等待结果
fetch_from_image_source(Src, 'wait', Image2)

stop_image_source(Src, _)
disconnect_image_source(Src)
```

### 示例 3：触发模式（硬件触发模拟）

```hdevelop
* 设置为外部触发模式
connect_image_source('FileImageSource', \
                     ['directory', 'pattern', 'trigger_mode'], \
                     ['images/', '*.png', 'manual'], Src)

start_image_source(Src, _)

* 软件触发抓取（模拟硬件触发信号）
for i := 1 to 10 by 1
    wait_seconds(0.5)   * 模拟触发间隔
    snap_from_image_source(Src, Image)   * 触发+抓取
    * 处理...
endfor

stop_image_source(Src, _)
disconnect_image_source(Src)
```

### 示例 4：查询状态与错误恢复

```hdevelop
connect_image_source('NetworkImageSource', ['url', 'port'], \
                     ['rtsp://192.168.1.50/stream', 554], Src)
start_image_source(Src, _)

* 查询参数
get_image_source_param(Src, 'frame_rate', FPS)
get_image_source_param(Src, 'resolution', Res)
dev_disp_text('FPS: ' + FPS + ', Res: ' + Res, 'window', 'top', 'left', 'black', [], [])

* 监测是否在线
while (true)
    is_image_source_alive(Src, Alive)
    if (not Alive)
        dev_disp_text('连接断开，尝试重连...', 'window', 'top', 'left', 'red', [], [])
        disconnect_image_source(Src)
        wait_seconds(2)
        connect_image_source('NetworkImageSource', ['url', 'port'], \
                             ['rtsp://192.168.1.50/stream', 554], Src)
        start_image_source(Src, _)
    endif
    
    fetch_from_image_source(Src, 'sync', Image)
    * 处理...
endwhile
```

---

## 6. 典型工业流水线

### 流水线 A：离线调试（文件模拟相机）

```
开发期：                           生产期：
connect_image_source('File...')    open_framegrabber('GigE...')
        ↓                                  ↓
fetch_from_image_source            grab_image
        ↓                                  ↓
业务逻辑（不变）                    业务逻辑（不变）
```

### 流水线 B：多相机协同

```
* 相机 A
connect_image_source('GigE_A', [...], SrcA)
start_image_source(SrcA, _)

* 相机 B
connect_image_source('GigE_B', [...], SrcB)
start_image_source(SrcB, _)

* 同步抓取
par_join(
    <ProcCameraA(SrcA)>,
    <ProcCameraB(SrcB)>
)

stop_image_source(SrcA, _)
stop_image_source(SrcB, _)
disconnect_image_source(SrcA)
disconnect_image_source(SrcB)
```

---

## 7. 常见陷阱与最佳实践

1. **`fetch_from_image_source` 的 Mode**：`'sync'` 阻塞等待；`'async'` 不阻塞；`'wait'` 等到有数据。
2. **图像源必须先 `start_image_source`**：未启动时 `fetch_*` 通常会等待或失败。
3. **`connect_image_source` 的 SourceName**：HALCON 自带 `'FileImageSource'`、`'GigEVision'`、`'GenICamTL'` 等。
4. **流结束处理**：文件型源读到末尾会抛异常，需 `try/catch`。
5. **网络源超时**：`fetch_from_image_source` 默认无超时，需 `set_image_source_param(Src, 'timeout', 5000)`。
6. **断线重连**：网络源易断，需 `is_image_source_alive` 监测并重连。
7. **触发模式**：硬件触发（光电传感器、编码器）需 `set_image_source_param(Src, 'trigger_mode', 'external')`。

---

## 8. 参数调优指南

| 场景 | 建议 |
|------|------|
| 离线调试 | `'FileImageSource'` + 指定目录 + 通配符 |
| 高速采集 | 用 `'async'` + 重叠 IO，避免 CPU 等待 |
| 网络相机断线 | `is_image_source_alive` 监测 + 自动重连 |
| 帧率控制 | `set_image_source_param(Src, 'frame_rate', N)` 限制最大帧率 |
| 触发延迟 | 硬件触发设 `'trigger_mode', 'external'` |

---

## 9. 相关分类

- **Image / Acquisition**：经典帧抓取（`open_framegrabber` + `grab_image`）。
- **System / Multithreading**：`par_join` 并行处理多源数据。
- **System / Sockets**：网络流型源底层用 socket。

---

## 10. 学习小结

Image Source 分类是"统一图像输入层"。**学习优先级**：
1. **必学**：`connect_image_source` / `start_image_source` / `fetch_from_image_source` / `stop_image_source` / `disconnect_image_source`。
2. **重要**：`set_image_source_param`、`snap_from_image_source`、`is_image_source_alive`。
3. **专项**：`fetch_from_image_source` 的 `'sync'` / `'async'` / `'wait'` 模式。

**核心要点**：
- 用文件模拟相机是离线调试的黄金方法——同一套业务代码可在文件/相机间无缝切换。
- **生产代码建议直接用 `open_framegrabber`**（性能更好），Image Source 主要用于通用化和离线调试。
- 异步模式 `'async'` 可重叠 IO 与 CPU，提升多相机协同吞吐量。

> **后续阅读**：详见 `C:\Program Files\MVTec\HALCON-26.05-Progress\doc\html\reference\operators\toc_imagesource.html`。