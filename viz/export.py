import io
from datetime import datetime
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib import colors


def conversation_to_pdf(messages: list) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )

    styles = getSampleStyleSheet()

    #Estilo personalizados
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Title'],
        fontSize=18,
        textColor=HexColor('#4A4AE8'),
        spaceAfter=6
    )
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=HexColor('#888888'),
        spaceAfter=20
    )
    user_label_style = ParagraphStyle(
        'UserLabel',
        parent=styles['Normal'],
        fontSize=9,
        textColor=HexColor('#4A4AE8'),
        fontName='Helvetica-Bold',
        spaceAfter=2
    )
    user_msg_style = ParagraphStyle(
        'UserMsg',
        parent=styles['Normal'],
        fontSize=11,
        textColor=HexColor('#1a1a2e'),
        backColor=HexColor('#f0f0ff'),
        borderPadding=(6, 8, 6, 8),
        spaceAfter=10
    )
    assistant_label_style = ParagraphStyle(
        'AssistantLabel',
        parent=styles['Normal'],
        fontSize=9,
        textColor=HexColor('#2e7d32'),
        fontName='Helvetica-Bold',
        spaceAfter=2
    )
    assistant_msg_style = ParagraphStyle(
        'AssistantMsg',
        parent=styles['Normal'],
        fontSize=11,
        textColor=HexColor('#1a1a2e'),
        spaceAfter=10
    )
    sql_style = ParagraphStyle(
        'SQL',
        parent=styles['Code'],
        fontSize=8,
        textColor=HexColor('#333333'),
        backColor=HexColor('#f5f5f5'),
        borderPadding=(4, 6, 4, 6),
        fontName='Courier',
        spaceAfter=10
    )

    elements = []

    #Cabecera
    elements.append(Paragraph("Agente de Cohortes de Pacientes", title_style))
    elements.append(Paragraph(
        f"Informe exportado el {datetime.now().strftime('%d/%m/%Y a las %H:%M')}",
        subtitle_style
    ))
    elements.append(HRFlowable(width="100%", thickness=1, color=HexColor('#4A4AE8')))
    elements.append(Spacer(1, 0.4*cm))

    #Mensajes
    for msg in messages:
        if msg["role"] == "user":
            elements.append(Paragraph("Usuario", user_label_style))
            elements.append(Paragraph(msg["content"], user_msg_style))

        elif msg["role"] == "assistant":
            elements.append(Paragraph("Agente", assistant_label_style))
            #Limpiamos markdown básico para PDF
            content = msg["content"]
            content = content.replace("**", "")
            content = content.replace("*", "")
            elements.append(Paragraph(content, assistant_msg_style))

            #Código SQL (en el caso de que exista)
            if msg.get("sql") and msg["sql"] != "CANNOT_ANSWER":
                elements.append(Paragraph("SQL ejecutado:", sql_style))
                sql_text = msg["sql"].replace("<", "&lt;").replace(">", "&gt;")
                elements.append(Paragraph(sql_text, sql_style))

            elements.append(HRFlowable(
                width="100%", thickness=0.5,
                color=HexColor('#dddddd')
            ))
            elements.append(Spacer(1, 0.3*cm))

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()