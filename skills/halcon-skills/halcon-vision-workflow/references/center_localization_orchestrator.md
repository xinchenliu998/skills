# Skill: 中心定位编排流程 (Center Localization Orchestrator)

## 概述
本文件是中心定位任务的**编排控制器**，定义了各step skill之间的流转逻辑。每个step是独立的skill文件，编排器只负责：
1. 决定执行哪个step
2. 根据step输出决定下一步走向
3. 汇总最终结果

## 设计原则
- **编排器不包含算子细节**：所有Halcon算子逻辑在各step skill中
- **每个step自带反思**：每个策略step内含"打分+反思"，判断自身结果是否可信
- **按需加载**：只读取当前需要执行的step skill，避免一次性加载全部skill消耗token
- **提前退出**：某个策略step的反思通过后，可直接输出结果，不必执行后续策略

## 完整编排流程

```
用户请求(图片路径 + ROI坐标)
  │
  ▼
╔═══════════════════════════════════════════════════════╗
║  Step 0: 图像预处理                                    ║
║  读取: skill/step0_image_preprocess.md                 ║
║  职责: ReadImage → ROI限定 → 阈值分割预检              ║
║  输出: ImageROI, ROI信息, 有效阈值模式列表              ║
║        ThresholdFailed标志                              ║
╚═══════════════════════════════════════════════════════╝
  │
  ├─ IF ThresholdFailed == true ──────────────────────┐
  │                                                     │
  ▼                                                     │
╔═══════════════════════════════════════════════════════╗ │
║  Step 1: 圆策略 (策略A)                               ║ │
║  读取: skill/step1_circle_strategy.md                 ║ │
║  职责: 圆特征探测 → 同心性判断 → 打分 → 自反思         ║ │
║  输出: 策略A结果 + 可信度判定                          ║ │
╚═══════════════════════════════════════════════════════╝ │
  │                                                     │
  ├─ IF 策略A可信(自反思通过) ─→ 记录A为候选，继续      │
  │                                                     │
  ▼                                                     │
╔═══════════════════════════════════════════════════════╗ │
║  Step 2: 平行线/矩形策略 (策略B)                      ║ │
║  读取: skill/step2_rectangle_strategy.md              ║ │
║  职责: 平行线探测 → 矩形拟合 → 打分 → 自反思          ║ │
║  输出: 策略B结果 + 可信度判定                          ║ │
╚═══════════════════════════════════════════════════════╝ │
  │                                                     │
  ├─ IF 策略B可信(自反思通过) ─→ 记录B为候选，继续      │
  │                                                     │
  ▼                                                     │
╔═══════════════════════════════════════════════════════╗ │
║  Step 3: 区域重心策略 (策略C) — 兜底                   ║ │
║  读取: skill/step3_centroid_strategy.md               ║ │
║  职责: 阈值分割 → 最大连通域 → 重心 → 打分 → 自反思   ║ │
║  输出: 策略C结果 + 可信度判定                          ║ │
╚═══════════════════════════════════════════════════════╝ │
  │                                                     │
  ◄─────────────────────────────────────────────────────┘
  │  (ThresholdFailed时，Step1/2/3跳过或标记N/A，直接到Step3b)
  ▼
╔═══════════════════════════════════════════════════════╗
║  Step 3b: 镜面反光过滤 — 始终执行                      ║
║  读取: skill/step3b_specular_filter.md                ║
║  职责: 检测高亮光斑 → 验证确认 → 膨胀掩膜             ║
║        → 生成CleanImageROI → 自反思                   ║
║  输出: SpecularDetected, CleanImageROI, 光斑信息       ║
║  注意: 无光斑时CleanImageROI=ImageROI，不影响后续      ║
╚═══════════════════════════════════════════════════════╝
  │
  ▼
╔═══════════════════════════════════════════════════════╗
║  Step 4: Edge直接边缘策略 (策略Edge) — 始终执行        ║
║  读取: skill/step4_edge_strategy.md                   ║
║  职责: Emphasize增强 → 直接边缘检测 → 矩形拟合        ║
║        → 打分 → 自反思                                ║
║  输出: 策略Edge结果 + 可信度判定                       ║
╚═══════════════════════════════════════════════════════╝
  │
  ▼
╔═══════════════════════════════════════════════════════╗
║  Step 5: 全局反思 + 置信度评分                         ║
║  读取: skill/step5_global_reflection.md               ║
║  职责: 收集所有策略结果 → 交叉校验 → 选择最优          ║
║        → 计算置信度 → 输出最终结果                     ║
║  输出: 最终中心坐标 + 置信度等级(HIGH/MEDIUM/LOW)      ║
╚═══════════════════════════════════════════════════════╝
  │
  ▼
╔═══════════════════════════════════════════════════════╗
║  Step 6: 生成独立cs文件                                ║
║  命名: {YYYYMMDD}_{图片名}.cs                         ║
║  内容: 包含执行过的策略代码 + 反思逻辑                  ║
╚═══════════════════════════════════════════════════════╝
```

## 编排规则

