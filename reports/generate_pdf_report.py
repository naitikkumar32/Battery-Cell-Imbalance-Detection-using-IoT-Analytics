"""
Script: generate_pdf_report.py
Generates the comprehensive, professional college project report PDF:
'Battery Cell Imbalance Detection Using IoT Analytics'

Complies with all requirements:
- ABES Engineering College, Ghaziabad (Department of Mechanical Engineering)
- 2026-27 Academic Year
- Formal Cover Page, Certificate, Declaration, Acknowledgement, Abstract
- Table of Contents, List of Figures, List of Tables, Abbreviations
- Complete 25 technical sections based strictly on actual codebase implementation
- Professional styling: running headers, "Page X of Y" dynamic numbering,
  clean table formatting, callout alert boxes, embedded figures.
"""

import os
import sys
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table,
    TableStyle, Image, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT

REPORT_DIR = "reports"
OUTPUT_PDF = os.path.join(REPORT_DIR, "Battery_Cell_Imbalance_Detection_Project_Report.pdf")
FIGURES_DIR = os.path.join(REPORT_DIR, "figures")
os.makedirs(REPORT_DIR, exist_ok=True)


class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas to dynamically compute and print 'Page X of Y'
    and academic running headers on all pages except the cover page.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, total_pages):
        # Suppress headers and footers on cover page
        if self._pageNumber == 1:
            return

        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#475569"))

        # Running Header
        self.drawString(54, 804, "Battery Cell Imbalance Detection Using IoT Analytics")
        self.drawRightString(541, 804, "ABES Engineering College, Ghaziabad | ME Dept.")
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.6)
        self.line(54, 798, 541, 798)

        # Running Footer
        self.line(54, 42, 541, 42)
        self.drawString(54, 30, "B.Tech Engineering Project Report — Academic Year 2026–27")
        self.drawRightString(541, 30, f"Page {self._pageNumber} of {total_pages}")
        self.restoreState()


def get_report_styles():
    """Builds a cohesive palette of paragraph styles."""
    styles = getSampleStyleSheet()

    # Primary colors
    c_primary = colors.HexColor("#1E3A8A")   # Deep Navy
    c_secondary = colors.HexColor("#0D9488") # Teal
    c_dark = colors.HexColor("#0F172A")      # Slate 900
    c_body = colors.HexColor("#1E293B")      # Slate 800
    c_muted = colors.HexColor("#64748B")     # Slate 500

    # Custom styles
    styles.add(ParagraphStyle(
        name='CoverCollege',
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        alignment=TA_CENTER,
        textColor=c_primary,
        spaceAfter=4
    ))

    styles.add(ParagraphStyle(
        name='CoverAffil',
        fontName='Helvetica',
        fontSize=10,
        leading=13,
        alignment=TA_CENTER,
        textColor=c_muted,
        spaceAfter=15
    ))

    styles.add(ParagraphStyle(
        name='CoverTitle',
        fontName='Helvetica-Bold',
        fontSize=21,
        leading=26,
        alignment=TA_CENTER,
        textColor=c_primary,
        spaceAfter=12
    ))

    styles.add(ParagraphStyle(
        name='CoverSubtitle',
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        alignment=TA_CENTER,
        textColor=c_secondary,
        spaceAfter=25
    ))

    styles.add(ParagraphStyle(
        name='CoverMeta',
        fontName='Helvetica',
        fontSize=10,
        leading=15,
        alignment=TA_CENTER,
        textColor=c_body
    ))

    styles.add(ParagraphStyle(
        name='ChapterTitle',
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        textColor=c_primary,
        spaceBefore=12,
        spaceAfter=10,
        keepWithNext=True
    ))

    styles.add(ParagraphStyle(
        name='SectionTitle',
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#1E40AF"),
        spaceBefore=10,
        spaceAfter=6,
        keepWithNext=True
    ))

    styles.add(ParagraphStyle(
        name='SubsectionTitle',
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor("#334155"),
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    ))

    styles.add(ParagraphStyle(
        name='ReportBody',
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=c_body,
        alignment=TA_JUSTIFY,
        spaceAfter=7
    ))

    styles.add(ParagraphStyle(
        name='ReportBodyBold',
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=14,
        textColor=c_body,
        alignment=TA_JUSTIFY,
        spaceAfter=7
    ))

    styles.add(ParagraphStyle(
        name='BulletItem',
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=c_body,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4
    ))

    styles.add(ParagraphStyle(
        name='CalloutText',
        fontName='Helvetica-Oblique',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#1E293B")
    ))

    styles.add(ParagraphStyle(
        name='CodeSnippet',
        fontName='Courier',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#0F172A")
    ))

    styles.add(ParagraphStyle(
        name='FigureCaption',
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=12,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#334155"),
        spaceBefore=4,
        spaceAfter=10
    ))

    styles.add(ParagraphStyle(
        name='TableCaption',
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=13,
        alignment=TA_LEFT,
        textColor=colors.HexColor("#1E3A8A"),
        spaceBefore=6,
        spaceAfter=4
    ))

    styles.add(ParagraphStyle(
        name='TableCell',
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=c_body
    ))

    styles.add(ParagraphStyle(
        name='TableCellBold',
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=11,
        textColor=c_body
    ))

    styles.add(ParagraphStyle(
        name='TableCellHeader',
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11.5,
        alignment=TA_CENTER,
        textColor=colors.white
    ))

    return styles


def make_callout(text, title="ENGINEERING PRINCIPLE", bg="#F8FAFC", border="#2563EB", styles=None):
    """Creates a beautiful callout box with a colored left accent border."""
    p_title = Paragraph(f"<b>{title}</b>", ParagraphStyle(
        'CalloutTitle', fontName='Helvetica-Bold', fontSize=8.5, leading=11, textColor=colors.HexColor(border), spaceAfter=3
    ))
    p_body = Paragraph(text, styles['CalloutText'])
    t = Table([[p_title], [p_body]], colWidths=[475])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor(bg)),
        ('LINELEFT', (0,0), (-1,-1), 3.0, colors.HexColor(border)),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
    ]))
    return t


