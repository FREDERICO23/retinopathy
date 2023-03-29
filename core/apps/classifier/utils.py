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
