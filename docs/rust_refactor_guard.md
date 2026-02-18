# Rust 重构回归测试方案（AMSS-NCKU）

## 目标

在 Rust 重构过程中，持续验证“新实现数值行为不偏离旧实现”。

## 已落地内容

- 比较器模块：`tools/regression/numdiff.py`
- TwoPuncture 差分入口：`tools/regression/two_puncture_diff.py`
- 回归脚本：`scripts/refactor_guard.sh`
- 案例配置：`tests/refactor_guard/cases/*.json`（自动遍历）
- 框架单测：`tests/refactor_guard/test_numdiff.py`、`tests/refactor_guard/test_two_puncture_diff.py`

## 如何运行

1. 先确保旧实现可执行（已有 `AMSS_NCKU_source/TwoPunctureABE`）。
2. 运行回归脚本（自动遍历所有 case）：

```bash
./scripts/refactor_guard.sh
```

可通过 `CASE_GLOB` 指定子集，例如：

```bash
CASE_GLOB='tests/refactor_guard/cases/*spin*.json' ./scripts/refactor_guard.sh
```

3. 接入 Rust 二进制后开启差分：

```bash
RUST_TWOPUNCTURE_BIN=/path/to/rust_twopuncture ./scripts/refactor_guard.sh
```

4. 在 CI 中强制要求 Rust 差分必须执行：

```bash
REQUIRE_RUST_DIFF=1 RUST_TWOPUNCTURE_BIN=/path/to/rust_twopuncture ./scripts/refactor_guard.sh
```

## 差分检查内容

- `Ansorg.psid`：
  - 忽略不稳定时间戳行（`#File created on ...`）
  - 全部数值序列按 `rtol/atol` 比较
  - 关键命名字段（如 `bhmass1/bhmass2/bhpy1/bhpy2`）单独比较
- 标准输出：
  - 提取 `resulted Mp/Mm`
  - 提取 `total ADM mass`
  - 按 `rtol/atol` 比较

## 扩展建议（下一阶段）

1. 增加多个输入场景：自旋、非对称质量比、不同 `nA/nB/nphi`。
2. 为 BSSN/Z4c 主流程建立短时演化 case（固定步数，固定网格）。
3. 将每个 case 输出归档到 `build/refactor-guard/`，并在 CI 上传为 artifact。
4. 对 Rust 侧关键数值核补属性测试（守恒量、对称性、边界条件）。
