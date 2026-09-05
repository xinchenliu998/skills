---
name: example-halcon-skill
title: Halcon Vision Skill 索引
description: 项目中所有skill文件的name和description索引
---

# Halcon Vision Skill 索引

## 编排入口

| name | description |
|------|-------------|
| center_localization_orchestrator | 中心定位编排控制器，协调多策略定位目标中心 |
| stray_light_orchestrator | 杂光检测编排入口，逐光源检测光刺长度和数量 |

## 中心定位流程

| name | description |
|------|-------------|
| step0_image_preprocess | 图像预处理+阈值预检 |
| step1_circle_strategy | 圆策略(判断+打分+自反思) |
| step2_rectangle_strategy | 矩形策略(判断+打分+自反思) |
| step3_centroid_strategy | 区域重心(判断+打分+自反思) |
| step3b_specular_filter | 镜面反光过滤(始终执行) |
| step4_edge_strategy | Edge策略(使用CleanImageROI+判断+打分+自反思) |
| step5_global_reflection | 全局反思+置信度评分(含光斑场景规则) |
| center_localization_coarse_analysis | 旧版粗分析(已拆分，仅供参考) |
| center_localization_reflection | 旧版反思(已拆分，仅供参考) |

## 杂光检测流程

| name | description |
|------|-------------|
| stray_light_step0_preprocess | 图像预处理+全局统计 |
| stray_light_step1_spot_detection | 正常光斑检测与分离 |
| stray_light_step2_stray_classify | 杂光分类 |
| stray_light_step3_fft_analysis | FFT频域分析 |
| stray_light_step4_judgment | 综合判定+置信度评分 |

## 图像处理基础

| name | description |
|------|-------------|
| image_enhancement | 图像增强与预处理，含光照校正和对比度增强 |
| image_smoothing | 高斯/中值/双边/引导滤波降噪 |
| segmentation_threshold | 阈值分割与区域处理，动态阈值分割不均匀光照 |
| edges_detection | 边缘检测算子，涵盖亚像素级边缘检测方法 |
| region_features | 区域特征与选择，含圆度、凸度等特征提取筛选 |
| morphology_operations | 灰度/二值形态学开闭运算、腐蚀膨胀去噪填孔 |
| roi_emphasize_enhance | ROI区域对比度增强、图像局部Emphasize处理 |

## 形状与轮廓

| name | description |
|------|-------------|
| shape_matching | Shape-Based Matching完整流程 |
| correlation_deformable_matching | 模板匹配与变形匹配 |
| xld_contour_fitting | XLD圆/线/椭圆/矩形拟合、轮廓分割合并 |
| geometric_transforms | 几何变换、仿射变换、投影变换 |

## 特征检测与分析

| name | description |
|------|-------------|
| defect_inspection | 纹理检测模型、FFT带通滤波、形态学差分缺陷检测 |
| line_detection | lines_gauss线裂纹检测、极坐标环形展开变换 |
| fft_processing | FFT频域处理与纹理分析，含带通滤波划痕检测 |
| measuring_metrology | 1D边缘测量、2D计量圆线矩形拟合尺寸测量 |

## 识别与检测

| name | description |
|------|-------------|
| ocr_barcode | DataMatrix二维码、条码识别、OCR字符识别 |
| completeness_check | 完整性检测、缺失零件检测 |

## 3D与标定

| name | description |
|------|-------------|
| camera_calibration | 相机内参标定、手眼标定、像素转世界坐标 |
| focal_length_triangle | 焦距三角关系计算：相似三角形法 f/L5=L2/L1，无需标定板描述文件 |
| chessboard_corner_detection | 棋盘格角点多策略检测(边缘交叉+梯度突变+象限棋盘+鞍点)+焦距计算，含踩坑总结 |
| libcbdetect_chessboard_corners | libcbdetect棋盘格角点检测算法库深度解析：多尺度模板卷积+种子生长+能量最小化 |
| 3d_vision | 3D点云处理、表面匹配、Sheet-of-Light激光扫描 |

## 学习与参考

| name | description |
|------|-------------|
| halcon_skill_learning_plan | Halcon技能学习计划路线图 |
| application_cases | 工业视觉综合案例、引脚/PCB/圆孔/标签检测 |

*生成时间: 2026-05-14*