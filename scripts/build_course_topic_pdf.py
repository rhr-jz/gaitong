"""Generate reports/课程与课题结合说明.pdf from briefing content."""
from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    ListFlowable,
    ListItem,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "reports"
OUT_FILE = OUT_DIR / "课程与课题结合说明.pdf"
HEADER_TEXT = "课程与课题结合说明（组员版）"


def register_fonts() -> tuple[str, str]:
    pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))
    body_font = "STSong-Light"
    heading_font = body_font
    simhei = Path("C:/Windows/Fonts/simhei.ttf")
    if simhei.exists():
        pdfmetrics.registerFont(TTFont("SimHei", str(simhei)))
        heading_font = "SimHei"
    return body_font, heading_font


BODY_FONT, HEADING_FONT = register_fonts()


def make_styles() -> dict[str, ParagraphStyle]:
    styles = getSampleStyleSheet()
    return {
        "cover_title": ParagraphStyle(
            "cover_title",
            parent=styles["Title"],
            fontName=HEADING_FONT,
            fontSize=22,
            leading=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#16324F"),
            spaceAfter=14,
            wordWrap="CJK",
        ),
        "cover_subtitle": ParagraphStyle(
            "cover_subtitle",
            parent=styles["Normal"],
            fontName=BODY_FONT,
            fontSize=12,
            leading=19,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#475569"),
            wordWrap="CJK",
        ),
        "meta": ParagraphStyle(
            "meta",
            parent=styles["Normal"],
            fontName=BODY_FONT,
            fontSize=10.5,
            leading=17,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#334155"),
            wordWrap="CJK",
        ),
        "h1": ParagraphStyle(
            "h1",
            parent=styles["Heading1"],
            fontName=HEADING_FONT,
            fontSize=14.5,
            leading=21,
            textColor=colors.HexColor("#12355B"),
            spaceBefore=12,
            spaceAfter=6,
            wordWrap="CJK",
        ),
        "body": ParagraphStyle(
            "body",
            parent=styles["BodyText"],
            fontName=BODY_FONT,
            fontSize=10.5,
            leading=16.5,
            alignment=TA_JUSTIFY,
            firstLineIndent=21,
            spaceAfter=4,
            wordWrap="CJK",
        ),
        "body_noindent": ParagraphStyle(
            "body_noindent",
            parent=styles["BodyText"],
            fontName=BODY_FONT,
            fontSize=10.5,
            leading=16.5,
            alignment=TA_JUSTIFY,
            firstLineIndent=0,
            spaceAfter=4,
            wordWrap="CJK",
        ),
        "bullet": ParagraphStyle(
            "bullet",
            parent=styles["BodyText"],
            fontName=BODY_FONT,
            fontSize=10,
            leading=15.5,
            wordWrap="CJK",
        ),
        "table": ParagraphStyle(
            "table",
            parent=styles["BodyText"],
            fontName=BODY_FONT,
            fontSize=8.6,
            leading=12.5,
            wordWrap="CJK",
        ),
        "table_header": ParagraphStyle(
            "table_header",
            parent=styles["BodyText"],
            fontName=HEADING_FONT,
            fontSize=8.8,
            leading=12.5,
            textColor=colors.white,
            wordWrap="CJK",
        ),
        "callout": ParagraphStyle(
            "callout",
            parent=styles["BodyText"],
            fontName=BODY_FONT,
            fontSize=10,
            leading=16,
            textColor=colors.HexColor("#1E293B"),
            backColor=colors.HexColor("#EFF6FF"),
            borderColor=colors.HexColor("#93C5FD"),
            borderWidth=0.8,
            borderPadding=8,
            spaceBefore=6,
            spaceAfter=8,
            wordWrap="CJK",
        ),
        "small": ParagraphStyle(
            "small",
            parent=styles["BodyText"],
            fontName=BODY_FONT,
            fontSize=9,
            leading=14,
            textColor=colors.HexColor("#64748B"),
            wordWrap="CJK",
        ),
    }


