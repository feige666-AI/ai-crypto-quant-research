# 项目状态

更新时间：2026-07-16

## 当前定位

本项目是使用 Python 构建的本地加密货币量化研究学习 Demo，展示 synthetic OHLCV 校验、均线信号、基础回测、结果导出、图表和自动化测试。它不是实盘交易系统，也不代表策略市场有效。

## 已完成

- 标准 `src` 包和 `pyproject.toml`，支持 Python 3.10+。
- `python -m crypto_quant_research` 与 `crypto-quant` 命令入口。
- `validate`、`signals`、`backtest`、`demo` 四个子命令。
- 严格 CSV 字段、有限数值、价格、成交量、OHLC、时间顺序和重复校验。
- 5/20 默认窗口的简单均线信号。
- 单资产只做多回测，包含手续费、滑点、期末仓位、回撤、基准、暴露率、胜率和 Profit Factor。
- 300 行固定种子 synthetic data、四份结果文件和三张 PNG。
- 77 个 pytest 测试，核心包总覆盖率 96%。
- Ruff、编译检查和 Python 3.10/3.11/3.12 GitHub Actions 配置。
- README、基线审计、架构、回测假设、作品集、面试和简历文档。

## 验证状态

- 本地安装：通过。
- `pytest -q`：77 passed。
- 覆盖率：96%。
- `ruff check .`：通过。
- `ruff format --check .`：通过。
- `python -m compileall src`：通过。
- 示例 `demo`：通过。
- GitHub Actions：需在 PR 创建后观察远端运行结果。

## 已知限制

- 使用合成数据，不代表真实历史市场。
- 当前收盘信号与当前收盘成交存在教学型时点偏差。
- 只支持单资产、只做多、全仓进出。
- 不模拟盘口、流动性、部分成交、税费或订单失败。
- 少量完成交易下的统计指标不稳定。

## 未完成且不属于当前范围

交易所 API、实盘、真实账户、做空、杠杆、永续合约、多资产组合、参数寻优、数据库、Web 前端、云部署和机器学习。

## 下一步优先级

1. 等待人工检查 Draft PR 和 GitHub Actions。
2. 如继续迭代，优先增加“下一根开盘价成交”对照模型。
3. 保持数据、策略、回测和实盘边界分离。
