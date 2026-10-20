# Sprite 精灵

<!-- source: https://handyorg.github.io/handycontrol/extend_controls/sprite/ -->

可将常用功能集成到 `Sprite` 中而无需打开主程序.

```csharp
public sealed class Sprite : System.Windows.Window
```

## 方法

| 名称 | 说明 |
| --- | --- |
| Show(object) | 将内容作为控件主体，Pin 到桌面上 |

## 案例

```xml
<hc:SimplePanel x:Class="HandyControlDemo.UserControl.AppSprite"
             xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
             xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
             xmlns:hc="https://handyorg.github.io/handycontrol">
    <Border Background="White" CornerRadius="20" Effect="{StaticResource EffectShadow4}">
        <Path Width="70" Height="70" Data="{StaticResource LogoGeometry}" Fill="#f06632"/>
    </Border>
    <Button Command="hc:ControlCommands.CloseWindow" CommandParameter="{Binding RelativeSource={RelativeSource Self}}" Visibility="{Binding IsMouseOver,RelativeSource={RelativeSource AncestorType=hc:SimplePanel},Converter={StaticResource Boolean2VisibilityConverter}}" Width="22" Height="22" Style="{StaticResource ButtonIcon}" Foreground="White" hc:IconElement.Geometry="{StaticResource ErrorGeometry}" Padding="0" HorizontalAlignment="Right" VerticalAlignment="Top" Margin="0,-8,-8,0"/>
</hc:SimplePanel>
```
```csharp
public partial class AppSprite
{
    public AppSprite()
    {
        InitializeComponent();
    }
}
```
```csharp
Sprite.Show(new AppSprite());
```
