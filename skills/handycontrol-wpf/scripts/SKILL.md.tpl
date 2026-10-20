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

<!-- INDEX_EXTEND -->

## 原生控件与可用样式键

原生控件默认走隐式样式；下表的键通过 `Style="{StaticResource 键名}"` 切换外观。

<!-- INDEX_NATIVE -->

## 附加属性

形态 `hc:类名.属性名`。

<!-- INDEX_ATTACH -->

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
