# MVVM 核心规约：VM/V 无感

> 本文件回答两个问题：① 一份可复用的 framework-neutral 命令怎么写；② 怎样保持 VM 与 V 彻底解耦（「无感」），以及哪些情况下允许少量 code-behind 而不算破坏解耦。

## 目录

1. [Framework-neutral 命令实现](#1-framework-neutral-命令实现)
2. [VM/V 无感规约（为什么 & 怎么做）](#2-vmv-无感规约)
3. [参数传递边界：传值，别传事件对象](#3-参数传递边界)
4. [「局部允许 code-behind」的例外](#4-局部允许-code-behind的例外)
5. [自定义行为 / 事件转命令封装](#5-自定义行为--事件转命令封装)

---

## 1. Framework-neutral 命令实现

不绑特定 MVVM 库时，用一个 `RelayCommand` 和带参数的 `RelayCommand<T>` 就够。它们做的事很简单：把 `Execute/CanExecute` 委托给 `Action` / `Action<T>` 和谓词。

```csharp
using System;
using System.Windows.Input;

// 无参数命令
public sealed class RelayCommand : ICommand
{
    private readonly Action _execute;
    private readonly Func<bool>? _canExecute;

    public RelayCommand(Action execute, Func<bool>? canExecute = null)
    {
        _execute = execute ?? throw new ArgumentNullException(nameof(execute));
        _canExecute = canExecute;
    }

    public bool CanExecute(object? parameter) => _canExecute?.Invoke() ?? true;
    public void Execute(object? parameter) => _execute();

    public event EventHandler? CanExecuteChanged
    {
        add => CommandManager.RequerySuggested += value;
        remove => CommandManager.RequerySuggested -= value;
    }
}

// 带参数命令（配合 CommandParameter 用）
public sealed class RelayCommand<T> : ICommand
{
    private readonly Action<T?> _execute;
    private readonly Predicate<T?>? _canExecute;

    public RelayCommand(Action<T?> execute, Predicate<T?>? canExecute = null)
    {
        _execute = execute ?? throw new ArgumentNullException(nameof(execute));
        _canExecute = canExecute;
    }

    public bool CanExecute(object? parameter) =>
        _canExecute?.Invoke(parameter is T t ? t : default) ?? true;

    public void Execute(object? parameter) =>
        _execute(parameter is T t ? t : default);

    public event EventHandler? CanExecuteChanged
    {
        add => CommandManager.RequerySuggested += value;
        remove => CommandManager.RequerySuggested -= value;
    }
}
```

用法：`Command="{Binding SaveCommand}"` 配 `RelayCommand`；`CommandParameter="{Binding SelectedItem}"` 配 `RelayCommand<MyItem>`。若工程本身用了 CommunityToolkit.Mvvm（`[RelayCommand]`）或 Prism（`DelegateCommand`），直接替换 `New RelayCommand(...)` 两行即可，XAML 侧完全不变——这正是「View 只认 ICommand」带来的自由。

> 为什么 `CommandManager.RequerySuggested`：WPF 会在用户输入时自动重触发 `CanExecute`，免去手动 `CanExecuteChanged` 通知，对多数按钮启用/禁用场景够用。

---

## 2. VM/V 无感规约

「无感」的完整含义是：**VM 不知道 View 长什么样、发生了什么事件；View 不知道 VM 内部怎么实现。**

**View 侧—— 声明式、无类型引用：**

- 指令：用 `Interaction.Triggers` / `Behaviors` 表达交互，用 `{Binding ...}` 连数据，用 `DataTemplate` 连列表项。
- 禁止：在 code-behind 里写业务逻辑；在 XAML 或 code-behind 里直接 `new MainViewModel()` 之外再塞 View 类型进入 VM。
- View 持有 VM 的方式只有一种：`DataContext="{Binding ...}"` 或 `DataContext` 由服务定位注入。View 代码里不出现 `vm.SomeMethod()` 这种调用（除了第 4 节允许的纯 View 例外）。

**VM 侧—— 只暴露契约：**

- 暴露：`ICommand`、`[ObservableProperty]`/`INotifyPropertyChanged` 属性、以及必要的方法（供 `CallMethodAction`）。
- 禁止：引用 `Window` / `Button` / `Control` 等 UI 类型；接收 `RoutedEventArgs` / `sender`；直接改动 UI 元素属性。
- 若某动作「必须影响 View」（关窗、聚焦、弹窗、滚动到某项），不要在 VM 里 `window.Close()`。见第 4、5 节。

**自检问题（写完交互后逐条问）：**

- VM 引用了任何 `System.Windows.*` 或本项目的 View/UserControl 类型吗？ → 是就错了。
- 事件处理器里传进 VM 的是 `e`/`sender` 吗？ → 是就该改成传值。
- 这个交互能改成纯 XAML 的 Trigger+Action 吗？ → 能就改。

---

## 3. 参数传递边界

最优雅的传参方式：**把 x:Name 元素的属性值，用 `Binding` 进 `CommandParameter`，让 VM 收到一个普通数据**，而不是收到控件。

```xml
<StackPanel>
  <TextBox x:Name="SearchBox" />
  <Button Content="搜索">
    <i:Interaction.Triggers>
      <i:EventTrigger EventName="Click">
        <i:InvokeCommandAction Command="{Binding SearchCommand}"
                               CommandParameter="{Binding Text, ElementName=SearchBox}" />
      </i:EventTrigger>
    </i:Interaction.Triggers>
  </Button>
</StackPanel>
```

VM：

```csharp
public ICommand SearchCommand { get; }
ViewModel() { SearchCommand = new RelayCommand<string>(DoSearch); }
private void DoSearch(string? keyword) { /* 只用 value，不碰任何控件 */ }
```

拿列表项：`CommandParameter="{Binding SelectedItem, ElementName=ItemsList}"`。拿 DataTemplate 里的当前项：`CommandParameter="{Binding}"`（此时即 DataContext 项）。

**何时真的需要事件参数本身？** 例如鼠标位置、拖拽坐标、被点击的行。两个不写 code-behind 的做法任选其一：

- **用行为的 `Attach` 里的数据。** 自定义 `Behavior<T>` 里可以订阅控件事件并转换成清理过的数据（第 5 节）。
- **用 `TriggerBase` + 转换器。** 把 `CommandParameter` 绑定到一个转换器，把 `e` 转成你需要的值。缺点是把 `e` 引入绑定链，尽量只在确实需要原始坐标时用。

---

## 4. 「局部允许 code-behind」的例外

严格 MVVM 不是说 code-behind 一行都不能有。**纯 View 关心的事**（渲染、焦点、窗口生命周期、关闭窗口）留在 View 的 code-behind 里，反而让 VM 更干净、更「无感」——VM 不必知道「关闭窗口」「聚焦输入框」这些平台细节。

公认可接受、且能保持 VM 无感的局部 code-behind 场景：

- **关闭窗口 / 关闭对话框**：VM 暴露一个 `event EventHandler CloseRequested;`，View 在 code-behind 订阅并 `this.Close()`。VM 只声明「我请求关闭」，不知道窗口怎么关。
  ```csharp
  // VM：只发信号
  public event EventHandler? CloseRequested;
  private void Close() => CloseRequested?.Invoke(this, EventArgs.Empty);
  ```
  ```csharp
  // View code-behind：只做纯 View 动作
  this.DataContext = vm;                       // 或由绑定提供
  ((MainViewModel)this.DataContext).CloseRequested += (_, _) => this.Close();
  ```
- **获取焦点 / 选中所有文本 / 滚动到某行**：这些是 UI 细节，写在 code-behind 或用一个小的 `Behavior<TextBox>` 里，别进 VM。
- **窗口状态 / 所有权 / 拖拽移动窗口**：属于 View 职责。

**判断标准**：这段 code-behind 是否只服务于「视图外观/生命周期」，而不含业务规则？是 → 允许；否 → 移到 VM。

---

## 5. 自定义行为 / 事件转命令封装

当内置触发器不够，或想事件参数时，写一个 `Behavior<T>` 最干净——它在 XAML 里像 `FluidMoveBehavior` 一样挂在元素上，把复杂交互收敛在自己内部，对外只暴露可绑定的属性。

```csharp
using Microsoft.Xaml.Behaviors;
using System.Windows;
using System.Windows.Controls;

// 示例：双击列表项 → 执行命令，并带上被双击的项
public sealed class ItemDoubleClickBehavior : Behavior<ListBox>
{
    public static readonly DependencyProperty CommandProperty =
        DependencyProperty.Register(nameof(Command), typeof(ICommand),
            typeof(ItemDoubleClickBehavior));

    public ICommand? Command
    {
        get => (ICommand?)GetValue(CommandProperty);
        set => SetValue(CommandProperty, value);
    }

    protected override void OnAttached()
    {
        base.OnAttached();
        AssociatedObject.MouseDoubleClick += OnDoubleClick;
    }

    protected override void OnDetaching()
    {
        AssociatedObject.MouseDoubleClick -= OnDoubleClick;
        base.OnDetaching();
    }

    private void OnDoubleClick(object sender, MouseButtonEventArgs e)
    {
        // 把选中项作为参数，而不是把 e 传给 VM
        Command?.Execute(AssociatedObject.SelectedItem);
    }
}
```

XAML 使用：

```xml
<ListBox ItemsSource="{Binding Items}" SelectedItem="{Binding SelectedItem}">
  <i:Interaction.Behaviors>
    <local:ItemDoubleClickBehavior Command="{Binding OpenItemCommand}" />
  </i:Interaction.Behaviors>
</ListBox>
```

要点：

- 继承 `Behavior<T>`（T 是目标控件类型），重写 `OnAttached`/`OnDetaching` 订阅/退订，**务必在 `OnDetaching` 退订**，防内存泄漏。
- 对外只暴露依赖属性（`Command` 等），让其可被 XAML 绑定。VM 只看到 `ICommand`，依旧无感。
- 若事件不来自 `AssociatedObject` 本身而是其子元素（如 `Button` 里的 `Click`），在 `OnAttached` 里用 `AddHandler` 处理子元素冒泡事件。

> 想用 `i:EventTrigger` 但需要事件参数时，也可扩展 `EventTrigger`/`TriggerBase`，但自定义 `Behavior<T>` 更直观，优先用它。
