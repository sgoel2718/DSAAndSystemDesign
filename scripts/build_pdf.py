import datetime as dt
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table,
                                TableStyle, PageBreak, KeepTogether, CondPageBreak)
from plan_data import DAYS, WEEKS, PROJECT, EXTRAS, RESOURCES, DAILY_SCHEDULE, START

INK = colors.HexColor("#1d2433"); MUTED = colors.HexColor("#5b6478")
ACC = colors.HexColor("#b4441f"); JAVA = colors.HexColor("#1f5f8b")
NOTE = colors.HexColor("#fff3b0"); LINE = colors.HexColor("#d9dce3"); PANEL = colors.HexColor("#f3f5f9")
DIFF = {"Easy": "#2e7d4f", "Medium": "#b07a00", "Hard": "#b4441f"}

def S(name, **kw):
    base = dict(fontName="Helvetica", fontSize=9.5, leading=13.5, textColor=INK)
    base.update(kw); return ParagraphStyle(name, **base)
H0 = S("h0", fontName="Helvetica-Bold", fontSize=30, leading=35)
H1 = S("h1", fontName="Helvetica-Bold", fontSize=17, leading=22, spaceAfter=6)
H2 = S("h2", fontName="Helvetica-Bold", fontSize=13, leading=17, spaceBefore=4, spaceAfter=3)
LAB = S("lab", fontName="Helvetica-Bold", fontSize=7.5, leading=10, textColor=ACC)
BODY = S("body"); SMALL = S("small", fontSize=8.5, leading=11.5, textColor=MUTED)
BUL = S("bul", leftIndent=10, bulletIndent=0)
MONO = S("mono", fontName="Courier", fontSize=8.5, leading=11.5)

start = dt.date.fromisoformat(START)
def date_of(d): return (start + dt.timedelta(days=d - 1)).strftime("%a %d %b")

def on_page(c, doc):
    c.saveState(); c.setFont("Helvetica", 7.5); c.setFillColor(MUTED)
    c.drawString(18*mm, 10*mm, "30-Day DSA to System Design in Java  |  Shubham")
    c.drawRightString(A4[0]-18*mm, 10*mm, f"Page {doc.page}")
    c.setStrokeColor(LINE); c.line(18*mm, 14*mm, A4[0]-18*mm, 14*mm); c.restoreState()

doc = BaseDocTemplate("DSA_30_Day_Java_Plan.pdf", pagesize=A4, leftMargin=18*mm, rightMargin=18*mm,
                      topMargin=16*mm, bottomMargin=20*mm, title="30-Day DSA to System Design Plan (Java)",
                      author="Claude for Shubham")
frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="f")
doc.addPageTemplates([PageTemplate(id="p", frames=[frame], onPage=on_page)])
W = doc.width
st = []

def bullets(items, style=BUL):
    return [Paragraph(i, style, bulletText="•") for i in items]

def panel(flows, bg=PANEL, pad=7):
    t = Table([[flows]], colWidths=[W])
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),bg),("LEFTPADDING",(0,0),(-1,-1),pad),
        ("RIGHTPADDING",(0,0),(-1,-1),pad),("TOPPADDING",(0,0),(-1,-1),pad),("BOTTOMPADDING",(0,0),(-1,-1),pad)]))
    return t

# ---- cover ----
st += [Spacer(1, 30*mm), Paragraph("JAVA EDITION  ·  30 DAYS  ·  2-5 HRS/DAY", LAB), Spacer(1, 4),
       Paragraph("Data Structures to<br/>System Design", H0), Spacer(1, 8),
       Paragraph("A day-by-day plan to crack Google, Microsoft and Amazon interviews, "
                 "with a live Java demo every day and a resume-grade distributed systems project.", S("x", fontSize=12, leading=17, textColor=MUTED)),
       Spacer(1, 14)]
nprob = sum(len(d["problems"]) for d in DAYS)
stats = Table([[Paragraph(f"<b><font size=20>{a}</font></b><br/><font color='#5b6478'>{b}</font>", BODY) for a, b in
                [("30","days"),(str(nprob),"LeetCode problems"),("30","live Java demos"),("20","coding patterns")]]], colWidths=[W/4]*4)
