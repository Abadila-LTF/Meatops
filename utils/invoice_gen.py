from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from datetime import datetime
import os

def generate_invoice_pdf(invoice_data, items, filename=None):
    """Generate PDF invoice"""
    
    if not filename:
        filename = f"invoice_{invoice_data['invoice_number']}.pdf"
    
    # Ensure invoices directory exists
    os.makedirs("invoices", exist_ok=True)
    filepath = os.path.join("invoices", filename)
    
    # Create PDF document
    doc = SimpleDocTemplate(filepath, pagesize=A4)
    story = []
    
    # Get styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=1  # Center alignment
    )
    
    # Shop header
    story.append(Paragraph("🥩 MEAT SHOP POS", title_style))
    story.append(Paragraph("Fresh Quality Meats", styles['Normal']))
    story.append(Paragraph("123 Main Street, City, State 12345", styles['Normal']))
    story.append(Paragraph("Phone: (555) 123-4567", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Invoice details
    invoice_info = [
        ["Invoice Number:", invoice_data['invoice_number']],
        ["Date:", datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
        ["Customer:", invoice_data.get('customer_name', 'Walk-in Customer')],
        ["Phone:", invoice_data.get('customer_phone', 'N/A')],
        ["Payment Method:", invoice_data.get('payment_method', 'Cash').title()]
    ]
    
    invoice_table = Table(invoice_info, colWidths=[2*inch, 3*inch])
    invoice_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    story.append(invoice_table)
    story.append(Spacer(1, 20))
    
    # Items table
    table_data = [['Product', 'Weight (kg)', 'Price/kg', 'Total']]
    
    for item in items:
        table_data.append([
            item['product_name'],
            f"{item['weight_kg']:.2f}",
            f"${item['price_per_kg']:.2f}",
            f"${item['total_price']:.2f}"
        ])
    
    # Add total row
    total_amount = sum(item['total_price'] for item in items)
    table_data.append(['', '', 'TOTAL:', f"${total_amount:.2f}"])
    
    # Create table
    items_table = Table(table_data, colWidths=[3*inch, 1*inch, 1*inch, 1*inch])
    items_table.setStyle(TableStyle([
        # Header row
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        
        # Data rows
        ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -2), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.beige, colors.white]),
        
        # Total row
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -1), (-1, -1), 12),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
        
        # Grid
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(items_table)
    story.append(Spacer(1, 30))
    
    # Footer
    story.append(Paragraph("Thank you for your business!", styles['Normal']))
    story.append(Paragraph("Please come again!", styles['Normal']))
    
    # Build PDF
    doc.build(story)
    
    return filepath

def generate_receipt_text(invoice_data, items):
    """Generate simple text receipt for display"""
    receipt = f"""
🥩 MEAT SHOP POS
================
Invoice: {invoice_data['invoice_number']}
Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Customer: {invoice_data.get('customer_name', 'Walk-in')}
Phone: {invoice_data.get('customer_phone', 'N/A')}

ITEMS:
"""
    
    total = 0
    for item in items:
        receipt += f"{item['product_name']:<20} {item['weight_kg']:>6.2f}kg @ ${item['price_per_kg']:>6.2f} = ${item['total_price']:>8.2f}\n"
        total += item['total_price']
    
    receipt += f"""
{'='*50}
TOTAL: ${total:.2f}
Payment: {invoice_data.get('payment_method', 'Cash').title()}

Thank you for your business!
"""
    
    return receipt 