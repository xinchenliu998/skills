---
name: handycontrol-wpf
description: HandyControl（WPF 控件库，XAML 命名空间 hc:）的官方文档库与使用指南。当在 WPF/.NET 项目中挑选 HandyControl 控件、查询控件属性/方法/事件/附加属性、查找样式键（ButtonPrimary 等）与主题资源键（画刷/颜色/几何/路径/字体/阴影/行为/转换器）、编写 hc: 命名空间 XAML、使用 Dialog/MessageBox/Growl/Loading/Pagination/PropertyGrid 等组件，或排查"样式不生效/控件没变样"这类接入问题时使用。
---

# HandyControl WPF 控件库

HandyControl 重写了几乎全部 WPF 原生控件样式，另含 79 款扩展控件。
本 skill 收录官网 <https://handyorg.github.io/handycontrol/>（文档版本 3.0.0）全部正文，转成 148 个 Markdown 文件放在 `references/` 下，一控件一文件、单文件不超过 250 行，按需读取。

## 何时使用

- 在 WPF 项目中挑控件、写 `hc:` 命名空间的 XAML
- 查某控件的属性、方法、事件、附加属性、可用样式键
- 查主题资源键：画刷、颜色、几何形状、Path、字体、阴影、行为、转换器
- 用 `Dialog` / `MessageBox` / `Growl` / `Loading` / `Pagination` / `PropertyGrid` 等交互组件
- 排查"引用了库但按钮没变样""StaticResource 找不到键"这类接入问题

## 工作流

1. 在下方目录里按**控件名 / 样式键 / 附加属性类**定位，拿到 `references/` 相对路径。
2. 只读命中的 1-2 个文件，不要整目录加载。需要"这个控件是干什么的"时读 `references/index.md`（含一句话说明）。
3. 复制文档示例再改。属性名、枚举取值、默认值、样式键名一律照文档，不要凭记忆猜。
4. 文档未覆盖的能力（如主题/皮肤运行时切换的 `ThemeManager` API）不要臆造，去源码 `HandyControl/Themes`、`HandyControl/Controls` 确认后再用。

文档中的 `效果` 段落指向官网截图（`raw.githubusercontent.com` 地址），需要判断视觉形态时直接打开图片。

## 项目接入

```xml
<!-- App.xaml：先皮肤、后主题，顺序不能反 -->
<Application.Resources>
    <ResourceDictionary>
        <ResourceDictionary.MergedDictionaries>
            <ResourceDictionary Source="pack://application:,,,/HandyControl;component/Themes/SkinDefault.xaml"/>
            <ResourceDictionary Source="pack://application:,,,/HandyControl;component/Themes/Theme.xaml"/>
        </ResourceDictionary.MergedDictionaries>
    </ResourceDictionary>
</Application.Resources>
```

```xml
<!-- 任意 XAML：URL 形式命名空间映射到 HandyControl.Controls -->
xmlns:hc="https://handyorg.github.io/handycontrol"
```

NuGet 包名 `HandyControl`。详见 `references/quick_start.md`。

## 关键概念（踩坑高发区）

1. **原生控件不加 `hc:`**。`Button`、`DataGrid`、`ListBox` 等已被隐式样式重写，直接 `<Button/>` 就是 HandyControl 外观，不存在 `<hc:Button/>`。少数原生控件另有 `hc:` 扩展版（`hc:TextBox`、`hc:ComboBox`、`hc:DatePicker`、`hc:PasswordBox`、`hc:ScrollViewer`、`hc:TabControl`、`hc:Window`），两者都可用，扩展版多了附加功能；其余自定义控件（`hc:Badge`、`hc:Card`…）必须用 `hc:`。
2. **`controls:` 与 `hc:` 等价**。官网示例里的 `controls:Growl.GrowlParent`、`controls:BorderElement.CornerRadius` 来自 Demo 的 `xmlns:controls="clr-namespace:HandyControl.Controls"`；用 URL 命名空间时全部换成 `hc:`。
3. **带 `Base` / `BaseStyle` 的样式只作地基**，供其它样式 `BasedOn`，不要直接用在视图里。
4. **覆盖默认样式要按类型引用**：隐式样式没有 Key，用 `BasedOn="{StaticResource {x:Type Button}}"`。
5. **附加属性统一形态 `hc:XxxElement.Yyy`**：`hc:IconElement.Geometry`、`hc:BorderElement.CornerRadius`、`hc:TitleElement.Title`。以 `Element` 结尾的类对所有控件生效，以 `Attach` 结尾的只对特定控件生效；标注"内部专用"的不要直接用。
6. **画刷/颜色用 `DynamicResource`**（换肤才刷新），几何、样式、尺寸用 `StaticResource`。
7. **样式键没有命名规律**：按钮是 `ButtonPrimary`/`ButtonDanger`，标签却是 `LabelPrimary`，文本框是 `TextBoxExtend`。必须查下表。