stats.setStyle(TableStyle([("LINEABOVE",(0,0),(-1,0),1.2,ACC),("TOPPADDING",(0,0),(-1,-1),8)]))
st += [stats, Spacer(1, 16),
       Paragraph(f"Prepared for <b>Shubham</b>  ·  Day 1: {date_of(1)} {start.year}  ·  Day 30: {date_of(30)}", BODY),
       Paragraph("Version 2  ·  updated 01 Nov 2026 (added matrices, cyclic sort, math & number theory, randomised algorithms, "
                 "core Java/JVM, API design & security, distributed transactions, 20-pattern table, Java cheat sheet, interview loops)", SMALL),
       Spacer(1, 22)]
st.append(panel([Paragraph("FLAGSHIP PROJECT", LAB),
                 Paragraph(f"<b>{PROJECT['name']}</b>: {PROJECT['tagline']}", S("p", fontSize=11, leading=15)),
                 Spacer(1,3), Paragraph(PROJECT["why"], SMALL)]))
st.append(PageBreak())

# ---- how to use ----
st.append(Paragraph("How this plan works", H1))
st += bullets(["Every day has: <b>concepts</b> to learn, a <b>live Java demo</b> you type and run, <b>LeetCode problems</b> "
               "(easy to hard, linked), a <b>NexusKV project task</b> on build days, and <b>sticky notes</b> to revise.",
               "Each topic is taught one at a time in chat: tell me <i>'Start Day N'</i> and I teach it in depth with full Java code, "
               "dry runs and interview tips, then update the sticky-notes board.",
               "On short (2-hour) days, do the concepts, demo and the first 3 problems. Catch up the rest on weekends.",
               "Rule of 25: if stuck on a problem for 25 minutes, read the hint/solution, then re-solve it from scratch 2 days later.",
               "Everything is in Java 21 (records, var, switch expressions, streams where it helps; plain loops in interview code)."])
st.append(Spacer(1, 8))
rows = [[Paragraph(f"<b>{n}</b>", BODY), [Paragraph(x, BUL, bulletText="•") for x in items]] for n, items in DAILY_SCHEDULE]
t = Table(rows, colWidths=[30*mm, W-30*mm])
t.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"),("LINEBELOW",(0,0),(-1,-1),0.5,LINE),("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6)]))
st += [Paragraph("Daily time split", H2), t, Spacer(1, 10)]

st.append(Paragraph("The 30 days at a glance", H2))
rows = [[Paragraph("<b>Day</b>", SMALL), Paragraph("<b>Date</b>", SMALL), Paragraph("<b>Topic</b>", SMALL), Paragraph("<b>Build</b>", SMALL)]]
for d in DAYS:
    rows.append([Paragraph(str(d["day"]), BODY), Paragraph(date_of(d["day"]), SMALL), Paragraph(d["title"], S("t", fontSize=8.8, leading=11.5)),
                 Paragraph("<font name='ZapfDingbats'>l</font>" if d["project"] else "", S("c", textColor=ACC))])
t = Table(rows, colWidths=[11*mm, 22*mm, W-45*mm, 12*mm], repeatRows=1)
ts = [("LINEBELOW",(0,0),(-1,-1),0.4,LINE),("VALIGN",(0,0),(-1,-1),"MIDDLE"),("TOPPADDING",(0,0),(-1,-1),2.5),("BOTTOMPADDING",(0,0),(-1,-1),2.5)]
for i, d in enumerate(DAYS, 1):
    if d["day"] in (7, 14, 21): ts.append(("LINEBELOW",(0,i),(-1,i),1,MUTED))
t.setStyle(TableStyle(ts)); st += [t, PageBreak()]

