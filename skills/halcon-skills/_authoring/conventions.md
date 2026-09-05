# HALCON 脚本编写规范（Authoring Conventions）

> 本文件由顶层 `halcon-skill` 的作者规则整理而来，作为 `halcon-skills` 库内各 skill 的**共同编写规范**。
> 任何生成 HDevelop (`.hdev`) / HDevelopEVO (`.hscript`) 代码时遵循下列规则。

---

## 一、目标格式
- **HDevelop** (`.hdev`) — XML，用 `hrun` 运行。
- **HDevelopEVO** (`.hscript`) — 纯文本，用 `hscriptengine` 运行。
- 两者共用同一批算子、数据模型与控制流；差异在文件格式、过程语法与导入机制。
- 默认 `.hdev`，除非用户提到 HDevelopEVO / HScript / `.hscript` / `hscriptengine`。

## 二、作用范围
- 只生成/编辑 HALCON 脚本：`.hdev`（脚本）、`.hdvp`（单过程）、`.hdpl`（过程库）；`.hscript`（脚本/过程/库共用后缀）。
- 倾向确定性、可测试、参数显式、明确的 pass/fail 输出。

## 三、测试约定
- 若有 `images/` 文件夹则用于测试/实现，可能按 `/ok` `/nok`、`/io` `/nio`、`/training` `/test` `/validation` 分类，或用 `json`/`yaml` 标注；合理使用其内容。
- 输出图默认写入 `result/` 文件夹，每个图的 `hrun`/`hscriptengine` 输出也留同名文本。

## 四、作者流程
1. 把需求转成显式阶段流水线：**采集 → ROI/域限制 → 预处理 → 核心检测/测量/匹配 → 判定与报告**。
2. 从算子参考选算子，保证参数"按构造即合法"。
3. **比较至少三种不同实现**，权衡后选最终方案；不确定时问用户偏好。
4. 可调参数一律作为过程参数，带合理默认值与范围；`main()` 顶部集中一个参数块。
5. 重复逻辑封装为局部/外部过程。
6. 用 `dev_*` 做可视化与调试；多种可视化用多个窗口；优先 `dev_set_part()` 而非裁剪。只在 `main()` 里写注解图。遵循下方配色。
7. 运行时可能失败处加 `try/catch` 或返回码处理。
8. 仅对独立任务与隔离输出加并行（`par_start`/`par_join`）。
9. 输出语义显式（`ok`/`nok`、分数、测量值、原因）。
10. `main()` 当作**单元测试**；所有参数/输入图用全局变量，便于 `hrun -D` / `hscriptengine --input` 覆盖。
11. 生产核心逻辑放在独立过程，至少一个 `Image` 图标输入 + 布尔 `JobPass` 输出。
12. 无相机/外部通信/文件 I/O 访问，除非用户明确要求。
13. 可 headless 运行（`hrun`/`hscriptengine`）：无 `stop()`、无 `dev_open_dialog`、无交互算子；可视化用 `try/catch` 包裹使其无显示时优雅降级。

---

## 五、可视化配色方案
用以下 HALCON 颜色码（十六进制），**不要**用 `'green'`/`'red'`/`'blue'` 命名色。在可视化过程顶部只声明该过程用到的颜色，变量按含意命名（`ColorGoodDetection`、`ColorFailure`、`ColorCalculatedValue`、`ColorWarningLow`、`ColorWarningHigh`、`ColorDismissedFeature`），勿用 `Green`/`Color1`。

| 含意 | 源色 | RGB | HALCON 码 |
|---|---|---:|---|
| 合格/接受，`JobPass=true` | OK/绿 | 133,164,7 | `#85A407` |
| 错误/失败/拒绝，`JobPass=false` | Alarm/红 | 202,51,51 | `#CA3333` |
| 计算/测量值 | Accent/蓝 | 0,95,135 | `#005F87` |
| 低警告/特注意 | WarningLow/黄 | 234,206,33 | `#EACE21` |
| 高警告/特注意 | WarningHigh/橙 | 231,121,16 | `#E77910` |
| 被忽略/排除特征 | 黄或橙按严重度 | 234,206,33 或 231,121,16 | `#EACE21` / `#E77910` |

