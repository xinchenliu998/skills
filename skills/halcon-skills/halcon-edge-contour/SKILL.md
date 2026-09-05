---
name: halcon-edge-contour
description: >-
  HALCON subpixel-precise edge and line extraction, XLD contour processing,
  segmentation, merging, and fitting (line/circle/ellipse/rectangle), and XLD
  shape features. Use this skill whenever a HALCON/HDevelop task needs subpixel
  accuracy, free-form edge/contour measurement, or fitting a known shape to edges
  — edges_sub_pix / edges_color_sub_pix, lines_gauss, zero_crossing_sub_pix,
  segment_contours_xld, select_contours_xld / select_shape_xld,
  union_*_contours_xld, fit_line_contour_xld / fit_circle_contour_xld /
  fit_ellipse_contour_xld / fit_rectangle2_contour_xld, or any XLD shape
  feature (area_center_xld, diameter_xld, orientation_xld). Use it when pixel
  precision isn't enough and the object has a clear edge, or when choosing the
  right edge/line operator (pixel-precise vs subpixel, edges_sub_pix vs
  lines_gauss). Applies to 2D as well as color images.
---

# HALCON 亚像素边缘、线与轮廓

> 定位：把"清晰灰度/颜色过渡"变成**亚像素精度**的 XLD 轮廓，再做分割、合并、拟合、特征提取。
> 与像素级（`sobel_amp`/`edges_image` 见 `halcon-image-preprocessing`）相对：这里是亚像素级。
> 编写规范见 `../_authoring/`（conventions.md 为精简总结；完整规范在 halcon_skill.md；脚本格式/CLI 见同名 *_reference.md）。

---

## 一、一句话选型

| 需求 | 首选算子 | 说明 |
|---|---|---|
| 亚像素边（开放/闭合） | `edges_sub_pix` | 最常用；`'lanser2'`/`'canny'` |
| 彩色亚像素边 | `edges_color_sub_pix` | 多通道 |
| 亚像素阈值 | `threshold_sub_pix` | 光照稳定时快替代 |
| 带宽度细线（ridge） | `lines_gauss`（/`lines_facet`/`lines_color`） | 线越宽 `Sigma` 越大 |
| 医疗零交叉 | `zero_crossing_sub_pix` + `derivate_gauss('laplace')` | 不"压平"曲线 |
| 分段成线/圆/椭圆 | `segment_contours_xld` | `'lines'`/`'lines_circles'`/`'lines_ellipses'` |
| 拟合已知形状 | `fit_line/circle/ellipse/rectangle2_contour_xld` | `'tukey'` 抗离群点 |
| 合并相邻/共线/共圆 | `union_adjacent/collinear/cocircular/cotangential_contours_xld` | 提取完整形状 |
| 轮廓特征 | `area_center_xld`/`diameter_xld`/`orientation_xld`/`smallest_circle_xld` | 未知形状 |

---

## 二、提取边缘/线

```hdevelop
* 亚像素边（递归滤波 lanser2 大平滑不增耗时；canny 高斯）
edges_sub_pix (Image, Edges, 'lanser2', 0.5, 8, 50)
* 彩色版
edges_color_sub_pix (ImageColor, Edges, 'canny', 0.7, 10, 60)
* 细线（Sigma 决定检测线宽：线越宽 Sigma 越大）
lines_gauss (Image, Lines, 1.5, 2, 8, 'light', 'true', 'bar-shaped', 'true')
```
- 属性读取：点属性 `get_contour_attrib_xld`（`'angle'`/`'width_left'`/`'width_right'`/`'contrast'`/`'response'`）；整体属性 `get_contour_global_attrib_xld`；查可用 `query_contour_attribs_xld`。
- 世界坐标：`contour_to_world_plane_xld (Contours, CT, CamParam, Pose, Scale)`。
- **加速**：先用区域处理（`fast_threshold`+`boundary`+`clip_region_rel`+`dilation_circle`+`reduce_domain`）限定 ROI，再在 ROI 内亚像素提取。
- 细节坑：`lines_gauss` 输出是"边缘对构成的线"，不是拟合出的 XLD 线。

