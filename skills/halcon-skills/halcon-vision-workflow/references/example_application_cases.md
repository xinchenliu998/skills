# Halcon 综合应用案例技能手册

> 学习来源: `Applications/` 全系列
> 涵盖Task20：综合应用案例、算子组合策略、工业场景解决方案

---

## 一、工业视觉典型场景→技能索引

| 场景 | 核心技能 | 对应skill文件 |
|---|---|---|
| **定位/对位** ⭐ | 形状匹配+仿射变换 | `shape_matching.md` + `geometric_transforms.md` |
| **尺寸测量** | 1D测量/2D计量/XLD拟合 | `measuring_metrology.md` + `xld_contour_fitting.md` |
| **缺陷检测** ⭐ | Blob差分/纹理/FFT | `defect_inspection.md` + `fft_processing.md` |
| **完整性检查** | Blob计数+多ROI | `completeness_check.md` |
| **OCR/码读取** | OCR+条码/二维码 | `ocr_barcode.md` |
| **圆/孔检测** ⭐ | 边缘+XLD圆拟合 | `edges_detection.md` + `xld_contour_fitting.md` |
| **颜色分类** | 颜色空间+分类器 | `image_enhancement.md` |
| **3D检测** | 点云+高度图 | `3d_vision.md` + `camera_calibration.md` |

---

## 二、综合处理流程模板 ⭐

### 通用工业视觉检测流程
```
1. 图像采集 → read_image
2. 预处理:
   - 增强: emphasize/scale_image_max (image_enhancement.md)
   - 去噪: gauss_filter/median_image (image_smoothing.md)
   - ROI裁剪: reduce_domain
3. 定位:
   - 形状匹配: find_shape_model (shape_matching.md)
   - 或Blob定位: threshold→connection→select_shape
4. 对齐:
   - vector_angle_to_rigid → affine_trans (geometric_transforms.md)
5. 检测:
   - 尺寸: measure_pos/metrology (measuring_metrology.md)
   - 缺陷: blob差分/纹理 (defect_inspection.md)
   - 完整性: 计数/面积 (completeness_check.md)
6. 判定: OK/NG
7. 输出结果
```

---

## 三、典型案例组合

### 案例1: 引脚检测(定位+测量) ⭐
```
1. shape_matching定位芯片 → Row, Col, Angle
2. vector_angle_to_rigid对齐
3. 在对齐图上设置多个measure_rectangle
4. measure_pairs测量引脚宽度/间距
5. 判断是否在公差范围内
```

### 案例2: PCB缺陷检测(差分+Blob)
```
1. shape_matching定位PCB
2. affine_trans对齐到标准位置
3. abs_diff_image与标准图比较
4. threshold提取差异区域
5. select_shape过滤噪声
6. 判定缺陷类型(缺件/多件/偏移)
```

### 案例3: 圆孔尺寸测量(边缘+拟合) ⭐
```
1. threshold粗定位孔区域
2. edges_sub_pix亚像素边缘
3. select_contours_xld按长度筛选
4. fit_circle_contour_xld('atukey')圆拟合
5. 输出圆心坐标+半径
6. 可选: metrology进一步精测
```

### 案例4: 标签OCR(定位+识别)
```
1. shape_matching定位标签区域
2. affine_trans_region裁剪文字区域
3. threshold字符分割
4. sort_region排序
5. do_ocr_multi_class_mlp识别
```

### 案例5: 环形缺陷检测(极坐标+FFT)
```
1. 找圆(fit_circle_contour_xld)
2. polar_trans_image_ext环形展开
3. FFT滤波或deviation_image
4. threshold提取缺陷
```

---

## 四、算子组合速查表

### 图像→区域
| 输入 | 方法 | 输出 |
|---|---|---|
| 图像 | `threshold` | 区域 |
| 图像 | `dyn_threshold` | 区域 |
| 图像 | `auto_threshold` | 区域 |
| 图像 | `var_threshold` | 区域 |

### 图像→XLD轮廓
| 输入 | 方法 | 输出 |
|---|---|---|
| 图像 | `edges_sub_pix` | XLD |
| 图像 | `threshold_sub_pix` | XLD |
| 图像 | `lines_gauss` | XLD |

### 区域→特征
| 输入 | 方法 | 输出 |
|---|---|---|
| 区域 | `area_center` | 面积+中心 |
| 区域 | `select_shape` | 筛选后区域 |
| 区域 | `smallest_circle` | 最小外接圆 |
| 区域 | `smallest_rectangle2` | 最小外接矩形 |

### XLD→几何参数
| 输入 | 方法 | 输出 |
|---|---|---|
| XLD | `fit_circle_contour_xld` | 圆(Row,Col,R) |
| XLD | `fit_line_contour_xld` | 直线(端点) |
| XLD | `fit_ellipse_contour_xld` | 椭圆 |

### 匹配→位姿
| 输入 | 方法 | 输出 |
|---|---|---|
| 图像+模型 | `find_shape_model` | Row,Col,Angle,Score |
| 位姿 | `vector_angle_to_rigid` | HomMat2D |
| HomMat2D | `affine_trans_image/region/contour` | 对齐结果 |

---

## 五、性能优化策略

| 策略 | 方法 | 加速比 |
|---|---|---|
| **ROI限制** ⭐ | `reduce_domain`减小搜索区域 | 2~10x |
| **金字塔** | NumLevels=4~5 | 2~5x |
| **降分辨率** | `zoom_image_factor(0.5)` | 4x |
| **贪婪搜索** | Greediness=0.8~0.9 | 1.5~2x |
| **多线程** | `set_system('parallelize_operators','true')` | 2~4x |
| **模型预加载** | `read_shape_model`启动时加载 | 避免重复创建 |

---

## 六、20个Skill文件总索引

| # | Skill文件 | 核心能力 |
|---|---|---|
| 01 | `edges_detection.md` | 边缘检测(Canny/Sobel/亚像素) |
| 02 | `image_enhancement.md` | 图像增强(对比度/均衡化/颜色) |
| 03 | `image_smoothing.md` | 平滑去噪(高斯/中值/双边) |
| 04 | `fft_processing.md` | FFT频域滤波+纹理分析+角点 |
| 05 | `line_detection.md` | 线检测+极坐标变换 |
| 06+07 | `xld_contour_fitting.md` | XLD轮廓拟合+操作 |
| 08 | `morphology_operations.md` | 形态学(开闭/膨胀/腐蚀) |
| 09 | `segmentation_threshold.md` | 阈值分割+区域处理 |
| 10 | `region_features.md` | 区域特征+选择 |
| 11 | `shape_matching.md` | 形状匹配(定位) |
| 12 | `correlation_deformable_matching.md` | NCC+变形匹配 |
| 13 | `measuring_metrology.md` | 1D测量+2D计量 |
| 14 | `camera_calibration.md` | 相机标定+坐标转换 |
| 15 | `defect_inspection.md` | 缺陷检测(纹理/Blob/珠) |
| 16 | `ocr_barcode.md` | OCR+条码/二维码 |
| 17 | `completeness_check.md` | 完整性检查 |
| 18 | `geometric_transforms.md` | 几何变换+仿射+投影 |
| 19 | `3d_vision.md` | 3D视觉+表面匹配 |
| 20 | `application_cases.md` | 综合应用案例(本文件) |
