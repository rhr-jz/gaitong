# 概率与数理统计大作业 · 北京多站点空气质量

北京大学 2026 春季《概率与数理统计》课程大作业仓库。

**仓库地址（给其他 AI / 组员直接引用）：**

```
https://github.com/zeande668-arch/gaitong
```

克隆：

```bash
git clone https://github.com/zeande668-arch/gaitong.git
cd gaitong
```

## 选题概要

基于 UCI [Beijing Multi-Site Air Quality Data](https://archive.ics.uci.edu/dataset/501/beijing+multi+site+air+quality+data)（2013–2017，12 个监测站），开展统计推断与可视化，报告需可复现。

## 目录结构

| 路径 | 说明 |
|------|------|
| `src/` | 共享配置与后续分析代码（`config.py` 含站点分组、污染物列名等常量） |
| `scripts/` | 工具脚本（如生成项目计划书 PDF） |
| `data/beijing+multi+site+air+quality+data/` | 课程数据集（已入库） |
| `reference/` | 作业说明、参考文献摘录 |
| `reports/` | 报告 PDF、图表、表格（本地生成） |

## 环境

```bash
python -m venv .venv
.venv\Scripts\activate    # Windows
pip install pandas numpy matplotlib seaborn scipy reportlab
```

## 组员分工（请在 Issue / PR 中更新）

| 角色 | 职责 |
|------|------|
| A 同学 | 数据预处理、探索性分析、仓库维护 |
| （待填） | 建模与推断 |
| （待填） | 报告撰写 |

## 给 AI 助手的使用说明

1. 优先阅读 [`AGENTS.md`](./AGENTS.md)，其中包含路径约定、禁止事项和推荐工作流。
2. 需要读原始数据时，使用 `data/beijing+multi+site+air+quality+data/` 下各站点 CSV，勿重复提交 `data/raw/`。
3. 共享常量（站点中英文、污染物列、随机种子等）统一从 `src/config.py` 导入。
4. 课程要求：报告须声明生成式 AI 使用情况；核心结论与实验设计由作者负责。

## 许可证

课程作业用途；数据集版权归 UCI / 原作者所有。
