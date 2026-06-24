from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
)

OUTPUT = "output/pdf/Carlyse_Jordan_Operations_Program_Manager_Resume.pdf"

NAVY = colors.HexColor("#17324D")
TEAL = colors.HexColor("#087E8B")
INK = colors.HexColor("#1E2933")
MUTED = colors.HexColor("#52616B")
LIGHT = colors.HexColor("#DCE4E8")

pdfmetrics.registerFont(TTFont("DejaVu", "/System/Library/Fonts/Supplemental/Arial.ttf"))
pdfmetrics.registerFont(TTFont("DejaVu-Bold", "/System/Library/Fonts/Supplemental/Arial Bold.ttf"))
pdfmetrics.registerFont(TTFont("DejaVu-Italic", "/System/Library/Fonts/Supplemental/Arial Italic.ttf"))


def style(name, **kwargs):
    base = dict(fontName="DejaVu", fontSize=8.15, leading=10.15, textColor=INK, spaceAfter=0)
    base.update(kwargs)
    return ParagraphStyle(name, **base)


NAME = style("Name", fontName="DejaVu-Bold", fontSize=20, leading=22, textColor=NAVY, alignment=TA_CENTER)
CONTACT = style("Contact", fontSize=8.1, leading=10, textColor=MUTED, alignment=TA_CENTER)
HEADLINE = style("Headline", fontName="DejaVu-Bold", fontSize=8.6, leading=10.5, textColor=TEAL, alignment=TA_CENTER)
SUMMARY = style("Summary", fontSize=8.25, leading=10.45, alignment=TA_LEFT)
SECTION = style("Section", fontName="DejaVu-Bold", fontSize=9.25, leading=11, textColor=NAVY, spaceBefore=4.5, spaceAfter=2)
ORG = style("Org", fontName="DejaVu-Bold", fontSize=8.6, leading=10, textColor=INK)
RIGHT = style("Right", fontName="DejaVu-Bold", fontSize=8.0, leading=10, textColor=MUTED, alignment=TA_RIGHT)
ROLE = style("Role", fontName="DejaVu-Italic", fontSize=8.0, leading=9.4, textColor=MUTED)
BULLET = style("Bullet", fontSize=7.95, leading=9.7, leftIndent=8, firstLineIndent=-5.5, bulletIndent=1.5, spaceAfter=1.5)
CAPS = style("Caps", fontSize=7.65, leading=9.4, textColor=INK)
EDU = style("Edu", fontSize=7.9, leading=9.7)


def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(LIGHT)
    canvas.setLineWidth(0.5)
    canvas.line(doc.leftMargin, 0.36 * inch, letter[0] - doc.rightMargin, 0.36 * inch)
    canvas.setFont("DejaVu", 6.7)
    canvas.setFillColor(MUTED)
    canvas.drawString(doc.leftMargin, 0.23 * inch, "Carlyse Jordan | Operations Program Management")
    canvas.drawRightString(letter[0] - doc.rightMargin, 0.23 * inch, str(doc.page))
    canvas.restoreState()


def section(title):
    return [Paragraph(title, SECTION), Table([[""]], colWidths=[7.35 * inch], rowHeights=[0.7], style=TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), TEAL),
        ("LINEBELOW", (0, 0), (-1, -1), 0.6, TEAL),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ])), Spacer(1, 2)]


def role_header(org, location, role, dates):
    table = Table(
        [[Paragraph(org, ORG), Paragraph(location, RIGHT)],
         [Paragraph(role, ROLE), Paragraph(dates, RIGHT)]],
        colWidths=[5.25 * inch, 2.10 * inch],
        hAlign="LEFT",
    )
    table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    return table


def bullets(items):
    return [Paragraph(item, BULLET, bulletText="-") for item in items]


doc = BaseDocTemplate(
    OUTPUT,
    pagesize=letter,
    leftMargin=0.58 * inch,
    rightMargin=0.58 * inch,
    topMargin=0.42 * inch,
    bottomMargin=0.48 * inch,
    title="Carlyse Jordan - Operations Program Manager Resume",
    author="Carlyse Jordan",
    subject="Operations program management, AI-powered analytics, and change enablement",
)
frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="main", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
doc.addPageTemplates([PageTemplate(id="resume", frames=[frame], onPage=footer)])

story = [
    Paragraph("CARLYSE JORDAN", NAME),
    Paragraph("Washington, DC | 202.276.8589 | jordan.carlyse@gmail.com | linkedin.com/in/carly-jordan", CONTACT),
    Spacer(1, 2),
    Paragraph("OPERATIONS PROGRAM MANAGEMENT | AI-POWERED ANALYTICS | CHANGE ENABLEMENT", HEADLINE),
    Spacer(1, 4),
    Paragraph(
        "Program and operations-focused technologist with 6+ years leading cross-functional modernization, automation, and performance-improvement initiatives, plus frontline retail experience across grocery, apparel, electronics, and home improvement. Delivered <b>$200K in annual savings</b>, a <b>75% gain in operational efficiency</b>, and a <b>65% reduction in provisioning time</b>. Builds AI-powered diagnostics, dashboards, and scalable operating capabilities, then translates root-cause findings into clear actions for technical, nontechnical, and executive stakeholders.",
        SUMMARY,
    ),
]

