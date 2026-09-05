# HALCON Skills

**11 个领域 skill 的自包含 HALCON 知识库，用于在 Agent（Claude Code / OpenAI Codex / Cursor 等）中生成、审、重构、运行 HDevelop（`.hdev`）与 HDevelopEVO（`.hscript`）程序。**

> 完全自包含 —— 所有需要的参考内容已收进本目录内，**无任何外部依赖**（除用户机器上 HALCON 自身的运行时/CLI `hrun`/`hscriptengine`，以及环境变量 `HALCONROOT`/`HALCONEXAMPLES` 指到 HALCON 安装目录）。
> 内容依据 HALCON 26.05 官方文档整理：8 个 solution guide（"Guide to HALCON Methods" 全 23 章）、`reference_hdevelop.pdf` 30 个算子分类章、`hdevelop_users_guide`、相关 HALCON 项目材料。

---

## 目录结构

```
halcon-skills/
├── README.md                     ← 本文件
├── SKILL.md                      ← 库索引/入口（含 name + description 触发）
├── _authoring/                   ← 共享书写规范（任何 skill 触发时必读）
│   ├── conventions.md                 精简总结（目标格式/流程/配色/编码规则）
│   ├── halcon_skill.md                完整元 skill（212 行）
│   ├── halcon_skill_README.md         原 halcon-skill README
│   ├── hdev_format_reference.md       .hdev XML schema / <docu> 三语
│   ├── hscript_format_reference.md    .hscript 语法
│   ├── hrun_reference.md              hrun CLI
│   └── hscriptengine_reference.md     hscriptengine CLI
└── <11 skills>/
    ├── SKILL.md                  ← 领域正文（英文 name/description + 中文内容）
    └── references/               ← 中文算子总览 / 官方逐算子 / 真实用例
```

## 11 个领域 skill

| skill | 一句话 |
|---|---|
| `halcon-image-preprocessing` | 采集/读图/通道/域/类型/滤波/颜色/分割/形态学（流水线前端）|
| `halcon-edge-contour` | 亚像素边缘/线、XLD、分割合并、圆线椭圆矩形拟合 |
| `halcon-matching` | 2D 匹配全谱（NCC/Shape/Scaled/Aniso/Local/Planar/Descriptor）|
| `halcon-measuring-metrology` | 1D 卡尺、2D 计量模型、几何运算、世界坐标 |
| `halcon-calibration` | 单相机/双目/手眼标定、像素↔世界、畸变校正 |
| `halcon-identification-ocr` | 条码、2D 码、OCR、Deep OCR、打印质量 |
| `halcon-classification-dl` | MLP/SVM/GMM/kNN、图像分类、LUT、DL/CNN |
| `halcon-inspection-defect` | Variation Model、纹理、FFT、缺陷检测 |
| `halcon-3d-vision` | 3D 模型、3D 匹配、位姿、立体、结构光、DFF |
| `halcon-visualization-system` | 可视化、GPU、I/O、tuple/matrix/object/file |
| `halcon-vision-workflow` | 方法选型、流水线骨架、多策略编排 + 置信度 |

## 安装与使用

### A) 用 `npx skills`（推荐 —— 装到所有支持的 agent）

```bash
npx skills add ./halcon-skills
```

或从 git 仓库（把目录 push 后）：

```bash
npx skills add <your-git-url>
```

### B) 手动安装（Claude Code）

把整个 `halcon-skills/` 目录拷到 `.claude/skills/`：

```bash
cp -r halcon-skills ~/.claude/skills/
# 或针对单个 skill 拷贝（仅 11 个 skill 之一）
cp -r halcon-skills/halcon-matching ~/.claude/skills/
```

### C) 手动安装（Cursor / OpenAI Codex 等）

按各自 agent 的 skills 目录约定放置（参考各 agent 文档）。

### 触发方式

任何时候用户提出 HALCON 任务，agent 的 `available_skills` 列表会带上 `halcon-*` 11 个 skill，按 SKILL.md 中的 `name` + `description` 自动匹配触发。描述按"做什么/何时用"双重组织，确保该用就用（强触发）。

## 用户写作 HALCON 脚本时的前置要求

| 项 | 说明 |
|---|---|
| `HALCONROOT` 环境变量 | HALCON 安装根目录（`bin/`、`procedures/general/`、`doc/`、`images/`、`calib/`、`ocr/`、`dl/` 等）|
| `HALCONEXAMPLES` 环境变量 | HALCON 示例目录（`hdevelop/`、`hdevelopevo/`、`solution_guide/`、`images/` 等）|
| `hrun` CLI | 在 `HALCONROOT/bin/`，用于 headless `.hdev` 执行 |
| `hscriptengine` CLI | 在 `HALCONROOT/bin/`，用于 headless `.hscript` 执行 |

## 库内导航

| 你想知道 | 看这里 |
|---|---|
| 写 `.hdev` 的完整规范、配色、`<docu>` 三语 | `_authoring/halcon_skill.md`（完整）/ `_authoring/conventions.md`（精简）|
| `.hdev` XML schema、`<procedure>` / `<interface>` / `<docu>` 字段 | `_authoring/hdev_format_reference.md` |
| `.hscript` 语法 / `proc`/`endproc`/`from import` | `_authoring/hscript_format_reference.md` |
| `hrun` CLI 用法（headless、参数覆盖）| `_authoring/hrun_reference.md` |
| `hscriptengine` CLI 用法 | `_authoring/hscriptengine_reference.md` |
| 选方法 → 选 skill | `halcon-vision-workflow/SKILL.md`（16 应用场景 → 方法）|
| 看真实代码示例 | 各 skill 的 `references/example_*.md` |
| 某个算子的精确签名/默认值 | 各 skill 的 `references/<NN>_<算子分类>.txt`（30 个算子分类全覆盖）|
| 整个库的所有 skill + 用例索引 | `SKILL.md` |

## 致谢 / Acknowledgements

本库整合自以下三方面工作：

- **HALCON 官方文档**（MVTec） —— Solution Guide I（"Guide to HALCON Methods" 全 23 章）、Solution Guide II-A/B/C/D、Solution Guide III-A/B/C、`reference_hdevelop.pdf` 30 个算子分类章、`hdevelop_users_guide` 等，是本库方法论与算子级知识的主要权威依据。
- [bertram-eu/halcon-skill](https://github.com/bertram-eu/halcon-skill) —— HDevelop / HDevelopEVO 脚本编写规范与格式参考
- [Nenezerrp/halcon-skill](https://github.com/Nenezerrp/halcon-skill) —— 编排模式与多策略示例

并融合相关中文算子总览与真实工业用例库，构建为统一的 self-contained Agent Skill 集合。

## 协议

无外部 LICENSE 文本随库附带；按原内容源（MVTec HALCON 文档及上游项目材料）的合理使用约定。

## 反馈 / 改进

每个 skill 的内容都基于 HALCON 官方文档提炼。如发现某 skill 信息过时/算子参数错误/案例方法过时，请直接编辑对应 `SKILL.md` 或 `references/` 中的文件 —— 库内所有内容都是普通 Markdown，可直接修改。