from django.shortcuts import render, redirect, HttpResponse
from django.conf import settings
from urllib import parse
import os

# Create your views here.
def index(request):
    dirList = os.listdir(settings.MEDIA_ROOT)
    content = {
        'dirList':dirList,
    }
    return render(request, 'updown/index.html', content)

def upload(request):
    if request.method == "POST":
        for x in request.FILES.getlist("files"):
            ext = str(x)[-4:]
            if ext in ['.png', '.jpg', 'jpeg', '.gif']:
                print(ext)
                upload_file = open(settings.MEDIA_ROOT + "\\" + str(x), 'wb')
                for chunk in x.chunks():
                    print(chunk)
                    upload_file.write(chunk)
            else:
                msg = "<script>";
                msg += "alert('이미지 파일 이외는 업로드가 금지됩니다.');"
                msg += "location.href='/updown/upload/';"
                msg += "</script>"
                return HttpResponse(msg)
        return redirect('/updown/')
    else:
        return render(request, 'updown/upload.html')
    
def download(request, borderId, filename):
    file_path = os.path.join(settings.MEDIA_ROOT, borderId + "/" + filename)
    
    # exists() : 파일이 있으면 True 없으면 False
    if os.path.exists(file_path):
        readFile = open(file_path, 'rb')
        response = HttpResponse(readFile.read())
        response['Content-Disposition']='attachment;filename='+parse.quote(filename)
        return response

def delete(request, borderId, filename):
    path = borderId + "/" + filename
    file_path = os.path.join(settings.MEDIA_ROOT, path)
    os.remove(file_path)

    msg = "<script>"
    msg += f"alert('{filename} 파일을 삭제했습니다.');"
    msg += f"location.href='/border/{borderId}/update/';";
    msg += "</script>"

    return HttpResponse(msg)