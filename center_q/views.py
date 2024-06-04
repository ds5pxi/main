from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.urls import reverse
from center_q.models import Center_q, Reply
from datetime import datetime
from django.core.paginator import Paginator
from django.db.models import Max, Min, Avg, Sum
import os
from django.conf import settings
import shutil
from urllib import parse

# 파일 다운로드, 삭제
def download(request, center_qId, filename):
    file_path = os.path.join(settings.CENTER_Q_MEDIA_ROOT, center_qId + "/" + filename)
    
    # exists() : 파일이 있으면 True 없으면 False
    if os.path.exists(file_path):
        readFile = open(file_path, 'rb')
        response = HttpResponse(readFile.read())
        response['Content-Disposition']='attachment;filename='+parse.quote(filename)
        return response

def deleteFile(request, center_qId, filename):
    path = center_qId + "/" + filename
    file_path = os.path.join(settings.CENTER_Q_MEDIA_ROOT, path)
    os.remove(file_path)

    msg = "<script>"
    msg += f"alert('{filename} 파일을 삭제했습니다.');"
    msg += f"location.href='/center_q/{center_qId}/update/';";
    msg += "</script>"

    return HttpResponse(msg)

# Create your views here.
def index(request, page):
    query = request.GET.get('query', '')
    search_by = request.GET.get('search_by', 'title')

    if search_by == 'title':
        center_q = Center_q.objects.filter(제목__icontains=query)
    elif search_by == 'author':
        center_q = Center_q.objects.filter(작성자__icontains=query)
    elif search_by == 'content':
        center_q = Center_q.objects.filter(내용__icontains=query)
    else:
        center_q = Center_q.objects.all()

    center_q = center_q.order_by('-id')
    
    # Paginator(데이터, 분할할 데이터 수)
    paging = Paginator(center_q, 10)
    
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
            'center_q':paging.page(page),
            'page_num':page_num,
            'query': query,
            'search_by': search_by,
        }
    except:
        content = {
            'center_q':paging.page(paging.num_pages),
            'page_num':page_num,
            'query': query,
            'search_by': search_by,
        }
    return render(request, 'QnA/center_q/index.html', content);

def detail(request, center_qId):
    # Center_q.obejcts.get() : Center_q의 class 객체
    # center_q = Center_q.objects.get(id=center_qId);
    # center_q.조회수 = center_q.조회수 + 1;
    # center_q.save()
    # Center_q.obejcts.values().get() : dict 형태
    if request.user.is_active :
        video = get_object_or_404(Center_q, pk=center_qId)
        center_q = Center_q.objects.values().get(id=center_qId);
        Center_q.objects.filter(id=center_qId).update(조회수 = center_q['조회수'] + 1)
        # get(id=고유번호)
        # filter(컬럼명 = 값)
        reply = Reply.objects.filter(center_q_id=center_qId).values()
        
        try:
            dirList = os.listdir(settings.CENTER_Q_MEDIA_ROOT + "/" + str(center_qId))

            content = {
                'center_q':center_q,
                'reply':reply,
                'dirList':dirList,
                'video': video,
            }
        except:
            content = {
                'center_q':center_q,
                'reply':reply,
            }
        return render(request, 'QnA/center_q/detail.html', content);
    else:
        msg = "<script>";
        msg += "alert('로그인 후 사용 가능합니다.');"
        msg += "location.href='/account/login/';"
        msg += "</script>"
        return HttpResponse(msg);

