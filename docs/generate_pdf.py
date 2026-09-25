"""
AI-NIDS Complete Project Learning & Technical Guide
PDF Generator using ReportLab
"""

import os
import sys
from pathlib import Path

# ── ReportLab imports ────────────────────────────────────────────────────────
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    HRFlowable,
    Image,
    ListFlowable,
    ListItem,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
)
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib.utils import ImageReader

# ── Output path ──────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent
OUTPUT_PDF = BASE_DIR / "AI_NIDS_COMPLETE_GUIDE.pdf"

# ═══════════════════════════════════════════════════════════════════════════════
# COLOUR PALETTE  (Retro-Futuristic Technical Parchment)
# ═══════════════════════════════════════════════════════════════════════════════
C_BG        = colors.HexColor("#F4EFE6")   # sand / cream
C_PARCHMENT = colors.HexColor("#EFE7D8")   # parchment card
C_TEAL      = colors.HexColor("#1B4D4F")   # dark technical teal
C_RUST      = colors.HexColor("#B84A2A")   # terracotta rust
C_AMBER     = colors.HexColor("#C28829")   # amber warning
C_DARK      = colors.HexColor("#2B2520")   # near-black brown
C_MID       = colors.HexColor("#6E6456")   # muted mid-brown
C_LIGHT     = colors.HexColor("#BAA894")   # light tan
C_WHITE     = colors.white
C_ATTACK    = colors.HexColor("#B84A2A")
C_BENIGN    = colors.HexColor("#1B4D4F")
C_CODE_BG   = colors.HexColor("#E8E0D4")

PAGE_W, PAGE_H = A4
MARGIN = 2.2 * cm

# ═══════════════════════════════════════════════════════════════════════════════
# STYLES
# ═══════════════════════════════════════════════════════════════════════════════
def make_styles():
    base = getSampleStyleSheet()
    styles = {}

    def S(name, **kw):
        styles[name] = ParagraphStyle(name, **kw)

    # Cover styles
    S("CoverTitle",    fontName="Helvetica-Bold",   fontSize=26, textColor=C_WHITE,
      alignment=TA_CENTER, spaceAfter=8, leading=32)
    S("CoverSub",      fontName="Helvetica",        fontSize=13, textColor=C_PARCHMENT,
      alignment=TA_CENTER, spaceAfter=6, leading=18)
    S("CoverMeta",     fontName="Helvetica-Oblique",fontSize=10, textColor=C_LIGHT,
      alignment=TA_CENTER, spaceAfter=4)

    # Chapter heading
    S("ChapterNum",    fontName="Helvetica-Bold",   fontSize=10, textColor=C_RUST,
      alignment=TA_LEFT,   spaceAfter=2, spaceBefore=18, leading=14,
      textTransform="uppercase")
    S("ChapterTitle",  fontName="Helvetica-Bold",   fontSize=20, textColor=C_TEAL,
      alignment=TA_LEFT,   spaceAfter=6, spaceBefore=4,  leading=26)

    # Section heading
    S("H2",            fontName="Helvetica-Bold",   fontSize=13, textColor=C_TEAL,
      alignment=TA_LEFT,   spaceAfter=4, spaceBefore=14, leading=17)
    S("H3",            fontName="Helvetica-Bold",   fontSize=11, textColor=C_DARK,
      alignment=TA_LEFT,   spaceAfter=3, spaceBefore=10, leading=15)
    S("H4",            fontName="Helvetica-BoldOblique", fontSize=10, textColor=C_MID,
      alignment=TA_LEFT,   spaceAfter=2, spaceBefore=6,  leading=14)

    # Body text
    S("Body",          fontName="Helvetica",        fontSize=10, textColor=C_DARK,
      alignment=TA_JUSTIFY, spaceAfter=6, leading=15)
    S("BodyLeft",      fontName="Helvetica",        fontSize=10, textColor=C_DARK,
      alignment=TA_LEFT,    spaceAfter=5, leading=15)
    S("Small",         fontName="Helvetica",        fontSize=9,  textColor=C_MID,
      alignment=TA_LEFT,    spaceAfter=4, leading=13)

    # Code style
    S("Code",          fontName="Courier",          fontSize=8.5,textColor=C_DARK,
      alignment=TA_LEFT,    spaceAfter=6, spaceBefore=4, leading=13,
      backColor=C_CODE_BG,  leftIndent=10, rightIndent=10,
      borderPad=6)

    # Label callout styles
    S("Callout",       fontName="Helvetica-Bold",   fontSize=9,  textColor=C_WHITE,
      alignment=TA_LEFT,    spaceAfter=2, leading=13,
      backColor=C_TEAL,     leftIndent=8, rightIndent=8, borderPad=5)
    S("Warning",       fontName="Helvetica-Bold",   fontSize=9,  textColor=C_WHITE,
      alignment=TA_LEFT,    spaceAfter=2, leading=13,
      backColor=C_RUST,     leftIndent=8, rightIndent=8, borderPad=5)
    S("Note",          fontName="Helvetica-Bold",   fontSize=9,  textColor=C_DARK,
      alignment=TA_LEFT,    spaceAfter=2, leading=13,
      backColor=C_PARCHMENT,leftIndent=8, rightIndent=8, borderPad=5)
    S("Tip",           fontName="Helvetica-Bold",   fontSize=9,  textColor=C_WHITE,
      alignment=TA_LEFT,    spaceAfter=2, leading=13,
      backColor=C_AMBER,    leftIndent=8, rightIndent=8, borderPad=5)

    # Bullet
    S("Bullet",        fontName="Helvetica",        fontSize=10, textColor=C_DARK,
      alignment=TA_LEFT,    spaceAfter=3, leading=14, leftIndent=14,
      bulletIndent=4,  bulletFontName="Helvetica-Bold", bulletFontSize=12)

    # TOC
    S("TOCHeading1",   fontName="Helvetica-Bold",   fontSize=11, textColor=C_TEAL,
      leftIndent=0,    spaceAfter=3,  leading=15)
    S("TOCHeading2",   fontName="Helvetica",        fontSize=10, textColor=C_DARK,
      leftIndent=14,   spaceAfter=2,  leading=13)

    # Diagram mono text
    S("Mono",          fontName="Courier",          fontSize=9,  textColor=C_TEAL,
      alignment=TA_CENTER,  spaceAfter=6, leading=13,
      backColor=C_CODE_BG,  borderPad=8)
    S("MonoLeft",      fontName="Courier",          fontSize=8.5,textColor=C_DARK,
      alignment=TA_LEFT,    spaceAfter=4, leading=12,
      backColor=C_CODE_BG,  leftIndent=10, borderPad=6)

    return styles

ST = make_styles()

# ═══════════════════════════════════════════════════════════════════════════════
# DOCUMENT TEMPLATE WITH HEADER & FOOTER
# ═══════════════════════════════════════════════════════════════════════════════
class AIDoc(BaseDocTemplate):
    def __init__(self, filename, **kw):
        super().__init__(filename, pagesize=A4, **kw)
        self.chapter_title = ""
        content_frame = Frame(
            MARGIN, MARGIN + 1.0*cm,
            PAGE_W - 2*MARGIN,
            PAGE_H - 2*MARGIN - 2.2*cm,
            id="content"
        )
        self.addPageTemplates([
            PageTemplate(id="normal", frames=[content_frame],
                         onPage=self._draw_page)
        ])

    def _draw_page(self, canvas, doc):
        canvas.saveState()
        # Header bar
        canvas.setFillColor(C_TEAL)
        canvas.rect(0, PAGE_H - 1.1*cm, PAGE_W, 1.1*cm, fill=1, stroke=0)
        canvas.setFillColor(C_WHITE)
        canvas.setFont("Helvetica-Bold", 8)
        canvas.drawString(MARGIN, PAGE_H - 0.7*cm, "AI-NIDS  \xb7  Complete Project Learning & Technical Guide")
        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(C_PARCHMENT)
        canvas.drawRightString(PAGE_W - MARGIN, PAGE_H - 0.7*cm,
                               self.chapter_title[:70])

        # Footer line
        canvas.setStrokeColor(C_LIGHT)
        canvas.setLineWidth(0.5)
        canvas.line(MARGIN, MARGIN + 0.6*cm, PAGE_W - MARGIN, MARGIN + 0.6*cm)
        canvas.setFillColor(C_MID)
        canvas.setFont("Helvetica", 8)
        canvas.drawString(MARGIN, MARGIN + 0.2*cm,
                          "MCA Mini Project  \xb7  AI-Based Real-Time Network Intrusion Detection System")
        canvas.setFont("Helvetica-Bold", 9)
        canvas.setFillColor(C_TEAL)
        canvas.drawRightString(PAGE_W - MARGIN, MARGIN + 0.2*cm, str(doc.page))
        canvas.restoreState()

    def afterFlowable(self, flowable):
        if isinstance(flowable, Paragraph):
            style = flowable.style.name
            if style in ("ChapterTitle", "H2"):
                self.chapter_title = flowable.getPlainText()[:70]
            if style == "ChapterTitle":
                self.notify("TOCEntry", (0, flowable.getPlainText(), self.page))
            elif style == "H2":
                self.notify("TOCEntry", (1, flowable.getPlainText(), self.page))

# ═══════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════
def P(text, style="Body"):
    return Paragraph(text, ST[style])

def H2(text):
    return Paragraph(text, ST["H2"])

def H3(text):
    return Paragraph(text, ST["H3"])

def H4(text):
    return Paragraph(text, ST["H4"])

def SP(n=8):
    return Spacer(1, n)

def HR(color=C_LIGHT, thickness=0.5):
    return HRFlowable(width="100%", thickness=thickness, color=color, spaceAfter=8, spaceBefore=4)

def Code(text):
    return Paragraph(text.replace("\n", "<br/>").replace(" ", "&nbsp;"), ST["Code"])

def Mono(text):
    return Paragraph(text.replace("\n", "<br/>").replace(" ", "&nbsp;"), ST["Mono"])

def MonoLeft(text):
    return Paragraph(text.replace("\n", "<br/>").replace(" ", "&nbsp;"), ST["MonoLeft"])

def Callout(text):
    return Paragraph(f"[ACTUAL PROJECT]&nbsp;&nbsp;{text}", ST["Callout"])

def Warn(text):
    return Paragraph(f"[IMPORTANT]&nbsp;&nbsp;{text}", ST["Warning"])

def Note(text):
    return Paragraph(f"[NOTE]&nbsp;&nbsp;{text}", ST["Note"])

def Tip(text):
    return Paragraph(f"[TIP]&nbsp;&nbsp;{text}", ST["Tip"])

def ConceptNote(text):
    return Paragraph(f"[CONCEPT]&nbsp;&nbsp;{text}", ST["Note"])

def chapter_header(num, title, subtitle=""):
    elems = [
        SP(16),
        P(f"CHAPTER {num}", "ChapterNum"),
        Paragraph(title, ST["ChapterTitle"]),
    ]
    if subtitle:
        elems.append(P(subtitle, "Small"))
    elems.append(HR(C_RUST, 1.5))
    elems.append(SP(6))
    return elems

def bullets(items, style="Bullet"):
    return [P(f"• &nbsp;{item}", style) for item in items]

