"""HandyControl 官方文档（handyorg.github.io）-> Markdown 转换与 Skill references 生成。

用法:
    python sync_handycontrol_docs.py --site <已克隆的站点目录> --out <skill 目录>
    python sync_handycontrol_docs.py --out <skill 目录>          # 自动浅克隆站点到临时目录

站点为 Hexo + NexT 生成后的静态 HTML，正文位于 div.post-body，
代码块为 figure.highlight[lang]，行号在 td.gutter 中需剔除。
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

from bs4 import BeautifulSoup, NavigableString, Tag
from markdownify import markdownify as md

SITE_REPO = "https://github.com/HandyOrg/handyorg.github.io.git"
SITE_BASE = "https://handyorg.github.io"
SITE_ROOT = "handycontrol"

# 每个分区 -> 输出文件名模板 ("{section}" 表示逐页单独成文件)
SECTION_TITLES = {
    "quick_start": "快速开始",
    "basic_xaml": "基础 XAML 定义",
    "attach": "附加属性",
    "native_controls": "原生控件",
    "extend_controls": "扩展控件",
    "data": "数据类",
    "tools": "工具与扩展",
    "langs": "国际化",
    "tnx": "鸣谢",
}

# 占位符必须不含 markdown 特殊字符，否则会被转义后无法还原
CODE_TOKEN = "HANDYCONTROLCODEBLOCK{}END"

# 官网无正文的分区与占位内容
SKIP_SECTIONS = {"tnx"}
EMPTY_BODIES = {"建设中", ""}


@dataclass
class Page:
    section: str
    slug: str          # 空字符串表示分区首页
    url: str
    title: str
    body: str


CS_HINT = re.compile(r"(^|\s)(var|new |public |private |internal |using |return |await |string |int )|;\s*$|=>|\bConsole\.")


def sniff_lang(lang: str, code: str) -> str:
    """文档里有 code 块标错语言（例如 XAML 片段标成 c#/plain），按内容纠正。"""
    body = code.strip()
    # 以 < 开头的必然是 XAML 片段，官网有把 XAML 标成 cs 的页面
    if body.startswith("<"):
        return "xml"
    if lang in ("", "plain", "text"):
        if CS_HINT.search(body):
            return "csharp"
        return "text"
    return lang


def extract_code_blocks(soup: BeautifulSoup) -> list[tuple[str, str]]:
    """把 figure.highlight 换成占位符，返回 [(lang, code)]。"""
    blocks: list[tuple[str, str]] = []
    for fig in soup.select("figure.highlight"):
        classes = [c for c in (fig.get("class") or []) if c != "highlight"]
        lang = classes[0] if classes else ""
        lang = {"c#": "csharp", "cs": "csharp", "": "text"}.get(lang, lang)
        holder = fig.select_one("td.code") or fig.select_one("pre") or fig
        pre = holder.select_one("pre") or holder
        # 源码每行是 span.line + br，必须先把 br 转成换行再取文本，否则多行会被压成一行
        for br in pre.find_all("br"):
            br.replace_with(NavigableString("\n"))
        code = pre.get_text() if isinstance(pre, Tag) else str(pre)
        code = code.replace("\xa0", " ").rstrip("\n")
        token = CODE_TOKEN.format(len(blocks))
        blocks.append((sniff_lang(lang, code), code))
        fig.replace_with(NavigableString(f"\n{token}\n"))
    return blocks


def clean_body(soup: BeautifulSoup) -> None:
    """去掉锚点、脚本等对参考无意义的节点（图片保留，便于对照效果）。"""
    for sel in ("a.headerlink", "script", "style", "iframe", ".post-copyright"):
        for node in soup.select(sel):
            node.decompose()
    for br in soup.select("br"):
        br.replace_with(NavigableString("\n"))
    # 标题降一级，给页面标题留出 #
    for level in (4, 3, 2, 1):
        for h in soup.select(f"h{level}"):
            h.name = f"h{level + 1}"


