# 使用示例

## 运行本地回测 Demo

在 PowerShell 中进入项目目录：

```powershell
cd D:\PPT\ai-crypto-quant-research
$env:PYTHONPATH = "src"
python -m crypto_quant_research.cli backtest --input data/sample_data.csv --output results/backtest_result_sample.csv --summary-output results/backtest_summary_sample.json
```

## 输入数据

输入文件：`data/sample_data.csv`

必要字段：

- `timestamp`：时间
- `open`：开盘价
- `high`：最高价
- `low`：最低价
- `close`：收盘价
- `volume`：成交量

## 输出结果

输出文件：

- `results/backtest_result_sample.csv`
- `results/backtest_summary_sample.json`

结果字段说明：

| 字段 | 含义 |
|---|---|
| `timestamp` | 当前数据行时间 |
| `close` | 当前收盘价 |
| `short_ma` | 短期均线 |
| `long_ma` | 长期均线 |
| `signal` | 策略信号 |
| `executed_action` | 实际执行动作 |
| `cash` | 当前现金 |
| `asset_qty` | 当前持仓数量 |
| `equity` | 当前总权益 |
| `drawdown_pct` | 当前回撤比例 |

## 注意事项

这里的样例数据和结果只用于展示流程。它们不代表真实行情，不构成投资建议，也不能用于判断真实策略收益。
