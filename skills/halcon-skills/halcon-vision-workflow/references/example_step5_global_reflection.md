# Step 5: 全局反思与置信度评分

## 职责
收集所有策略(A/B/C/Edge)的结果和自反思状态，进行交叉校验，选择最优策略，计算全局置信度评分，输出最终结果。

## 前置条件
- Step 0~4 均已完成
- 至少有策略C或策略Edge之一有输出

## 输入（来自Step 1~4 + Step 3b）
| 来源 | 字段 |
|------|------|
| Step 0 | ROI信息, ThresholdFailed |
| Step 1 | 策略A: Valid, Row, Col, SelfCheck |
| Step 2 | 策略B: Valid, Row, Col, HasParallelLines, SelfCheck |
| Step 3 | 策略C: Row, Col, AreaRatio, SelfCheck |
| Step 3b | SpecularDetected, SpecularCount, SpecularAreaRatio, SpecularSelfCheck |
| Step 4 | 策略Edge: Valid, Row, Col, Method, SelfCheck (可能使用CleanImageROI) |

## 输出
| 字段 | 类型 | 说明 |
|------|------|------|
| FinalRow, FinalCol | double | 最终中心坐标 |
| Confidence | double | 置信度分数 (0~1) |
| ConfidenceLevel | enum | HIGH / MEDIUM / LOW |
| ChosenStrategy | string | 最终采用的策略名 |
| Reasoning | string | 决策理由 |

## 交叉校验规则

### 规则1: B与C一致性（原反思规则2）
```
IF B.Valid AND C.SelfCheck != FAIL:
    Dist_BC = Distance(B, C)
    TargetSize = sqrt(C.Area)
    
    IF Dist_BC > TargetSize * 0.1:
        → B和C不一致，至少一个不可靠
        → 倾向信任C（C更鲁棒）
```

### 规则2: Edge与C交叉验证（原反思规则5）
```
IF Edge.Valid AND C.SelfCheck != FAIL:
    Dist_Edge_C = Distance(Edge, C)
    
    IF Dist_Edge_C < 2.0 px:
        → 高度一致，互相印证 → 置信度 +0.15
        → 即使C的AreaRatio>95%（规则4告警），结果仍可信
    
    IF Dist_Edge_C < 5.0 px:
        → 基本一致 → 置信度 +0.05
    
    IF Dist_Edge_C > TargetSize * 0.1:
        → 偏差过大，需审慎选择
```

### 规则3: 多策略一致性加分
```
可信策略列表 = [s for s in (A,B,C,Edge) if s.SelfCheck == PASS]

IF 可信策略.Count >= 3:
    → 计算所有可信策略结果的两两距离
    → IF 所有距离 < TargetSize * 0.05:
        → 高度一致 → 置信度 +0.1
```

## 策略选择决策树

```
Step 1: 收集可信策略
  可信列表 = SelfCheck为PASS的策略
  部分可信列表 = SelfCheck为WARN的策略
  失败列表 = SelfCheck为FAIL或N_A的策略

Step 2: 按优先级选择
  IF A.SelfCheck == PASS:
    → 候选 = A（同心圆最精确）
  ELIF B.SelfCheck == PASS AND B.HasParallelLines:
    → 候选 = B（有平行线的矩形可信）
  ELIF B.SelfCheck == PASS AND !B.HasParallelLines:
    → 候选 = 加权(B*0.4 + C*0.6)（无平行线时C权重更高）
  ELIF C.SelfCheck == PASS:
    → 候选 = C
  ELIF Edge.SelfCheck == PASS:
    → 候选 = Edge
  ELIF C.SelfCheck == WARN AND Edge.SelfCheck == PASS:
    → 候选 = Edge（C告警时Edge补救）
  ELIF C.SelfCheck == WARN:
    → 候选 = C（有值总比没有好）
  ELSE:
    → 候选 = ROI几何中心（最终兜底）

Step 3: 交叉验证调整
  → 应用规则1/2/3
  → 如果交叉验证发现候选不可靠，降级到下一个
```

## 置信度评分体系

