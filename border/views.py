from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from border.models import Border, Reply
from datetime import datetime
from django.core.paginator import Paginator
from django.db.models import Max, Min, Avg, Sum
import os
from django.conf import settings
import shutil
from django.urls import reverse


def index(request, page):
    query = request.GET.get('query', '')
    search_by = request.GET.get('search_by', 'title')
    post_by = request.GET.get('post_by', 'present')

    if search_by == 'title':
        border = Border.objects.filter(제목__icontains=query)
    elif search_by == 'author':
        border = Border.objects.filter(작성자__icontains=query)
    elif search_by == 'content':
        border = Border.objects.filter(내용__icontains=query)
    else:
        border = Border.objects.all()

    if post_by == 'present' :
        border = border.order_by('-id')
    elif post_by == 'like' :
        border = border.order_by('-좋아요','-id')

    best_border = Border.objects.order_by("-좋아요")
    
    # Paginator(데이터, 분할할 데이터 수)
    paging = Paginator(border, 8)
    
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
            'border':paging.page(page),
            'page_num':page_num,
            'best_border':best_border,
        }
    except:
        content = {
            'border':paging.page(paging.num_pages),
            'page_num':page_num,
            'best_border':best_border,
        }
    return render(request, 'border/index.html', content);

def detail(request, borderId):
    # Border.obejcts.get() : Border의 class 객체
    # border = Border.objects.get(id=borderId);
    # border.조회수 = border.조회수 + 1;
    # border.save()
    # Border.obejcts.values().get() : dict 형태
    if request.user.is_active :
        video = get_object_or_404(Border, pk=borderId)
        border = Border.objects.values().get(id=borderId);
        Border.objects.filter(id=borderId).update(조회수 = border['조회수'] + 1)
        # get(id=고유번호)
        # filter(컬럼명 = 값)
        reply = Reply.objects.filter(border_id=borderId).values()
        
        try:
            dirList = os.listdir(settings.MEDIA_ROOT + "/" + str(borderId))

            content = {
                'border':border,
                'reply':reply,
                'dirList':dirList,
                'video': video,
            }
        except:
            content = {
                'border':border,
                'reply':reply,
            }
        return render(request, 'border/detail.html', content);
    else:
        msg = "<script>";
        msg += "alert('로그인 후 사용 가능합니다.');"
        msg += "location.href='/account/login/';"
        msg += "</script>"
        return HttpResponse(msg);

def update(request, borderId):
    border = Border.objects.get(id=borderId)
    if request.method == 'GET':
        if request.user.is_active:
            if request.user.username == border.작성자:
                try:
                    dirList = os.listdir(settings.MEDIA_ROOT + "/" + str(borderId))
                    content = {
                        'border':border,
                        'dirList':dirList,
                    }
                except:
                    content = {
                        'border':border,
                    }
                return render(request, 'border/update.html', content);
            else :
                msg = "<script>"
                msg += "alert('접근할 수 없는 URL 입니다.');"
                msg += "location.href='/border/page/1';"
                msg += "</script>"
                return HttpResponse(msg);
        else :
            return render(request, 'error/errorAccess.html');
    elif request.method == "POST":
        border.제목 = request.POST.get('title');
        border.내용 = request.POST.get('content');
        border.video_url = request.POST.get('video_url')
        border.수정일 = datetime.now();
        border.save()

        file_upload(request, border.id);

        msg = "<script>"
        msg += f"alert('{ border.id }번 게시글이 수정되었습니다.');"
        msg += f"location.href='/border/{ border.id }/';"
        msg += "</script>"
        return HttpResponse(msg);

def delete(request, borderId):
    # os.remove(파일삭제)
    # os.rmdir(폴더삭제 - 빈폴더만 삭제가능)
    path = settings.MEDIA_ROOT + "/" + str(borderId) + "/"
    if os.path.isdir(path):
        # dirList = os.listdir(path)
        # for f in dirList:
        #     os.remove(path + "/" + f)
        # os.rmdir(path)
        shutil.rmtree(path)

    Border.objects.get(id=borderId).delete()
    Reply.objects.filter(border_id=borderId).delete()
    content = {
        'borderId':borderId
    }
    return render(request, 'border/delete.html', content);

def add(request):
    if request.method == 'POST':
        now = datetime.now()
        border = Border()
        border.제목 = request.POST['title']
        border.video_url = request.POST.get('video_url')
        border.내용 = request.POST.get("context");
        border.작성자 = request.user.username;
        border.작성일 = now
        border.수정일 = now
        border.조회수 = 0
        border.save()

        file_upload(request, border.id);

        msg = "<script>";
        msg += "alert('게시글이 저장되었습니다.');";
        msg += f"location.href='/border/{border.id}/';";
        msg += "</script>";
        return HttpResponse(msg);
        # return redirect('BD', border.id)
        # return render(request, 'border/detail.html')
    else: # GET 방식
        if request.user.is_active:
            return render(request, 'border/add.html');
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
    return render(request, 'border/page.html', content);

def addreply(request, borderId):
    reply = Reply()
    reply.작성자 = request.user.username;
    reply.작성일 = datetime.now()
    reply.border_id = borderId
    reply.내용 = request.GET['reply']
    reply.save()
    Border.objects.filter(id=borderId).update(댓글수 = Reply.objects.filter(border_id=borderId).count())
    return redirect('BD:D', borderId)

def delreply(request, borderId, replyId):
    Reply.objects.get(id=replyId).delete()
    Border.objects.filter(id=borderId).update(댓글수 = Reply.objects.filter(border_id=borderId).count())
    return redirect('BD:D', borderId)


def file_upload(request, borderId):
    # 각 border.id 의 이름으로 폴더 생성
    dirName = str(borderId)
    path = settings.MEDIA_ROOT + "/" + dirName + "/"

    if not os.path.isdir(path):
        os.mkdir(path)

    for x in request.FILES.getlist("files"):
        upload_file = open(path + str(x), 'wb')
        for chunk in x.chunks():
            upload_file.write(chunk)

def good(request, borderId):
    border = Border.objects.get(id=borderId)
    border.좋아요 = border.좋아요 + 1
    border.save()

    return redirect('BD:D', borderId)

def hate(request, borderId):
    border = Border.objects.get(id=borderId)
    border.싫어요 = border.싫어요 + 1
    border.save()
    return redirect('BD:D', borderId)