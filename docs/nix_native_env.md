# Nix Ubuntu22-Compatible Environment + Native Tests

## 1. Why this exists

AMSS-NCKU 的 Python 层之外还包含大量 `AMSS_NCKU_source/*.C` 和 `AMSS_NCKU_source/*.f90`。  
为了在接近 Ubuntu 22.04 的工具链环境中稳定复现构建与测试，这里提供了 `nixos-22.11` 的 Nix 开发环境。

开发环境同时包含 Rust 工具链（`rustc`、`cargo`、`rustfmt`、`clippy`、`rust-analyzer`），用于重构阶段的编译和静态检查。

## 2. Enter the Nix shell

```bash
nix develop
```

进入后会自动提示可用测试命令。

## 3. Run Python tests

```bash
python -m pytest
```

## 3.1 Run refactor guard tests

```bash
./scripts/refactor_guard.sh
```

只运行部分 case：

```bash
CASE_GLOB='tests/refactor_guard/cases/*q2*.json' ./scripts/refactor_guard.sh
```

## 4. Run native C/C++/Fortran tests

```bash
./scripts/test_native.sh
```

该脚本会执行三类检查：

1. C++ 单元测试（编译并运行）
   - 覆盖 `AMSS_NCKU_source/round.C`
   - 覆盖 `AMSS_NCKU_source/norm.C`
   - 覆盖 `AMSS_NCKU_source/fuzzy.C`
2. Fortran 单元测试（编译并运行）
   - 覆盖 `AMSS_NCKU_source/FFT.f90` 中 `four1` 子程序
3. CPU-only makefile 冒烟构建
   - 使用 `AMSS_NCKU_source/makefile` 编译 `TwoPunctureABE`（去除 CUDA 依赖）

## 5. Files added for native tests

- `flake.nix`
- `scripts/test_native.sh`
- `tests/native/test_ahf_utils.cpp`
- `tests/native/test_fft_roundtrip.f90`