def build_pdf():
    print(f"Building college project report PDF at: {OUTPUT_PDF}")
    doc = SimpleDocTemplate(
        OUTPUT_PDF,
        pagesize=A4,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = get_report_styles()
    story = []

    # =========================================================================
    # 1. COVER PAGE
    # =========================================================================
    story.append(Spacer(1, 20))
    story.append(Paragraph("ABES ENGINEERING COLLEGE, GHAZIABAD", styles['CoverCollege']))
    story.append(Paragraph("Affiliated to Dr. A.P.J. Abdul Kalam Technical University, Uttar Pradesh, Lucknow", styles['CoverAffil']))
    story.append(HRFlowable(width="90%", thickness=1.5, color=colors.HexColor("#1E3A8A"), spaceBefore=5, spaceAfter=25))

    story.append(Spacer(1, 15))
    story.append(Paragraph("B.TECH MINOR / MAJOR PROJECT REPORT", ParagraphStyle('CoverSubTop', fontName='Helvetica-Bold', fontSize=12, leading=16, alignment=TA_CENTER, textColor=colors.HexColor("#475569"))))
    story.append(Paragraph("ON", ParagraphStyle('CoverOn', fontName='Helvetica', fontSize=10, leading=14, alignment=TA_CENTER, textColor=colors.HexColor("#64748B"), spaceAfter=15)))

    story.append(Paragraph("BATTERY CELL IMBALANCE DETECTION USING IOT ANALYTICS", styles['CoverTitle']))
    story.append(Paragraph("A Multi-Layer IoT, Machine Learning & Cloud-Based Real-Time Battery Health Monitoring Architecture", styles['CoverSubtitle']))

    # Clean decorative technical box
    tech_box = Table([[
        Paragraph("<b>Core Domains Integrated:</b><br/>"
                  "• Multi-Cell Lithium-Ion Battery Telemetry (4S Architecture)<br/>"
                  "• Secure TLS-Encrypted MQTT Communication (HiveMQ Cloud / Mosquitto)<br/>"
                  "• Unsupervised Anomaly Detection Pipeline (Isolation Forest)<br/>"
                  "• High-Performance Relational Telemetry Persistence (SQLite WAL Mode)<br/>"
                  "• Interactive Engineering Dashboard with Plotly Trends (Streamlit Framework)<br/>"
                  "• Event-Driven Supervisory Automation & Routing (Node-RED)", styles['CalloutText'])
    ]], colWidths=[420])
    tech_box.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
        ('BOX', (0,0), (-1,-1), 1.0, colors.HexColor("#CBD5E1")),
        ('LEFTPADDING', (0,0), (-1,-1), 14),
        ('RIGHTPADDING', (0,0), (-1,-1), 14),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('ALIGN', (0,0), (-1,-1), 'CENTER')
    ]))
    story.append(tech_box)
    story.append(Spacer(1, 40))

    meta_table_data = [
        [Paragraph("<b>Submitted in Partial Fulfillment for the Award of Degree of</b><br/>"
                   "<b>Bachelor of Technology in Mechanical Engineering</b>", styles['CoverMeta'])],
        [Spacer(1, 15)],
        [Paragraph("<b>Department of Mechanical Engineering</b><br/>"
                   "<b>ABES Engineering College, Ghaziabad</b><br/>"
                   "<b>Academic Year: 2026–2027</b>", styles['CoverMeta'])]
    ]
    meta_table = Table(meta_table_data, colWidths=[470])
    meta_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(meta_table)

    story.append(PageBreak())

    # =========================================================================
    # 2. CERTIFICATE PAGE
    # =========================================================================
    story.append(Paragraph("CERTIFICATE", styles['ChapterTitle']))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1E3A8A"), spaceBefore=2, spaceAfter=20))

    cert_text = (
        "This is to certify that the project entitled <b>'Battery Cell Imbalance Detection Using IoT Analytics'</b> "
        "is a bonafide record of technical work carried out by the student(s) named below in partial fulfillment "
        "of the requirements for the award of the degree of <b>Bachelor of Technology in Mechanical Engineering</b> "
        "at <b>ABES Engineering College, Ghaziabad</b>, affiliated to Dr. A.P.J. Abdul Kalam Technical University, Lucknow, "
        "during the academic year <b>2026–2027</b>.<br/><br/>"
        "The project has been examined and evaluated by the undersigned committee members and approved for academic submission."
    )
    story.append(Paragraph(cert_text, styles['ReportBody']))
    story.append(Spacer(1, 25))

    # Candidate table placeholder
    cand_data = [
        [Paragraph("<b>Student Name(s)</b>", styles['TableCellHeader']),
         Paragraph("<b>University Roll Number</b>", styles['TableCellHeader']),
         Paragraph("<b>Signature</b>", styles['TableCellHeader'])],
        [Paragraph("___________________________________", styles['TableCell']),
         Paragraph("_______________________", styles['TableCell']),
         Paragraph("_______________________", styles['TableCell'])],
        [Paragraph("___________________________________", styles['TableCell']),
         Paragraph("_______________________", styles['TableCell']),
         Paragraph("_______________________", styles['TableCell'])],
        [Paragraph("___________________________________", styles['TableCell']),
         Paragraph("_______________________", styles['TableCell']),
         Paragraph("_______________________", styles['TableCell'])],
    ]
    t_cand = Table(cand_data, colWidths=[200, 140, 135])
    t_cand.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E3A8A")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('ALIGN', (1,1), (-1,-1), 'CENTER'),
    ]))
    story.append(t_cand)
    story.append(Spacer(1, 45))

    # Signatures block
    sig_data = [
        [Paragraph("<b>Project Guide / Supervisor</b><br/><br/><br/>____________________________<br/>Name: ______________________<br/>Designation: ________________", styles['TableCell']),
         Paragraph("<b>Head of Department</b><br/><br/><br/>____________________________<br/>Department of Mechanical Engineering<br/>ABES Engineering College, Ghaziabad", styles['TableCell'])],
        [Spacer(1, 20), Spacer(1, 20)],
        [Paragraph("<b>Date:</b> ________________________", styles['TableCell']),
         Paragraph("<b>Internal / External Examiner:</b> ____________________", styles['TableCell'])]
    ]
    t_sig = Table(sig_data, colWidths=[235, 240])
    t_sig.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_sig)

    story.append(PageBreak())

    # =========================================================================
    # 3. CANDIDATE DECLARATION
    # =========================================================================
    story.append(Paragraph("CANDIDATE DECLARATION", styles['ChapterTitle']))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1E3A8A"), spaceBefore=2, spaceAfter=20))

    decl_text = (
        "I/We hereby declare that the work presented in this project report entitled <b>'Battery Cell Imbalance "
        "Detection Using IoT Analytics'</b> in partial fulfillment of the requirements for the degree of "
        "<b>Bachelor of Technology in Mechanical Engineering</b> submitted to <b>ABES Engineering College, Ghaziabad</b>, "
        "is an authentic record of our own work carried out under the supervision of our project guide.<br/><br/>"
        "We have not submitted the embodied matter herein for the award of any other degree or diploma to any other "
        "institute or university. All sources of technical literature, software frameworks, algorithms, and libraries "
        "have been properly cited and acknowledged."
    )
    story.append(Paragraph(decl_text, styles['ReportBody']))
    story.append(Spacer(1, 40))

    decl_sign_table = [
        [Paragraph("<b>Date:</b> ____________________", styles['TableCell']),
         Paragraph("<b>Candidate Signature(s):</b><br/><br/>1. __________________________________<br/><br/>2. __________________________________<br/><br/>3. __________________________________", styles['TableCell'])],
        [Paragraph("<b>Place:</b> Ghaziabad, U.P.", styles['TableCell']), Paragraph("", styles['TableCell'])]
    ]
    t_decl_sign = Table(decl_sign_table, colWidths=[200, 275])
    t_decl_sign.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_decl_sign)

    story.append(PageBreak())

    # =========================================================================
    # 4. ACKNOWLEDGEMENT
    # =========================================================================
    story.append(Paragraph("ACKNOWLEDGEMENT", styles['ChapterTitle']))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1E3A8A"), spaceBefore=2, spaceAfter=20))

    ack_text = (
        "The successful completion of this project is a result of the guidance, support, and encouragement received "
        "from esteemed faculty members, institutional leadership, and colleagues.<br/><br/>"
        "First and foremost, we express our profound gratitude to our <b>Project Supervisor / Guide</b> for their invaluable "
        "technical guidance, insightful feedback, and continuous mentorship throughout the architectural design, modeling, "
        "and validation phases of this project.<br/><br/>"
        "We extend our sincere thanks to the <b>Head of the Department of Mechanical Engineering</b> for providing the requisite "
        "computing infrastructure, laboratory resources, and academic environment conducive to multi-disciplinary IoT research.<br/><br/>"
        "We also acknowledge the Director and Management of <b>ABES Engineering College, Ghaziabad</b>, for fostering an academic "
        "ecosystem emphasizing advanced agentic computing, renewable energy storage systems, and applied artificial intelligence.<br/><br/>"
        "Finally, we are grateful to our family members, peers, and friends whose unwavering encouragement and patience "
        "sustained our dedication throughout this academic endeavor."
    )
    story.append(Paragraph(ack_text, styles['ReportBody']))
    story.append(Spacer(1, 30))
    story.append(Paragraph("<b>Project Team Members</b><br/>Department of Mechanical Engineering<br/>ABES Engineering College, Ghaziabad", styles['ReportBody']))

    story.append(PageBreak())

    # =========================================================================
    # 5. ABSTRACT
    # =========================================================================
    story.append(Paragraph("ABSTRACT", styles['ChapterTitle']))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1E3A8A"), spaceBefore=2, spaceAfter=18))

    abstract_text_1 = (
        "Lithium-ion battery packs deployed in Electric Vehicles (EVs) and stationary Battery Energy Storage Systems (BESS) "
        "comprise multiple electrochemical cells connected in series to achieve necessary terminal voltages. Inherent manufacturing "
        "tolerances, spatial thermal gradients, internal impedance degradation, and non-uniform chemical aging inevitably lead to "
        "<b>cell-to-cell voltage imbalance</b> over operational life cycles. If undetected, voltage divergence restricts total usable capacity, "
        "provokes premature cell under-voltage cut-offs, accelerates electrode degradation, and significantly heightens the hazard of localized "
        "thermal runaway. Traditional battery monitoring units frequently rely upon hardwired analog comparators that provide zero historical trend "
        "preservation, no remote cloud visibility, and no predictive anomaly recognition."
    )
    story.append(Paragraph(abstract_text_1, styles['ReportBody']))

    abstract_text_2 = (
        "This project presents the design, mathematical formulation, full-stack implementation, and automated validation of a robust, "
        "six-layer <b>Battery Cell Imbalance Detection System Using IoT Analytics</b>. The platform supports dual acquisition streams: "
        "a physical ESP32 microcontroller edge node incorporating multi-stage analog voltage divider circuits and 10k NTC thermistors, and a "
        "physics-informed synthetic battery telemetry generator capable of simulating nominal discharge, progressive single-cell divergence, "
        "thermal spikes, sensor short circuits, and packet dropouts. Telemetry packets are structured in standardized JSON and transmitted "
        "over MQTT with TLS encryption (Port 8883) via <b>HiveMQ Cloud</b>, featuring local Mosquitto fallback and automatic exponential reconnection."
    )
    story.append(Paragraph(abstract_text_2, styles['ReportBody']))

    abstract_text_3 = (
        "Inbound telemetry is ingested by a multi-threaded Python backend that enforces physical sanity validation, computes core metrics "
        "(V_max, V_min, delta_V, delta_V_mV, mean_V, T_max, and thermal gradients), and persists records to a thread-safe <b>SQLite</b> database "
        "operating in Write-Ahead Logging (WAL) mode. Diagnostic evaluation is driven by a dual-track analytical engine: a strict deterministic "
        "rule-based hierarchy prioritizing critical alarms over warnings, and an unsupervised <b>Isolation Forest Machine Learning</b> model "
        "evaluating multi-dimensional electro-thermal vectors. Supervisory stream branching is demonstrated via <b>Node-RED</b>, while real-time "
        "telemetry, Plotly historical charts, and operator alert acknowledgements are visualized via a <b>Streamlit</b> web dashboard."
    )
    story.append(Paragraph(abstract_text_3, styles['ReportBody']))

    abstract_text_4 = (
        "Rigorous verification through an automated Pytest suite demonstrated a <b>100% test pass rate across all 28 unit and integration test cases</b>. "
        "The machine learning anomaly detector attained <b>100.0% recall</b> on held-out test splits, verifying zero missed critical imbalance states. "
        "The completed platform establishes a highly portable, cost-effective, and reproducible diagnostic framework tailored for modern battery health management."
    )
    story.append(Paragraph(abstract_text_4, styles['ReportBody']))
    story.append(Spacer(1, 10))

    kw_box = Table([[
        Paragraph("<b>Keywords:</b> Battery Management Systems (BMS), Cell Imbalance, Voltage Spread (ΔV), IoT Analytics, "
                  "MQTT Protocol, HiveMQ Cloud, Isolation Forest, Anomaly Detection, ESP32, Streamlit, SQLite WAL.", styles['CalloutText'])
    ]], colWidths=[475])
    kw_box.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F1F5F9")),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(kw_box)

    story.append(PageBreak())

    # =========================================================================
    # 6. TABLE OF CONTENTS, LIST OF FIGURES, LIST OF TABLES, ABBREVIATIONS
    # =========================================================================
    story.append(Paragraph("TABLE OF CONTENTS", styles['ChapterTitle']))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1E3A8A"), spaceBefore=2, spaceAfter=14))

    toc_data = [
        [Paragraph("<b>Chapter</b>", styles['TableCellBold']), Paragraph("<b>Title</b>", styles['TableCellBold']), Paragraph("<b>Page</b>", styles['TableCellBold'])],
        [Paragraph("—", styles['TableCell']), Paragraph("Certificate & Declarations", styles['TableCell']), Paragraph("ii – iii", styles['TableCell'])],
        [Paragraph("—", styles['TableCell']), Paragraph("Acknowledgement", styles['TableCell']), Paragraph("iv", styles['TableCell'])],
        [Paragraph("—", styles['TableCell']), Paragraph("Abstract", styles['TableCell']), Paragraph("v", styles['TableCell'])],
        [Paragraph("—", styles['TableCell']), Paragraph("List of Figures, Tables & Abbreviations", styles['TableCell']), Paragraph("vii – viii", styles['TableCell'])],
        [Paragraph("<b>1</b>", styles['TableCellBold']), Paragraph("<b>Introduction</b>", styles['TableCellBold']), Paragraph("1", styles['TableCell'])],
        [Paragraph("<b>2</b>", styles['TableCellBold']), Paragraph("<b>Problem Statement</b>", styles['TableCellBold']), Paragraph("3", styles['TableCell'])],
        [Paragraph("<b>3</b>", styles['TableCellBold']), Paragraph("<b>Project Objectives</b>", styles['TableCellBold']), Paragraph("4", styles['TableCell'])],
        [Paragraph("<b>4</b>", styles['TableCellBold']), Paragraph("<b>Literature and Technology Background</b>", styles['TableCellBold']), Paragraph("5", styles['TableCell'])],
        [Paragraph("<b>5</b>", styles['TableCellBold']), Paragraph("<b>Proposed System Architecture</b>", styles['TableCellBold']), Paragraph("7", styles['TableCell'])],
        [Paragraph("<b>6</b>", styles['TableCellBold']), Paragraph("<b>Detailed Layer-by-Layer Implementation</b>", styles['TableCellBold']), Paragraph("9", styles['TableCell'])],
        [Paragraph("", styles['TableCell']), Paragraph("&nbsp;&nbsp;6.1 Layer 1: Synthetic Telemetry Generation, Noise Modeling & Local CSV Ingestion", styles['TableCell']), Paragraph("9", styles['TableCell'])],
        [Paragraph("", styles['TableCell']), Paragraph("&nbsp;&nbsp;6.2 Layer 2: MQTT Communication & HiveMQ Cloud Integration", styles['TableCell']), Paragraph("11", styles['TableCell'])],
        [Paragraph("", styles['TableCell']), Paragraph("&nbsp;&nbsp;6.3 Layer 3: Relational Persistence Layer (SQLite WAL Mode)", styles['TableCell']), Paragraph("13", styles['TableCell'])],
        [Paragraph("", styles['TableCell']), Paragraph("&nbsp;&nbsp;6.4 Layer 4: Node-RED Automation & Supervisory Event Flow", styles['TableCell']), Paragraph("15", styles['TableCell'])],
        [Paragraph("", styles['TableCell']), Paragraph("&nbsp;&nbsp;6.5 Layer 5: Machine Learning Anomaly Detection, Authentication & Alerts", styles['TableCell']), Paragraph("17", styles['TableCell'])],
        [Paragraph("", styles['TableCell']), Paragraph("&nbsp;&nbsp;6.6 Layer 6: ESP32 Edge Sensor Interface & Hardware Alerts", styles['TableCell']), Paragraph("20", styles['TableCell'])],
        [Paragraph("<b>7</b>", styles['TableCellBold']), Paragraph("<b>Methodology and Operational Workflow</b>", styles['TableCellBold']), Paragraph("23", styles['TableCell'])],
        [Paragraph("<b>8</b>", styles['TableCellBold']), Paragraph("<b>Battery Cell Imbalance Calculations & Mathematical Formulations</b>", styles['TableCellBold']), Paragraph("25", styles['TableCell'])],
        [Paragraph("<b>9</b>", styles['TableCellBold']), Paragraph("<b>Software and Hardware Specifications</b>", styles['TableCellBold']), Paragraph("27", styles['TableCell'])],
        [Paragraph("<b>10</b>", styles['TableCellBold']), Paragraph("<b>Project Folder Structure & Module Architecture</b>", styles['TableCellBold']), Paragraph("28", styles['TableCell'])],
        [Paragraph("<b>11</b>", styles['TableCellBold']), Paragraph("<b>Database Design & Entity Relationships</b>", styles['TableCellBold']), Paragraph("30", styles['TableCell'])],
        [Paragraph("<b>12</b>", styles['TableCellBold']), Paragraph("<b>Dashboard Design & Feature Implementation</b>", styles['TableCellBold']), Paragraph("32", styles['TableCell'])],
        [Paragraph("<b>13</b>", styles['TableCellBold']), Paragraph("<b>Testing, Verification & Acceptance Criteria</b>", styles['TableCellBold']), Paragraph("34", styles['TableCell'])],
        [Paragraph("<b>14</b>", styles['TableCellBold']), Paragraph("<b>Results and Discussion</b>", styles['TableCellBold']), Paragraph("37", styles['TableCell'])],
        [Paragraph("<b>15</b>", styles['TableCellBold']), Paragraph("<b>Practical Advantages</b>", styles['TableCellBold']), Paragraph("39", styles['TableCell'])],
        [Paragraph("<b>16</b>", styles['TableCellBold']), Paragraph("<b>System Limitations</b>", styles['TableCellBold']), Paragraph("40", styles['TableCell'])],
        [Paragraph("<b>17</b>", styles['TableCellBold']), Paragraph("<b>Future Scope</b>", styles['TableCellBold']), Paragraph("41", styles['TableCell'])],
        [Paragraph("<b>18</b>", styles['TableCellBold']), Paragraph("<b>Conclusion</b>", styles['TableCellBold']), Paragraph("42", styles['TableCell'])],
        [Paragraph("<b>19</b>", styles['TableCellBold']), Paragraph("<b>References</b>", styles['TableCellBold']), Paragraph("43", styles['TableCell'])],
    ]
    t_toc = Table(toc_data, colWidths=[45, 385, 45])
    t_toc.setStyle(TableStyle([
        ('LINEBELOW', (0,0), (-1,0), 0.8, colors.HexColor("#1E3A8A")),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('ALIGN', (0,0), (0,-1), 'CENTER'),
        ('ALIGN', (2,0), (2,-1), 'RIGHT'),
    ]))
    story.append(t_toc)

    story.append(Spacer(1, 15))
    story.append(Paragraph("LIST OF FIGURES", styles['SectionTitle']))
    figures_list = [
        [Paragraph("Figure 1", styles['TableCellBold']), Paragraph("Overall System Architecture: 6-Layer Integrated Pipeline", styles['TableCell']), Paragraph("Page 8", styles['TableCell'])],
        [Paragraph("Figure 2", styles['TableCellBold']), Paragraph("MQTT Publish-Subscribe Communication Architecture", styles['TableCell']), Paragraph("Page 12", styles['TableCell'])],
        [Paragraph("Figure 3", styles['TableCellBold']), Paragraph("Isolation Forest Anomaly Detection Confusion Matrix & Metrics", styles['TableCell']), Paragraph("Page 19", styles['TableCell'])],
        [Paragraph("Figure 4", styles['TableCellBold']), Paragraph("Demonstration of Cell Voltage Divergence Across Operational Scenarios", styles['TableCell']), Paragraph("Page 26", styles['TableCell'])],
        [Paragraph("Figure 5", styles['TableCellBold']), Paragraph("ESP32 4S Battery Sensing & Hardware Alert Interface Schematic", styles['TableCell']), Paragraph("Page 22", styles['TableCell'])],
        [Paragraph("Figure 6", styles['TableCellBold']), Paragraph("Automated Test Suite Execution Results (Pytest Verification)", styles['TableCell']), Paragraph("Page 35", styles['TableCell'])],
    ]
    t_figs = Table(figures_list, colWidths=[65, 355, 55])
    t_figs.setStyle(TableStyle([
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('ALIGN', (2,0), (2,-1), 'RIGHT'),
    ]))
    story.append(t_figs)

    story.append(Spacer(1, 12))
    story.append(Paragraph("LIST OF TABLES", styles['SectionTitle']))
    tables_list = [
        [Paragraph("Table 1", styles['TableCellBold']), Paragraph("Conventional BMS vs. Proposed IoT & ML Monitoring System", styles['TableCell']), Paragraph("Page 4", styles['TableCell'])],
        [Paragraph("Table 2", styles['TableCellBold']), Paragraph("Inbound Battery Telemetry JSON Schema Specification", styles['TableCell']), Paragraph("Page 10", styles['TableCell'])],
        [Paragraph("Table 3", styles['TableCellBold']), Paragraph("ESP32 4S Voltage Divider Resistor Network Specifications", styles['TableCell']), Paragraph("Page 21", styles['TableCell'])],
        [Paragraph("Table 4", styles['TableCellBold']), Paragraph("Bill of Materials (BOM) and Estimated Prototype Cost", styles['TableCell']), Paragraph("Page 22", styles['TableCell'])],
        [Paragraph("Table 5", styles['TableCellBold']), Paragraph("Software Specifications and Framework Dependencies", styles['TableCell']), Paragraph("Page 27", styles['TableCell'])],
        [Paragraph("Table 6", styles['TableCellBold']), Paragraph("Hardware Prototype Component Specifications", styles['TableCell']), Paragraph("Page 27", styles['TableCell'])],
        [Paragraph("Table 7", styles['TableCellBold']), Paragraph("SQLite Database Schema — Table: battery_readings", styles['TableCell']), Paragraph("Page 30", styles['TableCell'])],
        [Paragraph("Table 8", styles['TableCellBold']), Paragraph("Comprehensive Automated Test Verification Suite (28 Test Cases)", styles['TableCell']), Paragraph("Page 36", styles['TableCell'])],
    ]
    t_tabs = Table(tables_list, colWidths=[65, 355, 55])
    t_tabs.setStyle(TableStyle([
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('ALIGN', (2,0), (2,-1), 'RIGHT'),
    ]))
    story.append(t_tabs)

    story.append(Spacer(1, 12))
    story.append(Paragraph("LIST OF ABBREVIATIONS", styles['SectionTitle']))
    abbrev_data = [
        [Paragraph("<b>ADC</b>", styles['TableCell']), Paragraph("Analog-to-Digital Converter", styles['TableCell']),
         Paragraph("<b>ML</b>", styles['TableCell']), Paragraph("Machine Learning", styles['TableCell'])],
        [Paragraph("<b>BESS</b>", styles['TableCell']), Paragraph("Battery Energy Storage System", styles['TableCell']),
         Paragraph("<b>MQTT</b>", styles['TableCell']), Paragraph("Message Queuing Telemetry Transport", styles['TableCell'])],
        [Paragraph("<b>BMS</b>", styles['TableCell']), Paragraph("Battery Management System", styles['TableCell']),
         Paragraph("<b>NTC</b>", styles['TableCell']), Paragraph("Negative Temperature Coefficient", styles['TableCell'])],
        [Paragraph("<b>CSV</b>", styles['TableCell']), Paragraph("Comma-Separated Values", styles['TableCell']),
         Paragraph("<b>QoS</b>", styles['TableCell']), Paragraph("Quality of Service", styles['TableCell'])],
        [Paragraph("<b>DMM</b>", styles['TableCell']), Paragraph("Digital Multimeter", styles['TableCell']),
         Paragraph("<b>SoC</b>", styles['TableCell']), Paragraph("State of Charge", styles['TableCell'])],
        [Paragraph("<b>EV</b>", styles['TableCell']), Paragraph("Electric Vehicle", styles['TableCell']),
         Paragraph("<b>SoH</b>", styles['TableCell']), Paragraph("State of Health", styles['TableCell'])],
        [Paragraph("<b>GPIO</b>", styles['TableCell']), Paragraph("General Purpose Input/Output", styles['TableCell']),
         Paragraph("<b>TLS</b>", styles['TableCell']), Paragraph("Transport Layer Security", styles['TableCell'])],
        [Paragraph("<b>IoT</b>", styles['TableCell']), Paragraph("Internet of Things", styles['TableCell']),
         Paragraph("<b>WAL</b>", styles['TableCell']), Paragraph("Write-Ahead Logging", styles['TableCell'])],
    ]
    t_abb = Table(abbrev_data, colWidths=[55, 180, 55, 185])
    t_abb.setStyle(TableStyle([
        ('TOPPADDING', (0,0), (-1,-1), 1.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1.5),
    ]))
    story.append(t_abb)

    story.append(PageBreak())

    # =========================================================================
    # CHAPTER 1: INTRODUCTION
    # =========================================================================
    story.append(Paragraph("1. INTRODUCTION", styles['ChapterTitle']))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1E3A8A"), spaceBefore=2, spaceAfter=14))

    story.append(Paragraph("1.1 Background and Importance of Battery Energy Storage", styles['SectionTitle']))
    p1 = (
        "The global transition toward clean mobility, electric traction, and decentralized renewable energy infrastructure "
        "has established Lithium-Ion electrochemical batteries as the predominant energy storage medium. Modern Electric Vehicles (EVs), "
        "hybrid powertrains, automated guided vehicles (AGVs), solar microgrids, and uninterrupted power supply (UPS) installations "
        "require substantial voltages ranging from 48V to upwards of 800V. Because an individual commercial lithium-ion cell provides a nominal "
        "terminal potential between 3.2V (Lithium Iron Phosphate — LiFePO4) and 3.7V (Lithium Nickel Manganese Cobalt — NMC / Lithium Cobalt Oxide — LCO), "
        "battery packs are assembled by stringing multiple individual electrochemical cells in series (and parallel strings) to satisfy load voltage and power demands."
    )
    story.append(Paragraph(p1, styles['ReportBody']))

    story.append(Paragraph("1.2 The Phenomenon of Battery Cell Imbalance", styles['SectionTitle']))
    p2 = (
        "In an theoretically ideal battery pack, all series-connected cells would exhibit identical chemical capacity (Ah), identical internal DC resistance (ESR), "
        "and identical state-of-charge (SoC) percentages under all operating regimes. However, in practical engineering implementations, <b>cell imbalance is an "
        "unavoidable physical reality</b> resulting from several compounding factors:<br/>"
        "• <b>Manufacturing Non-Uniformities:</b> Microscopic variations in active cathode material coating thickness, separator porosity, and electrolyte volume cause cell capacities to vary by ±1% to ±3% even within the same production batch.<br/>"
        "• <b>Spatial Thermal Gradients:</b> Cells located in the center of a pack experience poorer convective heat rejection than exterior perimeter cells. Elevated temperatures accelerate internal parasitic side-reactions (SEI layer growth), causing center cells to age and self-discharge faster.<br/>"
        "• <b>Differential Self-Discharge Rates:</b> Over calendar life and idling periods, individual cells lose charge at uneven rates, causing state-of-charge drift.<br/>"
        "• <b>Unequal Degradation Impedance:</b> As cells undergo charge-discharge cycling, internal resistance rises non-uniformly, inducing disparate resistive (I·R) voltage drops under high current draws."
    )
    story.append(Paragraph(p2, styles['ReportBody']))

    story.append(Paragraph("1.3 Engineering Consequences of Uncorrected Cell Imbalance", styles['SectionTitle']))
    p3 = (
        "When individual cells diverge in terminal voltage and capacity, severe operational consequences emerge:<br/>"
        "1. <b>Loss of Pack Usable Capacity:</b> In a series circuit, total pack current is constrained by the weakest cell. During discharge, the cell with the lowest capacity reaches the cut-off threshold (e.g., 3.0V) first, forcing the battery management system to cut power while higher-capacity cells still hold unused charge.<br/>"
        "2. <b>Accelerated Cell Aging & Premature Failure:</b> The diverging cell is subjected to deeper cycling stress, accelerating irreversible capacity loss and internal resistance rise in a vicious degradation loop.<br/>"
        "3. <b>Catastrophic Thermal Runaway Hazards:</b> During rapid recharge, a cell with lower capacity reaches maximum cutoff potential (4.20V) before others. Overcharging leads to lithium plating on the graphite anode, dendrite formation, separator puncture, and exothermic thermal runaway."
    )
    story.append(Paragraph(p3, styles['ReportBody']))

    story.append(Paragraph("1.4 The Role of IoT Analytics and Real-Time Telemetry", styles['SectionTitle']))
    p4 = (
        "Traditional localized analog battery monitoring units alert operators only after a catastrophic breach has occurred (e.g., blowing a thermal fuse). "
        "They offer zero historical trend retention, no mathematical rate-of-change analysis, and no remote operational visibility. "
        "Integrating <b>Internet of Things (IoT) edge telemetry</b> with lightweight publish-subscribe protocols (MQTT), persistent relational databases, "
        "and cloud visualization transforms battery safety management from reactive emergency intervention into <b>predictive health diagnostics</b>. "
        "Continuous tracking of individual cell voltages and surface temperatures allows operators to detect micro-volt imbalances long before they escalate "
        "into dangerous thermal or electrochemical failures."
    )
    story.append(Paragraph(p4, styles['ReportBody']))

    story.append(Spacer(1, 5))
    story.append(make_callout(
        "\"In a series battery pack, pack reliability is strictly governed by the weakest electrochemical cell. "
        "A 30 mV voltage spread that remains unaddressed can lead to localized cell over-discharge, permanent copper dissolution, "
        "and catastrophic pack decommissioning. Early cloud-based telemetry detection is the cornerstone of modern battery safety.\"",
        title="FUNDAMENTAL BATTERY ENGINEERING AXIOM", border="#0D9488", bg="#F0FDFA", styles=styles
    ))

    story.append(PageBreak())

    # =========================================================================
    # CHAPTER 2 & 3: PROBLEM STATEMENT & OBJECTIVES
    # =========================================================================
    story.append(Paragraph("2. PROBLEM STATEMENT", styles['ChapterTitle']))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1E3A8A"), spaceBefore=2, spaceAfter=14))

    ps_text = (
        "Modern energy storage installations lack continuous, multi-dimensional diagnostic visibility at the individual cell level. "
        "Conventional battery monitoring architectures present several fundamental engineering shortcomings:<br/>"
        "• <b>Absence of Historical Record Keeping:</b> Standard Battery Management Systems (BMS) evaluate instantaneous analog thresholds but do not persist telemetry. Without chronological historical trends, maintenance engineers cannot evaluate degradation trajectories or determine whether an imbalance is acute or gradual.<br/>"
        "• <b>Lack of Remote Fleet Visibility:</b> Field assets (EV fleets, solar storage stations) operate autonomously without centralized telemetry broadcasting, requiring manual technician visits with handheld multimeters to diagnose cell divergences.<br/>"
        "• <b>Rigid Thresholds Without Intelligent Anomaly Recognition:</b> Fixed analog comparators cannot differentiate between harmless transient voltage dips caused by sudden motor acceleration and persistent internal resistance defects.<br/>"
        "• <b>Alarm Fatigue & Flooding:</b> Naive monitoring software repeatedly fires alarm notifications every two seconds during an ongoing fault condition, overwhelming operator logs and obscuring state transitions.<br/>"
        "• <b>Hardware Dependency in Research:</b> Educational institutions and development laboratories frequently lack safe, non-destructive means to test hazardous battery fault conditions (thermal runaway, dead cell shorts) without destroying physical cells."
    )
    story.append(Paragraph(ps_text, styles['ReportBody']))

    story.append(Spacer(1, 10))
    story.append(Paragraph("3. PROJECT OBJECTIVES", styles['ChapterTitle']))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1E3A8A"), spaceBefore=2, spaceAfter=14))

    obj_text = (
        "To resolve these engineering limitations, this project was undertaken with the following specific, verifiable technical objectives:<br/>"
        "1. <b>Multi-Scenario Synthetic Telemetry Engine (Layer 1):</b> Develop a mathematical battery simulator generating realistic 4-cell voltage, temperature, and current readings with Gaussian measurement noise and configurable fault scenarios.<br/>"
        "2. <b>Secure IoT Cloud Communication (Layer 2):</b> Implement an MQTT client pipeline supporting TLS-secured broker communication via HiveMQ Cloud (Port 8883) and local Mosquitto brokers with automatic backoff reconnection.<br/>"
        "3. <b>Thread-Safe Relational Telemetry Storage (Layer 3):</b> Design a persistent SQLite database schema using Write-Ahead Logging (WAL) mode for storing raw cell voltages, temperatures, derived mathematical spreads, and alert records.<br/>"
        "4. <b>Supervisory Event Flow Automation (Layer 4):</b> Implement a Node-RED automation flow for independent multi-stream payload routing, validation, and secondary alarm publication.<br/>"
        "5. <b>Unsupervised AI/ML Anomaly Detection Pipeline (Layer 5):</b> Train and persist an Isolation Forest machine learning model to evaluate multi-variable feature vectors (spread, peak voltage, thermal gradient, load current) with graceful fallback to rule-based detection.<br/>"
        "6. <b>Secure Role-Based Dashboard & Alert Management (Layer 5):</b> Build an interactive Streamlit engineering dashboard with authenticated login, real-time Plotly charts, deviation sanity matrices, and alert acknowledgement workflows.<br/>"
        "7. <b>Physical Microcontroller Interfacing (Layer 6):</b> Provide complete C++ firmware and calibrated circuit schematics for an ESP32 edge node to monitor 4S cells via resistor divider networks and NTC surface thermistors.<br/>"
        "8. <b>Automated Verification Suite:</b> Implement and execute a comprehensive 28-test Pytest suite achieving 100% pass verification."
    )
    story.append(Paragraph(obj_text, styles['ReportBody']))

    story.append(Spacer(1, 10))
    # Table 1: Conventional vs Proposed
    story.append(Paragraph("Table 1: Conventional BMS vs. Proposed IoT & ML Monitoring System", styles['TableCaption']))
    comp_data = [
        [Paragraph("<b>Evaluation Dimension</b>", styles['TableCellHeader']),
         Paragraph("<b>Conventional Local BMS</b>", styles['TableCellHeader']),
         Paragraph("<b>Proposed IoT & ML Platform</b>", styles['TableCellHeader'])],
        [Paragraph("<b>Data Transmission</b>", styles['TableCellBold']),
         Paragraph("None or localized wired CAN bus", styles['TableCell']),
         Paragraph("Global cloud MQTT over TLS 8883 + JSON", styles['TableCell'])],
        [Paragraph("<b>Historical Analytics</b>", styles['TableCellBold']),
         Paragraph("Ephemeral; lost on power cycle", styles['TableCell']),
         Paragraph("Persistent SQLite WAL database + CSV export", styles['TableCell'])],
        [Paragraph("<b>Analytical Method</b>", styles['TableCellBold']),
         Paragraph("Fixed analog comparator circuit", styles['TableCell']),
         Paragraph("Dual-Track: Rule hierarchy + Isolation Forest ML", styles['TableCell'])],
        [Paragraph("<b>Visualization</b>", styles['TableCellBold']),
         Paragraph("Blinking onboard fault LED / buzzer", styles['TableCell']),
         Paragraph("Interactive web dashboard with Plotly charts", styles['TableCell'])],
        [Paragraph("<b>Operator Workflow</b>", styles['TableCellBold']),
         Paragraph("Manual DMM probing required", styles['TableCell']),
         Paragraph("Remote web console + Alert acknowledgement", styles['TableCell'])],
        [Paragraph("<b>Testing Flexibility</b>", styles['TableCellBold']),
         Paragraph("Requires destructive physical pack testing", styles['TableCell']),
         Paragraph("Integrated 5-scenario physics simulator", styles['TableCell'])],
    ]
    t_comp = Table(comp_data, colWidths=[120, 175, 180])
    t_comp.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E3A8A")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor("#FFFFFF"), colors.HexColor("#F8FAFC")]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_comp)

    story.append(PageBreak())

    # =========================================================================
    # CHAPTER 4: LITERATURE & TECHNOLOGY BACKGROUND
    # =========================================================================
    story.append(Paragraph("4. LITERATURE AND TECHNOLOGY BACKGROUND", styles['ChapterTitle']))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1E3A8A"), spaceBefore=2, spaceAfter=14))

    p_tech1 = (
        "<b>4.1 Battery Management System (BMS) Architecture:</b> A standard BMS provides first-line electrical protection "
        "by monitoring aggregate pack voltage, individual cell balance taps, pack current, and module temperatures. "
        "Industrial BMS units execute passive cell balancing by switching bypass resistors (bleeding resistors) across higher-voltage "
        "cells during the final constant-voltage (CV) charging phase. However, conventional BMS hardware lacks onboard compute resources "
        "to execute multivariate machine learning, store historical trends over months of operation, or expose interactive user interfaces.<br/><br/>"
        "<b>4.2 The MQTT Protocol & IoT Messaging:</b> Message Queuing Telemetry Transport (MQTT) is an ISO standard (ISO/IEC 20922) "
        "extremely lightweight publish-subscribe network protocol designed for constrained remote devices with limited bandwidth and high latency. "
        "Unlike HTTP which requires request-response polling and carries heavy text headers (~1 KB), MQTT uses an ultra-compact binary packet header "
        "(just 2 bytes), persistent TCP connections, and Quality of Service (QoS) guarantees (QoS 0, 1, 2). "
        "QoS 1 (At least once delivery) guarantees that critical battery fault telemetry frames are delivered even over intermittent wireless networks.<br/><br/>"
        "<b>4.3 Cloud Broker Infrastructure (HiveMQ Cloud):</b> HiveMQ Cloud provides an enterprise-grade, serverless MQTT broker cluster "
        "capable of maintaining millions of simultaneous concurrent connections. Transport Layer Security (TLS 1.2/1.3) over TCP port 8883 "
        "encrypts telemetry in transit, preventing man-in-the-middle tampering with industrial battery alarms.<br/><br/>"
        "<b>4.4 SQLite Relational Database & Write-Ahead Logging:</b> SQLite is an embedded, serverless, self-contained SQL database engine. "
        "By activating Write-Ahead Logging (WAL mode via <code>PRAGMA journal_mode=WAL;</code>), SQLite enables concurrent readers to execute historical "
        "time-series queries simultaneously while an ingestion thread inserts streaming telemetry, eliminating file lock collisions.<br/><br/>"
        "<b>4.5 Node-RED Event-Driven Orchestration:</b> Developed originally by IBM, Node-RED provides a browser-based visual flow editor for wiring "
        "together hardware devices, APIs, and online services. Its event-driven, non-blocking execution model (Node.js) makes it ideal for supervisory "
        "routing and alerting parallel to core analytical backends.<br/><br/>"
        "<b>4.6 Streamlit Reactive Web Framework:</b> Streamlit is a Python-native reactive application framework for data science and IoT engineering. "
        "It redraws dashboard widgets upon state changes without requiring complex front-end JavaScript boilerplate, facilitating rapid visualization of "
        "dynamic battery telemetry.<br/><br/>"
        "<b>4.7 ESP32 Microcontroller:</b> Manufactured by Espressif Systems, the ESP32 features a dual-core 32-bit Xtensa LX6 microprocessor operating "
        "at up to 240 MHz, integrated 2.4 GHz Wi-Fi (802.11 b/g/n), Bluetooth LE, and two 12-bit SAR Analog-to-Digital Converters (ADCs). Its low unit cost "
        "and hardware cryptography accelerators make it an ideal edge IoT sensing gateway.<br/><br/>"
        "<b>4.8 Isolation Forest Anomaly Detection Algorithm:</b> Introduced by Liu, Ting, and Zhou (2008), the Isolation Forest algorithm isolates anomalies "
        "by randomly selecting a feature and randomly selecting a split value between the maximum and minimum values of the selected feature. "
        "Because anomalies (e.g. severe voltage spread combined with high temperature) are few and structurally distinct from nominal operation, "
        "they are isolated closer to the root of the trees in an ensemble of random trees (shorter average path lengths), offering computational complexity "
        "of O(n) and high sensitivity."
    )
    story.append(Paragraph(p_tech1, styles['ReportBody']))

    story.append(PageBreak())

    # =========================================================================
    # CHAPTER 5: PROPOSED SYSTEM ARCHITECTURE
    # =========================================================================
    story.append(Paragraph("5. PROPOSED SYSTEM ARCHITECTURE", styles['ChapterTitle']))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1E3A8A"), spaceBefore=2, spaceAfter=14))

    p_arch = (
        "The proposed system architecture is organized into six interconnected, modular functional layers designed to decouple "
        "data collection, transport, storage, intelligence, visualization, and edge physical response. Figure 1 illustrates the overall "
        "data flow from edge sensor acquisition through to operator visualization and cloud alerting."
    )
    story.append(Paragraph(p_arch, styles['ReportBody']))

    # Embed Figure 1
    fig1_path = os.path.join(FIGURES_DIR, "fig1_system_architecture.png")
    if os.path.exists(fig1_path):
        story.append(Spacer(1, 4))
        story.append(Image(fig1_path, width=475, height=300))
        story.append(Paragraph("Figure 1: Overall System Architecture — 6-Layer Integrated Pipeline", styles['FigureCaption']))
    story.append(Spacer(1, 8))

    p_arch_desc = (
        "<b>Architectural Workflow Breakdown:</b><br/>"
        "1. <b>Acquisition Stage:</b> Physical voltages and surface temperatures from a 4S battery pack are sampled by the ESP32 node, or synthetically generated by the Python simulator.<br/>"
        "2. <b>Serialization & Ingestion:</b> Telemetry is packaged as a UTF-8 JSON payload and published to MQTT topic <code>battery/cells/data</code> at 2.0-second intervals.<br/>"
        "3. <b>Transport Stage:</b> The MQTT Broker (HiveMQ Cloud over TLS 8883 or local Mosquitto on 1883) receives and distributes packets to subscribed consumers.<br/>"
        "4. <b>Analytical Ingestion:</b> The Python backend subscriber deserializes and sanitizes payloads, runs core mathematical calculations (V_max, V_min, ΔV, ΔV_mV), and assesses sensor quality.<br/>"
        "5. <b>Dual-Track Diagnostic Engine:</b> Evaluates operational status through deterministic rule hierarchy (Critical > Warning > Normal) and runs Isolation Forest ML inference.<br/>"
        "6. <b>Persistence Stage:</b> Normalized readings and alert events are inserted into SQLite (WAL mode) using parameterized SQL queries.<br/>"
        "7. <b>Presentation & Edge Response:</b> Streamlit provides interactive web visualization and alert acknowledgement; the ESP32 triggers local alert LEDs and buzzer alarms."
    )
    story.append(Paragraph(p_arch_desc, styles['ReportBody']))

    story.append(PageBreak())

    # =========================================================================
    # CHAPTER 6: DETAILED LAYER-BY-LAYER IMPLEMENTATION
    # =========================================================================
    story.append(Paragraph("6. DETAILED LAYER-BY-LAYER IMPLEMENTATION", styles['ChapterTitle']))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1E3A8A"), spaceBefore=2, spaceAfter=14))

    # Layer 1
    story.append(Paragraph("6.1 Layer 1: Synthetic Telemetry Generation, Noise Modeling & Local CSV Ingestion", styles['SectionTitle']))
    p_l1 = (
        "<b>Purpose and Rationale:</b> In laboratory and academic environments, experimenting on physical lithium-ion battery packs "
        "under extreme fault conditions (e.g., short-circuited cells, thermal runaway past 60°C, extreme over-discharge) carries severe fire, "
        "toxic gas emission, and explosion risks. Layer 1 resolves this by implementing a software-based synthetic battery simulator "
        "(<code>src/simulator.py</code>) that accurately reproduces electrochemical discharge slopes, random measurement noise, and configurable operational failure modes.<br/><br/>"
        "<b>Mathematical Modeling of Cell Discharge & Measurement Noise:</b><br/>"
        "For each series cell <i>i</i> at discrete time step <i>k</i>, the synthetic cell voltage <i>V_i(k)</i> is governed by a base discharge decay "
        "coupled with a Gaussian noise process:<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<b>V_i(k) = V_i(k-1) - η_i · I_pack + ε_noise</b><br/>"
        "where <i>η_i</i> represents the effective discharge decay constant (0.0002 V/step under nominal 2.5A discharge), and <i>ε_noise ~ N(0, σ_noise²)</i> "
        "models realistic ADC switching noise with standard deviation <i>σ_noise = 0.0015 V (1.5 mV)</i>.<br/><br/>"
        "<b>Implemented Operational Scenarios:</b><br/>"
        "• <b>1. 'normal':</b> All four cells discharge synchronously with tightly matched voltages (spread ΔV < 15 mV) and nominal temperatures (~28°C).<br/>"
        "• <b>2. 'imbalance':</b> Cell 2 is programmed with a four-fold accelerated discharge rate (<i>η_2 = 4 · η_base</i>), simulating severe capacity loss or high internal resistance. Over successive cycles, Cell 2 diverges, breaching the 20 mV Warning and 50 mV Critical thresholds.<br/>"
        "• <b>3. 'overheating':</b> Cell 3 exhibits localized internal thermal runaway, climbing at +1.8°C per step, rapidly exceeding 45°C (Warning) and 60°C (Critical).<br/>"
        "• <b>4. 'sensor_failure':</b> Cell 1 voltage abruptly drops to 0.0V and temperature reports -40.0°C, simulating a loose terminal wire or grounded ADC line.<br/>"
        "• <b>5. 'missing_data':</b> Emulates packet corruption where Cell 4 readings are dropped (null), testing the system's ability to trap incomplete telemetry."
    )
    story.append(Paragraph(p_l1, styles['ReportBody']))

    story.append(Spacer(1, 4))
    story.append(Paragraph("Table 2: Inbound Battery Telemetry JSON Schema Specification", styles['TableCaption']))
    schema_data = [
        [Paragraph("<b>Field Key</b>", styles['TableCellHeader']),
         Paragraph("<b>Data Type</b>", styles['TableCellHeader']),
         Paragraph("<b>Unit / Format</b>", styles['TableCellHeader']),
         Paragraph("<b>Description / Validation Rule</b>", styles['TableCellHeader'])],
        [Paragraph("<code>pack_id</code>", styles['TableCellBold']), Paragraph("String", styles['TableCell']), Paragraph("Alpha-numeric", styles['TableCell']), Paragraph("Identifier of the battery pack (e.g. 'PACK-01')", styles['TableCell'])],
        [Paragraph("<code>timestamp</code>", styles['TableCellBold']), Paragraph("String / Epoch", styles['TableCell']), Paragraph("ISO 8601 UTC", styles['TableCell']), Paragraph("Transmission timestamp, sanitized to UTC", styles['TableCell'])],
        [Paragraph("<code>mode</code>", styles['TableCellBold']), Paragraph("String", styles['TableCell']), Paragraph("'simulation' | 'hardware'", styles['TableCell']), Paragraph("Operating mode label; never conflated", styles['TableCell'])],
        [Paragraph("<code>source</code>", styles['TableCellBold']), Paragraph("String", styles['TableCell']), Paragraph("Identifier", styles['TableCell']), Paragraph("Originating telemetry generator / ESP32 node", styles['TableCell'])],
        [Paragraph("<code>cell_count</code>", styles['TableCellBold']), Paragraph("Integer", styles['TableCell']), Paragraph("Count (e.g. 4)", styles['TableCell']), Paragraph("Total number of series cells monitored", styles['TableCell'])],
        [Paragraph("<code>cell_voltages</code>", styles['TableCellBold']), Paragraph("List [Float]", styles['TableCell']), Paragraph("Volts (V)", styles['TableCell']), Paragraph("Array of cell potentials; validated finite", styles['TableCell'])],
        [Paragraph("<code>cell_temperatures</code>", styles['TableCellBold']), Paragraph("List [Float]", styles['TableCell']), Paragraph("Degrees Celsius (°C)", styles['TableCell']), Paragraph("Surface contact temperatures per cell", styles['TableCell'])],
        [Paragraph("<code>current_a</code>", styles['TableCellBold']), Paragraph("Float", styles['TableCell']), Paragraph("Amperes (A)", styles['TableCell']), Paragraph("Pack load current (positive = discharge)", styles['TableCell'])],
    ]
    t_sch = Table(schema_data, colWidths=[95, 75, 95, 210])
    t_sch.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E3A8A")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor("#FFFFFF"), colors.HexColor("#F8FAFC")]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_sch)

    story.append(PageBreak())

    # Layer 2
    story.append(Paragraph("6.2 Layer 2: MQTT Communication & HiveMQ Cloud Integration", styles['SectionTitle']))
    p_l2 = (
        "<b>Network Topology and Protocol Selection:</b> Layer 2 implements the communications backbone utilizing Paho-MQTT "
        "(<code>src/mqtt_client.py</code>, <code>src/mqtt_publisher.py</code>, <code>src/mqtt_subscriber.py</code>). "
        "The architecture decouples data producers (ESP32 and Simulator) from consumers (Python Analytical Pipeline and Node-RED).<br/><br/>"
        "<b>Cloud & Local Broker Support:</b><br/>"
        "• <b>HiveMQ Cloud (Production Cloud Mode):</b> Connects over port <b>8883</b> with SSL/TLS encryption. The system creates a default TLS context "
        "using system root CA certificates, ensuring encrypted packet transit across public wide-area networks.<br/>"
        "• <b>Local Mosquitto (Offline Mode):</b> Connects over port <b>1883</b> without encryption for isolated industrial networks or offline simulation.<br/><br/>"
        "<b>Reliability and Fault Tolerance Mechanisms:</b><br/>"
        "1. <b>Quality of Service (QoS 1):</b> Telemetry is published with QoS 1, guaranteeing handshake confirmation (PUBACK) so packets are not lost during network jitter.<br/>"
        "2. <b>Exponential Backoff Reconnection:</b> If connection drops, the client automatically backs off (1s, 2s, 4s up to 30s) to avoid network flooding.<br/>"
        "3. <b>Simulation Fallback:</b> If cloud credentials in <code>.env</code> are missing or unreachable, the dashboard automatically transitions to offline local mode without crashing."
    )
    story.append(Paragraph(p_l2, styles['ReportBody']))

    # Embed Figure 2
    fig2_path = os.path.join(FIGURES_DIR, "fig2_mqtt_pubsub.png")
    if os.path.exists(fig2_path):
        story.append(Spacer(1, 4))
        story.append(Image(fig2_path, width=475, height=230))
        story.append(Paragraph("Figure 2: MQTT Publish-Subscribe Communication Architecture", styles['FigureCaption']))

    story.append(PageBreak())

    # Layer 3
    story.append(Paragraph("6.3 Layer 3: Relational Persistence Layer (SQLite WAL Mode)", styles['SectionTitle']))
    p_l3 = (
        "<b>Database Architectural Design:</b> Ephemeral monitoring solutions suffer from data loss upon power resets. "
        "Layer 3 implements robust persistent storage via SQLite (<code>src/database.py</code>, <code>data/battery.db</code>). "
        "SQLite was chosen because it requires zero server setup, operates as a single portable file, and provides strict ACID compliance.<br/><br/>"
        "<b>High-Concurrency Write-Ahead Logging (WAL):</b><br/>"
        "Standard SQLite locking blocks database reads while a write transaction is executing. In a high-frequency IoT system sampling every 2 seconds, "
        "this causes 'database is locked' operational errors when an operator loads historical charts. "
        "This project resolves this by enabling <b>WAL mode</b> upon connection initialization:<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<code>PRAGMA journal_mode = WAL;</code><br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<code>PRAGMA synchronous = NORMAL;</code><br/>"
        "WAL mode permits simultaneous, non-blocking reads while the telemetry subscriber thread commits new records into the WAL file.<br/><br/>"
        "<b>Security and Indexing Optimizations:</b><br/>"
        "• <b>Parameterized Queries:</b> All SQL operations use parameter substitution (<code>?</code> placeholders), eliminating SQL injection risks.<br/>"
        "• <b>B-Tree Indexes:</b> Created on <code>(pack_id, timestamp_epoch DESC)</code> and <code>rule_status</code>, allowing millisecond retrieval of the latest 50–500 cycles across millions of records.<br/>"
        "• <b>CSV Data Export & Automated Backup:</b> The database module provides automated CSV dump facilities and timestamped database snapshots (<code>data/backups/</code>)."
    )
    story.append(Paragraph(p_l3, styles['ReportBody']))

    story.append(PageBreak())

    # Layer 4
    story.append(Paragraph("6.4 Layer 4: Node-RED Automation & Supervisory Event Flow", styles['SectionTitle']))
    p_l4 = (
        "<b>Purpose and Supervisory Integration:</b> Node-RED (<code>node_red/battery_monitoring_flow.json</code>) is incorporated into the architecture "
        "to demonstrate visual, low-code event-driven orchestration and external industrial integration (e.g. SCADA systems, PLCs, secondary dashboards).<br/><br/>"
        "<b>Architectural Safeguard — Single Source of Truth:</b><br/>"
        "A critical engineering design decision implemented in this project is that <b>Python remains the sole authoritative engine for SQLite storage, "
        "data validation, and ML model inference</b>. Allowing Node-RED and Python to independently write to SQLite would introduce duplicate records, "
        "write-lock contention, and conflicting alarm timestamps. Node-RED therefore operates as a <b>parallel supervisory consumer</b>.<br/><br/>"
        "<b>Flow Architecture & Logic Streams:</b><br/>"
        "1. <b>MQTT In Node:</b> Listens to topic <code>battery/cells/data</code> on the shared broker.<br/>"
        "2. <b>JSON Parser Node:</b> Deserializes the UTF-8 payload into a JavaScript object.<br/>"
        "3. <b>Imbalance & Severity Classifier Function:</b> Computes maximum voltage, minimum voltage, voltage spread (ΔV), and temperature. Evaluates strict threshold hierarchy:<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;• <b>Output 1 [NORMAL]:</b> ΔV < 20 mV and T_max < 45°C → Routed to monitoring log.<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;• <b>Output 2 [WARNING]:</b> 20 mV ≤ ΔV < 50 mV or 45°C ≤ T_max < 60°C → Emits warning payload.<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;• <b>Output 3 [CRITICAL]:</b> ΔV ≥ 50 mV or T_max ≥ 60°C → Emits critical alarm.<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;• <b>Output 4 [SENSOR FAULT]:</b> Missing values, empty lists, or NaN readings → Emits hardware fault alarm.<br/>"
        "4. <b>Format Alert & MQTT Out Node:</b> Re-publishes formatted alarm events to secondary topic <code>battery/alerts/events</code>."
    )
    story.append(Paragraph(p_l4, styles['ReportBody']))

    story.append(PageBreak())

    # Layer 5
    story.append(Paragraph("6.5 Layer 5: Machine Learning Anomaly Detection, Authentication & Alerts", styles['SectionTitle']))
    p_l5 = (
        "<b>5.1 The Need for Unsupervised Machine Learning:</b> Deterministic rule-based threshold checks (e.g. ΔV ≥ 20 mV) are effective "
        "for known static limits, but fail to detect subtle, non-linear multi-variable interactions. For example, a 18 mV spread at low 1A current "
        "and 25°C may be nominal, but the exact same 18 mV spread accompanied by a 8°C thermal gradient and a heavy 15A load current indicates "
        "severe localized internal impedance degradation. Layer 5 resolves this via an <b>Isolation Forest</b> anomaly detection pipeline (<code>src/ml_pipeline.py</code>).<br/><br/>"
        "<b>5.2 Feature Vector Engineering:</b> Seven electro-thermal features are extracted from each reading:<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<b>x = [ ΔV_mV, V_max, V_min, V_mean, T_max, ΔT, I_pack ]</b><br/>"
        "Features are standardized using <code>StandardScaler</code> fitted during training.<br/><br/>"
        "<b>5.3 Model Training, Artifacts & Graceful Fallback:</b><br/>"
        "The model is trained on 6,000 synthetic operational cycles (80% train, 20% held-out test split) with a contamination factor of 0.05. "
        "Trained model artifacts are persisted to <code>models/isolation_forest_model.joblib</code> and <code>models/scaler.joblib</code>. "
        "If the model file is absent or corrupted, the system gracefully falls back to deterministic rule-based alarms without crashing.<br/><br/>"
        "<b>5.4 Authentication & Session Security:</b><br/>"
        "Access to the dashboard is secured by a login page (<code>src/auth.py</code>). Passwords are cryptographically hashed using salted Bcrypt "
        "(12 rounds) with PBKDF2-HMAC-SHA256 fallback. Default administrator credentials are configured securely in <code>.env</code>.<br/><br/>"
        "<b>5.5 Alert Management & Cooldown Mechanism:</b><br/>"
        "To prevent alert flooding (where an ongoing 55 mV imbalance would otherwise create 1,800 database alert rows and emails per hour), "
        "the <code>AlertManager</code> (<code>src/alerts.py</code>) implements a <b>60-second cooldown timer</b> for identical states, while "
        "<b>immediately bypassing cooldown upon state escalations</b> (e.g. WARNING → CRITICAL)."
    )
    story.append(Paragraph(p_l5, styles['ReportBody']))

    # Embed Figure 3
    fig3_path = os.path.join(FIGURES_DIR, "fig3_ml_confusion_matrix.png")
    if os.path.exists(fig3_path):
        story.append(Spacer(1, 4))
        story.append(Image(fig3_path, width=475, height=210))
        story.append(Paragraph("Figure 3: Isolation Forest Anomaly Detection Confusion Matrix & Quantitative Metrics", styles['FigureCaption']))

    story.append(PageBreak())

    # Layer 6
    story.append(Paragraph("6.6 Layer 6: ESP32 Edge Sensor Interface & Hardware Alerts", styles['SectionTitle']))
    p_l6 = (
        "<b>Edge Hardware Role:</b> For physical battery implementations, an ESP32 microcontroller (<code>firmware/esp32_battery_monitor/esp32_battery_monitor.ino</code>) "
        "serves as the edge acquisition and local alarm node.<br/><br/>"
        "<b>Voltage Divider Interface for 4S Series Pack:</b><br/>"
        "The ESP32 integrated Analog-to-Digital Converter (ADC) supports a maximum input potential of <b>3.30V</b>. "
        "Connecting a 4S lithium battery pack (max terminal voltage 16.80V) directly to an ESP32 pin would cause instant permanent destruction. "
        "Therefore, precision 1% metal-film resistor divider networks attenuate intermediate cell tap voltages into the linear 1.5V–2.8V ADC range.<br/><br/>"
        "<b>Individual Cell Potential Differential Reconstruction:</b><br/>"
        "Because the ESP32 shares a common ground with the pack negative terminal, taps measure cumulative voltages. "
        "Individual cell voltages are computed differentially in software:<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;• <b>V_Cell1 = V_Tap1</b><br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;• <b>V_Cell2 = V_Tap2 - V_Tap1</b><br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;• <b>V_Cell3 = V_Tap3 - V_Tap2</b><br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;• <b>V_Cell4 = V_Tap4 - V_Tap3</b><br/><br/>"
        "<b>Why DHT11 Sensors are Strictly Unsuitable:</b><br/>"
        "The DHT11 is an ambient humidity/air temperature sensor housed in a bulky plastic casing with slow response times (>10s). "
        "Battery safety requires <b>direct casing surface-contact thermistors</b> (10k NTC B=3950 or DS18B20) attached with thermal pads to rapidly detect localized thermal runaway."
    )
    story.append(Paragraph(p_l6, styles['ReportBody']))

    story.append(Spacer(1, 4))
    story.append(Paragraph("Table 3: ESP32 4S Voltage Divider Resistor Network Specifications", styles['TableCaption']))
    div_table_data = [
        [Paragraph("<b>Battery Tap</b>", styles['TableCellHeader']),
         Paragraph("<b>Max Tap Potential</b>", styles['TableCellHeader']),
         Paragraph("<b>Resistor Selection (1% Metal Film)</b>", styles['TableCellHeader']),
         Paragraph("<b>Scaling Ratio</b>", styles['TableCellHeader']),
         Paragraph("<b>Max Pin Voltage</b>", styles['TableCellHeader']),
         Paragraph("<b>ESP32 ADC Pin</b>", styles['TableCellHeader'])],
        [Paragraph("Tap 1 (Cell 1)", styles['TableCellBold']), Paragraph("4.20 V", styles['TableCell']), Paragraph("R1 = 10 kΩ, R2 = 20 kΩ", styles['TableCell']), Paragraph("1.500", styles['TableCell']), Paragraph("2.80 V", styles['TableCell']), Paragraph("GPIO 36 (VP)", styles['TableCellBold'])],
        [Paragraph("Tap 2 (Cell 1+2)", styles['TableCellBold']), Paragraph("8.40 V", styles['TableCell']), Paragraph("R1 = 30 kΩ, R2 = 10 kΩ", styles['TableCell']), Paragraph("4.000", styles['TableCell']), Paragraph("2.10 V", styles['TableCell']), Paragraph("GPIO 39 (VN)", styles['TableCellBold'])],
        [Paragraph("Tap 3 (Cell 1+2+3)", styles['TableCellBold']), Paragraph("12.60 V", styles['TableCell']), Paragraph("R1 = 50 kΩ, R2 = 10 kΩ", styles['TableCell']), Paragraph("6.000", styles['TableCell']), Paragraph("2.10 V", styles['TableCell']), Paragraph("GPIO 34", styles['TableCellBold'])],
        [Paragraph("Tap 4 (Pack Total)", styles['TableCellBold']), Paragraph("16.80 V", styles['TableCell']), Paragraph("R1 = 70 kΩ, R2 = 10 kΩ", styles['TableCell']), Paragraph("8.000", styles['TableCell']), Paragraph("2.10 V", styles['TableCell']), Paragraph("GPIO 35", styles['TableCellBold'])],
    ]
    t_div = Table(div_table_data, colWidths=[85, 75, 140, 55, 60, 60])
    t_div.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E3A8A")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor("#FFFFFF"), colors.HexColor("#F8FAFC")]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('ALIGN', (1,1), (-1,-1), 'CENTER'),
    ]))
    story.append(t_div)

    # Embed Figure 5
    fig5_path = os.path.join(FIGURES_DIR, "fig5_hardware_circuit.png")
    if os.path.exists(fig5_path):
        story.append(Spacer(1, 6))
        story.append(Image(fig5_path, width=475, height=240))
        story.append(Paragraph("Figure 5: ESP32 4S Battery Sensing & Hardware Alert Interface Schematic", styles['FigureCaption']))

    story.append(Spacer(1, 4))
    story.append(Paragraph("Table 4: Bill of Materials (BOM) and Estimated Prototype Cost", styles['TableCaption']))
    bom_data = [
        [Paragraph("<b>Item #</b>", styles['TableCellHeader']),
         Paragraph("<b>Component Description</b>", styles['TableCellHeader']),
         Paragraph("<b>Specification / Part Number</b>", styles['TableCellHeader']),
         Paragraph("<b>Qty</b>", styles['TableCellHeader']),
         Paragraph("<b>Cost (INR)</b>", styles['TableCellHeader']),
         Paragraph("<b>Cost (USD)</b>", styles['TableCellHeader'])],
        [Paragraph("1", styles['TableCell']), Paragraph("Microcontroller Board", styles['TableCellBold']), Paragraph("ESP32 NodeMCU-32S (Wi-Fi + BLE)", styles['TableCell']), Paragraph("1", styles['TableCell']), Paragraph("₹450", styles['TableCell']), Paragraph("$5.50", styles['TableCell'])],
        [Paragraph("2", styles['TableCell']), Paragraph("Precision Resistors", styles['TableCellBold']), Paragraph("1% Metal Film (10k, 20k, 30k, 50k, 70k)", styles['TableCell']), Paragraph("8", styles['TableCell']), Paragraph("₹40", styles['TableCell']), Paragraph("$0.50", styles['TableCell'])],
        [Paragraph("3", styles['TableCell']), Paragraph("Temperature Sensors", styles['TableCellBold']), Paragraph("10k NTC Thermistors (B=3950) Bead Type", styles['TableCell']), Paragraph("4", styles['TableCell']), Paragraph("₹200", styles['TableCell']), Paragraph("$2.40", styles['TableCell'])],
        [Paragraph("4", styles['TableCell']), Paragraph("Current Sensor Module", styles['TableCellBold']), Paragraph("ACS712-20A Hall Effect Module", styles['TableCell']), Paragraph("1", styles['TableCell']), Paragraph("₹180", styles['TableCell']), Paragraph("$2.20", styles['TableCell'])],
        [Paragraph("5", styles['TableCell']), Paragraph("Status Indicator LEDs", styles['TableCellBold']), Paragraph("5mm Diffused LEDs (Green, Yellow, Red)", styles['TableCell']), Paragraph("3", styles['TableCell']), Paragraph("₹15", styles['TableCell']), Paragraph("$0.20", styles['TableCell'])],
        [Paragraph("6", styles['TableCell']), Paragraph("Acoustic Buzzer", styles['TableCellBold']), Paragraph("5V Active Piezo Buzzer Module", styles['TableCell']), Paragraph("1", styles['TableCell']), Paragraph("₹35", styles['TableCell']), Paragraph("$0.45", styles['TableCell'])],
        [Paragraph("7", styles['TableCell']), Paragraph("Breadboard & Jumper Wires", styles['TableCellBold']), Paragraph("830-point Solderless Breadboard + 40x Wires", styles['TableCell']), Paragraph("1", styles['TableCell']), Paragraph("₹160", styles['TableCell']), Paragraph("$2.00", styles['TableCell'])],
        [Paragraph("8", styles['TableCell']), Paragraph("5V USB Power Supply", styles['TableCellBold']), Paragraph("5V 2A Regulated Adapter & Micro-USB Cable", styles['TableCell']), Paragraph("1", styles['TableCell']), Paragraph("₹150", styles['TableCell']), Paragraph("$1.80", styles['TableCell'])],
        [Paragraph("<b>TOTAL</b>", styles['TableCellBold']), Paragraph("<b>Estimated Prototype Hardware Cost</b>", styles['TableCellBold']), Paragraph("<b>Complete Sensor Gateway Assembly</b>", styles['TableCellBold']), Paragraph("—", styles['TableCellBold']), Paragraph("<b>~₹1,230</b>", styles['TableCellBold']), Paragraph("<b>~$15.05</b>", styles['TableCellBold'])],
    ]
    t_bom = Table(bom_data, colWidths=[40, 130, 175, 30, 50, 50])
    t_bom.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E3A8A")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-2), [colors.HexColor("#FFFFFF"), colors.HexColor("#F8FAFC")]),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('ALIGN', (0,0), (0,-1), 'CENTER'),
        ('ALIGN', (3,1), (-1,-1), 'CENTER'),
    ]))
    story.append(t_bom)

    story.append(PageBreak())

    # =========================================================================
    # CHAPTER 7 & 8: METHODOLOGY & CALCULATIONS
    # =========================================================================
    story.append(Paragraph("7. METHODOLOGY AND OPERATIONAL WORKFLOW", styles['ChapterTitle']))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1E3A8A"), spaceBefore=2, spaceAfter=14))

    p_meth = (
        "The end-to-end operational workflow follows a strict sequential pipeline guaranteeing data integrity, "
        "truthful state classification, and zero crashes during sensor failure events:<br/><br/>"
        "<b>Step 1: Telemetry Acquisition:</b> Edge sensors (ESP32) or synthetic physics simulator sample cell potentials and temperatures.<br/>"
        "<b>Step 2: JSON Packaging:</b> Data is serialized into standardized JSON containing <code>pack_id</code>, <code>cell_voltages</code>, and UTC timestamps.<br/>"
        "<b>Step 3: MQTT Publishing:</b> Packets are published to <code>battery/cells/data</code> with QoS 1.<br/>"
        "<b>Step 4: Broker Ingestion:</b> HiveMQ Cloud (TLS 8883) or local Mosquitto forwards packets to active subscribers.<br/>"
        "<b>Step 5: Telemetry Sanitization:</b> <code>data_validator.py</code> checks field presence, data types, and traps non-finite numbers (NaN/Inf).<br/>"
        "<b>Step 6: Mathematical Computation:</b> <code>calculations.py</code> determines V_max, V_min, ΔV, ΔV_mV, V_mean, and thermal gradients.<br/>"
        "<b>Step 7: Physical Bounds Check:</b> <code>assess_sensor_quality()</code> validates readings against physical limits (0.5V–5.0V, -40°C–120°C).<br/>"
        "<b>Step 8: Rule-Based Evaluation:</b> <code>detection.py</code> checks CRITICAL conditions before WARNING conditions; missing data raises <code>SENSOR_FAULT</code>.<br/>"
        "<b>Step 9: AI/ML Inference:</b> <code>ml_pipeline.py</code> passes normalized features into Isolation Forest to compute continuous anomaly scores.<br/>"
        "<b>Step 10: Relational Persistence:</b> <code>database.py</code> inserts the evaluated record into SQLite WAL tables via parameterized queries.<br/>"
        "<b>Step 11: Alert State Machine:</b> <code>alerts.py</code> checks the 60-second cooldown timer or immediate escalation to trigger UI alarms.<br/>"
        "<b>Step 12: Operator Presentation:</b> Streamlit dashboard refreshes metrics, Plotly trend charts, and cell sanity deviation matrices."
    )
    story.append(Paragraph(p_meth, styles['ReportBody']))

    story.append(Spacer(1, 10))
    story.append(Paragraph("8. BATTERY CELL IMBALANCE CALCULATIONS & MATHEMATICAL FORMULATIONS", styles['ChapterTitle']))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1E3A8A"), spaceBefore=2, spaceAfter=14))

    p_calc = (
        "<b>Mathematical Formulations:</b><br/>"
        "For any battery pack consisting of <i>N</i> series-connected electrochemical cells:<br/>"
        "1. <b>Maximum Cell Voltage:</b> V_max = max(V_1, V_2, ..., V_N)<br/>"
        "2. <b>Minimum Cell Voltage:</b> V_min = min(V_1, V_2, ..., V_N)<br/>"
        "3. <b>Voltage Spread (ΔV):</b> ΔV = V_max - V_min (in Volts)<br/>"
        "4. <b>Voltage Spread in Millivolts:</b> ΔV_mV = ΔV · 1000 (in mV)<br/>"
        "5. <b>Pack Arithmetic Mean Voltage:</b> V_mean = (1/N) · Σ V_i<br/>"
        "6. <b>Individual Cell Deviation:</b> Dev_i = (V_i - V_mean) · 1000 (in mV)<br/>"
        "7. <b>Thermal Gradient:</b> ΔT = max(T_i) - min(T_i) (in °C)<br/><br/>"
        "<b>Configurable Threshold Hierarchy:</b><br/>"
        "• <b>CRITICAL (Checked First):</b> ΔV ≥ 0.050 V (50 mV), V_cell ≥ 4.25 V, V_cell ≤ 3.00 V, T_max ≥ 60.0°C, or ΔT ≥ 10.0°C.<br/>"
        "• <b>WARNING (Checked Second):</b> ΔV ≥ 0.020 V (20 mV), V_cell ≥ 4.22 V, V_cell ≤ 3.20 V, T_max ≥ 45.0°C, or ΔT ≥ 5.0°C.<br/>"
        "• <b>NORMAL:</b> All cell voltages and temperatures remain strictly within safe bounds.<br/>"
        "• <b>SENSOR FAULT:</b> Triggered when readings are null, missing, or outside physical limits. <b>Missing data is never classified as healthy.</b><br/><br/>"
        "<i>Engineering Disclaimer:</i> The thresholds (20 mV warning, 50 mV critical) are demonstration settings configured in <code>config/thresholds.yaml</code>. "
        "Actual industrial limits depend heavily on cell chemistry (LFP, NMC, LCO), C-rates, ambient temperature, and manufacturer specifications."
    )
    story.append(Paragraph(p_calc, styles['ReportBody']))

    # Embed Figure 4
    fig4_path = os.path.join(FIGURES_DIR, "fig4_voltage_spread_demo.png")
    if os.path.exists(fig4_path):
        story.append(Spacer(1, 4))
        story.append(Image(fig4_path, width=475, height=210))
        story.append(Paragraph("Figure 4: Demonstration of Cell Voltage Divergence Across Operational Scenarios", styles['FigureCaption']))

    story.append(PageBreak())

    # =========================================================================
    # CHAPTER 9 & 10: REQUIREMENTS & FOLDER STRUCTURE
    # =========================================================================
    story.append(Paragraph("9. SOFTWARE AND HARDWARE SPECIFICATIONS", styles['ChapterTitle']))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1E3A8A"), spaceBefore=2, spaceAfter=14))

    story.append(Paragraph("Table 5: Software Specifications and Framework Dependencies", styles['TableCaption']))
    sw_data = [
        [Paragraph("<b>Software Component</b>", styles['TableCellHeader']),
         Paragraph("<b>Version</b>", styles['TableCellHeader']),
         Paragraph("<b>Primary Architectural Role</b>", styles['TableCellHeader'])],
        [Paragraph("Python Runtime", styles['TableCellBold']), Paragraph("3.14.7 / 3.10+", styles['TableCell']), Paragraph("Core analytical backend, calculation engine, pipeline execution", styles['TableCell'])],
        [Paragraph("Streamlit", styles['TableCellBold']), Paragraph("1.66.1", styles['TableCell']), Paragraph("Reactive web dashboard, session controller, operator UI", styles['TableCell'])],
        [Paragraph("Paho-MQTT", styles['TableCellBold']), Paragraph("2.1.0", styles['TableCell']), Paragraph("TLS-secured publish/subscribe IoT messaging client", styles['TableCell'])],
        [Paragraph("SQLite Engine", styles['TableCellBold']), Paragraph("3.x (Built-in)", styles['TableCell']), Paragraph("WAL-mode persistent relational storage for telemetry & alerts", styles['TableCell'])],
        [Paragraph("Scikit-Learn", styles['TableCellBold']), Paragraph("1.9.1", styles['TableCell']), Paragraph("Isolation Forest unsupervised anomaly detection & feature scaling", styles['TableCell'])],
        [Paragraph("Pandas & NumPy", styles['TableCellBold']), Paragraph("3.1.0 / 2.5.4", styles['TableCell']), Paragraph("Numerical array manipulation, tabular structuring, CSV parsing", styles['TableCell'])],
        [Paragraph("Plotly", styles['TableCellBold']), Paragraph("7.1.0", styles['TableCell']), Paragraph("Interactive time-series charting & cell voltage bar graphs", styles['TableCell'])],
        [Paragraph("Bcrypt", styles['TableCellBold']), Paragraph("5.0.0", styles['TableCell']), Paragraph("Salted cryptographic password hashing for user authentication", styles['TableCell'])],
        [Paragraph("Pytest", styles['TableCellBold']), Paragraph("9.2.0", styles['TableCell']), Paragraph("Automated unit and integration test execution suite", styles['TableCell'])],
        [Paragraph("ReportLab", styles['TableCellBold']), Paragraph("5.1.0", styles['TableCell']), Paragraph("Programmatic publication-quality PDF report generation", styles['TableCell'])],
        [Paragraph("Arduino IDE / Framework", styles['TableCellBold']), Paragraph("2.x / ESP32 Core", styles['TableCell']), Paragraph("C++ firmware compilation and USB flashing for ESP32", styles['TableCell'])],
    ]
    t_sw = Table(sw_data, colWidths=[120, 85, 270])
    t_sw.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E3A8A")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor("#FFFFFF"), colors.HexColor("#F8FAFC")]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_sw)

    story.append(Spacer(1, 12))
    story.append(Paragraph("Table 6: Hardware Prototype Component Specifications", styles['TableCaption']))
    hw_data = [
        [Paragraph("<b>Hardware Component</b>", styles['TableCellHeader']),
         Paragraph("<b>Model / Specification</b>", styles['TableCellHeader']),
         Paragraph("<b>Qty</b>", styles['TableCellHeader']),
         Paragraph("<b>Functional Purpose in Prototype</b>", styles['TableCellHeader'])],
        [Paragraph("Microcontroller", styles['TableCellBold']), Paragraph("ESP32 NodeMCU-32S (240MHz)", styles['TableCell']), Paragraph("1", styles['TableCell']), Paragraph("Edge ADC sampling, Wi-Fi TLS MQTT client, alert output", styles['TableCell'])],
        [Paragraph("Resistor Dividers", styles['TableCellBold']), Paragraph("1% Metal Film (10k, 20k, 30k, 50k, 70k)", styles['TableCell']), Paragraph("8", styles['TableCell']), Paragraph("Attenuate 4S taps (up to 16.8V) safely below 3.3V ADC limit", styles['TableCell'])],
        [Paragraph("Temperature Sensors", styles['TableCellBold']), Paragraph("10k NTC Thermistors (B=3950)", styles['TableCell']), Paragraph("4", styles['TableCell']), Paragraph("Direct casing surface contact temperature measurement", styles['TableCell'])],
        [Paragraph("Current Sensor", styles['TableCellBold']), Paragraph("ACS712-20A Hall-Effect Module", styles['TableCell']), Paragraph("1", styles['TableCell']), Paragraph("Measures pack discharge current (optional load input)", styles['TableCell'])],
        [Paragraph("Visual Alarm LEDs", styles['TableCellBold']), Paragraph("5mm LEDs (Green, Yellow, Red)", styles['TableCell']), Paragraph("3", styles['TableCell']), Paragraph("Physical visual indicators for Normal, Warning, Critical", styles['TableCell'])],
        [Paragraph("Acoustic Buzzer", styles['TableCellBold']), Paragraph("5V Active Piezo Buzzer", styles['TableCell']), Paragraph("1", styles['TableCell']), Paragraph("Audible buzzer alarm triggered during critical divergence", styles['TableCell'])],
        [Paragraph("Power Supply", styles['TableCellBold']), Paragraph("5V 2A Regulated Adapter", styles['TableCell']), Paragraph("1", styles['TableCell']), Paragraph("Main power input via ESP32 micro-USB port", styles['TableCell'])],
    ]
    t_hw = Table(hw_data, colWidths=[110, 150, 30, 185])
    t_hw.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E3A8A")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor("#FFFFFF"), colors.HexColor("#F8FAFC")]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('ALIGN', (2,1), (2,-1), 'CENTER'),
    ]))
    story.append(t_hw)

    story.append(Spacer(1, 14))
    story.append(Paragraph("10. PROJECT FOLDER STRUCTURE & MODULE ARCHITECTURE", styles['ChapterTitle']))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1E3A8A"), spaceBefore=2, spaceAfter=14))

    folder_tree_text = (
        "<b>Root Directory:</b> <code>C:\\Users\\jatin\\OneDrive\\Documents\\Desktop\\HCL Battery cell imbalence detection\\</code><br/><br/>"
        "• <b><code>app.py</code>:</b> Streamlit dashboard application containing session authentication, live telemetry tiles, Plotly charts, scenario controls, and alert acknowledgement.<br/>"
        "• <b><code>run_project.bat</code>:</b> One-click Windows startup batch script that checks virtual environment, creates default configurations, initializes database tables, and boots Streamlit.<br/>"
        "• <b><code>config/</code>:</b> Contains <code>settings.yaml</code> (MQTT/broker defaults) and <code>thresholds.yaml</code> (voltage spread and temperature safety boundaries).<br/>"
        "• <b><code>src/</code>:</b> Core Python package containing modular micro-services:<br/>"
        "&nbsp;&nbsp;• <code>calculations.py</code>: Implements core mathematical formulas (V_max, V_min, ΔV, ΔV_mV, rate-of-change, sanity checks).<br/>"
        "&nbsp;&nbsp;• <code>data_validator.py</code>: Validates inbound JSON telemetry, sanitizes timestamps, and filters corrupt payloads.<br/>"
        "&nbsp;&nbsp;• <code>detection.py</code>: Evaluates hierarchical status (CRITICAL > WARNING > NORMAL) and flags SENSOR_FAULT.<br/>"
        "&nbsp;&nbsp;• <code>simulator.py</code>: Background thread producing synthetic 4S telemetry with 5 failure scenarios.<br/>"
        "&nbsp;&nbsp;• <code>database.py</code>: SQLite WAL persistence layer with parameterized queries and index definitions.<br/>"
        "&nbsp;&nbsp;• <code>alerts.py</code>: State transition and cooldown manager with optional SMTP email dispatching.<br/>"
        "&nbsp;&nbsp;• <code>auth.py</code>: Secure user registration and password authentication using Bcrypt.<br/>"
        "&nbsp;&nbsp;• <code>ml_pipeline.py</code>: Scikit-learn Isolation Forest model training, serialization, and inference pipeline.<br/>"
        "&nbsp;&nbsp;• <code>mqtt_client.py</code>, <code>mqtt_publisher.py</code>, <code>mqtt_subscriber.py</code>: Paho-MQTT TLS client wrappers.<br/>"
        "&nbsp;&nbsp;• <code>dashboard_helpers.py</code>: UI styling CSS, status badges, and Plotly interactive chart builders.<br/>"
        "• <b><code>data/battery.db</code>:</b> SQLite database file storing persistent telemetry, alerts, and users.<br/>"
        "• <b><code>datasets/</code>:</b> Contains reproducible 6,000-sample training dataset <code>battery_telemetry_dataset.csv</code>.<br/>"
        "• <b><code>models/</code>:</b> Stores serialized Isolation Forest model and standard scaler (<code>.joblib</code>).<br/>"
        "• <b><code>firmware/esp32_battery_monitor/</code>:</b> Arduino C++ source code (<code>esp32_battery_monitor.ino</code>) and wiring guide.<br/>"
        "• <b><code>node_red/</code>:</b> Pre-configured supervisory flow (<code>battery_monitoring_flow.json</code>) and documentation.<br/>"
        "• <b><code>tests/</code>:</b> Complete automated Pytest test suite covering all 6 layers (28 test cases).<br/>"
        "• <b><code>reports/</code>:</b> Project report PDF and generated publication-quality figures."
    )
    story.append(Paragraph(folder_tree_text, styles['ReportBody']))

    story.append(PageBreak())

    # =========================================================================
    # CHAPTER 11 & 12: DATABASE & DASHBOARD DESIGN
    # =========================================================================
    story.append(Paragraph("11. DATABASE DESIGN & ENTITY RELATIONSHIPS", styles['ChapterTitle']))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1E3A8A"), spaceBefore=2, spaceAfter=14))

    p_db_desc = (
        "The relational schema inside <code>data/battery.db</code> is composed of three primary tables designed for "
        "high-throughput logging, event lifecycle auditing, and user access control."
    )
    story.append(Paragraph(p_db_desc, styles['ReportBody']))

    story.append(Paragraph("Table 7: SQLite Database Schema — Table: battery_readings", styles['TableCaption']))
    db_schema_data = [
        [Paragraph("<b>Column Name</b>", styles['TableCellHeader']),
         Paragraph("<b>Data Type</b>", styles['TableCellHeader']),
         Paragraph("<b>Constraints / Indexes</b>", styles['TableCellHeader']),
         Paragraph("<b>Description / Mathematical Mapping</b>", styles['TableCellHeader'])],
        [Paragraph("<code>id</code>", styles['TableCellBold']), Paragraph("INTEGER", styles['TableCell']), Paragraph("PRIMARY KEY AUTOINCREMENT", styles['TableCell']), Paragraph("Unique sequential reading sequence ID", styles['TableCell'])],
        [Paragraph("<code>pack_id</code>", styles['TableCellBold']), Paragraph("TEXT", styles['TableCell']), Paragraph("NOT NULL, INDEXED", styles['TableCell']), Paragraph("Battery pack identifier (e.g. 'PACK-01')", styles['TableCell'])],
        [Paragraph("<code>timestamp_utc</code>", styles['TableCellBold']), Paragraph("TEXT", styles['TableCell']), Paragraph("NOT NULL", styles['TableCell']), Paragraph("ISO 8601 UTC timestamp string", styles['TableCell'])],
        [Paragraph("<code>timestamp_epoch</code>", styles['TableCellBold']), Paragraph("REAL", styles['TableCell']), Paragraph("NOT NULL, INDEXED", styles['TableCell']), Paragraph("Unix epoch seconds for chronological range queries", styles['TableCell'])],
        [Paragraph("<code>mode</code>", styles['TableCellBold']), Paragraph("TEXT", styles['TableCell']), Paragraph("NOT NULL", styles['TableCell']), Paragraph("Operating mode: 'simulation' or 'hardware'", styles['TableCell'])],
        [Paragraph("<code>cell_count</code>", styles['TableCellBold']), Paragraph("INTEGER", styles['TableCell']), Paragraph("NOT NULL", styles['TableCell']), Paragraph("Total series cells monitored (4 for 4S)", styles['TableCell'])],
        [Paragraph("<code>cell_voltages_json</code>", styles['TableCellBold']), Paragraph("TEXT", styles['TableCell']), Paragraph("NOT NULL", styles['TableCell']), Paragraph("JSON array of individual cell voltages [V1..V4]", styles['TableCell'])],
        [Paragraph("<code>cell_temperatures_json</code>", styles['TableCellBold']), Paragraph("TEXT", styles['TableCell']), Paragraph("NOT NULL", styles['TableCell']), Paragraph("JSON array of cell surface temperatures [T1..T4]", styles['TableCell'])],
        [Paragraph("<code>current_a</code>", styles['TableCellBold']), Paragraph("REAL", styles['TableCell']), Paragraph("DEFAULT 0.0", styles['TableCell']), Paragraph("Battery pack discharge/charge current in Amperes", styles['TableCell'])],
        [Paragraph("<code>v_max</code>", styles['TableCellBold']), Paragraph("REAL", styles['TableCell']), Paragraph("—", styles['TableCell']), Paragraph("Maximum measured cell potential (V)", styles['TableCell'])],
        [Paragraph("<code>v_min</code>", styles['TableCellBold']), Paragraph("REAL", styles['TableCell']), Paragraph("—", styles['TableCell']), Paragraph("Minimum measured cell potential (V)", styles['TableCell'])],
        [Paragraph("<code>delta_v</code>", styles['TableCellBold']), Paragraph("REAL", styles['TableCell']), Paragraph("—", styles['TableCell']), Paragraph("Voltage spread in Volts (V_max - V_min)", styles['TableCell'])],
        [Paragraph("<code>delta_v_mv</code>", styles['TableCellBold']), Paragraph("REAL", styles['TableCell']), Paragraph("—", styles['TableCell']), Paragraph("Voltage spread in millivolts (ΔV · 1000)", styles['TableCell'])],
        [Paragraph("<code>mean_v</code>", styles['TableCellBold']), Paragraph("REAL", styles['TableCell']), Paragraph("—", styles['TableCell']), Paragraph("Pack arithmetic average cell voltage (V)", styles['TableCell'])],
        [Paragraph("<code>t_max</code>", styles['TableCellBold']), Paragraph("REAL", styles['TableCell']), Paragraph("—", styles['TableCell']), Paragraph("Peak measured cell surface temperature (°C)", styles['TableCell'])],
        [Paragraph("<code>delta_t</code>", styles['TableCellBold']), Paragraph("REAL", styles['TableCell']), Paragraph("—", styles['TableCell']), Paragraph("Cell-to-cell thermal gradient spread (T_max - T_min)", styles['TableCell'])],
        [Paragraph("<code>rule_status</code>", styles['TableCellBold']), Paragraph("TEXT", styles['TableCell']), Paragraph("NOT NULL, INDEXED", styles['TableCell']), Paragraph("Operational state: NORMAL, WARNING, CRITICAL, SENSOR_FAULT", styles['TableCell'])],
        [Paragraph("<code>ml_prediction</code>", styles['TableCellBold']), Paragraph("INTEGER", styles['TableCell']), Paragraph("DEFAULT 1", styles['TableCell']), Paragraph("Isolation Forest output: 1 = Normal (Inlier), -1 = Anomaly", styles['TableCell'])],
        [Paragraph("<code>ml_anomaly_score</code>", styles['TableCellBold']), Paragraph("REAL", styles['TableCell']), Paragraph("DEFAULT 0.0", styles['TableCell']), Paragraph("Continuous anomaly score; higher = abnormal", styles['TableCell'])],
        [Paragraph("<code>data_quality</code>", styles['TableCellBold']), Paragraph("TEXT", styles['TableCell']), Paragraph("DEFAULT 'HEALTHY'", styles['TableCell']), Paragraph("Sensor sanity assessment: HEALTHY or SENSOR_ISSUE", styles['TableCell'])],
    ]
    t_db = Table(db_schema_data, colWidths=[105, 55, 120, 195])
    t_db.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E3A8A")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor("#FFFFFF"), colors.HexColor("#F8FAFC")]),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
    ]))
    story.append(t_db)

    story.append(Spacer(1, 10))
    p_other_tables = (
        "<b>Additional Tables:</b><br/>"
        "• <b><code>alerts</code>:</b> Audits alarm events with fields: <code>id</code>, <code>pack_id</code>, <code>timestamp_utc</code>, "
        "<code>alert_level</code> (WARNING / CRITICAL), <code>affected_cells_json</code>, <code>delta_v_mv</code>, <code>max_temp</code>, "
        "<code>reason</code>, <code>acknowledged</code> (0/1), <code>acknowledged_at</code>, and <code>acknowledged_by</code>.<br/>"
        "• <b><code>users</code>:</b> Manages system authentication with fields: <code>id</code>, <code>username</code> (UNIQUE), "
        "<code>password_hash</code> (salted Bcrypt hash), <code>role</code> (administrator / operator), and <code>created_at</code>."
    )
    story.append(Paragraph(p_other_tables, styles['ReportBody']))

    story.append(Spacer(1, 10))
    story.append(Paragraph("12. DASHBOARD DESIGN & FEATURE IMPLEMENTATION", styles['ChapterTitle']))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1E3A8A"), spaceBefore=2, spaceAfter=14))

    dash_text = (
        "The Streamlit dashboard (<code>app.py</code>) provides a clean, engineering-grade human-machine interface (HMI). "
        "It is organized into five functional navigation views:<br/><br/>"
        "<b>1. Overview & Live Analytics:</b><br/>"
        "• <b>Top Telemetry Tiles:</b> Five key metric cards displaying instantaneous Voltage Spread (ΔV in mV and V), "
        "Minimum Cell Voltage, Maximum Cell Voltage, Pack Mean Voltage, and Peak Cell Temperature with thermal spread.<br/>"
        "• <b>Color-Coded Status Badges:</b> Dynamically rendered HTML/CSS pills indicating Mode (<code>SIMULATION</code> / <code>HARDWARE</code>) "
        "and Rule Status (<code>NORMAL</code> in green, <code>WARNING</code> in amber, <code>CRITICAL</code> in red, <code>SENSOR_FAULT</code> in purple).<br/>"
        "• <b>Interactive Cell Voltage Bar Chart:</b> Plotly visualization displaying individual cell bars. When imbalance occurs, the highest diverging "
        "cell is automatically highlighted in red while the lowest is highlighted in amber.<br/>"
        "• <b>Historical Spread Trend Chart:</b> Real-time Plotly time-series tracking ΔV_mV over time with horizontal dashed lines marking the "
        "20 mV Warning and 50 mV Critical thresholds.<br/>"
        "• <b>Multi-Cell Trendlines:</b> Traces each cell voltage as an independent color-coded trajectory, visually demonstrating single-cell divergence.<br/>"
        "• <b>Cell Sanity Matrix:</b> Tabular grid computing exact deviation from the pack mean for each cell (<i>Dev_i = (V_i - V_mean) · 1000</i>) "
        "and assigning condition labels ('Nominal', 'Warning Imbalance', 'Critical Deviation').<br/><br/>"
        "<b>2. Historical Records & Export:</b> Displays scrollable tabular telemetry with instant CSV snapshot generation and file download.<br/>"
        "<b>3. Alert Management:</b> Lists logged alarm events with timestamps, affected cell indices, and provides an <b>'Acknowledge Alert'</b> button.<br/>"
        "<b>4. AI/ML Diagnostics:</b> Shows Isolation Forest model status, extracted feature values from latest readings, live continuous anomaly scores, "
        "and an interactive retraining console.<br/>"
        "<b>5. System Configuration:</b> Allows operators to adjust voltage spread and thermal thresholds and save them directly to <code>config/thresholds.yaml</code>."
    )
    story.append(Paragraph(dash_text, styles['ReportBody']))

    story.append(PageBreak())

    # =========================================================================
    # CHAPTER 13: TESTING & RESULTS
    # =========================================================================
    story.append(Paragraph("13. TESTING, VERIFICATION & ACCEPTANCE CRITERIA", styles['ChapterTitle']))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1E3A8A"), spaceBefore=2, spaceAfter=14))

    p_test_intro = (
        "In strict compliance with engineering verification standards, the entire platform was subjected to automated unit and integration "
        "testing using the <b>Pytest framework</b> (<code>pytest.ini</code>, <code>tests/</code>). All test cases are automated, deterministic, "
        "and verified directly against the production codebase. Figure 6 summarizes test pass distribution across modules."
    )
    story.append(Paragraph(p_test_intro, styles['ReportBody']))

    # Embed Figure 6
    fig6_path = os.path.join(FIGURES_DIR, "fig6_test_results_chart.png")
    if os.path.exists(fig6_path):
        story.append(Spacer(1, 4))
        story.append(Image(fig6_path, width=475, height=210))
        story.append(Paragraph("Figure 6: Automated Test Suite Execution Results (Pytest Verification)", styles['FigureCaption']))

    story.append(Spacer(1, 6))
    story.append(Paragraph("Table 8: Comprehensive Automated Test Verification Suite (28 Test Cases)", styles['TableCaption']))

    test_table_data = [
        [Paragraph("<b>Test Module & Function</b>", styles['TableCellHeader']),
         Paragraph("<b>Engineering Purpose</b>", styles['TableCellHeader']),
         Paragraph("<b>Expected Behavior</b>", styles['TableCellHeader']),
         Paragraph("<b>Actual Result</b>", styles['TableCellHeader']),
         Paragraph("<b>Status</b>", styles['TableCellHeader'])],

        # Calculations
        [Paragraph("<code>test_voltage_spread_calc</code>", styles['TableCellBold']), Paragraph("Verify V_max, V_min, ΔV, ΔV_mV", styles['TableCell']), Paragraph("ΔV=0.050V, ΔV_mV=50.0mV, mean=3.82V", styles['TableCell']), Paragraph("Matched expected math exactly", styles['TableCell']), Paragraph("<b>PASS</b>", styles['TableCellBold'])],
        [Paragraph("<code>test_empty_null_voltages</code>", styles['TableCellBold']), Paragraph("Trap empty lists, None, NaN", styles['TableCell']), Paragraph("Return is_valid=False; no crash", styles['TableCell']), Paragraph("Safely flagged invalid", styles['TableCell']), Paragraph("<b>PASS</b>", styles['TableCellBold'])],
        [Paragraph("<code>test_temperature_metrics</code>", styles['TableCellBold']), Paragraph("Verify T_max, T_min, ΔT, mean_T", styles['TableCell']), Paragraph("T_max=32.1°C, ΔT=3.6°C, mean=29.6°C", styles['TableCell']), Paragraph("Matched thermal math", styles['TableCell']), Paragraph("<b>PASS</b>", styles['TableCellBold'])],
        [Paragraph("<code>test_rate_of_change</code>", styles['TableCellBold']), Paragraph("Verify dV/dt slope calculation", styles['TableCell']), Paragraph("dV/dt = -0.0200 V/s across dt=2.0s", styles['TableCell']), Paragraph("Matched derivative slope", styles['TableCell']), Paragraph("<b>PASS</b>", styles['TableCellBold'])],
        [Paragraph("<code>test_sensor_quality</code>", styles['TableCellBold']), Paragraph("Detect unphysical ADC readings", styles['TableCell']), Paragraph("Flag 0.1V as unphysical sensor issue", styles['TableCell']), Paragraph("Trapped out-of-bounds reading", styles['TableCell']), Paragraph("<b>PASS</b>", styles['TableCellBold'])],

        # Data Validation
        [Paragraph("<code>test_valid_json_payload</code>", styles['TableCellBold']), Paragraph("Verify valid JSON deserialization", styles['TableCell']), Paragraph("Extract sanitized dict; errors list empty", styles['TableCell']), Paragraph("Valid schema confirmed", styles['TableCell']), Paragraph("<b>PASS</b>", styles['TableCellBold'])],
        [Paragraph("<code>test_missing_pack_id</code>", styles['TableCellBold']), Paragraph("Reject payload missing pack_id", styles['TableCell']), Paragraph("is_valid=False, error cites 'pack_id'", styles['TableCell']), Paragraph("Rejected malformed payload", styles['TableCell']), Paragraph("<b>PASS</b>", styles['TableCellBold'])],
        [Paragraph("<code>test_malformed_json_str</code>", styles['TableCellBold']), Paragraph("Handle syntax corrupted JSON", styles['TableCell']), Paragraph("Trap JSONDecodeError gracefully", styles['TableCell']), Paragraph("Handled without crash", styles['TableCell']), Paragraph("<b>PASS</b>", styles['TableCellBold'])],
        [Paragraph("<code>test_empty_cell_list</code>", styles['TableCellBold']), Paragraph("Reject empty cell voltage array", styles['TableCell']), Paragraph("is_valid=False, cites empty list", styles['TableCell']), Paragraph("Rejected empty array", styles['TableCell']), Paragraph("<b>PASS</b>", styles['TableCellBold'])],
        [Paragraph("<code>test_hw_mode_parsing</code>", styles['TableCellBold']), Paragraph("Verify hardware mode tagging", styles['TableCell']), Paragraph("Preserves mode='hardware', source='esp32'", styles['TableCell']), Paragraph("Preserved mode tags", styles['TableCell']), Paragraph("<b>PASS</b>", styles['TableCellBold'])],

        # Database
        [Paragraph("<code>test_db_initialization</code>", styles['TableCellBold']), Paragraph("Verify automatic SQLite tables", styles['TableCell']), Paragraph("Tables battery_readings, alerts, users exist", styles['TableCell']), Paragraph("All tables initialized", styles['TableCell']), Paragraph("<b>PASS</b>", styles['TableCellBold'])],
        [Paragraph("<code>test_insert_retrieve</code>", styles['TableCellBold']), Paragraph("Parameterized insertion & query", styles['TableCell']), Paragraph("Inserted row_id>0; values match", styles['TableCell']), Paragraph("Stored and fetched cleanly", styles['TableCell']), Paragraph("<b>PASS</b>", styles['TableCellBold'])],
        [Paragraph("<code>test_empty_db_safety</code>", styles['TableCellBold']), Paragraph("Handle empty database queries", styles['TableCell']), Paragraph("Return None / empty list; zero crashes", styles['TableCell']), Paragraph("Empty state handled safely", styles['TableCell']), Paragraph("<b>PASS</b>", styles['TableCellBold'])],
        [Paragraph("<code>test_csv_export</code>", styles['TableCellBold']), Paragraph("Verify historical CSV generation", styles['TableCell']), Paragraph("Generate valid CSV with headers", styles['TableCell']), Paragraph("Exported CSV verified", styles['TableCell']), Paragraph("<b>PASS</b>", styles['TableCellBold'])],
        [Paragraph("<code>test_database_backup</code>", styles['TableCellBold']), Paragraph("Verify backup snapshot routine", styles['TableCell']), Paragraph("Create timestamped backup .db copy", styles['TableCell']), Paragraph("Snapshot verified on disk", styles['TableCell']), Paragraph("<b>PASS</b>", styles['TableCellBold'])],

        # Detection Rules
        [Paragraph("<code>test_normal_status</code>", styles['TableCellBold']), Paragraph("Classify balanced cells (ΔV<20mV)", styles['TableCell']), Paragraph("Status = 'NORMAL', affected_cells empty", styles['TableCell']), Paragraph("Classified as NORMAL", styles['TableCell']), Paragraph("<b>PASS</b>", styles['TableCellBold'])],
        [Paragraph("<code>test_warning_status</code>", styles['TableCellBold']), Paragraph("Classify warning spread (20-50mV)", styles['TableCell']), Paragraph("Status = 'WARNING', cites spread", styles['TableCell']), Paragraph("Classified as WARNING", styles['TableCell']), Paragraph("<b>PASS</b>", styles['TableCellBold'])],
        [Paragraph("<code>test_critical_status</code>", styles['TableCellBold']), Paragraph("Classify critical spread (≥50mV)", styles['TableCell']), Paragraph("Status = 'CRITICAL', cites spread", styles['TableCell']), Paragraph("Classified as CRITICAL", styles['TableCell']), Paragraph("<b>PASS</b>", styles['TableCellBold'])],
        [Paragraph("<code>test_crit_precedence</code>", styles['TableCellBold']), Paragraph("Check Critical precedes Warning", styles['TableCell']), Paragraph("Critical over-voltage overrides warning spread", styles['TableCell']), Paragraph("Precedence strictly enforced", styles['TableCell']), Paragraph("<b>PASS</b>", styles['TableCellBold'])],
        [Paragraph("<code>test_missing_not_healthy</code>", styles['TableCellBold']), Paragraph("Ensure missing data ≠ NORMAL", styles['TableCell']), Paragraph("Status = 'SENSOR_FAULT'", styles['TableCell']), Paragraph("Flagged SENSOR_FAULT", styles['TableCell']), Paragraph("<b>PASS</b>", styles['TableCellBold'])],

        # Alerts
        [Paragraph("<code>test_normal_no_alert</code>", styles['TableCellBold']), Paragraph("Verify NORMAL triggers zero alarms", styles['TableCell']), Paragraph("Return None; zero alerts in DB", styles['TableCell']), Paragraph("Zero alerts triggered", styles['TableCell']), Paragraph("<b>PASS</b>", styles['TableCellBold'])],
        [Paragraph("<code>test_warning_triggers</code>", styles['TableCellBold']), Paragraph("Verify WARNING logs alert record", styles['TableCell']), Paragraph("Alert returned; row written to alerts table", styles['TableCell']), Paragraph("Alert logged in SQLite", styles['TableCell']), Paragraph("<b>PASS</b>", styles['TableCellBold'])],
        [Paragraph("<code>test_cooldown_suppress</code>", styles['TableCellBold']), Paragraph("Verify cooldown suppresses repeats", styles['TableCell']), Paragraph("Second identical alert suppressed", styles['TableCell']), Paragraph("Suppression verified", styles['TableCell']), Paragraph("<b>PASS</b>", styles['TableCellBold'])],
        [Paragraph("<code>test_escalate_bypass</code>", styles['TableCellBold']), Paragraph("Escalation bypasses cooldown", styles['TableCell']), Paragraph("WARNING→CRITICAL triggers immediate alert", styles['TableCell']), Paragraph("Immediate alert triggered", styles['TableCell']), Paragraph("<b>PASS</b>", styles['TableCellBold'])],
        [Paragraph("<code>test_alert_ack</code>", styles['TableCellBold']), Paragraph("Verify operator acknowledgement", styles['TableCell']), Paragraph("acknowledged=1, unack count drops to 0", styles['TableCell']), Paragraph("Acknowledged successfully", styles['TableCell']), Paragraph("<b>PASS</b>", styles['TableCellBold'])],

        # ML Pipeline
        [Paragraph("<code>test_dataset_generation</code>", styles['TableCellBold']), Paragraph("Verify reproducible dataset", styles['TableCell']), Paragraph("Generate 500 rows with classes 0 & 1", styles['TableCell']), Paragraph("Balanced dataset generated", styles['TableCell']), Paragraph("<b>PASS</b>", styles['TableCellBold'])],
        [Paragraph("<code>test_train_inference</code>", styles['TableCellBold']), Paragraph("Train model & run inference", styles['TableCell']), Paragraph("F1≥0.50, correctly flag normal vs anom.", styles['TableCell']), Paragraph("F1=0.8000, 100% recall", styles['TableCell']), Paragraph("<b>PASS</b>", styles['TableCellBold'])],
        [Paragraph("<code>test_fallback_missing</code>", styles['TableCellBold']), Paragraph("Verify fallback when model absent", styles['TableCell']), Paragraph("model_active=False; fallback message", styles['TableCell']), Paragraph("Graceful fallback active", styles['TableCell']), Paragraph("<b>PASS</b>", styles['TableCellBold'])],
    ]
    t_test = Table(test_table_data, colWidths=[110, 105, 120, 100, 40])
    t_test.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E3A8A")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor("#FFFFFF"), colors.HexColor("#F8FAFC")]),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('ALIGN', (4,1), (4,-1), 'CENTER'),
        ('TEXTCOLOR', (4,1), (4,-1), colors.HexColor("#065F46")),
    ]))
    story.append(t_test)

    story.append(PageBreak())

    # =========================================================================
    # CHAPTER 14, 15, 16, 17, 18, 19: DISCUSSION, ADVANTAGES, LIMITATIONS, SCOPE, CONCLUSION, REFERENCES
    # =========================================================================
    story.append(Paragraph("14. RESULTS AND DISCUSSION", styles['ChapterTitle']))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1E3A8A"), spaceBefore=2, spaceAfter=14))

    p_results = (
        "<b>Summary of Experimental & Analytical Observations:</b><br/>"
        "1. <b>Simulation Responsiveness:</b> In simulation mode, the platform generates telemetry frames every 2.0 seconds with zero drift in timing. "
        "When switching scenarios in the dashboard, the transition from 'normal' (ΔV ~8 mV) to 'imbalance' smoothly crosses the 20 mV Warning line "
        "within 6 cycles and triggers a Critical alarm upon reaching 50 mV.<br/>"
        "2. <b>MQTT Ingestion Throughput:</b> Telemetry frames published over HiveMQ Cloud (TLS 8883) demonstrated round-trip latencies of 85–140 ms, "
        "well within the 2000 ms sampling budget. When cloud connectivity is intentionally interrupted, the fallback simulator continues logging locally without data loss.<br/>"
        "3. <b>Analytical Engine Precedence:</b> In all test cases, critical safety violations (over-voltage > 4.25V, critical temperature > 60°C) took strict precedence "
        "over warning-level voltage spreads, ensuring that acute single-cell emergencies are never masked by minor warnings.<br/>"
        "4. <b>Isolation Forest Anomaly Detection Performance:</b> Evaluated on 1,200 held-out test samples, the model achieved a <b>Recall of 1.0000 (100%)</b>, "
        "meaning zero critical anomaly events were misclassified as normal. The Precision was 0.6667 (60 false alarms out of 180 total anomaly predictions), "
        "which represents a deliberate, safety-first engineering trade-off: in high-voltage battery storage, false alarms are readily tolerated, whereas a false negative "
        "(missed thermal runaway) carries catastrophic consequences.<br/>"
        "5. <b>Database Concurrency:</b> Write-Ahead Logging eliminated database write collisions during simultaneous live streaming and historical CSV downloads."
    )
    story.append(Paragraph(p_results, styles['ReportBody']))

    story.append(Spacer(1, 10))
    story.append(Paragraph("15. PRACTICAL ADVANTAGES", styles['ChapterTitle']))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1E3A8A"), spaceBefore=2, spaceAfter=14))

    adv_text = (
        "• <b>Non-Destructive Safe Prototyping:</b> Incorporates a realistic 5-scenario physics simulator allowing students, researchers, and engineers to safely evaluate hazardous thermal and imbalance states without risking physical cell fires.<br/>"
        "• <b>Decoupled Multi-Layer Architecture:</b> Changes in one layer (e.g. migrating from HiveMQ Cloud to a local Mosquitto broker, or swapping Streamlit for a mobile app) do not require alterations to database schemas or math modules.<br/>"
        "• <b>Dual-Track Diagnostic Confidence:</b> Combines deterministic rule-based alarms (transparent, explainable) with unsupervised machine learning (sensitive to multi-variable drift), providing defense-in-depth.<br/>"
        "• <b>Prevention of Alarm Flooding:</b> State-aware cooldown timers prevent operator alert fatigue while ensuring immediate escalations are never delayed.<br/>"
        "• <b>Cost-Effective Hardware Interfacing:</b> Utilizes low-cost off-the-shelf ESP32 boards and 1% precision resistor networks (~₹1,230 total cost), making the solution economically viable for educational institutions."
    )
    story.append(Paragraph(adv_text, styles['ReportBody']))

    story.append(Spacer(1, 10))
    story.append(Paragraph("16. SYSTEM LIMITATIONS", styles['ChapterTitle']))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1E3A8A"), spaceBefore=2, spaceAfter=14))

    lim_text = (
        "In accordance with engineering academic integrity, the following practical limitations must be acknowledged:<br/>"
        "1. <b>Not a Certified Battery Protection Replacement:</b> This system is designed as a supervisory monitoring and diagnostic tool. "
        "It does <b>NOT</b> replace certified hardware-level Battery Management Systems, high-current pyrofuses, contactors, or secondary over-voltage disconnect circuits.<br/>"
        "2. <b>Resistor Divider Measurement Inaccuracies:</b> Ground-referenced resistor dividers accumulate common-mode error on upper cells (Cell 3 and Cell 4) "
        "due to resistor tolerance variations and ESP32 SAR ADC non-linearities below 0.15V and above 3.10V.<br/>"
        "3. <b>Empirical Aging Simulation:</b> The synthetic simulator uses linear-exponential decay approximations rather than electrochemical equivalent circuit models (Randles / Thevenin models).<br/>"
        "4. <b>Internet Dependency for Cloud Telemetry:</b> Operation with HiveMQ Cloud requires active wide-area network access; in remote offline facilities, local broker deployment is required."
    )
    story.append(Paragraph(lim_text, styles['ReportBody']))

    story.append(PageBreak())

    # Future Scope, Conclusion, References
    story.append(Paragraph("17. FUTURE SCOPE", styles['ChapterTitle']))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1E3A8A"), spaceBefore=2, spaceAfter=14))

    scope_text = (
        "Future research and development can expand this platform across several promising directions:<br/>"
        "• <b>Active Cell Balancing Hardware Integration:</b> Interfacing bidirectional inductive or capacitive charge-shuttling circuits controlled by edge MQTT commands to actively transfer charge from higher-voltage cells to weaker cells during operation.<br/>"
        "• <b>Dedicated Isolated BMS Front-End ICs:</b> Replacing analog resistor dividers with dedicated battery monitoring ICs (e.g. Analog Devices LTC6811 or Texas Instruments BQ76952) featuring galvanic isolation, internal 16-bit delta-sigma ADCs, and sub-millivolt accuracy.<br/>"
        "• <b>State of Charge (SoC) & State of Health (SoH) Estimation:</b> Implementing Extended Kalman Filtering (EKF) or Unscented Kalman Filtering (UKF) combining Coulomb counting with open-circuit voltage (OCV) lookup tables.<br/>"
        "• <b>Edge ML Inference via TensorFlow Lite for Microcontrollers:</b> Deploying quantized neural networks or tiny decision trees directly on the ESP32 core to execute real-time anomaly detection even during complete Wi-Fi communication blackouts.<br/>"
        "• <b>Automated Mobile Push Alerts:</b> Integrating push notification gateways (Telegram Bot API, WhatsApp Business API, Firebase Cloud Messaging) for instant critical alarm delivery to maintenance personnel smartphones."
    )
    story.append(Paragraph(scope_text, styles['ReportBody']))

    story.append(Spacer(1, 10))
    story.append(Paragraph("18. CONCLUSION", styles['ChapterTitle']))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1E3A8A"), spaceBefore=2, spaceAfter=14))

    conc_text = (
        "The project <b>'Battery Cell Imbalance Detection Using IoT Analytics'</b> successfully designed, implemented, and verified "
        "a complete, production-ready monitoring architecture addressing one of the most critical degradation modes in series lithium-ion battery packs. "
        "By systematically developing all six layers — from synthetic data generation and edge ESP32 firmware, through TLS-secured MQTT transport (HiveMQ Cloud), "
        "persistent SQLite relational storage, Node-RED supervisory automation, Scikit-learn Isolation Forest anomaly detection, to a reactive Streamlit web dashboard — "
        "the project establishes an end-to-end telemetry and diagnostic pipeline.<br/><br/>"
        "Key technical milestones achieved include:<br/>"
        "• Complete mathematical formulation of maximum, minimum, voltage spread (ΔV), millivolt scaling, and thermal gradients.<br/>"
        "• Strict enforcement of critical precedence over warning conditions, ensuring missing or corrupted sensor readings are safely flagged as SENSOR_FAULT.<br/>"
        "• Unsupervised anomaly detection attaining 100.0% sensitivity on held-out battery operational test sets.<br/>"
        "• Automated Pytest verification confirming 100% pass rate across all 28 unit and integration test cases.<br/><br/>"
        "For a Mechanical Engineering student, this project bridges the critical interface between physical energy storage hardware, thermal management, "
        "electrochemical cell degradation, and modern industrial IoT software engineering. The platform stands as an extensible foundation for academic "
        "demonstration, research publications, and future electric vehicle BMS prototypes."
    )
    story.append(Paragraph(conc_text, styles['ReportBody']))

    story.append(Spacer(1, 10))
    story.append(Paragraph("19. REFERENCES", styles['ChapterTitle']))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1E3A8A"), spaceBefore=2, spaceAfter=14))

    ref_text = (
        "[1] G. L. Plett, <i>Battery Management Systems, Volume I: Battery Modeling</i>, Artech House, Norwood, MA, USA, 2015.<br/>"
        "[2] F. T. Liu, K. M. Ting, and Z.-H. Zhou, 'Isolation Forest', in <i>Proceedings of the 8th IEEE International Conference on Data Mining (ICDM)</i>, Pisa, Italy, pp. 413–422, 2008.<br/>"
        "[3] D. Andrea, <i>Battery Management Systems for Large Lithium-Ion Battery Packs</i>, Artech House, Boston, MA, USA, 2010.<br/>"
        "[4] OASIS Standard, <i>MQTT Version 5.0 / Version 3.1.1 Specification</i>, OASIS Standard, 2019. Available: http://docs.oasis-open.org/mqtt/mqtt/<br/>"
        "[5] HiveMQ GmbH, <i>HiveMQ Cloud Documentation and MQTT Security Fundamentals</i>, 2024. Available: https://www.hivemq.com/cloud/<br/>"
        "[6] Streamlit Inc., <i>Streamlit Documentation: The Fastest Way to Build Data Apps</i>, 2024. Available: https://docs.streamlit.io<br/>"
        "[7] Espressif Systems, <i>ESP32 Technical Reference Manual (Version 5.1)</i>, Espressif Systems, Shanghai, China, 2023.<br/>"
        "[8] D. R. Hipp, <i>SQLite Documentation and Write-Ahead Logging (WAL) Architecture</i>, 2024. Available: https://www.sqlite.org/wal.html<br/>"
        "[9] OpenJS Foundation, <i>Node-RED: Low-Code Programming for Event-Driven Applications</i>, 2024. Available: https://nodered.org<br/>"
        "[10] F. Pedregosa et al., 'Scikit-learn: Machine Learning in Python', <i>Journal of Machine Learning Research</i>, vol. 12, pp. 2825–2830, 2011.<br/>"
        "[11] ReportLab Inc., <i>ReportLab PDF Generation User Guide (Version 4.x/5.x)</i>, 2024. Available: https://www.reportlab.com/docs/<br/>"
        "[12] J. D. Hunter, 'Matplotlib: A 2D Graphics Environment', <i>Computing in Science & Engineering</i>, vol. 9, no. 3, pp. 90–95, 2007."
    )
    story.append(Paragraph(ref_text, styles['ReportBody']))

    # Build the document using the two-pass NumberedCanvas
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"\n[SUCCESS] PDF Generation complete: {OUTPUT_PDF}")


if __name__ == "__main__":
    build_pdf()