```
初始置信度 = 1.0

// ===== 扣分项 =====
IF Step1(A).SelfCheck == FAIL AND 最终采用了A:
    置信度 -= 0.5
IF Step1(A).SelfCheck == FAIL AND 未采用A:
    置信度 -= 0.05  // 说明系统正确避开

IF Step2(B).SelfCheck == FAIL (B退化为ROI中心):
    IF 最终采用了B → 置信度 -= 0.4
    ELSE → 置信度 -= 0.1

IF 规则1告警 (B和C不一致):
    置信度 -= 0.2

IF Step3(C).SelfCheck == WARN (面积异常):
    置信度 -= 0.3

IF ThresholdFailed:
    置信度 -= 0.2  // 阈值全面失效是全局风险

// ===== 加分项 =====
IF 规则2: Edge-C一致 < 2px:
    置信度 += 0.15

IF 规则2: Edge-C一致 < 5px:
    置信度 += 0.05

IF 规则3: 多策略一致:
    置信度 += 0.1

IF A.SelfCheck == PASS AND 圆心距 < 5px:
    置信度 += 0.15

// ===== 置信度等级 =====
置信度 > 0.8  → HIGH（可直接使用）
0.5 < 置信度 ≤ 0.8 → MEDIUM（建议人工确认）
置信度 ≤ 0.5 → LOW（需要缩小ROI或切换方法）

// 置信度钳位到 [0, 1]
置信度 = Math.Max(0, Math.Min(1, 置信度))
```

## 阈值失效时的特殊决策路径

```
ThresholdFailed == true:
  │
  ├─ A: N/A, B: N/A
  ├─ C: 有结果但WARN (面积>95%)
  ├─ Edge: 唯一补救手段
  │
  ├─ IF Edge.PASS + Edge-C一致(<2px):
  │    → 采用Edge, 置信度: 1.0 - 0.2(阈值失效) - 0.3(C面积) + 0.15(Edge-C一致) = 0.65 → MEDIUM
  │    → 但如果Edge-C<1px，可手动提升到HIGH
  │
  ├─ IF Edge.PASS + Edge-C不一致:
  │    → 采用Edge, MEDIUM
  │
  └─ IF Edge.FAIL:
       → 采用ROI几何中心, LOW
       → 建议用户重新选择ROI
```

## ⚠️ 镜面反光场景的特殊反思规则（新增）

### 规则4: 光斑检测对置信度的影响
```
IF SpecularDetected == true:
    // 记录光斑信息
    Console.WriteLine($"光斑检测: {SpecularCount}个, 面积占比={SpecularAreaRatio:P2}");
    
    // Edge使用了CleanImageROI → 加分（已排除干扰）
    IF Edge.SelfCheck == PASS AND Edge使用了CleanImageROI:
        置信度 += 0.10  // 光斑已过滤，Edge结果更可信
    
    // 光斑面积占比>15% → 全局降低置信度（信息损失风险）
    IF SpecularAreaRatio > 0.15:
        置信度 -= 0.10
    
    // 光斑偏向一侧 + Edge也偏向对侧 → 强烈WARN
    IF 光斑偏向ROI某侧 AND Edge结果也偏离ROI中心:
        → SelfCheck = WARN
        → 原因: "光斑偏向一侧可能导致Edge中心偏移"
```

### 规则5: 光斑场景下的策略C修正
```
// 光斑会影响阈值分割区域的重心
IF SpecularDetected == true AND C.SelfCheck == PASS:
    // 光斑区域属于"light"前景 → light模式的重心会被拉向光斑
    // dark模式的前景不含光斑 → dark模式的重心更可信
    → 如果C使用的是light模式，降低C的权重
    → 如果C使用的是dark模式，C结果不受光斑影响
```

### 规则6: 光斑场景下Edge vs 无光斑Edge的差异检验
```
// 如果同时有带光斑和去光斑的Edge结果，可以做差异检验
IF SpecularDetected AND 有原始Edge结果 AND 有CleanEdge结果:
    Dist_Orig_Clean = Distance(原始Edge, CleanEdge)
    IF Dist_Orig_Clean > 10px:
        → 光斑确实造成了显著偏差
        → 优先信任CleanEdge结果
        → 置信度 += 0.05（成功纠偏）
    ELSE:
        → 光斑影响不大
        → 两者均可使用
```