## 扩展控件目录

均为 `HandyControl.Controls` 下的类型。表头第三列是文件路径（相对 `references/`），带一句话用途的完整版见 `references/index.md`。

| 控件 | 标签 / 调用方式 | 文档 |
| --- | --- | --- |
| AnimationPath 动画路径 | `hc:AnimationPath` | extend_controls/animationPath.md |
| Badge 标记 | `hc:Badge` | extend_controls/badge.md |
| BlurWindow 背景模糊窗口 | `hc:BlurWindow` | extend_controls/blurWindow.md |
| ButtonGroup 按钮组 | `hc:ButtonGroup`（子项为 RadioButton 样式） | extend_controls/buttonGroup.md |
| CalendarWithClock 带有时钟的日历 | `hc:CalendarWithClock` | extend_controls/calendarWithClock.md |
| Card 卡片 | `hc:Card` | extend_controls/card.md |
| Carousel 轮播 | `hc:Carousel` | extend_controls/carousel.md |
| ChatBubble 对话气泡 | `hc:ChatBubble` | extend_controls/chatBubble.md |
| CheckComboBox 复选组合框 | `hc:CheckComboBox` | extend_controls/checkComboBox.md |
| CirclePanel 圆形布局 | `hc:CirclePanel` | extend_controls/circlePanel.md |
| CircleProgressBar 圆形进度条 | `hc:CircleProgressBar` | extend_controls/circleProgressBar.md |
| Clock 时钟 | `hc:Clock` | extend_controls/clock.md |
| ColorPicker 颜色拾取器 | `hc:ColorPicker` | extend_controls/colorPicker.md |
| ComboBox 组合框 | `hc:ComboBox` | extend_controls/comboBox.md |
| CompareSlider 对比滑块 | `hc:CompareSlider` | extend_controls/compareSlider.md |
| ContextMenuButton 上下文菜单按钮 | `hc:ContextMenuButton` / `hc:ContextMenuToggleButton` | extend_controls/contextMenuButton.md |
| CoverFlow 封面流 | `hc:CoverFlow` | extend_controls/coverFlow.md |
| CoverView 封面视图 | `hc:CoverView` | extend_controls/coverView.md |
| DashedBorder 虚线边框 | `hc:DashedBorder` | extend_controls/dashedBorder.md |
| DatePicker 日期选择器 | `hc:DatePicker` | extend_controls/datePicker.md |
| DateTimePicker 日期时间选择器 | `hc:DateTimePicker` | extend_controls/dateTimePicker.md |
| Dialog 对话框 | `hc:DialogContainer` + C# `Dialog.Show(...)` | extend_controls/dialog.md |
| Divider 分割线 | `hc:Divider` | extend_controls/divider.md |
| Drawer 抽屉 | `hc:Drawer` | extend_controls/drawer.md |
| FlipClock 翻页时钟 | `hc:FlipClock` | extend_controls/flipClock.md |
| FloatingBlock 漂浮块 | `hc:FloatingBlock` | extend_controls/floatingBlock.md |
| GifImage Gif图片 | `hc:GifImage` | extend_controls/gifImage.md |
| GlowWindow 辉光窗口 | `hc:GlowWindow` | extend_controls/glowWindow.md |
| GotoTop 回到顶部 | `hc:GotoTop` | extend_controls/gotoTop.md |
| Gravatar 头像 | `hc:Gravatar` | extend_controls/gravatar.md |
| Grid 栅格 | `hc:Row` / `hc:Col` | extend_controls/grid.md |
| Growl 信息通知 | C# 静态方法 `Growl.Success(...)` | extend_controls/growl.md |
| HoneycombPanel 蜂窝布局 | `hc:HoneycombPanel` | extend_controls/honeycombPanel.md |
| ImageBlock 图片块 | `hc:ImageBlock` | extend_controls/imageBlock.md |
| ImageBrowser 图片浏览器 | C# `new ImageBrowser(uri).Show()` | extend_controls/imageBrowser.md |
| ImageSelector 图片选择器 | `hc:ImageSelector` | extend_controls/imageSelector.md |
| ImageViewer 图片视图 | `hc:ImageViewer` | extend_controls/imageViewer.md |
| Loading 加载条 | `hc:LoadingLine` / `hc:LoadingCircle` | extend_controls/loading.md |
| Magnifier 放大镜 | `hc:Magnifier` | extend_controls/magnifier.md |
| MessageBox 消息对话框 | C# `MessageBox.Success/Show(...)` | extend_controls/messageBox.md |
| Notification 桌面通知 | C# 继承 `Notification` 后 `new Xxx().Show()` | extend_controls/notification.md |
| NotifyIcon 托盘图标 | `hc:NotifyIcon` | extend_controls/notifyIcon.md |
| NumericUpDown 数值选择控件 | `hc:NumericUpDown` | extend_controls/numericUpDown.md |
| OutlineText 轮廓文本 | `hc:OutlineText` | extend_controls/outlineText.md |
| Pagination 页码条 | `hc:Pagination` | extend_controls/pagination.md |
| PasswordBox 密码框 | `hc:PasswordBox` | extend_controls/passwordBox.md |
| PinBox PIN码框 | `hc:PinBox` | extend_controls/pinBox.md |
| PopTip 气泡提示 | `hc:Poptip` | extend_controls/popTip.md |
| PopupWindow 弹出窗口 | C# 静态方法 `PopupWindow.Show(...)` | extend_controls/popupWindow.md |
| PreviewSlider 预览滑块 | `hc:PreviewSlider` | extend_controls/previewSlider.md |
| ProgressButton 进度按钮 | `hc:ProgressButton` | extend_controls/progressButton.md |
| PropertyGrid 属性编辑器 | `hc:PropertyGrid` | extend_controls/propertyGrid.md |
| RangeSlider 范围滑块 | `hc:RangeSlider` | extend_controls/rangeSlider.md |
| Rate 评分 | `hc:Rate` | extend_controls/rate.md |
| RelativePanel 相对布局 | `hc:RelativePanel` | extend_controls/relativePanel.md |
| RunningBlock 滚动块 | `hc:RunningBlock` | extend_controls/runningBlock.md |
| Screenshot 截图 | C# `new Screenshot().Start()` | extend_controls/screenshot.md |
| ScrollViewer 滚动视图 | `hc:ScrollViewer` | extend_controls/scrollViewer.md |
| SearchBar 搜索栏 | `hc:SearchBar` | extend_controls/searchBar.md |
| Shield 徽章 | `hc:Shield` | extend_controls/shield.md |
| SideMenu 侧边菜单 | `hc:SideMenu` | extend_controls/sideMenu.md |
| SimpleItemsControl 简单项目控件 | `hc:SimpleItemsControl` | extend_controls/simpleItemsControl.md |
| SimplePanel 简单面板 | `hc:SimplePanel` | extend_controls/simplePanel.md |
| SimpleText 简单文本 | `hc:SimpleText` | extend_controls/simpleText.md |
| SplitButton 分割按钮 | `hc:SplitButton` | extend_controls/splitButton.md |
| Sprite 精灵 | C# 继承 `Sprite` 后 `new Xxx().Show()` | extend_controls/sprite.md |
| StepBar 步骤条 | `hc:StepBar` | extend_controls/stepBar.md |
| TabControl 选项卡控件 | `hc:TabControl` | extend_controls/tabControl.md |
| Tag 标签 | `hc:Tag` | extend_controls/tag.md |
| TextBox 文本框 | `hc:TextBox` | extend_controls/textBox.md |
| TimeBar 时间条 | `hc:TimeBar` | extend_controls/timeBar.md |
| TimePicker 时间选择器 | `hc:TimePicker` | extend_controls/timePicker.md |
| ToggleBlock 切换块 | `hc:ToggleBlock` | extend_controls/toggleBlock.md |
| Transfer 穿梭框 | `hc:Transfer` | extend_controls/transfer.md |
| TransitioningContentControl 内容过渡控件 | `hc:TransitioningContentControl` | extend_controls/transitioningContentControl.md |
| WaterfallPanel 瀑布流 | `hc:WaterfallPanel` | extend_controls/waterfallPanel.md |
| Watermark 水印 | `hc:Watermark` | extend_controls/watermark.md |
| WaveProgressBar 波形进度条 | `hc:WaveProgressBar` | extend_controls/waveProgressBar.md |
| Window 窗口 | `hc:Window` | extend_controls/window.md |

