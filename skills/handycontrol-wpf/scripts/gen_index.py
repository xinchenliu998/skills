"""生成索引表。

输出若干带 <!-- 名称 --> 标记的段落：
- EXTEND_COMPACT：仅 控件名 + XAML 标签，给 SKILL.md 用
- EXTEND_FULL：附一句话用途与文档路径，给 references/index.md 用
- NATIVE：原生控件可用样式键
- ATTACH：附加属性类与主要属性

扩展控件的标签名取文档示例中真实出现的 <hc:XXX 用法，因为部分页面首个
public class 是内部基类（LoadingBase / Row / TwoWayRangeBase 等）。
"""

from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

TAG_RE = re.compile(r"<hc:(\w+)[\s/>]")
TAG_LOOSE_RE = re.compile(r"hc:(\w+)")
CLASS_RE = re.compile(
    r"public (?:abstract |sealed |partial |static )*class (\w+)\s*(?::\s*([\w<>, .]+?))?\s*(?:\r?\n|\{|$)"
)
H1_RE = re.compile(r"^# (.+)$", re.M)
H2_RE = re.compile(r"^## (.+?) : (.+)$", re.M)
ROW_RE = re.compile(r"^\| ([A-Za-z_][\w.]*) \| (.+?) \|$", re.M)

# 页面里的非样式 H2（"FAQ" 之类）不能当成样式键
NOT_STYLE_HEADINGS = {"FAQ", "API", "TODO", "Note", "Tips"}
# 官网页面标题里的错别字，索引按正确控件名显示
NAME_FIX = {"Lable": "Label", "Seperator": "Separator"}
# 单行展示的样式键上限，超出只给数量
MAX_KEYS = 10

# 样式键与源码（HandyControl v3.0.0 / master 的 Themes）核对后的校正
STALE_KEYS = {
    # 文档正文自己说明：新版本用 BorderRegion，老版本才是 BorderRegionStyle
    "BorderRegionStyle": "BorderRegion",
}
DROP_KEYS = {
    # DataGrid 页里的居中列样式是示例中自定义的，库里没有这个键
    "DataGridTextCenterColumnStyle",
}

# 附加属性：文档属性表写错、但同页示例与源码一致的情况（按 slug 覆盖）
ATTACH_PROPS_FIX = {
    # 源码 RectangleAttach 只有 Circular（文档属性表误写成 CornerRadius）
    "rectangleAttach": ["Circular"],
}

# 文档里没有标准 XAML 标签（静态类、纯样式、一页多控件）的条目，人工校正
TAG_OVERRIDES = {
    "buttonGroup": "`hc:ButtonGroup`（子项为 RadioButton 样式）",
    "contextMenuButton": "`hc:ContextMenuButton` / `hc:ContextMenuToggleButton`",
    "dialog": "`hc:DialogContainer` + C# `Dialog.Show(...)`",
    "grid": "`hc:Row` / `hc:Col`",
    "growl": "C# 静态方法 `Growl.Success(...)`",
    "imageBrowser": "C# `new ImageBrowser(uri).Show()`",
    "loading": "`hc:LoadingLine` / `hc:LoadingCircle`",
    "messageBox": "C# `MessageBox.Success/Show(...)`",
    "notification": "C# 继承 `Notification` 后 `new Xxx().Show()`",
    "popTip": "`hc:Poptip`",
    "popupWindow": "C# 静态方法 `PopupWindow.Show(...)`",
    "screenshot": "C# `new Screenshot().Start()`",
    "sprite": "C# 继承 `Sprite` 后 `new Xxx().Show()`",
}


def one_liner(text: str, limit: int = 40) -> str:
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith(("#", "```", "|", "!", "<!--", ">", "-", "*")):
            continue
        line = re.sub(r"`", "", line)
        line = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", line)
        line = re.sub(r"\s+", " ", line)
        return line[:limit] + ("…" if len(line) > limit else "")
    return ""


