# Skill: 粗分析——模组中心定位 (Coarse Analysis: Center Localization)

## 默认配置

### 依赖项
- **HalconDotNet引用**: 默认使用项目 `lib/halcondotnet.dll`（相对路径: `../lib/halcondotnet.dll`）
- **项目模板**: .NET 8.0 控制台应用，csproj中需包含以下引用：
```xml
<Reference Include="halcondotnet">
  <HintPath>..\lib\halcondotnet.dll</HintPath>
</Reference>
```

### 反思skill默认开启
- **粗分析完成后，必须自动触发反思skill**: `skill/center_localization_reflection.md`
- **不可跳过反思**: 粗分析输出的策略A/B/C/Edge结果，必须经过反思skill的自校验规则检查后，才能输出最终结果
- **反思skill负责**: 自校验 → 循环思考（如有告警）→ 标记不可信策略 → 输出最终可信结果 + 置信度评分

### 完整技能链（自动串联，无需用户手动触发）
```
用户请求(图片路径 + ROI坐标)
  │
  ├─ Step 1: 可选 → skill/roi_emphasize_enhance.md（ROI对比度增强，按需）
  │
  ├─ Step 2: 必选 → skill/center_localization_coarse_analysis.md（本skill: 粗分析）
  │    └─ 输出: 策略A/B/C/Edge各自的中心坐标 + 各项中间数据
  │
  ├─ Step 3: 必选 → skill/center_localization_reflection.md（反思自校验）
  │    └─ 输入: 粗分析的全部输出数据
  │    └─ 输出: 最终可信中心坐标 + 置信度等级(HIGH/MEDIUM/LOW)
  │
  └─ Step 4: 必选 → 生成独立cs文件
       └─ 命名: {年月日}_{图片名}.cs（含反思逻辑的完整可运行代码）
```

### 生成cs文件规则
- **每次独立生成新的cs文件**，不覆盖已有文件
- **命名使用当前计算机获取的年月日 + 图片名**，如: `20260325_0.019100.cs`
- **生成位置**: 与图片同目录，或用户指定目录
- **文件内容**: 包含完整的粗分析 + 反思自校验逻辑的可独立运行的C#代码

## 场景描述
**用户请求**: 给定一个图像处理任务：帮我找出这张图中ROI区域的模组中心  
**模型响应**: 分析任务决定所需工具 → 自动调用本skill（粗分析）→ 自动调用反思skill → 输出最终结果

## 核心思路
中心定位是一个**探索式**的粗分析过程，不是直接跳到某个算子，而是先对ROI区域内的图像特征进行整体探索，判断当前图像**适合用哪种几何特征来逼近中心**，然后选择最优策略。

### 决策树：如何选择中心定位策略

```
输入：ROI区域图像
  │
  ├─ Step1: 阈值分割有效性预检（★ 新增关键步骤）
  │    ├─ BinaryThreshold('max_separability', 'dark') → 计算前景面积占比
  │    ├─ BinaryThreshold('max_separability', 'light') → 计算前景面积占比
  │    └─ 判断: 是否存在有效分割模式？（前景占比在5%~95%之间）
  │         ├─ 是 → 进入传统三策略探索（Step2）
  │         └─ 否（两种模式都失效）→ 直接进入策略Edge（Step3）
  │
  ├─ Step2: 传统特征探索（需阈值分割有效）
  │    ├─ 策略A: 探测圆特征 → edges_sub_pix + fit_circle_contour_xld
  │    │    └─ 多个圆的圆心是否接近？
  │    │         ├─ 是（近似同心圆）→ 策略A：同心圆圆心法
  │    │         └─ 否 → 转向策略B
  │    │
  │    ├─ 策略B: 探测直线/矩形特征 → fit_line/fit_rectangle2
  │    │    └─ 是否存在两组以上近似平行线？
  │    │         ├─ 是 → 策略B：外轮廓边缘中心法
  │    │         └─ 否 → 转向策略C
  │    │
  │    └─ 策略C: 区域重心法（兜底）
  │
  └─ Step3: 直接边缘检测策略（★ 不依赖阈值分割）
       ├─ 策略Edge: Emphasize增强 → EdgesSubPix → 矩形拟合/整体包围
       └─ 适用于: 阈值分割失效、模组填满ROI等场景
```

