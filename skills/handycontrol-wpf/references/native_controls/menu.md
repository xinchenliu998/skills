# Menu 菜单

<!-- source: https://handyorg.github.io/handycontrol/native_controls/menu/ -->

## MenuBaseStyle

菜单默认样式，不推荐直接使用，应该始终被其它样式以BasedOn的方式使用。

用例：

```xml
    <Menu ItemsSource="{Binding Menus}">
        <Menu.ItemTemplate>
            <HierarchicalDataTemplate ItemsSource="{Binding Children}">
                <TextBlock Text="{Binding Name}"></TextBlock>
            </HierarchicalDataTemplate>
        </Menu.ItemTemplate>
</Menu>
```

![Menu.BaseStyle](https://raw.githubusercontent.com/HandyOrg/HandyOrgResource/master/HandyControl/Doc/native_controls/Menu.BaseStyle.png)
