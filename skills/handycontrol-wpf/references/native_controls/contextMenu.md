# ContextMenu 上下文菜单

<!-- source: https://handyorg.github.io/handycontrol/native_controls/contextMenu/ -->

## ContextMenuBaseStyle

上下文菜单默认样式，不推荐直接使用，应该始终被其它样式以BasedOn的方式使用。

用例：

```xml
<ContextMenu ItemsSource="{Binding DataList}">
    <ContextMenu.ItemTemplate>
        <HierarchicalDataTemplate ItemsSource="{Binding DataList}">
            <TextBlock Text="{Binding Name}"/>
        </HierarchicalDataTemplate>
    </ContextMenu.ItemTemplate>
</ContextMenu>
```
![ContextMenu](https://raw.githubusercontent.com/HandyOrg/HandyOrgResource/master/HandyControl/Resources/ContextMenu.png)
