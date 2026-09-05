# HALCON 算子分类详解：Matrix（矩阵运算）

> **HALCON 版本**：26.05.0.0 Progress
> **算子数量**：约 60 个
> **一级分类目录**：`toc_matrix.html`
> **学习层级**：L2–L3（按需查阅，底层数学）

---

## 1. 概述

Matrix 分类提供了 HALCON 的**矩阵运算能力**——但这不是简单的数组运算（那是 Tuple 分类），而是真正的"线性代数矩阵"。HALCON 的 Matrix 是 `HMatrix` 句柄类型（不同于元组 `HTuple`），专门用于：

1. **批量数值计算**：N×N 矩阵运算
2. **线性方程组求解**：`solve_matrix`（Ax = b）
3. **特征分解**：SVD、QR、LU
4. **特征值问题**：`eigenvalues_*_matrix`
5. **主成分分析（PCA）**：`principal_comp`
6. **几何/物理计算**：惯性张量、最小二乘拟合
7. **机器学习底层**：特征归一化、协方差矩阵

该分类分为 8 个子分类：Access / Arithmetic / Creation / Decomposition / Eigenvalues / Features / File / Solve。

**与 Tuple 的关键区别**：
- `HTuple`：标量/数组（任意维度），用于通用数据
- `HMatrix`：N×N 矩阵，专为线性代数设计

---

## 2. 应用场景

### 场景 1：相机标定内参计算（Calibration 底层）

`camera_calibration` 内部就是用矩阵运算：构建像素-世界点对应关系 → 构建法方程 A·x = b → `solve_matrix` 求解内参 → 用 SVD 检查条件数。

### 场景 2：点云配准（ICP 初值求解）

两个点云片段 → 提取对应点对 → 构造 4×4 变换矩阵的法方程 → `solve_matrix` 求解旋转+平移 → 用于 ICP 的初值。

### 场景 3：主成分分析（PCA 降维）

高维特征（如 64×64 图像 = 4096 维）→ `principal_comp` 计算协方差矩阵的特征向量 → 取前 N 个主成分 → 投影到低维空间 → 用于分类、可视化。

### 场景 4：多项式曲面拟合（高度图生成）

已知 (x, y, z) 散点 → 构造多项式系数矩阵 A → `solve_matrix` 求解系数向量 → 用多项式 `z = f(x, y)` 生成完整高度图。

### 场景 5：物理仿真（机器人动力学）

机械臂的惯性张量 → 矩阵乘法计算动能 → 特征分解找主惯性轴 → 用于动力学仿真。

### 场景 6：批量矩阵运算（机器学习模型推理）

神经网络的一层 → `mult_matrix` 实现 W·x + b → 批量计算 N 个样本。

---

## 3. 子分类详解

### 3.1 Creation（矩阵创建）— 约 8 算子

| 算子 | 用途 |
|------|------|
| `create_matrix` | 创建矩阵（全 0） |
| `copy_matrix` | 复制 |
| `set_full_matrix` | 设置全部元素（从元组） |
| `set_sub_matrix` | 设置子矩阵（从另一个矩阵） |
| `set_value_matrix` | 设置单元素 |
| `set_diagonal_matrix` | 设置对角线 |
| `repeat_matrix` | 矩阵块平铺（类似 numpy tile） |
| `gen_matrix` | 通过表达式生成（高级） |

### 3.2 Access（矩阵访问）— 约 5 算子

| 算子 | 用途 |
|------|------|
| `get_full_matrix` | 拿全部元素（→ 元组） |
| `get_sub_matrix` | 拿子矩阵（→ 新矩阵） |
| `get_value_matrix` | 拿单元素 |
| `get_diagonal_matrix` | 拿对角线 |
| `get_size_matrix` | 拿尺寸 |

### 3.3 Arithmetic（矩阵算术）— 约 14 算子

每个都有 `*_mod` 即时（in-place）版本：