story += section("CORE CAPABILITIES")
story += [Paragraph(
    "Operations Program Delivery | Retail Operations and Customer Experience | Cross-Functional Stakeholder Leadership | AI/ML Automation | Performance Diagnostics and Root-Cause Analysis | Change Enablement and Adoption | Data Analysis and Visualization | Process Standardization | Executive Communication | AWS | Splunk | Python | Streamlit | Pandas | Jira | Terraform | GitHub Actions",
    CAPS,
)]

story += section("PROFESSIONAL EXPERIENCE")
story += [role_header("SAIC", "Washington, DC", "Software Engineer | Public Trust", "Jan 2022 - Jul 2025")]
story += bullets([
    "Owned delivery and continuous improvement of high-availability AWS operations supporting <b>150+ annual releases</b> and <b>99.9% uptime</b> in a high-accountability environment.",
    "Used Splunk analytics and ML-driven anomaly detection to identify operational risks, strengthen security posture by <b>60%</b>, and inform targeted database and container improvements that increased processing speed by <b>60%</b>.",
    "Led automation of CI/CD and infrastructure workflows with Terraform and Python, reducing provisioning time by <b>65%</b> and replacing manual work with repeatable, scalable operating processes.",
])
story += [Spacer(1, 1.5), role_header("National Democratic Institute", "Washington, DC", "Cloud Engineer | Consultant (part-time)", "May 2022 - Apr 2025")]
story += bullets([
    "Directed an end-to-end AWS migration and operating-model modernization, aligning executive and technical stakeholders to deliver <b>$200K in annual savings</b> and a <b>75% improvement in operational efficiency</b>.",
    "Drove adoption of EKS, Terraform, and GitHub Actions workflows that tripled deployment frequency and reduced cycle time by <b>60%</b>, translating complex platform changes into clear execution paths.",
    "Improved security posture by <b>30%</b> through IAM redesign and strengthened global application responsiveness with SQS-based asynchronous workflows.",
])
story += [role_header("", "", "Web Developer", "May 2019 - Apr 2022")]
story += bullets([
    "Influenced executive stakeholders on scope and delivery tradeoffs, saving <b>$50K</b> and shortening the program timeline by <b>two months</b>.",
    "Analyzed and improved platform performance for <b>50K+ users</b>, increasing engagement by <b>25%</b> and uptime by <b>30%</b> while resolving <b>150+ operational issues per quarter</b>.",
    "Automated recurring work with Python, reducing manual effort by <b>40%</b> and creating durable processes that scaled beyond individual contributors.",
])
story += [Spacer(1, 1.5), role_header("New Light Technologies", "Washington, DC", "Software Engineer Intern", "Apr 2018 - Apr 2019")]
story += bullets([
    "Improved system performance by <b>30%</b> and accelerated QA cycles by standardizing Docker-based deployment and test automation.",
])

story += section("EARLIER RETAIL OPERATIONS EXPERIENCE")
story += [role_header("American Eagle Outfitters | Food Lion | Walmart | Best Buy | Lowe's", "Prior Experience", "Customer Service | Product | Electronics Department | Cashier Roles", "")]
story += bullets([
    "Built hands-on experience with customer service, product support, point-of-sale transactions, and daily store operations across apparel, grocery, consumer electronics, and home improvement environments.",
])

story += section("SELECTED AI AND ANALYTICS PROJECTS")
story += [KeepTogether([
    role_header("AI-Powered Job Scanner Bot", "Independent Project", "Python | Sentence-Transformers | Streamlit | Discord", "Apr 2026 - Present"),
    *bullets([
        "Built an AI-powered diagnostic and decision-support platform that uses NLP vector embeddings to analyze role requirements, identify resume alignment and skill gaps, and surface prioritized opportunities from <b>8+ APIs and RSS feeds</b>.",
        "Designed a modular plugin architecture, persistent deduplication layer, automated tailoring engine, interactive Streamlit dashboard, and Discord alerts for scalable, repeatable adoption.",
    ])
])]
story += [KeepTogether([
    role_header("Splunk Security Bootcamp", "ThinkCloudly | Remote", "Applied Analytics Project", "Jul 2025 - Dec 2025"),
    *bullets([
        "Created interactive Splunk dashboards that converted high-volume security data into actionable findings; applied machine learning for pattern detection and AI-powered research tools to accelerate documentation and technical discovery.",
    ])
])]

story += section("EDUCATION")
story += [Table([
    [Paragraph("<b>Western Governors University</b> | B.S., Information Technology", EDU), Paragraph("Expected May 2027", RIGHT)],
    [Paragraph("<b>University of the District of Columbia</b> | A.A., Graphic Design", EDU), Paragraph("May 2021", RIGHT)],
], colWidths=[5.85 * inch, 1.50 * inch], style=TableStyle([
    ("LEFTPADDING", (0, 0), (-1, -1), 0),
    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ("TOPPADDING", (0, 0), (-1, -1), 0),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
]))]

doc.build(story)
print(OUTPUT)