### 光斑场景典型案例参考
```
案例: MVSA_Pic_2026_03_25_16_28_36.bmp
  实际中心(人工): (1855.02, 1527.64)
  原Edge结果(无过滤): (1852.00, 1567.00) — ΔRow=39.4px 偏差！
  原因: 镜头下半区光斑产生假边缘，拉偏矩形拟合Y坐标
  教训: 
    1. 策略A/B/C/Edge全部WARN或偏差，说明存在系统性干扰
    2. 当多策略不一致时，应检查是否存在镜面反光
    3. Edge覆盖度100%但中心偏差大 → 高覆盖度不等于高精度
    4. 光斑过滤后Edge可纠偏约30~50px
```

## 快速判断表

| A | B | C | Edge | 光斑 | 最终选择 | 置信度 |
|---|---|---|------|------|----------|--------|
| PASS | PASS | PASS | PASS | 无 | A | HIGH |
| PASS | FAIL | PASS | PASS | 无 | A | HIGH |
| FAIL | PASS(有平行线) | PASS | PASS | 无 | B | HIGH |
| FAIL | PASS(无平行线) | PASS | PASS | 无 | B*0.4+C*0.6 | MEDIUM~HIGH |
| FAIL | FAIL | PASS | PASS | 无 | C (Edge验证) | HIGH |
| FAIL | FAIL | WARN | PASS | 无 | Edge | MEDIUM~HIGH |
| FAIL | FAIL | WARN | FAIL | 无 | C(勉强) | LOW~MEDIUM |
| N/A | N/A | WARN | PASS | 无 | Edge | MEDIUM |
| N/A | N/A | WARN | FAIL | 无 | ROI中心 | LOW |
| WARN | WARN | PASS | PASS | **有** | Edge(Clean) | **MEDIUM~HIGH** |
| FAIL | WARN | PASS | PASS | **有** | Edge(Clean)+C交叉 | **MEDIUM** |
| FAIL | FAIL | WARN | PASS | **有** | Edge(Clean) | **MEDIUM** |

## 输出格式
```
=== Step 5: 全局反思 ===
策略汇总:
  A: PASS/WARN/FAIL/N_A — (Row, Col) — {原因}
  B: PASS/WARN/FAIL/N_A — (Row, Col) — {原因}
  C: PASS/WARN/FAIL — (Row, Col) — 面积占比xx.x%
  Edge: PASS/WARN/FAIL — (Row, Col) — 方法x

交叉校验:
  B-C距离: xx.x px → 一致/不一致
  Edge-C距离: xx.x px → 一致/不一致
  多策略一致性: 是/否

最终决策:
  采用策略: A/B/C/Edge/B+C加权/ROI中心
  决策理由: {详细说明}
  最终中心: (Row, Col)
  置信度: x.xx → HIGH/MEDIUM/LOW

=== 全局反思完成 ===
```

## 核心教训
1. **不能盲目平均**：偏差大时取平均是"两边都不靠"
2. **告警≠错误**：告警是提醒需要验证，不是直接否定
3. **交叉验证是关键**：多策略一致性比任何单策略的自检更可靠
4. **ROI质量决定上限**：紧凑ROI→所有策略可靠；宽松ROI→B容易退化
5. **⚠️ 镜面反光是隐蔽的系统性干扰**：光斑产生的"假边缘"灰度梯度比真实物体边缘更强，会同时干扰多个策略。当所有策略结果都不一致（全WARN/偏差大），应首先怀疑是否存在镜面反光
6. **高覆盖度≠高精度**：Edge策略覆盖度100%仍可能偏差40px（因光斑假边缘参与了拟合）
7. **光斑必须先于边缘检测处理**：在Step 3b过滤光斑后再做Edge检测，是修正光斑干扰的唯一有效路径
8. **light模式重心受光斑影响更大**：光斑属于高灰度区域，light模式会将其作为"前景"，导致重心被拉偏。有光斑时dark模式的重心更可信