### 规则1: Step按序执行，但可提前标记跳过
- Step 0 **必须执行**（图像预处理是所有策略的前置）
- Step 1/2/3 依赖阈值分割：若 `ThresholdFailed=true`，标记为 N/A 但仍需走流程（策略C会尝试执行并标记低可信度）
- Step 3b **始终执行**（镜面反光检测，无光斑时直接PASS不影响后续）
- Step 4 **始终执行**（不依赖阈值，作为交叉验证/补救；优先使用Step 3b的CleanImageROI）
- Step 5 **必须执行**（全局反思，含光斑场景的特殊规则）

### 规则2: 按需读取skill文件
每到一个step时，**只读取该step对应的skill文件**，不要提前读取后续step：
```
到Step 0时 → 读取 skill/step0_image_preprocess.md
到Step 1时 → 读取 skill/step1_circle_strategy.md
到Step 2时 → 读取 skill/step2_rectangle_strategy.md
到Step 3时 → 读取 skill/step3_centroid_strategy.md
到Step 3b时 → 读取 skill/step3b_specular_filter.md
到Step 4时 → 读取 skill/step4_edge_strategy.md
到Step 5时 → 读取 skill/step5_global_reflection.md
```

### 规则3: Step之间的数据传递
每个step的输出通过控制台打印传递给下一个step：
```
Step 0 输出 → 供 Step 1/2/3/4 使用:
  - ImageROI对象（通过代码内传递）
  - ROI信息: Row1, Col1, Row2, Col2, CenterRow, CenterCol, Area, Diagonal
  - 有效阈值模式: validModes[] ('dark'/'light'/空)
  - ThresholdFailed: bool
  - 各模式前景占比: darkRatio, lightRatio

Step 1 输出 → 供 Step 5 使用:
  - 策略A: Valid(bool), Row, Col, Radii[], CircleCount, 同心性(bool), SelfCheck(PASS/WARN/FAIL)

Step 2 输出 → 供 Step 5 使用:
  - 策略B: Valid(bool), Row, Col, HasParallelLines(bool), ParallelPairs, SelfCheck(PASS/WARN/FAIL)

Step 3 输出 → 供 Step 3b/5 使用:
  - 策略C: Row, Col, Area, AreaRatio, UsedMode, SelfCheck(PASS/WARN/FAIL)

Step 3b 输出 → 供 Step 4/5 使用:
  - SpecularDetected(bool), SpecularCount(int), SpecularAreaRatio(double)
  - CleanImageROI(HObject): 去除光斑后的ROI图像（无光斑时=ImageROI）
  - SpecularRegion(HObject): 光斑掩膜区域
  - SpecularSelfCheck(PASS/WARN/FAIL)

Step 4 输出 → 供 Step 5 使用:
  - 策略Edge: Valid(bool), Row, Col, Method(1/2), Coverage, SelfCheck(PASS/WARN/FAIL)
  - 使用的输入图像: CleanImageROI或ImageROI
```

### 规则4: 代码实现方式
所有step的代码在**同一个Program.cs**中实现，每个step对应一个方法：
```csharp
static void Main(string[] args) {
    // Step 0
    var preResult = Step0_Preprocess(imagePath, row1, col1, row2, col2);
    
    // Step 1 (如果阈值有效)
    var circleResult = Step1_CircleStrategy(preResult);
    
    // Step 2 (如果阈值有效)
    var rectResult = Step2_RectangleStrategy(preResult);
    
    // Step 3 (始终执行)
    var centroidResult = Step3_CentroidStrategy(preResult);
    
    // Step 3b (始终执行 - 镜面反光过滤)
    var specularResult = Step3b_SpecularFilter(preResult);
    
    // Step 4 (始终执行 - 使用CleanImageROI)
    var edgeResult = Step4_EdgeStrategy(preResult, specularResult);
    
    // Step 5 (全局反思 - 含光斑场景规则)
    Step5_GlobalReflection(circleResult, rectResult, centroidResult, edgeResult, specularResult, preResult);
}
```

## 默认配置（继承自原skill）

### 依赖项
- **HalconDotNet引用**: `lib/halcondotnet.dll`
- **项目模板**: .NET 8.0 控制台应用

### 生成cs文件规则
- 每次独立生成新的cs文件，不覆盖已有文件
- 命名: `{当前日期YYYYMMDD}_{图片文件名(不含扩展名)}.cs`
- 生成位置: 与输入图片同目录
- 文件内容: 包含执行过的所有策略代码 + 全局反思逻辑

## 技能链总览
```
skill/center_localization_orchestrator.md  ← 本文件（编排入口）
  ├── skill/step0_image_preprocess.md      ← 图像预处理+阈值预检
  ├── skill/step1_circle_strategy.md       ← 策略A: 圆特征
  ├── skill/step2_rectangle_strategy.md    ← 策略B: 矩形/平行线特征
  ├── skill/step3_centroid_strategy.md     ← 策略C: 区域重心(兜底)
  ├── skill/step3b_specular_filter.md      ← Step 3b: 镜面反光过滤(始终执行)
  ├── skill/step4_edge_strategy.md         ← 策略Edge: 直接边缘检测(使用CleanImageROI)
  └── skill/step5_global_reflection.md     ← 全局反思+置信度评分
```