## 原生控件与可用样式键

原生控件默认走隐式样式；下表的键通过 `Style="{StaticResource 键名}"` 切换外观。

| 控件 | 可用样式键 | 文档 |
| --- | --- | --- |
| Border | `BorderRegion`, `BorderVerticallySplitter`, `BorderHorizontallySplitter`, `BorderCircular`, `BorderClip` | native_controls/border.md |
| Button | `ButtonBaseStyle`, `ButtonPrimary`, `ButtonSuccess`, `ButtonInfo`, `ButtonWarning`, `ButtonDanger`, `ButtonIcon`, `ButtonCustom` | native_controls/button.md |
| Calendar | `CalendarBaseStyle` | native_controls/calendar.md |
| CheckBox | `CheckBoxBaseStyle` | native_controls/checkBox.md |
| ComboBox | `ComboBoxBaseStyle`, `ComboBoxExtendBaseStyle`, `ComboBoxExtend` | native_controls/comboBox.md |
| ContentControl | 页内未列样式键，用隐式样式 | native_controls/contentControl.md |
| ContextMenu | `ContextMenuBaseStyle` | native_controls/contextMenu.md |
| DataGrid | 页内未列样式键，用隐式样式 | native_controls/dataGrid.md |
| DatePicker | `DatePickerBaseStyle`, `DatePickerExtendBaseStyle`, `DatePickerExtend` | native_controls/datePicker.md |
| Expander | `ExpanderBaseStyle` | native_controls/expander.md |
| FlowDocument | `FlowDocumentScrollViewerBaseStyle`, `FlowDocumentPageViewerBaseStyle`, `FlowDocumentReaderBaseStyle` | native_controls/flowDocument.md |
| Frame | `FrameBaseStyle` | native_controls/frame.md |
| GroupBox | `GroupBoxBaseStyle`, `GroupBoxTab`, `GroupBoxOriginal` | native_controls/groupBox.md |
| Image | 页内未列样式键，用隐式样式 | native_controls/image.md |
| Label | `LabelBaseStyle`, `LabelPrimary`, `LabelSuccess`, `LabelInfo`, `LabelWarning`, `LabelDanger` | native_controls/label.md |
| ListBox | `ListBoxBaseStyle`, `ListBoxCustom`, `WrapPanelHorizontalListBox`, `WrapPanelVerticalListBox`, `StackPanelHorizontalListBox`, `StackPanelVerticalListBox` | native_controls/listBox.md |
| ListView | 页内未列样式键，用隐式样式 | native_controls/listView.md |
| Menu | `MenuBaseStyle` | native_controls/menu.md |
| PasswordBox | `PasswordBoxBaseStyle`, `PasswordBoxExtendBaseStyle`, `PasswordBoxExtend` | native_controls/passwordBox.md |
| ProgressBar | `ProgressBarBaseStyle` | native_controls/progressBar.md |
| RadioButton | `RadioButtonBaseStyle`, `RadioButtonIcon` | native_controls/radioButton.md |
| RichTextBox | `TextBoxBaseBaseStyle`, `RichTextBoxBaseStyle` | native_controls/richTextBox.md |
| ScrollViewer | `ScrollViewerNativeBaseStyle`, `ScrollViewerUpDown` | native_controls/scrollViewer.md |
| Separator | `SeparatorBaseStyle` | native_controls/seperator.md |
| Slider | `SliderBaseStyle` | native_controls/slider.md |
| StatusBar | `StatusBarBaseStyle` | native_controls/statusBar.md |
| TabControl | `TabControlBaseStyle`, `TabControlInLine`, `TabControlCapsule`, `TabControlCapsuleSolid` | native_controls/tabControl.md |
| TextBlock | `TextBlockBaseStyle`, `TextBlockBoldBaseStyle`, `TextBlockLargeBold`, `TextBlockLarge`, `TextBlockTitleBold`, `TextBlockTitle`, `TextBlockSubTitleBold`, `TextBlockSubTitle`, `TextBlockDefaultBold`, `TextBlockDefault` …(+8) | native_controls/textBlock.md |
| TextBox | `TextBoxBaseStyle`, `TextBoxExtendBaseStyle`, `TextBoxExtend` | native_controls/textBox.md |
| ToggleButton | `ToggleButtonBaseStyle`, `ToggleButtonIconBaseStyle`, `ToggleButtonSwitchBaseStyle`, `ToggleButtonFlip`, `ToggleButtonCustom`, `ToggleButtonPrimary`, `ToggleButtonSuccess`, `ToggleButtonInfo`, `ToggleButtonWarning`, `ToggleButtonDanger` …(+8) | native_controls/toggleButton.md |
| ToolBar | `ToolBarBaseStyle` | native_controls/toolBar.md |
| ToolTip | `ToolTipBaseStyle` | native_controls/toolTip.md |
| TreeView | `TreeViewBaseStyle` | native_controls/treeView.md |
| Window | 页内未列样式键，用隐式样式 | native_controls/window.md |