| 算子 | 用途 | 对应 `*_mod` |
|------|------|-------------|
| `add_matrix` | C = A + B | `add_matrix_mod` |
| `sub_matrix` | C = A - B | `sub_matrix_mod` |
| `mult_matrix` | C = A · B（矩阵乘法）| `mult_matrix_mod` |
| `mult_element_matrix` | C = A ⊙ B（逐元素乘）| `mult_element_matrix_mod` |
| `div_element_matrix` | C = A ⊘ B（逐元素除）| `div_element_matrix_mod` |
| `pow_element_matrix` | C = A ⌐ B（逐元素幂）| `pow_element_matrix_mod` |
| `scale_matrix` | C = A * s（标量乘）| `scale_matrix_mod` |
| `abs_matrix` | C = |A|（绝对值）| `abs_matrix_mod` |
| `min_matrix` | 元素级 min | `min_matrix_mod` |
| `max_matrix` | 元素级 max | `max_matrix_mod` |
| `mean_matrix` | 元素级 mean | `mean_matrix_mod` |
| `norm_matrix` | 元素级 norm | `norm_matrix_mod` |
| `transpose_matrix` | C = Aᵀ | `transpose_matrix_mod` |
| `invert_matrix` | C = A⁻¹ | `invert_matrix_mod` |

### 3.4 Decomposition（矩阵分解）— 约 5 算子

| 算子 | 用途 |
|------|------|
| `decompose_matrix` | LU 分解（带部分主元） |
| `orthogonal_decompose_matrix` | QR 分解（Householder 反射） |
| `svd_matrix` | SVD 分解：A = U·S·Vᵀ |
| `principal_comp` | PCA 主成分分析 |
| `generalized_eigenvalues_symmetric_matrix` | 广义对称特征值 |

### 3.5 Eigenvalues（特征值）— 约 4 算子

| 算子 | 用途 |
|------|------|
| `eigenvalues_general_matrix` | 一般矩阵特征值（返回复数） |
| `eigenvalues_symmetric_matrix` | 对称矩阵特征值（返回实数） |
| `generalized_eigenvalues_symmetric_matrix` | 广义对称特征值 |
| `generalized_eigenvalues_general_matrix` | 广义一般特征值 |

### 3.6 Features（矩阵特征）— 约 6 算子

| 算子 | 用途 |
|------|------|
| `determinant_matrix` | 行列式 |
| `mean_matrix` | 元素均值 |
| `sum_matrix` | 元素总和 |
| `norm_matrix` | 元素范数（L1/L2/L∞） |
| `min_matrix` | 全局最小值 |
| `max_matrix` | 全局最大值 |

### 3.7 Solve（线性方程组求解）— 约 2 算子

| 算子 | 用途 |
|------|------|
| `solve_matrix` | 求解 A · X = B |
| `generalized_solve_matrix` | 广义求解 |

### 3.8 File（文件 I/O）— 约 2 算子

| 算子 | 用途 |
|------|------|
| `read_matrix` | 读取（ASCII 或二进制） |
| `write_matrix` | 写出 |

---

## 4. 核心算子详解

### 4.1 `create_matrix` / `set_full_matrix` / `get_full_matrix`

```hdevelop
* 创建 3×4 全 0 矩阵
create_matrix(3, 4, 0.0, MatrixID)

* 设置全部元素（从元组）
Vals := [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
set_full_matrix(MatrixID, Vals)

* 拿回元组
get_full_matrix(MatrixID, ValuesOut)
```

### 4.2 `set_sub_matrix`

```hdevelop
* 创建子矩阵
create_matrix(2, 2, 0.0, SubMat)
Vals := [1, 2, 3, 4]
set_full_matrix(SubMat, Vals)

* 把子矩阵插入到目标矩阵的 (Row, Col) 位置
set_sub_matrix(TargetMat, SubMat, 1, 1)
```

### 4.3 `mult_matrix`（矩阵乘法）

```hdevelop
* A · B = C（注意：HALCON 默认按数学约定）
mult_matrix(A, B, 'AB', C)
* 'AB' = A·B
* 'BA' = B·A
* 'ATB' = Aᵀ·B
* 'ABT' = A·Bᵀ
* 'ATBT' = Aᵀ·Bᵀ
* 'identity' = A（如 B 是单位矩阵）
```

### 4.4 `mult_element_matrix`（逐元素乘）

```hdevelop
mult_element_matrix(A, B, C)
* C[i,j] = A[i,j] * B[i,j]
* 与 numpy 的 A * B 等价（不是 numpy 的 A @ B）
```

### 4.5 `transpose_matrix`

```hdevelop
transpose_matrix(A, ATrans)
* ATrans[i,j] = A[j,i]
```

### 4.6 `invert_matrix`

```hdevelop
invert_matrix(A, AInv)
* 等价于 solve_matrix(A, Identity)
* 但 invert 内部用 LU 分解，更稳定
```

