---
name: halcon-vision-workflow
description: >-
  HALCON vision workflow design: selecting the right method for a use case (map
  the 16 application areas — position/object recognition 2D/3D, measuring &
  comparison 2D/3D, completeness check, identification, print/surface/texture
  inspection, robot vision, quality inspection, security — to the underlying
  HALCON methods), composing a full pipeline (acquisition → ROI → preprocessing →
  detection → decision), and managing multi-strategy orchestration with
  per-strategy scoring, self-reflection, early-exit and final confidence scoring
  (as in the center-localization and stray-light orchestrators). Use this skill
  whenever a HALCON/HDevelop task needs to decide WHICH technique to apply, how
  to sequence several methods robustly, or how to combine multiple detection
  strategies with a confidence/reflection layer to pick the best result. Trigger
  on "which HALCON method should I use for X", building an end-to-end inspection
  flow, orchestrating several localization/defect strategies, or when a single
  method is unstable and a multi-strategy fallback with confidence scoring is
  needed.
---

# HALCON 视觉流程编排与选型

> 定位：**先选对方法 / 再排对顺序 / 再组合多种策略自动择优**——这是"从需求到可靠工程"的黏合层。
> 各方法细节见对应领域 skill；本 skill 讲"怎么选、怎么串、怎么让流程稳"。
> 编写规范见 `../_authoring/`（conventions.md 为精简总结；完整规范在 halcon_skill.md；脚本格式/CLI 见同名 *_reference.md）。

---

## 一、16 个应用场景 → 方法（选型地图）

| 应用场景 | 常用方法 |
|---|---|
| **Color Inspection** | Color Processing（`trans_from_rgb`+阈值） |
| **Completeness Check** | 物体/位姿识别 2D/3D；Variation Model |
| **Identification** | 符号/字符：Bar Code、2D Code、OCR；一般物体：物体/位姿识别 2D/3D |
| **Measuring & Comparison 2D** | Blob、Contour（+亚像素边缘）、Matching、1D Measuring |
| **Measuring & Comparison 3D** | 2D 方法+标定；位姿估计；3D 重建（Stereo/光切/DFF/Photometric） |
| **Object Recognition 2D** | Blob、Contour、Matching、Classification、Color、Texture、运动检测 |
| **Object Recognition 3D** | 3D Matching（CAD）；平面任意朝向：perspective/descriptor 匹配 |
| **Position Recognition 2D** | Blob、Contour、Matching、1D Measuring |
| **Position Recognition 3D** | 2D+标定；位姿估计；Stereo；3D Matching |
| **Print Inspection** | OCV、2D Code 打印质量、Variation Model |
| **Quality Inspection** | Surface/Texture inspection、Completeness、Measuring 2D/3D、Classification |
| **Robot Vision** | 物体/位姿识别 2D/3D + hand-eye 标定 |
| **Security System** | Blob（dyn_threshold 运动）、背景估计、Optical flow、Kalman、Classification |
| **Surface Inspection** | 对参考图：Variation Model；对参考纹理/颜色：Texture/Color/Classification；均匀表面缺陷：Blob/Contour；多图：拼接 |
| **Texture Inspection** | FFT、Classification、Texture Analysis |
| **Text Processing** | tuple 字符串、OCR/OCV 分类器、正则 |

**选型口诀**：
- **找东西** → 先问是否 3D（是→3D 匹配；否→2D 匹配）+ 是否透视（是→perspective/descriptor；否→shape/NCC）→ 需亚像素/角度用 shape；纯纹理/模糊用 NCC；局部变形用 local-deformable。
- **量尺寸** → 找 blob/轮廓/计量；边缘清晰→亚像素轮廓拟合；参数近似已知+简单形状→2D 计量；沿一条线→1D 卡尺。
- **看缺陷** → 有参考图→Variation Model；纹理异常→Texture/FFT；局部亮暗→Blob/Edge。
- **读数/识别** → 条码/二维码/OCR；按码型选。

---

## 二、完整流水线的通用骨架

```
① 采集/读图   （halcon-image-preprocessing: grab_image / read_image）
② ROI/域限制  （reduce_domain → 提速、聚焦）
③ 预处理      （滤波/增强/类型转换/颜色 → 让目标更清晰）
④ 核心检测/测量/匹配（选对应领域 skill）
⑤ 判定与输出  （ok/nok、分数、测量值、原因）
⑥ 可视化/存档 （配色见 `../_authoring/conventions.md`；write_image / dump_window）
```
- **对齐优先**：对象位置/姿态不稳时，先用 shape-based matching 对齐，再把后续交测/识别，稳定且快。
- **可观测性**：核心处理封装为带 `Image` 输入 + 布尔 `JobPass` 输出的独立 procedure；`main()` 当单元测试，所有参数/输入图用全局变量便于 `hrun -D`/`hscriptengine --input` 覆盖。
- **稳健性**：`try/catch` 包可视化；`set_check('~give_error')` 提速；`set_system('init_new_image','false')`。

