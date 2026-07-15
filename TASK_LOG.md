# 任务记录

## 2026-07-16：作品集项目完整升级

### 本次目标

把原始最小均线 Demo 升级成可安装、可测试、可复现、可解释的求职作品集，并发布到独立工作分支和 Draft PR。

### 已完成

- 通过 GitHub API 读取 `main` 的完整 18 文件基线并记录 `docs/baseline_audit.md`。
- 从最新 `main` 提交创建 `codex/portfolio-upgrade`，没有直接修改 `main`。
- 完成包结构、CLI、数据校验、策略、回测、报告、图表、合成数据和测试。
- 生成 300 行样例数据、四份结果文件和三张图表。
- 重写 README 与作品集文档，并同步决策和项目状态。
- 本地验证 77 个测试通过，覆盖率 96%。

### 遇到的问题

- 普通 `git clone` 在当前环境分别遇到 SSL/TLS 握手失败和 HTTP 403；仓库访问及账号权限本身正常。
- GitHub 插件连接器只能读取，创建分支返回集成权限 403；改用已登录且具有 `repo`/`workflow` 权限的 GitHub CLI API。
- pip 首次在受限网络中失败，获准联网后安装成功。
- 首次 Ruff 检查发现 3 处导入排序，已修正。
- matplotlib 默认缓存目录不可写，已改用进程临时缓存目录。

### 删除记录

本次未删除任何文件。旧 `results/backtest_result_sample.csv` 会作为原版本输出保留，避免在未单独确认删除的情况下执行删除操作；当前正式入口使用 `results/equity_curve_sample.csv`。

### 下一步

- 完成最终命令验收、隐私扫描和三轮自查。
- 发布真实 Git commit，创建 Draft PR，检查 GitHub Actions。

### 阻塞点

当前无代码阻塞；远端 CI 状态需在 PR 创建后确认。

## 2026-07-16：PR #1 跨平台 CI 修复

### 根因

GitHub Actions 的 Python 3.10、3.11、3.12 任务在测试收集阶段均报 `ModuleNotFoundError: No module named 'scripts'`。本地测试此前恰好能从仓库根目录导入顶层脚本，但 Ubuntu 安装环境不保证该导入路径。

### 已完成

- 将样本数据生成核心和 CLI 实现移入 `src/crypto_quant_research/sample_data.py`。
- 保留 `scripts/generate_sample_data.py` 作为只调用正式包 `main` 的轻量入口，没有重复业务逻辑。
- 两份测试改用 `crypto_quant_research.sample_data`，并让生成器命令测试真实执行脚本文件。
- 本地全量测试仍为 77 项且全部通过；分支覆盖率提升到 97%。
- `ruff check .` 与 `ruff format --check .` 均通过，生成器脚本和主 CLI 的帮助命令均正常。

### 删除记录

本次 CI 修复未删除任何文件。

### 下一步与阻塞点

推送修复提交到 `codex/portfolio-upgrade`，等待 PR #1 的 GitHub Actions 全部完成；最终状态以远端当前 head commit 的检查结果为准。
