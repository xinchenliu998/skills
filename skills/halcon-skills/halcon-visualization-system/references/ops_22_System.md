# HALCON 算子分类详解：System（系统集成）

> **分类定位**：HALCON 与操作系统、硬件、网络、并行化框架的接口层。
> **算子数量**：约 180 个，覆盖 Compute Devices、Multithreading、Sockets、Serial、Serialized Item、Memory Block、IO Devices 等 15 个子类。
> **HALCON 版本**：26.05.0.0 Progress
> **官方文档**：`toc_system.html`

---

## 1. 概述

System 分类提供了 HALCON 与外部世界的"桥梁"，包括：
- **并行计算**：CPU/GPU 切换、多线程同步原语
- **进程通信**：TCP 套接字、串口、消息队列
- **外设 IO**：工业 IO 设备、共享内存
- **序列化**：跨进程/网络的任意句柄打包
- **算子元信息**：运行时查询参数、算子、错误码
- **错误处理**：try/catch/throw 机制
- **系统参数**：运行时调整 `set_system('parallelize_operators', 'true')`

---

## 2. 应用场景

| 场景 | 关键算子 |
|------|----------|
| **GPU 推理加速** | `query_available_compute_devices` + `init_compute_device` + `activate_compute_device` |
| **并行流水线** | `set_system('parallelize_operators', 'true')` + `par_join` |
| **PLC 通信** | `open_serial` + `read_serial` + `write_serial` |
| **TCP 通信（上位机）** | `open_socket_connect` + `send_data` + `receive_data` |
| **跨进程对象传递** | `serialize_image` + `send_serialized_item` + `deserialize_image` |
| **工业 IO 卡（光栅/编码器）** | `open_io_device` + `control_io_device` |
| **错误恢复** | `try` + `catch` + `get_extended_error_info` |
| **性能监控** | `count_seconds` + `count_relation` |

**典型行业**：跨平台集成项目、深度学习部署、多相机协同、产线联动。

---

## 3. 子分类详解

### 3.1 Compute Devices（GPU 加速，约 15 算子）

- `query_available_compute_devices` — 列出可用设备
- `init_compute_device` — 初始化
- `activate_compute_device` / `deactivate_compute_device`
- `open_compute_device` / `release_compute_device`
- `set_compute_device_param` / `get_compute_device_param`
- `get_compute_device_info`

### 3.2 Multithreading（多线程，约 30 算子）

- 互斥：`create_mutex` / `lock_mutex` / `try_lock_mutex` / `unlock_mutex` / `clear_mutex`
- 条件变量：`create_condition` / `wait_condition` / `timed_wait_condition` / `signal_condition` / `broadcast_condition`
- 事件：`create_event` / `wait_event` / `try_wait_event` / `signal_event`
- 屏障：`create_barrier` / `wait_barrier`
- 并行：`par_join` / `get_current_hthread_id`
- 超时：`set_operator_timeout` / `interrupt_operator`
- 线程属性：`get_threading_attrib`

### 3.3 Sockets（TCP，约 20 算子）

- `open_socket_connect` / `open_socket_accept` / `socket_accept_connect` / `close_socket`
- `send_data/image/region/xld/tuple/serialized_item`
- `receive_data/image/region/xld/tuple/serialized_item`
- `set_socket_param` / `get_socket_param` / `get_socket_descriptor`
- `get_next_socket_data_type`

### 3.4 Serial（串口，6 算子）

`open_serial` / `close_serial` / `read_serial` / `write_serial` / `set_serial_param` / `get_serial_param`

### 3.5 Serialized Item（序列化，覆盖几乎所有 H 句柄，约 30 算子）

`serialize_image/region/xld/tuple/pose/quaternion/dual_quaternion/shape_model/...` + 对应 `deserialize_*`。

### 3.6 Message Queue（消息队列，约 12 算子）

`create_message_queue` / `clear_message_queue` / `enqueue_message` / `dequeue_message` + `create_message` / `set_message_tuple/obj/param` / `get_message_tuple/obj/param`。

### 3.7 IO Devices（工业 IO，8 算子）

`open_io_device` / `close_io_device` / `query_io_device` / `query_io_interface` / `control_io_device` / `control_io_interface` / `set_io_device_param` / `get_io_device_param`。

