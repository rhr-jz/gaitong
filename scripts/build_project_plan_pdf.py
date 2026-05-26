from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    FrameBreak,
    KeepTogether,
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
OUT_FILE = OUT_DIR / "项目计划书.pdf"


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
            fontSize=23,
            leading=31,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#16324F"),
            spaceAfter=18,
            wordWrap="CJK",
        ),
        "cover_subtitle": ParagraphStyle(
            "cover_subtitle",
            parent=styles["Normal"],
            fontName=BODY_FONT,
            fontSize=12.5,
            leading=20,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#475569"),
            wordWrap="CJK",
        ),
        "meta": ParagraphStyle(
            "meta",
            parent=styles["Normal"],
            fontName=BODY_FONT,
            fontSize=10.5,
            leading=18,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#334155"),
            wordWrap="CJK",
        ),
        "h1": ParagraphStyle(
            "h1",
            parent=styles["Heading1"],
            fontName=HEADING_FONT,
            fontSize=15.5,
            leading=22,
            textColor=colors.HexColor("#12355B"),
            spaceBefore=14,
            spaceAfter=8,
            wordWrap="CJK",
        ),
        "h2": ParagraphStyle(
            "h2",
            parent=styles["Heading2"],
            fontName=HEADING_FONT,
            fontSize=12.5,
            leading=18,
            textColor=colors.HexColor("#1F4E79"),
            spaceBefore=10,
            spaceAfter=5,
            wordWrap="CJK",
        ),
        "body": ParagraphStyle(
            "body",
            parent=styles["BodyText"],
            fontName=BODY_FONT,
            fontSize=10.5,
            leading=17,
            alignment=TA_JUSTIFY,
            firstLineIndent=21,
            spaceAfter=5,
            wordWrap="CJK",
        ),
        "body_noindent": ParagraphStyle(
            "body_noindent",
            parent=styles["BodyText"],
            fontName=BODY_FONT,
            fontSize=10.5,
            leading=17,
            alignment=TA_JUSTIFY,
            firstLineIndent=0,
            spaceAfter=5,
            wordWrap="CJK",
        ),
        "bullet": ParagraphStyle(
            "bullet",
            parent=styles["BodyText"],
            fontName=BODY_FONT,
            fontSize=10.2,
            leading=16,
            leftIndent=0,
            firstLineIndent=0,
            wordWrap="CJK",
        ),
        "small": ParagraphStyle(
            "small",
            parent=styles["BodyText"],
            fontName=BODY_FONT,
            fontSize=9.2,
            leading=14,
            textColor=colors.HexColor("#475569"),
            wordWrap="CJK",
        ),
        "table": ParagraphStyle(
            "table",
            parent=styles["BodyText"],
            fontName=BODY_FONT,
            fontSize=9.2,
            leading=13.2,
            wordWrap="CJK",
            alignment=TA_LEFT,
        ),
        "table_header": ParagraphStyle(
            "table_header",
            parent=styles["BodyText"],
            fontName=HEADING_FONT,
            fontSize=9.4,
            leading=13.5,
            textColor=colors.white,
            wordWrap="CJK",
            alignment=TA_CENTER,
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
    }


S = make_styles()


class PlanDocTemplate(BaseDocTemplate):
    def __init__(self, filename: str):
        super().__init__(
            filename,
            pagesize=A4,
            leftMargin=2.1 * cm,
            rightMargin=2.1 * cm,
            topMargin=1.85 * cm,
            bottomMargin=1.7 * cm,
            title="北京多站点 PM2.5 统计推断项目计划书",
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
            [
                PageTemplate(id="normal", frames=[frame], onPage=self._draw_header_footer),
            ]
        )

    def _draw_header_footer(self, canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor("#CBD5E1"))
        canvas.setLineWidth(0.5)
        canvas.line(doc.leftMargin, A4[1] - 1.25 * cm, A4[0] - doc.rightMargin, A4[1] - 1.25 * cm)
        canvas.setFont(BODY_FONT, 8.5)
        canvas.setFillColor(colors.HexColor("#64748B"))
        if doc.page > 1:
            canvas.drawString(doc.leftMargin, A4[1] - 1.05 * cm, "概率与数理统计课程大作业项目计划书")
        canvas.drawRightString(A4[0] - doc.rightMargin, 0.9 * cm, f"第 {doc.page} 页")
        canvas.restoreState()


