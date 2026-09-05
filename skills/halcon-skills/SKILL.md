---
name: halcon-skills
title: Halcon 通用 Skill 库
description: >-
  HALCON generic skill library — 11 domain skills covering image preprocessing,
  subpixel edge & contour, 2D matching, measuring/metrology, calibration,
  barcode/OCR identification, classification & deep learning, defect inspection,
  3D vision, visualization & system integration, and vision workflow design. Use
  this index to navigate to the right HALCON domain skill, then open that skill's
  SKILL.md and load its references. Select based on the task: reading images &
  ROI → halcon-image-preprocessing; subpixel measurement → halcon-edge-contour;
  locating an object → halcon-matching; measuring dimensions →
  halcon-measuring-metrology; camera/hand-eye calibration → halcon-calibration;
  reading codes/text → halcon-identification-ocr; classifying →
  halcon-classification-dl; defect detection → halcon-inspection-defect; 3D/6D
  pose → halcon-3d-vision; display/GPU/I-O/data types →
  halcon-visualization-system; method selection & multi-strategy orchestration →
  halcon-vision-workflow.
---

# HALCON 通用 Skill 库

> 本库**完全自包含**：所有需要的参考内容已收进 `halcon-skills/` 内部（各 skill 的 `references/` + 共享的 `_authoring/`），**不依赖任何外部文件夹**。
> 书写规范/配色/编码规则见 `_authoring/conventions.md`（精简总结）+ `halcon_skill.md`（完整元 skill）；脚本格式/CLI 参考见 `_authoring/` 中各 `*_reference.md`；原元 skill 项目的 README 见 `_authoring/halcon_skill_README.md`；各领域知识在 skill 正文；逐算子签名在各自 `references/`；真实用例按主题归档在各 skill 的 `references/example_*.md`；原 example 库的索引见 `halcon-vision-workflow/references/example_INDEX.md`。

## 领域 skill 索引

| skill | 一句话 | 适用任务 |
|---|---|---|
| `halcon-image-preprocessing` | 采集/读图/通道/域/类型/滤波/颜色/分割/形态学 | 任何视觉流水线前端 |
| `halcon-edge-contour` | 亚像素边缘/线、XLD、分割合并、拟合 | 亚像素测量、自由形状边缘 |
| `halcon-matching` | 2D 匹配全谱（NCC/Shape/Deformable/Descriptor） | 定位、机器人引导、多实例 |
| `halcon-measuring-metrology` | 1D 卡尺、2D 计量、几何运算、世界坐标 | 尺寸/角度/位姿测量 |
| `halcon-calibration` | 单相机/双目/手眼标定、像素↔世界、畸变 | 标定、手眼、世界坐标 |
| `halcon-identification-ocr` | 条码、2D 码、OCR、Deep OCR、打印质量 | 读码/读字/验证 |
| `halcon-classification-dl` | MLP/SVM/GMM/kNN、图像分类、LUT、DL/CNN | 分类、新颖检测、深度学习 |
| `halcon-inspection-defect` | Variation Model、纹理、FFT、缺陷检测 | 缺陷/划痕/缺件/表面检 |
| `halcon-3d-vision` | 3D 模型、3D 匹配、位姿、立体、结构光、DFF | 点云、6D 位姿、重建 |
| `halcon-visualization-system` | 可视化、GPU、I/O、tuple/matrix/object/file | 显示、加速、集成、数据结构 |
| `halcon-vision-workflow` | 方法选型、流水线骨架、多策略编排+置信度 | 从需求到可靠流程 |

## 目录结构

```
halcon-skills/
├── SKILL.md                  # 本索引
├── _authoring/
│   └── conventions.md        # 书写规范 / 配色 / 编码规则（共享）
├── <skill>/
│   ├── SKILL.md              # 该领域知识（英文 name/description + 中文正文）
│   └── references/
│       ├── ops_*.md          # 中文算子总览
│       ├── <算子分类>.txt     # 官方算子参考章节（reference_hdevelop.pdf 抽取）
│       ├── example_*.md      # 真实工业用例（按主题归档）
│       └── ref_OPERATOR_REFERENCE.md  # 本地逐算子描述索引
└── halcon-vision-workflow/references/  # 另含编排示例 .md
```

## 使用方式

1. 确定任务领域 → 打开对应 skill 的 `SKILL.md`（英文 name/description 触发 + 中文正文）。
2. 正文给出：选型、核心 workflow、关键参数默认值、典型流水线、踩坑。
3. 需要某算子精确签名/默认值/取值范围 → 读该 skill `references/ref_OPERATOR_REFERENCE.md` 指向的本地 `<算子分类>.txt`（官方 `reference_hdevelop.pdf` 逐算子描述）。
4. 中文算子总览在该 skill `references/ops_*.md`。

## 与外部的关系

本库已**完全自包含**；安装/使用时只拷贝 `halcon-skills/` 即可。
唯一运行时外部依赖：用户机器上的 HALCON 安装（`HALCONROOT`/`HALCONEXAMPLES` 环境变量），用于 `hrun`/`hscriptengine` 执行以及参考 `procedures/general/` 内置过程。

> 内容依据 HALCON 26.05 官方文档整理；各 skill 正文按官方方法体系与逐算子参数收敛。