### 3.8 Memory Block（共享内存，约 7 算子）

`create_memory_block_extern` / `create_memory_block_extern_copy` / `read_memory_block` / `write_memory_block` / `compare_memory_block` / `get_memory_block_ptr` / `image_to_memory_block` / `memory_block_to_image`。

### 3.9 Encrypted Item（加密，4 算子）

`read_encrypted_item` / `write_encrypted_item` / `encrypt_serialized_item` / `decrypt_serialized_item`。

### 3.10 Error Handling（错误，10 算子）

`get_error_text` / `get_extended_error_info` / `set_check` / `get_check` / `dev_error_var` / `dev_get_exception_data` / `throw` / `dev_set_check`。

### 3.11 OS（操作系统，10 算子）

`system_call` / `get_current_dir` / `set_current_dir` / `make_dir` / `remove_dir` / `list_files` / `file_exists` / `copy_file` / `delete_file` / `wait_seconds`。

### 3.12 Database（数据库元信息，约 12 算子）

`get_modules` / `get_param_names` / `get_param_num` / `get_param_types` / `get_param_info` / `query_param_info` / `search_operator` / `get_operator_info` / `query_operator_info` / `get_operator_name` / `query_all_colors` / `reset_obj_db`。

### 3.13 Parameters / Information

`set_system` / `get_system` / `get_system_info` / `count_seconds` / `count_relation`。

---

## 4. 核心算子详解

### 4.1 GPU/CPU 切换（深度学习必备）

```hdevelop
* 1. 查询可用设备
query_available_compute_devices('runtime', Devices)
* Devices: ['cpu', 'gpu:0', 'gpu:1', ...] (取决于硬件)

* 2. 初始化 GPU
init_compute_device('gpu:0', 'runtime', DevID)

* 3. 激活
activate_compute_device(DevID)

* 4. 设置 DL 模型使用 GPU
set_dl_model_param(DLModel, 'device', DevID)

* 5. 推理（自动用 GPU）
apply_dl_model(Image, DLModel, Result)

* 6. 释放（程序退出前）
deactivate_compute_device(DevID)
release_compute_device(DevID)
```

### 4.2 多线程并行（par_join）

```hdevelop
* 自动并行：全局开关（默认 true）
set_system('parallelize_operators', 'true')
set_system('maximum_parallelism', 4)   * 最大 4 核

* 手动 fork-join（子程序并行执行）
par_join(ProcA, ProcB, ProcC)
* ProcA/ProcB/ProcC 是 HDevelop 子程序，无依赖时可并行
```

### 4.3 互斥与条件变量（生产者-消费者）

```hdevelop
* 创建同步原语
create_mutex('mutex1', MutexID)
create_condition('cond1', CondID)

* 生产者
lock_mutex(MutexID)
* 修改共享数据
signal_condition(CondID, MutexID)
unlock_mutex(MutexID)

* 消费者
lock_mutex(MutexID)
try
    while (DataNotReady)
        wait_condition(CondID, MutexID)
    endwhile
    * 读取共享数据
catch (Exception)
    * 异常处理
endtry
unlock_mutex(MutexID)
```

### 4.4 TCP 套接字通信

```hdevelop
* 客户端连接服务端
open_socket_connect('192.168.1.100', 8080, 'protocol', SocketID)

* 发送字符串
send_data(SocketID, 'TRIGGER\n', 'string')

* 接收图像（带协议）
receive_image(Image, SocketID)

* 设置超时
set_socket_param(SocketID, 'timeout', 5000)

* 关闭
close_socket(SocketID)
```

### 4.5 串口通信

```hdevelop
* 打开串口
open_serial('COM3', SerialID)

* 配置参数
set_serial_param(SerialID, 'baud_rate', 115200)
set_serial_param(SerialID, 'data_bits', 8)
set_serial_param(SerialID, 'stop_bits', 1)

* 发送指令
write_serial(SerialID, 'GET_VALUE\n')

* 读取响应（带超时）
set_serial_param(SerialID, 'timeout', 1000)
read_serial(SerialID, 1, 0, Response)

* 关闭
close_serial(SerialID)
```