S = make_styles()


class BriefDocTemplate(BaseDocTemplate):
    def __init__(self, filename: str):
        super().__init__(
            filename,
            pagesize=A4,
            leftMargin=2.0 * cm,
            rightMargin=2.0 * cm,
            topMargin=1.8 * cm,
            bottomMargin=1.65 * cm,
            title=HEADER_TEXT,
            author="概率与数理统计大作业小组",
        )
        frame = Frame(
            self.leftMargin,
            self.bottomMargin,
            self.width,
            self.height,
            id="normal",
        )
        self.addPageTemplates(
            [PageTemplate(id="normal", frames=[frame], onPage=self._draw_header_footer)]
        )

    def _draw_header_footer(self, canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor("#CBD5E1"))
        canvas.setLineWidth(0.5)
        canvas.line(
            doc.leftMargin, A4[1] - 1.22 * cm, A4[0] - doc.rightMargin, A4[1] - 1.22 * cm
        )
        canvas.setFont(BODY_FONT, 8.5)
        canvas.setFillColor(colors.HexColor("#64748B"))
        if doc.page > 1:
            canvas.drawString(doc.leftMargin, A4[1] - 1.02 * cm, HEADER_TEXT)
        canvas.drawRightString(A4[0] - doc.rightMargin, 0.88 * cm, f"第 {doc.page} 页")
        canvas.restoreState()


def p(text: str, style: str = "body") -> Paragraph:
    return Paragraph(text, S[style])


def bullets(items: list[str]) -> ListFlowable:
    return ListFlowable(
        [ListItem(Paragraph(item, S["bullet"]), leftIndent=0) for item in items],
        bulletType="bullet",
        leftIndent=14,
        bulletFontName=BODY_FONT,
        bulletFontSize=7,
        bulletOffsetY=2,
    )


def table(data: list[list[str]], col_widths: list[float]) -> Table:
    converted = []
    for row_idx, row in enumerate(data):
        converted.append(
            [
                Paragraph(str(cell), S["table_header" if row_idx == 0 else "table"])
                for cell in row
            ]
        )
    t = Table(converted, colWidths=col_widths, repeatRows=1, hAlign="LEFT")
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F4E79")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#CBD5E1")),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F8FAFC")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return t


