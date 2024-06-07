from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.urls import reverse
from diet_info.models import Diet_info, Reply
from datetime import datetime
from django.core.paginator import Paginator
from django.db.models import Max, Min, Avg, Sum
import os
from django.conf import settings
import shutil
from urllib import parse

# 파일 다운로드, 삭제
def download(request, diet_infoId, filename):
    file_path = os.path.join(settings.DIET_INFO_MEDIA_ROOT, diet_infoId + "/" + filename)
    
    # exists() : 파일이 있으면 True 없으면 False
    if os.path.exists(file_path):
        readFile = open(file_path, 'rb')
        response = HttpResponse(readFile.read())
        response['Content-Disposition']='attachment;filename='+parse.quote(filename)
        return response

def deleteFile(request, diet_infoId, filename):
    path = diet_infoId + "/" + filename
    file_path = os.path.join(settings.DIET_INFO_MEDIA_ROOT, path)
    os.remove(file_path)

    msg = "<script>"
    msg += f"alert('{filename} 파일을 삭제했습니다.');"
    msg += f"location.href='/diet_info/{diet_infoId}/update/';";
    msg += "</script>"

    return HttpResponse(msg)

# Create your views here.
def index(request, page):
    query = request.GET.get('query', '')
    search_by = request.GET.get('search_by', 'title')
    post_by = request.GET.get('post_by', 'present')

    if search_by == 'title':
        diet_info = Diet_info.objects.filter(제목__icontains=query)
    elif search_by == 'author':
        diet_info = Diet_info.objects.filter(작성자__icontains=query)
    elif search_by == 'content':
        diet_info = Diet_info.objects.filter(내용__icontains=query)
    else:
        diet_info = Diet_info.objects.all()

    if post_by == 'present' :
        diet_info = diet_info.order_by('-id')
    elif post_by == 'like' :
        diet_info = diet_info.order_by('-좋아요','-id')

    best_border = Diet_info.objects.order_by("-좋아요")
    
    # Paginator(데이터, 분할할 데이터 수)
    paging = Paginator(diet_info, 8)
    
    str_page = str(page)
    # 맨 마지막 숫자
    last = int(str_page[-1])
    first = int(str_page[:-1] + '1')

    if last == 0:
        max = first
        first = max - 10
    elif first + 10 > paging.num_pages:
        max = paging.num_pages + 1
    else :
        max = first + 10
    page_num = range(first, max)

    try:
        content = {
            'diet_info':paging.page(page),
            'page_num':page_num,
            'best_border':best_border,
        }
    except:
        content = {
            'diet_info':paging.page(paging.num_pages),
            'page_num':page_num,
            'best_border':best_border,
        }
    return render(request, 'information/diet_info/index.html', content);

def detail(request, diet_infoId):
    # diet_info.obejcts.get() : diet_info의 class 객체
    # diet_info = diet_info.objects.get(id=diet_infoId);
    # diet_info.조회수 = diet_info.조회수 + 1;
    # diet_info.save()
    # diet_info.obejcts.values().get() : dict 형태
    if request.user.is_active :
        video = get_object_or_404(Diet_info, pk=diet_infoId)
        diet_info = Diet_info.objects.values().get(id=diet_infoId);
        Diet_info.objects.filter(id=diet_infoId).update(조회수 = diet_info['조회수'] + 1)
        # get(id=고유번호)
        # filter(컬럼명 = 값)
        reply = Reply.objects.filter(diet_info_id=diet_infoId).values()
        
        try:
            dirList = os.listdir(settings.DIET_INFO_MEDIA_ROOT + "/" + str(diet_infoId))

            content = {
                'diet_info':diet_info,
                'reply':reply,
                'dirList':dirList,
                'video':video,
            }
        except:
            content = {
                'diet_info':diet_info,
                'reply':reply,
            }
        return render(request, 'information/diet_info/detail.html', content);
    else:
        msg = "<script>";
        msg += "alert('로그인 후 사용 가능합니다.');"
        msg += "location.href='/account/login/';"
        msg += "</script>"
        return HttpResponse(msg);