def update(request, center_qId):
    center_q = Center_q.objects.get(id=center_qId)
    if request.method == 'GET':
        if request.user.is_active:
            if request.user.username == center_q.작성자:
                try:
                    dirList = os.listdir(settings.CENTER_Q_MEDIA_ROOT + "/" + str(center_qId))
                    content = {
                        'center_q':center_q,
                        'dirList':dirList,
                    }
                except:
                    content = {
                        'center_q':center_q,
                    }
                return render(request, 'QnA/center_q/update.html', content);
            else :
                msg = "<script>"
                msg += "alert('접근할 수 없는 URL 입니다.');"
                msg += "location.href='center_q/page/1';"
                msg += "</script>"
                return HttpResponse(msg);
        else :
            return render(request, 'error/errorAccess.html');
    elif request.method == "POST":
        center_q.제목 = request.POST.get('title');
        center_q.내용 = request.POST.get('content');
        center_q.video_url = request.POST.get('video_url');
        center_q.수정일 = datetime.now();
        center_q.save()

        file_upload(request, center_q.id);

        msg = "<script>"
        msg += f"alert('{ center_q.id }번 게시글이 수정되었습니다.');"
        msg += f"location.href='/center_q/{ center_q.id }/';"
        msg += "</script>"
        return HttpResponse(msg);

def delete(request, center_qId):
    # os.remove(파일삭제)
    # os.rmdir(폴더삭제 - 빈폴더만 삭제가능)
    path = settings.CENTER_Q_MEDIA_ROOT + "/" + str(center_qId) + "/"
    if os.path.isdir(path):
        # dirList = os.listdir(path)
        # for f in dirList:
        #     os.remove(path + "/" + f)
        # os.rmdir(path)
        shutil.rmtree(path)

    Center_q.objects.get(id=center_qId).delete()
    Reply.objects.filter(center_q_id=center_qId).delete()
    content = {
        'center_qId':center_qId
    }
    return render(request, 'QnA/center_q/delete.html', content);

def add(request):
    if request.method == 'POST':
        now = datetime.now()
        center_q = Center_q()
        center_q.제목 = request.POST['title']
        center_q.video_url = request.POST.get('video_url')
        center_q.내용 = request.POST.get("context");
        center_q.작성자 = request.user.username;
        center_q.작성일 = now
        center_q.수정일 = now
        center_q.조회수 = request.POST['vcount']
        center_q.save()

        file_upload(request, center_q.id);

        msg = "<script>";
        msg += "alert('게시글이 저장되었습니다.');";
        msg += f"location.href='/center_q/{center_q.id}/';";
        msg += "</script>";
        return HttpResponse(msg);
        # return redirect('CQ', center_q.id)
        # return render(request, 'QnA/center_q/detail.html')
    else: # GET 방식
        if request.user.is_active:
            return render(request, 'QnA/center_q/add.html');
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
    return render(request, 'QnA/center_q/page.html', content);

def addreply(request, center_qId):
    reply = Reply()
    reply.작성자 = request.user.username;
    reply.작성일 = datetime.now()
    reply.center_q_id = center_qId
    reply.내용 = request.GET['reply']
    reply.save()
    Center_q.objects.filter(id=center_qId).update(댓글수 = Reply.objects.filter(center_q_id=center_qId).count())
    return redirect('CQ:D', center_qId)

def delreply(request, center_qId, replyId):
    Reply.objects.get(id=replyId).delete()
    Center_q.objects.filter(id=center_qId).update(댓글수 = Reply.objects.filter(center_q_id=center_qId).count())
    return redirect('CQ:D', center_qId)


def file_upload(request, center_qId):
    # 각 center_q.id 의 이름으로 폴더 생성
    dirName = str(center_qId)
    path = settings.CENTER_Q_MEDIA_ROOT + "/" + dirName + "/"

    if not os.path.isdir(path):
        os.mkdir(path)

    for x in request.FILES.getlist("files"):
        upload_file = open(path + str(x), 'wb')
        for chunk in x.chunks():
            upload_file.write(chunk)

def good(request, center_qId):
    center_q = Center_q.objects.get(id=center_qId)
    center_q.좋아요 = center_q.좋아요 + 1
    center_q.save()

    return redirect('CQ:D', center_qId)

def hate(request, center_qId):
    center_q = Center_q.objects.get(id=center_qId)
    center_q.싫어요 = center_q.싫어요 + 1
    center_q.save()
    return redirect('CQ:D', center_qId)