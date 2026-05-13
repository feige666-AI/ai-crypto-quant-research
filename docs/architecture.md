# 架构说明

## 项目定位

本项目是一个本地运行的加密货币量化研究学习 Demo，用于展示数据处理、策略拆解、回测输出和文档整理能力。当前不接入真实交易所，不保存真实账户信息，不执行真实交易。

## 数据流

```text
data/sample_data.csv
    ↓
data_loader.py
读取 CSV，校验字段，转换为 PriceBar
    ↓
strategy.py
计算移动平均线，生成 Signal
    ↓
backtest.py
执行简单多头回测，生成资金曲线和摘要
    ↓
results/
保存 backtest_result_sample.csv 和 backtest_summary_sample.json
    ↓
README / examples
解释输入、命令和输出含义
```

## 模块关系

```text
cli.py
  ├── data_loader.read_ohlcv_csv
  ├── strategy.generate_ma_signals
  └── backtest.run_long_only_backtest
        ├── write_equity_curve
        └── write_summary
```

## 主要模块说明

| 模块 | 作用 |
|---|---|
| `data_loader.py` | 读取本地 OHLCV CSV，并检查必要字段是否存在。 |
| `strategy.py` | 根据收盘价计算短期和长期移动平均线，并生成买入、卖出或持有信号。 |
| `backtest.py` | 根据策略信号执行简单回测，记录资金、持仓、权益和回撤。 |
| `cli.py` | 提供命令行入口，让用户可以用一条命令运行演示流程。 |

## 当前回测规则

- 初始资金默认是 10000。
- 策略只做多，不支持做空。
- 买入信号出现时，如果没有持仓，则用全部现金买入。
- 卖出信号出现时，如果已有持仓，则全部卖出。
- 默认手续费是 0.1%。
- 回测结果只用于展示流程，不代表策略有效性。

## 安全边界

- 不需要 API Key。
- 不连接交易所。
- 不读取真实账户。
- 不执行真实下单。
- 不上传 `data/raw/`、`data/private/`、`results/private/` 里的内容。

## 后续可扩展方向

- 加入更多指标，例如 RSI、布林带、成交量过滤等。
- 增加交易明细表和更完整的统计指标。
- 增加图表输出，例如资金曲线和回撤曲线。
- 增加测试用例，降低后续修改时出错的概率。
- 当命令变多时，引入 Typer 改善 CLI 体验。