def p(text: str, style: str = "body"):
    return Paragraph(text, S[style])


def bullets(items: list[str], level: int = 0):
    return ListFlowable(
        [ListItem(Paragraph(item, S["bullet"]), leftIndent=0) for item in items],
        bulletType="bullet",
        start=None,
        leftIndent=16 + level * 10,
        bulletFontName=BODY_FONT,
        bulletFontSize=7,
        bulletOffsetY=2,
    )


def table(data, col_widths):
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
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return t


def build_story():
    story = []

    story += [
        Spacer(1, 3.2 * cm),
        p("北京多站点 PM2.5 浓度的统计推断", "cover_title"),
        p("分布特征、季节/站点差异与气象因素影响分析", "cover_subtitle"),
        Spacer(1, 1.0 * cm),
        p("《概率与数理统计》课程大作业项目计划书", "meta"),
        Spacer(1, 0.4 * cm),
        p("数据来源：UCI Beijing Multi-Site Air Quality Data<br/>计划日期：2026 年 5 月 26 日<br/>建议提交形态：PDF 报告 + 可复现代码 + 原始/处理数据说明", "meta"),
        Spacer(1, 1.0 * cm),
        p("本计划书用于确定研究问题、统计方法、数据处理标准、代码组织和项目进度。后续报告应在此基础上压缩为 4-6 页的正式课程报告，并附带可复现实验材料。", "callout"),
        PageBreak(),
    ]

    story += [
        p("一、项目基本介绍", "h1"),
        p("本项目拟以北京市 12 个空气质量监测站在 2013 年 3 月 1 日至 2017 年 2 月 28 日的小时级空气质量与气象数据为研究对象，围绕 PM2.5 浓度的分布特征、季节差异、站点差异与气象因素影响展开统计推断。相比单纯绘图或套用复杂预测模型，本项目强调课程知识的完整落地：从数据清洗、统计量描述、分布建模、区间估计、假设检验到回归建模，形成一条可解释、可复现、能回应现实问题的分析链。"),
        p("推荐题目：北京多站点 PM2.5 浓度的统计推断：分布特征、季节/站点差异与气象因素影响分析。", "callout"),
        p("选题价值", "h2"),
        bullets(
            [
                "现实意义明确：PM2.5 是评价空气污染和健康风险的重要指标，分析其变化规律有助于理解污染暴露、季节性污染和气象扩散条件。",
                "数据质量较高：UCI 数据集包含 12 个站点、420,768 条小时记录，字段覆盖 PM2.5、PM10、SO2、NO2、CO、O3、温度、气压、露点、降水、风向和风速等变量。",
                "课程贴合度高：可以系统运用描述统计、随机变量分布、相关系数、参数估计、置信区间、假设检验、一元/多元线性回归等课内内容。",
                "拓展空间可控：在主线之外可加入 bootstrap 置信区间、稳健回归或 logistic 回归作为自主学习内容，但不追求方法堆叠。"
            ]
        ),
        p("项目定位", "h2"),
        p("本项目不以“预测比赛”为核心，而以“统计推断”为核心：先提出关于 PM2.5 分布、差异与影响因素的统计问题，再用恰当模型和检验方法给出证据，并讨论结论的限制。这样更符合课程大作业对“问题提出、概率模型建立、方法介绍、数据分析结果与讨论、参考文献”的要求。"),
    ]

    story += [
        p("二、研究问题与预期结论", "h1"),
        table(
            [
                ["研究问题", "统计表达", "拟采用方法", "预期产出"],
                [
                    "PM2.5 的总体分布形态如何？",
                    "PM2.5 是否强右偏、重尾？log(PM2.5+1) 后是否更接近正态？",
                    "直方图、核密度图、QQ 图、偏度/峰度、候选分布拟合",
                    "说明原始浓度不宜直接套用正态模型，并为后续变换建模提供依据",
                ],
                [
                    "季节之间是否存在显著差异？",
                    "春、夏、秋、冬的日均 PM2.5 均值或中位数是否相同？",
                    "置信区间、单因素 ANOVA、Kruskal-Wallis 稳健性检验",
                    "量化冬季污染更高、夏季较低等季节性规律",
                ],
                [
                    "不同站点是否存在空间差异？",
                    "12 个站点的 PM2.5 水平是否相同，城区与郊区是否不同？",
                    "分组箱线图、方差分析、非参数检验、效应量比较",
                    "识别污染水平较高与较低的典型站点，讨论城市功能区差异",
                ],
                [
                    "气象因素如何影响 PM2.5？",
                    "风速、降水、温度、气压、露点、风向等变量与 PM2.5 的关系如何？",
                    "相关分析、多元线性回归、虚拟变量、残差诊断",
                    "建立可解释模型，判断风速、季节、站点等因素的方向和显著性",
                ],
                [
                    "重污染风险能否被简单建模？",
                    "日均 PM2.5 是否超过阈值，如 75 或 150 微克/立方米？",
                    "比例估计、置信区间、可选 logistic 回归",
                    "给出不同季节/站点的重污染概率估计，作为拓展结果",
                ],
            ],
            [3.3 * cm, 4.4 * cm, 4.0 * cm, 4.8 * cm],
        ),
        Spacer(1, 0.15 * cm),
        p("初步数据体检显示，PM2.5 缺失约 2.08%，整体均值约 79.79，中位数约 55，95% 分位数约 242，最大值达 999，呈明显右偏和重尾特征；冬季均值约 95.48，夏季约 64.67，季节差异具有清晰的分析价值。", "small"),
    ]

    story += [
        p("三、数据来源与预处理方案", "h1"),
        p("原始数据来自 UCI Machine Learning Repository 的 Beijing Multi-Site Air Quality Data。项目文件夹中真正用于分析的是 data/beijing+multi+site+air+quality+data/PRSA2017_Data_20130301-20170228/PRSA_Data_20130301-20170228 下的 12 个站点 CSV 文件；顶层的 data.csv、test.csv 为股票价格样例数据，不属于本项目，应在 README 中明确排除。"),
        table(
            [
                ["处理环节", "具体做法", "理由"],
                ["时间字段构造", "将 year、month、day、hour 合成为 datetime，并检查每站是否覆盖完整小时序列", "保证时间索引正确，为日均聚合和季节划分打基础"],
                ["缺失值处理", "对 PM2.5 和气象变量统计缺失比例；小时级缺失可使用站点内时间插值，日均聚合要求一天至少 18 个有效小时", "避免少量缺失破坏分析，同时防止用信息不足的日期构造日均值"],
                ["分析单位选择", "主分析使用“站点-日期”的日均 PM2.5；小时级数据用于补充展示日变化", "小时记录存在强自相关，直接当作独立样本会夸大显著性"],
                ["异常值处理", "不随意删除高浓度值；仅对明显不可能值做标记，并在分布分析中保留重污染尾部", "高值本身是污染研究的重要对象，不能简单视为噪声"],
                ["变量构造", "构造 season、year、month、weekday、是否重污染、风向类别等变量", "便于进行分组比较、回归建模和结果解释"],
            ],
            [3.1 * cm, 7.3 * cm, 5.7 * cm],
        ),
        p("数据预处理脚本应做到可复现：输入原始 CSV，输出统一的 processed_daily.csv 和 processed_hourly.csv；所有图表和统计结论都应由处理后数据自动生成。", "callout"),
    ]

    story += [
        p("四、统计模型与方法路线", "h1"),
        p("本项目方法路线按照“描述 - 推断 - 建模 - 验证”的顺序展开。报告中每一种方法都应解释它回答的具体问题，避免只罗列方法名称。"),
        p("1. 描述统计与分布建模", "h2"),
        bullets(
            [
                "计算 PM2.5 的均值、中位数、标准差、四分位数、偏度、峰度和主要分位点。",
                "绘制 PM2.5 原始值与 log(PM2.5+1) 的直方图、密度图和 QQ 图，比较其正态性。",
                "可选比较对数正态、Gamma 等候选分布，但重点放在解释“为什么直接正态假设不合适”。",
            ]
        ),
        p("2. 区间估计与假设检验", "h2"),
        bullets(
            [
                "估计总体日均 PM2.5 的均值置信区间，以及不同季节、不同站点的均值置信区间。",
                "检验季节均值是否相同、站点均值是否相同；同时报告 p 值和效应大小，避免只说“显著”。",
                "由于 PM2.5 分布右偏，可将 ANOVA 与非参数检验结合，作为结论稳健性的说明。",
            ]
        ),
        p("3. 相关分析与回归建模", "h2"),
        bullets(
            [
                "先计算 PM2.5 与气象变量的 Pearson/Spearman 相关系数，观察方向和强度。",
                "建立以 log(PM2.5+1) 为因变量的多元线性回归模型，解释变量包括风速、温度、气压、露点、降水、季节和站点虚拟变量。",
                "检查残差图、异方差、共线性和异常点，说明模型适用范围。",
                "拓展模型可将“是否重污染日”作为二分类变量，使用 logistic 回归估计重污染概率。",
            ]
        ),
        p("4. 自主学习与仿真部分", "h2"),
        p("为满足作业对动手实践和课程拓展的要求，建议加入 bootstrap 置信区间：对日均数据按站点-日期重抽样，估计季节均值差或重污染概率差的 bootstrap 置信区间，并与传统置信区间进行比较。该部分既有实际意义，又不会使项目偏离主线。"),
    ]

    story += [
        p("五、代码组织与可复现要求", "h1"),
        p("优秀作业不只是报告漂亮，还应让助教能够根据提交材料复现全部结果。建议将项目按成熟 GitHub 项目的习惯组织。"),
        table(
            [
                ["路径", "内容", "说明"],
                ["README.md", "项目简介、数据来源、复现命令、主要结论、AI 使用说明", "作为项目入口，优先保证清晰可读"],
                ["data/raw/", "原始 UCI CSV 数据", "保持原样，不在代码中覆盖"],
                ["data/processed/", "清洗后的 hourly/daily 数据", "由脚本生成，可被复现"],
                ["src/load_data.py", "读取、合并、校验 12 个站点数据", "包含字段检查和时间范围检查"],
                ["src/preprocess.py", "缺失处理、日均聚合、变量构造", "输出可分析数据表"],
                ["src/eda.py", "描述统计和分布图", "生成报告中的基础图表"],
                ["src/inference.py", "置信区间、假设检验、bootstrap", "对应课程统计推断内容"],
                ["src/regression.py", "相关分析、回归模型、诊断图", "生成模型结果表和残差图"],
                ["reports/figures/", "报告使用的图片", "由脚本自动输出，文件名规范"],
                ["reports/report.pdf", "最终报告", "建议 4-6 页，附参考文献和 AI 声明"],
            ],
            [4.0 * cm, 6.3 * cm, 5.8 * cm],
        ),
        p("基本代码规范：函数命名清晰，避免在 notebook 中堆叠不可复现的临时代码；随机过程如 bootstrap 需固定随机种子；所有统计结果尽量由脚本生成并保存为 CSV/PNG，减少手工复制错误。"),
    ]

    story += [
        p("六、项目安排与分工建议", "h1"),
        p("课程提交截止日期为 2026 年 6 月 21 日。建议在期末考试前完成主体分析，最后一周只做报告润色、复现检查和压缩包整理。若小组为 3-4 人，可按“数据与代码、统计推断、建模可视化、报告整合”分工。"),
        table(
            [
                ["阶段", "时间建议", "主要任务", "阶段产出"],
                ["阶段 1：定题与数据核验", "5 月 26 日 - 5 月 29 日", "确认研究问题；核对数据范围、字段、缺失比例；排除无关 data.csv/test.csv", "数据体检记录、项目计划书、README 初稿"],
                ["阶段 2：预处理与 EDA", "5 月 30 日 - 6 月 3 日", "完成数据合并、缺失处理、日均聚合；绘制分布、季节、站点差异图", "processed 数据、EDA 图表、描述统计表"],
                ["阶段 3：统计推断", "6 月 4 日 - 6 月 8 日", "完成置信区间、假设检验、bootstrap；比较季节和站点差异", "推断结果表、检验结论、方法说明草稿"],
                ["阶段 4：回归与拓展", "6 月 9 日 - 6 月 13 日", "完成相关分析、多元回归、残差诊断；可选 logistic 回归", "模型结果表、诊断图、可解释结论"],
                ["阶段 5：报告与复现", "6 月 14 日 - 6 月 18 日", "撰写 4-6 页 PDF 报告；整理参考文献、AI 声明、复现命令", "报告初稿、完整代码、README"],
                ["阶段 6：终检与提交", "6 月 19 日 - 6 月 21 日", "从零运行代码；检查图片、页码、压缩包结构；邮件提交", "最终 PDF、ZIP 压缩包、提交邮件"],
            ],
            [2.9 * cm, 3.1 * cm, 6.3 * cm, 4.4 * cm],
        ),
        p("分工建议", "h2"),
        bullets(
            [
                "成员 A：负责数据读取、清洗、缺失处理和项目目录规范。",
                "成员 B：负责描述统计、分布分析、置信区间和假设检验。",
                "成员 C：负责相关分析、回归建模、模型诊断和图表美化。",
                "成员 D：负责 README、报告整合、参考文献、AI 使用声明和最终复现检查。若小组人数不足，可合并相邻角色。",
            ]
        ),
    ]

    story += [
        p("七、报告结构建议", "h1"),
        p("正式报告建议控制在 4-6 页，附录或代码文件承担更多细节。报告不应把所有图表都堆进去，而应选择最能支撑结论的图表。"),
        table(
            [
                ["章节", "建议篇幅", "核心内容"],
                ["1. 问题提出", "约 0.5 页", "说明 PM2.5 研究意义、数据背景和本文要回答的统计问题"],
                ["2. 数据来源与预处理", "约 0.75 页", "介绍 UCI 数据、站点、时间范围、变量、缺失处理和日均聚合策略"],
                ["3. 方法介绍", "约 1 页", "说明分布分析、置信区间、假设检验、回归和 bootstrap 的统计思想"],
                ["4. 结果与讨论", "约 2-3 页", "展示关键图表和表格，回答分布、季节、站点和气象因素问题"],
                ["5. 结论与局限", "约 0.5 页", "总结主要发现，说明相关不等于因果、时间相关性、站点覆盖等限制"],
                ["6. AI 使用声明与参考文献", "约 0.5 页", "按课程要求列明 AI 工具贡献，并列出数据和方法参考来源"],
            ],
            [3.0 * cm, 2.4 * cm, 10.7 * cm],
        ),
        p("建议主图表", "h2"),
        bullets(
            [
                "PM2.5 原始分布与 log 变换分布对比图。",
                "按季节划分的日均 PM2.5 箱线图或小提琴图。",
                "12 个站点日均 PM2.5 均值与置信区间图。",
                "气象变量与 PM2.5 的相关热力图或回归系数图。",
                "模型残差诊断图或重污染概率结果图。",
            ]
        ),
    ]

    story += [
        p("八、质量标准与风险控制", "h1"),
        table(
            [
                ["质量维度", "优秀标准", "风险与应对"],
                ["问题意识", "每个统计方法都对应一个明确问题，结论能回到空气污染机制或规律", "避免方法堆叠；报告中删去不能支撑结论的分析"],
                ["统计严谨性", "说明样本单位、缺失处理、模型假设、p 值和置信区间含义", "小时数据相关性强；主分析改用日均站点数据"],
                ["可解释性", "优先使用可解释模型，报告方向、大小和不确定性", "不将相关关系表述为因果关系"],
                ["代码质量", "目录清楚、函数封装、固定随机种子、输出可复现", "避免只交 notebook；关键流程脚本化"],
                ["报告呈现", "图表简洁，正文围绕核心结论，AI 声明和参考文献完整", "避免图太多、文字太散；最终统一图表风格"],
            ],
            [3.0 * cm, 6.2 * cm, 6.8 * cm],
        ),
        p("最终交付清单", "h2"),
        bullets(
            [
                "正式报告 PDF：建议命名为 report.pdf。",
                "完整代码：包含数据预处理、分析、绘图和结果生成脚本。",
                "原始数据或数据来源说明：保留 UCI 原始 CSV，并说明顶层无关 CSV 不参与分析。",
                "README.md：包含项目介绍、复现命令、环境依赖、主要结果和 AI 使用说明。",
                "参考文献列表：至少包含 UCI 数据集页面、PM2.5 健康/环境背景资料、统计方法资料。",
            ]
        ),
        p("总体判断：该选题具备成为优秀作业的潜力。成功关键不是加入更多复杂模型，而是围绕 PM2.5 的分布、差异与影响因素形成清晰主线，并保证分析严谨、代码整洁、结果可复现。", "callout"),
    ]

    return story


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    doc = PlanDocTemplate(str(OUT_FILE))
    doc.build(build_story())
    print(OUT_FILE)


if __name__ == "__main__":
    main()
