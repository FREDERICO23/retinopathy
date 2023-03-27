from django.shortcuts import render
from fastbook import *
from fastai.vision.all import *
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

def classify(img_file):
    img = PILImage.create(img_file[0])
    prediction = model.predict(img)
    probs_list = prediction[2].numpy()
    encoded = b64encode(img_file[1])
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


def imageclassifier(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_image = form.save(commit=False)
            # Make a prediction using your custom function
            # uploaded_image.prediction = classify(uploaded_image.image.path)
            print("Absolute path:", os.path.join(settings.MEDIA_ROOT, uploaded_image.image.url[1:]))

            uploaded_image.prediction = classify(os.path.join(settings.MEDIA_ROOT, uploaded_image.image.url[1:]))
            print("Image path:", uploaded_image.image.path)
            print("Image URL:", uploaded_image.image.url)
            print("Absolute path:", os.path.join(settings.MEDIA_ROOT, uploaded_image.image.url[1:]))
            uploaded_image.save()
            print("Image path:", uploaded_image.image.path)

            # Generate a report
            report_file = generate_report()

            return render(request, 'success.html') # Redirect to a success page

    else:
        form = ImageUploadForm()

    return render(request, 'index.html', {'form': form})

def download_report(request):
    report_file = generate_report()
    response = FileResponse(open(report_file, 'rb'), content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{os.path.basename(report_file)}"'
    return response