### 4.7 `solve_matrix`（最常用）

```hdevelop
* 求解线性方程组 A · X = B
solve_matrix(A, 'general', 0, B, X)
* Mode：'general' / 'upper_triangular' / 'lower_triangular' / 'symmetric' / 'symmetric_posdef' / 'tridiagonal' / 'cholesky'
* Epsilon：奇异阈值（接近 0 的奇异值视为 0）
* X = A⁻¹ · B
```

### 4.8 `svd_matrix`

```hdevelop
* SVD：A = U · S · Vᵀ
svd_matrix(A, 'full', 'both', U, S, V)
* 'full' / 'reduced' / 'values_only'
* 'both' = 计算 U 和 V；'left' = 只 U；'right' = 只 V
* S 是对角线元素（奇异值）
```

### 4.9 `principal_comp`（PCA）

```hdevelop
* 主成分分析
principal_comp(Matrix, 'columns', 'centered', false, InfoPerComp, Trans, Mean, Projected)
* Matrix：N×M（行=样本，列=特征）
* Trans：转换矩阵（M×M），列向量是主成分
* Mean：每列均值
* Projected：投影后的低维表示（N×M）
```

### 4.10 `decompose_matrix`（LU）

```hdevelop
* LU 分解：A = P · L · U
decompose_matrix(A, 'lu', LU, Permutation, Info)
* Info = 0 表示成功，非 0 表示奇异
```

### 4.11 `orthogonal_decompose_matrix`（QR）

```hdevelop
* QR 分解：A = Q · R
orthogonal_decompose_matrix(A, 'qr', Q, R)
```

### 4.12 `eigenvalues_symmetric_matrix`

```hdevelop
* 对称矩阵特征值分解
eigenvalues_symmetric_matrix(ASym, 'jaccobi', Eigenvalues)
* 'jaccobi' / 'householder' / 'tridiagonal' / 'ql_implicit' / 'ql_explicit'
* 返回实数特征值
```

### 4.13 `eigenvalues_general_matrix`

```hdevelop
* 一般矩阵特征值（返回复数）
eigenvalues_general_matrix(A, 'jacobi', EigenvaluesReal, EigenvaluesImag)
```

### 4.14 `determinant_matrix`

```hdevelop
determinant_matrix(A, Det)
* 行列式（判断矩阵是否可逆：Det ≈ 0）
```

### 4.15 `norm_matrix`

```hdevelop
norm_matrix(A, 'frobenius', Norm)
* 'frobenius' / 'infinity' / 'one' / 'two'（谱范数）
* 'two' = 最大奇异值
```

### 4.16 `scale_matrix`

```hdevelop
scale_matrix(A, Factor, AScaled)
* AScaled[i,j] = A[i,j] * Factor
```

### 4.17 `repeat_matrix`

```hdevelop
* 把矩阵块平铺（类似 numpy tile）
create_matrix(2, 2, 1.0, A)
repeat_matrix(A, 3, 4, ATiled)
* 3×4 平铺 → 6×8 矩阵，每个位置都是 A
```

### 4.18 `read_matrix` / `write_matrix`

```hdevelop
write_matrix(A, 'ascii', 'matrix.dat')
read_matrix('matrix.dat', 'ascii', MatrixID)
```

### 4.19 `*_mod` 系列（即时版本）

```hdevelop
* 所有 *_mod 算子都是 in-place，节省内存
add_matrix_mod(A, B, A)  * A = A + B（覆盖 A）
mult_matrix_mod(A, B, 'AB', A)
transpose_matrix_mod(A)
* 注意：输入和输出是同一个矩阵！
```

---

## 5. HDevelop 示例代码

### 示例 1：基本矩阵运算

```hdevelop
* Matrix_Basic.hdev
* 演示矩阵创建、加减乘、转置、求逆

* 创建 2×2 矩阵
create_matrix(2, 2, 0.0, A)
set_full_matrix(A, [1, 2, 3, 4])  * [[1,2],[3,4]]

create_matrix(2, 2, 0.0, B)
set_full_matrix(B, [5, 6, 7, 8])  * [[5,6],[7,8]]

* 加法
add_matrix(A, B, Sum)
get_full_matrix(Sum, SumVals)  * [6,8,10,12]

* 乘法（矩阵乘）
mult_matrix(A, B, 'AB', Prod)
get_full_matrix(Prod, ProdVals)  * [19,22,43,50]

* 转置
transpose_matrix(A, ATrans)
get_full_matrix(ATrans, ATransVals)  * [1,3,2,4]

* 求逆
invert_matrix(A, AInv)
get_full_matrix(AInv, AInvVals)  * [[-2, 1], [1.5, -0.5]]

* 验证：A · A⁻¹ = I
mult_matrix(A, AInv, 'AB', Check)
get_full_matrix(Check, CheckVals)  * 应该接近 [1,0,0,1]
```

