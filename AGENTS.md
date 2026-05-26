# AI 协作指南（AGENTS.md）

本文件供 Cursor、GitHub Copilot、Claude 等 coding agent 快速理解仓库，无需通读全部 CSV。

## 仓库元信息

- **GitHub（公开）**: https://github.com/zeande668-arch/gaitong
- **默认分支**: `main`
- **语言**: Python 3.10+
- **主题**: 北京多站点空气质量 · 统计推断大作业

## 为何使用公开仓库

- 其他 AI 可通过 `https://raw.githubusercontent.com/zeande668-arch/gaitong/main/...` 只读拉取文件，**无需** GitHub Token。
- 组员与 AI 可直接粘贴仓库链接作为上下文。
- 若含未公开数据或个人隐私，请改用 **Private** 仓库，并仅向可信 AI 提供只读 Token。

## 当前提问者身份

若用户自称 **「A 同学」**，其职责为：

- 维护本仓库结构与文档（README、本文件、`.gitignore`）
- 数据清洗、缺失值处理、日/小时聚合脚本（放在 `src/` 或 `scripts/`）
- 产出 `data/processed/` 与 `reports/` 下的可复现中间结果
- 不在未沟通情况下修改他人负责的建模/报告章节

## 关键路径（勿猜）

```text
src/config.py          # ROOT, 站点列表, 污染物列, RANDOM_SEED=42
data/.../PRSA_Data_*.csv   # 各站点小时数据（已入库）
reference/_extracted.txt   # 课程 PDF 文字摘录
scripts/build_project_plan_pdf.py
```

## 代码约定

- 从 `src.config` 导入 `ROOT`, `POLLUTANT_COLS`, `URBAN_SITES`, `SITE_LABELS_ZH` 等，避免魔法字符串。
- 随机过程固定 `RANDOM_SEED = 42`（见 config）。
- 图表输出到 `reports/figures/`，表格到 `reports/tables/`。
- 新增依赖写入 `requirements.txt`（若不存在则创建）。

## 禁止

- 不要将 `data/raw/` 再次提交（与 `data/beijing+multi+site+air+quality+data/` 重复）。
- 不要捏造数据；分析须可追溯到 UCI 源文件。
- 不要提交 API 密钥、`.env`、个人学号等敏感信息。

## 推荐工作流（给 AI）

1. 读 `AGENTS.md` → `src/config.py` → 用户具体任务。
2. 小改：单文件 PR 式修改；大改：先列文件清单再问用户。
3. 跑分析前确认 `data/processed/` 是否存在；若无则先写预处理脚本。
4. 完成后用 1–2 句话说明如何复现（命令 + 输入输出路径）。

## 原始数据说明

- 12 个站点，2013-03-01 至 2017-02-28，小时分辨率。
- 污染物：`PM2.5`, `PM10`, `SO2`, `NO2`, `CO`, `O3`；气象：`TEMP`, `PRES`, `DEWP`, `RAIN`, `WSPM`。
- 重污染日阈值（PM2.5 日均）见 `config.HEAVY_POLLUTION_THRESHOLD`（75 µg/m³）。

## 联系

课程助教邮箱见 `reference/_extracted.txt`；仓库协作问题用 GitHub Issues。