### 人类经验先验知识
- **多个近似同心圆的图像中**，圆心往往更接近模组真实中心
- **没有近似同心圆时**，外轮廓边缘的几何中心更接近模组真实中心
- 圆特征通常比矩形特征更精确（亚像素拟合精度更高）
- 但当图像中无明显圆特征时，强行拟合圆会产生严重误差
- **当模组几乎填满ROI时**，阈值分割会失效（前景占比接近100%或接近0%），此时需要不依赖阈值的方法

---

## 阈值分割有效性预检（★ 新增关键步骤）

### 为什么需要预检？

**经验教训（实验3: Image_20260225093305139.bmp）**：
- ROI区域灰度均匀，BinaryThreshold('max_separability')无法有效分割
- dark模式前景面积98.7%（几乎全是前景），light模式仅1.3%（几乎没有前景）
- **三策略A/B/C全部失效**，因为它们都以阈值分割为前置步骤
- 根因：**模组几乎完美填满了整个ROI区域**，前景和ROI几乎重合

### 预检逻辑

```
// 对dark和light两种模式分别检查
foreach mode in ['dark', 'light']:
    BinaryThreshold(ImageROI, 'max_separability', mode) → ForegroundRegion
    AreaCenter(ForegroundRegion) → FgArea
    AreaCenter(Domain) → DomArea
    FgRatio = FgArea / DomArea

    IF 0.05 <= FgRatio <= 0.95:
        → 该模式有效，记录为可用模式
    ELSE:
        → 该模式无效（前景占比异常），跳过

IF 无任何有效模式:
    → ⚠️ 阈值分割全面失效，标记 ThresholdFailed = true
    → 策略A/B直接标记N/A，策略C仍执行但标记低可信度
    → 必须执行策略Edge作为补救
```

### dark/light双模式自适应规则

每个传统策略（A/B/C）都需要**同时尝试dark和light两种模式**：

| 场景 | dark模式 | light模式 | 选择规则 |
|------|----------|-----------|----------|
| 暗色模组在亮背景上 | 前景占比合理 | 前景占比异常 | 使用dark模式 |
| 亮色模组在暗背景上 | 前景占比异常 | 前景占比合理 | 使用light模式 |
| 两种都合理 | 有效 | 有效 | 选面积占比更接近目标特征的 |
| 两种都失效 | >95%或<5% | >95%或<5% | 阈值分割失效，转Edge策略 |

---

## 策略A：同心圆圆心法

### 适用条件
- ROI区域内存在**多个近似同心圆**（如晶圆、镜头模组、圆形芯片等）
- 多个圆的圆心距离在阈值范围内（判定为近似同心）
- **前提**: 阈值分割有效（前景占比5%~95%）

### 算子流程
```
ReadImage → GenRectangle1(ROI) → ReduceDomain
→ BinaryThreshold('max_separability', mode)（尝试dark/light两种模式）
  → 检查前景占比: 5%~95%有效，否则跳过该模式
→ Boundary（提取边界）→ DilationCircle（边界膨胀构建边缘ROI）
→ ReduceDomain → EdgesSubPix（亚像素边缘检测）
→ SelectShapeXld（按轮廓长度筛选有效边缘）
→ FitCircleContourXld（对多条边缘分别拟合圆）
→ 判断: 多个圆心距离是否 < 阈值？
    → 是: 取所有圆心的加权平均（权重=拟合质量/半径） → 输出中心
    → 否: 转向策略B
```

### 关键算子说明
| 算子 | 作用 | 关键参数 |
|------|------|----------|
| `binary_threshold` | 前景/背景分割 | 'max_separability', 尝试'dark'和'light' |
| `boundary` | 提取区域边界 | 'inner' |
| `dilation_circle` | 膨胀边界以构建边缘检测ROI | 半径3.5 |
| `edges_sub_pix` | 亚像素级边缘检测 | 'canny', Alpha=1, Low=20, High=40 |
| `fit_circle_contour_xld` | 对XLD轮廓拟合圆 | 'geohuber'（鲁棒拟合）|
| `area_center` | 区域面积和重心 | 作为辅助验证 |

