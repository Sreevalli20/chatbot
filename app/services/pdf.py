from io import BytesIO
from app.models import Invoice


class PDFService:
    def __init__(self):
        self.company_name = "InvoiceAI"
        self.company_address = "Business Address"
        self.payment_terms = "Payment due within 30 days"

    def generate_invoice_pdf(self, invoice: Invoice) -> BytesIO:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72,
                               topMargin=72, bottomMargin=18)

        elements = []
        styles = getSampleStyleSheet()

        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#635BFF'),
            spaceAfter=30
        )

        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#333333'),
            spaceAfter=12
        )

        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#555555')
        )

        # Header
        elements.append(Paragraph(self.company_name, title_style))
        elements.append(Spacer(1, 0.2 * inch))

        # Invoice details
        invoice_info = """
        <b>Invoice Number:</b> """ + invoice.invoice_number + """<br/>
        <b>Invoice Date:</b> """ + invoice.invoice_date.strftime('%B %d, %Y') + """<br/>
        <b>Due Date:</b> """ + invoice.due_date.strftime('%B %d, %Y')
        elements.append(Paragraph(invoice_info, normal_style))
        elements.append(Spacer(1, 0.3 * inch))

        # Customer details
        elements.append(Paragraph("Bill To", heading_style))
        customer_info = """
        <b>""" + invoice.customer.name + """</b><br/>
        """ + invoice.customer.email + """<br/>
        """
        if invoice.customer.phone:
            customer_info += invoice.customer.phone + "<br/>"
        if invoice.customer.address:
            customer_info += invoice.customer.address + "<br/>"

        elements.append(Paragraph(customer_info, normal_style))
        elements.append(Spacer(1, 0.3 * inch))

        # Items table
        table_data = [
            ['Description', 'Qty', 'Unit Price', 'Tax %', 'Amount']
        ]

        for item in invoice.items:
            table_data.append([
                item.service_name,
                str(item.quantity),
                "INR " + f"{item.unit_price:,.2f}",
                f"{item.tax_rate}%",
                "INR " + f"{item.amount:,.2f}"
            ])

        table = Table(table_data, colWidths=[3*inch, 0.8*inch, 1.2*inch, 0.8*inch, 1.2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#635BFF')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
        ]))

        elements.append(table)
        elements.append(Spacer(1, 0.3 * inch))

        # Totals
        totals_data = [
            ['Subtotal', "INR " + f"{invoice.subtotal:,.2f}"],
            ['Discount', "-INR " + f"{invoice.discount:,.2f}"],
            ['Tax', "INR " + f"{invoice.tax:,.2f}"],
            ['Total', "INR " + f"{invoice.total:,.2f}"]
        ]

        totals_table = Table(totals_data, colWidths=[4*inch, 2*inch])
        totals_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 3), (-1, 3), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 3), (-1, 3), 14),
            ('TEXTCOLOR', (0, 3), (-1, 3), colors.HexColor('#635BFF')),
            ('LINEABOVE', (0, 3), (-1, 3), 2, colors.HexColor('#635BFF')),
        ]))

        elements.append(totals_table)
        elements.append(Spacer(1, 0.3 * inch))

        # Notes
        if invoice.notes:
            elements.append(Paragraph("Notes", heading_style))
            elements.append(Paragraph(invoice.notes, normal_style))
            elements.append(Spacer(1, 0.2 * inch))

        # Payment terms
        elements.append(Paragraph("Payment Terms", heading_style))
        elements.append(Paragraph(self.payment_terms, normal_style))

        # Build PDF
        doc.build(elements)
        buffer.seek(0)

        return buffer