## 附加属性

形态 `hc:类名.属性名`。

| 附加属性类 | 主要属性 | 文档 |
| --- | --- | --- |
| BackgroundSwitchElement 可切换背景的元素 | `MouseHoverBackground`, `MouseDownBackground` | attach/backgroundSwitchElement.md |
| BorderElement 具有边框的元素 | `CornerRadius`, `Circular` | attach/borderElement.md |
| DataGridAttach DataGrid专用 | `ApplyDefaultStyle`, `TextColumnStyle`, `EditingTextColumnStyle`, `ComboBoxColumnStyle`, `EditingComboBoxColumnStyle`, `CheckBoxColumnStyle`, `EditingCheckBoxColumnStyle`, `ShowRowNumber` | attach/dataGridAttach.md |
| DropDownElement 可下拉内容的元素 | `ConsistentWidth` | attach/dropDownElement.md |
| EdgeElement 具有边界内容的元素 | `LeftContent`, `TopContent`, `RightContent`, `BottomContent`, `ShowEdgeContent` | attach/edgeElement.md |
| IconElement 具有图标的元素 | `Geometry`, `Width`, `Height` | attach/iconElement.md |
| IconSwitchElement 可切换图标的元素 | `GeometrySelected` | attach/iconSwitchElement.md |
| ImageAttach Image专用 | `SourceFailed` | attach/imageAttach.md |
| InfoElement 信息元素 | `Placeholder`, `Necessary`, `Symbol`, `ContentHeight`, `MinContentHeight`, `MaxContentHeight`, `RegexPattern` | attach/infoElement.md |
| PanelElement 面板元素 | `FluidMoveBehavior` | attach/panelElement.md |
| PasswordBoxAttach 密码框专用 | `IsMonitoring`, `PasswordLength` | attach/passwordBoxAttach.md |
| RectangleAttach Rectangle专用 | `Circular` | attach/rectangleAttach.md |
| StatusSwitchElement 可切换状态的元素 | `CheckedElement`, `HideUncheckedElement` | attach/statusSwitchElement.md |
| TextBlockAttach 文本块专用 | `AutoTooltip` | attach/textBlockAttach.md |
| TipElement 提示元素 | `Placement`, `Visibility`, `StringFormat` | attach/tipElement.md |
| TitleElement 标题元素 | `Title`, `Background`, `Foreground`, `BorderBrush`, `TitlePlacement`, `TitleWidth` | attach/titleElement.md |
| VisualElement 可视化元素 | `HighlightBrush`, `HighlightBackground`, `HighlightBorderBrush`, `HighlightForeground`, `Text` | attach/visualElement.md |
| WindowAttach 窗体专用 | `IsDragElement`, `IgnoreAltF4`, `ShowInTaskManager` | attach/windowAttach.md |

