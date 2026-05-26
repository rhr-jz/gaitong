# AI 协作指南（AGENTS.md）

供 Cursor、Copilot、Claude 等快速理解本仓库，无需通读全部 CSV。

## 仓库

- **URL**: https://github.com/rhr-jz/gaitong
- **Raw 示例**: `https://raw.githubusercontent.com/rhr-jz/gaitong/main/AGENTS.md`
- **分支**: `main` · **Python** 3.10+

## 角色

| 用户说法 | 职责 |
|----------|------|
| 「A 同学」 | 数据清洗、`data/processed/`、维护 README/本文件；不擅自改他人报告章节 |
| 「组长」 | 协调分工、合并 PR、进度 |

## 关键路径

```text
src/config.py
  HOURLY_DIR     → 12 个站点 PRSA_Data_*.csv 所在目录
  PROCESSED_DIR  → 清洗后输出
  reports/figures|tables/

data/beijing+multi+site+air+quality+data/   # 勿重复提交 data/raw/
reference/_extracted.txt                    # 课程要求文字摘录
scripts/build_project_plan_pdf.py
```

## 代码约定

- `from src.config import HOURLY_DIR, POLLUTANT_COLS, URBAN_SITES, RANDOM_SEED`
- 新依赖写入 `requirements.txt`
- 图表 → `reports/figures/`，表格 → `reports/tables/`

## 禁止

- 提交 `data/raw/`、`.env`、API 密钥、学号等敏感信息
- 捏造数据

## 工作流

1. 读 `AGENTS.md` → `src/config.py` → 执行用户任务  
2. 无 `data/processed/` 时先写预处理脚本  
3. 结束时给出复现命令（一行即可）
