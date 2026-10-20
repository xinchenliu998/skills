"""重建整个 skill：同步官网文档 → 重算索引 → 装配 SKILL.md。

依赖：beautifulsoup4、markdownify，以及本机的 git（用于浅克隆官网仓库）。

用法:
    python build_skill.py                     # 在 scripts/ 内运行，输出到上层 skill 目录
    python build_skill.py --site <克隆目录>    # 复用已克隆的站点目录，省一次 clone
    python build_skill.py --skip-sync          # 只重算索引与 SKILL.md，不动 references 正文
    python build_skill.py --skill-root <目录>  # 指定 skill 根目录
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
import tempfile
from pathlib import Path

import gen_index
import sync_handycontrol_docs as sync

SCRIPT_DIR = Path(__file__).resolve().parent

TEMPLATE = SCRIPT_DIR / "SKILL.md.tpl"
RECIPES = SCRIPT_DIR / "recipes.md"

# SKILL.md 里的占位符 → gen_index 输出的段名
SKILL_MARKERS = {
    "INDEX_EXTEND": "EXTEND_COMPACT",
    "INDEX_NATIVE": "NATIVE",
    "INDEX_ATTACH": "ATTACH",
}

INDEX_HEADER = """# 控件总索引

`references/` 下一控件一文件，文件名取标签名的小驼峰形式（例外：`hc:Poptip`→`popTip.md`、
`hc:LoadingLine`/`hc:LoadingCircle`→`loading.md`、`hc:Row`/`hc:Col`→`grid.md`）。
分区索引页：`quick_start.md`、`basic_xaml.md`、`attach.md`、`native_controls.md`、`extend_controls.md`、`langs.md`；
另有数据类 `data/GrowlInfo.md`、`data/InfoType.md`（官网 tools 分区三页无正文，未收录）。

## 扩展控件（79）

`hc:` 前缀，均位于 `HandyControl.Controls`。

{extend}

## 原生控件样式键

原生控件默认走隐式样式；下表的键可用 `Style="{{StaticResource 键名}}"` 切换外观。

{native}

## 附加属性

形态 `hc:类名.属性名`。

{attach}
"""


def fill(text: str, sections: dict[str, str]) -> str:
    for marker, key in SKILL_MARKERS.items():
        if key not in sections:
            raise SystemExit(f"缺少索引段 {key}")
        text = text.replace(f"<!-- {marker} -->", sections[key])
    if "<!-- INDEX_" in text:
        raise SystemExit("仍有未替换的索引占位符")
    return text


def sync_references(skill_root: Path, site: Path | None) -> None:
    if site is not None:
        stats = sync.sync_docs(site, skill_root)
    else:
        tmp = Path(tempfile.mkdtemp(prefix="hc-doc-"))
        try:
            sync.clone_site(tmp)
            stats = sync.sync_docs(tmp, skill_root)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    for name, count in sorted(stats.items(), key=lambda kv: -kv[1]):
        print(f"  {name}: {count} 页")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skill-root", help="skill 根目录，默认取 scripts/ 的上级")
    parser.add_argument("--site", help="已克隆的 handyorg.github.io 目录")
    parser.add_argument("--skip-sync", action="store_true", help="跳过官网同步，只重算索引")
    args = parser.parse_args()

    skill_root = Path(args.skill_root).resolve() if args.skill_root else SCRIPT_DIR.parent
    refs = skill_root / "references"
    if not (skill_root / "SKILL.md").exists() and not args.skip_sync:
        print(f"目标不像 skill 目录: {skill_root}", file=sys.stderr)
        return 1

    if not args.skip_sync:
        print("同步官网文档…")
        # 先清空旧的正文，避免官网删页后本地残留过期文件
        for stale in refs.glob("**/*.md"):
            stale.unlink()
        sync_references(skill_root, Path(args.site).resolve() if args.site else None)

    shutil.copy2(RECIPES, refs / "recipes.md")
    # 清掉同步后残留的空目录（例如官网某个分区整块无正文）
    for empty in sorted(refs.rglob("*"), reverse=True):
        if empty.is_dir() and not any(empty.iterdir()):
            empty.rmdir()
    sections = gen_index.build_sections(refs)

    skill_md = fill(TEMPLATE.read_text(encoding="utf-8"), sections)
    (skill_root / "SKILL.md").write_text(skill_md, encoding="utf-8")
    (refs / "index.md").write_text(
        INDEX_HEADER.format(
            extend=sections["EXTEND_FULL"], native=sections["NATIVE"], attach=sections["ATTACH"]
        ),
        encoding="utf-8",
    )

    docs = list(refs.rglob("*.md"))
    lines = sum(len(p.read_text(encoding="utf-8").splitlines()) for p in docs)
    print(f"references: {len(docs)} 个文件 / {lines} 行")
    print(f"SKILL.md: {len(skill_md.splitlines())} 行 / {len(skill_md)} 字符")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
