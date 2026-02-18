# Rust 重构方案（保持 Python 脚本不变）

## 约束前提

Python 侧脚本不允许修改，因此 Rust 必须兼容现有调用约定：

- 可执行文件名：`TwoPunctureABE`（由 `makefile_and_run.py` 直接执行 `./TwoPunctureABE`）
- 输入文件名：`TwoPunctureinput.par`
- 输出主文件名：`Ansorg.psid`
- 关键 stdout 文本应保持可解析：
  - `resulted Mp = ... and Mm = ...`
  - `The total ADM mass is ...`

这些约束直接来自：`makefile_and_run.py`、`AMSS_NCKU_Program.py`、`generate_TwoPuncture_input.py`。

## 推荐迁移路线

1. 先做“二进制兼容壳层”
   - Rust 产物最终对外仍叫 `TwoPunctureABE`。
   - 启动参数、工作目录、输入输出文件路径行为与 C++ 版一致。
2. 再做“计算内核替换”
   - 第一阶段：仅替换解析+写出框架，计算仍调用旧库（FFI）或保持旧算法逐段迁移。
   - 第二阶段：逐模块替换数值计算，并持续跑差分测试。
3. 最后做“性能与并行优化”
   - 在行为一致后，再引入 rayon/simd/更 aggressive 的优化。

## 与测试框架的对接点

当前已提供差分脚本：`scripts/refactor_guard.sh`。

- 只跑旧实现基线：
  - `./scripts/refactor_guard.sh`
- 指定 Rust 二进制进行差分：
  - `RUST_TWOPUNCTURE_BIN=/path/to/rust/TwoPunctureABE ./scripts/refactor_guard.sh`
- CI 强制要求 Rust 必须参与差分：
  - `REQUIRE_RUST_DIFF=1 RUST_TWOPUNCTURE_BIN=/path/to/rust/TwoPunctureABE ./scripts/refactor_guard.sh`

多 case 由 `tests/refactor_guard/cases/*.json` 自动发现并执行。

## Rust 工程结构建议

```text
rust/
  Cargo.toml
  src/
    main.rs                 # CLI 与文件 I/O 兼容层
    input/
      twopuncture_par.rs    # 解析 ABE::key=value
    solver/
      two_puncture.rs       # 算法入口
      spectral.rs
      newton.rs
    output/
      ansorg_writer.rs      # 写 Ansorg.psid（格式严格兼容）
    compat/
      logging.rs            # 输出字符串与旧版对齐
```

## Python 不改时的关键兼容清单

1. `TwoPunctureinput.par` 的 key 命名保持一致（含大小写、下划线）。
2. `Ansorg.psid` 仍为文本格式，头字段与 data 段顺序保持稳定。
3. stdout 关键行保留（供日志与测试解析）。
4. 退出码语义保持：成功 `0`，失败非 `0`。
5. 工作目录模型不变：在当前目录读写文件（不改成固定绝对路径）。

## 容差与数值策略

- 对差分测试先使用当前 case 的容差（`tests/refactor_guard/cases/*.json`）。
- 迁移初期优先“结果一致性”而不是“更高性能/更少迭代步”。
- 若某模块改写后数值轨迹略变，先在 case 中单独收紧/放宽容差并记录原因，不要全局放宽。

## 立即可执行的下一步

1. Rust 创建最小可运行 `TwoPunctureABE`，仅完成参数解析与固定输出骨架。
2. 接入 `RUST_TWOPUNCTURE_BIN` 跑通差分脚本（先用最宽容差、再收紧）。
3. 逐段替换算法：每替换一段就新增至少 1 个 case 或 1 组单元测试。
