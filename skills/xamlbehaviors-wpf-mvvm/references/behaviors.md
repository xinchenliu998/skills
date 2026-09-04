# 行为（Behaviors）

> 行为（Behavior）与触发器（Trigger）不同：触发器是「响应某个时机」的一段动作；行为（特指 `Interaction.Behaviors` 里的 `Behavior<T>`）是**附着在元素上、持续存在的一段逻辑**——它挂上去就生效，直到元素卸载。Behaviors 通常用在「数据驱动状态」「拖拽/手势」「换行动画」等不依赖具体事件时机的场景。

## 目录

1. [DataStateBehavior：数据驱动切换视觉状态](#1-datastatebehavior数据驱动切换视觉状态)
2. [ConditionBehavior：给动作加逻辑条件](#2-conditionbehavior给动作加逻辑条件)
3. [FluidMoveBehavior：换行/移动动画](#3-fluidmovebehavior换行移动动画)
4. [FluidMoveSetTagBehavior：标记元素参与移动动画](#4-fluidmovesettagbehavior标记元素参与移动动画)
5. [MouseDragElementBehavior：拖拽](#5-mousedragelementbehavior拖拽)
6. [TranslateZoomRotateBehavior：平移/缩放/旋转手势](#6-translatezoomrotatebehavior平移缩放旋转手势)

---

## 1. DataStateBehavior：数据驱动切换视觉状态

绑定到某属性，其值等于 `Value` 时切到 `TrueState`，否则切到 `FalseState`。这是 MVVM 里处理「一个数据决定整块 UI 状态」最常用的行为——数据在 VM 里，UI 状态切换完全在 View 里完成，VM 依旧无感。

```xml
<ListBox ...>
  <i:Interaction.Behaviors>
    <i:DataStateBehavior Binding="{Binding Items.Count, RelativeSource={RelativeSource Self}}"
                         Value="0"
                         TrueState="Empty"     <!-- 没有项时 -->
                         FalseState="Normal" /> <!-- 有项时 -->
  </i:Interaction.Behaviors>
</ListBox>
```

配合该元素/其模板里的 `VisualStateManager` 状态（`Empty`、`Normal`）。属性：

- `Binding`：被监测的数据（可绑定）。
- `Value`：触发 `TrueState` 时绑定必须等于的值。
- `TrueState`：绑定==Value 时进入的状态。
- `FalseState`：否则进入的状态。

> 相比「两个 `DataTrigger` 各切一个状态」，`DataStateBehavior` 一句搞定，且切换是无缝的。

## 2. ConditionBehavior：给动作加逻辑条件

它是**挂在触发器上**的行为（注意：放在 `Interaction.Behaviors` 而不是 `Triggers` 里），用来抑制动作：当 `Condition` 不成立时，触发器的动作不执行。适合做「拆验证后再执行」的拦截。

```xml
<Button Content="提交">
  <i:Interaction.Triggers>
    <i:EventTrigger EventName="Click">
      <i:Interaction.Behaviors>
        <i:ConditionBehavior>
          <i:ConditionalExpression>
            <i:ComparisonCondition LeftOperand="{Binding Id}" RightOperand="0"
                                   Operator="Equal" />
          </i:ConditionalExpression>
        </i:ConditionBehavior>
      </i:Interaction.Behaviors>
      <i:InvokeCommandAction Command="{Binding SubmitCommand}" />
    </i:EventTrigger>
  </i:Interaction.Triggers>
</Button>
```

`ConditionalExpression` 里可嵌套组合：

- `ComparisonCondition`：`LeftOperand`（绑定或值）、`RightOperand`（比较基准）、`Operator`（比较方式，类型为 `ComparisonOperator` 枚举）。**注意 XAML 属性名是 `Operator`，不是 `ComparisonOperator`**——后者是枚举类型名，`ComparisonCondition` 的属性是 `Operator="Equal"`。枚举取值：`Equal`/`NotEqual`/`GreaterThan`/`LessThan`/`GreaterThanOrEqual`/`LessThanOrEqual`。
- `AndCondition`：内含多个条件，全部成立才通过。
- `OrCondition`：任一成立即通过。
- `NotCondition`：逻辑取反。

一个多条件示例（Id 非空 且 IsValid 为真才放行）：

```xml
<i:ConditionalExpression>
  <i:AndCondition>
    <i:ComparisonCondition LeftOperand="{Binding Id}" RightOperand="0" Operator="NotEqual" />
    <i:ComparisonCondition LeftOperand="{Binding IsValid}" RightOperand="True" Operator="Equal" />
  </i:AndCondition>
</i:ConditionalExpression>
```

> 逻辑验证型逻辑更推荐放到 VM 的 `CanExecute` 里（`RelayCommand(..., canExecute)`），可绑定到按钮 `IsEnabled`。`ConditionBehavior` 适合「纯 View 侧的一次性拦截」，两者别重复写。

## 3. FluidMoveBehavior：换行/移动动画

当元素在容器（如 `ItemsControl`/`Grid`）内的位置因重新布局而变化时，动画过渡而不是瞬时跳变。常配合 `AppliesTo="Children"` 用在整个容器上，让增删/重排列表项时有平滑移动。

```xml
<ItemsControl ItemsSource="{Binding Items}">
  <i:Interaction.Behaviors>
    <i:FluidMoveBehavior AppliesTo="Children" Duration="0:0:1" />
  </i:Interaction.Behaviors>
</ItemsControl>
```

属性：

- `AppliesTo`：`Self`（仅自身）或 `Children`（所有子元素）。
- `Duration`：过渡时长（`TimeSpan`）。
- `EaseX` / `EaseY`：X/Y 方向的缓动曲线。

## 4. FluidMoveSetTagBehavior：标记元素参与移动动画

给元素打一个 tag，供 `FluidMoveBehavior` 识别并动画它的移动。常用于把「当前项」固定参与动画。

```xml
<ListBox ...>
  <i:Interaction.Behaviors>
    <i:FluidMoveSetTagBehavior Tag="{Binding}" />
  </i:Interaction.Behaviors>
</ListBox>
```

- `Tag`：要与 `FluidMoveBehavior` 匹配的标识（通常绑定到项）。不设 tag 时按默认规则参与。

## 5. MouseDragElementBehavior：拖拽

让元素可用鼠标拖拽移动。适合可拖动的小部件（拖到某处、或允许自由摆放）。

```xml
<Canvas>
  <Border Width="80" Height="80" Background="LightBlue" Canvas.Left="20" Canvas.Top="20">
    <i:Interaction.Behaviors>
      <i:MouseDragElementBehavior />
    </i:Interaction.Behaviors>
  </Border>
</Canvas>
```

属性：

- `X` / `Y`：当前拖动到的坐标（可绑定）。
- `ConstrainToParentBounds`：`true` 时限制在父元素范围内拖动。
- 拖拽的开始、移动、结束分别暴露事件/MouseButton 行为，感兴趣的可在其中接逻辑。

## 6. TranslateZoomRotateBehavior：平移/缩放/旋转手势

启用对元素的触摸/鼠标手势：单指/单键平移、双指缩放、旋转。适合地图、图片查看器、可交互画布。

```xml
<Image Source="map.png" Width="300" Height="300">
  <i:Interaction.Behaviors>
    <i:TranslateZoomRotateBehavior ZoomMode="Scale" />
  </i:Interaction.Behaviors>
</Image>
```

属性：

- `Translate` / `Scale` / `Rotate` 相关布尔控制哪些手势启用；`ZoomMode` 指定缩放行为等。
- 具体可组合手势。需要精细控制时，可核对 `Microsoft.Xaml.Behaviors` 文档中对应属性名。

> 惯例：这类行为直接挂在目标元素上的 `Interaction.Behaviors`，挂上即生效，与 `Interaction.Triggers` 的「事件驱动」正交。
