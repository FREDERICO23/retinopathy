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


def contains_maize_plant(img):
    model = MobileNetV2(weights='imagenet')
    
    img = img.resize((224, 224))
    img_array = keras_image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = preprocess_input(img_array)

    preds = model.predict(img_array)
    decoded_preds = decode_predictions(preds, top=5)[0]

    for pred in decoded_preds:
        if 'maize' in pred[1].lower() or 'corn' in pred[1].lower():
            return True

    return False

def classify(img_file):
    img = PILImage.create(img_file)
    prediction = model.predict(img)
    probs_list = prediction[2].numpy()
     # Read the content of the uploaded image
    content = img_file.read()    
    # Encode the content
    encoded = b64encode(content)    
    # Reset the file pointer to the beginning of the file
    img_file.seek(0)
    # encoded = b64encode(img_file)
    encoded = encoded.decode('ascii')
    mime = "image/jpg"
    image_uri = "data:%s;base64,%s" % (mime, encoded)
    return {
        'image' : image_uri,
        'category': classes[prediction[1].item()],
        'probs': "{:.2%}".format(max(probs_list)),
        'result': "It is {:.2%} {}!".format(max(probs_list), classes[prediction[1].item()])
    }

# Create your views here.
# def imageclassifier(request):
#     form = ImageUploadForm(request.POST, request.FILES)
#     result = {}
#     #print(result)

#     if form.is_valid():
#         image = [request.FILES['image'], form.cleaned_data['image'].file.read()]
#         result = classify(image)
    
#     context = {
#         'form' : form,
#         'result' : result,
#     }

#     return render(request, 'index.html', context)

# Make a prediction using your custom function
            # uploaded_image.prediction = classify(uploaded_image.image.path)
            # print("Image file path:", os.path.join(settings.MEDIA_ROOT, uploaded_image.image.name))

            # uploaded_image.prediction = classify(os.path.join(settings.MEDIA_ROOT, uploaded_image.image.name))            
            # uploaded_image.save()
            # print("Image path:", uploaded_image.image.path)

def imageclassifier(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        
        if form.is_valid():  

            uploaded_image = form.save(commit=False) 
            
            media_path = os.path.join(settings.BASE_DIR, 'media', 'uploads')
            if not os.path.exists(media_path):
                os.makedirs(media_path)
            
            uploaded_image.prediction = classify(request.FILES['image'])

              
            # Save the uploaded_image instance to the database
            uploaded_image.save()         
    
            context = {
                'form' : form,
                'result' : uploaded_image,}
    
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