def update(request, diet_infoId):
    diet_info = Diet_info.objects.get(id=diet_infoId)
    if request.method == 'GET':
        if request.user.is_active:
            if request.user.username == diet_info.작성자:
                try:
                    dirList = os.listdir(settings.DIET_INFO_MEDIA_ROOT + "/" + str(diet_infoId))
                    content = {
                        'diet_info':diet_info,
                        'dirList':dirList,
                    }
                except:
                    content = {
                        'diet_info':diet_info,
                    }
                return render(request, 'information/diet_info/update.html', content);
            else :
                msg = "<script>"
                msg += "alert('접근할 수 없는 URL 입니다.');"
                msg += "location.href='/diet_info/page/1';"
                msg += "</script>"
                return HttpResponse(msg);
        else :
            return render(request, 'error/errorAccess.html');
    elif request.method == "POST":
        diet_info.제목 = request.POST.get('title');
        diet_info.내용 = request.POST.get('content');
        diet_info.video_url = request.POST.get('video_url');
        diet_info.수정일 = datetime.now();
        diet_info.save()

        file_upload(request, diet_info.id);

        msg = "<script>"
        msg += f"alert('{ diet_info.id }번 게시글이 수정되었습니다.');"
        msg += f"location.href='/diet_info/{ diet_info.id }/';"
        msg += "</script>"
        return HttpResponse(msg);

def delete(request, diet_infoId):
    # os.remove(파일삭제)
    # os.rmdir(폴더삭제 - 빈폴더만 삭제가능)
    path = settings.DIET_INFO_MEDIA_ROOT + "/" + str(diet_infoId) + "/"
    if os.path.isdir(path):
        # dirList = os.listdir(path)
        # for f in dirList:
        #     os.remove(path + "/" + f)
        # os.rmdir(path)
        shutil.rmtree(path)

    Diet_info.objects.get(id=diet_infoId).delete()
    Reply.objects.filter(diet_info_id=diet_infoId).delete()
    content = {
        'diet_infoId':diet_infoId
    }
    return render(request, 'information/diet_info/delete.html', content);

def add(request):
    if request.method == 'POST':
        now = datetime.now()
        diet_info = Diet_info()
        diet_info.제목 = request.POST['title']
        diet_info.video_url = request.POST.get('video_url')
        diet_info.내용 = request.POST.get("context");
        diet_info.작성자 = request.user.username;
        diet_info.작성일 = now
        diet_info.수정일 = now
        diet_info.조회수 = 0
        diet_info.save()

        file_upload(request, diet_info.id);

        msg = "<script>";
        msg += "alert('게시글이 저장되었습니다.');";
        msg += f"location.href='/diet_info/{diet_info.id}/';";
        msg += "</script>";
        return HttpResponse(msg);
        # return redirect('BD', diet_info.id)
        # return render(request, 'information/diet_info/detail.html')
    else: # GET 방식
        if request.user.is_active:
            return render(request, 'information/diet_info/add.html');
        else:
            msg = "<script>"
            msg += "alert('로그인 후 이용이 가능합니다.');"
            msg += "location.href='/account/login/';"
            msg += "</script>"
            return HttpResponse(msg)


def page(request, page):
    content = {
        'page':page,
    }
    return render(request, 'information/diet_info/page.html', content);

def addreply(request, diet_infoId):
    reply = Reply()
    reply.작성자 = request.user.username;
    reply.작성일 = datetime.now()
    reply.diet_info_id = diet_infoId
    reply.내용 = request.GET['reply']
    reply.save()
    Diet_info.objects.filter(id=diet_infoId).update(댓글수 = Reply.objects.filter(diet_info_id=diet_infoId).count())
    return redirect('DI:D', diet_infoId)

def delreply(request, diet_infoId, replyId):
    Reply.objects.get(id=replyId).delete()
    Diet_info.objects.filter(id=diet_infoId).update(댓글수 = Reply.objects.filter(diet_info_id=diet_infoId).count())
    return redirect('DI:D', diet_infoId)


def file_upload(request, diet_infoId):
    # 각 diet_info.id 의 이름으로 폴더 생성
    dirName = str(diet_infoId)
    path = settings.DIET_INFO_MEDIA_ROOT + "/" + dirName + "/"

    if not os.path.isdir(path):
        os.mkdir(path)

    for x in request.FILES.getlist("files"):
        upload_file = open(path + str(x), 'wb')
        for chunk in x.chunks():
            upload_file.write(chunk)

def good(request, diet_infoId):
    diet_info = Diet_info.objects.get(id=diet_infoId)
    diet_info.좋아요 = diet_info.좋아요 + 1
    diet_info.save()

    return redirect('DI:D', diet_infoId)

def hate(request, diet_infoId):
    diet_info = Diet_info.objects.get(id=diet_infoId)
    diet_info.싫어요 = diet_info.싫어요 + 1
    diet_info.save()
    return redirect('DI:D', diet_infoId)