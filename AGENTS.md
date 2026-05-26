# AI 协作指南（概统大作业）

供 Cursor、Copilot、Claude 等快速理解本仓库，无需通读全部 CSV。

## 项目与仓库

| 项目 | 说明 |
|------|------|
| **项目名** | 概统大作业 |
| **本地根目录** | `C:\Users\LENOVO\Desktop\概统大作业` |
| **GitHub** | https://github.com/rhr-jz/gaitong |
| **Raw** | `https://raw.githubusercontent.com/rhr-jz/gaitong/main/AGENTS.md` |
| **分支** | `main` · Python 3.10+ |

## 角色

| 用户说法 | 职责 |
|----------|------|
| 「A 同学」 | 数据清洗、`data/processed/`、维护 README/本文件 |
| 「组长」 | 协调分工、合并 PR、进度 |

## 关键路径

```text
src/config.py          → HOURLY_DIR, PROCESSED_DIR, RANDOM_SEED
data/beijing+.../       → 12 站 PRSA_Data_*.csv（勿用 data/raw/）
reference/_extracted.txt
scripts/build_project_plan_pdf.py
reports/figures/  reports/tables/
```

## 代码约定

- `from src.config import HOURLY_DIR, POLLUTANT_COLS, URBAN_SITES, RANDOM_SEED`
- 新依赖写入 `requirements.txt`

## 禁止

- 提交 `data/raw/`、`.env`、密钥、学号
- 捏造数据

## 工作流

1. 读 `AGENTS.md` → `src/config.py` → 执行任务  
2. 无 `data/processed/` 时先写预处理  
3. 结束时给出一行复现命令
