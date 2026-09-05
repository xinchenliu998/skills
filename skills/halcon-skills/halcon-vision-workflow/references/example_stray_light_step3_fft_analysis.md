# Step 3: 杂光检测 - 光斑形态分析（异型光斑检测）

## 目标
对每个光源的光斑形状进行分析，检测"异型光斑"（非正常圆形/方形的变形光斑），作为NG判定的补充依据。

## 背景（来自标准限度样品）
- NG样品②描述: "灯源有异型光斑NG"
- OK极限②描述: "光源模糊变形（非光刺，是模糊）极限OK品"
- 区分: 严重变形→异型NG，轻微模糊→极限OK

## 输入
- `image`: 灰度图像
- `spots`: Step1/Step2更新后的光源列表

## 处理流程

### 3.1 逐光源形态分析
```csharp
foreach (var spot in spots)
{
    // 已在Step1中提取了: Circularity, Convexity, Rectangularity
    
    // 异型光斑判定条件（需同时满足多个）:
    // 1. 圆度过低: 正常光斑圆度>0.7, 异型<0.5
    // 2. 凸度过低: 正常>0.85, 异型<0.7
    // 3. 面积异常: 远超或远低于平均值
    
    double avgArea = spots.Average(s => s.Area);
    double areaRatio = spot.Area / Math.Max(avgArea, 1);
    
    bool isAbnormal = false;
    string reason = "";
    
    // 严重变形: 圆度和凸度都很低
    if (spot.Circularity < 0.4 && spot.Convexity < 0.65)
    {
        isAbnormal = true;
        reason = $"严重变形(圆度={spot.Circularity:F2},凸度={spot.Convexity:F2})";
    }
    // 面积异常+形状差: 面积偏离>50%且形状不规则
    else if ((areaRatio > 2.0 || areaRatio < 0.3) && spot.Circularity < 0.5)
    {
        isAbnormal = true;
        reason = $"面积异常(比值={areaRatio:F2})+形状差(圆度={spot.Circularity:F2})";
    }
    
    spot.IsAbnormalShape = isAbnormal;
}
```

### 3.2 边界情况: 模糊vs异型的区分
```csharp
// OK极限②: "光源模糊变形" → 面积可能偏大，但凸度仍>0.7
// 异型NG: 明显非圆非方，有尖角或缺口
// 区分关键: 凸度(Convexity)
//   - 模糊光斑: 边缘弥散但整体仍凸 → convexity > 0.7
//   - 异型光斑: 有明显凹陷/突起 → convexity < 0.65

// 进一步用轮廓分析验证(可选)
HOperatorSet.GenContourRegionXld(spotRegion, out HObject contour, "border");
HOperatorSet.ContourLength(contour, out HTuple contourLen);
// 紧凑度 = 4π*面积/周长² (圆=1.0)
double compactness = 4 * Math.PI * spot.Area / (contourLen.D * contourLen.D);
// 异型光斑的紧凑度通常<0.5
```

## 输出
- 更新每个spot的: `IsAbnormalShape`
- `abnormalCount`: 异型光斑数量
- 异型光斑列表（用于标注）

## 判定阈值总结
| 指标 | 正常光斑 | 模糊OK极限 | 异型NG |
|------|---------|-----------|--------|
| 圆度 | >0.7 | 0.5-0.7 | <0.4 |
| 凸度 | >0.85 | 0.7-0.85 | <0.65 |
| 面积比 | 0.7-1.5 | 0.5-2.0 | <0.3或>2.0 |

## 自反思
- 异型光斑阈值是否太严格/太松？
- 是否有正常光斑因边缘效应被误判为异型？
- 模糊光斑和异型光斑的边界是否清晰？