## 基础资源键

| 类别 | 常用键 | 文档 |
| --- | --- | --- |
| 画刷 | `PrimaryBrush` `DangerBrush` `WarningBrush` `InfoBrush` `SuccessBrush` `RegionBrush` `SecondaryRegionBrush` `BorderBrush` `SecondaryTextBrush` `BackgroundBrush` | basic_xaml/brushes.md |
| 颜色 | `PrimaryColor` `DangerColor` `RegionColor` `PrimaryTextColor` …（Colors.xaml / ColorsDark.xaml / ColorsViolet.xaml 三套） | basic_xaml/colors.md |
| 字体大小 | `LargeFontSize`(24) `HeadFontSize`(20) `SubHeadFontSize`(16) `TextFontSize`(12) | basic_xaml/fonts.md |
| 阴影 | `EffectShadow1`…`EffectShadow5`（半径 5/8/14/25/35） | basic_xaml/effects.md |
| 几何 | `SearchGeometry` `CloseGeometry` `DeleteGeometry` `ErrorGeometry` `SuccessGeometry` `CalendarGeometry` `StarGeometry` … | basic_xaml/geometries.md |
| Path | `SearchPathStyle` `SavePathStyle` `FullScreenPathStyle` … | basic_xaml/paths.md |
| 尺寸 | `DefaultControlHeight`(30) `DefaultControlPadding` `DefaultInputPadding` `DefaultCornerRadius`(4) | basic_xaml/sizes.md |
| 行为 | `BehaviorXY200` `BehaviorX200` `BehaviorY200` 及 400ms 版本 | basic_xaml/behaviors.md |
| 转换器 | `Boolean2VisibilityConverter` `Boolean2StringConverter` `Boolean2BooleanReConverter` `Object2VisibilityConverter` … | basic_xaml/converters.md |

