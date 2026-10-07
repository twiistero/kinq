"""Canonical contract text and branded, printable PDFs. No recipient email in a PDF."""
import html
import io
import json
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas as pdfcanvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, KeepTogether, Table, TableStyle

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT if (ROOT / "content/contracts.json").exists() else Path("/srv/source")
CATALOGUE = json.loads((SOURCE / "content/contracts.json").read_text())
MODELS = {item["id"]: item for item in CATALOGUE["models"]}


def sections(draft):
    model = MODELS[draft["model"]]
    date = lambda value: "/".join(reversed(value.split("-"))) if value else "À préciser"
    fields = [CATALOGUE["common"][0], *model["fields"], *CATALOGUE["common"][1:]]
    return [
        ("Notre accord", model["intro"]),
        ("Les personnes et les rôles", f'{draft["nameA"].strip() or "________________________"} : {draft["roleA"].strip() or model["roles"][0]}.\n{draft["nameB"].strip() or "________________________"} : {draft["roleB"].strip() or model["roles"][1]}.'),
        ("La durée", f'Début : {date(draft["start"])}. Fin : {date(draft["end"])}.\n{draft["duration"].strip() or "Durée et renouvellement à convenir ensemble."}'),
        *[(field["title"], draft["fields"][field["id"]].strip()) for field in fields if draft["fields"].get(field["id"], "").strip()],
        ("Un accord qui reste libre", CATALOGUE["closing"]),
    ]


def render_pdf(draft, signatures=None, reference=""):
    font_dir = SOURCE / "assets/fonts"
    if "KinqBody" not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont("KinqBody", str(font_dir / "DMSans-Regular.ttf")))
        pdfmetrics.registerFont(TTFont("KinqTitle", str(font_dir / "BarlowCondensed-Bold.ttf")))
    ink = colors.HexColor("#171916")
    muted = colors.HexColor("#5f645a")
    body = ParagraphStyle("body", fontName="KinqBody", fontSize=10.5, leading=14.5, textColor=ink, spaceAfter=6, splitLongWords=True)
    heading = ParagraphStyle("heading", fontName="KinqTitle", fontSize=16, leading=18, textColor=ink, spaceAfter=2, keepWithNext=True)
    title = ParagraphStyle("title", fontName="KinqTitle", fontSize=32, leading=36, textColor=ink, spaceAfter=24)
    output = io.BytesIO()
    pdf = SimpleDocTemplate(output, pagesize=A4, leftMargin=48, rightMargin=48, topMargin=146, bottomMargin=65, title=MODELS[draft["model"]]["title"], author="Kinq")
    safe = lambda value: html.escape(str(value)).replace("\n", "<br/>")
    items = []
    if reference:
        items.append(Paragraph(f"Référence : {safe(reference)}", body))
    closing=[]
    content=sections(draft)
    for index, (label, text) in enumerate(content, 1):
        pair=[Paragraph(f"{index:02d} / {safe(label)}", heading), Paragraph(safe(text), body)]
        if index==len(content): closing=pair
        else: items.extend(pair)
    signed = []
    for index, suffix in enumerate(("A", "B")):
        name = draft[f"name{suffix}"].strip() or f"Personne {index+1}"
        signature = (signatures or [None, None])[index]
        if signature:
            date = datetime.fromisoformat(signature["signedAt"]).astimezone(ZoneInfo("Europe/Paris")).strftime("%d/%m/%Y à %H:%M:%S")
            text = f'{safe(name)}<br/><br/>Signé électroniquement par :<br/>{safe(signature["name"])}<br/>{date} (Europe/Paris)'
        else:
            text = f'{safe(name)}<br/>Date : __________________<br/>Signature : __________________'
        signed.append(Paragraph(text, body))
    table = Table([signed], colWidths=[(A4[0]-96)/2]*2)
    table.setStyle(TableStyle([("VALIGN", (0,0), (-1,-1), "TOP"), ("LEFTPADDING", (0,0), (-1,-1), 0), ("RIGHTPADDING", (0,0), (-1,-1), 18)]))
    items.append(KeepTogether([*closing,Spacer(1,8), Paragraph("SIGNATURES", heading),table]))

    def decorate(canvas, doc):
        canvas.setFillColor(ink)
        page_title = Paragraph(safe(MODELS[draft["model"]]["title"]),
            ParagraphStyle("pageTitle", fontName="KinqTitle", fontSize=32 if doc.page==1 else 20,
                           leading=35 if doc.page==1 else 24, textColor=ink))
        _, title_height = page_title.wrap(A4[0]-96-167,90)
        page_title.drawOn(canvas,48,A4[1]-46-title_height)
        top=A4[1]-46;brand_width=108;brand_x=A4[0]-48-brand_width;wordmark_x=brand_x+brand_width*.35
        canvas.setFont("KinqBody",7.5);canvas.setFillColor(muted)
        canvas.drawString(wordmark_x,top-6,"Powered by")
        canvas.drawImage(str(SOURCE/"assets/kinq-logo-print.png"),brand_x,top-13-brand_width*64/166,width=brand_width,height=brand_width*64/166,mask="auto")
        canvas.setFont("KinqTitle",brand_width*18/166);canvas.setFillColor(ink)
        canvas.drawString(wordmark_x,top-60,"Make it kinky.")
        canvas.setFont("KinqBody",7.5);canvas.setFillColor(muted)
        canvas.drawString(wordmark_x,top-71,"kinq-app.com")
        canvas.setStrokeColor(colors.HexColor("#d6d9d0"))
        canvas.line(48,A4[1]-126,A4[0]-48,A4[1]-126)
        canvas.line(48,44,A4[0]-48,44)
        canvas.setFont("KinqBody",8);canvas.drawString(48,28,"Accord personnel de jeu")

    class PageNumbers(pdfcanvas.Canvas):
        def __init__(self,*args,**kwargs):
            super().__init__(*args,**kwargs)
            self.saved=[]
        def showPage(self):
            self.saved.append(dict(self.__dict__))
            self._startPage()
        def save(self):
            total=len(self.saved)
            for state in self.saved:
                self.__dict__.update(state)
                self.setFont("KinqBody",8);self.setFillColor(muted)
                self.drawRightString(A4[0]-48,28,f"{self._pageNumber} / {total}")
                super().showPage()
            super().save()
    pdf.build(items,onFirstPage=decorate,onLaterPages=decorate,canvasmaker=PageNumbers)
    return output.getvalue()