中性色（背景/面板/非活动元素）：`Light #DADCE0`、`DarkGrey #273338`、`Grey #404D53`、`LightGrey #C4C7CC`、`White #F9F7F8`。

半透明用 RGBA（alpha 128 → `80`）：`#CA333380`(透明失败)、`#85A40780`(透明合格)、`#005F8780`(透明计算值)、`#F9F7F880`(透明白)、`#EACE2180`、`#E7791080`。精确匹配 Qt `AlarmTranslucent` 用 `#CA33337F`。

```hdevelop
ColorGoodDetection := '#85A407'
ColorFailure := '#CA3333'
ColorCalculatedValue := '#005F87'
ColorDismissedFeature := '#E7791080'
dev_set_color (ColorGoodDetection); dev_display (AcceptedDetections)
dev_set_color (ColorFailure); dev_display (FailedDetections)
```
- 用显式窗口句柄渲染时改用 `set_color(WindowHandle, Color)`。

## 六、编码规则
- 地道的 HDevelop 语法（`:=`、元组、矢量、字典、`if/for/while/switch`）。
- 过程名、参数名、变量名任务相关且稳定；避免隐藏全局状态。
- 处理多图时**复用昂贵句柄/模型**（measure、metrology、matching、data code）。
- 度量输出用标定变换，而非像素近似。
- **绝不使用 `stop()`**（headless 时会挂死）；出错用 `return ()` 退过程或 `throw` 抛错。
- **Region 裁剪**：默认 `set_system('clip_region','true')` 时，未 `read_image` 前 `gen_rectangle1` 会**静默**产生空 region；先 `read_image` 或 `set_system('clip_region','false')`。
- **文档每个过程与参数**：
  - `.hdev`：每个 `<procedure>`（含 `main`）须有 `<docu>`（`<abstract>`/`<short>`/`<parameters>`/`<example>`，酌情 `<attention>`/`<warning>`/`<references>`/`<complexity>`）；每个文本元素提供**三份**：无 `lang`（回退）、`lang="en_US"`、`lang="de_DE"`（用户 locale 已知则再加一份）。参数设 `<sem_type>`/`<multivalue>`/`<type_list>`/`<default_type>`/`<mixed_type>`；输入控制参数加 `<default_value>`/`<values>`/`<value_min>`/`<value_max>`；图标参数只用精确语义类型。
  - `.hscript`：用 `//` 注释描述每个过程与参数（方向、图标/控制类型、语义、单/元组、混合类型、用途、范围、单位、默认值），英德两语。
- 解释所有代码。

## 七、输出契约
- 提供完整可执行片段，非伪代码。
- 说明关键假定（图像类型、标定可用性、对象极性、光照稳定）。
- 点出关键算子及为何选它；暴露可能需要调参的参数范围。
- `.hscript`：`from ... import *`、`proc`/`endproc`、`//`/`*` 注释。

## 八、环境约定
- `HALCONROOT`：HALCON 安装根（`bin/`、`procedures/general/`、`doc/`、`images/`、`calib/`、`ocr/`、`dl/`、`lut/`）。
- `HALCONEXAMPLES`：示例目录（`hdevelop/`、`hdevelopevo/`、`solution_guide/`、`images/`、各语言集成）。
- 算子级细节可用 `HALCONROOT/doc/html/reference/operators/` 与 `doc/pdf/`。

## 九、输出风格
- 一个主过程 + 小助手；参数块集中顶部；可视化可选且运行时非阻塞；判定逻辑显式可审计。
- `.hscript`：`public proc` 供导入，`proc` 为文件内助手；`.hdev`：过程为 XML `<procedure>` + 类型化 `<interface>`。
