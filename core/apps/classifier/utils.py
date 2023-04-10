import csv
import os
from .models import UploadedImage

def generate_report():
    # Define the report's filename and location
    report_file = 'reports/prediction-report.csv'

    # Get all the UploadedImage instances
    uploaded_images = UploadedImage.objects.all()

    os.makedirs('reports', exist_ok=True)

    # Write the data to the CSV file
    with open(report_file, 'w', newline='') as csvfile:
        fieldnames = ['id', 'image', 'prediction', 'upload_date']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()

        for image in uploaded_images:
            writer.writerow({
                'id': image.id,
                'image': image.image.path,
                'prediction': image.prediction,
                'upload_date': image.upload_date.strftime('%Y-%m-%d %H:%M:%S')
            })

    return report_file

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER

def generate_pdf_report(result):
    report_filename = f"{result['category']}_report.pdf"
    report_path = os.path.join("reports", report_filename)

    if not os.path.exists("reports"):
        os.makedirs("reports")

    doc = SimpleDocTemplate(report_path, pagesize=letter)
    story = []

    # Set up styles
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))
    styles.add(ParagraphStyle(name='Center', alignment=TA_CENTER))

    # Add title
    title = f"Image Classification Report: {result['category']}"
    story.append(Paragraph(title, styles['Heading1']))
    story.append(Spacer(1, 12))

    # Add image
    img = Image(result['image'], width=300, height=300)
    story.append(img)
    story.append(Spacer(1, 12))

    # Add results
    story.append(Paragraph(f"Category: {result['category']}", styles['Center']))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"Confidence: {result['probs']}", styles['Center']))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"Severity level: {result['severity']}", styles['Center']))
    story.append(Spacer(1, 12))

    # Add note for non-techy users
    note = '''
    <para align=center spaceb=12>
        <b>Note:</b> This report provides information about the classification
        of the image you submitted. The category indicates the classification
        result, while the confidence shows how sure the system is about the
        classification. The severity level represents the estimated impact or
        severity of the identified category.
    </para>
    '''
    story.append(Paragraph(note, styles['Justify']))

    # Build the PDF
    doc.build(story)

    return report_path
