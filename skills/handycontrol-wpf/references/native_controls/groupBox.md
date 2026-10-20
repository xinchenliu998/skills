# GroupBox 分组框

<!-- source: https://handyorg.github.io/handycontrol/native_controls/groupBox/ -->

## GroupBoxBaseStyle

GroupBox 分组框 默认样式，不推荐直接使用，应该始终被其它样式以BasedOn的方式使用。

用例：

```xml
<GroupBox Grid.Row="0" Grid.Column="0" Width="300" Height="200" Header="{x:Static langs:Lang.TitleDemoStr1}" 
    Padding="10" Margin="16">
    <Border Background="{DynamicResource PrimaryBrush}" CornerRadius="4">
        <TextBlock Text="{x:Static langs:Lang.ContentDemoStr}" VerticalAlignment="Center" HorizontalAlignment="Center" 
        Foreground="White"/>
    </Border>
</GroupBox>
```
![GroupBoxBaseStyle](https://raw.githubusercontent.com/HandyOrg/HandyOrgResource/master/HandyControl/Doc/native_controls/GroupBox_Base.png)

这里提供另外一种样式,供开发者选择

只需要添加扩展属性即可

```text
hc:TitleElement.TitlePlacement="Left"
```
用例：
```xml
<GroupBox Grid.Row="0" Grid.Column="1" Width="300" Height="200" Header="{x:Static langs:Lang.TitleDemoStr1}" Padding="10" 
    Margin="16"  hc:TitleElement.TitlePlacement="Left">
    <Border Background="{DynamicResource PrimaryBrush}" CornerRadius="4">
        <TextBlock Text="{x:Static langs:Lang.ContentDemoStr}" VerticalAlignment="Center" HorizontalAlignment="Center" 
        Foreground="White"/>
    </Border>
</GroupBox>
```

![GroupBox_Base_left](https://raw.githubusercontent.com/HandyOrg/HandyOrgResource/master/HandyControl/Doc/native_controls/GroupBox_Base_left.png)

## GroupBoxTab : GroupBoxTabBaseStyle : GroupBoxBaseStyle

GroupBox 分组框 的另一种样式 GroupBoxTabBaseStyle 不推荐直接使用，应该始终被其它样式以BasedOn的方式使用。

用例：

```xml
<GroupBox Grid.Row="1" Grid.Column="0" Width="300" Height="200" Header="{x:Static langs:Lang.TitleDemoStr1}" Padding="10" 
    Margin="16" Style="{StaticResource GroupBoxTab}">
    <Border Background="{DynamicResource PrimaryBrush}" CornerRadius="4">
        <TextBlock Text="{x:Static langs:Lang.ContentDemoStr}" VerticalAlignment="Center" HorizontalAlignment="Center" 
        Foreground="White"/>
    </Border>
</GroupBox>
```

- 同样可以 使用扩展属性
  ```text
hc:TitleElement.TitlePlacement="Left" 
```

![GroupBox_Tab](https://raw.githubusercontent.com/HandyOrg/HandyOrgResource/master/HandyControl/Doc/native_controls/GroupBox_Tab.png) ![GroupBox_Tab_left](https://raw.githubusercontent.com/HandyOrg/HandyOrgResource/master/HandyControl/Doc/native_controls/GroupBox_Tab_left.png)

## GroupBoxOriginal : GroupBoxOriginalBaseStyle : GroupBoxBaseStyle

GroupBox 分组框 的另一种样式 GroupBoxOriginalBaseStyle 不推荐直接使用，应该始终被其它样式以BasedOn的方式使用。

用例：

```xml
<GroupBox Grid.Row="2" Grid.Column="0" Width="300" Header="{x:Static langs:Lang.TitleDemoStr1}" Margin="16" 
    Style="{StaticResource GroupBoxOriginal}" HorizontalContentAlignment="Left">
    <TextBox/>
</GroupBox>
<GroupBox Grid.Row="2" VerticalAlignment="Bottom" Grid.Column="1" Width="300" hc:TitleElement.TitleWidth="100"
    Header="{x:Static langs:Lang.TitleDemoStr1}" Margin="16" Style="{StaticResource GroupBoxOriginal}"
    HorizontalContentAlignment="Left" hc:TitleElement.TitlePlacement="Left">
    <ComboBox DataContext="{Binding ComboBoxDemo,Source={StaticResource Locator}}" ItemsSource="{Binding DataList}"/>
</GroupBox>
```

![GroupBox_Origin](https://raw.githubusercontent.com/HandyOrg/HandyOrgResource/master/HandyControl/Doc/native_controls/GroupBox_Origin.png) ![GroupBox_Origin_left](https://raw.githubusercontent.com/HandyOrg/HandyOrgResource/master/HandyControl/Doc/native_controls/GroupBox_Origin_left.png)