def escape_table_pipes(soup: BeautifulSoup) -> None:
    """表格单元格内的裸 | 会把 markdown 表格拆错列，先转义。"""
    for cell in soup.select("th, td"):
        for node in cell.find_all(string=True):
            if "|" in node:
                node.replace_with(node.replace("|", "\\|"))


def html_to_markdown(soup: BeautifulSoup) -> str:
    blocks = extract_code_blocks(soup)
    clean_body(soup)
    escape_table_pipes(soup)
    text = md(str(soup), heading_style="ATX", bullets="-", strip=["span"])
    for idx, (lang, code) in enumerate(blocks):
        fence = "```" if "```" not in code else "````"
        text = text.replace(CODE_TOKEN.format(idx), f"{fence}{lang}\n{code}\n{fence}")
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def page_title(soup: BeautifulSoup) -> str:
    node = soup.select_one(".post-title") or soup.select_one("title")
    if node is None:
        return ""
    return node.get_text(strip=True)


def parse_page(path: Path, site_dir: Path) -> Page | None:
    rel = path.parent.relative_to(site_dir / SITE_ROOT)
    parts = [] if str(rel) == "." else list(rel.parts)
    section = parts[0] if parts else ""
    slug = parts[1] if len(parts) > 1 else ""
    if section in ("", "css", "js", "lib", "images"):
        return None

    soup = BeautifulSoup(path.read_text(encoding="utf-8", errors="ignore"), "html.parser")
    body = soup.select_one(".post-body")
    if body is None:
        return None
    title = page_title(soup)
    url = f"{SITE_BASE}/{SITE_ROOT}/" + (f"{section}/" if section else "") + (f"{slug}/" if slug else "")
    return Page(section=section, slug=slug, url=url, title=title, body=html_to_markdown(body))


def collect(site_dir: Path) -> list[Page]:
    pages = []
    for path in sorted((site_dir / SITE_ROOT).rglob("index.html")):
        page = parse_page(path, site_dir)
        if page:
            pages.append(page)
    return pages


def render(page: Page) -> str:
    title = page.title or page.slug or SECTION_TITLES.get(page.section, page.section)
    header = f"# {title}\n\n<!-- source: {page.url} -->\n\n"
    return header + page.body + "\n"


def write_outputs(pages: list[Page], out_dir: Path) -> dict[str, int]:
    stats: dict[str, int] = {}
    for page in pages:
        if page.section in SKIP_SECTIONS:
            continue
        # 官网有若干占位页（分区首页写"建设中"、tools 下三页只有标题），无正文则不输出
        if page.body.strip() in EMPTY_BODIES:
            continue
        section_title = SECTION_TITLES.get(page.section, page.section)
        if page.slug:
            rel = Path("references") / page.section / f"{page.slug}.md"
        else:
            rel = Path("references") / f"{page.section}.md"
        target = out_dir / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(render(page), encoding="utf-8")
        stats[section_title] = stats.get(section_title, 0) + 1
    return stats


def sync_docs(site_dir: Path, out_dir: Path) -> dict[str, int]:
    """把站点目录转为 references/，返回各分区页数。供 build_skill 复用。"""
    pages = collect(site_dir)
    if not pages:
        raise RuntimeError("未解析到任何页面")
    return write_outputs(pages, out_dir)


def clone_site(target: Path) -> None:
    subprocess.run(["git", "clone", "--depth", "1", SITE_REPO, str(target)], check=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", help="已克隆的 handyorg.github.io 目录")
    parser.add_argument("--out", required=True, help="skill 目录")
    args = parser.parse_args()

    site_dir = Path(args.site).resolve() if args.site else None
    tmp = None
    if site_dir is None:
        tmp = tempfile.mkdtemp(prefix="hc-doc-")
        clone_site(Path(tmp))
        site_dir = Path(tmp)

    try:
        stats = sync_docs(site_dir, Path(args.out).resolve())
        total = sum(stats.values())
        for name, count in sorted(stats.items(), key=lambda kv: -kv[1]):
            print(f"{name}: {count} 页")
        print(f"合计 {total} 页")
    except RuntimeError as exc:
        print(exc, file=sys.stderr)
        return 1
    finally:
        if tmp:
            shutil.rmtree(tmp, ignore_errors=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