### 示例 2：解线性方程组（最小二乘法）

```hdevelop
* Matrix_Solve_Linear.hdev
* 求解过定方程组 A · x = b（最小二乘解）

* 构造：3 个方程，2 个未知数（超定）
create_matrix(3, 2, 0.0, A)
set_full_matrix(A, [1, 1, 1, 2, 1, 3])

create_matrix(3, 1, 0.0, B)
set_full_matrix(B, [6, 9, 11])

* 求解 A · X = B
solve_matrix(A, 'general', 0, B, X)

* 拿回 X（最小二乘解）
get_full_matrix(X, XVals)
* XVals 应该接近 [4.5, 2.0]（即 4.5 + 2x ≈ y）
```

### 示例 3：PCA 主成分分析

```hdevelop
* Matrix_PCA.hdev
* 演示主成分分析降维

* 构造样本矩阵：5 个样本，每个 3 维
* 例如：[身高, 体重, 年龄]
create_matrix(5, 3, 0.0, Data)
Vals := [
    170, 65, 30,
    180, 75, 35,
    165, 55, 25,
    175, 70, 40,
    160, 60, 28
]
set_full_matrix(Data, Vals)

* PCA（centered = 减去均值）
principal_comp(Data, 'columns', 'centered', true, Info, Trans, Mean, Projected)

* 拿转换矩阵（主成分）
get_full_matrix(Trans, TransVals)
* Trans 是 3×3，每一列是一个主成分方向

* 拿均值向量
get_full_matrix(Mean, MeanVals)

* 拿投影结果（5×3，维度未变，但按主成分排序）
get_full_matrix(Projected, ProjVals)

* 取前 2 个主成分（降维）
create_matrix(5, 2, 0.0, Reduced)
create_matrix(2, 2, 0.0, Trans2x2)
* 取 Trans 的前 2 列...
```

### 示例 4：SVD 分解与应用

```hdevelop
* Matrix_SVD.hdev
* 用 SVD 做矩阵的秩近似

* 创建 4×3 矩阵
create_matrix(4, 3, 0.0, A)
Vals := [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
set_full_matrix(A, Vals)

* SVD 分解：A = U · S · Vᵀ
svd_matrix(A, 'full', 'both', U, S, V)

* 拿奇异值
get_full_matrix(S, SVals)
* SVals 是 [σ1, σ2, σ3]

* 视觉化（4×3 矩阵，秩 ≤ 3）
* 如果 σ3 接近 0，可以截断到秩 2
```

### 示例 5：多项式曲面拟合

```hdevelop
* Matrix_Polynomial_Fit.hdev
* 用 solve_matrix 做二次多项式曲面拟合

* 已知 5 个 (x, y, z) 散点
NumPoints := 5
X := [0, 1, 2, 1, 0]
Y := [0, 0, 1, 1, 2]
Z := [0, 1, 4, 2, 4]  * z = x² + y²

* 拟合 z = a0 + a1*x + a2*y + a3*x² + a4*xy + a5*y²
* 设计矩阵（6 个未知数，5 个方程 → 最小二乘）
create_matrix(NumPoints, 6, 0.0, A)
for i := 0 to NumPoints-1 by 1
    create_matrix(1, 6, 0.0, Row)
    set_full_matrix(Row, [1, X[i], Y[i], X[i]*X[i], X[i]*Y[i], Y[i]*Y[i]])
    set_sub_matrix(A, Row, i, 0)
endfor

create_matrix(NumPoints, 1, 0.0, B)
set_full_matrix(B, Z)

* 求解
solve_matrix(A, 'general', 0, B, Coeffs)
get_full_matrix(Coeffs, CoeffVals)
* 系数：[1, 0, 0, 1, 0, 1]（对应 a0=1, a3=1, a5=1）
```

### 示例 6：特征值分解（找主轴）

