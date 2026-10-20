# 常用配方

全部示例取自官网文档，属性名与默认值以对应控件页为准。每节末尾标注详细文档路径（相对 `references/`）。

## 表单输入

`InfoElement` 继承自 `TitleElement`，一套附加属性即可给输入类控件加标题、占位符、必填星号。

```xml
<hc:TextBox hc:InfoElement.Title="设备编号"
            hc:InfoElement.Placeholder="请输入 8 位编号"
            hc:InfoElement.Necessary="True"
            hc:InfoElement.RegexPattern="^\d{8}$"/>
```

```xml
<!-- 标题位置：Top（顶）/ Left（左），另有 TitleWidth、Symbol 可调 -->
<hc:TextBox hc:InfoElement.Title="标题信息" hc:TitleElement.TitlePlacement="Left"/>
```

`hc:InfoElement.Symbol="x"` 可替换必填标记符号。详见 `attach/infoElement.md`、`attach/titleElement.md`。

## 自定义标题栏窗口

用 `hc:Window` 替代 `Window`；非客户区内容用 `NonClientAreaContent` 注入，`ShowTitle`、`NonClientAreaHeight` 控制是否显示标题与区域高度。

```xml
<hc:Window x:Class="App.MainWindow"
           xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
           xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
           xmlns:hc="https://handyorg.github.io/handycontrol"
           ShowNonClientArea="True" NonClientAreaHeight="32">
    <hc:Window.NonClientAreaContent>
        <TextBlock Text="标题" VerticalAlignment="Center" Margin="10,0,0,0"/>
    </hc:Window.NonClientAreaContent>
</hc:Window>
```

窗口级附加能力（拖动、忽略 Alt+F4、任务栏显示）用 `hc:WindowAttach`：

```xml
<hc:Window hc:WindowAttach.IsDragElement="True" hc:WindowAttach.IgnoreAltF4="True"/>
```

需要更炫的外观时换 `hc:BlurWindow`（背景模糊，牺牲性能）或 `hc:GlowWindow`（边框辉光）。
详见 `extend_controls/window.md`、`attach/windowAttach.md`、`extend_controls/blurWindow.md`、`extend_controls/glowWindow.md`。

## 内容对话框 Dialog

承载内容通常是 `Border` + `x:Class` 的 UserControl；关闭按钮直接绑 `hc:ControlCommands.Close`。

```xml
<Border x:Class="App.Views.TextDialog" Width="400" Height="247"
        xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        xmlns:hc="https://handyorg.github.io/handycontrol"
        Background="{DynamicResource RegionBrush}" CornerRadius="10">
    <hc:SimplePanel>
        <TextBlock Text="处理中…" HorizontalAlignment="Center" VerticalAlignment="Center"/>
        <Button Command="hc:ControlCommands.Close" Style="{StaticResource ButtonIcon}"
                hc:IconElement.Geometry="{StaticResource CloseGeometry}"
                Foreground="{DynamicResource PrimaryBrush}"
                HorizontalAlignment="Right" VerticalAlignment="Top"/>
    </hc:SimplePanel>
</Border>
```

```csharp
Dialog.Show(new TextDialog());       // 立即弹出
var d = Dialog.Show<ProgressDialog>();  // 泛型自动实例化
await Task.Delay(5000);
d.Close();                            // 手动关闭

// 等对话框返回结果
Dialog.Show<InteractiveDialog>()
    .Initialize<InteractiveDialogViewModel>(vm => vm.Message = DialogResult)
    .GetResultAsync<string>()
    .ContinueWith(t => DialogResult = t.Result);
```

不传 `token` 时在**当前激活窗口**弹出；传入元素则在该元素的 `hc:DialogContainer` 内弹出：

```xml
<UserControl hc:Dialog.Token="DialogContainer">
    <hc:DialogContainer>
        <!-- 内部控件 -->
    </hc:DialogContainer>
</UserControl>
```

详见 `extend_controls/dialog.md`。

## 消息框 MessageBox

用法与原生一致，另有语义化快捷方法。

```csharp
// 每个语义方法都是 (消息, 标题) 两个参数
MessageBox.Success("保存成功", "提示");
MessageBox.Info("已刷新", "提示");
MessageBox.Warning("配置已过期", "警告");
MessageBox.Error("写入失败", "错误");
MessageBox.Fatal("不可恢复错误", "致命错误");
MessageBox.Ask("确定删除？", "请确认");
// 需要自定义按钮/图标时用原生签名
MessageBox.Show("内容", "标题", MessageBoxButton.YesNo, MessageBoxImage.Question);
```

