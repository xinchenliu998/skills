# Lable标签

<!-- source: https://handyorg.github.io/handycontrol/native_controls/label/ -->

## LabelBaseStyle

Label标签默认样式，不推荐直接使用，应该始终被其它样式以BasedOn的方式使用。

用例：

```xml
<Label Content="Label默认样式" Margin="10"></Label>
```

![Label.BaseStyle](https://raw.githubusercontent.com/HandyOrg/HandyOrgResource/master/HandyControl/Doc/native_controls/Label.BaseStyle.png)

## LabelPrimary : LabelBaseStyle

主样式

用例：

```xml
<Label Content="LabelPrimary样式" Margin="10" Style="{DynamicResource LabelPrimary}"></Label>
```

![Label.PrimaryStyle](https://raw.githubusercontent.com/HandyOrg/HandyOrgResource/master/HandyControl/Doc/native_controls/Label.PrimaryStyle.png)

## LabelSuccess : LabelBaseStyle

成功类型样式

用例：

```xml
<Label Content="LabelSuccess样式" Margin="10" Style="{DynamicResource LabelSuccess}"></Label>
```

![Label.SuccessStyle](https://raw.githubusercontent.com/HandyOrg/HandyOrgResource/master/HandyControl/Doc/native_controls/Label.SuccessStyle.png)

## LabelInfo : LabelBaseStyle

信息类型样式

用例：

```xml
<Label Content="LabelInfo样式" Margin="10" Style="{DynamicResource LabelInfo}"></Label>
```

![Label.InfoStyle](https://raw.githubusercontent.com/HandyOrg/HandyOrgResource/master/HandyControl/Doc/native_controls/Label.InfoStyle.png)

## LabelWarning : LabelBaseStyle

警告类型样式

用例：

```xml
<Label Content="LabelWarning样式" Margin="10" Style="{DynamicResource LabelWarning}"></Label>
```

![Label.WarningStyle](https://raw.githubusercontent.com/HandyOrg/HandyOrgResource/master/HandyControl/Doc/native_controls/Label.WarningStyle.png)

## LabelDanger : LabelBaseStyle

危险类型样式

用例：

```xml
<Label Content="LabelDanger样式" Margin="10" Style="{DynamicResource LabelDanger}"></Label>
```

![Label.DangerStyle](https://raw.githubusercontent.com/HandyOrg/HandyOrgResource/master/HandyControl/Doc/native_controls/Label.DangerStyle.png)