### 同心性判断逻辑
```
输入: 多个拟合圆的 (Row_i, Col_i, Radius_i)
计算: 所有圆心的两两距离
判定: 若所有圆心两两距离 < max(Radius_max * 0.1, 10像素)
      → 判定为近似同心圆
      → 中心 = 加权平均圆心
```

---

## 策略B：外轮廓边缘中心法

### 适用条件
- ROI区域内无明显同心圆特征
- 但存在**两组以上近似平行线**（如矩形模组、PCB、芯片封装等）
- **前提**: 阈值分割有效（前景占比5%~95%）

### 算子流程
```
ReadImage → GenRectangle1(ROI) → ReduceDomain
→ BinaryThreshold('max_separability', mode)（尝试dark/light两种模式）
  → 检查前景占比: 5%~95%有效，否则跳过该模式
→ Connection（连通域分析）
→ SelectShape（按面积筛选: ROI面积的5%~150%）
→ FillUp → ShapeTrans('convex')（凸包变换）
→ Boundary → DilationCircle
→ ReduceDomain → EdgesSubPix（亚像素边缘检测）
→ SelectShapeXld（按轮廓长度筛选）
→ UnionAdjacentContoursXld（合并相邻轮廓段）
→ FitLineContourXld（直线拟合，判断平行性）
→ SmallestRectangle2（最小外接矩形中心）
→ 输出矩形中心 (Row, Column) 作为模组中心
```

### 关键算子说明
| 算子 | 作用 | 关键参数 |
|------|------|----------|
| `binary_threshold` | 阈值分割 | 尝试'dark'和'light'两种模式 |
| `connection` | 连通域提取 | - |
| `select_shape` | 按形状特征筛选 | 'area', ROI面积的5%~150% |
| `fill_up` | 填充区域内部孔洞 | - |
| `shape_trans` | 形状变换（凸包） | 'convex' |
| `edges_sub_pix` | 亚像素边缘检测 | 'canny', Alpha=1, Low=20, High=40 |
| `union_adjacent_contours_xld` | 合并相邻轮廓 | MaxDist=5, MaxAngle=1 |
| `fit_line_contour_xld` | 直线拟合（判断平行性） | 'tukey' |
| `smallest_rectangle2` | 最小外接矩形 | 输出中心+角度+半轴长 |

### 平行线判断逻辑
```
输入: 拟合得到的多条直线 (Row_i, Col_i, Phi_i)
计算: 所有直线对的角度差
判定: 若存在 ≥ 2组 角度差 < 5° 的直线对
      → 判定为存在近似平行线结构
      → 适合使用矩形拟合或平行线中心法
```

---

## 策略C：区域重心法（兜底方案）

### 适用条件
- 圆特征和直线特征均不明显
- 目标区域形状不规则
- 作为最后的兜底方案
- **注意**: 虽然C也使用阈值分割，但即使分割异常也会输出结果（标记低可信度）

### 算子流程
```
ReadImage → GenRectangle1(ROI) → ReduceDomain
→ BinaryThreshold('max_separability', mode)（尝试dark/light两种模式）
  → 对每种模式计算: 最大连通域面积、重心、面积占比
  → 选择面积占比最合理的模式（最接近50%的优先，5%~95%范围内）
→ Connection → SelectShapeStd('max_area', 0)（选最大连通域）
→ AreaCenter（计算区域重心）
→ 输出重心 (Row, Column) 作为模组中心
```

### 关键算子说明
| 算子 | 作用 | 关键参数 |
|------|------|----------|
| `binary_threshold` | 自动阈值分割 | 'max_separability', 尝试'dark'和'light' |
| `connection` | 连通域提取 | - |
| `select_shape_std` | 选择标准形状区域 | 'max_area'（选最大区域）|
| `area_center` | 计算面积和重心 | 输出 Area, Row, Column |

### dark/light模式选择规则（策略C特有）
```
对dark和light两种模式都执行分割:
  → 计算各自的面积占比 areaRatio = maxConnectedArea / domainArea

选择规则:
  1. 优先选面积占比在5%~95%范围内的模式
  2. 如果两种模式都在范围内，选更接近50%的
  3. 如果两种模式都不在范围内，选面积更大的模式（但标记低可信度）
```

---

## 策略Edge：直接边缘检测法（★ 新增补救策略）

