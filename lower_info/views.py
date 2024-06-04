from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.urls import reverse
from lower_info.models import Lower_info, Reply
from datetime import datetime
from django.core.paginator import Paginator
from django.db.models import Max, Min, Avg, Sum
import os
from django.conf import settings
import shutil
from urllib import parse

# 파일 다운로드, 삭제
def download(request, lower_infoId, filename):
    file_path = os.path.join(settings.LOWER_INFO_MEDIA_ROOT, lower_infoId + "/" + filename)
    
    # exists() : 파일이 있으면 True 없으면 False
    if os.path.exists(file_path):
        readFile = open(file_path, 'rb')
        response = HttpResponse(readFile.read())
        response['Content-Disposition']='attachment;filename='+parse.quote(filename)
        return response

def deleteFile(request, lower_infoId, filename):
    path = lower_infoId + "/" + filename
    file_path = os.path.join(settings.LOWER_INFO_MEDIA_ROOT, path)
    os.remove(file_path)

    msg = "<script>"
    msg += f"alert('{filename} 파일을 삭제했습니다.');"
    msg += f"location.href='/lower_info/{lower_infoId}/update/';";
    msg += "</script>"

    return HttpResponse(msg)

# Create your views here.
def index(request, page):
    query = request.GET.get('query', '')
    search_by = request.GET.get('search_by', 'title')

    if search_by == 'title':
        lower_info = Lower_info.objects.filter(제목__icontains=query)
    elif search_by == 'author':
        lower_info = Lower_info.objects.filter(작성자__icontains=query)
    elif search_by == 'content':
        lower_info = Lower_info.objects.filter(내용__icontains=query)
    else:
        lower_info = Lower_info.objects.all()

    lower_info = lower_info.order_by('-id')
    
    # Paginator(데이터, 분할할 데이터 수)
    paging = Paginator(lower_info, 8)
    
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
            'lower_info':paging.page(page),
            'page_num':page_num,
        }
    except:
        content = {
            'lower_info':paging.page(paging.num_pages),
            'page_num':page_num,
        }
    return render(request, 'information/lower_info/index.html', content);

def detail(request, lower_infoId):
    # lower_info.obejcts.get() : lower_info의 class 객체
    # lower_info = lower_info.objects.get(id=lower_infoId);
    # lower_info.조회수 = lower_info.조회수 + 1;
    # lower_info.save()
    # lower_info.obejcts.values().get() : dict 형태
    if request.user.is_active :
        video = get_object_or_404(Lower_info, pk=lower_infoId)
        lower_info = Lower_info.objects.values().get(id=lower_infoId);
        Lower_info.objects.filter(id=lower_infoId).update(조회수 = lower_info['조회수'] + 1)
        # get(id=고유번호)
        # filter(컬럼명 = 값)
        reply = Reply.objects.filter(lower_info_id=lower_infoId).values()
        
        try:
            dirList = os.listdir(settings.LOWER_INFO_MEDIA_ROOT + "/" + str(lower_infoId))

            content = {
                'lower_info':lower_info,
                'reply':reply,
                'dirList':dirList,
                'video': video,
            }
        except:
            content = {
                'lower_info':lower_info,
                'reply':reply,
            }
        return render(request, 'information/lower_info/detail.html', content);
    else:
        msg = "<script>";
        msg += "alert('로그인 후 사용 가능합니다.');"
        msg += "location.href='/account/login/';"
        msg += "</script>"
        return HttpResponse(msg);

