---
name: xamlbehaviors-wpf-mvvm
description: 用 Microsoft.Xaml.Behaviors.Wpf（XamlBehaviors WPF / XAML Behaviors）做 MVVM 声明式绑定，消除 code-behind 事件处理器，让 ViewModel 与 View 彼此无感、彻底解耦。当用户提到 XAML Behaviors、XamlBehaviorsWpf、WPF MVVM 绑定、避免直接用事件（Click/事件 handler）、Interaction.Triggers / EventTrigger / InvokeCommandAction / CallMethodAction / DataStateBehavior / GoToStateAction / ConditionBehavior 这类触发器、行为、动作，想把 Click 或 Loaded 等事件换成声明式交互，或者想写不依赖事件、VM 不认识 View 的 WPF 交互代码时，一定要使用本 skill。即使用户没明确说 “behavior”，只要涉及 WPF 的声明式命令绑定、触发器、视觉状态切换、交互动作，也应优先使用本 skill。
compatibility:
  - "Microsoft.Xaml.Behaviors.Wpf (NuGet) — WPF 桌面应用"
  - "framework-neutral ICommand / RelayCommand；也可对接 CommunityToolkit.Mvvm、Prism 等"
---

# XamlBehaviorsWpf MVVM 声明式交互（事件自由）

## 为什么这个 skill 存在

WPF 传统写法是 `Click="SaveButton_Click"`：把 UI 交互写进 code-behind 事件处理器。这会让 View 和 ViewModel 互相纠缠——VM 里不得不引用 `Button`/`Window` 等 View 类型，代码难以测试、复用、迁移。

XamlBehaviorsWpf 提供一种**声明式**写法：整段交互动作直接写在 XAML 里，用 `Interaction.Triggers` + `EventTrigger` + `InvokeCommandAction` 等，把「UI 事件」映射到「ViewModel 上的命令」。于是：

- **View** 只声明「这个按钮点击时调用那个命令」，不持有 VM 类型引用，不向 VM 传 View 对象或事件参数。
- **ViewModel** 只暴露 `ICommand` 和可绑定属性，完全不知道「按钮」「点击」这些 View 概念的存在。

这正是「VM 和 V 无感」：两边只通过绑定的 `ICommand` / 属性契约通信，谁都不需要知道对方的内部实现。

> **核心铁律**：能用声明式触发器 / 行为 / 动作表达的交互，就绝不写 code-behind 事件处理器。写完交互后，VM 里不得出现 `Button`、`RoutedEventArgs`、`sender` 等 View 概念。

## 环境准备

```xml
<Window ...
    xmlns:i="http://schemas.microsoft.com/xaml/behaviors">
```

- NuGet 包：`Microsoft.Xaml.Behaviors.Wpf`
- 命名空间别名 `i` 是惯用写法（也有项目用 `behaviors:`）。别名叫什么都行，`i` 最通用，下文统一用它。

## 核心工作流：把事件处理器翻译成声明式命令

**第 0 步：找出要替代的 code-behind 事件处理器**

```xml
<Button x:Name="SaveButton" Click="SaveButton_Click" Content="保存" />   <!-- 想干掉这个 -->
```

```csharp
private void SaveButton_Click(object sender, RoutedEventArgs e) { vm.Save(); }  // 要删掉的
```

**第 1 步：在 ViewModel 上加一个命令**

```csharp
public ICommand SaveCommand { get; }
public MainViewModel() { SaveCommand = new RelayCommand(Save); }
private void Save() { /* 业务逻辑 */ }
```

（框架中立的 RelayCommand 见 `references/mvvm-patterns.md`；若用 CommunityToolkit.Mvvm / Prism，用它们的 `[RelayCommand]` / `DelegateCommand` 也能无缝对接，原理相同。）

**第 2 步：用触发器替换事件**

```xml
<Button Content="保存">
  <i:Interaction.Triggers>
    <i:EventTrigger EventName="Click">
      <i:InvokeCommandAction Command="{Binding SaveCommand}" />
    </i:EventTrigger>
  </i:Interaction.Triggers>
</Button>
```

**第 3 步：删掉 code-behind 处理器**，重新编译。完成。

以上就是全部核心。剩下的只是两个分支问题：**要不要传参**、**要不要根据数据切状态**。往下看一张速查表即可对号入座。

## 选择哪个组件（速查）

| 你的需求 | 用这些 |
|---|---|
| 某事件触发 → 调用 VM 命令 | `EventTrigger` + `InvokeCommandAction` |
| 事件触发 → 直接调 VM 的方法（不经命令） | `EventTrigger` + `CallMethodAction` |
| 给命令传参数 | `CommandParameter` + `RelayCommand<T>` |
| 数据等于某值 → 切换 VisualState | `DataStateBehavior` |
| 属性变化 → 触发动作 | `PropertyChangedTrigger` |
| 定时触发 | `TimerTrigger` |
| 键组合触发 | `KeyTrigger` |
| 改元素属性 / 放动画 / 放声音 / 打开链接 / 移除元素 | `ChangePropertyAction` / `ControlStoryboardAction` / `PlaySoundAction` / `LaunchUriOrFileAction` / `RemoveElementAction` |
| 拖拽 / 平移缩放 / 流体动画 | `MouseDragElementBehavior` / `TranslateZoomRotateBehavior` / `FluidMoveBehavior` |
| 满足逻辑条件才允许动作 | `ConditionBehavior` |
| 手动切到某个视觉状态（非数据驱动） | `GoToStateAction` |

## 两个最容易踩的坑

1. **别把事件参数塞进 VM。** VM 里冒出 `RoutedEventArgs`、`sender`，就破坏了「无感」。要传就传**值**而不是事件对象：`CommandParameter="{Binding Text, ElementName=InputBox}"` 传的是 `string`；`CommandParameter="{Binding SelectedItem, ElementName=List}"` 传的是选中项。极少数确实要拿 event args 的场合，用 `references/mvvm-patterns.md` 里的封装做法，**不要直接把 `e` 交给 VM**。

2. **`i:Interaction.Triggers` 一般挂在目标元素上。** 想让哪个控件响应，就把 `Interaction.Triggers` 放进那个控件的标签里；`EventTrigger` 的 `EventName` 是该控件真正会触发的事件名（如 `Click`、`MouseLeftButtonDown`、`Loaded`）。事件默认由该元素发生，如需监听别处的路由事件，可加 `SourceObject`。

## 深入阅读（渐进式披露：按需读取）

- `references/triggers.md` — 全部触发器（EventTrigger / DataTrigger / PropertyChangedTrigger / TimerTrigger / KeyTrigger）逐一讲解与示例
- `references/actions.md` — 全部动作，含 `InvokeCommandAction` 的参数传递详解
- `references/behaviors.md` — 全部行为，含 `DataStateBehavior`、`ConditionBehavior` 条件表达式
- `references/mvvm-patterns.md` — 核心规约：VM/V 解耦细节、framework-neutral 命令实现、自定义 Behavior、参数传递边界