# ---- days ----
for w in WEEKS:
    st += [Paragraph(f"WEEK {w['n']}", LAB), Paragraph(w["name"], H1), Paragraph(w["goal"], SMALL), Spacer(1, 6)]
    for d in [x for x in DAYS if x["week"] == w["n"]]:
        block = [CondPageBreak(60*mm),
                 Paragraph(f"DAY {d['day']}  ·  {date_of(d['day']).upper()}", LAB),
                 Paragraph(d["title"], H2), Paragraph("<b>Concepts</b>", S("b", fontSize=8.5, textColor=MUTED))]
        block += bullets(d["concepts"])
        if d.get("approach"):
            block += [Spacer(1, 3), Paragraph("<b>How to approach questions</b>", S("ap", fontSize=8.5, textColor=MUTED))]
            block += [Paragraph(f"{k}. {a}", S("apl", leftIndent=10)) for k, a in enumerate(d["approach"], 1)]
        block += [Spacer(1, 4), panel([Paragraph("LIVE JAVA DEMO", S("l", fontName="Helvetica-Bold", fontSize=7.5, textColor=JAVA)),
                                       Paragraph(d["demo"], BODY)], bg=colors.HexColor("#eaf2f8"), pad=6)]
        if d["problems"]:
            prow = []
            for i, (name, slug, diff) in enumerate(d["problems"], 1):
                prow.append([Paragraph("<font name='ZapfDingbats' size='8' color='#5b6478'>o</font>", BODY),
                             Paragraph(f'<link href="https://leetcode.com/problems/{slug}/" color="#1f5f8b">{name}</link>', BODY),
                             Paragraph(f"<font color='{DIFF[diff]}'><b>{diff}</b></font>", SMALL)])
            pt = Table(prow, colWidths=[6*mm, W-26*mm, 20*mm])
            pt.setStyle(TableStyle([("TOPPADDING",(0,0),(-1,-1),1.5),("BOTTOMPADDING",(0,0),(-1,-1),1.5),("LEFTPADDING",(0,0),(-1,-1),0)]))
            block += [Spacer(1, 4), Paragraph("<b>Problems</b>", S("b2", fontSize=8.5, textColor=MUTED)), pt]
        if d["project"]:
            block += [Spacer(1, 3), Paragraph(f"<font color='#b4441f'><b>NexusKV build:</b></font> {d['project']}", BODY)]
        notes = "<br/>".join("• " + n for n in d["notes"])
        block += [Spacer(1, 4), panel([Paragraph("STICKY NOTES", S("sn", fontName="Helvetica-Bold", fontSize=7.5, textColor=colors.HexColor("#7a5c00"))),
                                       Paragraph(notes, S("n", fontSize=9, leading=12.5))], bg=NOTE, pad=6), Spacer(1, 12)]
        st += block
    st.append(PageBreak())

# ---- project ----
P = PROJECT
st += [Paragraph("FLAGSHIP PROJECT", LAB), Paragraph(f"{P['name']}: {P['tagline']}", H1), Paragraph(P["why"], BODY), Spacer(1, 8),
       Paragraph("Architecture", H2),
       Paragraph("Client CLI → NIO TCP server → Router (consistent-hash ring) → Leader node → [WAL → Skip-list memtable → "
                 "SSTables + Bloom filters → Compaction]  →  replicated to Follower nodes (heartbeats + leader election). "
                 "Spring Boot admin dashboard reads node health and metrics.", MONO), Spacer(1, 6),
       Paragraph("Features", H2)]
t = Table([[Paragraph(f"<b>{a}</b>", BODY), Paragraph(b, BODY)] for a, b in P["features"]], colWidths=[34*mm, W-34*mm])
t.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"),("LINEBELOW",(0,0),(-1,-1),0.4,LINE),("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4)]))
st += [t, Spacer(1, 6), Paragraph("Tech stack", H2), Paragraph("  ·  ".join(P["stack"]), BODY), Spacer(1, 6),
       Paragraph("Build timeline", H2)]
st += bullets([f"<b>Day {d['day']}:</b> {d['project'].replace('NexusKV: ','')}" for d in DAYS if d["project"]])
st += [Spacer(1, 6), Paragraph("Resume bullets (fill in your benchmark numbers)", H2)]
st += bullets(P["resume"])
st += [Spacer(1, 6), Paragraph(f"<i>{P['alt']}</i>", SMALL), PageBreak()]

