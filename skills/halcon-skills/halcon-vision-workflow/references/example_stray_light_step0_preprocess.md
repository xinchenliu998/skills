# Step 0: 杂光检测 - 图像预处理

## 目标
读取图像并进行基础预处理，为后续逐光源分析提供输入图像。

## 输入
- 图像路径（JPG格式，2624x2624 binning后）

## 处理流程

### 0.1 图像读取与灰度转换
```csharp
HOperatorSet.ReadImage(out HObject image, imagePath);
HOperatorSet.CountChannels(image, out HTuple channels);
if (channels.I > 1)
{
    HOperatorSet.Rgb1ToGray(image, out HObject gray);
    image.Dispose();
    image = gray;
}
HOperatorSet.GetImageSize(image, out HTuple width, out HTuple height);
// 预期: 2624 x 2624
```

### 0.2 全局统计（仅供参考，不作为判定依据）
```csharp
// 基本统计（辅助信息，非判定依据）
HOperatorSet.Intensity(fullRoi, image, out HTuple meanGray, out _);
HOperatorSet.MinMaxGray(fullRoi, image, 0, out HTuple minGray, out HTuple maxGray, out _);
```

### 0.3 图像质量预检
- 图像尺寸是否为2624x2624
- 图像是否过暗(meanGray < 10)或过亮(meanGray > 200) → 拍摄异常
- 如果预检失败，提前返回错误

## 输出
- `image`: 灰度图像 (HObject)
- `width`, `height`: 图像尺寸
- `meanGray`: 全局均值（仅参考）

## 自反思
- 图像尺寸是否匹配2624x2624?
- 是否成功转为灰度?
- 全局均值是否在合理范围(20-80)?
