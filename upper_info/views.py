from django.shortcuts import render, redirect, HttpResponse
from upper_info.models import Upper_info, Reply
from datetime import datetime
from django.core.paginator import Paginator
from django.db.models import Max, Min, Avg, Sum
import os
from django.conf import settings
import shutil

# Create your views here.
def index(request, page):
    upper_info = Upper_info.objects.all().order_by('-id')
    
    # Paginator(데이터, 분할할 데이터 수)
    paging = Paginator(upper_info, 10)
    
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
            'upper_info':paging.page(page),
            'page_num':page_num,
        }
    except:
        content = {
            'upper_info':paging.page(paging.num_pages),
            'page_num':page_num,
        }
    return render(request, 'information/upper_info/index.html', content);

def detail(request, upper_infoId):
    # upper_info.obejcts.get() : upper_info의 class 객체
    # upper_info = upper_info.objects.get(id=upper_infoId);
    # upper_info.조회수 = upper_info.조회수 + 1;
    # upper_info.save()
    # upper_info.obejcts.values().get() : dict 형태
    if request.user.is_active :
        upper_info = Upper_info.objects.values().get(id=upper_infoId);
        Upper_info.objects.filter(id=upper_infoId).update(조회수 = upper_info['조회수'] + 1)
        # get(id=고유번호)
        # filter(컬럼명 = 값)
        reply = Reply.objects.filter(upper_info_id=upper_infoId).values()
        
        try:
            dirList = os.listdir(settings.UPPER_INFO_MEDIA_ROOT + "/" + str(upper_infoId))

            content = {
                'upper_info':upper_info,
                'reply':reply,
                'dirList':dirList,
            }
        except:
            content = {
                'upper_info':upper_info,
                'reply':reply,
            }
        return render(request, 'information/upper_info/detail.html', content);
    else:
        msg = "<script>";
        msg += "alert('로그인 후 사용 가능합니다.');"
        msg += "location.href='/account/login/';"
        msg += "</script>"
        return HttpResponse(msg);

def update(request, upper_infoId):
    upper_info = Upper_info.objects.get(id=upper_infoId)
    if request.method == 'GET':
        if request.user.is_active:
            if request.user.username == upper_info.작성자:
                try:
                    dirList = os.listdir(settings.UPPER_INFO_MEDIA_ROOT + "/" + str(upper_infoId))
                    content = {
                        'upper_info':upper_info,
                        'dirList':dirList,
                    }
                except:
                    content = {
                        'upper_info':upper_info,
                    }
                return render(request, 'information/upper_info/update.html', content);
            else :
                msg = "<script>"
                msg += "alert('접근할 수 없는 URL 입니다.');"
                msg += "location.href='/upper_info/page/1';"
                msg += "</script>"
                return HttpResponse(msg);
        else :
            return render(request, 'error/errorAccess.html');
    elif request.method == "POST":
        upper_info.제목 = request.POST.get('title');
        upper_info.내용 = request.POST.get('content');
        upper_info.수정일 = datetime.now();
        upper_info.save()

        file_upload(request, upper_info.id);

        msg = "<script>"
        msg += f"alert('{ upper_info.id }번 게시글이 수정되었습니다.');"
        msg += f"location.href='/upper_info/{ upper_info.id }/';"
        msg += "</script>"
        return HttpResponse(msg);

def delete(request, upper_infoId):
    # os.remove(파일삭제)
    # os.rmdir(폴더삭제 - 빈폴더만 삭제가능)
    path = settings.UPPER_INFO_MEDIA_ROOT + "/" + str(upper_infoId) + "/"
    if os.path.isdir(path):
        # dirList = os.listdir(path)
        # for f in dirList:
        #     os.remove(path + "/" + f)
        # os.rmdir(path)
        shutil.rmtree(path)

    Upper_info.objects.get(id=upper_infoId).delete()
    Reply.objects.filter(upper_info_id=upper_infoId).delete()
    content = {
        'upper_infoId':upper_infoId
    }
    return render(request, 'information/upper_info/delete.html', content);

def add(request):
    if request.method == 'POST':
        now = datetime.now()
        upper_info = Upper_info()
        upper_info.제목 = request.POST['title']
        upper_info.내용 = request.POST.get("context");
        upper_info.작성자 = request.user.username;
        upper_info.작성일 = now
        upper_info.수정일 = now
        upper_info.조회수 = request.POST['vcount']
        upper_info.save()

        file_upload(request, upper_info.id);

        msg = "<script>";
        msg += "alert('게시글이 저장되었습니다.');";
        msg += f"location.href='/upper_info/{upper_info.id}/';";
        msg += "</script>";
        return HttpResponse(msg);
        # return redirect('BD', upper_info.id)
        # return render(request, 'information/upper_info/detail.html')
    else: # GET 방식
        if request.user.is_active:
            return render(request, 'information/upper_info/add.html');
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
    return render(request, 'information/upper_info/page.html', content);

def addreply(request, upper_infoId):
    reply = Reply()
    reply.작성자 = request.user.username;
    reply.작성일 = datetime.now()
    reply.upper_info_id = upper_infoId
    reply.내용 = request.GET['reply']
    reply.save()
    Upper_info.objects.filter(id=upper_infoId).update(댓글수 = Reply.objects.filter(upper_info_id=upper_infoId).count())
    return redirect('UI:D', upper_infoId)

def delreply(request, upper_infoId, replyId):
    Reply.objects.get(id=replyId).delete()
    Upper_info.objects.filter(id=upper_infoId).update(댓글수 = Reply.objects.filter(upper_info_id=upper_infoId).count())
    return redirect('UI:D', upper_infoId)


def file_upload(request, upper_infoId):
    # 각 upper_info.id 의 이름으로 폴더 생성
    dirName = str(upper_infoId)
    path = settings.UPPER_INFO_MEDIA_ROOT + "/" + dirName + "/"

    if not os.path.isdir(path):
        os.mkdir(path)

    for x in request.FILES.getlist("files"):
        upload_file = open(path + str(x), 'wb')
        for chunk in x.chunks():
            upload_file.write(chunk)

def good(request, upper_infoId):
    upper_info = Upper_info.objects.get(id=upper_infoId)
    upper_info.좋아요 = upper_info.좋아요 + 1
    upper_info.save()

    return redirect('UI:D', upper_infoId)

def hate(request, upper_infoId):
    upper_info = Upper_info.objects.get(id=upper_infoId)
    upper_info.싫어요 = upper_info.싫어요 + 1
    upper_info.save()
    return redirect('UI:D', upper_infoId)