## 文档与源码的已知出入

以下四处官网文档与控件库源码（v3.0.0 与 master 的 `Themes`）对不上，已按源码校正；读对应页面时若看到另一种写法，以本表为准。

| 文档写法 | 实际可用 | 说明 |
| --- | --- | --- |
| `BorderRegionStyle` | `BorderRegion` | border.md 正文自己注明：新版本改用 `BorderRegion`，由直角变圆角 |
| `Boolean2StrConverter`（converters.md 标题） | `Boolean2StringConverter` | 标题漏了 `ing`，`Converters.xaml` 里的键是后者 |
| `DataGridTextCenterColumnStyle` | 需自行定义 | 这是 dataGrid.md 示例里自定义的居中列样式，库里没有这个键 |
| `RectangleAttach.CornerRadius`（属性表） | `hc:RectangleAttach.Circular` | 源码 `RectangleAttach` 只有 `Circular`，同页示例用的也是它 |

## 最小配方

```xml
<!-- 自定义标题栏窗口（xmlns 省略，hc 前缀指向 https://handyorg.github.io/handycontrol） -->
<hc:Window x:Class="App.MainWindow" ShowNonClientArea="True" NonClientAreaHeight="32">
    <hc:Window.NonClientAreaContent>
        <TextBlock Text="标题" VerticalAlignment="Center" Margin="10,0,0,0"/>
    </hc:Window.NonClientAreaContent>
</hc:Window>
```