```hdevelop
* Matrix_Eigenvalues.hdev
* 计算协方差矩阵的特征值 → 找主方向

* 构造对称矩阵（协方差矩阵）
create_matrix(3, 3, 0.0, Cov)
Vals := [2.0, 1.0, 0.5, 1.0, 3.0, 0.8, 0.5, 0.8, 1.5]
set_full_matrix(Cov, Vals)

* 特征值分解（对称矩阵）
eigenvalues_symmetric_matrix(Cov, 'jaccobi', Eigenvalues)
* Eigenvalues 是 3 个特征值（按降序）
```

---

## 6. 典型工业流水线

### 流水线 A：相机标定（最小二乘求解内参）

```hdevelop
* 简化版：构造像素-世界对应，solve_matrix 求解

* 构造法方程 A · p = b（p 是相机参数向量）
* ...

* 求解
solve_matrix(A, 'general', 0, b, Params)

* 拿回相机参数
get_full_matrix(Params, ParamsArray)
* ParamsArray 包含焦距、主点、畸变系数等
```

### 流水线 B：点云刚体配准（最小二乘求解变换）

```hdevelop
* 已知 N 对 3D 对应点：(P_i, Q_i)
* 求解变换 T 使 Q_i ≈ T · P_i

* 构造 12×12 系数矩阵（线性化后）
* ...（构造过程略）

* 求解
solve_matrix(AMatrix, 'general', 0, BVector, XVector)

* XVector 包含旋转矩阵 9 个元素 + 平移 3 个元素
```

### 流水线 C：机器学习批量推理

```hdevelop
* 假设 W (10×3), X (N×10), b (3)
* 计算 Y = X · W + b

* 加载权重
read_matrix('weights.dat', 'ascii', W)
read_matrix('bias.dat', 'ascii', B)
read_matrix('features.dat', 'ascii', X)

* 矩阵乘法
mult_matrix(X, W, 'AB', XW)

* 加偏置（广播加）
* ... (HALCON 没有直接广播，需要重复矩阵或逐列加)
```

### 流水线 D：图像变换矩阵验证

```hdevelop
* 求解的 HomMat2D 必须满足：T · 原图坐标 = 对齐后坐标

* 构造多组对应
SourcePoints := [[10, 20], [100, 50], [200, 200]]
TargetPoints := [[12, 22], [105, 51], [198, 205]]

* 构造矩阵 A (3×6) 和 b (3×1)
* ...（展开点对为线性方程组）

* 求解
solve_matrix(A, 'general', 0, b, H)

* H 包含 6 个仿射参数（a, b, c, d, e, f）
```

---

## 7. 常见陷阱与最佳实践

### 陷阱 1：`mult_matrix` 模式混淆

```hdevelop
mult_matrix(A, B, 'AB', C)  * 数学：C = A·B（按 A 列、B 行的内积）
mult_matrix(A, B, 'BA', C)  * 数学：C = B·A
* HALCON 的字符串参数命名约定是字母顺序（先 A 后 B）
```

### 陷阱 2：`solve_matrix` 的 Mode 选择

- `'general'`：通用 LU 分解，慢但最稳定。
- `'symmetric_posdef'`：对称正定（协方差、Cholesky），快 2×。
- `'upper_triangular'` / `'lower_triangular'`：已经是三角阵，最快。
- 选错 Mode 可能导致结果错误或效率低。

**最佳实践**：知道矩阵性质就用对应 Mode，否则用 `'general'`。

### 陷阱 3：奇异矩阵的 `solve_matrix`

A 接近奇异（`det(A) ≈ 0`）时，`solve_matrix` 结果会很大、不可信。

**最佳实践**：
- 先 `determinant_matrix` 检查 |Det|
- 接近 0 时用 `svd_matrix` 截断小奇异值
- 或用岭回归：在 AᵀA 上加 λI

### 陷阱 4：`transpose_matrix` 的物理含义

矩阵转置只在**双线性形式**下与几何意义相反：
- 数学：A·x = b 描述"前向变换"
- 转置：Aᵀ·x = b' 描述"伴随变换"

**陷阱**：误用转置会导致物理含义错误。

### 陷阱 5：`invert_matrix` 在大矩阵上极慢

O(N³) 算法 + LU 分解。10×10 矩阵约 1 ms，100×100 约 10 ms，1000×1000 约 1 s。

**最佳实践**：大矩阵优先考虑 `solve_matrix(A, 'general', 0, B, X)` 替代 `X = A⁻¹ · B`（合并运算，更稳定）。

