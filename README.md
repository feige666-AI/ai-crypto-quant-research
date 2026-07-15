# AI Crypto Quant Research

## 项目简介

AI Crypto Quant Research 是一个本地运行的加密货币量化研究学习 Demo。项目通过小型 CSV 数据、简单均线信号和基础回测输出，展示一个量化研究流程从“数据读取”到“策略信号”再到“结果分析”的最小闭环。

本项目由 Codex 辅助整理和搭建，重点用于展示 AI 工具使用能力、项目拆解能力、数据处理意识、文档整理能力和基础代码验证能力。项目不连接真实交易所，不执行真实下单，不承诺任何收益。

## 项目背景

加密货币市场数据适合用来学习量化研究流程，例如读取行情数据、设计简单策略、生成回测结果、分析结果指标等。相比直接做实盘交易，本项目先从本地 CSV 和演示数据开始，降低风险，也更适合作为求职作品集展示。

## 项目目标

- 用一个小而完整的 Demo 展示量化研究的基本流程。
- 使用本地样例数据，避免上传真实账户、真实交易或隐私数据。
- 通过 README、项目状态、决策记录和架构文档，让 HR 和技术人员都能快速理解项目。
- 展示 Codex 辅助开发、文档整理、功能拆解和结果分析的实践过程。

## 核心功能

- 读取本地 OHLCV 行情 CSV。
- 检查 CSV 是否包含必要字段：`timestamp`、`open`、`high`、`low`、`close`、`volume`。
- 基于短期和长期移动平均线生成 `buy`、`sell`、`hold` 信号。
- 执行一个简单的“全仓买入 / 全仓卖出”的本地回测。
- 输出资金曲线 CSV 和回测摘要 JSON。

## 技术栈

- Python 3.10+
- Python 标准库：`csv`、`argparse`、`dataclasses`、`json`
- Markdown 项目文档
- 本地 CSV 数据文件

当前版本没有强制第三方依赖，因此 `pip install -r requirements.txt` 可以作为标准项目步骤保留。后续如果命令行功能变多，可以再引入 Typer 优化 CLI 体验。

## 项目流程图

```text
sample_data.csv
    ↓
读取和校验行情数据
    ↓
计算短期 / 长期移动平均线
    ↓
生成 buy / sell / hold 信号
    ↓
执行本地回测
    ↓
输出 backtest_result_sample.csv 和 summary JSON
    ↓
阅读结果，记录分析和后续改进方向
```

## 目录结构说明

```text
ai-crypto-quant-research/
├── README.md
├── PROJECT_STATE.md
├── DECISIONS.md
├── TASK_LOG.md
├── requirements.txt
├── .gitignore
├── docs/
│   ├── architecture.md
│   └── resume_project_description.md
├── src/
│   └── crypto_quant_research/
│       ├── __init__.py
│       ├── backtest.py
│       ├── cli.py
│       ├── data_loader.py
│       └── strategy.py
├── data/
│   └── sample_data.csv
├── results/
│   ├── backtest_result_sample.csv
│   └── backtest_summary_sample.json
└── examples/
    └── usage_example.md
```

## 如何安装依赖

建议使用虚拟环境，但当前 Demo 没有强制第三方依赖。

```powershell
cd D:\PPT\ai-crypto-quant-research
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

如果 Windows 里提示找不到 `python`，可以先安装 Python，或尝试把上面的 `python` 改成 `py`。

## 如何运行项目

在 PowerShell 中运行：

git clone <repository-url>
cd ai-crypto-quant-research
$env:PYTHONPATH = "src"
python -m crypto_quant_research.cli backtest --input data/sample_data.csv --output results/backtest_result_sample.csv --summary-output results/backtest_summary_sample.json
```

运行后会生成：

- `results/backtest_result_sample.csv`：逐行资金曲线和交易动作。
- `results/backtest_summary_sample.json`：最终资金、收益率、最大回撤、交易次数等摘要。

## 示例输入和示例输出

示例输入来自 `data/sample_data.csv`，字段如下：

```csv
timestamp,open,high,low,close,volume
2026-01-01,100,102,99,100,12.5
```

示例输出字段来自 `results/backtest_result_sample.csv`：

```csv
timestamp,close,short_ma,long_ma,signal,executed_action,cash,asset_qty,equity,drawdown_pct
```

这些数据是演示数据，只用于说明流程，不代表真实行情、真实交易或真实收益。

## 当前已完成内容

- 已整理成独立的 GitHub 展示目录。
- 已补充 README、项目状态、决策记录、任务记录和架构说明。
- 已创建本地 CSV 示例数据。
- 已实现基础移动平均线信号和本地回测流程。
- 已生成示例回测结果文件。
- 已配置 `.gitignore`，避免上传缓存、环境文件、私有数据和数据库文件。

## 后续计划

- 计划中：增加更多策略参数和结果指标，例如胜率、交易明细、年化指标等。
- 计划中：增加单元测试，覆盖数据读取、信号生成和回测边界情况。
- 计划中：引入 Typer 或其他 CLI 工具，让命令行参数更友好。
- 计划中：增加更规范的数据来源说明，但仍保持“不上传真实账户数据”的原则。
- 计划中：增加可视化图表，例如资金曲线图和回撤图。

## 我在项目中的工作内容

- 使用 Codex 辅助梳理项目定位、目录结构和 GitHub 展示方式。
- 将项目拆解为数据读取、信号生成、回测执行、结果输出和文档说明几个模块。
- 设计本地演示数据，避免泄露真实账户、真实交易或隐私信息。
- 整理 README、架构文档、项目状态和任务记录，让非技术人员也能理解项目价值。
- 对回测结果进行基础说明，强调学习和验证流程，不夸大策略效果。

## 免责声明

本项目仅用于学习、研究和作品集展示，不构成任何投资建议。项目中的样例数据和回测结果均为演示用途，不代表真实市场表现，也不承诺任何收益。