### 4.6 序列化与跨进程传输

```hdevelop
* 1. 本地序列化（用于跨网络发送）
serialize_image(Image, SerializedItem)

* 2. 通过套接字发送
open_socket_connect('192.168.1.200', 9000, 'protocol', Sock)
send_serialized_item(Sock, SerializedItem)
close_socket(Sock)

* 3. 接收端反序列化
open_socket_accept('9000', 'protocol', AcceptSock)
socket_accept_connect(AcceptSock, 'protocol', Sock2)
receive_serialized_item(Sock2, ReceivedItem)
deserialize_image(ReceivedItem, Image2)
```

### 4.7 错误处理（try/catch）

```hdevelop
set_check('~give_error')   * 让算子错误抛出异常而非立即中断

try
    read_image(Image, 'nonexistent.png')
catch (Exception)
    get_extended_error_info(HErrorInfo)
    get_error_text(HErrorInfo, ErrorText)
    dev_disp_text('错误: ' + ErrorText, 'window', 'top', 'left', 'red', [], [])
endtry
```

---

## 5. HDevelop 示例代码

### 示例 1：GPU 加速的 DL 推理完整流程

```hdevelop
* 查询可用设备
query_available_compute_devices('runtime', Devices)
tuple_length(Devices, NDev)

* 显示设备列表
dev_disp_text('可用计算设备:', 'window', 'top', 'left', 'black', [], [])
for i := 0 to NDev - 1 by 1
    dev_disp_text('  ' + Devices[i], 'window', 20 + i*15, 'left', 'black', [], [])
endfor

* 选 GPU 0
init_compute_device('gpu:0', 'runtime', DevID)
activate_compute_device(DevID)

* 加载 DL 模型
read_dl_model('anomaly_model.hdl', DLModel)
set_dl_model_param(DLModel, 'device', DevID)

* 推理（GPU 加速）
read_image(Image, 'test_image.png')
count_seconds(StartTime)
apply_dl_model(Image, DLModel, Result)
count_seconds(EndTime)
Elapsed := EndTime - StartTime

dev_disp_text('推理耗时: ' + tuple_string(Elapsed, '$.3f') + ' 秒',
              'window', 400, 'left', 'green', [], [])

* 释放
deactivate_compute_device(DevID)
release_compute_device(DevID)
```

### 示例 2：TCP 服务端接收图像并处理

```hdevelop
* 服务端：监听 9000 端口
open_socket_accept('9000', 'protocol', AcceptSock)
dev_disp_text('等待客户端连接...', 'window', 'top', 'left', 'blue', [], [])

socket_accept_connect(AcceptSock, 'protocol', Sock)
dev_disp_text('已连接', 'window', 20, 'left', 'green', [], [])

* 接收图像并显示
while (1)
    receive_image(Image, Sock)
    get_image_size(Image, W, H)
    dev_disp_text('收到图: ' + tuple_string(W, '.0f') + 'x' + tuple_string(H, '.0f'),
                  'window', 40, 'left', 'black', [], [])
    
    * 处理：阈值化
    threshold(Image, Region, 128, 255)
    connection(Region, Connected)
    count_obj(Connected, N)
    
    * 返回处理结果
    send_data(Sock, tuple_string(N, '.0f'), 'string')
endwhile

close_socket(Sock)
close_socket(AcceptSock)
```

### 示例 3：多线程流水线（生产者-消费者）

```hdevelop
* 创建同步对象
create_message_queue('queue1', QueueID)
create_mutex('mtx', MutexID)

* 启动生产者（异步）
par_join(<ProducerProc>)

* 消费者（主线程）
for i := 0 to 100 - 1 by 1
    dequeue_message(QueueID, 'timeout', 5000, MsgID)
    get_message_tuple(MsgID, 'row', Row)
    get_message_tuple(MsgID, 'col', Col)
    * 处理消息...
endfor

clear_message_queue(QueueID)
```

### 示例 4：系统参数与运行时调整

```hdevelop
* 启用算子并行化
set_system('parallelize_operators', 'true')

* 设置最大并行度
set_system('maximum_parallelism', 8)

* 设置算子超时（毫秒）
set_system('operator_timeout', 30000)

* 设置缓存大小
set_system('temporary_mem_cache', 'true')

* 获取当前系统参数
get_system('parallelize_operators', Current)
dev_disp_text('算子并行化: ' + Current, 'window', 'top', 'left', 'black', [], [])
```