# ---- extras & resources ----
st.append(Paragraph("Extra topics included (beyond pure DSA)", H1))
t = Table([[Paragraph(f"<b>{a}</b>", BODY), Paragraph(b, BODY)] for a, b in EXTRAS], colWidths=[42*mm, W-42*mm])
t.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"),("LINEBELOW",(0,0),(-1,-1),0.4,LINE),("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4)]))
st += [t, Spacer(1, 10), Paragraph("Interview day framework", H2)]
st += bullets(["<b>DSA:</b> clarify → examples → brute force → optimise → code → dry run → complexity",
               "<b>LLD:</b> requirements → entities → relationships → class diagram → code core classes → patterns & extensibility",
               "<b>HLD:</b> requirements → estimates → API → data model → high-level diagram → deep dives → bottlenecks & trade-offs",
               "<b>Behavioural:</b> STAR, with a number in every Result"])
st += [Spacer(1, 10), Paragraph("Resources", H2)]
st += bullets([f'<link href="{u}" color="#1f5f8b"><b>{n}</b></link>: {why}' for n, u, why in RESOURCES])
st += [Spacer(1, 10), Paragraph("After Day 30", H2)]
st += bullets(["Keep 2 problems/day (one new, one re-solve) until your interviews.",
               "One HLD case study per week from the list on Day 27.",
               "Weekly LeetCode contest every Sunday morning."])

from plan_data import PATTERNS, JAVA_CHEATSHEET, REVISION, COMPANIES, SD_FRAMEWORK, SD_BLOCKS, SD_CASES, SD_LLD, SD_NUMBERS
def grid(rows, widths, head=None):
    data = ([[Paragraph(f"<b>{h}</b>", SMALL) for h in head]] if head else []) + rows
    t = Table(data, colWidths=widths, repeatRows=1 if head else 0)
    t.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"),("LINEBELOW",(0,0),(-1,-1),0.4,LINE),("TOPPADDING",(0,0),(-1,-1),3.5),("BOTTOMPADDING",(0,0),(-1,-1),3.5)]))
    return t
st.append(PageBreak())
st += [Paragraph("SYSTEM DESIGN HANDBOOK", LAB), Paragraph("System design at a glance (Days 22-28)", H1),
       Paragraph("Everything system design in one place: the answer framework, the building blocks, the case studies and low-level design. "
                 "Each row names the day it is taught.", SMALL), Spacer(1, 6), Paragraph("The 7-step answer framework", H2),
       grid([[Paragraph(f"<b>{a}</b>", BODY), Paragraph(b, BODY)] for a, b in SD_FRAMEWORK], [42*mm, W-42*mm]), Spacer(1, 8),
       Paragraph("High-level design building blocks", H2),
       grid([[Paragraph(f"<b>{t}</b><br/><font color='#5b6478'>{w}</font>", BODY), Paragraph(k, BODY), Paragraph(f"Day {d}", SMALL)] for t, w, k, d in SD_BLOCKS],
            [48*mm, W-64*mm, 16*mm], head=["Block", "Key points", "Day"]),
       Spacer(1, 8), Paragraph("Case studies to practise", H2),
       grid([[Paragraph(f"<b>{t}</b>", BODY), Paragraph(k, BODY), Paragraph(f"Day {d}", SMALL)] for t, k, d in SD_CASES],
            [48*mm, W-64*mm, 16*mm], head=["Design", "Key idea", "Day"]),
       Spacer(1, 8), Paragraph("Low-level design", H2),
       grid([[Paragraph(f"<b>{t}</b>", BODY), Paragraph(k, BODY), Paragraph(f"Day {d}", SMALL)] for t, k, d in SD_LLD], [48*mm, W-64*mm, 16*mm]),
       Spacer(1, 8), CondPageBreak(60*mm), Paragraph("Numbers to know for estimates", H2),
       grid([[Paragraph(a, BODY), Paragraph(b, MONO)] for a, b in SD_NUMBERS], [W*0.6, W*0.4])]
