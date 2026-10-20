# CheckBox 复选框

<!-- source: https://handyorg.github.io/handycontrol/native_controls/checkBox/ -->

## CheckBoxBaseStyle

复选框默认样式，不推荐直接使用，应该始终被其它样式以BasedOn的方式使用。

用例：

```xml
<StackPanel>
    <CheckBox Content="CheckBox" IsChecked="True"/>
    <CheckBox Margin="0,16,0,0" Content="CheckBox" IsChecked="True" IsEnabled="False"/>
    <CheckBox Margin="0,16,0,0" Content="CheckBox"/>
    <CheckBox Margin="0,16,0,0" Content="CheckBox" IsEnabled="False"/>
    <CheckBox Margin="0,16,0,0" Content="CheckBox" IsChecked="{x:Null}"/>
    <CheckBox Margin="0,16,0,0" Content="CheckBox" IsChecked="{x:Null}" IsEnabled="False"/>
</StackPanel>
```
![CheckBox](https://raw.githubusercontent.com/HandyOrg/HandyOrgResource/master/HandyControl/Resources/CheckBox.png)