def update(request, lower_infoId):
    lower_info = Lower_info.objects.get(id=lower_infoId)
    if request.method == 'GET':
        if request.user.is_active:
            if request.user.username == lower_info.작성자:
                try:
                    dirList = os.listdir(settings.LOWER_INFO_MEDIA_ROOT + "/" + str(lower_infoId))
                    content = {
                        'lower_info':lower_info,
                        'dirList':dirList,
                    }
                except:
                    content = {
                        'lower_info':lower_info,
                    }
                return render(request, 'information/lower_info/update.html', content);
            else :
                msg = "<script>"
                msg += "alert('접근할 수 없는 URL 입니다.');"
                msg += "location.href='/lower_info/page/1';"
                msg += "</script>"
                return HttpResponse(msg);
        else :
            return render(request, 'error/errorAccess.html');
    elif request.method == "POST":
        lower_info.제목 = request.POST.get('title');
        lower_info.내용 = request.POST.get('content');
        lower_info.video_url = request.POST.get('video_url');
        lower_info.수정일 = datetime.now();
        lower_info.save()

        file_upload(request, lower_info.id);

        msg = "<script>"
        msg += f"alert('{ lower_info.id }번 게시글이 수정되었습니다.');"
        msg += f"location.href='/lower_info/{ lower_info.id }/';"
        msg += "</script>"
        return HttpResponse(msg);

def delete(request, lower_infoId):
    # os.remove(파일삭제)
    # os.rmdir(폴더삭제 - 빈폴더만 삭제가능)
    path = settings.LOWER_INFO_MEDIA_ROOT + "/" + str(lower_infoId) + "/"
    if os.path.isdir(path):
        # dirList = os.listdir(path)
        # for f in dirList:
        #     os.remove(path + "/" + f)
        # os.rmdir(path)
        shutil.rmtree(path)

    Lower_info.objects.get(id=lower_infoId).delete()
    Reply.objects.filter(lower_info_id=lower_infoId).delete()
    content = {
        'lower_infoId':lower_infoId
    }
    return render(request, 'information/lower_info/delete.html', content);

def add(request):
    if request.method == 'POST':
        now = datetime.now()
        lower_info = Lower_info()
        lower_info.제목 = request.POST['title']
        lower_info.video_url = request.POST.get('video_url')
        lower_info.내용 = request.POST.get("context");
        lower_info.작성자 = request.user.username;
        lower_info.작성일 = now
        lower_info.수정일 = now
        lower_info.조회수 = request.POST['vcount']
        lower_info.save()

        file_upload(request, lower_info.id);

        msg = "<script>";
        msg += "alert('게시글이 저장되었습니다.');";
        msg += f"location.href='/lower_info/{lower_info.id}/';";
        msg += "</script>";
        return HttpResponse(msg);
        # return redirect('BD', lower_info.id)
        # return render(request, 'information/lower_info/detail.html')
    else: # GET 방식
        if request.user.is_active:
            return render(request, 'information/lower_info/add.html');
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
    return render(request, 'information/lower_info/page.html', content);

def addreply(request, lower_infoId):
    reply = Reply()
    reply.작성자 = request.user.username;
    reply.작성일 = datetime.now()
    reply.lower_info_id = lower_infoId
    reply.내용 = request.GET['reply']
    reply.save()
    Lower_info.objects.filter(id=lower_infoId).update(댓글수 = Reply.objects.filter(lower_info_id=lower_infoId).count())
    return redirect('LI:D', lower_infoId)

def delreply(request, lower_infoId, replyId):
    Reply.objects.get(id=replyId).delete()
    Lower_info.objects.filter(id=lower_infoId).update(댓글수 = Reply.objects.filter(lower_info_id=lower_infoId).count())
    return redirect('LI:D', lower_infoId)


def file_upload(request, lower_infoId):
    # 각 lower_info.id 의 이름으로 폴더 생성
    dirName = str(lower_infoId)
    path = settings.LOWER_INFO_MEDIA_ROOT + "/" + dirName + "/"

    if not os.path.isdir(path):
        os.mkdir(path)

    for x in request.FILES.getlist("files"):
        upload_file = open(path + str(x), 'wb')
        for chunk in x.chunks():
            upload_file.write(chunk)

def good(request, lower_infoId):
    lower_info = Lower_info.objects.get(id=lower_infoId)
    lower_info.좋아요 = lower_info.좋아요 + 1
    lower_info.save()

    return redirect('LI:D', lower_infoId)

def hate(request, lower_infoId):
    lower_info = Lower_info.objects.get(id=lower_infoId)
    lower_info.싫어요 = lower_info.싫어요 + 1
    lower_info.save()
    return redirect('LI:D', lower_infoId)
