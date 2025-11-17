from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, HRFlowable, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

def generar_pdf_liquidacion(df_display, saldo_deudor, interes_moratorio, monto_actualizado,
                            num_liquidacion, fecha_liquidacion, razon_social, ruc_obligado,
                            expediente_eem, resolucion_subintendencia, fec_notif_rsi, fecha_consentimiento):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=inch, rightMargin=inch, topMargin=inch, bottomMargin=inch)
    story = []

    # ============================================================
    #   ESTILOS
    # ============================================================

    styles = getSampleStyleSheet()

    titulo_style = ParagraphStyle(
        'Title',
        parent=styles['Title'],
        fontSize=16,
        leading=20,
        alignment=1,  # Centrado
    )

    section_title_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Normal'],
        fontSize=11.5,
        leading=13,
        spaceAfter=4,
    )

    left_style = ParagraphStyle(
        'LeftColumn',
        parent=styles['Normal'],
        fontSize=9,     # Solo lado izquierdo
        leading=13,
        spaceAfter=4
    )

    right_style = ParagraphStyle(
        'RightColumn',
        parent=styles['Normal'],
        fontSize=9,     # Solo lado derecho
        leading=11,
    )


    # ============================================================
    #   ENCABEZADO PRINCIPAL
    # ============================================================

    story.append(Paragraph("<b>Liquidación de Deuda</b>", titulo_style))
    story.append(Spacer(1, 0.12 * inch))

    # ============================================================
    #   FUNCIÓN PARA CREAR TABLAS CON TÍTULO + LÍNEA SEPARADORA
    # ============================================================

    def create_titled_info_table(title, data):
        elements = []

        # Título de sección
        elements.append(Paragraph(f"<b>{title}</b>", section_title_style))
        elements.append(Spacer(1, 0.05 * inch))

        # Tabla
        table = Table(data, colWidths=[2.0 * inch, 4.5 * inch])
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('LEFTPADDING', (1, 0), (1, -1), 60), # Sangría del valor
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        elements.append(table)

        # Separador
        elements.append(Spacer(1, 0.12 * inch))
        elements.append(HRFlowable(width="100%", thickness=0.7, color=colors.black, spaceBefore=4, spaceAfter=4))
        elements.append(Spacer(1, 0.12 * inch))

        return elements

    # ============================================================
    #   SECCIÓN: N° LIQUIDACIÓN Y FECHA
    # ============================================================

    seccion1_data = [
        ['N° de Liquidación', Paragraph(f": {num_liquidacion}", right_style)],
        ['Fecha de Liquidación', Paragraph(f": {fecha_liquidacion.strftime('%d/%m/%Y')}", right_style)]
    ]
    story.extend(create_titled_info_table("", seccion1_data))

    # ============================================================
    #   SECCIÓN: DATOS DEL OBLIGADO
    # ============================================================

    obligado_data = [
        ['Razón Social', Paragraph(f": {razon_social}", right_style)],
        ['DNI/RUC', Paragraph(f": {ruc_obligado}", right_style)]
    ]
    story.extend(create_titled_info_table("Datos del Obligado:", obligado_data))

    # ============================================================
    #   SECCIÓN: DATOS DEL EXPEDIENTE
    # ============================================================

    expediente_data = [
        ['Expediente Sancionador', Paragraph(f": {expediente_eem}", right_style)],
        ['Resolución de Subintendencia', Paragraph(f": {resolucion_subintendencia}", right_style)],
        ['Fecha Notificación de RSI', Paragraph(f": {fec_notif_rsi}", right_style)],
        ['Fecha Consentimiento', Paragraph(f": {fecha_consentimiento}", right_style)],
    ]
    story.extend(create_titled_info_table("Datos del Expediente de Ejecución de Multa:", expediente_data))
    story.append(Spacer(1, 0.2 * inch))

    # ============================================================
    #   SECCIÓN: DETALLE DEL SALDO ACTUALIZADO
    # ============================================================
    
    story.append(Paragraph("<b>Detalle del Saldo Actualizado:</b>", section_title_style))
    story.append(Spacer(1, 0.2 * inch))

    df_display['Fecha de actualización'] = fecha_liquidacion.strftime('%d/%m/%Y')
    df_pdf_table = df_display[['Fecha de actualización', 'Saldo Deudor', 'Dias transcurridos', 'Interes', 'Saldo Actualizado']].copy()
    df_pdf_table.columns = ['Fecha de actualización', 'Saldo deudor', 'N° de Días', 'Interes Moratorio', 'Saldo Actualizado']

    data = [df_pdf_table.columns.tolist()] + df_pdf_table.values.tolist()
    table = Table(data, hAlign='CENTER', vAlign='MIDDLE')
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.black),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey)
    ]))
    story.append(table)

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()