详见 `extend_controls/messageBox.md`。

## 右上角通知 Growl

第一步，在窗口右侧放置容器并打标记；第二步，调 `Growl` 静态方法发送。

```xml
<ScrollViewer VerticalScrollBarVisibility="Hidden" HorizontalAlignment="Right">
    <StackPanel hc:Growl.GrowlParent="True" VerticalAlignment="Top" Margin="0,10,10,10"/>
</ScrollViewer>
```

```csharp
Growl.Success("文件保存成功！");
Growl.Warning("磁盘空间不足", "SuccessMsg");   // 第二参为 Token，只发往该标记的容器
```

- **只在激活窗口显示**：重写窗口 `OnActivated` / `OnDeactivated`，分别调 `Growl.SetGrowlParent(panel, true)` / `(panel, false)`，此时 xaml 不必写 `GrowlParent`。一个窗口对应一个容器，Growl 内部只保存最近一次注册的容器。
- **发往指定容器**：容器上写 `hc:Growl.Token="SuccessMsg"`，调用时带上同名 Token。

详见 `extend_controls/growl.md`。

## 加载动效 Loading

```xml
<hc:LoadingLine/>                                  <!-- 直线，默认 -->
<hc:LoadingCircle/>                                <!-- 圆形 -->
<hc:LoadingCircle Style="{StaticResource LoadingCircleLight}"/>  <!-- 浅色，用于深底 -->
<hc:LoadingLine IsRunning="{Binding IsBusy}" Style="{StaticResource LoadingLineLarge}"/>
```

基类 `LoadingBase` 常用属性：`IsRunning`(true)、`DotCount`(5)、`DotDiameter`(6)、`DotSpeed`(4s)、`DotDelayTime`(80ms)。详见 `extend_controls/loading.md`。

## 分页 Pagination

```xml
<hc:Pagination MaxPageCount="{Binding MaxPageCount}"
               PageIndex="{Binding PageIndex}"
               DataCountPerPage="20"
               IsJumpEnabled="True"
               PageUpdated="OnPageUpdated"/>
```

`MaxPageInterval`(3) 控制省略号出现的距离。详见 `extend_controls/pagination.md`。

## 属性面板 PropertyGrid

```xml
<hc:PropertyGrid SelectedObject="{Binding Model}" MaxTitleWidth="120" MinTitleWidth="80"/>
```

内置编辑器：`NumberPropertyEditor`、`PlainTextPropertyEditor`、`ReadOnlyTextPropertyEditor`、`SwitchPropertyEditor`、`EnumPropertyEditor`、`DatePropertyEditor`、`DateTimePropertyEditor`、`ImagePropertyEditor`、`HorizontalAlignmentPropertyEditor`。详见 `extend_controls/propertyGrid.md`。

## 数据列表与步骤引导

- `hc:StepBar`：分步导航条，`extend_controls/stepBar.md`
- `hc:TabControl`：扩展选项卡（样式键 `TabControlInLine`、`TabControlCapsuleSolid`），`extend_controls/tabControl.md`
- `hc:SideMenu`：左右布局的侧边导航，`extend_controls/sideMenu.md`
- `hc:Transfer`：穿梭框，`extend_controls/transfer.md`
- `hc:Carousel`：轮播，`extend_controls/carousel.md`

## 托盘与桌面通知

- `hc:NotifyIcon`（XAML 控件）：系统托盘图标，`extend_controls/notifyIcon.md`
- `Notification`（C# 驱动）：继承 `Notification` 后 `new 你的通知().Show()`，`extend_controls/notification.md`
- `hc:Gravatar`（XAML 控件）：随机头像，`extend_controls/gravatar.md`
- `Screenshot`（C# 驱动）：`new Screenshot().Start()` 触发截图，`extend_controls/screenshot.md`

## 国际化

```csharp
ConfigHelper.Instance.SetLang("en");   // zh-cn（默认）/ en / fa / fr / ko-kr
```

```xml
<TextBlock Text="{x:Static hc:Lang.Cancel}"/>
```

语言包不支持运行时动态切换。详见 `langs.md`。

## 主题与皮肤

官方文档只说明 `Themes/SkinDefault.xaml` + `Themes/Theme.xaml` 的合并方式，以及 `Colors.xaml` / `ColorsDark.xaml` / `ColorsViolet.xaml` 三套配色。运行时切换主题的 API 官网未收录，请查源码 `HandyControl/Themes` 与 `ThemeManager`，不要凭记忆写。