---

## 6. 典型工业流水线

### 流水线 A：分布式视觉系统

```
[工控机A]                          [工控机B]
 read_image                         
 ↓                                  
 serialize_image                    
 ↓                                  
 open_socket_connect →→→→→→→→→→→→  receive_serialized_item
 ↓                                  ↓
 GPU推理                             deserialize_image
 ↓                                  ↓
 send_data('OK')                    应用层处理
```

### 流水线 B：GPU 加速 DL 检测完整流程

```
query_available_compute_devices → init → activate
                                       ↓
                       set_dl_model_param(..., 'device', DevID)
                                       ↓
                       apply_dl_model → 推理（GPU）
                                       ↓
                       get_dict_object / get_dict_tuple
                                       ↓
                       解析结果（坐标/置信度）
                                       ↓
                       deactivate → release
```

---

## 7. 常见陷阱与最佳实践

1. **GPU 必须显式激活**：未 `activate_compute_device` 时 DL 推理默认 CPU，可能 OOM 或慢。
2. **多核共享数据竞争**：`lock_mutex` / `unlock_mutex` 必须配对，遗漏会导致死锁。
3. **串口超时阻塞**：`read_serial` 无超时会让程序挂死，必须 `set_serial_param(..., 'timeout', 1000)`。
4. **socket 超时**：`set_socket_param(..., 'timeout', 5000)` 防网络阻塞。
5. **序列化版本兼容**：`serialize_*` 后的数据**跨 HALCON 版本**可能不兼容——保证相同版本。
6. **`set_check('~give_error')` 影响全局**：仅在 try/catch 内临时使用。
7. **`par_join` 仅 HDevelop 有效**：C++/C# 工程中需用 `std::async` 或 HALCON 多线程 API。
8. **`create_mutex` 等系统资源**：必须在退出前 `clear_mutex` 释放（否则句柄泄漏）。

---

## 8. 参数调优指南

| 场景 | 建议 |
|------|------|
| DL 推理慢 | `activate_compute_device` 切换 GPU；`optimize_dl_model_for_inference` 提速 30–60% |
| 多核 CPU 利用不足 | `set_system('parallelize_operators', 'true')` + `set_system('maximum_parallelism', N)` |
| 串口/网络通信超时 | `set_socket_param(..., 'timeout', 5000)` |
| DL 训练 OOM | 减小 `batch_size` 或 `'image_width/height'`；`set_dl_model_param(..., 'device', 'cpu')` |
| 跨进程数据传递 | 用 `serialize_*` + 套接字，比手动拆解字段稳定 |

---

## 9. 相关分类

- **File**：本地文件 IO（`read/write_image` 等）。
- **Develop**：`dev_set_check` / `dev_error_var` 用于调试。
- **Tuple**：所有元组类型可被 `serialize_tuple` 打包。
- **Deep Learning**：`set_dl_model_param(..., 'device', ...)` 直接与 Compute Devices 联动。

---

## 10. 学习小结

System 分类是 HALCON 的"系统调用层"，**学习优先级**：
1. **必学**：`set_system` / `get_system`（运行时配置）、`try/catch/throw`（错误处理）、`par_join`（并行化）。
2. **重要**：`query_available_compute_devices` / `activate_compute_device`（GPU 切换）、`open_socket_connect` / `send_*` / `receive_*`（网络）。
3. **专项**：多线程原语（`create_mutex` / `create_condition`）、`open_io_device`（工业 IO 卡）、`create_memory_block_extern`（C++ 共享内存）。

**核心要点**：
- GPU 推理必须在 `activate_compute_device` 后才能用于 DL 模型。
- `par_join` 仅 HDevelop 有效，C++/C# 中需用 HALCON 多线程算子（`create_mutex` 等）。
- 跨进程对象传递用 `serialize_*` + `send_serialized_item`，稳定且版本兼容。

> **后续阅读**：详见 `C:\Program Files\MVTec\HALCON-26.05-Progress\doc\html\reference\operators\toc_system.html`。