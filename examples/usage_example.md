# 使用示例

以下命令均从仓库根目录运行，安装后不需要设置 `PYTHONPATH`。

## 安装

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

## 校验合成数据

```powershell
.\.venv\Scripts\python.exe -m crypto_quant_research validate --input data\sample_data.csv
```

成功时会显示 300 行、起止时间、无重复、升序、字段有效、数值有效和 OHLC 有效。

## 生成信号

```powershell
.\.venv\Scripts\python.exe -m crypto_quant_research signals `
  --input data\sample_data.csv `
  --short-window 5 `
  --long-window 20 `
  --output results\signals_sample.csv
```

## 运行回测

```powershell
.\.venv\Scripts\python.exe -m crypto_quant_research backtest `
  --input data\sample_data.csv `
  --short-window 5 `
  --long-window 20 `
  --initial-cash 10000 `
  --fee-rate 0.001 `
  --slippage-rate 0.0005 `
  --equity-output results\equity_curve_sample.csv `
  --trades-output results\trades_sample.csv `
  --summary-output results\backtest_summary_sample.json
```

## 一键生成全部展示产物

```powershell
.\.venv\Scripts\python.exe -m crypto_quant_research demo
```

输入和输出均为 synthetic data，只用于解释流程，不代表真实行情、真实交易或未来收益。