```csharp
// 内容对话框：Dialog.Show 传出任意元素，Close() 关闭，GetResultAsync 异步等结果
Dialog.Show(new TextDialog());
var d = Dialog.Show<ProgressDialog>();
d.Close();
await Dialog.Show<InteractiveDialog>()
    .Initialize<InteractiveDialogViewModel>(vm => vm.Message = "hi")
    .GetResultAsync<string>();
```

```xml
<!-- Growl 通知：先在窗口右侧准备容器并打标记，再 Growl.Success(...) 发送 -->
<ScrollViewer VerticalScrollBarVisibility="Hidden" HorizontalAlignment="Right">
    <StackPanel hc:Growl.GrowlParent="True" VerticalAlignment="Top" Margin="0,10,10,10"/>
</ScrollViewer>
```

更多配方（MessageBox、Loading、Pagination、PropertyGrid、国际化、多窗口 Growl）见 `references/recipes.md`。

## 排查清单

| 现象 | 先查 |
| --- | --- |
| 控件完全没变样 | App.xaml 是否合并了 `SkinDefault.xaml` + `Theme.xaml`，顺序是否皮肤在前 |
| `hc:XXX` 报找不到类型 | 是否漏了 `xmlns:hc`；该控件是不是原生控件（不该加 `hc:`） |
| `StaticResource` 找不到键 | 键名拼写；属于哪套 xaml；是否需要改成 `DynamicResource` |
| 覆盖样式不生效 | 是否用 `BasedOn="{StaticResource {x:Type Button}}"`；隐式样式没有 Key |
| 弹窗弹到错误窗口 | `Dialog.Show` 的 token 与 `hc:DialogContainer` 注册位置 |
| 通知不显示 | 容器是否标了 `hc:Growl.GrowlParent="True"` 或 `hc:Growl.Token` |

## 其他参考

| 内容 | 说明 | 文档 |
| --- | --- | --- |
| `GrowlInfo` | Growl 消息模型（Message / WaitTime / ConfirmStr / ActionBeforeClose 等） | data/GrowlInfo.md |
| `InfoType` | 消息类型枚举：Success=0、Info=1、Warning=2、Error=3、Fatal=4、Ask=5 | data/InfoType.md |
| 分区说明页 | 各分区总述：`quick_start.md`、`basic_xaml.md`、`attach.md`、`native_controls.md`、`extend_controls.md`、`langs.md` | 根目录 |

官网 "工具和扩展" 分区（Effect / HatchBrushGenerator / MorphingAnimation）三页只有标题、无正文，已剔除，未收录。

## 覆盖范围与维护

- 分区：快速开始 1、基础 XAML 10（1 索引 + 9 明细）、附加属性 19（1+18）、原生控件 35（1+34）、扩展控件 80（1+79）、数据类 2、国际化 1，共 148 篇。
- 每个 `references/**/*.md` 顶部有 `<!-- source: ... -->` 指回官网原页；有歧义时以官网与 GitHub 源码为准。
- 索引里的 86 个样式键、18 个附加属性类的属性名、75 个控件类名，均已对照 HandyControl 源码（master 分支 `Themes`、`Controls`）校验；文档写错的四处见上一节。
- 更新文档：在 `scripts/` 下运行 `python build_skill.py`，会浅克隆官网仓库、重建 `references/`、重算索引并重写 `SKILL.md`；`--skip-sync` 只重算索引，`--site <目录>` 复用已克隆的站点。依赖 `beautifulsoup4`、`markdownify`、`git`。
- 重建后建议跑两个自检：`python audit_skill.py`（结构、引用、篇数，纯本地）与 `python check_keys.py`（样式键与附加属性名对照 GitHub 源码，需联网）。
- NuGet 发布版约每月一更，可能滞后于文档与源码；`ConfigHelper`、`ThemeManager` 等少量 API 官网未收录。
