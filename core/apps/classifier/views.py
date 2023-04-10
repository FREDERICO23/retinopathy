from django.shortcuts import render
from fastbook import *
from fastai.vision.all import *
import numpy as np

from base64 import b64encode
import pathlib
from django.conf import settings
from django.http import FileResponse

from .forms import ImageUploadForm
from .models import UploadedImage
from .utils import generate_report

temp = pathlib.PosixPath
pathlib.PosixPath = pathlib.WindowsPath
BASE_DIR = Path(__file__).resolve().parent.parent
filepath = os.path.join(BASE_DIR, 'classifier/resnet50_export.pkl')
model = load_learner(filepath)
classes = model.dls.vocab

classes = {
    0: 'healthy',
    1: 'fall armyworm attack',
}
severity_levels = {
    'healthy': ['low', 'medium', 'high'],
    'fall armyworm attack': ['low', 'medium', 'high'],

}

def estimate_severity(category, probs):
  
    if probs < 0.6:
        return severity_levels[category][0]  # Low severity
    elif 0.6 <= probs < 0.85:
        return severity_levels[category][1]  # Medium severity
    else:
        return severity_levels[category][2]  # High severity


def classify(img_file):
    img = PILImage.create(img_file)
    prediction = model.predict(img)
    probs_list = prediction[2].numpy()
    content = img_file.read()    
    encoded = b64encode(content)    
    img_file.seek(0)
    encoded = encoded.decode('ascii')
    mime = "image/jpg"
    image_uri = "data:%s;base64,%s" % (mime, encoded)

    category = classes[prediction[1].item()] # Use the updated classes dictionary
    probs = max(probs_list)
    severity = estimate_severity(category, probs)

    return {
        'image': image_uri,
        'category': category,
        'probs': "{:.2%}".format(probs),
        'severity': severity,
        'result': "It is {:.2%} {}. Severity level: {}!".format(probs, category, severity)
    }


def imageclassifier(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        
        if form.is_valid():  

            uploaded_image = form.save(commit=False) 
            
            media_path = os.path.join(settings.BASE_DIR, 'media', 'uploads')
            if not os.path.exists(media_path):
                os.makedirs(media_path)
            
            result = classify(request.FILES['image'])
            uploaded_image.prediction = result
              
            # Save the uploaded_image instance to the database
            uploaded_image.save()         
    
            context = {
                'form' : form,
                'result' : result,}
    
            # Generate a report
            report_file = generate_report()

            return render(request, 'success.html', context) # Redirect to a success page

    else:
        form = ImageUploadForm()

    return render(request, 'index.html', {'form': form})



def download_report(request):
    report_file = generate_report()
    response = FileResponse(open(report_file, 'rb'), content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{os.path.basename(report_file)}"'
    return response