def pick_tag(text: str, slug: str) -> str:
    """类名精确匹配优先于标签频次，避免示例里客串的其它控件抢走归属。"""
    low = slug.lower()
    classes = [m.group(1) for m in CLASS_RE.finditer(text)]
    tags = Counter(TAG_LOOSE_RE.findall(text))

    for pool in (classes, list(tags)):
        for name in pool:
            if name.lower() == low:
                return name
    for pool in (classes, list(tags)):
        for name in pool:
            if low in name.lower():
                return name
    if tags:
        return tags.most_common(1)[0][0]
    return ""


def iter_pages(root: Path, section: str):
    for path in sorted((root / section).glob("*.md")):
        text = path.read_text(encoding="utf-8")
        title_m = H1_RE.search(text)
        title = title_m.group(1).strip() if title_m else path.stem
        yield path, text, title


def table_extend(root: Path, compact: bool) -> list[str]:
    rows = []
    for path, text, title in iter_pages(root, "extend_controls"):
        tag = TAG_OVERRIDES.get(path.stem)
        if tag is None:
            name = pick_tag(text, path.stem)
            tag = f"`hc:{name}`" if name else "—"
        if compact:
            rows.append(f"| {title} | {tag} | extend_controls/{path.stem}.md |")
        else:
            desc = one_liner(text.split("\n", 3)[-1])
            rows.append(f"| {title} | {tag} | {desc} | extend_controls/{path.stem}.md |")
    return rows


def table_native(root: Path) -> list[str]:
    """样式键有两个来源：H2 标识符标题（`Key` 或 `Key : Parent`）与示例里的 Style="{StaticResource Key}"。"""
    rows = []
    for path, text, title in iter_pages(root, "native_controls"):
        m = re.match(r"[A-Za-z][A-Za-z0-9]*", title)
        name = m.group(0) if m else title.split(" ")[0]
        name = NAME_FIX.get(name, name)
        keys: list[str] = []
        for line in text.splitlines():
            h = re.match(r"^## ([A-Za-z]\w*)\s*(?::|$)", line)
            if h and h.group(1) not in NOT_STYLE_HEADINGS:
                keys.append(h.group(1))
        for used in re.findall(r'Style="\{StaticResource ([A-Za-z]\w*)\}"', text):
            keys.append(used)
        keys = [STALE_KEYS.get(k, k) for k in keys if k not in DROP_KEYS]
        uniq = list(dict.fromkeys(keys))
        if uniq:
            style = ", ".join(f"`{k}`" for k in uniq[:MAX_KEYS])
            if len(uniq) > MAX_KEYS:
                style += f" …(+{len(uniq) - MAX_KEYS})"
        else:
            style = "页内未列样式键，用隐式样式"
        rows.append(f"| {name} | {style} | native_controls/{path.stem}.md |")
    return rows


def table_attach(root: Path) -> list[str]:
    rows = []
    for path, text, title in iter_pages(root, "attach"):
        props = ATTACH_PROPS_FIX.get(path.stem) or [
            n for n, _ in ROW_RE.findall(text) if n not in ("名称", "属性名称", "Property")
        ]
        shown = ", ".join(f"`{p}`" for p in props[:10])
        if len(props) > 10:
            shown += f" …(+{len(props) - 10})"
        rows.append(f"| {title} | {shown or '—'} | attach/{path.stem}.md |")
    return rows


def build_sections(root: Path) -> dict[str, str]:
    """返回 {段名: 表格 markdown}，供 SKILL.md 与 references/index.md 装配。"""
    return {
        "EXTEND_COMPACT": "| 控件 | 标签 / 调用方式 | 文档 |\n| --- | --- | --- |\n"
        + "\n".join(table_extend(root, compact=True)),
        "EXTEND_FULL": "| 控件 | XAML 标签 | 用途 | 文档 |\n| --- | --- | --- | --- |\n"
        + "\n".join(table_extend(root, compact=False)),
        "NATIVE": "| 控件 | 可用样式键 | 文档 |\n| --- | --- | --- |\n" + "\n".join(table_native(root)),
        "ATTACH": "| 附加属性类 | 主要属性 | 文档 |\n| --- | --- | --- |\n" + "\n".join(table_attach(root)),
    }


def main(root: Path) -> None:
    for name, table in build_sections(root).items():
        print(f"\n<!-- {name} -->")
        print(table)


if __name__ == "__main__":
    main(Path(sys.argv[1]))
