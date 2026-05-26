# 概统大作业

**概统大作业嘿嘿，组长组员们加油呀 💪💪💪**

北京大学 2026 春季《概率与数理统计》课程大作业 · 基于北京多站点空气质量数据的统计推断。

| | |
|---|---|
| **本地文件夹** | `概统大作业`（本仓库根目录） |
| **GitHub 仓库** | https://github.com/rhr-jz/gaitong |
| **可见性** | Public（方便组员与其他 AI 通过链接只读访问） |
| **默认分支** | `main` |

> GitHub 上的仓库名目前为 `gaitong`。若组长在 GitHub **Settings → Repository name** 改为 `概统大作业`，请将本地远程地址改为 `https://github.com/rhr-jz/概统大作业.git`。

---

## 快速开始

### 用 GitHub Desktop（推荐）

1. 安装 [GitHub Desktop](https://desktop.github.com/)
2. **File → Add local repository** → 选择：
   ```text
   C:\Users\LENOVO\Desktop\概统大作业
   ```
3. 确认 Remote 为 `https://github.com/rhr-jz/gaitong.git`
4. 日常：**Fetch origin** → 修改 → **Commit** → **Push origin**

克隆到本机时，本地文件夹可命名为 `概统大作业`：

**File → Clone repository** → 选 `rhr-jz/gaitong` → 本地路径选 `...\概统大作业`

### 用命令行

```bash
git clone https://github.com/rhr-jz/gaitong.git 概统大作业
cd 概统大作业
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
```

### 给 AI 助手的一句话

```
请阅读 https://github.com/rhr-jz/gaitong（项目名：概统大作业），
先看 AGENTS.md 和 src/config.py，再帮我完成任务。
```

---

## 选题

利用 UCI [Beijing Multi-Site Air Quality Data](https://archive.ics.uci.edu/dataset/501/beijing+multi+site+air+quality+data)（2013–2017，北京 **12** 个监测站、小时分辨率），完成统计建模/推断，并保证**报告、代码、数据**可复现全部结果。

---

## 目录结构

```text
概统大作业/
├── README.md
├── AGENTS.md
├── requirements.txt
├── src/config.py
├── scripts/
├── data/
│   ├── README.md
│   ├── processed/
│   └── beijing+multi+site+air+quality+data/…/PRSA_Data_*.csv
├── reference/
└── reports/
    ├── figures/
    └── tables/
```

> 勿提交 `data/raw/`（与 UCI 目录重复，已在 `.gitignore` 忽略）。

---

## 组员分工

| 分工 | 组员 | 主要负责 |
|------|--------|----------|
| A | rhr | 仓库创建、协调、总进度 |
| B |  | 数据预处理、探索性分析、目录与文档维护 |
| C |  | 统计建模与推断 |
| D | ljl | 报告撰写与排版 |

分工变动请在 [Issues](https://github.com/rhr-jz/gaitong/issues) 更新。

---

## 开发约定

- 共享常量从 `src.config` 导入（`HOURLY_DIR`、`POLLUTANT_COLS`、`RANDOM_SEED` 等）。
- 读原始 CSV 使用 `config.HOURLY_DIR`，不要写死路径。
- 使用生成式 AI 须在报告中单独声明（见 `reference/大作业安排.pdf`）。

---

## 提交截止

见 `reference/大作业安排.pdf`（课程要求 6 月 21 日前邮件提交助教）。

---

## 许可

课程作业用途；UCI 数据集版权归原作者所有。