---

## 三、筛选 / 合并 / 简化
- 筛选：`select_shape_xld`（~30 种形状特征）、`select_contours_xld`（按 `'contour_length'`/曲率/方向）、`select_xld_point`（交互）。
- 合并：`union_collinear_contours_xld`（共线）、`union_cocircular_contours_xld`（共圆）、`union_adjacent_contours_xld`（相邻拼接）、`union_cotangential_contours_xld`（相切）。
- 简化：`shape_trans_xld`（最小外接圆/等价椭圆/凸包/最小外接矩形）。
- 闭合轮廓集合运算：`intersection/difference/union2_closed_contours_xld`(`_polygons_xld`)。

---

## 四、分段与拟合
```hdevelop
* 分段
segment_contours_xld (Edges, Split, 'lines_circles', 6, 4, 4)
* 查每段形状（1=圆/椭圆，0=线）
get_contour_global_attrib_xld (Split, 'cont_approx', Attrib)
* 据形状拟合（'tukey'/'ahuber' 抗离群；'regression' 快速）
fit_line_contour_xld (Split, 'tukey', -1, 0, 2, Row, Col, Phi, Dist)
fit_circle_contour_xld (Circles, 'algebraic', -1, 2, 0, Row, Col, Radius, Phi, Theta, N)
fit_ellipse_contour_xld (Ellipse, 'fitzgibbon', -1, 2, 0, Row, Col, Phase, Ra, Rb, Phi)
fit_rectangle2_contour_xld (Rects, 'tukey', -1, 2, 0, Row, Col, Phi, L1, L2)
```
- 重新生成可视化轮廓：`gen_contour_polygon_xld`/`gen_circle_contour_xld`/`gen_ellipse_contour_xld`/`gen_rectangle2_contour_xld`。
- 只对直线，可用 `gen_polygons_xld ('ramer')` + `split_contours_xld`。

---

## 五、未知形状特征（点到点/区域）
`area_center_xld` `diameter_xld` `elliptic_axis_xld` `length_xld` `orientation_xld` `smallest_circle_xld` `smallest_rectangle1/2_xld`。
- 自相交检验：`test_self_intersection_xld`；对应"点式"算子：`area_center_points_xld`/`moments_points_xld`/`orientation_points_xld` 等。
- 距离：`distance_contours_xld`、`distance_pp`、`dist_ellipse_contour_xld`。

---

## 六、常见陷阱与最佳实践
1. 拟合算法选 `'tukey'`/`'ahuber'` 抗离群点，`'regression'` 最速但受离群影响大。
2. `edges_image` 与 `edges_sub_pix` 的后备：`edges_image` 已含 NMS+滞后阈值，像素级；亚像素切边缘用 `sobel_amp` + `skeleton`。
3. 用 ROI 精确定位想要的轮廓（轮廓提取耗时）。
4. 彩色：`edges_color`/`edges_color_sub_pix`；`lines_color` 用于彩色线。
5. 宽线建议先 `zoom_image_factor` 缩图省时。
6. 高精度：先离线 `radiometric_self_calibration` + `lut_trans` 线性化响应。
7. 不"压平"外缘曲线：用 `derivate_gauss(...,'laplace')` + `zero_crossing_sub_pix` 替代 `edges_sub_pix`。
8. 线裂纹/环形展开：`lines_gauss` 提取 + 极坐标 `polar_trans_image_ext` 展开。

---

## 七、引用
- 中文算子总览：`references/ops_06_XLD.md`
- 逐算子签名/默认值：见 `references/ref_OPERATOR_REFERENCE.md`（XLD 章）。
- 关联：`halcon-measuring-metrology`（拟合结果做尺寸）、`halcon-image-preprocessing`（像素级边缘/分割）、`halcon-3d-vision`（轮廓→世界）。


---

## 用例参考（example_*.md）

本 skill 目录下 `references/` 含以下项目里抽出的真实用例（按主题归档，可直接借鉴实现思路/算子组合）：

- `references/example_edges_detection.md`
- `references/example_line_detection.md`
- `references/example_xld_contour_fitting.md`