st.append(PageBreak())
st += [Paragraph("APPENDIX A", LAB), Paragraph("20 coding patterns: spot the pattern in 2 minutes", H1)]
rows = [[Paragraph("<b>Pattern</b>", SMALL), Paragraph("<b>Signal in the question</b>", SMALL), Paragraph("<b>Classic problem</b>", SMALL)]]
rows += [[Paragraph(f"<b>{a}</b>", BODY), Paragraph(b, BODY), Paragraph(c, SMALL)] for a, b, c in PATTERNS]
t = Table(rows, colWidths=[42*mm, W-92*mm, 50*mm], repeatRows=1)
t.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"),("LINEBELOW",(0,0),(-1,-1),0.4,LINE),("TOPPADDING",(0,0),(-1,-1),3.5),("BOTTOMPADDING",(0,0),(-1,-1),3.5)]))
st += [t, Spacer(1, 14), Paragraph("APPENDIX B", LAB), Paragraph("What the interview loops look like (typical, varies by team and level)", H1)]
t = Table([[Paragraph(f"<b>{a}</b>", BODY), Paragraph(b, BODY)] for a, b in COMPANIES], colWidths=[28*mm, W-28*mm])
t.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"),("LINEBELOW",(0,0),(-1,-1),0.4,LINE),("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5)]))
st.append(t)
from plan_data import PLAYBOOK
st += [PageBreak(), Paragraph("PATTERN PLAYBOOK", LAB), Paragraph("How to approach each pattern, with a Java template", H1)]
for k, (n, sig, ex) in enumerate(PATTERNS, 1):
    P = PLAYBOOK[n]
    code_html = P["template"].replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace(" ", "&nbsp;").replace("\n","<br/>")
    st.append(CondPageBreak(70*mm))
    st += [Paragraph(f"{k}. {n}", H2), Paragraph(f"<b>Use when:</b> {sig}", BODY), Spacer(1, 2)]
    st += [Paragraph(f"{j}. {x}", S("ps", leftIndent=10)) for j, x in enumerate(P["steps"], 1)]
    st += [Spacer(1, 3), panel([Paragraph(code_html, MONO)], pad=6), Spacer(1, 3),
           Paragraph(f"<b>Common mistakes:</b> {P['pitfalls']}", BODY),
           Paragraph(f"<b>Complexity:</b> {P['complexity']}", BODY), Spacer(1, 4),
           Paragraph("<b>Questions solved with this pattern</b> (click to open on LeetCode):", BODY)]
    from plan_data import PATTERN_Q
    qrows = []
    for q in PATTERN_Q[n]:
        tag = f"Day {q['day']}" if q["day"] else "Extra"
        qrows.append([Paragraph(f'<link href="https://leetcode.com/problems/{q["slug"]}/" color="#1f5f8b">{q["name"]}</link>', BODY),
                      Paragraph(tag, SMALL), Paragraph(f"<font color='{DIFF[q['diff']]}'><b>{q['diff']}</b></font>", SMALL)])
    qt = Table(qrows, colWidths=[W - 40*mm, 18*mm, 22*mm])
    qt.setStyle(TableStyle([("LINEBELOW",(0,0),(-1,-1),0.3,LINE),("TOPPADDING",(0,0),(-1,-1),2),
                            ("BOTTOMPADDING",(0,0),(-1,-1),2),("LEFTPADDING",(0,0),(-1,-1),2)]))
    st += [qt, Spacer(1, 12)]
st += [PageBreak(), Paragraph("APPENDIX C", LAB), Paragraph("Java DSA syntax cheat sheet", H1)]
for name, code in JAVA_CHEATSHEET:
    code_html = code.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace("\n","<br/>")
    st.append(KeepTogether([Paragraph(name, S("cn", fontName="Helvetica-Bold", fontSize=9.5, spaceBefore=4)),
                            panel([Paragraph(code_html, MONO)], pad=6), Spacer(1, 4)]))
st += [Spacer(1, 8), Paragraph("APPENDIX D", LAB), Paragraph("Revision system", H1)]
st += bullets(REVISION)

doc.build(st)
print("ok")