---

## 三、多策略编排（自反思 + 置信度）

当单个方法在复杂场景下不稳时，采用**多策略并行 + 各自打分 + 自反思 + 全局择优**的编排模式（参考项目 `center_localization` 与 `stray_light` 编排器）。

### 设计原则
1. **编排器不含算子细节**：每步策略是独立 skill，只负责"逻辑与调度"，按需加载。
2. **每步自带反思**：策略内部做"打分 + 自反思"，自我判断结果是否可信（PASS / WARN / FAIL）。
3. **提前退出**：某策略反思通过且高置信度，可直接输出，不必执行后续策略（省时）。但要有**兜底/交叉验证**策略始终执行。
4. **全局反思 + 置信度评分**：收集所有策略结果 → 交叉校验 → 选最优 → 输出置信度等级（如 HIGH / MEDIUM / LOW）。

### 编排骨架（伪码）
```
前置(必须): 预处理/阈值预检  →  输出 有效模式、前置是否失败
策略A/B/C: (依赖前置阈值) 探测→打分→自反思  →  可信则记为候选
策略X(始终): 兜底/交叉验证（不依赖前置，作为补救/交叉验证）
统一返回: 全局反思(所有结果交叉校验→选最优→置信度评分)
```
- **数据传递**：每步输出显式化（结构体/字典），如 `Valid(bool)`、`Row/Col`、`SelfCheck(PASS/WARN/FAIL)`、`Confidence`；`SpecularDetected` 这类特殊信号触发专门的过滤/分支。
- **结果汇聚**：所有策略的候选列表 + 各自置信度 → 全局评分器选取（几何一致性校验、重叠度、置信度加权）。
- **示例输入**：图像路径 + ROI 坐标；**输出**：最终位姿/中心 + 置信度等级。

### 为什么这样设计
- 复杂场景（镜面反光、光照变化、目标多样）下，单一策略的"过拟合"会失效；多策略+置信度能**在一个流程里覆盖更多变化**，并在策略间相互验证，输出可信度。
- 每个策略独立、可读、可测试，便于迭代；失败策略被标记为低置信度而非硬失败，避免整个流程宕掉。

---

## 四、方法组合的常见"坑"
1. **贪多求全**：默认参数能读多数码/能匹配多数目标，先试默认；明确失败的根因多在图质而非参数。
2. **不打桩**：任何测量/匹配前先可视化 ROI/阈值结果，确认无误再传算法。
3. **忽略对齐**：对象移动时若不对齐就测，误差全部来自位移而非算法。
4. **单一策略硬扛**：局部缺陷用 Blob 失败时，往往需要跨领域组合（Blob + FFT + 纹理 + 差异模型）交叉验证。
5. **缺少置信度**：只输出 0/1 而不输出置信度，无法在边界场景做分级处理。

---

## 五、引用
- 参考文档：本 skill 正文已含"16 应用场景→方法"选型表；各方法细节见对应领域 skill。
- 编排示例（已内置本 skill references/）：`center_localization_orchestrator.md`、`stray_light_orchestrator.md`（多策略+自反思+置信度的参考实现），以及 `example_INDEX.md`（原 example 库的完整 40 项 skill 索引）。
- 该 skill 为**跨领域黏合层**，无独立算子分类；具体算子见各领域 skill。


---

## 用例参考（example_*.md）

本 skill 目录下 `references/` 含以下项目里抽出的真实用例（按主题归档，可直接借鉴实现思路/算子组合）：

- `references/example_application_cases.md`
- `references/example_center_localization_coarse_analysis.md`
- `references/example_center_localization_reflection.md`
- `references/example_step0_image_preprocess.md`
- `references/example_step1_circle_strategy.md`
- `references/example_step2_rectangle_strategy.md`
- `references/example_step3_centroid_strategy.md`
- `references/example_step3b_specular_filter.md`
- `references/example_step4_edge_strategy.md`
- `references/example_step5_global_reflection.md`
- `references/example_stray_light_step0_preprocess.md`
- `references/example_stray_light_step1_spot_detection.md`
- `references/example_stray_light_step2_stray_classify.md`
- `references/example_stray_light_step3_fft_analysis.md`
- `references/example_stray_light_step4_judgment.md`
