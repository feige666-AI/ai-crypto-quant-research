# 简历项目描述

项目链接：<https://github.com/feige666-AI/ai-crypto-quant-research>

## 版本 A：精简版（3 条）

- 使用 Python 标准库构建本地 OHLCV 校验、均线信号与单资产只做多回测流程，支持手续费、滑点和期末仓位规则。
- 输出信号、资金曲线、交易明细、JSON 指标摘要与 matplotlib 图表，使用固定种子合成数据保证可复现。
- 编写 77 个 pytest 测试并达到 96% 核心包覆盖率，配置 Ruff 和 Python 3.10–3.12 GitHub Actions。

## 版本 B：标准版（4 条）

- 将原始最小 Demo 重构为标准 Python `src` 包，提供 `validate`、`signals`、`backtest`、`demo` 四个 argparse 子命令。
- 实现 CSV 字段、有限数值、OHLC 关系、时间顺序和重复时间校验，并提供包含文件、行号、字段和值的错误提示。
- 实现含双边手续费、滑点、最大回撤、买入并持有基准、市场暴露率、胜率和 Profit Factor 的教学型回测与稳定报告。
- 使用 Codex 辅助代码与文档迭代，并通过 77 个测试、96% 覆盖率、Ruff、编译检查、图表目视检查和 CI 完成人工验收。

## 版本 C：面试详细版

AI Crypto Quant Research 是一个完全本地运行的 Python 量化研究学习项目。项目使用 300 行固定种子合成 OHLCV，先执行严格数据校验，再生成 5/20 日均线交易意图，最后运行单资产、只做多、全仓进出的教学回测。回测明确处理双边手续费、滑点、期末强制平仓、交易明细、资金曲线、基准收益、最大回撤、胜率、Profit Factor 和市场暴露率，并把不可计算指标保存为 `null`。项目包含 CLI、CSV/JSON 报告、三张 matplotlib 图表、77 个 pytest 测试、96% 核心包覆盖率、Ruff 和多 Python 版本 GitHub Actions。Codex 用于辅助拆解、编码、测试和文档，人工负责范围、风险、输出检查与最终验证。项目不连接交易所、不执行真实订单，也不把合成结果描述为市场验证。