### 适用条件
- **阈值分割失效**（dark/light两种模式前景占比都>95%或<5%）
- **模组几乎填满ROI**，灰度均匀，前景/背景对比度极低
- 作为传统三策略失效时的**循环思考补救方案**

### 为什么需要这个策略？

**经验教训**: 当模组完美填满ROI时，`BinaryThreshold`无法区分前景和背景。但即使前景/背景灰度接近，**模组的物理边缘**（如IC封装边缘、玻璃边缘等）仍然会在图像中产生微弱的灰度梯度。`Emphasize`增强 + `EdgesSubPix`可以捕获这些微弱边缘。

### 设计原理

```
传统策略: 阈值分割 → 区域提取 → 在区域边界上做边缘检测
  ↓ 阈值分割失效时，区域提取就失败了

Edge策略: 跳过阈值分割 → 直接对ROI图像做边缘检测 → 从边缘重建几何形状
  ↓ 不依赖阈值，只依赖灰度梯度（边缘信息）
```

### 算子流程
```
输入: ROI区域图像（ReduceDomain后的图像）

Step 1: 对比度增强
→ Emphasize(Image, 7, 7, 1.5)  // 局部对比度增强，让微弱边缘更明显

Step 2: 直接亚像素边缘检测（不需要先做阈值分割！）
→ EdgesSubPix(Enhanced, 'canny', 1.5, 15, 35)  // 低阈值以捕获微弱边缘

Step 3: 筛选有意义的边缘轮廓
→ SelectShapeXld('contlength', minLen, 99999)
   其中 minLen = min(ROI_Height, ROI_Width) * 0.2  // ROI短边的20%
   如果筛选结果为空，降低到 * 0.1 再试

Step 4: 合并相邻轮廓
→ UnionAdjacentContoursXld(MaxDist=10, MaxAngle=1)

Step 5: 矩形拟合（两种方法，逐级尝试）

  方法1: 逐轮廓FitRectangle2（精确但可能只覆盖局部）
  → 对每条合并后轮廓: FitRectangle2ContourXld('tukey', ...)
  → 计算矩形面积 = L1 * L2 * 4
  → 选面积最大的矩形
  → 验证: 矩形面积是否覆盖ROI面积的50%以上？
    → 是: 该矩形中心即为模组中心（可信度高）
    → 否: 说明只拟合到局部边缘，转方法2

  方法2: 整体SmallestRectangle2（更鲁棒的全局方法）
  → GenRegionContourXld(united, 'filled')  // XLD → 区域
  → Union1 → ShapeTrans('convex')  // 合并+凸包
  → SmallestRectangle2  // 整体最小外接矩形
  → 验证: 中心是否在ROI范围内？
    → 是: 该矩形中心即为模组中心
    → 否: Edge策略失效
```

### 关键算子说明
| 算子 | 作用 | 关键参数 |
|------|------|----------|
| `emphasize` | 局部对比度增强 | MaskWidth=7, MaskHeight=7, Factor=1.5 |
| `edges_sub_pix` | 亚像素边缘检测（直接在ROI上） | 'canny', Alpha=1.5, Low=15, High=35 |
| `select_shape_xld` | 按轮廓长度筛选 | 'contlength', min=ROI短边*0.2 |
| `union_adjacent_contours_xld` | 合并相邻轮廓 | MaxDist=10, MaxAngle=1 |
| `fit_rectangle2_contour_xld` | 逐轮廓矩形拟合 | 'tukey'（需try/catch，部分轮廓会失败） |
| `gen_region_contour_xld` | XLD转区域 | 'filled' |
| `smallest_rectangle2` | 整体最小外接矩形 | 用于方法2备选 |

### Edge策略的关键注意事项

1. **FitRectangle2ContourXld可能对某些轮廓抛异常**（HALCON #3266: No points found for at least one side），必须用try/catch包裹每个轮廓的拟合调用
2. **方法1的覆盖度验证很关键**：单轮廓矩形拟合可能只覆盖ROI的一部分（如40%），此时矩形中心偏向该边缘所在区域，不代表模组整体中心
3. **方法2（整体SmallestRectangle2）通常更可靠**：因为它利用了所有有效边缘的空间分布，给出的是整体包围矩形
4. **Edge策略的Emphasize参数**：Factor=1.5是适中值，如果边缘太弱可以增大到2.0

