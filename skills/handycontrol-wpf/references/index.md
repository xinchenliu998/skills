# 控件总索引

`references/` 下一控件一文件，文件名取标签名的小驼峰形式（例外：`hc:Poptip`→`popTip.md`、
`hc:LoadingLine`/`hc:LoadingCircle`→`loading.md`、`hc:Row`/`hc:Col`→`grid.md`）。
分区索引页：`quick_start.md`、`basic_xaml.md`、`attach.md`、`native_controls.md`、`extend_controls.md`、`langs.md`；
另有数据类 `data/GrowlInfo.md`、`data/InfoType.md`（官网 tools 分区三页无正文，未收录）。

## 扩展控件（79）

`hc:` 前缀，均位于 `HandyControl.Controls`。

| 控件 | XAML 标签 | 用途 | 文档 |
| --- | --- | --- | --- |
| AnimationPath 动画路径 | `hc:AnimationPath` | AnimationPath动画路径，设定Geometry派生类型几何图形的数据，… | extend_controls/animationPath.md |
| Badge 标记 | `hc:Badge` | 标记控件作为其他控件的特定状态内容标记，能够做到最小程度的侵入原有控件，可以看作… | extend_controls/badge.md |
| BlurWindow 背景模糊窗口 | `hc:BlurWindow` | 背景模糊窗口可用于增强UI效果，但是会牺牲部分性能. | extend_controls/blurWindow.md |
| ButtonGroup 按钮组 | `hc:ButtonGroup`（子项为 RadioButton 样式） | ButtonGroup控件中的子集RadioButton样式基类，不建议直接使用… | extend_controls/buttonGroup.md |
| CalendarWithClock 带有时钟的日历 | `hc:CalendarWithClock` | CalendarWithClock 控件由日历和时钟组成，允许用户通过鼠标选择日… | extend_controls/calendarWithClock.md |
| Card 卡片 | `hc:Card` | 用于卡片化展示数据，为ContentControl的派生类 | extend_controls/card.md |
| Carousel 轮播 | `hc:Carousel` | 可以在固定时间内循环切换项目。 | extend_controls/carousel.md |
| ChatBubble 对话气泡 | `hc:ChatBubble` | 对话气泡常出现于通讯类软件中，相对于纯文本形式的上下文对话，使用对话气泡可以让聊… | extend_controls/chatBubble.md |
| CheckComboBox 复选组合框 | `hc:CheckComboBox` | 可选选中多个项目的组合框. | extend_controls/checkComboBox.md |
| CirclePanel 圆形布局 | `hc:CirclePanel` | 圆形布局常用作方向按钮、功能按钮的容器。 | extend_controls/circlePanel.md |
| CircleProgressBar 圆形进度条 | `hc:CircleProgressBar` | 在宽高存在一定限制的区域可以使用圆形进度条节省空间。 | extend_controls/circleProgressBar.md |
| Clock 时钟 | `hc:Clock` | Clock 控件展示一个虚拟的时钟，允许用户在这个时钟上选择时间。 | extend_controls/clock.md |
| ColorPicker 颜色拾取器 | `hc:ColorPicker` | 仿制Chrome的颜色拾取器，相关博文：《WPF 控件库——仿制Chrome的C… | extend_controls/colorPicker.md |
| ComboBox 组合框 | `hc:ComboBox` | 原生组合框的HC扩展。 | extend_controls/comboBox.md |
| CompareSlider 对比滑块 | `hc:CompareSlider` | 借助对比滑块可以很方便得看出元素改动前后的差异。 | extend_controls/compareSlider.md |
| ContextMenuButton 上下文菜单按钮 | `hc:ContextMenuButton` / `hc:ContextMenuToggleButton` | HC提供了两个上下文菜单按钮，分别是 ContextMenuButton 和 C… | extend_controls/contextMenuButton.md |
| CoverFlow 封面流 | `hc:CoverFlow` | 该控件将封面以3D的形式展示出来，可用于增强界面效果。 | extend_controls/coverFlow.md |
| CoverView 封面视图 | `hc:CoverView` | 仿制Itunes的专辑视图。 | extend_controls/coverView.md |
| DashedBorder 虚线边框 | `hc:DashedBorder` | 一种装饰元素，可提供虚线边框，以实现某些特殊效果. | extend_controls/dashedBorder.md |
| DatePicker 日期选择器 | `hc:DatePicker` | DatePicker 控件允许用户通过在文本框中键入日期或使用下拉的日历控件来选… | extend_controls/datePicker.md |
| DateTimePicker 日期时间选择器 | `hc:DateTimePicker` | DatePicker 控件允许用户通过在文本框中键入日期和时间，或使用下拉的日历… | extend_controls/dateTimePicker.md |
| Dialog 对话框 | `hc:DialogContainer` + C# `Dialog.Show(...)` | 在保留当前页面状态的情况下，告知用户并承载相关操作。 | extend_controls/dialog.md |
| Divider 分割线 | `hc:Divider` | 区隔内容的分割线。 | extend_controls/divider.md |
| Drawer 抽屉 | `hc:Drawer` | 当 Dialog 组件不能满足我们的需求时（例如展示一些文档），可以使用 Dra… | extend_controls/drawer.md |
| FlipClock 翻页时钟 | `hc:FlipClock` | 一种3D形式的时钟方案。 | extend_controls/flipClock.md |
| FloatingBlock 漂浮块 | `hc:FloatingBlock` | 可借助漂浮块实现特殊的点击效果。 | extend_controls/floatingBlock.md |
| GifImage Gif图片 | `hc:GifImage` | Gif的wpf实现。 | extend_controls/gifImage.md |
| GlowWindow 辉光窗口 | `hc:GlowWindow` | 边框具有辉光效果的窗口，代码提取自Visual Studio | extend_controls/glowWindow.md |
| GotoTop 回到顶部 | `hc:GotoTop` | 通过点击 GotoTop 可以让 ScrollView 或带有 ScrollVi… | extend_controls/gotoTop.md |
| Gravatar 头像 | `hc:Gravatar` | 一种用户随机头像的实现方式. | extend_controls/gravatar.md |
| Grid 栅格 | `hc:Row` / `hc:Col` | 栅格系统的wpf实现，web版本可参考 element/layout | extend_controls/grid.md |
| Growl 信息通知 | C# 静态方法 `Growl.Success(...)` | 当需要在窗口的右侧区域，以从上到下排列通知信息时可以使用本控件。 | extend_controls/growl.md |
| HoneycombPanel 蜂窝布局 | `hc:HoneycombPanel` | 一种可以让子元素呈现蜂窝状布局的容器. | extend_controls/honeycombPanel.md |
| ImageBlock 图片块 | `hc:ImageBlock` | 图片块可用于将一张大图片分割成宽高一致的小图片，并按序播放形成类似于gif图片的… | extend_controls/imageBlock.md |
| ImageBrowser 图片浏览器 | C# `new ImageBrowser(uri).Show()` | 可借助 ImageBrowser 简单地浏览单张图片. | extend_controls/imageBrowser.md |
| ImageSelector 图片选择器 | `hc:ImageSelector` | 该控件封装了图片选择、展示、删除的一整套逻辑. | extend_controls/imageSelector.md |
| ImageViewer 图片视图 | `hc:ImageViewer` | ImageViewer 是 ImageBrowser 的核心构件，它可以作为独立… | extend_controls/imageViewer.md |
| Loading 加载条 | `hc:LoadingLine` / `hc:LoadingCircle` | 耗时操作时显示动效，目前包含圆形和直线两种加载条。相关博文：《WPF 控件库——… | extend_controls/loading.md |
| Magnifier 放大镜 | `hc:Magnifier` | 借助 Magnifier 可对任意控件局部放大. | extend_controls/magnifier.md |
| MessageBox 消息对话框 | C# `MessageBox.Success/Show(...)` | HC重写了一套消息对话框，使用方式和原生一致. | extend_controls/messageBox.md |
| Notification 桌面通知 | C# 继承 `Notification` 后 `new Xxx().Show()` | 用于在桌面显示一则富内容消息. | extend_controls/notification.md |
| NotifyIcon 托盘图标 | `hc:NotifyIcon` | 系统托盘图标的wpf实现方式. | extend_controls/notifyIcon.md |
| NumericUpDown 数值选择控件 | `hc:NumericUpDown` | NumericUpDown 控件看起来像一对用户可以单击来调整值的箭头按钮和Te… | extend_controls/numericUpDown.md |
| OutlineText 轮廓文本 | `hc:OutlineText` | OutlineText 可以使文本突出显示. | extend_controls/outlineText.md |
| Pagination 页码条 | `hc:Pagination` | 当数据量过多时，使用分页分解数据. | extend_controls/pagination.md |
| PasswordBox 密码框 | `hc:PasswordBox` | 表示用于输入和处理密码的控件。 | extend_controls/passwordBox.md |
| PinBox PIN码框 | `hc:PinBox` | 密码框的另一种形式. | extend_controls/pinBox.md |
| PopTip 气泡提示 | `hc:Poptip` | 常用于展示鼠标 hover 时的提示信息. | extend_controls/popTip.md |
| PopupWindow 弹出窗口 | C# 静态方法 `PopupWindow.Show(...)` | PopupWindow 相对于 PopTip 能更灵活地控制弹出元素的位置. | extend_controls/popupWindow.md |
| PreviewSlider 预览滑块 | `hc:PreviewSlider` | 可借助预览滑块向用户反馈在不同位置的状态信息. | extend_controls/previewSlider.md |
| ProgressButton 进度按钮 | `hc:ProgressButton` | 在切换按钮的基础上附带了进度显示. | extend_controls/progressButton.md |
| PropertyGrid 属性编辑器 | `hc:PropertyGrid` | 可自动为模型对象中的属性生成与之相匹配的编辑器集合. | extend_controls/propertyGrid.md |
| RangeSlider 范围滑块 | `hc:RangeSlider` | 支持选择某一数值范围. | extend_controls/rangeSlider.md |
| Rate 评分 | `hc:Rate` | 当对评价进行展示或对事物进行快速的评级操作时，可使用评分控件. | extend_controls/rate.md |
| RelativePanel 相对布局 | `hc:RelativePanel` | 可以使用 RelativePanel 的附加属性对其内容进行相对布局. | extend_controls/relativePanel.md |
| RunningBlock 滚动块 | `hc:RunningBlock` | 滚动块可用于对连续性内容进行轮播. | extend_controls/runningBlock.md |
| Screenshot 截图 | C# `new Screenshot().Start()` | 可通过快捷键触发，将整个屏幕或者指定区域内容保存为图片. | extend_controls/screenshot.md |
| ScrollViewer 滚动视图 | `hc:ScrollViewer` | 对原生滚动视图的扩展. | extend_controls/scrollViewer.md |
| SearchBar 搜索栏 | `hc:SearchBar` | 通过键入关键字触发搜索. | extend_controls/searchBar.md |
| Shield 徽章 | `hc:Shield` | 徽章由左半部分的名称和右半部分的值组成，点击徽章可以打开对应的链接. | extend_controls/shield.md |
| SideMenu 侧边菜单 | `hc:SideMenu` | 当界面为左右布局时，可以使用侧边菜单来导航. | extend_controls/sideMenu.md |
| SimpleItemsControl 简单项目控件 | `hc:SimpleItemsControl` | 一种轻量级ItemsControl控件. | extend_controls/simpleItemsControl.md |
| SimplePanel 简单面板 | `hc:SimplePanel` | 当不需要Grid的行、列分隔等功能时建议用此轻量级类代替. | extend_controls/simplePanel.md |
| SimpleText 简单文本 | `hc:SimpleText` | 一种轻量级文本显示控件. | extend_controls/simpleText.md |
| SplitButton 分割按钮 | `hc:SplitButton` | 在普通按钮的基础上提供额外的点击项. | extend_controls/splitButton.md |
| Sprite 精灵 | C# 继承 `Sprite` 后 `new Xxx().Show()` | 可将常用功能集成到 Sprite 中而无需打开主程序. | extend_controls/sprite.md |
| StepBar 步骤条 | `hc:StepBar` | 引导用户按照流程完成任务的分步导航条. | extend_controls/stepBar.md |
| TabControl 选项卡控件 | `hc:TabControl` | HC 对wpf原生 TabControl 的扩展. | extend_controls/tabControl.md |
| Tag 标签 | `hc:Tag` | 用以指示用户选中的项，相对于文字，Tag 有额外的交互. | extend_controls/tag.md |
| TextBox 文本框 | `hc:TextBox` | 表示一个控件，该控件可用于显示或编辑无格式文本。 | extend_controls/textBox.md |
| TimeBar 时间条 | `hc:TimeBar` | 一种包含热区和时间刻度的进度条. | extend_controls/timeBar.md |
| TimePicker 时间选择器 | `hc:TimePicker` | TimePicker 控件允许用户通过在文本框中键入时间或使用下拉的日历控件来选… | extend_controls/timePicker.md |
| ToggleBlock 切换块 | `hc:ToggleBlock` | 该控件可根据选中状态切换显示内容，在某些情况下可以代替 ToggleButton… | extend_controls/toggleBlock.md |
| Transfer 穿梭框 | `hc:Transfer` | 穿梭选择框用直观的方式在两栏中移动元素，完成选择行为。 | extend_controls/transfer.md |
| TransitioningContentControl 内容过渡控件 | `hc:TransitioningContentControl` | 主要用于变化内容的过渡呈现效果. | extend_controls/transitioningContentControl.md |
| WaterfallPanel 瀑布流 | `hc:WaterfallPanel` | 该面板可使元素按照等宽不等高或者等高不等宽进行布局. | extend_controls/waterfallPanel.md |
| Watermark 水印 | `hc:Watermark` | 可使用指定的内容创建平铺背景. | extend_controls/watermark.md |
| WaveProgressBar 波形进度条 | `hc:WaveProgressBar` | 进度条的一种特殊效果，可用于增强用户体验. | extend_controls/waveProgressBar.md |
| Window 窗口 | `hc:Window` | HC 对wpf原生 Window 的扩展. | extend_controls/window.md |

## 原生控件样式键

原生控件默认走隐式样式；下表的键可用 `Style="{StaticResource 键名}"` 切换外观。

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
