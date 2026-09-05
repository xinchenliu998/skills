# Skill: ROI区域对比度增强 (ROI Emphasize Enhance)

## 描述
读取一张图像，并对指定的ROI（矩形区域）进行Emphasize对比度增强处理。该技能适用于需要对图像局部区域进行对比度增强的场景，例如缺陷检测前的图像预处理。

## 适用场景
- 工业视觉中对局部区域进行对比度增强以突出细节
- 缺陷检测预处理阶段，增强目标区域的纹理/边缘特征
- 图像质量较低时对感兴趣区域进行增强

## 输入参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| ImagePath | string | 是 | 输入图像的完整文件路径 |
| ROI_Row1 | double | 是 | ROI矩形左上角行坐标 |
| ROI_Col1 | double | 是 | ROI矩形左上角列坐标 |
| ROI_Row2 | double | 是 | ROI矩形右下角行坐标 |
| ROI_Col2 | double | 是 | ROI矩形右下角列坐标 |
| MaskWidth | int | 否 | Emphasize滤波器掩膜宽度，默认7，范围[3, 15]，必须为奇数 |
| MaskHeight | int | 否 | Emphasize滤波器掩膜高度，默认7，范围[3, 15]，必须为奇数 |
| Factor | double | 否 | Emphasize增强因子，默认1.0，范围[0.3, 2.0]。值越大对比度增强越明显 |

### 参数调控建议
- **MaskWidth / MaskHeight**: 控制滤波器的作用范围。值越大，增强效果越平滑、作用范围越广；值越小，增强效果越精细、局部性越强。推荐范围 3~15（奇数）。
- **Factor**: 控制增强强度。Factor=1.0 为适中增强；Factor<1.0 为轻度增强；Factor>1.0 为强增强。建议不超过2.0以避免过增强。

## 输出
- 增强后的ROI区域图像对象（HObject）

## 代码模板

```csharp
using HalconDotNet;

/// <summary>
/// 对指定ROI区域进行Emphasize对比度增强
/// </summary>
/// <param name="imagePath">图像文件路径</param>
/// <param name="row1">ROI左上角行坐标</param>
/// <param name="col1">ROI左上角列坐标</param>
/// <param name="row2">ROI右下角行坐标</param>
/// <param name="col2">ROI右下角列坐标</param>
/// <param name="maskWidth">Emphasize掩膜宽度，范围[3,15]奇数，默认7</param>
/// <param name="maskHeight">Emphasize掩膜高度，范围[3,15]奇数，默认7</param>
/// <param name="factor">增强因子，范围[0.3,2.0]，默认1.0</param>
/// <returns>增强后的图像对象</returns>
public static HObject RoiEmphasizeEnhance(
    string imagePath,
    double row1, double col1, double row2, double col2,
    int maskWidth = 7, int maskHeight = 7, double factor = 1.0)
{
    // 参数约束校验
    maskWidth = Math.Max(3, Math.Min(15, maskWidth));
    maskHeight = Math.Max(3, Math.Min(15, maskHeight));
    if (maskWidth % 2 == 0) maskWidth += 1;
    if (maskHeight % 2 == 0) maskHeight += 1;
    factor = Math.Max(0.3, Math.Min(2.0, factor));

    HObject ho_Image, ho_ROI, ho_ImageReduced, ho_ImageEmphasized;

    // 读取图像
    HOperatorSet.ReadImage(out ho_Image, imagePath);

    // 生成矩形ROI
    HOperatorSet.GenRectangle1(out ho_ROI, row1, col1, row2, col2);

    // 将图像域限定到ROI区域
    HOperatorSet.ReduceDomain(ho_Image, ho_ROI, out ho_ImageReduced);

    // 对ROI区域进行Emphasize对比度增强
    HOperatorSet.Emphasize(ho_ImageReduced, out ho_ImageEmphasized, maskWidth, maskHeight, factor);

    // 释放中间变量
    ho_Image.Dispose();
    ho_ROI.Dispose();
    ho_ImageReduced.Dispose();

    return ho_ImageEmphasized;
}
```

## 调用示例

```csharp
// 示例：对图像的指定区域进行对比度增强
HObject result = RoiEmphasizeEnhance(
    imagePath: "D:/datasets/jiazhua/20260311Data/模板/Image_20260311140159256.bmp",
    row1: 824.116, col1: 1332.3,
    row2: 1003.53, col2: 1604.87,
    maskWidth: 7,
    maskHeight: 7,
    factor: 1.0
);

// 使用完毕后释放
result.Dispose();
```

## 算子流程概要
1. `ReadImage` — 读取图像
2. `GenRectangle1` — 生成矩形ROI
3. `ReduceDomain` — 将图像域缩减到ROI
4. `Emphasize` — 对ROI区域进行对比度增强

## 注意事项
- 确保输入图像路径有效且图像文件存在
- ROI坐标不应超出图像边界
- Emphasize的掩膜尺寸必须为奇数，代码中已包含自动修正逻辑
- 返回的HObject使用完毕后需调用Dispose()释放资源
