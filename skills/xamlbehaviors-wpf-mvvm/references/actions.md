# 动作（Actions）

> 动作（Action）是触发器（Trigger）触发时执行的「行为」。触发器决定时机，动作决定结果。声明式地组合它们，即可替代几乎全部 code-behind 事件处理器。
>
> **MVVM 优先级**：`InvokeCommandAction`（连命令，保证 VM 无感）> `CallMethodAction`（连 VM 方法）> `ChangePropertyAction` 等纯 View 动作（只改 UI）。

## 目录

1. [InvokeCommandAction：调 VM 命令（首选）](#1-invokecommandaction调-vm-命令首选)
2. [InvokeCommandAction 参数传递详解](#2-invokecommandaction-参数传递详解)
3. [CallMethodAction：调 VM 方法](#3-callmethodaction调-vm-方法)
4. [ChangePropertyAction：改属性 / 增量 / 动画](#4-changepropertyaction改属性--增量--动画)
5. [ControlStoryboardAction：控制故事板](#5-controlstoryboardaction控制故事板)
6. [GoToStateAction：切视觉状态](#6-gotostateaction切视觉状态)
7. [其他轻量动作](#7-其他轻量动作)

---

## 1. InvokeCommandAction：调 VM 命令（首选）

触发时执行指定 `Command`，可选 `CommandParameter`。这是「把 UI 事件连到 VM 命令」的标准通道，也是维持 VM 无感的关键（VM 只看到 `ICommand`）。

```xml
<Button Content="新增"
  <i:Interaction.Triggers>
    <i:EventTrigger EventName="Click">
      <i:InvokeCommandAction Command="{Binding AddItemCommand}"
                             CommandParameter="{Binding SelectedItem}" />
    </i:EventTrigger>
  </i:Interaction.Triggers>
</Button>
```

属性：

- `Command`：要执行的命令，绑定到 VM 的 `ICommand`。
- `CommandParameter`：传给 `Execute` 的参数，可以是任意值或绑定结果。
- `IsEnabled`：`false` 时即使触发也不执行（等价于提前返回）。

## 2. InvokeCommandAction 参数传递详解

**原则：传值，别传控件/事件对象**（详见 `mvvm-patterns.md` 第 3 节）。参数是普通数据，VM 才能无感。

| 想传的东西 | 写法 |
|---|---|
| 固定值 | `CommandParameter="Save"` |
| 当前 DataContext 项 | `CommandParameter="{Binding}"` |
| 别的控件某属性 | `CommandParameter="{Binding Text, ElementName=SearchBox}"` |
| 列表选中项 | `CommandParameter="{Binding SelectedItem, ElementName=ItemsList}"` |
| 需要绑定的对象 | `CommandParameter="{Binding MyItem}"` |

若没用 `CommandParameter` 也想触达「触发它的元素」，可写 `CommandParameter="{Binding DataContext}"` 区分。而 `EventTrigger` 的 `SourceObject` 可拿到事件来源元素，用于 `CommandParameter` 里做 `ElementName` 绑定源。

> 带参数的命令记得用 `RelayCommand<T>`（参 `mvvm-patterns.md` 第 1 节）；VM 里 `Execute(object?)` 收到的是 `CommandParameter` 的求值结果。

## 3. CallMethodAction：调 VM 方法

直接调用 `TargetObject` 上的方法，绕过命令。适合 VM 上已有的普通方法，或需要传参更直接，但**在 MVVM 中通常不如命令干净**——除非该动作本质是一次性操作、且不需要 `CanExecute`。

```xml
<Button Content="计数">
  <i:Interaction.Triggers>
    <i:EventTrigger EventName="Click">
      <i:CallMethodAction TargetObject="{Binding DataContext}" MethodName="IncrementCount" />
    </i:EventTrigger>
  </i:Interaction.Triggers>
</Button>
```

要点：

- `TargetObject`：要调用方法所在的对象，通常 `{Binding DataContext}` 或 `{Binding}`（绑定到 VM）。
- `MethodName`：方法名（必须是 public、无参数或匹配签名）。
- 这是**方法调用**，不是命令，因此没有 `CanExecute`；需要控制可用性时用 `InvokeCommandAction`。

## 4. ChangePropertyAction：改属性 / 增量 / 动画

修改指定对象的属性。很适合纯 View 状态切换（显隐、颜色、文本），无需动 VM。

```xml
<Button Content="只读切换">
  <i:Interaction.Triggers>
    <i:EventTrigger EventName="Click">
      <i:ChangePropertyAction TargetName="InputBox" PropertyName="IsReadOnly" Value="True" />
    </i:EventTrigger>
  </i:Interaction.Triggers>
</Button>
```

属性：

- `TargetObject` / `TargetName`：目标元素（`TargetName` 用 x:Name 更直观）。
- `PropertyName`：要改的属性名。
- `Value`：新值。
- `Increment`：`true` 时先尝试按 `Value` 做增量（如数值 +Value）。
- `Duration`：设置后在旧值到新值之间用动画过渡。

## 5. ControlStoryboardAction：控制故事板

对指定 Storyboard 执行控制（开始/暂停/停止/继续）。适合纯动画。

```xml
<Button Content="播放动画">
  <i:Interaction.Triggers>
    <i:EventTrigger EventName="Click">
      <i:ControlStoryboardAction TargetName="MyStoryboard" ControlStoryboardOption="Play"/>
    </i:EventTrigger>
  </i:Interaction.Triggers>
</Button>
```

- `TargetName`：DataTemplate/Resources 里定义的 `Storyboard` 名字。
- `ControlStoryboardOption`：`Play` / `Stop` / `Pause` / `Resume`。

## 6. GoToStateAction：切视觉状态

把 `TargetObject`/`TargetName` 指定的元素切到某个 `StateName`（VisualState），可选 `UseTransitions` 控制是否播放过渡动画。适合「手动、非数据驱动」地切状态。

```xml
<Button Content="切到禁用态">
  <i:Interaction.Triggers>
    <i:EventTrigger EventName="Click">
      <i:GoToStateAction StateName="Disabled" TargetObject="{Binding ElementName=SampleButton}"/>
    </i:EventTrigger>
  </i:Interaction.Triggers>
</Button>
```

- `StateName`：视觉状态名。
- `TargetObject` / `TargetName`：承载 `VisualStateGroups` 的元素。
- `UseTransitions`：默认 `true` 播放过渡。

> 想要「根据数据自动切状态」，用 `DataStateBehavior`（behaviors.md）更贴合，无需写死触发条件。

## 7. 其他轻量动作

- **`LaunchUriOrFileAction`**：打开 URL 或本地文件。`Path`（URI 或路径）。
  ```xml
  <i:EventTrigger EventName="Click">
    <i:LaunchUriOrFileAction Path="https://github.com/Microsoft/XamlBehaviorsWpf" />
  </i:EventTrigger>
  ```
- **`PlaySoundAction`**：播放音频文件。`Source`（音频文件路径）。
  ```xml
  <i:EventTrigger EventName="MouseLeftButtonDown">
    <i:PlaySoundAction Source="ding.wav" />
  </i:EventTrigger>
  ```
- **`RemoveElementAction`**：把 `TargetObject`/`TargetName` 指定的元素从视觉树移除。
  ```xml
  <i:EventTrigger EventName="Click">
    <i:RemoveElementAction TargetName="AdBanner" />
  </i:EventTrigger>
  ```
- **`SetDataStoreValueAction`**：往 `DataStore`（`Interaction.DataStore`）里写入一个值，供其它 `DataTrigger`/`DataStoreChangedTrigger` 读取。可用于跨元素轻量共享状态。
