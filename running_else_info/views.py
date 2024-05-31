from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, HttpResponse
from running_else_info.models import Running_else_info, Reply
from datetime import datetime
from django.core.paginator import Paginator
from django.db.models import Max, Min, Avg, Sum
import os
from django.conf import settings
import shutil

# Create your views here.
def index(request, page):
    running_else_info = Running_else_info.objects.all().order_by('-id')
    
    # Paginator(데이터, 분할할 데이터 수)
    paging = Paginator(running_else_info, 10)
    
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
            'running_else_info':paging.page(page),
            'page_num':page_num,
        }
    except:
        content = {
            'running_else_info':paging.page(paging.num_pages),
            'page_num':page_num,
        }
    return render(request,'information/running_else_info/index.html', content);

def detail(request, running_else_infoId):
    # running_else_info.obejcts.get() : running_else_info의 class 객체
    # running_else_info = running_else_info.objects.get(id=running_else_infoId);
    # running_else_info.조회수 = running_else_info.조회수 + 1;
    # running_else_info.save()
    # running_else_info.obejcts.values().get() : dict 형태
    if request.user.is_active :
        running_else_info = Running_else_info.objects.values().get(id=running_else_infoId);
        Running_else_info.objects.filter(id=running_else_infoId).update(조회수 = running_else_info['조회수'] + 1)
        # get(id=고유번호)
        # filter(컬럼명 = 값)
        reply = Reply.objects.filter(running_else_info_id=running_else_infoId).values()
        
        try:
            dirList = os.listdir(settings.RUNNING_ELSE_INFO_MEDIA_ROOT + "/" + str(running_else_infoId))

            content = {
                'running_else_info':running_else_info,
                'reply':reply,
                'dirList':dirList,
            }
        except:
            content = {
                'running_else_info':running_else_info,
                'reply':reply,
            }
        return render(request, 'information/running_else_info/detail.html', content);
    else:
        msg = "<script>";
        msg += "alert('로그인 후 사용 가능합니다.');"
        msg += "location.href='/account/login/';"
        msg += "</script>"
        return HttpResponse(msg);

def update(request, running_else_infoId):
    running_else_info = Running_else_info.objects.get(id=running_else_infoId)
    if request.method == 'GET':
        if request.user.is_active:
            if request.user.username == running_else_info.작성자:
                try:
                    dirList = os.listdir(settings.RUNNING_ELSE_INFO_MEDIA_ROOT + "/" + str(running_else_infoId))
                    content = {
                        'running_else_info':running_else_info,
                        'dirList':dirList,
                    }
                except:
                    content = {
                        'running_else_info':running_else_info,
                    }
                return render(request, 'information/running_else_info/update.html', content);
            else :
                msg = "<script>"
                msg += "alert('접근할 수 없는 URL 입니다.');"
                msg += "location.href='/running_else_info/page/1';"
                msg += "</script>"
                return HttpResponse(msg);
        else :
            return render(request, 'error/errorAccess.html');
    elif request.method == "POST":
        running_else_info.제목 = request.POST.get('title');
        running_else_info.내용 = request.POST.get('content');
        running_else_info.수정일 = datetime.now();
        running_else_info.save()

        file_upload(request, running_else_info.id);

        msg = "<script>"
        msg += f"alert('{ running_else_info.id }번 게시글이 수정되었습니다.');"
        msg += f"location.href='/running_else_info/{ running_else_info.id }/';"
        msg += "</script>"
        return HttpResponse(msg);

def delete(request, running_else_infoId):
    # os.remove(파일삭제)
    # os.rmdir(폴더삭제 - 빈폴더만 삭제가능)
    path = settings.RUNNING_ELSE_INFO_MEDIA_ROOT + "/" + str(running_else_infoId) + "/"
    if os.path.isdir(path):
        # dirList = os.listdir(path)
        # for f in dirList:
        #     os.remove(path + "/" + f)
        # os.rmdir(path)
        shutil.rmtree(path)

    Running_else_info.objects.get(id=running_else_infoId).delete()
    Reply.objects.filter(running_else_info_id=running_else_infoId).delete()
    content = {
        'running_else_infoId':running_else_infoId
    }
    return render(request, 'information/running_else_info/delete.html', content);

def add(request):
    if request.method == 'POST':
        now = datetime.now()
        running_else_info = Running_else_info()
        running_else_info.제목 = request.POST['title']
        running_else_info.내용 = request.POST.get("context");
        running_else_info.작성자 = request.user.username;
        running_else_info.작성일 = now
        running_else_info.수정일 = now
        running_else_info.조회수 = request.POST['vcount']
        running_else_info.save()

        file_upload(request, running_else_info.id);

        msg = "<script>";
        msg += "alert('게시글이 저장되었습니다.');";
        msg += f"location.href='/running_else_info/{running_else_info.id}/';";
        msg += "</script>";
        return HttpResponse(msg);
        # return redirect('BD', running_else_info.id)
        # return render(request, 'information/running_else_info/detail.html')
    else: # GET 방식
        if request.user.is_active:
            return render(request, 'information/running_else_info/add.html');
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
    return render(request, 'information/running_else_info/page.html', content);

def addreply(request, running_else_infoId):
    reply = Reply()
    reply.작성자 = request.user.username;
    reply.작성일 = datetime.now()
    reply.running_else_info_id = running_else_infoId
    reply.내용 = request.GET['reply']
    reply.save()
    Running_else_info.objects.filter(id=running_else_infoId).update(댓글수 = Reply.objects.filter(running_else_info_id=running_else_infoId).count())
    return redirect('EI:D', running_else_infoId)

def delreply(request, running_else_infoId, replyId):
    Reply.objects.get(id=replyId).delete()
    Running_else_info.objects.filter(id=running_else_infoId).update(댓글수 = Reply.objects.filter(running_else_info_id=running_else_infoId).count())
    return redirect('EI:D', running_else_infoId)


def file_upload(request, running_else_infoId):
    # 각 running_else_info.id 의 이름으로 폴더 생성
    dirName = str(running_else_infoId)
    path = settings.RUNNING_ELSE_INFO_MEDIA_ROOT + "/" + dirName + "/"

    if not os.path.isdir(path):
        os.mkdir(path)

    for x in request.FILES.getlist("files"):
        upload_file = open(path + str(x), 'wb')
        for chunk in x.chunks():
            upload_file.write(chunk)

def good(request, running_else_infoId):
    running_else_info = Running_else_info.objects.get(id=running_else_infoId)
    running_else_info.좋아요 = running_else_info.좋아요 + 1
    running_else_info.save()

    return redirect('EI:D', running_else_infoId)

def hate(request, running_else_infoId):
    running_else_info = Running_else_info.objects.get(id=running_else_infoId)
    running_else_info.싫어요 = running_else_info.싫어요 + 1
    running_else_info.save()
    return redirect('EI:D', running_else_infoId)