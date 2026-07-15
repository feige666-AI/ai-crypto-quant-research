# 修改前基线审计

审计时间：2026-07-16（Asia/Shanghai）  
审计对象：`feige666-AI/ai-crypto-quant-research`  
基线分支：`main`  
基线提交：`bf2536be66bccbfd416c6b708337ff25da233e24`

## 修改前目录结构

```text
.
├── .gitignore
├── DECISIONS.md
├── PROJECT_STATE.md
├── README.md
├── TASK_LOG.md
├── requirements.txt
├── data/sample_data.csv
├── docs/
│   ├── architecture.md
│   └── resume_project_description.md
├── examples/usage_example.md
├── results/
│   ├── backtest_result_sample.csv
│   └── backtest_summary_sample.json
└── src/crypto_quant_research/
    ├── __init__.py
    ├── backtest.py
    ├── cli.py
    ├── data_loader.py
    └── strategy.py
```

## 已实现功能

- 从本地 CSV 读取六个 OHLCV 字段。
- 计算短期和长期简单移动平均线。
- 生成 `buy`、`sell`、`hold` 信号。
- 运行单资产、只做多、全仓进出的基础回测。
- 输出一份资金曲线 CSV 和一份简要 JSON。

## 修改前运行方法

README 要求手动设置 `PYTHONPATH=src` 后运行 `python -m crypto_quant_research.cli backtest`。仓库没有 `pyproject.toml`、`setup.py` 或 `__main__.py`，因此不能标准安装，也不能运行 `python -m crypto_quant_research --help`。

## 修改前测试状态

- 仓库没有 `tests/` 目录，也没有自动化测试。
- 没有覆盖率记录。
- 没有 Ruff、格式检查或编译检查配置。
- 没有 GitHub Actions。

## 修改前输出文件

- `results/backtest_result_sample.csv`
- `results/backtest_summary_sample.json`

已有输出只有 15 行数据，交易计数把买入和卖出动作混在一起，缺少完整交易明细、滑点、累计手续费、基准收益、市场暴露率、胜率和 Profit Factor。

## 发现的问题

1. README 代码围栏损坏，安装和运行命令不完整。
2. 需要手动设置 `PYTHONPATH`，没有标准包安装入口。
3. CSV 仅检查字段和基本数值转换，未检查空文件、NaN、Infinity、时间顺序、重复时间、正价格和 OHLC 关系。
4. 普通用户错误使用含义不清晰的 `ValueError`，且 CLI 没有统一的简洁错误输出。
5. 回测没有滑点、交易明细、期末平仓选项、累计手续费、基准、暴露率、胜率或 Profit Factor。
6. 示例数据只有 15 行，不能充分覆盖均线交叉和多个市场阶段。
7. 没有图表、测试、覆盖率、代码质量检查和 CI。
8. `examples/usage_example.md` 与 `TASK_LOG.md` 含个人 Windows 绝对路径；简历文档含错误的旧 GitHub 用户名。
9. README 第一屏突出 Codex，多于项目本身，不利于招聘人员快速理解作品价值。
10. 文档把 RSI 等复杂功能列为扩展方向，与本次保持简单均线策略的定位不一致。

## 隐私检查

对基线 18 个文本文件进行了人工和关键词检查。未发现 API Key、Token、密码、邮箱、手机号、真实账户或真实交易记录；发现的个人绝对路径和错误旧链接属于需要修正的隐私与可移植性问题。

## 本次升级范围

- 标准 Python `src` 布局和安装配置。
- `validate`、`signals`、`backtest`、`demo` 四个 CLI 子命令。
- 完整 OHLCV 校验、可配置均线信号、教学型长仓回测。
- 稳定 CSV/JSON 导出、可复现合成数据和三张 matplotlib 图表。
- pytest 测试、覆盖率、Ruff、编译检查和 GitHub Actions。
- README、架构、回测假设、作品集讲解、面试要点和简历文案。

## 明确不做

不接交易所、不做实盘、不使用真实数据、不管理密钥、不做空、不加杠杆、不做多资产、不做参数寻优、不加入数据库、Web 服务、机器学习或云部署。
