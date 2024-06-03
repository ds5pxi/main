from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.urls import reverse
from routine_info.models import Routine_info, Reply
from datetime import datetime
from django.core.paginator import Paginator
from django.db.models import Max, Min, Avg, Sum
import os
from django.conf import settings
import shutil

# Create your views here.
def index(request, page):
    routine_info = Routine_info.objects.all().order_by('-id')
    
    # Paginator(데이터, 분할할 데이터 수)
    paging = Paginator(routine_info, 10)
    
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
            'routine_info':paging.page(page),
            'page_num':page_num,
        }
    except:
        content = {
            'routine_info':paging.page(paging.num_pages),
            'page_num':page_num,
        }
    return render(request, 'information/routine_info/index.html', content);

def detail(request, routine_infoId):
    # routine_info.obejcts.get() : routine_info의 class 객체
    # routine_info = routine_info.objects.get(id=routine_infoId);
    # routine_info.조회수 = routine_info.조회수 + 1;
    # routine_info.save()
    # routine_info.obejcts.values().get() : dict 형태
    if request.user.is_active :
        video = get_object_or_404(Routine_info, pk=routine_infoId)
        routine_info = Routine_info.objects.values().get(id=routine_infoId);
        Routine_info.objects.filter(id=routine_infoId).update(조회수 = routine_info['조회수'] + 1)
        # get(id=고유번호)
        # filter(컬럼명 = 값)
        reply = Reply.objects.filter(routine_info_id=routine_infoId).values()
        
        try:
            dirList = os.listdir(settings.ROUTINE_INFO_MEDIA_ROOT + "/" + str(routine_infoId))

            content = {
                'routine_info':routine_info,
                'reply':reply,
                'dirList':dirList,
                'video':video,
            }
        except:
            content = {
                'routine_info':routine_info,
                'reply':reply,
            }
        return render(request, 'information/routine_info/detail.html', content);
    else:
        msg = "<script>";
        msg += "alert('로그인 후 사용 가능합니다.');"
        msg += "location.href='/account/login/';"
        msg += "</script>"
        return HttpResponse(msg);

def update(request, routine_infoId):
    routine_info = Routine_info.objects.get(id=routine_infoId)
    if request.method == 'GET':
        if request.user.is_active:
            if request.user.username == routine_info.작성자:
                try:
                    dirList = os.listdir(settings.ROUTINE_INFO_MEDIA_ROOT + "/" + str(routine_infoId))
                    content = {
                        'routine_info':routine_info,
                        'dirList':dirList,
                    }
                except:
                    content = {
                        'routine_info':routine_info,
                    }
                return render(request, 'information/routine_info/update.html', content);
            else :
                msg = "<script>"
                msg += "alert('접근할 수 없는 URL 입니다.');"
                msg += "location.href='/routine_info/page/1';"
                msg += "</script>"
                return HttpResponse(msg);
        else :
            return render(request, 'error/errorAccess.html');
    elif request.method == "POST":
        routine_info.제목 = request.POST.get('title');
        routine_info.내용 = request.POST.get('content');
        routine_info.video_url = request.POST.get('video_url');
        routine_info.수정일 = datetime.now();
        routine_info.save()

        file_upload(request, routine_info.id);

        msg = "<script>"
        msg += f"alert('{ routine_info.id }번 게시글이 수정되었습니다.');"
        msg += f"location.href='/routine_info/{ routine_info.id }/';"
        msg += "</script>"
        return HttpResponse(msg);

def delete(request, routine_infoId):
    # os.remove(파일삭제)
    # os.rmdir(폴더삭제 - 빈폴더만 삭제가능)
    path = settings.ROUTINE_INFO_MEDIA_ROOT + "/" + str(routine_infoId) + "/"
    if os.path.isdir(path):
        # dirList = os.listdir(path)
        # for f in dirList:
        #     os.remove(path + "/" + f)
        # os.rmdir(path)
        shutil.rmtree(path)

    Routine_info.objects.get(id=routine_infoId).delete()
    Reply.objects.filter(routine_info_id=routine_infoId).delete()
    content = {
        'routine_infoId':routine_infoId
    }
    return render(request, 'information/routine_info/delete.html', content);

def add(request):
    if request.method == 'POST':
        now = datetime.now()
        routine_info = Routine_info()
        routine_info.제목 = request.POST['title']
        routine_info.video_url = request.POST.get('video_url')
        routine_info.내용 = request.POST.get("context");
        routine_info.작성자 = request.user.username;
        routine_info.작성일 = now
        routine_info.수정일 = now
        routine_info.조회수 = request.POST['vcount']
        routine_info.save()

        file_upload(request, routine_info.id);

        msg = "<script>";
        msg += "alert('게시글이 저장되었습니다.');";
        msg += f"location.href='/routine_info/{routine_info.id}/';";
        msg += "</script>";
        return HttpResponse(msg);
        # return redirect('RI', routine_info.id)
        # return render(request, 'information/routine_info/detail.html')
    else: # GET 방식
        if request.user.is_active:
            return render(request, 'information/routine_info/add.html');
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
    return render(request, 'information/routine_info/page.html', content);

def addreply(request, routine_infoId):
    reply = Reply()
    reply.작성자 = request.user.username;
    reply.작성일 = datetime.now()
    reply.routine_info_id = routine_infoId
    reply.내용 = request.GET['reply']
    reply.save()
    Routine_info.objects.filter(id=routine_infoId).update(댓글수 = Reply.objects.filter(routine_info_id=routine_infoId).count())
    return redirect('RI:D', routine_infoId)

def delreply(request, routine_infoId, replyId):
    Reply.objects.get(id=replyId).delete()
    Routine_info.objects.filter(id=routine_infoId).update(댓글수 = Reply.objects.filter(routine_info_id=routine_infoId).count())
    return redirect('RI:D', routine_infoId)


def file_upload(request, routine_infoId):
    # 각 routine_info.id 의 이름으로 폴더 생성
    dirName = str(routine_infoId)
    path = settings.ROUTINE_INFO_MEDIA_ROOT + "/" + dirName + "/"

    if not os.path.isdir(path):
        os.mkdir(path)

    for x in request.FILES.getlist("files"):
        upload_file = open(path + str(x), 'wb')
        for chunk in x.chunks():
            upload_file.write(chunk)

def good(request, routine_infoId):
    routine_info = Routine_info.objects.get(id=routine_infoId)
    routine_info.좋아요 = routine_info.좋아요 + 1
    routine_info.save()

    return redirect('RI:D', routine_infoId)

def hate(request, routine_infoId):
    routine_info = Routine_info.objects.get(id=routine_infoId)
    routine_info.싫어요 = routine_info.싫어요 + 1
    routine_info.save()
    return redirect('RI:D', routine_infoId)