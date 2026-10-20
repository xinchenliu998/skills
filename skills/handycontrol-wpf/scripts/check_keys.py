"""对照 HandyControl 源码校验索引里的键名是否真实存在。

做法：拉 GitHub 仓库文件树 → 并发下载 Themes 下全部 xaml（取 x:Key）与
Controls/Attach 下的 cs（取依赖属性名）→ 逐条核对 SKILL.md / index.md 的表格。
只读网络，不改任何文件；用于官网文档更新后确认没有写错的键。

用法:
    python check_keys.py            # 默认校验上层 skill 目录
    python check_keys.py <skill 目录>
"""

from __future__ import annotations

import concurrent.futures
import json
import re
import sys
import urllib.request
from pathlib import Path

API = "https://api.github.com/repos/HandyOrg/HandyControl/git/trees/master?recursive=1"
RAW = "https://raw.githubusercontent.com/HandyOrg/HandyControl/master/"
THEMES = "src/Shared/HandyControl_Shared/Themes/"
ATTACH = "src/Shared/HandyControl_Shared/Controls/Attach/"


def fetch(url: str, retries: int = 3) -> str:
    last: Exception | None = None
    for _ in range(retries):
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                return r.read().decode("utf-8", "ignore")
        except Exception as exc:  # noqa: BLE001 - 网络异常统一重试
            last = exc
    raise RuntimeError(f"{url}: {last}")


def source_keys() -> tuple[set[str], dict[str, str]]:
    tree = json.loads(fetch(API))["tree"]
    xaml = [t["path"] for t in tree if t["path"].startswith(THEMES) and t["path"].endswith(".xaml")]
    cs = [t["path"] for t in tree if t["path"].startswith(ATTACH) and t["path"].endswith(".cs")]

    keys: set[str] = set()
    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as pool:
        for text in pool.map(lambda p: fetch(RAW + p), xaml):
            keys |= set(re.findall(r'x:Key="([^"]+)"', text))

    props: dict[str, str] = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        for path, text in zip(cs, pool.map(lambda p: fetch(RAW + p), cs)):
            props[path.rsplit("/", 1)[-1][:-3]] = text
    return keys, props


def table_rows(text: str, suffix: str) -> list[list[str]]:
    rows = []
    for line in text.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 3 and cells[-1].startswith(suffix):
            rows.append(cells)
    return rows


def main() -> int:
    skill = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
    md = (skill / "SKILL.md").read_text(encoding="utf-8")
    index = (skill / "references/index.md").read_text(encoding="utf-8")
    print("下载源码索引…")
    keys, props = source_keys()
    print(f"源码 x:Key {len(keys)} 个，Attach 类 {len(props)} 个")

    problems: list[str] = []
    for cells in table_rows(index, "native_controls/"):
        for key in re.findall(r"`([A-Za-z]\w*)`", cells[1]):
            if key not in keys:
                problems.append(f"样式键不存在: {key}（{cells[-1]}）")

    for cells in table_rows(md, "attach/"):
        cls = cells[0].split(" ")[0]
        body = props.get(cls)
        if body is None:
            problems.append(f"附加属性类无源码: {cls}")
            continue
        declared = set(re.findall(r"(\w+)Property\s*=", body))
        for name in re.findall(r"`([A-Za-z]\w*)`", cells[1]):
            if name not in declared:
                problems.append(f"{cls}.{name} 在源码中不存在")

    if problems:
        print(f"发现 {len(problems)} 处不一致：")
        for p in problems:
            print("  -", p)
        return 1
    print("键名校验通过：样式键与附加属性名都能在源码中找到")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