def simple_table(headers, rows, col_widths=None):
    data = [headers] + rows
    t = Table(data, colWidths=col_widths)
    t.setStyle(TableStyle([
        ("BACKGROUND",  (0, 0), (-1, 0), C_TEAL),
        ("TEXTCOLOR",   (0, 0), (-1, 0), C_WHITE),
        ("FONTNAME",    (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",    (0, 0), (-1, 0), 9),
        ("ALIGN",       (0, 0), (-1, 0), "CENTER"),
        ("BACKGROUND",  (0, 1), (-1, -1), C_PARCHMENT),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [C_BG, C_PARCHMENT]),
        ("FONTNAME",    (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE",    (0, 1), (-1, -1), 8.5),
        ("ALIGN",       (0, 1), (-1, -1), "LEFT"),
        ("VALIGN",      (0, 0), (-1, -1), "MIDDLE"),
        ("GRID",        (0, 0), (-1, -1), 0.4, C_LIGHT),
        ("TOPPADDING",  (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING",(0,0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING",(0, 0), (-1, -1), 6),
    ]))
    return t

# ═══════════════════════════════════════════════════════════════════════════════
# CONTENT BUILDING FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def build_cover(story):
    # Full-page teal cover
    from reportlab.platypus import HRFlowable

    story.append(Spacer(1, 3.5*cm))
    story.append(Paragraph(
        "AI-Based Real-Time Network Intrusion<br/>Detection System Using Machine Learning",
        ParagraphStyle("CT2", fontName="Helvetica-Bold", fontSize=28,
                       textColor=C_TEAL, alignment=TA_CENTER, leading=36, spaceAfter=10)
    ))
    story.append(HRFlowable(width="80%", thickness=2, color=C_RUST, spaceAfter=12, spaceBefore=4))
    story.append(Paragraph(
        "Complete Project Learning &amp; Technical Guide",
        ParagraphStyle("CS2", fontName="Helvetica-Bold", fontSize=17,
                       textColor=C_RUST, alignment=TA_CENTER, leading=22, spaceAfter=20)
    ))
    story.append(Spacer(1, 1*cm))
    meta_style = ParagraphStyle("META", fontName="Helvetica", fontSize=11,
                                textColor=C_DARK, alignment=TA_CENTER, leading=18, spaceAfter=6)
    story.append(Paragraph("MCA Mini Project  —  Complete Study &amp; Reference Document", meta_style))
    story.append(Paragraph("GitHub: github.com/vrajkiran/AI-NIDS", meta_style))
    story.append(Spacer(1, 2*cm))

    # Info box
    info_data = [
        ["Technology Stack", "Python 3.10+, Flask, Scapy, Scikit-learn, SQLite, Chart.js"],
        ["ML Algorithm", "Random Forest Binary Classifier (100 Trees)"],
        ["Dataset", "CICIDS2017 — Friday DDoS Traffic"],
        ["Model Accuracy", "99.97%  (54,097 test samples)"],
        ["Detection Mode", "BENIGN / ATTACK (Binary Classification)"],
        ["Frontend", "Jinja2 Templates + Vanilla JavaScript + Chart.js"],
    ]
    t = Table(info_data, colWidths=[5*cm, 10*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",  (0, 0), (0, -1), C_TEAL),
        ("TEXTCOLOR",   (0, 0), (0, -1), C_WHITE),
        ("BACKGROUND",  (1, 0), (1, -1), C_PARCHMENT),
        ("FONTNAME",    (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME",    (1, 0), (1, -1), "Helvetica"),
        ("FONTSIZE",    (0, 0), (-1, -1), 9),
        ("GRID",        (0, 0), (-1, -1), 0.4, C_LIGHT),
        ("TOPPADDING",  (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING",(0,0),(-1,-1),  7),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("VALIGN",      (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(t)
    story.append(PageBreak())


def build_toc(story):
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph("TABLE OF CONTENTS", ParagraphStyle(
        "TOCTitle", fontName="Helvetica-Bold", fontSize=18,
        textColor=C_TEAL, alignment=TA_LEFT, spaceAfter=8, leading=24
    )))
    story.append(HR(C_RUST, 1.5))
    story.append(SP(8))

    toc = TableOfContents()
    toc.levelStyles = [
        ParagraphStyle("toc1", fontName="Helvetica-Bold", fontSize=11,
                       textColor=C_TEAL, leftIndent=0, spaceAfter=3, leading=15),
        ParagraphStyle("toc2", fontName="Helvetica", fontSize=10,
                       textColor=C_DARK, leftIndent=14, spaceAfter=2, leading=13),
    ]
    story.append(toc)
    story.append(PageBreak())


# ─────────────────────────────────────────────────────────
# CHAPTER 1 — PROJECT OVERVIEW
# ─────────────────────────────────────────────────────────
def ch1(story):
    story += chapter_header("1", "Project Overview", "What is AI-NIDS and why does it exist?")

    story.append(H2("1.1 Project Title"))
    story.append(P("AI-Based Real-Time Network Intrusion Detection System Using Machine Learning"))
    story.append(SP())

    story.append(H2("1.2 Simple One-Paragraph Explanation"))
    story.append(P(
        "AI-NIDS is a software system that watches your computer's network connection in real time. "
        "It captures the header information of every packet (like letters on an envelope — who sent it, "
        "who receives it, and how large it is, but never the actual content). It groups these packets into "
        "network conversations called flows, calculates statistics about each flow, and feeds those statistics "
        "to a pre-trained Random Forest machine learning model. The model then decides whether each conversation "
        "is BENIGN (normal) or ATTACK (malicious). Results are stored in a local SQLite database and displayed "
        "live on a web dashboard at http://127.0.0.1:5000."
    ))

    story.append(H2("1.3 System Flow at a Glance"))
    story.append(Mono(
        "NETWORK INTERFACE (Wi-Fi / Ethernet)\n"
        "           ↓\n"
        "   SCAPY PACKET SNIFFER\n"
        "    (Header Metadata Only)\n"
        "           ↓\n"
        "  FLOW AGGREGATION ENGINE\n"
        "   (Group Packets → Flows)\n"
        "           ↓\n"
        "  FEATURE EXTRACTION (10 metrics)\n"
        "           ↓\n"
        "  RANDOM FOREST ML MODEL\n"
        "           ↓\n"
        "   BENIGN           ATTACK\n"
        "      ↓                ↓\n"
        "  STORE RECORD    STORE RECORD\n"
        "                  + ALERT\n"
        "           ↓\n"
        "   SQLite DATABASE\n"
        "           ↓\n"
        "  FLASK REST API (/api/summary, /api/live …)\n"
        "           ↓\n"
        "  JAVASCRIPT POLLING (every 3 seconds)\n"
        "           ↓\n"
        "   WEB DASHBOARD (Charts, Tables, Alerts)"
    ))
    story.append(SP())

    story.append(H2("1.4 Real-World Problem Solved"))
    story.append(P(
        "Modern networks generate millions of packets per day. A human analyst cannot inspect "
        "each one individually. Traditional firewall rules match known patterns but fail against "
        "novel attacks. AI-NIDS uses a machine learning model trained on real attack data "
        "(CICIDS2017) to automatically classify every network conversation without manual rule updates."
    ))

    story.append(H2("1.5 Aim"))
    story.append(P(
        "To design, implement, and evaluate a stateful, passive Network Intrusion Detection System "
        "that classifies real-time network flows as BENIGN or ATTACK using a Random Forest classifier, "
        "without inspecting or storing raw packet payloads."
    ))

    story.append(H2("1.6 Objectives"))
    story += bullets([
        "Passively capture IP packet headers from authorized network interfaces using Scapy.",
        "Aggregate packets into bidirectional 5-tuple network flows.",
        "Compute 10 statistical features from each flow matching the CICIDS2017 feature set.",
        "Classify each flow as BENIGN or ATTACK using a pre-trained Random Forest model.",
        "Store all flow results in SQLite, tagged as REAL or DEMO.",
        "Provide a live web dashboard with Chart.js visualizations.",
        "Support one-click launch via run_ai_nids.bat (Windows).",
        "Provide a DEMO MODE for presentation testing without live packet generation.",
    ])

    story.append(H2("1.7 Scope"))
    story.append(H3("In Scope"))
    story += bullets([
        "Passive monitoring of authorized local network adapters (Wi-Fi, Ethernet, Loopback).",
        "Binary classification: BENIGN vs ATTACK.",
        "SQLite persistence and Flask REST API.",
        "Web dashboard with live-updating charts and tables.",
        "Dual-mode operation: REAL capture and DEMO presentation mode.",
    ])
    story.append(H3("Out of Scope"))
    story += bullets([
        "Deep Packet Inspection (payload decryption or content analysis).",
        "Automatic firewall blocking or packet injection.",
        "Multi-node distributed sensor deployment.",
        "User authentication system.",
    ])

    story.append(H2("1.8 Expected Outcome"))
    story.append(P(
        "A fully functional web dashboard accessible at http://127.0.0.1:5000 that displays "
        "live network traffic records, detected attacks, severity alerts, and performance charts. "
        "The Random Forest model achieves 99.97% accuracy on the CICIDS2017 test set of 54,097 samples."
    ))
    story.append(PageBreak())


# ─────────────────────────────────────────────────────────
# CHAPTER 2 — CYBERSECURITY BASICS
# ─────────────────────────────────────────────────────────
def ch2(story):
    story += chapter_header("2", "Cybersecurity Basics", "Essential concepts before we understand the project")

    story.append(H2("2.1 Computer Network"))
    story.append(P(
        "A <b>computer network</b> is a collection of computers and devices connected together to share "
        "resources and communicate. When your laptop connects to a router via Wi-Fi to access the internet, "
        "that is a network. Networks can be small (your home) or enormous (the global internet)."
    ))

    story.append(H2("2.2 Internet vs LAN"))
    story.append(Mono(
        "YOUR LAPTOP\n"
        "    ↓  (Wi-Fi)\n"
        "HOME ROUTER  ← Local Area Network (LAN)\n"
        "    ↓  (Ethernet / ISP link)\n"
        "INTERNET SERVICE PROVIDER\n"
        "    ↓\n"
        "GLOBAL INTERNET\n"
        "    ↓\n"
        "GOOGLE / YOUTUBE / any server"
    ))
    story.append(P(
        "A <b>LAN (Local Area Network)</b> is the private network inside your home or office. "
        "The <b>Internet</b> is the vast global network connecting millions of LANs worldwide."
    ))

    story.append(H2("2.3 IP Address"))
    story.append(P(
        "Every device on a network has an <b>IP address</b> — a numeric label like 192.168.1.105. "
        "Think of it as the postal address of your device. "
        "Two types exist: IPv4 (four numbers like 192.168.1.1) and IPv6 (longer, newer format). "
        "In this project, we work with IPv4 addresses extracted from packet headers."
    ))

    story.append(H2("2.4 Port Number"))
    story.append(P(
        "A <b>port</b> is a numbered channel on a device for a specific service. "
        "Your computer can run many services simultaneously:"
    ))
    story.append(simple_table(
        ["Port Number", "Protocol", "Service"],
        [["80", "TCP", "HTTP — Web browsing (unencrypted)"],
         ["443", "TCP", "HTTPS — Web browsing (encrypted)"],
         ["22", "TCP", "SSH — Secure remote login"],
         ["53", "UDP", "DNS — Domain name resolution"],
         ["8080", "TCP", "Alternative HTTP (often used by web apps)"],
         ["445", "TCP", "SMB — Windows file sharing"]],
        [3.5*cm, 3*cm, 9.5*cm]
    ))
    story.append(Note(
        "Port 443 appearing in DEMO data (e.g., 192.168.1.105 → 104.21.52.12:443) means "
        "a standard HTTPS web browsing session — this is BENIGN."
    ))

    story.append(H2("2.5 Protocol"))
    story.append(P(
        "A <b>protocol</b> is a set of rules defining how data is formatted and transmitted. "
        "This project works with three key protocols:"
    ))
    story.append(simple_table(
        ["Protocol", "Full Name", "Protocol Number", "Characteristics"],
        [["TCP", "Transmission Control Protocol", "6",
          "Reliable, ordered delivery. Handshake required. Used for web, SSH, email."],
         ["UDP", "User Datagram Protocol", "17",
          "Fast, no handshake. Used for DNS, streaming, VoIP."],
         ["ICMP", "Internet Control Message Protocol", "1",
          "Control messages. Ping uses ICMP. No ports."]],
        [2.5*cm, 5*cm, 3.5*cm, 5*cm]
    ))

    story.append(H2("2.6 Network Packet"))
    story.append(P(
        "A <b>packet</b> is the fundamental unit of data transmission on a network. "
        "Large files are broken into many small packets, sent individually, and reassembled at the destination."
    ))
    story.append(Mono(
        "+---------------------------------------------+\n"
        "|        PACKET HEADER (Metadata)             |\n"
        "|  Source IP:       192.168.1.105             |\n"
        "|  Destination IP:  104.21.52.12              |\n"
        "|  Source Port:     52410                     |\n"
        "|  Destination Port:443                       |\n"
        "|  Protocol:        TCP (6)                   |\n"
        "|  Packet Length:   1460 bytes                |\n"
        "|  Timestamp:       2026-08-30 20:50:12.342   |\n"
        "+---------------------------------------------+\n"
        "|          PAYLOAD (Not stored by AI-NIDS)    |\n"
        "|     Encrypted / raw data bytes              |\n"
        "+---------------------------------------------+"
    ))
    story.append(Callout(
        "AI-NIDS extracts ONLY the header fields shown above. The payload section "
        "is explicitly discarded. No passwords, no web content, no personal data is stored."
    ))

    story.append(H2("2.7 Network Traffic"))
    story.append(P(
        "<b>Network traffic</b> is the collective movement of packets across a network. "
        "When you watch YouTube, download a file, or send an email, your device generates network traffic. "
        "AI-NIDS monitors the metadata of this traffic to detect abnormal patterns."
    ))

    story.append(H2("2.8 Firewall vs IDS vs IPS"))
    story.append(simple_table(
        ["System", "What It Does", "Can Block?", "AI-NIDS Type"],
        [["Firewall", "Filters packets by fixed rules (IP/port)", "Yes", "No"],
         ["IDS (Intrusion Detection System)", "Detects suspicious activity, raises alerts", "No (detect only)", "Yes — AI-NIDS is an IDS"],
         ["IPS (Intrusion Prevention System)", "Detects AND actively blocks threats", "Yes", "No — AI-NIDS is passive"]],
        [4*cm, 6.5*cm, 2.5*cm, 3*cm]
    ))

    story.append(H2("2.9 NIDS vs HIDS"))
    story.append(P(
        "An IDS can monitor at two levels:"
    ))
    story += bullets([
        "<b>NIDS (Network IDS)</b> — Monitors network traffic flowing through a network segment. "
        "AI-NIDS is a NIDS. It inspects packets at the network level.",
        "<b>HIDS (Host IDS)</b> — Monitors activities on a single computer (file changes, log files, processes). "
        "AI-NIDS does NOT implement HIDS functionality.",
    ])

    story.append(H2("2.10 Cyber Attack Types Relevant to This Project"))
    story.append(simple_table(
        ["Attack Type", "Description", "Relevance to AI-NIDS"],
        [["DDoS", "Distributed Denial of Service — overwhelming a server with requests",
          "CICIDS2017 dataset contains DDoS flows. Model trained on these."],
         ["Port Scanning", "Systematically probing ports to find open services",
          "Generates high packet rate flows. Model may detect."],
         ["Brute Force", "Repeated login attempts",
          "Creates many small flows to port 22 (SSH) or 80 (HTTP)."],
         ["Data Exfiltration", "Unauthorized large data transfer outward",
          "Shows as high byte count flows."]],
        [3*cm, 6.5*cm, 6.5*cm]
    ))
    story.append(PageBreak())


# ─────────────────────────────────────────────────────────
# CHAPTER 3 — INTRUSION DETECTION SYSTEMS
# ─────────────────────────────────────────────────────────
def ch3(story):
    story += chapter_header("3", "Intrusion Detection Systems",
                            "Understanding IDS, NIDS, and why ML helps")

    story.append(H2("3.1 What Is an IDS?"))
    story.append(P(
        "An <b>Intrusion Detection System (IDS)</b> is a security monitoring tool that inspects "
        "network traffic or system activity and generates alerts when it detects suspicious or "
        "potentially malicious behavior. Think of it as a security camera system for your network — "
        "it watches everything and calls for attention when something unusual happens."
    ))

    story.append(H2("3.2 Two Classic IDS Approaches"))
    story.append(simple_table(
        ["Approach", "How It Works", "Advantage", "Disadvantage"],
        [["Signature-Based",
          "Matches traffic against a database of known attack signatures (like antivirus)",
          "Very accurate for known attacks. Fast.",
          "Cannot detect new (zero-day) attacks. Needs frequent updates."],
         ["Anomaly-Based",
          "Learns 'normal' behavior and alerts when deviations occur",
          "Can detect new, unknown attacks.",
          "Higher false positive rate. Requires training data."]],
        [3.5*cm, 5*cm, 4*cm, 4*cm]
    ))
    story.append(P("AI-NIDS uses a <b>supervised ML approach</b>, which is closer to anomaly-based "
                   "but trained on labeled examples of both BENIGN and ATTACK traffic."))

    story.append(H2("3.3 Traditional IDS vs AI-based IDS"))
    story.append(simple_table(
        ["Property", "Traditional Signature IDS", "AI-NIDS (This Project)"],
        [["Detection Method", "Fixed rule matching", "Random Forest ML model"],
         ["Zero-Day Attack Detection", "No", "Possible (if similar to training data)"],
         ["Update Required", "Manual signature updates", "Retrain model on new data"],
         ["Feature Used", "Packet content bytes", "Flow-level statistical metadata"],
         ["Privacy Risk", "May inspect payload content", "Metadata only — no payload stored"],
         ["Speed", "Very fast", "Fast — model inference in milliseconds"],
         ["Accuracy (CICIDS2017)", "N/A", "99.97%"]],
        [4.5*cm, 6.5*cm, 5*cm]
    ))

    story.append(H2("3.4 How AI-NIDS Works as a NIDS"))
    story.append(Mono(
        "HOME NETWORK\n"
        "   |\n"
        "   |← All packets flow here\n"
        "   ↓\n"
        "SCAPY (Passive Sniffer — sees all packets)\n"
        "   |\n"
        "   |← Copies header metadata only\n"
        "   ↓\n"
        "FLOW ENGINE (Groups related packets)\n"
        "   |\n"
        "   |← Computes 10 statistical features\n"
        "   ↓\n"
        "RANDOM FOREST MODEL\n"
        "   |\n"
        "   |← Classifies: BENIGN or ATTACK?\n"
        "   ↓\n"
        "DASHBOARD ALERT"
    ))
    story.append(Note(
        "Passive sniffing means Scapy reads packet copies that the OS network stack delivers. "
        "It does NOT intercept or modify traffic. Normal communications are not disrupted."
    ))
    story.append(PageBreak())


# ─────────────────────────────────────────────────────────
# CHAPTER 4 — PROBLEM STATEMENT
# ─────────────────────────────────────────────────────────
def ch4(story):
    story += chapter_header("4", "Problem Statement", "The specific problem this project solves")

    story.append(H2("4.1 Increasing Network Threats"))
    story.append(P(
        "Network attacks are growing in frequency and sophistication. DDoS attacks have reached "
        "terabit-per-second scales. Attackers use encrypted traffic, randomized timing, and distributed "
        "botnets to evade traditional detection. Manual inspection by security analysts is impossible "
        "at modern network speeds."
    ))

    story.append(H2("4.2 Limitations of Traditional Methods"))
    story += bullets([
        "<b>Static Firewall Rules</b> — Block known bad IPs but miss attack patterns from new sources.",
        "<b>Signature IDS</b> — Requires manual rule updates; blind to novel attack variants.",
        "<b>Manual Analysis</b> — A human cannot inspect millions of packets per day.",
        "<b>Payload Inspection</b> — Decrypting HTTPS traffic violates privacy and requires expensive hardware.",
    ])

    story.append(H2("4.3 The Core Problem This Project Addresses"))
    story.append(P(
        "How can we automatically detect malicious network activity in real time, "
        "using only non-invasive packet header metadata, without storing private user data, "
        "with high accuracy, and with a visual dashboard for monitoring?"
    ))

    story.append(H2("4.4 Academic Scope Distinction"))
    story.append(Warn(
        "This is an MCA Mini Project for academic demonstration. It monitors a single local machine's "
        "network interface. It does NOT replace enterprise-grade IDS tools like Snort or Suricata. "
        "It is designed to demonstrate the ML-based detection concept clearly and correctly."
    ))
    story.append(PageBreak())


# ─────────────────────────────────────────────────────────
# CHAPTER 5 — PROPOSED SYSTEM
# ─────────────────────────────────────────────────────────
def ch5(story):
    story += chapter_header("5", "Proposed System Architecture",
                            "How the solution is designed")

    story.append(H2("5.1 Overall Architecture"))
    story.append(Mono(
        "                        USER\n"
        "                          |\n"
        "                          ▼\n"
        "              WEB BROWSER / DASHBOARD\n"
        "        http://127.0.0.1:5000\n"
        "          (HTML + JavaScript + Chart.js)\n"
        "                          |\n"
        "             HTTP GET / POST requests\n"
        "                          ▼\n"
        "                  FLASK BACKEND\n"
        "                    (app.py)\n"
        "          ┌───────────┼───────────┐\n"
        "          ▼           ▼           ▼\n"
        "       SQLite    PredictionService  PacketCapture\n"
        "      (db.py)    (predict.py)       (packet_capture.py)\n"
        "     nids.db     RandomForest        Scapy sniff()\n"
        "          ▲           ▲           ▲\n"
        "          └───────────┼───────────┘\n"
        "                      |\n"
        "              Flow (flow.py)\n"
        "              Features (features.py)\n"
        "                      |\n"
        "            REAL NETWORK PACKETS"
    ))
    story.append(SP())

    story.append(H2("5.2 Component Descriptions"))

    story.append(H3("Web Dashboard (templates/ + static/)"))
    story.append(P(
        "Five HTML pages rendered by Flask/Jinja2: Dashboard, Live Traffic, Alerts, Model Performance. "
        "Vanilla JavaScript polls five REST API endpoints every 3 seconds and updates Chart.js charts "
        "and HTML table rows dynamically without full page reloads."
    ))

    story.append(H3("Flask Backend (app.py)"))
    story.append(P(
        "The central coordinator. Defines all HTTP routes, manages the monitoring thread lifecycle "
        "with threading.Lock, reads model metrics from evaluation_results.txt, and serves JSON data "
        "to the frontend."
    ))

    story.append(H3("SQLite Database (database/db.py + nids.db)"))
    story.append(P(
        "Two tables: network_traffic (stores each classified flow) and alerts (stores ATTACK events). "
        "Each record has a data_source column: 'REAL' for live Scapy captures, 'DEMO' for "
        "seeded presentation data."
    ))

    story.append(H3("PredictionService (ml/predict.py)"))
    story.append(P(
        "Loads three Joblib binary files on startup: the trained RandomForestClassifier model, "
        "the ordered feature list, and the MedianImputer preprocessing object. "
        "Provides the predict() method that returns BENIGN/ATTACK, confidence, and severity."
    ))

    story.append(H3("PacketCapture (network/packet_capture.py)"))
    story.append(P(
        "Runs Scapy sniff() in a background daemon thread. For each IP packet received, "
        "calls extract_packet_metadata() (features.py), updates flow state (_update_flow), "
        "calls PredictionService.predict() with flow features, and triggers save_detection() "
        "in app.py to persist the result."
    ))

    story.append(H3("Flow Engine (network/flow.py)"))
    story.append(P(
        "The Flow class tracks one bidirectional network conversation. It maintains separate "
        "forward and backward packet/byte counters and timestamps. Its to_ml_features() method "
        "returns a dictionary of the 10 features expected by the model."
    ))
    story.append(PageBreak())


# ─────────────────────────────────────────────────────────
# CHAPTER 6 — COMPLETE WORKING MECHANISM
# ─────────────────────────────────────────────────────────
def ch6(story):
    story += chapter_header("6", "Complete Working Mechanism",
                            "Step-by-step walkthrough from user click to dashboard update")

    story.append(H2("6.1 Step-by-Step Process"))

    steps = [
        ("STEP 1 — User Opens Application",
         "User double-clicks run_ai_nids.bat. This runs run.py which calls create_database() "
         "to initialize nids.db, starts Flask on 127.0.0.1:5000, waits 1.5 seconds, then "
         "automatically opens the default browser to the dashboard URL."),
        ("STEP 2 — Dashboard Loads",
         "Flask renders dashboard.html via the / route, passing summary stats, recent traffic rows, "
         "recent alerts, monitoring status, list of Scapy-detected interfaces, and default_duration from config."),
        ("STEP 3 — JavaScript Begins Polling",
         "main.js calls refreshPage() immediately, then sets a 3-second interval. "
         "refreshPage() runs 6 async fetch() calls in parallel: /api/status, /api/summary, "
         "/api/charts, /api/live, /api/alerts, and dashboard table refreshes."),
        ("STEP 4 — User Selects Interface and Starts Monitoring",
         "User selects a network interface (e.g., 'Wi-Fi') from the dropdown, sets capture "
         "duration (default: 10 seconds from config.py CAPTURE_DURATION), and clicks "
         "▶ START MONITORING. A POST request goes to /start-monitoring."),
        ("STEP 5 — Flask Validates and Starts Background Thread",
         "Flask validates the interface name exists in get_interface_names() and duration is "
         "between 5 and 3600 seconds. It creates a PacketCapture object with enabled=True and "
         "prediction_enabled=True, starts a daemon thread running run_monitor(), and redirects "
         "to dashboard."),
        ("STEP 6 — Scapy Begins Packet Sniffing",
         "PacketCapture.start() calls load_predictor() (loads the Random Forest model), then calls "
         "scapy.sniff(iface=interface, prn=handle_packet, timeout=duration, store=False, "
         "stop_filter=lambda _: stop_event.is_set()). store=False means Scapy does NOT keep "
         "packets in memory."),
        ("STEP 7 — Each Packet is Processed",
         "For each IP packet received by Scapy, handle_packet() is called. "
         "extract_packet_metadata() extracts: timestamp, source IP, destination IP, "
         "source port, destination port, protocol number, packet length. Non-IP packets return None."),
        ("STEP 8 — Packet is Added to a Flow",
         "_update_flow() checks if a matching flow already exists using the 5-tuple key "
         "(src_ip, dst_ip, src_port, dst_port, protocol) or its reverse. If no match, a new "
         "Flow object is created. Packet stats are added to the flow counters."),
        ("STEP 9 — Flow Features are Extracted",
         "flow.to_ml_features() computes the 10 features: Destination Port, Protocol, "
         "Flow Duration (microseconds), Total Fwd Packets, Total Backward Packets, "
         "Total Length of Fwd Packets, Total Length of Bwd Packets, Fwd Packet Length Mean, "
         "Bwd Packet Length Mean, Flow Bytes/s, Flow Packets/s."),
        ("STEP 10 — Random Forest Makes a Prediction",
         "PredictionService.predict(features) validates all 10 feature values are numeric, "
         "builds a one-row DataFrame in the correct column order, applies the MedianImputer "
         "(for any NaN values), calls model.predict() to get 0/1, and model.predict_proba() "
         "to get confidence probability."),
        ("STEP 11 — Prediction is Classified",
         "prediction_number=0 → 'BENIGN'. prediction_number=1 → 'ATTACK'. "
         "If confidence >= 0.90 and ATTACK: severity = 'HIGH'. "
         "If confidence < 0.90 and ATTACK: severity = 'MEDIUM'. BENIGN: 'No alert'."),
        ("STEP 12 — Result Saved to SQLite",
         "save_detection() in app.py formats a timestamp, calls insert_network_traffic() "
         "with data_source='REAL' to save the flow record. If prediction=='ATTACK', "
         "also calls insert_alert() with data_source='REAL', status='OPEN'."),
        ("STEP 13 — Dashboard Automatically Updates",
         "JavaScript's 3-second interval fires. /api/summary returns updated counts. "
         "/api/live returns the latest 50 traffic rows. /api/charts returns aggregated "
         "chart data. JavaScript updates KPI card numbers, rebuilds table HTML, and "
         "updates Chart.js datasets."),
    ]

    for title, desc in steps:
        story.append(KeepTogether([
            H3(title),
            P(desc),
            SP(4),
        ]))

    story.append(H2("6.2 Main Decision Flowchart"))
    story.append(Mono(
        "START\n"
        "  ↓\n"
        "run_ai_nids.bat → python run.py\n"
        "  ↓\n"
        "create_database() → nids.db ready\n"
        "  ↓\n"
        "Flask starts on 127.0.0.1:5000\n"
        "  ↓\n"
        "Browser opens dashboard\n"
        "  ↓\n"
        "User clicks START MONITORING\n"
        "  ↓\n"
        "POST /start-monitoring\n"
        "  ↓\n"
        "Background thread → PacketCapture.start()\n"
        "  ↓\n"
        "Scapy sniff() ← IP packet arrives\n"
        "  ↓\n"
        "extract_packet_metadata()\n"
        "  ↓\n"
        "_update_flow() → Flow updated\n"
        "  ↓\n"
        "flow.to_ml_features() → 10 features dict\n"
        "  ↓\n"
        "predictor.predict(features)\n"
        "  ↓\n"
        "Result: BENIGN or ATTACK + confidence\n"
        "  ↓\n"
        "BENIGN? ──YES──→ insert_network_traffic(REAL)\n"
        "  ↓ NO\n"
        "ATTACK\n"
        "  ↓\n"
        "insert_network_traffic(REAL)\n"
        "  ↓\n"
        "insert_alert(REAL, status=OPEN)\n"
        "  ↓\n"
        "JS polls /api/* every 3s → Dashboard updates\n"
        "  ↓\n"
        "Continue until timeout or STOP clicked"
    ))
    story.append(PageBreak())


# ─────────────────────────────────────────────────────────
# CHAPTER 7 — NETWORK PACKETS (Deep Dive)
# ─────────────────────────────────────────────────────────
def ch7(story):
    story += chapter_header("7", "Network Packets — Deep Dive",
                            "What a packet is and how AI-NIDS reads it")

    story.append(H2("7.1 What Is a Packet?"))
    story.append(P(
        "When your computer sends data over a network (e.g., loading a web page), the data is broken "
        "into small chunks called <b>packets</b>. Each packet can travel independently and may take "
        "different paths to the destination, where they are reassembled in order."
    ))
    story.append(P(
        "Every packet has two parts: a <b>header</b> (metadata describing the packet) and a "
        "<b>payload</b> (the actual data content). AI-NIDS uses ONLY the header."
    ))

    story.append(H2("7.2 IP Packet Header Structure"))
    story.append(Mono(
        "+----------------------------------------------+\n"
        "|               IP HEADER                     |\n"
        "|  Version / Header Length / TOS              |\n"
        "|  Total Length                               |\n"
        "|  Identification / Flags / Fragment Offset   |\n"
        "|  TTL (Time to Live)                         |\n"
        "|  Protocol  (6=TCP, 17=UDP, 1=ICMP)  ← USED |\n"
        "|  Header Checksum                            |\n"
        "|  Source IP Address               ← USED    |\n"
        "|  Destination IP Address          ← USED    |\n"
        "+----------------------------------------------+\n"
        "|               TCP HEADER                    |\n"
        "|  Source Port                     ← USED    |\n"
        "|  Destination Port                ← USED    |\n"
        "|  Sequence Number                            |\n"
        "|  Acknowledgment Number                      |\n"
        "|  Flags (SYN, ACK, FIN, RST...)              |\n"
        "|  Window Size / Checksum                     |\n"
        "+----------------------------------------------+\n"
        "|               PAYLOAD                       |\n"
        "|  [ IGNORED by AI-NIDS ]                     |\n"
        "+----------------------------------------------+"
    ))

    story.append(H2("7.3 What AI-NIDS Extracts from Each Packet"))
    story.append(P("The function <b>extract_packet_metadata()</b> in network/features.py extracts:"))
    story.append(simple_table(
        ["Field Extracted", "Source", "Example Value", "Purpose in AI-NIDS"],
        [["timestamp",     "packet.time (Unix epoch)", "1756567212.342", "Flow duration calculation"],
         ["source_ip",     "packet[IP].src", "192.168.1.105", "Flow identification"],
         ["destination_ip","packet[IP].dst", "104.21.52.12", "Flow identification"],
         ["source_port",   "packet[TCP/UDP].sport", "52410", "Flow key"],
         ["destination_port","packet[TCP/UDP].dport","443", "ML feature: Destination Port"],
         ["protocol",      "packet[IP].proto", "6 (TCP)", "ML feature: Protocol"],
         ["packet_length", "len(packet)", "1460", "Byte counting for features"],
         ["protocol_name", "Lookup dict {1:'ICMP',6:'TCP',17:'UDP'}", "TCP", "Database display"]],
        [3.5*cm, 4*cm, 3.5*cm, 5*cm]
    ))

    story.append(H2("7.4 Why Payload Is Never Stored"))
    story += bullets([
        "<b>Privacy</b>: Payloads may contain passwords, personal messages, or bank details.",
        "<b>Legal protection</b>: Capturing payload data without authorization is illegal in most countries.",
        "<b>Unnecessary for ML</b>: Flow statistics (rates, counts, sizes) are sufficient to classify attacks.",
        "<b>Storage efficiency</b>: Headers are tiny (40-60 bytes) vs payloads (up to 65,535 bytes).",
    ])
    story.append(PageBreak())


# ─────────────────────────────────────────────────────────
# CHAPTER 8 — SCAPY
# ─────────────────────────────────────────────────────────
def ch8(story):
    story += chapter_header("8", "Scapy — Packet Capture Engine",
                            "How AI-NIDS captures packets from the network")

    story.append(H2("8.1 What Is Scapy?"))
    story.append(P(
        "<b>Scapy</b> is a powerful Python library for packet manipulation, sniffing, crafting, "
        "and dissection. In AI-NIDS, it is used only for <b>passive sniffing</b> — reading copies "
        "of packets from the network interface without modifying or injecting anything."
    ))

    story.append(H2("8.2 How Scapy Captures Packets"))
    story.append(P(
        "Scapy calls the operating system's network capture API (Npcap on Windows, libpcap on Linux/macOS). "
        "The network card is placed in <b>promiscuous mode</b>, meaning it receives all packets "
        "on the network segment, not just those addressed to your machine."
    ))
    story.append(Mono(
        "Network Interface Card (Wi-Fi / Ethernet)\n"
        "           |\n"
        "    Npcap / libpcap driver\n"
        "           |\n"
        "      Scapy sniff()\n"
        "           |\n"
        "   prn=handle_packet callback\n"
        "           |\n"
        "  Called for each arriving packet"
    ))

    story.append(H2("8.3 The Scapy sniff() Call — Actual Code"))
    story.append(Code(
        "sniff(\n"
        "    iface=self.interface or None,   # Network adapter to listen on\n"
        "    prn=self.handle_packet,         # Function called per packet\n"
        "    timeout=self.duration,          # Stop after N seconds\n"
        "    store=False,                    # Don't keep raw packets in memory\n"
        "    stop_filter=lambda _: self.stop_event.is_set()  # Stop if user clicks STOP\n"
        ")"
    ))
    story.append(H4("Line-by-line explanation:"))
    story += bullets([
        "<b>iface</b>: Which network adapter to sniff. If empty, Scapy picks its default. "
        "The user selects from the dropdown which shows all adapters detected by get_interface_names().",
        "<b>prn</b>: The callback function. Scapy calls handle_packet(packet) for every received packet.",
        "<b>timeout</b>: Automatically stops sniffing after this many seconds (user-configured, 5–3600).",
        "<b>store=False</b>: Critical privacy setting. Tells Scapy NOT to accumulate packets in RAM. "
        "Each packet is processed and discarded.",
        "<b>stop_filter</b>: Checked after each packet. Returns True when the user clicks ■ STOP, "
        "signalling Scapy to exit the sniff loop.",
    ])

    story.append(H2("8.4 Windows vs Linux Considerations"))
    story.append(simple_table(
        ["Platform", "Driver Required", "Notes"],
        [["Windows", "Npcap (installed separately)", "WinPcap API-compatible mode required for Scapy. "
          "AI-NIDS installed Npcap with /winpcap_mode=yes."],
         ["Linux/macOS", "libpcap (usually pre-installed)", "May require running as root (sudo) for raw socket access."]],
        [3*cm, 4.5*cm, 8.5*cm]
    ))

    story.append(H2("8.5 Fallback Mechanism"))
    story.append(P(
        "If Scapy cannot access Layer-2 (raw Ethernet frames) because Npcap is missing or misconfigured, "
        "packet_capture.py automatically falls back to Layer-3 IP socket sniffing:"
    ))
    story.append(Code(
        "except RuntimeError as error:\n"
        "    if 'winpcap is not installed' not in str(error).lower():\n"
        "        # Fatal error — stop\n"
        "        self.error_message = 'Scapy capture error: ' + str(error)\n"
        "        return\n"
        "    # Try Layer-3 fallback\n"
        "    socket = conf.L3socket(iface=self.interface or None)\n"
        "    sniff(opened_socket=socket, prn=self.handle_packet,\n"
        "          timeout=self.duration, store=False,\n"
        "          stop_filter=lambda _: self.stop_event.is_set())"
    ))
    story.append(Callout(
        "After installing Npcap (which we did), conf.use_pcap = True and the fallback is not needed. "
        "Full Layer-2 packet capture is now active."
    ))
    story.append(PageBreak())


# ─────────────────────────────────────────────────────────
# CHAPTER 9 — NETWORK FLOWS
# ─────────────────────────────────────────────────────────
def ch9(story):
    story += chapter_header("9", "Network Flows",
                            "Why packets are grouped into flows before ML classification")

    story.append(H2("9.1 Packet vs Flow"))
    story.append(P(
        "A single network <b>packet</b> carries very little information on its own. "
        "A single packet might be 60 bytes from IP 10.0.0.1 to 8.8.8.8 on port 443. "
        "Is that normal or suspicious? Impossible to tell from one packet alone."
    ))
    story.append(P(
        "A <b>flow</b> is a group of packets belonging to the same network conversation. "
        "By grouping packets and computing statistics (how many? how fast? how many bytes?), "
        "we get meaningful features that can reveal attack patterns."
    ))
    story.append(Mono(
        "PACKET 1  (src:192.168.1.105:52410 → dst:104.21.52.12:443, TCP, 60 bytes) ─┐\n"
        "PACKET 2  (src:104.21.52.12:443   → dst:192.168.1.105:52410, TCP, 1460 bytes) ─┤\n"
        "PACKET 3  (src:192.168.1.105:52410 → dst:104.21.52.12:443, TCP, 200 bytes)  ─┤→ FLOW\n"
        "PACKET 4  (src:104.21.52.12:443   → dst:192.168.1.105:52410, TCP, 1460 bytes) ─┘\n"
        "\n"
        "All 4 packets share the same 5-tuple → they belong to one HTTPS flow."
    ))

    story.append(H2("9.2 The 5-Tuple Flow Key"))
    story.append(P(
        "A flow is uniquely identified by five fields — the <b>5-tuple</b>:"
    ))
    story.append(simple_table(
        ["Field", "Example Value", "Purpose"],
        [["Source IP",          "192.168.1.105",  "Originating host"],
         ["Destination IP",     "104.21.52.12",   "Target host"],
         ["Source Port",        "52410",           "Originating service/ephemeral port"],
         ["Destination Port",   "443",             "Target service port"],
         ["Protocol",           "6 (TCP)",         "Transport protocol"]],
        [3.5*cm, 4*cm, 8.5*cm]
    ))

    story.append(H2("9.3 Bidirectional Flow Matching"))
    story.append(P(
        "Network conversations are bidirectional. When computer A sends to B, B also replies back. "
        "AI-NIDS groups both directions into one flow using forward and reverse key matching:"
    ))
    story.append(Code(
        "def _update_flow(self, metadata: dict):\n"
        "    flow_key = metadata_to_flow_key(metadata)     # (srcIP, dstIP, srcPort, dstPort, proto)\n"
        "    reverse_key = metadata_to_reverse_flow_key(metadata)  # (dstIP, srcIP, dstPort, srcPort, proto)\n"
        "\n"
        "    if flow_key in self.flows:       # Forward packet — flow exists\n"
        "        flow = self.flows[flow_key]\n"
        "    elif reverse_key in self.flows:  # Reverse packet — same flow, opposite direction\n"
        "        flow = self.flows[reverse_key]\n"
        "    else:                            # New conversation — create flow\n"
        "        flow = Flow(src_ip, dst_ip, src_port, dst_port, protocol)\n"
        "        self.flows[flow_key] = flow"
    ))

    story.append(H2("9.4 Flow State Tracked by AI-NIDS"))
    story.append(P("The Flow class (network/flow.py) tracks:"))
    story.append(simple_table(
        ["Attribute", "Description"],
        [["start_time",             "Timestamp of the first packet in this flow"],
         ["last_time",              "Timestamp of the most recent packet"],
         ["forward_packet_count",   "Number of packets from source → destination"],
         ["backward_packet_count",  "Number of packets from destination → source"],
         ["forward_byte_count",     "Total bytes in forward direction"],
         ["backward_byte_count",    "Total bytes in backward direction"]],
        [5*cm, 11*cm]
    ))
    story.append(PageBreak())


# ─────────────────────────────────────────────────────────
# CHAPTER 10 — FEATURE EXTRACTION
# ─────────────────────────────────────────────────────────
def ch10(story):
    story += chapter_header("10", "Feature Extraction",
                            "The 10 statistical features used by the ML model")

    story.append(H2("10.1 Why Statistical Features?"))
    story.append(P(
        "The Random Forest model cannot directly understand raw packets. It needs numeric features. "
        "Statistical flow features capture the <b>behavior</b> of a conversation: "
        "How fast? How much data? How many packets? These patterns differ sharply between "
        "normal browsing and a DDoS flood."
    ))

    story.append(H2("10.2 Feature Formulas and Calculations"))
    story.append(Callout(
        "These are the ACTUAL 10 features from SELECTED_FEATURES in ml/preprocess.py "
        "and computed by flow.to_ml_features() in network/flow.py."
    ))

    features_data = [
        ["#", "Feature Name", "Formula / Source", "CICIDS2017?", "Live Scapy?", "Why Useful for Attack Detection"],
        ["1", "Destination Port",
         "packet[TCP/UDP].dport", "Yes", "Yes",
         "High-risk ports (22, 445, 8080) are common attack targets. Scanning hits many ports rapidly."],
        ["2", "Flow Duration",
         "(last_time - start_time) * 1,000,000 μs", "Yes", "Yes",
         "DDoS floods have very short duration per flow. Long SSH sessions differ from port scans."],
        ["3", "Total Fwd Packets",
         "count of forward packets", "Yes", "Yes",
         "DDoS has enormous forward packet counts. Scanning has very few."],
        ["4", "Total Backward Packets",
         "count of reverse packets", "Yes", "Yes",
         "Asymmetric flows (many fwd, few bwd) indicate one-way flooding."],
        ["5", "Total Length of Fwd Packets",
         "Σ forward packet lengths (bytes)", "Yes", "Yes",
         "DDoS uses large forward byte volumes."],
        ["6", "Total Length of Bwd Packets",
         "Σ backward packet lengths (bytes)", "Yes", "Yes",
         "Low backward bytes with high forward bytes indicates flooding."],
        ["7", "Fwd Packet Length Mean",
         "Fwd Bytes / Fwd Packets", "Yes", "Yes",
         "DDoS often sends fixed-size packets. Normal traffic varies in size."],
        ["8", "Bwd Packet Length Mean",
         "Bwd Bytes / Bwd Packets", "Yes", "Yes",
         "Server response size reveals service type and abnormal behavior."],
        ["9", "Flow Bytes/s",
         "Total Bytes / Duration (seconds)", "Yes", "Yes",
         "DDoS floods have extremely high bytes/sec. Normal HTTPS: 10-100 KB/s."],
        ["10", "Flow Packets/s",
         "Total Packets / Duration (seconds)", "Yes", "Yes",
         "DDoS: thousands of packets/sec. Normal DNS: 1-2 packets/sec."],
    ]

    t = Table(features_data, colWidths=[0.6*cm, 3.8*cm, 4*cm, 1.5*cm, 1.5*cm, 4.6*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",  (0, 0), (-1, 0), C_TEAL),
        ("TEXTCOLOR",   (0, 0), (-1, 0), C_WHITE),
        ("FONTNAME",    (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",    (0, 0), (-1, 0), 8),
        ("ALIGN",       (0, 0), (-1, 0), "CENTER"),
        ("FONTNAME",    (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE",    (0, 1), (-1, -1), 7.5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [C_BG, C_PARCHMENT]),
        ("GRID",        (0, 0), (-1, -1), 0.3, C_LIGHT),
        ("VALIGN",      (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING",  (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING",(0,0),(-1,-1),  4),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING",(0, 0), (-1, -1), 4),
    ]))
    story.append(t)
    story.append(SP())

    story.append(H2("10.3 to_ml_features() — Actual Code"))
    story.append(Code(
        "def to_ml_features(self) -> dict:\n"
        "    duration_seconds = self.duration_seconds           # last_time - start_time\n"
        "    duration_microseconds = duration_seconds * 1_000_000\n"
        "    bytes_per_second = self.total_bytes / duration_seconds if duration_seconds > 0 else 0\n"
        "    packets_per_second = self.total_packets / duration_seconds if duration_seconds > 0 else 0\n"
        "\n"
        "    return {\n"
        "        'Destination Port':           self.destination.port,\n"
        "        'Protocol':                   self.protocol,\n"
        "        'Flow Duration':              duration_microseconds,\n"
        "        'Total Fwd Packets':          self.forward_packet_count,\n"
        "        'Total Backward Packets':     self.backward_packet_count,\n"
        "        'Total Length of Fwd Packets':self.forward_byte_count,\n"
        "        'Total Length of Bwd Packets':self.backward_byte_count,\n"
        "        'Fwd Packet Length Mean':     fwd_bytes/fwd_pkts if fwd_pkts else 0,\n"
        "        'Bwd Packet Length Mean':     bwd_bytes/bwd_pkts if bwd_pkts else 0,\n"
        "        'Flow Bytes/s':               bytes_per_second,\n"
        "        'Flow Packets/s':             packets_per_second,\n"
        "    }"
    ))
    story.append(Note(
        "IMPORTANT: The feature list in ml/preprocess.py has 10 entries but flow.to_ml_features() "
        "returns 11 key-value pairs (includes 'Protocol' which is in flow.py but NOT in SELECTED_FEATURES). "
        "PredictionService.arrange_features() orders the DataFrame using self.feature_list loaded from "
        "feature_list.joblib — so only the 10 trained features are used for prediction."
    ))
    story.append(PageBreak())


# ─────────────────────────────────────────────────────────
# CHAPTER 11 — CICIDS2017 DATASET
# ─────────────────────────────────────────────────────────
def ch11(story):
    story += chapter_header("11", "CICIDS2017 Dataset",
                            "The training data that taught the model what attacks look like")

    story.append(H2("11.1 What Is CICIDS2017?"))
    story.append(P(
        "CICIDS2017 (Canadian Institute for Cybersecurity Intrusion Detection Evaluation Dataset 2017) "
        "is a benchmark dataset created by the University of New Brunswick, Canada. "
        "It contains labeled network flow records generated in a controlled lab environment "
        "where both normal and attack traffic was generated systematically."
    ))

    story.append(H2("11.2 Dataset File Used"))
    story.append(Callout(
        "File: data/Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv.parquet — "
        "Friday afternoon DDoS attack traffic and benign background traffic."
    ))

    story.append(H2("11.3 Dataset Statistics"))
    story.append(simple_table(
        ["Metric", "Value"],
        [["Total rows loaded", "225,745"],
         ["Duplicate rows removed", "9,358"],
         ["Cleaned dataset size", "216,387 rows"],
         ["BENIGN flows", "89,199 (41.2%)"],
         ["ATTACK flows (DDoS)", "127,188 (58.8%)"],
         ["Training set (75%)", "162,290 rows"],
         ["Test set (25%)", "54,097 rows"]],
        [6*cm, 10*cm]
    ))

    story.append(H2("11.4 Dataset Processing Pipeline"))
    story.append(Mono(
        "CICIDS2017 Parquet File\n"
        "         ↓\n"
        "load_csv_files() → pd.read_parquet()\n"
        "         ↓\n"
        "normalize_column_names() → strip whitespace from column headers\n"
        "         ↓\n"
        "check_required_columns() → ensure 10 features + Label exist\n"
        "         ↓\n"
        "Select only 10 SELECTED_FEATURES + Label column\n"
        "         ↓\n"
        "drop_duplicates() → remove 9,358 duplicate rows\n"
        "         ↓\n"
        "pd.to_numeric(errors='coerce') → force all features to float\n"
        "         ↓\n"
        "replace([inf, -inf], NaN) → handle infinite values\n"
        "         ↓\n"
        "convert_labels() → 'BENIGN' → 0, everything else → 1\n"
        "         ↓\n"
        "train_test_split(test_size=0.25, stratify=y)\n"
        "         ↓\n"
        "fit_imputer(x_train) → learn median values for NaN filling\n"
        "         ↓\n"
        "apply_imputer(x_train/x_test) → fill NaNs with training medians\n"
        "         ↓\n"
        "Random Forest Training"
    ))

    story.append(H2("11.5 Why CICIDS2017?"))
    story += bullets([
        "Publicly available academic benchmark — used in hundreds of research papers.",
        "Contains labeled flows with both BENIGN and known attack categories.",
        "Features are pre-computed flow statistics (matching what AI-NIDS calculates live).",
        "The Friday afternoon file contains high-volume DDoS traffic — ideal for binary classification demo.",
    ])
    story.append(PageBreak())


# ─────────────────────────────────────────────────────────
# CHAPTER 12 — DATA PREPROCESSING
# ─────────────────────────────────────────────────────────
def ch12(story):
    story += chapter_header("12", "Data Preprocessing",
                            "How raw CICIDS2017 data is cleaned before training")

    story.append(H2("12.1 Why Preprocessing Is Needed"))
    story.append(P(
        "Real-world datasets are messy. CICIDS2017 has column names with extra spaces, "
        "some values that are infinite or missing (NaN), and duplicate rows. "
        "ML models need clean, numeric, consistent data to train correctly."
    ))

    story.append(H2("12.2 Step-by-Step Preprocessing — Actual Implementation"))

    steps = [
        ("Step 1 — Column Name Normalization",
         "normalize_column_names() calls dataframe.columns.str.strip(). "
         "CICIDS2017 CSV files sometimes have column headers with leading/trailing spaces "
         "like ' Destination Port' instead of 'Destination Port'. Stripping removes these "
         "so feature selection works correctly.",
         "' Destination Port ' → 'Destination Port'"),
        ("Step 2 — Select Only Required Columns",
         "Only the 10 SELECTED_FEATURES and the 'Label' column are kept. "
         "The full CICIDS2017 dataset has 80+ columns. Keeping only 11 reduces memory and "
         "speeds up training significantly.",
         "80 columns → 11 columns"),
        ("Step 3 — Remove Duplicate Rows",
         "dataframe.drop_duplicates() removes 9,358 rows that are exact copies. "
         "Duplicates can bias the model to overfit on repeated patterns.",
         "225,745 → 216,387 rows"),
        ("Step 4 — Convert to Numeric",
         "pd.to_numeric(column, errors='coerce') converts every feature column to float. "
         "If a value cannot be converted (e.g., 'Infinity', 'N/A' text), it becomes NaN. "
         "This handles corrupt or non-numeric entries safely.",
         "'Infinity' string → NaN float"),
        ("Step 5 — Handle Infinite Values",
         "dataframe.replace([np.inf, -np.inf], np.nan) replaces positive and negative "
         "infinity with NaN. Flow Bytes/s can produce Inf if duration is zero. "
         "These are then handled by the imputer.",
         "inf → NaN → median value"),
        ("Step 6 — Binary Label Conversion",
         "convert_labels() converts the Label column: 'BENIGN' → 0, everything else → 1. "
         "In the Friday DDoS file, non-BENIGN labels include 'DDoS'. "
         "Using np.where makes this efficient.",
         "'BENIGN' → 0, 'DDoS' → 1"),
        ("Step 7 — Train/Test Split",
         "train_test_split(X, y, test_size=0.25, random_state=42, stratify=y). "
         "stratify=y ensures the same BENIGN:ATTACK ratio in both train and test sets. "
         "75% (162,290) for training, 25% (54,097) for testing.",
         "162,290 train + 54,097 test"),
        ("Step 8 — Median Imputation",
         "MedianImputer.fit(x_train) computes the median of each feature column "
         "from training data. MedianImputer.transform(dataframe) replaces any remaining "
         "NaN values with the learned medians. The imputer is saved to preprocessing_info.joblib "
         "so the same medians are used for live traffic during prediction.",
         "NaN → median of training feature column"),
    ]

    for title, desc, example in steps:
        story.append(KeepTogether([
            H3(title),
            P(desc),
            P(f"<b>Example:</b> {example}", "Small"),
            SP(4),
        ]))

    story.append(H2("12.3 MedianImputer Class — Actual Code"))
    story.append(Code(
        "class MedianImputer:\n"
        "    def fit(self, dataframe: pd.DataFrame) -> 'MedianImputer':\n"
        "        self.medians = dataframe.median(numeric_only=True).fillna(0)\n"
        "        return self\n"
        "\n"
        "    def transform(self, dataframe: pd.DataFrame) -> pd.DataFrame:\n"
        "        return dataframe.fillna(self.medians)"
    ))
    story.append(P(
        "A custom MedianImputer is used instead of sklearn's SimpleImputer to keep the "
        "preprocessing code beginner-friendly and easy to explain without complex dependencies."
    ))
    story.append(PageBreak())


# ─────────────────────────────────────────────────────────
# CHAPTER 13 — ML BASICS
# ─────────────────────────────────────────────────────────
def ch13(story):
    story += chapter_header("13", "Machine Learning Basics",
                            "Core concepts needed to understand the AI model")

    story.append(H2("13.1 What Is Machine Learning?"))
    story.append(P(
        "Machine learning (ML) is a method of programming where a computer learns patterns "
        "from data examples rather than following manually written rules. "
        "Instead of writing 'IF packet_count > 10000 AND duration < 1 THEN ATTACK', "
        "we give the computer thousands of examples of both BENIGN and ATTACK flows "
        "and let it discover the rules automatically."
    ))

    story.append(H2("13.2 Key Terminology"))
    story.append(simple_table(
        ["Term", "Simple Explanation", "In AI-NIDS"],
        [["Dataset",    "A collection of examples", "CICIDS2017 CSV file — 216,387 flow records"],
         ["Feature",    "An input variable / column", "Flow Duration, Destination Port, Bytes/s..."],
         ["Label / Target", "The correct answer for each example", "0=BENIGN or 1=ATTACK"],
         ["Training",   "Model learns patterns from training data", "75% of dataset (162,290 rows)"],
         ["Testing",    "Evaluate model on unseen data", "25% of dataset (54,097 rows)"],
         ["Model",      "The learned mathematical function", "RandomForestClassifier object"],
         ["Prediction", "Model's output for new data", "'BENIGN' or 'ATTACK'"],
         ["Confidence", "How certain the model is (0.0-1.0)", "predict_proba() output"],
         ["Classification", "Task: assign a label to each input", "Binary: BENIGN vs ATTACK"],
         ["Overfitting", "Model memorizes training data, fails on new data", "Avoided by test split and balanced weights"]],
        [3.5*cm, 5*cm, 7.5*cm]
    ))

    story.append(H2("13.3 Training vs Prediction"))
    story.append(Mono(
        "TRAINING (done ONCE with ml/train.py):\n"
        "  CICIDS2017 Data → Preprocessing → Features + Labels\n"
        "      → RandomForestClassifier.fit(X_train, y_train)\n"
        "      → Saves: random_forest_model.joblib\n"
        "\n"
        "PREDICTION (done for EVERY new live flow):\n"
        "  New Flow Features → PredictionService.predict()\n"
        "      → model.predict([features]) → 0 or 1\n"
        "      → model.predict_proba() → confidence\n"
        "      → 'BENIGN' or 'ATTACK'"
    ))
    story.append(Note(
        "Training is a slow one-time process (minutes). Prediction is fast (milliseconds per flow). "
        "AI-NIDS ships with a pre-trained model — you only need to retrain if you change the dataset."
    ))
    story.append(PageBreak())


# ─────────────────────────────────────────────────────────
# CHAPTER 14 — RANDOM FOREST
# ─────────────────────────────────────────────────────────
def ch14(story):
    story += chapter_header("14", "Random Forest — The ML Algorithm",
                            "How AI-NIDS's brain makes decisions")

    story.append(H2("14.1 What Is a Decision Tree?"))
    story.append(P(
        "A <b>Decision Tree</b> is a model that makes predictions by asking a series of yes/no questions "
        "about the input features, following a tree-like structure until it reaches a leaf node "
        "(the prediction). Imagine a doctor's diagnosis flowchart."
    ))
    story.append(Mono(
        "Is Flow Bytes/s > 500,000?\n"
        "   ↓ YES                  ↓ NO\n"
        "Is Duration < 1,000μs?   Is Fwd Packets > 100?\n"
        "  ↓ YES    ↓ NO              ↓ YES    ↓ NO\n"
        "ATTACK    BENIGN           ATTACK   BENIGN"
    ))

    story.append(H2("14.2 What Is Random Forest?"))
    story.append(P(
        "A <b>Random Forest</b> is an ensemble of many decision trees. Each tree is trained on a "
        "random subset of the training data and uses a random subset of features at each split. "
        "The final prediction is made by <b>majority voting</b> across all 100 trees."
    ))
    story.append(Mono(
        "              RANDOM FOREST (100 Trees)\n"
        "                        |\n"
        "    ┌──────────┬─────────┼──────────┬──────────┐\n"
        "    ▼          ▼         ▼          ▼          ▼\n"
        "  Tree 1    Tree 2    Tree 3  ... Tree 99   Tree 100\n"
        "  ATTACK    BENIGN    ATTACK      ATTACK    ATTACK\n"
        "    └──────────┴─────────┼──────────┴──────────┘\n"
        "                         ▼\n"
        "             MAJORITY VOTE: ATTACK (80/100 trees)\n"
        "                         ▼\n"
        "                     ATTACK\n"
        "               Confidence = 0.80"
    ))

    story.append(H2("14.3 Why Random Forest for This Project?"))
    story += bullets([
        "<b>Handles non-linear relationships</b> — Attack patterns are not simple linear thresholds.",
        "<b>No feature scaling required</b> — Random Forest works with raw values; no normalization needed.",
        "<b>Provides probability estimates</b> — predict_proba() gives confidence scores used for severity.",
        "<b>Robust to noise</b> — Ensemble voting reduces impact of individual tree errors.",
        "<b>Explainable</b> — Feature importance can be extracted to explain why a flow was classified as attack.",
        "<b>Well-understood algorithm</b> — Appropriate for an MCA academic project.",
    ])

    story.append(H2("14.4 Actual Training Configuration"))
    story.append(Code(
        "model = RandomForestClassifier(\n"
        "    n_estimators=100,         # 100 decision trees in the forest\n"
        "    random_state=42,          # Fixed seed for reproducibility\n"
        "    class_weight='balanced',  # Compensate for BENIGN/ATTACK imbalance\n"
        "    n_jobs=-1,                # Use all CPU cores for parallel training\n"
        ")\n"
        "model.fit(x_train_clean, y_train)  # Train on 162,290 cleaned rows"
    ))
    story.append(H4("Parameter explanations:"))
    story += bullets([
        "<b>n_estimators=100</b>: Build 100 independent trees. More trees → more stable predictions. "
        "100 is a good balance between accuracy and training speed.",
        "<b>random_state=42</b>: A fixed random seed so results are exactly reproducible every run.",
        "<b>class_weight='balanced'</b>: The dataset has more ATTACK rows (127,188) than BENIGN (89,199). "
        "Balanced weights make the model treat both classes equally during training.",
        "<b>n_jobs=-1</b>: Trains all 100 trees in parallel using all available CPU cores.",
    ])
    story.append(PageBreak())


# ─────────────────────────────────────────────────────────
# CHAPTER 15 — MODEL TRAINING
# ─────────────────────────────────────────────────────────
def ch15(story):
    story += chapter_header("15", "Model Training",
                            "How the Random Forest model was built and saved")

    story.append(H2("15.1 Training Command"))
    story.append(Code("python ml/train.py"))
    story.append(P("Run from the project root with the virtual environment activated."))

    story.append(H2("15.2 Training Steps — Actual Code Flow"))
    story.append(Mono(
        "train(data_path=DATA_DIR)\n"
        "  |\n"
        "  ├─ load_csv_files(data_path)  → pd.read_parquet() → raw DataFrame\n"
        "  ├─ clean_dataset(raw_data)    → strip, select, dedupe, numeric, NaN, labels\n"
        "  ├─ split_features_and_label() → X (features), y (0/1 target)\n"
        "  ├─ train_test_split(X, y, test_size=0.25, stratify=y)\n"
        "  ├─ fit_imputer(x_train)       → learn medians\n"
        "  ├─ apply_imputer(x_train/x_test) → fill NaN values\n"
        "  ├─ RandomForestClassifier.fit(x_train_clean, y_train)  ← TRAINING\n"
        "  ├─ model.predict(x_test_clean) → y_pred\n"
        "  ├─ build_evaluation_text(y_test, y_pred) → accuracy, precision, recall, F1\n"
        "  ├─ joblib.dump(model, MODEL_PATH)            → random_forest_model.joblib\n"
        "  ├─ joblib.dump(SELECTED_FEATURES, FEATURE_LIST_PATH)  → feature_list.joblib\n"
        "  └─ joblib.dump({imputer, label_mapping}, PREPROCESSOR_PATH) → preprocessing_info.joblib"
    ))

    story.append(H2("15.3 Saved Model Files"))
    story.append(simple_table(
        ["File", "Contains", "Used By"],
        [["random_forest_model.joblib",
          "Trained RandomForestClassifier with 100 decision trees",
          "PredictionService.__init__() on application startup"],
         ["feature_list.joblib",
          "List of 10 feature names in training order",
          "arrange_features() — ensures correct column order"],
         ["preprocessing_info.joblib",
          "MedianImputer fitted on training data, label_mapping dict",
          "apply imputer to live flow features before prediction"],
         ["evaluation_results.txt",
          "Human-readable accuracy, precision, recall, F1, confusion matrix",
          "Flask /model route → read_model_metrics() → model.html display"]],
        [5.5*cm, 6.5*cm, 4*cm]
    ))
    story.append(PageBreak())


# ─────────────────────────────────────────────────────────
# CHAPTER 16 — MODEL EVALUATION
# ─────────────────────────────────────────────────────────
def ch16(story):
    story += chapter_header("16", "Model Evaluation",
                            "How well the model performs — real results from evaluation_results.txt")

    story.append(H2("16.1 Evaluation Metrics Explained"))

    story.append(H3("Accuracy"))
    story.append(P("Percentage of all predictions that were correct."))
    story.append(Code("Accuracy = Correct Predictions / Total Predictions"))

    story.append(H3("Precision"))
    story.append(P("Of all flows predicted as ATTACK, what fraction were actually attacks?"))
    story.append(Code("Precision = True Positives / (True Positives + False Positives)"))
    story.append(P(
        "<b>High precision</b> means few false alarms. Low precision means many legitimate "
        "flows are wrongly flagged as attacks."
    ))

    story.append(H3("Recall (Sensitivity)"))
    story.append(P("Of all actual ATTACK flows, what fraction did the model catch?"))
    story.append(Code("Recall = True Positives / (True Positives + False Negatives)"))
    story.append(P(
        "<b>High recall</b> means the model catches most real attacks. Low recall means "
        "many real attacks are missed."
    ))

    story.append(H3("F1-Score"))
    story.append(P("Harmonic mean of Precision and Recall — balances both."))
    story.append(Code("F1 = 2 × (Precision × Recall) / (Precision + Recall)"))

    story.append(H2("16.2 Actual Results from evaluation_results.txt"))
    story.append(Callout(
        "These are the ACTUAL results from ml/model/evaluation_results.txt generated by ml/train.py."
    ))
    story.append(simple_table(
        ["Metric", "Score", "Interpretation"],
        [["Accuracy",  "0.9997 (99.97%)", "Correct on 54,080 of 54,097 test flows"],
         ["Precision", "0.9998 (99.98%)", "When it says ATTACK, it's right 99.98% of the time"],
         ["Recall",    "0.9996 (99.96%)", "Detects 99.96% of all actual attacks"],
         ["F1-Score",  "0.9997 (99.97%)", "Near-perfect balance of precision and recall"]],
        [4*cm, 4.5*cm, 7.5*cm]
    ))

    story.append(H2("16.3 Confusion Matrix"))
    story.append(P("The confusion matrix shows exactly how many predictions were correct or wrong:"))
    story.append(simple_table(
        ["", "PREDICTED BENIGN", "PREDICTED ATTACK"],
        [["ACTUAL BENIGN", "22,295 (True Negatives ✓)", "5 (False Positives ✗)"],
         ["ACTUAL ATTACK", "12 (False Negatives ✗)", "31,785 (True Positives ✓)"]],
        [4.5*cm, 5.5*cm, 5.5*cm]
    ))
    story.append(simple_table(
        ["Result Type", "Count", "Meaning"],
        [["True Positive (TP)",  "31,785", "ATTACK correctly identified as ATTACK"],
         ["True Negative (TN)",  "22,295", "BENIGN correctly identified as BENIGN"],
         ["False Positive (FP)", "5",      "BENIGN wrongly flagged as ATTACK (false alarm)"],
         ["False Negative (FN)", "12",     "ATTACK missed — classified as BENIGN (missed detection)"]],
        [4*cm, 2.5*cm, 9.5*cm]
    ))

    story.append(H2("16.4 What Do These Numbers Mean Practically?"))
    story.append(P(
        "With only <b>5 false positives</b> and <b>12 false negatives</b> out of 54,097 test flows, "
        "the model is highly reliable for academic demonstration. In real production systems, "
        "the model would need retraining on diverse multi-year attack datasets, but for the CICIDS2017 "
        "Friday DDoS scenario, these results are excellent."
    ))
    story.append(PageBreak())


# ─────────────────────────────────────────────────────────
# CHAPTER 17 — LIVE PACKET → ML PREDICTION
# ─────────────────────────────────────────────────────────
def ch17(story):
    story += chapter_header("17", "From Live Packet to ML Prediction",
                            "The complete inference chain at runtime")

    story.append(H2("17.1 The Complete Inference Pipeline"))
    story.append(Mono(
        "REAL NETWORK PACKET\n"
        "         ↓\n"
        "Scapy prn=handle_packet(packet) callback\n"
        "         ↓\n"
        "extract_packet_metadata(packet)\n"
        "  → {timestamp, src_ip, dst_ip, src_port, dst_port,\n"
        "     protocol, protocol_name, packet_length}\n"
        "         ↓\n"
        "_update_flow(metadata)\n"
        "  → Flow.add_packet(timestamp, src_ip, src_port, length)\n"
        "  → Updates: forward/backward counts and bytes, timestamps\n"
        "         ↓\n"
        "flow.to_ml_features()\n"
        "  → Returns 10-key dict: Destination Port, Flow Duration...\n"
        "         ↓\n"
        "PredictionService.predict(features)\n"
        "  → validate_features()  → check all 10 present, all numeric\n"
        "  → arrange_features()   → build 1-row DataFrame, correct order\n"
        "  → imputer.transform()  → fill any NaN with training medians\n"
        "  → model.predict()      → [0] or [1]\n"
        "  → model.predict_proba() → [[0.03, 0.97]]\n"
        "         ↓\n"
        "Result: {'prediction': 'ATTACK', 'confidence': 0.97, 'severity': 'HIGH'}\n"
        "         ↓\n"
        "save_detection(metadata, flow, result)\n"
        "  → insert_network_traffic(REAL)\n"
        "  → if ATTACK: insert_alert(REAL, status=OPEN)\n"
        "         ↓\n"
        "JS polls /api/summary → Dashboard shows updated counts"
    ))

    story.append(H2("17.2 Feature Order Matters"))
    story.append(P(
        "The Random Forest model was trained with features in a specific order. "
        "If the live feature vector has columns in a different order, predictions will be wrong. "
        "This is why arrange_features() loads feature_list.joblib (the saved SELECTED_FEATURES list) "
        "and explicitly constructs the DataFrame in that exact order:"
    ))
    story.append(Code(
        "ordered_row = {feature: float(feature_values[feature]) for feature in self.feature_list}\n"
        "dataframe = pd.DataFrame([ordered_row], columns=self.feature_list)\n"
        "# Columns are now in EXACTLY the same order as during training"
    ))

    story.append(H2("17.3 Known Limitation — Per-Packet vs Per-Flow Prediction"))
    story.append(Warn(
        "IMPORTANT LIMITATION: AI-NIDS calls to_ml_features() and predict() on EVERY packet "
        "that updates a flow, not just at the end of the flow. This means early packets in a flow "
        "have very few statistics (e.g., Total Fwd Packets = 1, Flow Duration = 0). "
        "The model may produce less reliable predictions for very new flows. "
        "As more packets arrive and update the flow, predictions stabilize."
    ))
    story.append(PageBreak())


# ─────────────────────────────────────────────────────────
# CHAPTER 18 — FLASK BACKEND
# ─────────────────────────────────────────────────────────
def ch18(story):
    story += chapter_header("18", "Flask Backend",
                            "How the web server organizes routes, threads, and data")

    story.append(H2("18.1 What Is Flask?"))
    story.append(P(
        "<b>Flask</b> is a lightweight Python web framework. It maps URLs (routes) to Python functions, "
        "renders HTML templates, and returns JSON responses. In AI-NIDS, Flask is both the web server "
        "that delivers the dashboard HTML and the API server that delivers data to JavaScript."
    ))

    story.append(H2("18.2 Complete Route Reference"))
    story.append(Callout("All routes are defined in app.py — these are the ACTUAL routes."))
    story.append(simple_table(
        ["Route", "Method", "Purpose", "Returns"],
        [["/"              , "GET",  "Main dashboard page", "HTML (dashboard.html)"],
         ["/live"          , "GET",  "Live traffic full table", "HTML (live_traffic.html)"],
         ["/alerts"        , "GET",  "Security alerts full table", "HTML (alerts.html)"],
         ["/model"         , "GET",  "Model performance metrics", "HTML (model.html)"],
         ["/start-monitoring","POST","Start Scapy background thread", "Redirect → /"],
         ["/stop-monitoring","POST","Stop Scapy thread", "Redirect → /"],
         ["/load-demo"     , "POST", "Seed 10 demo traffic + 4 demo alert records", "Redirect → /"],
         ["/clear-demo"    , "POST", "DELETE FROM ... WHERE data_source='DEMO'", "Redirect → /"],
         ["/api/status"    , "GET",  "Monitor thread active/stopped status", "JSON"],
         ["/api/summary"   , "GET",  "KPI counts: packets, flows, attacks, alerts, has_demo_data", "JSON"],
         ["/api/live"      , "GET",  "Latest 50 traffic records from SQLite", "JSON array"],
         ["/api/alerts"    , "GET",  "Latest 50 alert records from SQLite", "JSON array"],
         ["/api/charts"    , "GET",  "Aggregated chart datasets", "JSON"]],
        [4*cm, 2*cm, 6.5*cm, 3.5*cm]
    ))

    story.append(H2("18.3 Thread Safety with monitoring_lock"))
    story.append(P(
        "Flask runs in multiple threads. The packet capture also runs in a background thread. "
        "To prevent race conditions when reading/writing monitor_status and monitor_capture, "
        "all modifications use a threading.Lock:"
    ))
    story.append(Code(
        "monitor_lock = threading.Lock()\n"
        "\n"
        "# Example: checking if already running\n"
        "with monitor_lock:\n"
        "    if monitor_thread and monitor_thread.is_alive():\n"
        "        monitor_status['error'] = 'A capture session is already running.'\n"
        "        return redirect(url_for('dashboard'))"
    ))

    story.append(H2("18.4 read_model_metrics() — Parsing the Evaluation File"))
    story.append(P(
        "The /model route calls read_model_metrics() which reads evaluation_results.txt "
        "and uses regex to extract Accuracy, Precision, Recall, F1, and confusion matrix numbers. "
        "It includes a safe fallback dictionary returned if the file doesn't exist or parsing fails."
    ))

    story.append(H2("18.5 Flask Template Rendering"))
    story.append(P(
        "Flask uses Jinja2 for HTML templates. When dashboard() is called, it passes "
        "Python objects to the template:"
    ))
    story.append(Code(
        "return render_template(\n"
        "    'dashboard.html',\n"
        "    summary=get_dashboard_summary(DATABASE_PATH),  # KPI numbers\n"
        "    traffic=fetch_latest_traffic(DATABASE_PATH, 8), # 8 recent rows\n"
        "    alerts=fetch_latest_alerts(DATABASE_PATH, 8),   # 8 recent alerts\n"
        "    status=monitor_status,                          # Active/stopped\n"
        "    interfaces=get_interface_names(),               # Dropdown list\n"
        "    default_duration=CAPTURE_DURATION,              # 10 seconds\n"
        ")"
    ))
    story.append(PageBreak())


# ─────────────────────────────────────────────────────────
# CHAPTER 19 — DATABASE
# ─────────────────────────────────────────────────────────
def ch19(story):
    story += chapter_header("19", "Database Design",
                            "SQLite schema and data management")

    story.append(H2("19.1 Why SQLite?"))
    story += bullets([
        "Zero configuration — no server installation required.",
        "Single file (nids.db) — easy to backup, delete, or inspect.",
        "Built into Python's standard library — no extra installation.",
        "Appropriate scale for an academic project with thousands of records.",
    ])

    story.append(H2("19.2 Table: network_traffic"))
    story.append(simple_table(
        ["Column", "Type", "Description", "Example Value"],
        [["id",               "INTEGER PK AUTO", "Unique row identifier", "1"],
         ["timestamp",        "TEXT NOT NULL",   "Flow capture time (ISO format)", "2026-08-30 20:51:30"],
         ["source_ip",        "TEXT",            "Origin host IP address", "192.168.1.105"],
         ["destination_ip",   "TEXT",            "Target host IP address", "104.21.52.12"],
         ["source_port",      "INTEGER",         "Originating port number", "52410"],
         ["destination_port", "INTEGER",         "Target service port", "443"],
         ["protocol",         "TEXT",            "Protocol name (TCP/UDP/ICMP)", "TCP"],
         ["packet_count",     "INTEGER",         "Total packets in flow", "148"],
         ["byte_count",       "INTEGER",         "Total bytes in flow", "124500"],
         ["prediction",       "TEXT",            "ML result: BENIGN or ATTACK", "BENIGN"],
         ["confidence",       "REAL",            "Prediction probability (0.0-1.0)", "0.9850"],
         ["data_source",      "TEXT DEFAULT 'REAL'", "Origin: 'REAL' or 'DEMO'", "REAL"]],
        [3.5*cm, 3*cm, 5*cm, 4.5*cm]
    ))

    story.append(H2("19.3 Table: alerts"))
    story.append(simple_table(
        ["Column", "Type", "Description", "Example Value"],
        [["id",             "INTEGER PK AUTO", "Unique row identifier", "1"],
         ["timestamp",      "TEXT NOT NULL",   "Alert generation time", "2026-08-30 20:51:30"],
         ["source_ip",      "TEXT",            "Attack source IP", "45.33.32.156"],
         ["destination_ip", "TEXT",            "Target IP", "192.168.1.105"],
         ["attack_type",    "TEXT",            "Always 'ATTACK'", "ATTACK"],
         ["confidence",     "REAL",            "Model confidence score", "0.9940"],
         ["severity",       "TEXT",            "HIGH (>=0.90) or MEDIUM (<0.90)", "HIGH"],
         ["status",         "TEXT",            "Alert state: OPEN / REVIEWED / CLOSED", "OPEN"],
         ["data_source",    "TEXT DEFAULT 'REAL'","Origin: 'REAL' or 'DEMO'", "REAL"]],
        [3.5*cm, 3*cm, 5*cm, 4.5*cm]
    ))

    story.append(H2("19.4 Schema Auto-Migration"))
    story.append(P(
        "When create_database() is called at startup, it checks whether the data_source column "
        "already exists using PRAGMA table_info. If an older database is present without this column, "
        "it is added automatically without losing any existing data:"
    ))
    story.append(Code(
        "for table in ['network_traffic', 'alerts']:\n"
        "    columns = [row['name'] for row in cursor.execute(f'PRAGMA table_info({table})')]\n"
        "    if 'data_source' not in columns:\n"
        "        cursor.execute(f'ALTER TABLE {table} ADD COLUMN data_source TEXT DEFAULT \"REAL\"')"
    ))

    story.append(H2("19.5 Key SQL Queries Used"))
    story.append(Code(
        "-- Dashboard KPI summary\n"
        "SELECT COALESCE(SUM(packet_count),0) AS total_packets,\n"
        "       COUNT(DISTINCT src||':'||sp||'>'||dst||':'||dp||'/'||proto) AS total_flows,\n"
        "       SUM(CASE WHEN prediction='BENIGN' THEN 1 ELSE 0 END) AS normal_traffic,\n"
        "       SUM(CASE WHEN prediction='ATTACK' THEN 1 ELSE 0 END) AS detected_attacks\n"
        "FROM network_traffic;\n"
        "\n"
        "-- Clear only demo data (never touches REAL records)\n"
        "DELETE FROM network_traffic WHERE data_source = 'DEMO';\n"
        "DELETE FROM alerts WHERE data_source = 'DEMO';"
    ))
    story.append(PageBreak())


# ─────────────────────────────────────────────────────────
# CHAPTER 20 — FRONTEND ARCHITECTURE
# ─────────────────────────────────────────────────────────
def ch20(story):
    story += chapter_header("20", "Frontend Architecture",
                            "How the dashboard is built and how it communicates with Flask")

    story.append(H2("20.1 Technology Stack"))
    story.append(simple_table(
        ["Technology", "Role", "File"],
        [["Jinja2 (Flask templates)", "Server-side HTML generation", "templates/*.html"],
         ["Vanilla CSS",             "Retro-Futuristic styling",    "static/css/style.css"],
         ["Bootstrap 5 (CDN)",       "Responsive grid and utilities","templates/base.html"],
         ["Vanilla JavaScript",      "Polling, dynamic updates",     "static/js/main.js"],
         ["Chart.js (CDN)",          "Doughnut, Line, Bar charts",   "Referenced in base.html"]],
        [4.5*cm, 5*cm, 6.5*cm]
    ))

    story.append(H2("20.2 Frontend-Backend Communication Flow"))
    story.append(Mono(
        "BROWSER\n"
        "   |\n"
        "   | 1. Page load: GET /\n"
        "   ↓\n"
        "FLASK → render_template('dashboard.html', summary=..., traffic=...) → HTML response\n"
        "   |\n"
        "   | 2. JavaScript starts (main.js runs on page load)\n"
        "   ↓\n"
        "JS refreshPage() every 3 seconds:\n"
        "   ├─ fetch('/api/status')  → JSON → update status dot + message\n"
        "   ├─ fetch('/api/summary') → JSON → update KPI card numbers + demo badge\n"
        "   ├─ fetch('/api/charts')  → JSON → update Chart.js datasets\n"
        "   ├─ fetch('/api/live')    → JSON → rebuild traffic table HTML\n"
        "   └─ fetch('/api/alerts')  → JSON → rebuild alerts table HTML\n"
        "   |\n"
        "   | 3. User clicks START MONITORING:\n"
        "   ↓\n"
        "HTML form POST /start-monitoring → Flask redirects → GET / (page reload)"
    ))

    story.append(H2("20.3 Jinja2 Templates Structure"))
    story.append(simple_table(
        ["Template", "Route", "Content"],
        [["base.html",       "All pages (extended)", "Topbar nav, CSS/JS imports, live clock, status dot"],
         ["dashboard.html",  "/",        "KPI cards, controls panel, charts, recent traffic/alert tables"],
         ["live_traffic.html","/live",   "Full traffic table with 100 rows"],
         ["alerts.html",     "/alerts",  "Full alerts table with severity badges"],
         ["model.html",      "/model",   "Accuracy/Precision/Recall/F1 cards, confusion matrix, raw report"]],
        [4*cm, 3.5*cm, 8.5*cm]
    ))

    story.append(H2("20.4 Design Palette"))
    story.append(simple_table(
        ["CSS Variable", "Hex Color", "Usage"],
        [["Sand background",  "#F4EFE6", "Page background"],
         ["Parchment cards",  "#EFE7D8", "Panel backgrounds"],
         ["Dark Teal",        "#1B4D4F", "Headers, nav, BENIGN badges"],
         ["Terracotta Rust",  "#B84A2A", "ATTACK badges, alerts, borders"],
         ["Amber",            "#C28829", "Demo mode badge, MEDIUM severity"],
         ["Dark Brown",       "#2B2520", "Primary text color"]],
        [4*cm, 3*cm, 9*cm]
    ))

    story.append(H2("20.5 JavaScript Polling — Actual Timing"))
    story.append(Code(
        "// main.js — bottom of file\n"
        "updateLiveClock();              // Run clock immediately\n"
        "setInterval(updateLiveClock, 1000);  // Update clock every 1 second\n"
        "\n"
        "refreshPage();                 // Load all data immediately on page load\n"
        "setInterval(refreshPage, 3000); // Refresh all data every 3 seconds"
    ))
    story.append(PageBreak())


# ─────────────────────────────────────────────────────────
# CHAPTER 21 — DASHBOARD COMPONENTS
# ─────────────────────────────────────────────────────────
def ch21(story):
    story += chapter_header("21", "Dashboard Components",
                            "Every element explained: what it shows, where the data comes from")

    story.append(H2("21.1 Topbar Navigation"))
    story + bullets([
        "<b>AI-NIDS logo/brand</b>: Displays project title.",
        "<b>Nav links</b>: Dashboard / Live Traffic / Alerts / Model Performance.",
        "<b>Status dot</b>: Green (●) = MONITORING ACTIVE, Red (●) = MONITORING STOPPED. "
        "Updated via /api/status polling.",
        "<b>Live clock badge</b>: Displays current date and time updated every second by updateLiveClock().",
    ])
    story += bullets([
        "<b>AI-NIDS logo/brand</b>: Displays project title.",
        "<b>Nav links</b>: Dashboard / Live Traffic / Alerts / Model Performance.",
        "<b>Status dot</b>: Green = MONITORING ACTIVE, Red = MONITORING STOPPED. Updated via /api/status.",
        "<b>Live clock badge</b>: Current date and time, updated every second by updateLiveClock().",
    ])

    story.append(H2("21.2 DEMO MODE ACTIVE Badge"))
    story.append(P(
        "A golden badge '⚡ DEMO MODE ACTIVE' appears in the directive banner when demo data is present. "
        "It is controlled by the has_demo_data field in /api/summary JSON response. "
        "JavaScript shows/hides the badge by toggling the CSS class 'd-none'."
    ))

    story.append(H2("21.3 Monitoring Control Panel"))
    story.append(simple_table(
        ["Control", "Action", "Backend Effect"],
        [["Interface dropdown", "Select network adapter", "Sent as POST parameter to /start-monitoring"],
         ["Duration input (seconds)", "Set capture time (5–3600s)", "Sent as POST parameter"],
         ["▶ START MONITORING", "POST /start-monitoring", "Starts PacketCapture daemon thread"],
         ["■ STOP", "POST /stop-monitoring", "Calls monitor_capture.stop() → sets stop_event"],
         ["⚡ DEMO DATA", "POST /load-demo", "Calls seed_demo_data() — inserts 10 traffic + 4 alert rows"],
         ["🗑 CLEAR DEMO", "POST /clear-demo", "Calls clear_demo_data() — DELETE WHERE data_source='DEMO'"]],
        [4.5*cm, 4*cm, 7.5*cm]
    ))

    story.append(H2("21.4 KPI Cards"))
    story.append(simple_table(
        ["Card", "Data Source", "SQL Query Behind It"],
        [["Total Packets",    "/api/summary → total_packets",    "SUM(packet_count) FROM network_traffic"],
         ["Total Flows",      "/api/summary → total_flows",      "COUNT(DISTINCT 5-tuple)"],
         ["Normal Traffic",   "/api/summary → normal_traffic",   "SUM(CASE WHEN prediction='BENIGN')"],
         ["Detected Attacks", "/api/summary → detected_attacks", "SUM(CASE WHEN prediction='ATTACK')"],
         ["Active Alerts",    "/api/summary → active_alerts",    "COUNT(*) FROM alerts WHERE status='OPEN'"]],
        [4*cm, 5*cm, 7*cm]
    ))

    story.append(H2("21.5 Charts"))
    story.append(simple_table(
        ["Chart", "Type", "Data Source", "What It Shows"],
        [["Benign vs Attack",  "Doughnut", "/api/charts → benign_attack",
          "Proportion of BENIGN vs ATTACK flows. Teal=BENIGN, Rust=ATTACK."],
         ["Traffic Over Time", "Line",     "/api/charts → traffic_over_time",
          "Number of flows per minute (last 10 minutes). Shows traffic volume trend."],
         ["Alert Severity",    "Bar",      "/api/charts → attack_count",
          "Count of HIGH vs MEDIUM severity alerts. Rust=HIGH, Amber=MEDIUM."]],
        [3.5*cm, 2.5*cm, 5*cm, 5*cm]
    ))
    story.append(PageBreak())


# ─────────────────────────────────────────────────────────
# CHAPTER 22 — ALERT SYSTEM
# ─────────────────────────────────────────────────────────
def ch22(story):
    story += chapter_header("22", "Alert System",
                            "When and how security alerts are generated and stored")

    story.append(H2("22.1 What Triggers an Alert?"))
    story.append(P(
        "An alert is created ONLY when the Random Forest model predicts <b>ATTACK</b>. "
        "BENIGN predictions generate a traffic record but no alert. "
        "This logic is in save_detection() in app.py:"
    ))
    story.append(Code(
        "if result.get('prediction') == 'ATTACK':\n"
        "    insert_alert(\n"
        "        DATABASE_PATH,\n"
        "        {\n"
        "            'timestamp':      timestamp,\n"
        "            'source_ip':      flow.source.ip,\n"
        "            'destination_ip': flow.destination.ip,\n"
        "            'attack_type':    'ATTACK',\n"
        "            'confidence':     confidence,\n"
        "            'severity':       result.get('severity', 'MEDIUM'),\n"
        "            'status':         'OPEN',\n"
        "        },\n"
        "        data_source='REAL',\n"
        "    )"
    ))

    story.append(H2("22.2 Severity Assignment"))
    story.append(P(
        "Severity is determined by calculate_severity() in ml/predict.py:"
    ))
    story.append(Code(
        "def calculate_severity(prediction: str, confidence: float | None) -> str:\n"
        "    if prediction == 'BENIGN':\n"
        "        return 'No alert'\n"
        "    if confidence is not None and confidence >= 0.90:  # HIGH_CONFIDENCE_THRESHOLD\n"
        "        return 'HIGH'\n"
        "    return 'MEDIUM'"
    ))
    story.append(P(
        "The threshold 0.90 is defined in config.py as HIGH_CONFIDENCE_THRESHOLD. "
        "It can be changed there without modifying any other code."
    ))

    story.append(H2("22.3 Alert Status Flow"))
    story.append(Mono(
        "ATTACK predicted → INSERT alert with status='OPEN'\n"
        "                                    |\n"
        "                  (Future manual review)\n"
        "                                    ↓\n"
        "                          status='REVIEWED'\n"
        "                                    ↓\n"
        "                          status='CLOSED'\n"
        "\n"
        "Note: Status change UI is a FUTURE SCOPE feature.\n"
        "All current alerts remain as 'OPEN'."
    ))

    story.append(H2("22.4 Alert Information Displayed"))
    story.append(simple_table(
        ["Field", "Value Example", "Meaning"],
        [["Timestamp",      "2026-08-30 20:51:30", "When the attack flow was detected"],
         ["Source IP",      "45.33.32.156",        "IP address of the suspected attacker"],
         ["Destination IP", "192.168.1.105",       "IP address of the victim machine"],
         ["Attack Type",    "ATTACK",              "Always 'ATTACK' in current version"],
         ["Confidence",     "0.9940",              "Model certainty: 99.4%"],
         ["Severity",       "HIGH",                "HIGH (>=90%) or MEDIUM (<90%)"],
         ["Status",         "OPEN",                "Alert has not yet been reviewed"]],
        [3.5*cm, 4*cm, 8.5*cm]
    ))
    story.append(PageBreak())


# ─────────────────────────────────────────────────────────
# CHAPTER 23 — REAL MONITORING MODE
# ─────────────────────────────────────────────────────────
def ch23(story):
    story += chapter_header("23", "Real Monitoring Mode",
                            "Step-by-step guide to live packet capture and classification")

    story.append(H2("23.1 Prerequisites"))
    story += bullets([
        "Application started via run_ai_nids.bat or python run.py.",
        "Npcap installed (conf.use_pcap = True verified after installation).",
        "ML model files present in ml/model/ (random_forest_model.joblib etc.).",
        "Running on an authorized network that you own or have permission to monitor.",
    ])

    story.append(H2("23.2 Step-by-Step Usage"))
    steps = [
        ("1. Open Dashboard", "Navigate to http://127.0.0.1:5000. The status dot is Red (STOPPED)."),
        ("2. Select Interface",
         "In the Interface dropdown, select your active adapter. "
         "Typically 'Wi-Fi' for wireless or 'Ethernet' for wired. "
         "The list comes from get_interface_names() which reads Scapy's conf.ifaces."),
        ("3. Set Duration",
         "Enter how many seconds to capture (default: 10 from config.py CAPTURE_DURATION). "
         "For testing, 15–30 seconds gives enough time to generate multiple flows."),
        ("4. Click ▶ START MONITORING",
         "A POST request goes to /start-monitoring. Flask validates the inputs and starts "
         "a background daemon thread. The status dot turns Green."),
        ("5. Generate Network Activity",
         "Open a browser tab and visit websites (HTTPS to port 443 → likely BENIGN). "
         "The Scapy sniffer captures these packets and processes them into flows."),
        ("6. Observe Live Updates",
         "Every 3 seconds, the dashboard automatically refreshes. "
         "KPI cards update, new rows appear in the Recent Traffic table, "
         "and the Benign vs Attack chart updates its proportions."),
        ("7. Wait for Capture to Complete",
         "After the duration expires, Scapy stops automatically. "
         "The status dot returns to Red. The final summary reflects all captured flows."),
        ("8. Click ■ STOP (Optional Early Stop)",
         "Clicking STOP before the timer expires calls monitor_capture.stop() which "
         "sets stop_event = True. Scapy's stop_filter checks this and exits the sniff loop."),
        ("9. View Full Records",
         "Click 'LIVE TRAFFIC' in the topbar to see all recorded flows. "
         "Click 'ALERTS' to see any detected attacks. "
         "All records have data_source='REAL'."),
    ]
    for num_title, desc in steps:
        story.append(KeepTogether([H3(num_title), P(desc), SP(4)]))

    story.append(H2("23.3 What Happens in the Background"))
    story.append(P(
        "While the user browses the dashboard, the packet capture thread independently processes packets. "
        "Python's threading.Lock ensures that when save_detection() writes to SQLite and when "
        "the Flask API reads from SQLite, they don't collide. SQLite itself is thread-safe with "
        "check_same_thread=False enabled in get_connection()."
    ))
    story.append(PageBreak())


# ─────────────────────────────────────────────────────────
# CHAPTER 24 — DEMO MODE
# ─────────────────────────────────────────────────────────
def ch24(story):
    story += chapter_header("24", "Demo Mode",
                            "Presenting the project without live network traffic")

    story.append(H2("24.1 Why Demo Mode Exists"))
    story.append(P(
        "During a college presentation or project viva, generating real attack traffic is not practical "
        "or ethical. Demo Mode seeds the database with 10 realistic synthetic traffic records and "
        "4 alert records that look exactly like real captured data. The dashboard then displays "
        "populated charts, tables, and KPI counts."
    ))

    story.append(H2("24.2 Demo Data vs Real Data — Side-by-Side"))
    story.append(Mono(
        "REAL MODE:\n"
        "  User's actual network packets\n"
        "      ↓\n"
        "  Scapy sniffer (handle_packet)\n"
        "      ↓\n"
        "  ML prediction\n"
        "      ↓\n"
        "  SQLite (data_source = 'REAL')\n"
        "\n"
        "DEMO MODE:\n"
        "  POST /load-demo button clicked\n"
        "      ↓\n"
        "  seed_demo_data() called directly\n"
        "      ↓\n"
        "  Pre-written synthetic records inserted\n"
        "      ↓\n"
        "  SQLite (data_source = 'DEMO')"
    ))
    story.append(Warn(
        "Demo data records are NOT generated by the ML model. They are hardcoded realistic-looking "
        "values written directly into database/db.py. The confidence scores and predictions are "
        "manually specified, not computed."
    ))

    story.append(H2("24.3 The 10 Demo Traffic Records (Actual Data)"))
    story.append(simple_table(
        ["Source IP", "Destination", "Port", "Proto", "Packets", "Prediction", "Confidence"],
        [["192.168.1.105", "104.21.52.12",   "443", "TCP", "148",  "BENIGN", "0.9850"],
         ["192.168.1.105", "8.8.8.8",        "53",  "UDP", "12",   "BENIGN", "0.9920"],
         ["192.168.1.105", "142.250.190.46", "443", "TCP", "210",  "BENIGN", "0.9780"],
         ["45.33.32.156",  "192.168.1.105",  "80",  "TCP", "1250", "ATTACK", "0.9940"],
         ["185.220.101.5", "192.168.1.105",  "22",  "TCP", "45",   "ATTACK", "0.8850"],
         ["192.168.1.105", "13.107.42.14",   "443", "TCP", "84",   "BENIGN", "0.9910"],
         ["192.168.1.120", "192.168.1.1",    "53",  "UDP", "6",    "BENIGN", "0.9960"],
         ["198.51.100.44", "192.168.1.105",  "8080","TCP", "2150", "ATTACK", "0.9980"],
         ["192.168.1.105", "172.217.16.206", "443", "TCP", "92",   "BENIGN", "0.9890"],
         ["103.21.244.0",  "192.168.1.105",  "445", "TCP", "32",   "ATTACK", "0.8720"]],
        [3.5*cm, 3.5*cm, 1.5*cm, 2*cm, 2.5*cm, 2.5*cm, 2.5*cm]
    ))

    story.append(H2("24.4 Clearing Demo Data"))
    story.append(P(
        "Clicking '🗑 CLEAR DEMO' sends POST to /clear-demo, which calls clear_demo_data(). "
        "This executes: DELETE FROM network_traffic WHERE data_source = 'DEMO' and "
        "DELETE FROM alerts WHERE data_source = 'DEMO'. "
        "Records with data_source = 'REAL' are NEVER affected."
    ))

    story.append(H2("24.5 DEMO MODE ACTIVE Badge"))
    story.append(P(
        "has_demo_data() queries COUNT(*) WHERE data_source='DEMO' > 0. "
        "This boolean is included in /api/summary JSON. JavaScript's refreshSummary() "
        "calls demoBadge.classList.remove('d-none') when has_demo_data is true, "
        "making the golden badge visible."
    ))
    story.append(PageBreak())


# ─────────────────────────────────────────────────────────
# CHAPTER 25 — ONE-CLICK LAUNCHER
# ─────────────────────────────────────────────────────────
def ch25(story):
    story += chapter_header("25", "One-Click Launcher",
                            "run_ai_nids.bat and run.py explained")

    story.append(H2("25.1 run_ai_nids.bat — Windows Batch Launcher"))
    story.append(Code(
        "@echo off\n"
        "TITLE AI-NIDS Launcher\n"
        "COLOR 0A                           :: Green text on black background\n"
        "CD /D \"%~dp0\"                       :: Change to the directory of this .bat file\n"
        "\n"
        "IF EXIST \".venv\\Scripts\\python.exe\" (\n"
        "    SET \"PYTHON_EXE=.venv\\Scripts\\python.exe\"  :: Use virtual environment\n"
        ") ELSE (\n"
        "    SET \"PYTHON_EXE=python\"                    :: Fall back to system Python\n"
        ")\n"
        "\n"
        "\"%PYTHON_EXE%\" run.py               :: Launch the Python runner script\n"
        "\n"
        "IF ERRORLEVEL 1 (\n"
        "    echo [ERROR] AI-NIDS failed to start.\n"
        "    pause                          :: Keep window open so error is visible\n"
        ")"
    ))

    story.append(H2("25.2 run.py — Python Launcher"))
    story.append(Code(
        "def main():\n"
        "    print_banner()                 # Print ASCII banner with paths\n"
        "    create_database(DATABASE_PATH) # Ensure nids.db exists with correct schema\n"
        "\n"
        "    url = f'http://{HOST}:{PORT}'  # http://127.0.0.1:5000\n"
        "\n"
        "    # Open browser BEFORE Flask's blocking app.run()\n"
        "    browser_thread = threading.Thread(\n"
        "        target=open_browser,\n"
        "        args=(url, 1.5),            # Wait 1.5 seconds then open\n"
        "        daemon=True\n"
        "    )\n"
        "    browser_thread.start()\n"
        "\n"
        "    from app import app\n"
        "    app.run(host=HOST, port=PORT, debug=False)  # Blocking call"
    ))

    story.append(H2("25.3 Startup Sequence"))
    story.append(Mono(
        "run_ai_nids.bat\n"
        "      ↓\n"
        ".venv/Scripts/python.exe run.py\n"
        "      ↓\n"
        "print_banner() — ASCII welcome message\n"
        "      ↓\n"
        "create_database(DATABASE_PATH) — nids.db initialized / migrated\n"
        "      ↓\n"
        "browser_thread starts (waits 1.5s then opens http://127.0.0.1:5000)\n"
        "      ↓\n"
        "app.run(host='127.0.0.1', port=5000, debug=False) — Flask starts serving\n"
        "      ↓\n"
        "Browser opens dashboard automatically\n"
        "      ↓\n"
        "Application ready"
    ))
    story.append(PageBreak())


# ─────────────────────────────────────────────────────────
# CHAPTER 26 — FILE STRUCTURE
# ─────────────────────────────────────────────────────────
def ch26(story):
    story += chapter_header("26", "Project File Structure",
                            "Every file explained")

    story.append(H2("26.1 Directory Tree"))
    story.append(MonoLeft(
        "AI-NIDS/\n"
        "├── app.py                   ← Flask application (routes, thread management)\n"
        "├── config.py                ← All configurable constants (paths, host, port)\n"
        "├── run.py                   ← Python launcher (banner, DB init, browser open)\n"
        "├── run_ai_nids.bat          ← Windows one-click launcher (double-click to run)\n"
        "├── requirements.txt         ← Python package dependencies\n"
        "├── README.md                ← Project overview and setup guide\n"
        "├── .gitignore               ← Git ignore rules (.venv, nids.db, .log files)\n"
        "│\n"
        "├── database/\n"
        "│   ├── __init__.py\n"
        "│   ├── db.py                ← All SQLite functions (create, insert, fetch, demo)\n"
        "│   └── models.py            ← (Unused schema reference placeholder)\n"
        "│\n"
        "├── ml/\n"
        "│   ├── __init__.py\n"
        "│   ├── preprocess.py        ← SELECTED_FEATURES, MedianImputer, clean_dataset()\n"
        "│   ├── train.py             ← Training script: load → clean → train → evaluate → save\n"
        "│   ├── predict.py           ← PredictionService: loads model, predicts BENIGN/ATTACK\n"
        "│   └── model/\n"
        "│       ├── random_forest_model.joblib   ← Trained RandomForestClassifier\n"
        "│       ├── feature_list.joblib           ← Ordered list of 10 feature names\n"
        "│       ├── preprocessing_info.joblib     ← MedianImputer + label_mapping\n"
        "│       └── evaluation_results.txt        ← Accuracy, F1, confusion matrix\n"
        "│\n"
        "├── network/\n"
        "│   ├── __init__.py\n"
        "│   ├── features.py          ← extract_packet_metadata() + flow key functions\n"
        "│   ├── flow.py              ← Flow class: bidirectional stats + to_ml_features()\n"
        "│   └── packet_capture.py    ← PacketCapture class: Scapy sniff + prediction wire\n"
        "│\n"
        "├── data/\n"
        "│   ├── Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv.parquet\n"
        "│   └── README.md\n"
        "│\n"
        "├── database/\n"
        "│   └── nids.db              ← SQLite database (gitignored; created on first run)\n"
        "│\n"
        "├── static/\n"
        "│   ├── css/style.css        ← Custom retro-futuristic CSS theme\n"
        "│   └── js/main.js           ← All JavaScript: polling, charts, clock, tables\n"
        "│\n"
        "├── templates/\n"
        "│   ├── base.html            ← Base template with topbar, nav, clock, imports\n"
        "│   ├── dashboard.html       ← Main dashboard: KPIs, controls, charts, tables\n"
        "│   ├── live_traffic.html    ← Full 100-row traffic table\n"
        "│   ├── alerts.html          ← Full 100-row alerts table\n"
        "│   └── model.html           ← Model performance: accuracy cards, confusion matrix\n"
        "│\n"
        "├── tests/\n"
        "│   ├── test_pipeline.py          ← Flow feature extraction unit test\n"
        "│   └── test_prediction_service.py ← Prediction service unit test\n"
        "│\n"
        "└── docs/\n"
        "    ├── PROJECT_DOCUMENTATION.md\n"
        "    ├── SYSTEM_ARCHITECTURE.md\n"
        "    ├── DATABASE_DESIGN.md\n"
        "    ├── ML_PIPELINE.md\n"
        "    ├── USER_GUIDE.md\n"
        "    └── DEVELOPMENT_HISTORY.md"
    ))
    story.append(PageBreak())


# ─────────────────────────────────────────────────────────
# CHAPTER 27 — CODE WALKTHROUGH
# ─────────────────────────────────────────────────────────
def ch27(story):
    story += chapter_header("27", "Code Walkthrough",
                            "Most important functions explained line by line")

    story.append(H2("27.1 network/features.py — extract_packet_metadata()"))
    story.append(Code(
        "def extract_packet_metadata(packet) -> dict | None:\n"
        "    if IP not in packet:          # Skip non-IP frames (ARP, etc.)\n"
        "        return None\n"
        "\n"
        "    ip_layer = packet[IP]\n"
        "    protocol_number = int(ip_layer.proto)  # 1=ICMP, 6=TCP, 17=UDP\n"
        "    source_port = 0\n"
        "    destination_port = 0\n"
        "\n"
        "    if TCP in packet:\n"
        "        source_port = int(packet[TCP].sport)\n"
        "        destination_port = int(packet[TCP].dport)\n"
        "    elif UDP in packet:\n"
        "        source_port = int(packet[UDP].sport)\n"
        "        destination_port = int(packet[UDP].dport)\n"
        "    elif ICMP in packet:\n"
        "        source_port = 0              # ICMP has no ports\n"
        "        destination_port = 0\n"
        "\n"
        "    return {\n"
        "        'timestamp':        float(packet.time),    # Unix epoch timestamp\n"
        "        'source_ip':        ip_layer.src,\n"
        "        'destination_ip':   ip_layer.dst,\n"
        "        'source_port':      source_port,\n"
        "        'destination_port': destination_port,\n"
        "        'protocol':         protocol_number,\n"
        "        'protocol_name':    PROTOCOL_NAMES.get(protocol_number, str(protocol_number)),\n"
        "        'packet_length':    len(packet),           # Total frame size in bytes\n"
        "    }"
    ))

    story.append(H2("27.2 network/flow.py — add_packet()"))
    story.append(Code(
        "def add_packet(self, timestamp: float, source_ip: str,\n"
        "               source_port: int, packet_length: int) -> None:\n"
        "    if self.start_time is None:\n"
        "        self.start_time = timestamp     # Record first packet time\n"
        "\n"
        "    self.last_time = timestamp          # Always update last packet time\n"
        "\n"
        "    # Determine direction: is this packet from the original source?\n"
        "    is_forward = (source_ip == self.source.ip and\n"
        "                  source_port == self.source.port)\n"
        "    if is_forward:\n"
        "        self.forward_packet_count += 1\n"
        "        self.forward_byte_count += packet_length\n"
        "    else:\n"
        "        self.backward_packet_count += 1\n"
        "        self.backward_byte_count += packet_length"
    ))

    story.append(H2("27.3 ml/predict.py — PredictionService.predict()"))
    story.append(Code(
        "def predict(self, feature_values: dict) -> dict:\n"
        "    # Step 1: Build correctly ordered 1-row DataFrame\n"
        "    dataframe = self.arrange_features(feature_values)\n"
        "    #   - validate all 10 features present and numeric\n"
        "    #   - order columns to match training order\n"
        "    #   - apply MedianImputer for any NaN\n"
        "\n"
        "    # Step 2: Model predicts class label\n"
        "    prediction_number = int(self.model.predict(dataframe)[0])  # 0 or 1\n"
        "    prediction = 'ATTACK' if prediction_number == 1 else 'BENIGN'\n"
        "\n"
        "    # Step 3: Model returns probability for each class\n"
        "    confidence = self._confidence(dataframe, prediction_number)\n"
        "    # e.g., [0.03, 0.97] → confidence for ATTACK = 0.97\n"
        "\n"
        "    # Step 4: Determine severity based on confidence threshold\n"
        "    return {\n"
        "        'prediction': prediction,\n"
        "        'confidence': confidence,\n"
        "        'severity':   calculate_severity(prediction, confidence)\n"
        "    }"
    ))

    story.append(H2("27.4 database/db.py — insert_network_traffic()"))
    story.append(Code(
        "def insert_network_traffic(database_path, record, data_source='REAL'):\n"
        "    with get_connection(database_path) as connection:\n"
        "        connection.execute(\n"
        "            'INSERT INTO network_traffic (timestamp, source_ip, destination_ip,\n"
        "             source_port, destination_port, protocol, packet_count, byte_count,\n"
        "             prediction, confidence, data_source) VALUES (?,?,?,?,?,?,?,?,?,?,?)',\n"
        "            (\n"
        "                record['timestamp'],\n"
        "                record['source_ip'],\n"
        "                record['destination_ip'],\n"
        "                record['source_port'],\n"
        "                record['destination_port'],\n"
        "                record['protocol'],\n"
        "                record['packet_count'],\n"
        "                record['byte_count'],\n"
        "                record['prediction'],\n"
        "                record['confidence'],\n"
        "                data_source,           # 'REAL' or 'DEMO'\n"
        "            )\n"
        "        )"
    ))
    story.append(PageBreak())


# ─────────────────────────────────────────────────────────
# CHAPTER 28 — END-TO-END EXAMPLE
# ─────────────────────────────────────────────────────────
def ch28(story):
    story += chapter_header("28", "Complete End-to-End Example",
                            "Tracing one real packet from capture to dashboard")

    story.append(H2("28.1 Scenario: Your laptop browses https://www.google.com"))
    story.append(P(
        "Let's trace exactly what happens when your browser makes an HTTPS request "
        "to Google while AI-NIDS monitoring is active."
    ))

    steps = [
        ("1 — Browser sends HTTPS request",
         "Your browser sends a TCP packet:\n"
         "  src: 192.168.1.105:52432  →  dst: 142.250.190.46:443  (Google)\n"
         "  Protocol: TCP (6), Length: 512 bytes"),
        ("2 — Scapy captures the packet",
         "Scapy's sniff() callback fires: handle_packet(packet) is called."),
        ("3 — Metadata extracted",
         "extract_packet_metadata(packet) returns:\n"
         "  timestamp=1756567212.342, src_ip='192.168.1.105', dst_ip='142.250.190.46'\n"
         "  src_port=52432, dst_port=443, protocol=6, protocol_name='TCP', length=512"),
        ("4 — Flow identified",
         "_update_flow() checks self.flows. If this is the first packet to :443, "
         "a new Flow is created with flow_key=(192.168.1.105, 142.250.190.46, 52432, 443, 6). "
         "add_packet() sets start_time=1756567212.342, forward_packet_count=1, "
         "forward_byte_count=512."),
        ("5 — Google's reply arrives",
         "Google sends back: src=142.250.190.46:443 → dst=192.168.1.105:52432, length=1460 bytes. "
         "reverse_key matches the existing flow. add_packet() increments backward_packet_count=1, "
         "backward_byte_count=1460."),
        ("6 — Features extracted",
         "to_ml_features() computes (assume duration=0.01s):\n"
         "  Destination Port=443, Protocol=6, Flow Duration=10000μs\n"
         "  Total Fwd Packets=1, Total Bwd Packets=1\n"
         "  Total Length Fwd=512, Total Length Bwd=1460\n"
         "  Fwd Mean=512.0, Bwd Mean=1460.0\n"
         "  Flow Bytes/s=197200, Flow Packets/s=200"),
        ("7 — Random Forest prediction",
         "PredictionService.predict(features):\n"
         "  → 1-row DataFrame with 10 columns in correct order\n"
         "  → model.predict() → [0] (BENIGN)\n"
         "  → model.predict_proba() → [[0.989, 0.011]]\n"
         "  → confidence=0.989, prediction='BENIGN', severity='No alert'"),
        ("8 — Database insert",
         "save_detection() formats timestamp='2026-08-30 20:54:15'.\n"
         "insert_network_traffic() INSERT INTO network_traffic ... prediction='BENIGN', "
         "confidence=0.989, data_source='REAL'.\n"
         "Since prediction ≠ 'ATTACK', NO alert is inserted."),
        ("9 — Dashboard updates",
         "JavaScript's 3-second interval fires:\n"
         "  /api/summary returns total_packets += 1972, normal_traffic += 1\n"
         "  /api/live returns the new traffic row\n"
         "  Charts update with new BENIGN count\n"
         "  The BENIGN slice of the doughnut grows slightly"),
    ]

    for title, desc in steps:
        story.append(KeepTogether([
            H3(title),
            Code(desc),
            SP(4),
        ]))

    story.append(PageBreak())


# ─────────────────────────────────────────────────────────
# CHAPTER 29 — ERROR HANDLING
# ─────────────────────────────────────────────────────────
def ch29(story):
    story += chapter_header("29", "Error Handling",
                            "What happens when things go wrong")

    story.append(simple_table(
        ["Problem", "Cause", "What AI-NIDS Does"],
        [["Port 5000 already in use",
          "Another Flask instance or process using port 5000",
          "Flask raises OSError. run.py catches it and prints 'Server error'. "
          "Kill old process with: netstat -ano | findstr :5000, then taskkill /PID <pid> /F"],
         ["Npcap not installed",
          "WinPcap/Npcap driver missing",
          "Scapy falls back to Layer-3 socket sniffing. If that also fails, "
          "error_message is set and capture stops. Install Npcap to fix."],
         ["Permission denied on interface",
          "Not running as Administrator",
          "Scapy raises OSError. error_message set. Run as Administrator or install Npcap properly."],
         ["ML model files missing",
          "ml/train.py was never run",
          "load_predictor() raises FileNotFoundError. prediction remains 'PENDING'. "
          "Fix: python ml/train.py"],
         ["Invalid interface selected",
          "Interface name not in Scapy's conf.ifaces",
          "Flask validates interface in get_interface_names() before starting. "
          "Shows error message in dashboard."],
         ["Invalid duration (<5 or >3600)",
          "Out-of-range duration form field value",
          "Flask checks: if duration < 5 or > 3600, redirects with error message."],
         ["Monitoring started twice",
          "User clicks START while already monitoring",
          "monitor_lock check: if monitor_thread.is_alive(), rejects with 'already running' message."],
         ["Non-numeric ML features",
          "Zero-duration flow or corrupted packet",
          "validate_features() raises ValueError. Caught in handle_packet() exception block. "
          "Prediction set to 'ERROR', error logged."],
         ["Database write fails",
          "Disk full, permissions, or SQLite locked",
          "save_detection() wraps everything in try/except. Exception logged, "
          "monitor_status['error'] updated for dashboard display."],
         ["No packets arriving",
          "Interface wrong, no traffic, or wrong permissions",
          "sniff() times out normally. Capture ends with 0 packets. No error raised."]],
        [3.5*cm, 3.5*cm, 9*cm]
    ))
    story.append(PageBreak())


# ─────────────────────────────────────────────────────────
# CHAPTER 30 — SECURITY & PRIVACY
# ─────────────────────────────────────────────────────────
def ch30(story):
    story += chapter_header("30", "Security & Privacy",
                            "How AI-NIDS protects privacy and the ethical rules for its use")

    story.append(Warn(
        "MANDATORY: AI-NIDS must ONLY be used on networks and devices you own or have explicit "
        "written authorization to monitor. Unauthorized network monitoring is illegal in most countries."
    ))

    story.append(H2("30.1 Privacy Protections Built Into the Code"))
    story.append(simple_table(
        ["Protection", "Implementation", "Effect"],
        [["No payload storage",
          "store=False in sniff(). features.py only extracts header fields.",
          "Raw packet content, passwords, web page content never written to disk."],
         ["Metadata only",
          "extract_packet_metadata() discards packet object after extracting 8 header fields.",
          "Only IP addresses, ports, protocol, size, timestamp stored."],
         ["No packet injection",
          "AI-NIDS uses Scapy in read-only sniffing mode. No send() or sendp() calls.",
          "Cannot modify, block, or inject packets."],
         ["Local only",
          "Flask bound to 127.0.0.1 (localhost). Not accessible from other machines.",
          "Dashboard and API not exposed to the internet."],
         ["Demo data is synthetic",
          "Demo IP addresses (45.33.32.156, etc.) are real internet IPs used as examples only. "
          "They are NOT being attacked. No actual attack is performed.",
          "Demo mode is safe for presentation."]],
        [3.5*cm, 5*cm, 7.5*cm]
    ))

    story.append(H2("30.2 Disclaimer"))
    story.append(P(
        "This software is an educational tool developed for an MCA academic project. "
        "It is designed to demonstrate machine learning concepts applied to network security. "
        "It should only be run on personal equipment on networks you are authorized to use. "
        "The authors do not condone any unauthorized use of this software."
    ))
    story.append(PageBreak())


# ─────────────────────────────────────────────────────────
# CHAPTER 31 — LIMITATIONS
# ─────────────────────────────────────────────────────────
def ch31(story):
    story += chapter_header("31", "Known Limitations",
                            "Honest assessment of what AI-NIDS cannot do")

    story.append(simple_table(
        ["Limitation", "Explanation"],
        [["Binary classification only",
          "Model predicts only BENIGN or ATTACK. It cannot tell you the specific attack type "
          "(port scan vs DDoS vs brute force). Multiclass would require additional labeled training data."],
         ["Trained on one dataset file",
          "The model is trained only on Friday afternoon DDoS data from CICIDS2017. "
          "It may have reduced accuracy on other attack types or traffic from different networks."],
         ["Per-packet prediction limitation",
          "Prediction is made after every packet update to the flow, not just at flow completion. "
          "Early-flow predictions (when Fwd Packets=1) may be less accurate."],
         ["Encrypted traffic",
          "HTTPS payload is encrypted. AI-NIDS can only see that an HTTPS connection exists "
          "and its volume/timing statistics. It cannot see what web pages are requested."],
         ["Single interface monitoring",
          "Monitors one interface at a time. Production NIDS systems monitor all network segments."],
         ["No alert management UI",
          "Alerts cannot be marked as Reviewed or Closed through the UI. All alerts remain OPEN."],
         ["No authentication",
          "Anyone with access to http://127.0.0.1:5000 can view the dashboard. No login required."],
         ["Passive monitoring only",
          "Cannot block detected attacks. Cannot reset TCP connections. Detection only, no prevention."],
         ["Alert status 'OPEN' permanently",
          "The 'REVIEWED' and 'CLOSED' status values are defined in the schema but no UI to change them."]],
        [4.5*cm, 11.5*cm]
    ))
    story.append(PageBreak())


# ─────────────────────────────────────────────────────────
# CHAPTER 32 — FUTURE IMPROVEMENTS
# ─────────────────────────────────────────────────────────
def ch32(story):
    story += chapter_header("32", "Future Improvements",
                            "Realistic enhancements that could be added next")

    story.append(Tip("All items in this chapter are FUTURE SCOPE — not implemented in the current version."))

    story.append(simple_table(
        ["Future Feature", "Description", "Complexity"],
        [["Multiclass attack classification",
          "Train on full CICIDS2017 with all 14 attack categories (PortScan, Brute Force, etc.)",
          "Medium — requires labeled data and expanded model"],
         ["WebSocket live updates",
          "Replace polling (every 3 seconds) with WebSocket push for instant chart updates",
          "Medium — Flask-SocketIO library"],
         ["User authentication",
          "Login page with username/password before accessing the dashboard",
          "Low — Flask-Login or Flask-HTTPAuth"],
         ["Alert management UI",
          "Buttons to mark alerts as Reviewed/Closed. Status history tracking.",
          "Low — simple form + SQL UPDATE"],
         ["PDF / CSV report export",
          "Download all detected alerts as PDF or Excel report",
          "Low — ReportLab or pandas to_csv()"],
         ["Multi-interface monitoring",
          "Monitor multiple network adapters simultaneously with separate threads",
          "Medium — thread pool per interface"],
         ["Automatic model retraining",
          "Scheduled job to retrain model on new data collected from real traffic",
          "High — requires labeled real traffic data"],
         ["Anomaly detection",
          "Unsupervised model (Isolation Forest / Autoencoder) to detect unknown attacks",
          "High — different model architecture needed"]],
        [4.5*cm, 8.5*cm, 3*cm]
    ))
    story.append(PageBreak())


# ─────────────────────────────────────────────────────────
# CHAPTER 33 — INSTALLATION
# ─────────────────────────────────────────────────────────
def ch33(story):
    story += chapter_header("33", "Complete Installation Guide",
                            "Setting up AI-NIDS from scratch")

    story.append(H2("33.1 Prerequisites"))
    story += bullets([
        "Python 3.10 or higher (https://python.org/downloads)",
        "Git (https://git-scm.com/downloads)",
        "Npcap (https://npcap.com) — install with 'WinPcap API-compatible mode' checked",
        "Windows 10/11 (or Linux/macOS with root access)",
    ])

    story.append(H2("33.2 Installation Commands"))
    story.append(Code(
        "# 1. Clone the GitHub repository\n"
        "git clone https://github.com/vrajkiran/AI-NIDS.git\n"
        "cd AI-NIDS\n"
        "\n"
        "# 2. Create virtual environment\n"
        "python -m venv .venv\n"
        "\n"
        "# 3. Activate virtual environment (Windows)\n"
        ".venv\\Scripts\\activate\n"
        "\n"
        "# 4. Install all dependencies\n"
        "pip install -r requirements.txt\n"
        "\n"
        "# requirements.txt contains:\n"
        "# Flask, scapy, pandas, numpy, scikit-learn, joblib, pyarrow\n"
        "\n"
        "# 5. (Pre-trained model already in ml/model/ — skip training if model files exist)\n"
        "# To retrain: python ml/train.py\n"
        "\n"
        "# 6. Launch the application\n"
        "python run.py\n"
        "# OR double-click: run_ai_nids.bat"
    ))

    story.append(H2("33.3 Verify Installation"))
    story.append(Code(
        "# Run unit tests to confirm everything works\n"
        ".venv\\Scripts\\python -m unittest discover tests\n"
        "\n"
        "# Expected output:\n"
        "# ....\n"
        "# Ran 4 tests in 0.021s\n"
        "# OK"
    ))
    story.append(PageBreak())


# ─────────────────────────────────────────────────────────
# CHAPTER 34 — HOW TO USE
# ─────────────────────────────────────────────────────────
def ch34(story):
    story += chapter_header("34", "How To Use the Application",
                            "Beginner-friendly step-by-step user guide")

    story.append(H2("34.1 Launching the Application"))
    story += bullets([
        "Double-click <b>run_ai_nids.bat</b> in the project folder.",
        "A terminal window opens showing the AI-NIDS banner.",
        "Your default browser opens automatically to http://127.0.0.1:5000.",
        "The dashboard loads with any existing records (or demo data).",
    ])

    story.append(H2("34.2 Dashboard Controls Summary"))
    story.append(simple_table(
        ["Button / Control", "What It Does"],
        [["▶ START MONITORING", "Begins live Scapy packet capture with ML classification"],
         ["■ STOP",            "Stops active monitoring (preserves existing records)"],
         ["⚡ DEMO DATA",      "Loads 10 sample traffic + 4 alert records for presentation"],
         ["🗑 CLEAR DEMO",     "Deletes ONLY demo records, REAL records are untouched"],
         ["Interface dropdown","Select your active network adapter (Wi-Fi, Ethernet, etc.)"],
         ["Duration input",   "Seconds to capture (5–3600). Default: 10 seconds"],
         ["LIVE TRAFFIC nav", "View all 100 most recent traffic flow records"],
         ["ALERTS nav",       "View all 100 most recent security alerts"],
         ["MODEL PERFORMANCE","View model accuracy, confusion matrix, classification report"]],
        [5*cm, 11*cm]
    ))

    story.append(H2("34.3 For Project Demonstration"))
    story += bullets([
        "Click ⚡ DEMO DATA to load realistic sample records instantly.",
        "The '⚡ DEMO MODE ACTIVE' badge appears in the header.",
        "Show KPI cards (Total Packets: 4029, Total Flows: 10, Detected Attacks: 4).",
        "Show the Doughnut chart (6 BENIGN : 4 ATTACK).",
        "Navigate to ALERTS page — show 4 alerts with HIGH/MEDIUM severity.",
        "Navigate to MODEL PERFORMANCE — show Accuracy 99.97%.",
        "Click 🗑 CLEAR DEMO to clean up after demonstration.",
    ])
    story.append(PageBreak())


# ─────────────────────────────────────────────────────────
# CHAPTER 35 — TROUBLESHOOTING
# ─────────────────────────────────────────────────────────
def ch35(story):
    story += chapter_header("35", "Troubleshooting",
                            "Common problems and their solutions")

    story.append(simple_table(
        ["Problem", "Likely Cause", "Solution"],
        [["Browser doesn't open or shows 'Unable to connect'",
          "Flask failed to start or port 5000 is busy",
          "Run: netstat -ano | findstr :5000. If found, taskkill /PID <pid> /F. Restart."],
         ["'WARNING: No libpcap provider' in terminal",
          "Npcap not installed or not configured for WinPcap compatibility",
          "Reinstall Npcap from npcap.com with 'WinPcap API-compatible mode' checked."],
         ["No packets captured after clicking START",
          "Wrong interface selected, no network activity, or permissions issue",
          "Try selecting a different interface. Generate traffic (open browser). Run as Administrator."],
         ["Dashboard shows 0 Flows / empty tables",
          "No REAL captures done and demo data was cleared",
          "Click ⚡ DEMO DATA to reload demo records, or start real monitoring."],
         ["Model page shows N/A for all metrics",
          "evaluation_results.txt missing — model not trained yet",
          "Run: python ml/train.py (requires CICIDS2017 data in data/ folder)"],
         ["'Missing required ML features' error in logs",
          "Flow features don't match the 10 trained feature names",
          "Ensure SELECTED_FEATURES in preprocess.py matches to_ml_features() keys in flow.py"],
         ["'A capture session is already running' message",
          "Clicked START while monitoring is still active",
          "Wait for current session to complete or click STOP first."],
         ["Git push fails with authentication error",
          "GitHub token expired or gh CLI not authenticated",
          "Run: gh auth login and re-authenticate."],
         ["Tests fail: ModuleNotFoundError",
          "Virtual environment not activated",
          "Run: .venv\\Scripts\\activate first, then run tests."],
         ["Charts are empty / not rendering",
          "Chart.js CDN not loading (offline) or JavaScript error",
          "Check browser console (F12) for errors. Ensure internet connection for CDN."]],
        [4*cm, 4*cm, 8*cm]
    ))
    story.append(PageBreak())


# ─────────────────────────────────────────────────────────
# CHAPTER 36 — DEVELOPMENT JOURNEY
# ─────────────────────────────────────────────────────────
def ch36(story):
    story += chapter_header("36", "Project Development Journey",
                            "How the project was built from idea to final product")

    phases = [
        ("Phase 1 — Planning & Architecture",
         "Defined the 5-component architecture: Scapy → Flow → ML → SQLite → Flask. "
         "Selected CICIDS2017 dataset for training. Selected Random Forest for its "
         "interpretability and strong performance on tabular flow data."),
        ("Phase 2 — Configuration Setup",
         "Created config.py with all file paths (BASE_DIR, MODEL_PATH, DATABASE_PATH, etc.), "
         "runtime constants (CAPTURE_DURATION=10, HIGH_CONFIDENCE_THRESHOLD=0.90), "
         "and server config (HOST='127.0.0.1', PORT=5000)."),
        ("Phase 3 — Dataset & Preprocessing (ml/preprocess.py)",
         "Defined SELECTED_FEATURES (10 live-calculable features), implemented "
         "load_csv_files() with Parquet support, clean_dataset() pipeline, "
         "convert_labels() (BENIGN→0, other→1), and custom MedianImputer class."),
        ("Phase 4 — Model Training (ml/train.py)",
         "Implemented train() function: 75/25 stratified split, "
         "RandomForestClassifier(n_estimators=100, class_weight='balanced'), "
         "evaluation with sklearn metrics, saving 3 Joblib files + evaluation_results.txt."),
        ("Phase 5 — Prediction Service (ml/predict.py)",
         "Implemented PredictionService: loads model on startup, validate_features() checks "
         "for missing/NaN/Inf values, arrange_features() preserves column order, "
         "predict() returns {prediction, confidence, severity}."),
        ("Phase 6 — Packet Capture Engine (network/features.py + flow.py + packet_capture.py)",
         "Built extract_packet_metadata() for safe header extraction, "
         "Flow class with bidirectional tracking and to_ml_features(), "
         "PacketCapture with Scapy sniff(), Layer-2/3 fallback, and stop_event threading."),
        ("Phase 7 — Database Layer (database/db.py)",
         "Designed SQLite schema for network_traffic and alerts tables, "
         "implemented get_connection(), create_database() with auto-migration, "
         "insert/fetch functions, dashboard summary query, and chart data queries."),
        ("Phase 8 — Flask Backend (app.py)",
         "Connected all components: Flask routes, threading with monitor_lock, "
         "save_detection() callback, read_model_metrics() with regex parsing, "
         "all API endpoints (/api/status, /api/summary, /api/live, /api/alerts, /api/charts)."),
        ("Phase 9 — Frontend & Dashboard (templates/ + static/)",
         "Built Jinja2 templates with base.html inheritance. Created CSS with "
         "Retro-Futuristic parchment/teal/rust palette. Implemented JavaScript polling, "
         "Chart.js initialization and update, live clock, and table rendering."),
        ("Phase 10 — Demo Mode & Data Separation",
         "Added data_source column with schema auto-migration, seed_demo_data() with "
         "10 realistic synthetic records, clear_demo_data() selective deletion, "
         "has_demo_data() check, /load-demo and /clear-demo routes, "
         "⚡ DEMO MODE ACTIVE badge with JavaScript toggle."),
        ("Phase 11 — Launcher & GitHub",
         "Created run_ai_nids.bat (Windows batch, auto .venv detection) and run.py "
         "(print_banner, create_database, browser_thread, app.run). "
         "Git initialized, .gitignore created (excluding .venv, nids.db, logs, installer). "
         "Pushed to https://github.com/vrajkiran/AI-NIDS."),
        ("Phase 12 — Testing & Documentation",
         "Wrapped unit tests in unittest.TestCase. Ran 4/4 tests passing. "
         "Created 6 documentation files in docs/. Generated this PDF guide."),
    ]

    for title, desc in phases:
        story.append(KeepTogether([H3(title), P(desc), SP(6)]))

    story.append(PageBreak())


# ─────────────────────────────────────────────────────────
# CHAPTER 37 — QUICK REVISION
# ─────────────────────────────────────────────────────────
def ch37(story):
    story += chapter_header("37", "Quick Revision",
                            "1-minute and 5-minute explanations + complete glossary")

    story.append(H2("37.1 One-Minute Explanation"))
    story.append(Callout(
        "AI-NIDS watches your computer's network, groups packets into conversations (flows), "
        "calculates 10 statistics per flow, feeds them to a Random Forest ML model trained on "
        "CICIDS2017 DDoS data, and classifies each flow as BENIGN or ATTACK with 99.97% accuracy. "
        "Results appear live on a Flask web dashboard at http://127.0.0.1:5000."
    ))

    story.append(H2("37.2 Five-Minute Explanation"))
    story.append(P(
        "<b>The Problem</b>: Networks are constantly being attacked. Traditional tools use fixed rules "
        "that miss new attacks. Humans can't inspect millions of packets."
    ))
    story.append(P(
        "<b>The Solution</b>: AI-NIDS uses machine learning. We trained a Random Forest model on "
        "225,745 labeled network flows from the CICIDS2017 dataset (BENIGN and DDoS attacks). "
        "The model learned patterns: attacks have very high packet rates, unusual byte volumes, "
        "and specific port/protocol signatures."
    ))
    story.append(P(
        "<b>Live Operation</b>: Scapy captures packet headers (never payload) from authorized "
        "network adapters. Packets are grouped into bidirectional 5-tuple flows. "
        "10 statistical features are computed per flow. The trained model predicts BENIGN or ATTACK "
        "with a confidence score in milliseconds."
    ))
    story.append(P(
        "<b>Storage</b>: Every flow and every alert is stored in SQLite with a data_source tag "
        "('REAL' for live captures, 'DEMO' for presentation data). The database is never exposed "
        "to the internet."
    ))
    story.append(P(
        "<b>Dashboard</b>: A Flask web server exposes REST API endpoints. JavaScript polls these "
        "every 3 seconds and updates Chart.js visualizations and HTML tables without page reloads. "
        "The Model Performance page shows the actual accuracy (99.97%) from the evaluation file."
    ))

    story.append(H2("37.3 Complete Technical Flow Diagram"))
    story.append(Mono(
        "run_ai_nids.bat\n"
        "      ↓\n"
        "Python run.py → create_database() → Flask on 127.0.0.1:5000\n"
        "      ↓\n"
        "Browser opens dashboard\n"
        "      ↓\n"
        "User: select interface + duration → POST /start-monitoring\n"
        "      ↓\n"
        "PacketCapture thread starts → load_predictor() → PredictionService()\n"
        "      ↓\n"
        "Scapy sniff() ← packet\n"
        "      ↓\n"
        "extract_packet_metadata() → {src_ip, dst_ip, ports, proto, length, time}\n"
        "      ↓\n"
        "_update_flow() → Flow.add_packet() → update fwd/bwd counters\n"
        "      ↓\n"
        "flow.to_ml_features() → 10-key feature dictionary\n"
        "      ↓\n"
        "PredictionService.predict() → arrange → impute → model.predict()\n"
        "      ↓\n"
        "{'prediction': 'BENIGN'/'ATTACK', 'confidence': 0.xx, 'severity': 'HIGH'/'MEDIUM'}\n"
        "      ↓\n"
        "save_detection() → insert_network_traffic(REAL)\n"
        "                 → if ATTACK: insert_alert(REAL, status=OPEN)\n"
        "      ↓\n"
        "JS polls /api/* every 3s → refreshSummary() → refreshCharts() → refreshLiveTable()\n"
        "      ↓\n"
        "Dashboard: KPI cards updated, charts redrawn, table rows added"
    ))

    story.append(H2("37.4 Glossary of Key Terms"))
    story.append(simple_table(
        ["Term", "Definition"],
        [["Packet",          "A small chunk of data sent over a network, containing header + payload"],
         ["Flow",            "A group of packets belonging to the same bidirectional network conversation"],
         ["5-tuple",         "The 5 fields that uniquely identify a flow: srcIP, dstIP, srcPort, dstPort, protocol"],
         ["IP Address",      "Numeric label (e.g., 192.168.1.105) identifying a device on a network"],
         ["Port",            "A numbered channel on a device for a specific service (443=HTTPS, 22=SSH)"],
         ["Protocol",        "Communication rules: TCP=6, UDP=17, ICMP=1"],
         ["Scapy",           "Python library for passive packet capture (sniffing) from network adapters"],
         ["Npcap",           "Windows kernel driver enabling Scapy to capture raw network packets"],
         ["Feature",         "A numeric input variable for the ML model (e.g., Flow Bytes/s)"],
         ["CICIDS2017",      "Canadian ICS benchmark dataset with labeled BENIGN and attack network flows"],
         ["Random Forest",   "Ensemble ML algorithm of 100 decision trees. Final prediction by majority vote"],
         ["Joblib",          "Python library for saving/loading large ML model objects efficiently"],
         ["MedianImputer",   "Custom class that fills missing values with the median of training data"],
         ["predict_proba()", "sklearn method returning probability for each class (confidence score)"],
         ["Confidence",      "Probability (0.0–1.0) that the prediction is correct"],
         ["SQLite",          "Serverless file-based relational database (nids.db)"],
         ["data_source",     "SQLite column: 'REAL' = live captured flow, 'DEMO' = synthetic demo record"],
         ["Flask",           "Python web framework mapping URLs to Python functions"],
         ["Jinja2",          "HTML templating engine for Flask (used in templates/*.html)"],
         ["REST API",        "HTTP interface that returns JSON data (/api/summary, /api/live, etc.)"],
         ["Chart.js",        "JavaScript library for interactive Doughnut, Line, and Bar charts"],
         ["Polling",         "JavaScript repeatedly calling /api/* every 3 seconds for fresh data"],
         ["Demo Mode",       "Presentation mode using synthetic data_source='DEMO' records"],
         ["BENIGN",          "ML classification: normal, expected network traffic"],
         ["ATTACK",          "ML classification: traffic matching learned DDoS/attack patterns"],
         ["Severity HIGH",   "ATTACK prediction with confidence >= 0.90 (90%)"],
         ["Severity MEDIUM", "ATTACK prediction with confidence < 0.90 (90%)"],
         ["True Positive",   "Real attack correctly classified as ATTACK"],
         ["False Positive",  "Normal traffic incorrectly classified as ATTACK (false alarm)"],
         ["False Negative",  "Real attack incorrectly classified as BENIGN (missed detection)"],
         ["F1-Score",        "Harmonic mean of Precision and Recall. Balance metric for classification"],
         ["Stratified split","Train/test split that preserves the class ratio from the original dataset"]],
        [4.5*cm, 11.5*cm]
    ))
    story.append(PageBreak())


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN PDF BUILDER
# ═══════════════════════════════════════════════════════════════════════════════

def build_pdf():
    story = []

    # Cover
    build_cover(story)

    # TOC (placeholder — rebuilt after first pass)
    build_toc(story)

    # All chapters
    ch1(story)
    ch2(story)
    ch3(story)
    ch4(story)
    ch5(story)
    ch6(story)
    ch7(story)
    ch8(story)
    ch9(story)
    ch10(story)
    ch11(story)
    ch12(story)
    ch13(story)
    ch14(story)
    ch15(story)
    ch16(story)
    ch17(story)
    ch18(story)
    ch19(story)
    ch20(story)
    ch21(story)
    ch22(story)
    ch23(story)
    ch24(story)
    ch25(story)
    ch26(story)
    ch27(story)
    ch28(story)
    ch29(story)
    ch30(story)
    ch31(story)
    ch32(story)
    ch33(story)
    ch34(story)
    ch35(story)
    ch36(story)
    ch37(story)

    # Build document
    doc = AIDoc(
        str(OUTPUT_PDF),
        title="AI-NIDS Complete Project Learning & Technical Guide",
        author="AI-NIDS MCA Project",
        subject="Network Intrusion Detection System using Machine Learning",
    )
    doc.multiBuild(story)
    safe_path = str(OUTPUT_PDF).encode('ascii', 'replace').decode('ascii')
    print("\nPDF successfully generated!")
    print("Path: " + safe_path)
    print("File size: %.1f KB" % (OUTPUT_PDF.stat().st_size / 1024))
    print("Done.")


if __name__ == "__main__":
    build_pdf()