### 何时Edge策略特别有效？

| 场景 | 阈值分割状态 | Edge策略效果 |
|------|-------------|-------------|
| 模组填满ROI，灰度均匀 | ❌ 失效（>95%前景） | ✅ 能检测到模组边缘 |
| 低对比度图像 | ❌ 分割不准确 | ✅ Emphasize增强后有效 |
| 多层透明/半透明结构 | ❌ 多阈值干扰 | ✅ 直接检测物理边缘 |

---

## 完整粗分析编排流程

### Phase 1: 图像读取与ROI限定
```
ReadImage(ImagePath) → Image
GenRectangle1(Row1, Col1, Row2, Col2) → ROI
ReduceDomain(Image, ROI) → ImageROI
GetImageSize → 输出图像尺寸
计算: ROI面积、ROI对角线、ROI几何中心
```

### Phase 2: 阈值分割预检 + 四策略特征探索
```
// 2.0 预检: 阈值分割有效性
foreach mode in ['dark', 'light']:
    BinaryThreshold → 计算前景占比
    记录: 哪些模式有效（5%~95%）

// 2a. 策略A: 圆特征探索（遍历有效模式）
foreach 有效mode:
    BinaryThreshold → Boundary → DilationCircle → EdgesSubPix
    FitCircleContourXld → 判断同心性 → 若同心则输出圆心

// 2b. 策略B: 矩形特征探索（遍历有效模式）
foreach 有效mode:
    BinaryThreshold → Connection → SelectShape → FillUp → ShapeTrans
    EdgesSubPix → FitLine → 判断平行性
    SmallestRectangle2 → 输出矩形中心

// 2c. 策略C: 区域重心（遍历所有模式，选最优）
foreach mode in ['dark', 'light']:
    BinaryThreshold → Connection → SelectShapeStd('max_area')
    AreaCenter → 记录(重心, 面积, 占比)
选择面积占比最合理的模式

// 2d. 策略Edge: 直接边缘检测（★ 始终执行，作为交叉验证/补救）
Emphasize → EdgesSubPix → SelectShapeXld → UnionAdjacentContours
→ 方法1: FitRectangle2(逐轮廓) → 覆盖度验证
→ 方法2: SmallestRectangle2(整体) → 备选
```

### Phase 3: 输出粗分析结果 → 自动触发反思skill
```
返回:
  策略A: (Valid, Row, Col, Radii[]) or N/A
  策略B: (Valid, Parallel, Row, Col) or N/A  
  策略C: (Row, Col, Area)  // 始终有值
  策略Edge: (Valid, Row, Col) or N/A  // ★ 新增
  ROI信息: (CenterRow, CenterCol, Area, Diagonal)
  分割状态: ThresholdFailed(bool)  // ★ 新增

→ 自动调用 reflection skill 进行自校验
```

---

## 策略选择总结

| 策略 | 适用场景 | 精度 | 鲁棒性 | 依赖阈值 | 典型对象 |
|------|----------|------|--------|----------|----------|
| A. 同心圆圆心法 | 多个近似同心圆 | ★★★★★ | ★★★★ | ✅ 是 | 晶圆、镜头、圆形芯片 |
| B. 外轮廓边缘中心法 | 矩形/多边形轮廓 | ★★★★ | ★★★★ | ✅ 是 | PCB、SMD、封装模组 |
| C. 区域重心法 | 任意形状（兜底） | ★★★ | ★★★★★ | ✅ 是 | 不规则零件、夹具 |
| **Edge. 直接边缘法** | **阈值失效/低对比度** | **★★★★** | **★★★** | **❌ 否** | **填满ROI的模组、透明件** |

### 策略优先级（无告警时）
```
A(同心圆) > B(矩形,有平行线) > B+C加权(矩形,无平行线) > C(重心)
```

### 策略失效时的补救链
```
传统策略全部失效（阈值分割失效）
  → Edge策略补救
    → Edge有效 → 采用Edge结果
    → Edge也失效 → 输出ROI几何中心 + LOW置信度
```

## 注意事项
- 粗分析的目的是**快速判断特征类型并给出初步中心**，不追求极致精度