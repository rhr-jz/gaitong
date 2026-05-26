# gaitong

**概统大作业嘿嘿，组长组员们加油呀 💪**

北京大学 2026 春季《概率与数理统计》课程大作业 · 基于北京多站点空气质量数据的统计推断。

| | |
|---|---|
| **仓库** | https://github.com/rhr-jz/gaitong |
| **可见性** | Public（方便组员与其他 AI 通过链接只读访问） |
| **默认分支** | `main` |

---

## 快速开始

### 用 GitHub Desktop 克隆（组员推荐）

1. 安装 [GitHub Desktop](https://desktop.github.com/)
2. **File → Clone repository** → 选 `rhr-jz/gaitong` → 选本地目录
3. 日常：**Fetch origin** → 改代码 → 写 Summary → **Commit** → **Push origin**

### 用命令行克隆

```bash
git clone https://github.com/rhr-jz/gaitong.git
cd gaitong
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
```

### 给 AI 助手的一句话

```
请阅读 https://github.com/rhr-jz/gaitong ，先看 AGENTS.md 和 src/config.py，再帮我完成任务。
```

---

## 选题

利用 UCI [Beijing Multi-Site Air Quality Data](https://archive.ics.uci.edu/dataset/501/beijing+multi+site+air+quality+data)（2013–2017，北京 **12** 个监测站、小时分辨率），完成统计建模/推断，并保证**报告、代码、数据**可复现全部结果。

---

## 目录结构

```text
gaitong/
├── README.md              # 本文件
├── AGENTS.md              # 给 Cursor 等 AI 的协作约定
├── requirements.txt       # Python 依赖
├── src/
│   └── config.py          # 路径、站点分组、污染物列名等共享常量
├── scripts/
│   └── build_project_plan_pdf.py
├── data/
│   ├── README.md          # 数据文件说明
│   ├── processed/         # 清洗后的中间结果（本地生成，默认不入库）
│   └── beijing+multi+site+air+quality+data/
│       └── PRSA2017_Data_.../PRSA_Data_.../PRSA_Data_*.csv   # 各站点原始小时数据
├── reference/             # 课程说明 PDF、讲义图片、文字摘录
└── reports/             # 项目计划书、终稿 PDF、图表
    ├── figures/           # 图（本地生成）
    └── tables/            # 表（本地生成）
```

> **注意**：请勿把 `data/raw/` 提交进仓库（与上面 UCI 目录重复，已在 `.gitignore` 忽略）。

---

## 组员分工

| 成员 | GitHub | 主要负责 |
|------|--------|----------|
| 组长 | [rhr-jz](https://github.com/rhr-jz) | 仓库创建、协调、总进度 |
| A 同学 | （待填） | 数据预处理、探索性分析、目录与文档维护 |
| （待填） | | 统计建模与推断 |
| （待填） | | 报告撰写与排版 |

分工有变动请在 [Issues](https://github.com/rhr-jz/gaitong/issues) 更新。

---

## 开发约定

- 共享常量从 `src.config` 导入，例如 `HOURLY_DIR`、`POLLUTANT_COLS`、`RANDOM_SEED`。
- 随机模拟、Bootstrap 等固定 `RANDOM_SEED = 42`。
- 读原始 CSV 请用 `config.HOURLY_DIR`，不要写死深层路径。
- 使用生成式 AI 须在终稿报告中单独声明（见 `reference/大作业安排.pdf`）。

---

## 首次 Push 说明（A 同学 / 维护仓库的同学）

远程仓库目前只有简短 README；本地已有完整代码与数据。用 GitHub Desktop 时：

1. **File → Add local repository**，选择本机文件夹：`概统大作业\原始资料`
2. **Repository → Repository settings**，确认远程为 `https://github.com/rhr-jz/gaitong.git`
3. 先 **Fetch origin**，若提示 unrelated histories，选 **合并**；README 冲突时保留**本地完整版**
4. 勾选变更 → Commit → **Push origin**

若 Desktop 提示无法推送，请组长在 GitHub 网页将 A 同学账号加入 **Collaborators**。

---

## 提交截止

见 `reference/大作业安排.pdf`（课程要求 6 月 21 日前邮件提交助教）。

---

## 许可

课程作业用途；UCI 数据集版权归原作者所有。