def build_story() -> list:
    story: list = []

    story += [
        Spacer(1, 2.8 * cm),
        p("课程与课题结合说明", "cover_title"),
        p("北京多站点 PM2.5 浓度的统计推断 · 组员版", "cover_subtitle"),
        Spacer(1, 0.6 * cm),
        p(
            "北京大学 2026 春季《概率与数理统计》大作业<br/>"
            "阅读对象：全体组员 · 约 5 分钟<br/>"
            "文档日期：2026 年 5 月 26 日",
            "meta",
        ),
        Spacer(1, 0.8 * cm),
        p(
            "本文说明课程要求、讲义章节与本课题的对应关系，便于分工与撰写正式报告。"
            "Markdown 源文件见 reference/课程与课题结合说明.md；重新生成 PDF 请运行："
            "<font face='Courier'>python scripts/build_course_topic_pdf.py</font>",
            "callout",
        ),
        PageBreak(),
    ]

    story += [
        p("一、大作业在考什么？", "h1"),
        table(
            [
                ["要求", "含义"],
                [
                    "真实数据 + 统计推断",
                    "提出实际问题，用数理统计方法分析，对规律给出推断；不能捏造数据",
                ],
                ["可复现", "助教凭报告 + 代码 + 数据能复现全部图表与数值"],
                [
                    "报告要素",
                    "问题提出 → 概率/统计模型 → 方法介绍 → 数据与预处理 → 结果与讨论 → 参考文献",
                ],
                ["篇幅", "PDF 建议 4–6 页；细节可放代码与 README"],
                [
                    "拓展实践",
                    "建议含动手实践（如 Bootstrap、简单 Monte Carlo 仿真），体现课外自主学习",
                ],
            ],
            [3.2 * cm, 13.5 * cm],
        ),
        Spacer(1, 0.2 * cm),
        p(
            "本选题走「基于实际数据的统计推断」路线，并用 Bootstrap / 仿真满足「动手实践」；"
            "不主打机器学习预测。课程要求全文见 reference/大作业安排.pdf。",
            "body_noindent",
        ),
    ]

    story += [
        p("二、我们研究什么？", "h1"),
        bullets(
            [
                "<b>数据</b>：UCI Beijing Multi-Site Air Quality，北京 12 个监测站，"
                "2013-03-01 至 2017-02-28，小时级；主分析聚合为<b>站点–日</b>日均 PM2.5（见 src/config.py）。",
                "<b>定位</b>：以统计推断为主线（分布 → 区间/检验 → 回归 → 拓展），不是预测比赛。",
                "<b>现实意义</b>：PM2.5 关系公众健康与污染治理；2013–2017 是北京大气污染治理推进期。"
                "讨论可联系政策背景，但须区分<b>相关与因果</b>。",
            ]
        ),
    ]

    story += [
        p("三、讲义章节 ↔ 本课题（核心对照表）", "h1"),
        p(
            "讲义分概率论（第 1–5 章）与数理统计（第 6–10 章）。"
            "本课题主要落在第 3–4 章 + 第 6–10 章；第 5 章在拓展部分呼应。",
            "body_noindent",
        ),
        table(
            [
                ["讲义章节", "课内知识点", "在本课题中的用法"],
                [
                    "第 3 章 连续型",
                    "密度、偏态、重尾",
                    "描述 PM2.5 分布；说明不宜直接假定正态；对 log(PM2.5+1) 做 QQ 图",
                ],
                [
                    "第 4.2 节",
                    "Pearson / Spearman 相关",
                    "分析 PM2.5 与温度、风速、降水等气象变量的关联",
                ],
                [
                    "第 6 章",
                    "总体、样本、统计量；χ²、t、F",
                    "明确样本 = 站点–日观测；构造均值、方差；为估计与检验铺垫",
                ],
                [
                    "第 8 章",
                    "置信区间",
                    "估计分季节、分城区/郊区日均 PM2.5 均值的置信区间",
                ],
                [
                    "第 9 章",
                    "检验、方差分析",
                    "季节差异（ANOVA）；城区 vs 郊区（Welch t 检验等）",
                ],
                [
                    "第 9.5 节",
                    "非参数检验",
                    "Kruskal-Wallis 等，作为右偏数据下参数检验的稳健性补充",
                ],
                [
                    "第 10 章",
                    "线性回归、残差",
                    "多元回归：log(PM2.5+1) ~ 气象 + 季节/站点虚拟变量；残差诊断",
                ],
                [
                    "第 5 章（拓展）",
                    "大数定律、CLT",
                    "Bootstrap 置信区间；可选仿真比较 t 检验在偏态数据下的表现",
                ],
            ],
            [2.6 * cm, 3.4 * cm, 10.7 * cm],
        ),
        Spacer(1, 0.15 * cm),
        p(
            "<b>写报告建议</b>：在「方法介绍」一节用一张小表列出「第 X 章 → 本文用法」，"
            "让评阅人看出这是概率统计课作业，而非纯 Python 画图作业。",
            "body_noindent",
        ),
        PageBreak(),
    ]

    story += [
        p("四、四个研究问题与课程方法的对应", "h1"),
        table(
            [
                ["编号", "研究问题", "主要方法", "负责"],
                [
                    "Q1",
                    "日均 PM2.5 分布形态？能否用正态模型？",
                    "直方图、QQ 图、描述统计、偏度",
                    "B：EDA",
                ],
                [
                    "Q2",
                    "季节、城区/郊区是否有显著差异？",
                    "置信区间；ANOVA + Kruskal-Wallis；Welch t",
                    "C：推断",
                ],
                [
                    "Q3",
                    "气象因素与 PM2.5 如何关联？",
                    "相关分析；多元线性回归 + 残差诊断",
                    "C：回归",
                ],
                [
                    "Q4",
                    "重污染日概率是否随季节/区域变化？",
                    "比例估计、Wilson 区间；可选 logistic",
                    "C + D",
                ],
                [
                    "拓展",
                    "偏态下传统区间是否可靠？",
                    "Bootstrap；可选 Monte Carlo 仿真",
                    "C",
                ],
            ],
            [1.3 * cm, 5.2 * cm, 6.0 * cm, 2.2 * cm],
        ),
        Spacer(1, 0.15 * cm),
        p("正式报告 4–6 页中，Q1–Q3 占主体；Q4 与 Bootstrap 约占 0.5–1 页。", "body_noindent"),
    ]

    story += [
        p("五、与分工的对应", "h1"),
        table(
            [
                ["组员", "分工", "与课程内容的联系"],
                [
                    "A（rhr）",
                    "协调、总进度、仓库",
                    "把控报告是否覆盖问题–模型–方法–数据–结果–文献全链条",
                ],
                [
                    "B",
                    "预处理、EDA、data/processed/",
                    "落实第 6 章「样本」定义：日均聚合、缺失处理（每天至少 18 有效小时）",
                ],
                [
                    "C",
                    "推断与回归",
                    "第 8–10 章 + 9.5 节 + Bootstrap；输出 reports/tables、figures",
                ],
                [
                    "D（ljl）",
                    "报告 PDF、排版",
                    "将对照表写入方法与结果；控制 4–6 页；撰写 AI 使用声明",
                ],
            ],
            [2.0 * cm, 4.2 * cm, 10.5 * cm],
        ),
    ]

    story += [
        p("六、三条必须统一的统计规范", "h1"),
        bullets(
            [
                "<b>分析单位</b>：主分析用站点–日日均数据；不用小时数据直接做 t 检验"
                "（小时强相关会夸大显著性）。",
                "<b>变换</b>：推断与回归优先使用 log(PM2.5+1)；正文说明原始浓度右偏、重尾。",
                "<b>表述</b>：相关与回归只说明关联，不写「风速导致 PM2.5 下降」式因果句；"
                "局限中写明站点非随机布设、时间自相关等。",
            ]
        ),
    ]

    story += [
        p("七、数据与仓库提醒", "h1"),
        bullets(
            [
                "只使用 data/.../PRSA_Data_*.csv（12 个站点）；勿用同目录 data.csv、test.csv（股票样例）。",
                "时间范围即 2013-03-01～2017-02-28；文件夹名含 2017 不代表有更晚年份。",
                "使用 AI 须在最终报告中单独一节声明（模板见 reference/大作业安排.pdf）。",
            ]
        ),
    ]

    story += [
        p("八、一句话总结", "h1"),
        p(
            "<b>用北京 PM2.5 真实数据，把讲义第 6–10 章的估计、检验、回归完整走一遍，"
            "并用第 3–4 章描述分布与相关，用 Bootstrap 体现拓展与动手实践——"
            "这就是本课题与课程的结合方式。</b>",
            "callout",
        ),
        Spacer(1, 0.3 * cm),
        p(
            "更细的时间表与图表清单见 reports/项目计划书.pdf（若已生成）。"
            "文档版本：2026-05-26；分工或选题调整请在组内同步并更新 Markdown 源文件后重新生成本 PDF。",
            "small",
        ),
    ]

    return story


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    doc = BriefDocTemplate(str(OUT_FILE))
    doc.build(build_story())
    print(f"Wrote: {OUT_FILE}")


if __name__ == "__main__":
    main()