### 陷阱 6：`HMatrix` 句柄需手动释放

```hdevelop
create_matrix(3, 3, 0.0, A)
* ...使用...
* 注意：HALCON 自动 GC，但显式释放更安全
* 在 C++ 中 clear_matrix(MatrixID)
```

### 陷阱 7：`set_sub_matrix` 的位置坐标

```hdevelop
* 位置 (Row, Col) 是子矩阵左上角在目标矩阵中的位置
set_sub_matrix(Target, Sub, 1, 2)
* Sub 的 (0,0) → Target 的 (1,2)
```

### 陷阱 8：`principal_comp` 的数据布局

HALCON 的 `principal_comp` 假设：
- 每行 = 一个样本
- 每列 = 一个特征

与 numpy 的 `np.linalg.eig(cov(X.T))` 等价，但**矩阵维度需要满足**：`NumFeatures ≤ NumSamples`（否则协方差矩阵奇异）。

---

## 8. 参数调优指南

### 8.1 `solve_matrix`

| 参数 | 推荐 | 说明 |
|------|------|------|
| `Mode` | 根据矩阵性质 | `'symmetric_posdef'` 最快 + 最稳定（如果矩阵确实正定）|
| `Epsilon` | 1e-12（双精度）/ 1e-6（单精度） | 奇异阈值，小奇异值截断 |

### 8.2 `svd_matrix`

| 参数 | 推荐 | 说明 |
|------|------|------|
| Mode | `'reduced'` | 比 `'full'` 快，结果一样用于主成分分析 |
| 'reduced'：只返回 N 个非零奇异值；'full'：返回全部 |

### 8.3 `principal_comp`

| 参数 | 推荐 | 说明 |
|------|------|------|
| `'columns'` vs `'rows'` | 根据数据 | 列=特征（PCA 标准）；行=特征（罕见） |
| `'centered'` | `'centered'` | 默认减均值（标准 PCA） |
| `'normalized'` | 按需 | 除以标准差（Z-score 标准化） |

### 8.4 `*_mod` 版本选择

| 场景 | 推荐 |
|------|------|
| 内存敏感 / 大矩阵 | `*_mod` |
| 需要保留原矩阵 | 不用 `*_mod` |
| 链式运算 | `*_mod`（避免中间变量） |

---

## 9. 相关分类

- **Calibration**：相机标定的底层就是 Matrix 运算（特别是 `solve_matrix`）。
- **Transformations**：`hom_mat2d/3d` 本质就是 `HMatrix` 的 2D/3D 特殊化。
- **Tuple**：数据转换的桥梁（`HMatrix` → `HTuple`）。
- **Matching**：模板匹配的相似度计算底层是矩阵点积。
- **3D Object Model**：点云配准（ICP）底层是 `solve_matrix`。

---

## 10. 学习小结

Matrix 是"**底层数学工具**"——大多数情况下你不需要直接用，因为 HALCON 的高级 API（匹配、标定、深度学习）已经封装好了。但当遇到以下场景时必须用它：

1. **解自定义最小二乘**：多相机协同、自定义相机模型
2. **PCA 降维**：高维特征预处理
3. **SVD 截断**：图像压缩、噪声过滤
4. **特征值分析**：主轴提取、稳定性分析
5. **批量矩阵计算**：机器学习模型推理、仿真

**学习路径建议**：
- **第 1 周**：掌握 `create_matrix` + `mult_matrix` + `solve_matrix`（基础三件套）。
- **第 2 周**：学 `svd_matrix` + `principal_comp`（常用分解）。
- **第 3 周**：学 `eigenvalues_*` + `*_mod`（按需深入）。
- **持续**：根据项目需求扩展。

**核心心法**：
1. **能用高级 API 就不用 Matrix**：先看是否有 `camera_calibration`、`register_object_model_3d` 等封装。
2. **`solve_matrix` > `invert_matrix` + `mult_matrix`**：更稳定、更快。
3. **知道矩阵性质就用对应 Mode**：对称正定用 `'symmetric_posdef'`，快 2 倍。
4. **`*_mod` 是 in-place**：节省内存，但会覆盖原矩阵。
5. **奇异矩阵要小心**：`det ≈ 0` 时加正则化或用 SVD。

最后：**Matrix 是"底层核武器"**——绝大多数项目不直接用，但当所有高级 API 都失败时，它能救场。
