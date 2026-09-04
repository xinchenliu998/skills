# 触发器（Triggers）

> 触发器是「何时发生」：它决定一串动作在什么时机被触发。动作（Action）是「发生什么」。触发器放在 `Interaction.Triggers` 里，动作放在触发器内部。

## 目录

1. [EventTrigger](#1-eventtrigger事件的开关)
2. [DataTrigger](#2-datatrigger数据等于某值)
3. [PropertyChangedTrigger](#3-propertychangedtrigger属性一变就触发)
4. [TimerTrigger](#4-timertrigger定时触发)
5. [KeyTrigger](#5-keytrigger按键组合触发)
6. [通用：多个触发器 & 挂载位置](#6-通用多个触发器--挂载位置)

---

## 1. EventTrigger：事件的开关

最强用、最常用。监听指定事件，事件发生时触发内部动作。典型场景是把 `Button.Click` 映射成 VM 命令。

```xml
<Button Content="登录"
        Command="{Binding LoginCommand}">   <!-- 按钮自带 Command，行为无需触发器 -->
</Button>
```

但凡是「没有自带 Command、但有事件」的控件，就用触发器包起来：

```xml
<Button Content="保存">
  <i:Interaction.Triggers>
    <i:EventTrigger EventName="Click">
      <i:InvokeCommandAction Command="{Binding SaveCommand}" />
    </i:EventTrigger>
  </i:Interaction.Triggers>
</Button>
```

要点：

- `EventName`：该元素会触发的路由事件名（`Click`、`MouseLeftButtonDown`、`MouseRightButtonUp`、`Loaded`、`Unloaded`、`TextChanged`、`SelectionChanged`……）。
- `SourceObject`：默认事件来自元素本身。若想监听别的元素的事件（例如在 Window 上监听子控件的 Click），设 `SourceObject="{Binding ElementName=Other}"`。
- 与控件自带的 `Command` 相比，`EventTrigger` 的优势是：事件类型不限（`MouseEnter`、`DataContextChanged`、非标准事件都能接），且能链上多个 Action、配上 `ConditionBehavior`。

## 2. DataTrigger：数据等于某值

当绑定的属性**等于某值**时触发。适合「状态驱动」的交互：某属性为 X 时执行动作。

```xml
<CheckBox Content="启用高级选项">
  <i:Interaction.Triggers>
    <i:DataTrigger Binding="{Binding IsChecked, RelativeSource={RelativeSource Self}}"
                   Value="True">
      <i:ChangePropertyAction TargetName="AdvancedPanel" PropertyName="Visibility" Value="Visible"/>
    </i:DataTrigger>
    <i:DataTrigger Binding="{Binding IsChecked, RelativeSource={RelativeSource Self}}"
                   Value="False">
      <i:ChangePropertyAction TargetName="AdvancedPanel" PropertyName="Visibility" Value="Collapsed"/>
    </i:DataTrigger>
  </i:Interaction.Triggers>
</CheckBox>
```

要点：

- `Binding`：任意可解析为值的绑定；`Value`：触发时该绑定须等于的值（`True`/`False`/字符串/枚举）。
- 这是「数据 == 值」的**瞬时判断**。若想「数据不同就切到另一个状态」，用 `DataStateBehavior`（见 behaviors.md）更省事。
- `Value` 用字符串时会被当作 `Binding` 目标类型解析；比较 `IsChecked` 这类 `bool` 时写 `True`/`False`。

## 3. PropertyChangedTrigger：属性一变就触发

只要绑定属性**发生变化**（无论变成什么值）就触发。适合不需要判断新值、只关心「变没变」的场景，如自动保存。

```xml
<TextBox x:Name="NameBox" Text="{Binding Name, UpdateSourceTrigger=PropertyChanged}">
  <i:Interaction.Triggers>
    <i:PropertyChangedTrigger Binding="{Binding Text, ElementName=NameBox}">
      <i:InvokeCommandAction Command="{Binding AutosaveCommand}" />
    </i:PropertyChangedTrigger>
  </i:Interaction.Triggers>
</TextBox>
```

要点：

- `Binding`：被监听的属性。属性值一变，动作就触发。
- 与 `DataTrigger` 区别：`PropertyChangedTrigger` 不管新值是什么；`DataTrigger` 只在等于特定值时触发。

## 4. TimerTrigger：定时触发

每隔 `Interval` 毫秒触发一次。适合轮询、自动刷新。

```xml
<i:Interaction.Triggers>
  <i:TimerTrigger Interval="5000">
    <i:InvokeCommandAction Command="{Binding RefreshCommand}" />
  </i:TimerTrigger>
</i:Interaction.Triggers>
```

要点：

- `Interval`：间隔毫秒数（int）。
- 通常把 `TimerTrigger` 挂在承载它的元素（如 Window 或 Grid 的 `Interaction.Triggers`）上。

## 5. KeyTrigger：按键组合触发

按下指定按键（含修饰键）时触发。适合快捷键。

```xml
<Window ...>
  <i:Interaction.Triggers>
    <i:KeyTrigger Key="F5">
      <i:InvokeCommandAction Command="{Binding RefreshCommand}" />
    </i:KeyTrigger>
    <i:KeyTrigger Key="S" Modifiers="Ctrl">
      <i:InvokeCommandAction Command="{Binding SaveCommand}" />
    </i:KeyTrigger>
  </i:Interaction.Triggers>
</Window>
```

要点：

- `Key`：`Key.F5`、`Key.S` 等 `System.Windows.Input.Key` 值。
- `Modifiers`：可组合的修饰键，如 `Ctrl`、`Alt`、`Shift`、`Ctrl+Shift`。

## 6. 通用：多个触发器 & 挂载位置

- 一个元素可以挂**多个** `Interaction.Triggers`，各自独立监听。
- 每个触发器里可以放**多个 Action**，会依次执行。
- 挂载位置决定 `DataContext` 么系：`Interaction.Triggers` 放在谁身上，`InvokeCommandAction` 的 `Binding` 默认就以谁的 `DataContext` 为根。列表项模板里的触发器，`DataContext` 就是当前列表项。
