"""重建后自检：确认文档结构完整、引用路径有效、索引无遗漏。

用法:
    python audit_skill.py            # 检查上层 skill 目录
    python audit_skill.py <skill 目录>
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

FENCE_RE = re.compile(r"^ {0,3}```")
HEADING_RE = re.compile(r"^(#{1,6}) ")
TABLE_SEP_RE = re.compile(r"^\|[\s:-]+\|")
ROW_PATH_RE = re.compile(r"(?:extend_controls|native_controls|attach|basic_xaml|data|tools)/[\w.-]+\.md")

# 允许不入索引的文件（分区首页、本 skill 自己的索引与配方）
NOT_INDEXED = {"index.md", "recipes.md", "quick_start.md", "basic_xaml.md", "attach.md",
               "native_controls.md", "extend_controls.md", "langs.md"}


def cells(line: str) -> int:
    """单元格分隔符计数，忽略转义的 \\|。"""
    return len(re.findall(r"(?<!\\)\|", line))


def check_docs(refs: Path) -> list[str]:
    problems: list[str] = []
    for path in sorted(refs.rglob("*.md")):
        rel = path.relative_to(refs).as_posix()
        text = path.read_text(encoding="utf-8")
        lines = text.splitlines()

        if not lines or not lines[0].startswith("# "):
            problems.append(f"{rel}: 缺一级标题")
        if rel not in ("index.md", "recipes.md") and "<!-- source:" not in text:
            problems.append(f"{rel}: 缺 source 注释")
        if len([l for l in lines if FENCE_RE.match(l)]) % 2:
            problems.append(f"{rel}: 代码块未闭合")

        for i, line in enumerate(lines):
            m = HEADING_RE.match(line)
            if not m or len(m.group(1)) < 2:
                continue
            nxt = next((x for x in lines[i + 1:] if x.strip()), "")
            m2 = HEADING_RE.match(nxt)
            if not nxt or (m2 and len(m2.group(1)) <= len(m.group(1))):
                problems.append(f"{rel}: 空章节 {line}")

        i = 0
        while i < len(lines):
            if lines[i].startswith("|") and i + 1 < len(lines) and TABLE_SEP_RE.match(lines[i + 1]):
                width = cells(lines[i])
                j = i
                while j < len(lines) and lines[j].startswith("|"):
                    if cells(lines[j]) != width:
                        problems.append(f"{rel}:{j + 1}: 表格列数不一致")
                    j += 1
                i = j
            else:
                i += 1

        if "HANDYCONTROLCODEBLOCK" in text:
            problems.append(f"{rel}: 残留代码占位符")
        if re.search(r"</?(?:div|span|p|table|td|tr|figure|pre)\b", text):
            problems.append(f"{rel}: 残留 HTML 标签")
    return problems


def check_links(skill: Path, refs: Path) -> list[str]:
    problems: list[str] = []
    docs = {p.relative_to(refs).as_posix() for p in refs.rglob("*.md")}
    for name in ("../SKILL.md", "index.md", "recipes.md"):
        file = (refs / name).resolve()
        text = file.read_text(encoding="utf-8")
        cited_all = set(re.findall(r"`([\w./-]+\.md)`", text)) | set(
            re.findall(r"references/[\w./-]+\.md", text)
        )
        for cited in cited_all:
            cited = cited.replace("references/", "")
            # 只校验带目录的路径引用；与自身同名的条目不校验
            if "/" not in cited or cited == file.name:
                continue
            if cited not in docs:
                problems.append(f"{file.name}: 引用不存在的 {cited}")
    return problems


def check_index_coverage(skill: Path, refs: Path) -> list[str]:
    index_text = (refs / "index.md").read_text(encoding="utf-8") + (skill / "SKILL.md").read_text(encoding="utf-8")
    listed = set(ROW_PATH_RE.findall(index_text))
    all_docs = {p.relative_to(refs).as_posix() for p in refs.rglob("*.md")}
    return [f"未进索引: {d}" for d in sorted(all_docs - listed - NOT_INDEXED)]


def check_counts(skill: Path, refs: Path) -> list[str]:
    """SKILL.md 里声明的篇数要与实际一致。"""
    problems: list[str] = []
    text = (skill / "SKILL.md").read_text(encoding="utf-8")
    m = re.search(r"转成 (\d+) 个 Markdown 文件", text)
    actual = len([p for p in refs.rglob("*.md") if p.name not in ("index.md", "recipes.md")])
    if m and int(m.group(1)) != actual:
        problems.append(f"SKILL.md 声明 {m.group(1)} 篇，实际 {actual} 篇")
    m = re.search(r"扩展控件（(\d+)）", (refs / "index.md").read_text(encoding="utf-8"))
    real_ctl = len(list((refs / "extend_controls").glob("*.md")))
    if m and int(m.group(1)) != real_ctl:
        problems.append(f"index.md 声明 {m.group(1)} 款扩展控件，实际 {real_ctl} 款")
    return problems


def main() -> int:
    skill = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
    refs = skill / "references"
    if not refs.is_dir():
        print(f"找不到 {refs}", file=sys.stderr)
        return 1

    problems = check_docs(refs) + check_links(skill, refs) + check_index_coverage(skill, refs) + check_counts(skill, refs)
    if problems:
        print(f"发现 {len(problems)} 处问题：")
        for p in problems:
            print("  -", p)
        return 1
    total = len(list(refs.rglob("*.md")))
    print(f"自检通过：{total} 个文件，结构与引用均正常")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
