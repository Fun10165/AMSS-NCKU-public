# Source Module Documentation: `derivative.py` / `derivative_xiaoqu.py`

## 1. Scope

当前仓库没有独立的 `src/` 目录。  
本次文档与测试覆盖的“源代码模块”为：

- `derivative.py`
- `derivative_xiaoqu.py`

这两个模块都用于一阶有限差分求导。

## 2. `derivative.py`

### API

- `first_order_derivative(f, x, dx, method)`
- `first_order_derivative_multivalue(f, x, dx, method)`

### `method` 可选值

- `"3-points 2-orders"`
- `"5-points 4-orders"`
- `"7-points 6-orders"`

### 行为说明

- `first_order_derivative` 支持标量函数 `f(x)`。
- `first_order_derivative_multivalue` 支持返回向量/数组的函数 `f(x)`，并逐分量求导。
- `first_order_derivative_multivalue` 会打印一次 `f(x)` 的值到标准输出（函数内 `print` 语句）。

### 异常与边界

- `first_order_derivative` 在 `method` 非法时会触发 `UnboundLocalError`（当前实现行为）。
- `first_order_derivative_multivalue` 在 `method` 非法时会返回全零数组（长度与 `f(x)` 分量数相同）。

## 3. `derivative_xiaoqu.py`

### API

- `first_order_derivative(f, x, dx, method)`
- `first_order_derivative_at_t0(f, t, i, method)`

### `method` 可选值

- `"3-points 2-orders"`
- `"5-points 4-orders"`
- `"7-points 6-orders"`
- `"9-points 8-orders"`

### 行为说明

- `first_order_derivative` 对解析函数进行点值求导。
- `first_order_derivative_at_t0` 对离散序列 `f` 在索引 `i` 处求导，时间步长取 `t[1] - t[0]`。
- 使用高阶模板时需保证索引邻域足够（例如 9 点模板需要 `i-4` 到 `i+4`）。

### 异常与边界

- 两个函数在 `method` 非法时都会触发 `UnboundLocalError`（当前实现行为）。

## 4. 测试与覆盖率

测试文件：

- `tests/test_derivative.py`
- `tests/test_derivative_xiaoqu.py`

运行命令：

```bash
python -m pytest \
  tests/test_derivative.py \
  tests/test_derivative_xiaoqu.py \
  --cov=derivative \
  --cov=derivative_xiaoqu \
  --cov-report=term-missing
```

目标：两个模块总体覆盖率 >= 95%。

## 5. Native source tests (`AMSS_NCKU_source`)

除 Python 模块外，仓库还包含 C/C++/Fortran 源码。  
对应的 Nix 环境与原生测试入口见：

- `docs/nix_native_env.md`
- `scripts/test_native.sh`
