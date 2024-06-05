from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.urls import reverse
from else_q.models import Else_q, Reply
from datetime import datetime
from django.core.paginator import Paginator
from django.db.models import Max, Min, Avg, Sum
import os
from django.conf import settings
import shutil
from urllib import parse

# 파일 다운로드, 삭제
def download(request, else_qId, filename):
    file_path = os.path.join(settings.ELSE_Q_MEDIA_ROOT, else_qId + "/" + filename)
    
    # exists() : 파일이 있으면 True 없으면 False
    if os.path.exists(file_path):
        readFile = open(file_path, 'rb')
        response = HttpResponse(readFile.read())
        response['Content-Disposition']='attachment;filename='+parse.quote(filename)
        return response

def deleteFile(request, else_qId, filename):
    path = else_qId + "/" + filename
    file_path = os.path.join(settings.ELSE_Q_MEDIA_ROOT, path)
    os.remove(file_path)

    msg = "<script>"
    msg += f"alert('{filename} 파일을 삭제했습니다.');"
    msg += f"location.href='/else_q/{else_qId}/update/';";
    msg += "</script>"

    return HttpResponse(msg)

# Create your views here.
def index(request, page):
    query = request.GET.get('query', '')
    search_by = request.GET.get('search_by', 'title')
    post_by = request.GET.get('post_by', 'present')

    if search_by == 'title':
        else_q = Else_q.objects.filter(제목__icontains=query)
    elif search_by == 'author':
        else_q = Else_q.objects.filter(작성자__icontains=query)
    elif search_by == 'content':
        else_q = Else_q.objects.filter(내용__icontains=query)
    else:
        else_q = Else_q.objects.all()

    if post_by == 'present' :
        else_q = else_q.order_by('-id')
    elif post_by == 'like' :
        else_q = else_q.order_by('-좋아요','-id')

    best_border = Else_q.objects.order_by("-좋아요")
    
    # Paginator(데이터, 분할할 데이터 수)
    paging = Paginator(else_q, 8)
    
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
            'else_q':paging.page(page),
            'page_num':page_num,
            'query': query,
            'search_by': search_by,
            'best_border':best_border,
        }
    except:
        content = {
            'else_q':paging.page(paging.num_pages),
            'page_num':page_num,
            'query': query,
            'search_by': search_by,
            'best_border':best_border,
        }
    return render(request, 'QnA/else_q/index.html', content);

def detail(request, else_qId):

    if request.user.is_active :
        video = get_object_or_404(Else_q, pk=else_qId)
        else_q = Else_q.objects.values().get(id=else_qId);
        Else_q.objects.filter(id=else_qId).update(조회수 = else_q['조회수'] + 1)
        reply = Reply.objects.filter(else_q_id=else_qId).values()
        
        try:
            dirList = os.listdir(settings.ELSE_Q_MEDIA_ROOT + "/" + str(else_qId))

            content = {
                'else_q':else_q,
                'reply':reply,
                'dirList':dirList,
                'video': video,
            }
        except:
            content = {
                'else_q':else_q,
                'reply':reply,
            }
        return render(request, 'QnA/else_q/detail.html', content);
    else:
        msg = "<script>";
        msg += "alert('로그인 후 사용 가능합니다.');"
        msg += "location.href='/account/login/';"
        msg += "</script>"
        return HttpResponse(msg);

def update(request, else_qId):
    else_q = Else_q.objects.get(id=else_qId)
    if request.method == 'GET':
        if request.user.is_active:
            if request.user.username == else_q.작성자:
                try:
                    dirList = os.listdir(settings.ELSE_Q_MEDIA_ROOT + "/" + str(else_qId))
                    content = {
                        'else_q':else_q,
                        'dirList':dirList,
                    }
                except:
                    content = {
                        'else_q':else_q,
                    }
                return render(request, 'QnA/else_q/update.html', content);
            else :
                msg = "<script>"
                msg += "alert('접근할 수 없는 URL 입니다.');"
                msg += "location.href='/else_q/page/1';"
                msg += "</script>"
                return HttpResponse(msg);
        else :
            return render(request, 'error/errorAccess.html');
    elif request.method == "POST":
        else_q.제목 = request.POST.get('title');
        else_q.내용 = request.POST.get('content');
        else_q.video_url = request.POST.get('video_url');
        else_q.수정일 = datetime.now();
        else_q.save()

        file_upload(request, else_q.id);

        msg = "<script>"
        msg += f"alert('{ else_q.id }번 게시글이 수정되었습니다.');"
        msg += f"location.href='/else_q/{ else_q.id }/';"
        msg += "</script>"
        return HttpResponse(msg);

def delete(request, else_qId):
    # os.remove(파일삭제)
    # os.rmdir(폴더삭제 - 빈폴더만 삭제가능)
    path = settings.ELSE_Q_MEDIA_ROOT + "/" + str(else_qId) + "/"
    if os.path.isdir(path):
        # dirList = os.listdir(path)
        # for f in dirList:
        #     os.remove(path + "/" + f)
        # os.rmdir(path)
        shutil.rmtree(path)

    Else_q.objects.get(id=else_qId).delete()
    Reply.objects.filter(else_q_id=else_qId).delete()
    content = {
        'else_qId':else_qId
    }
    return render(request, 'QnA/else_q/delete.html', content);

def add(request):
    if request.method == 'POST':
        now = datetime.now()
        else_q = Else_q()
        else_q.제목 = request.POST['title']
        else_q.video_url = request.POST.get('video_url')
        else_q.내용 = request.POST.get("context");
        else_q.작성자 = request.user.username;
        else_q.작성일 = now
        else_q.수정일 = now
        else_q.조회수 = request.POST['vcount']
        else_q.save()

        file_upload(request, else_q.id);

        msg = "<script>";
        msg += "alert('게시글이 저장되었습니다.');";
        msg += f"location.href='/else_q/{else_q.id}/';";
        msg += "</script>";
        return HttpResponse(msg);
        # return redirect('EQ', else_q.id)
        # return render(request, 'QnA/else_q/detail.html')
    else: # GET 방식
        if request.user.is_active:
            return render(request, 'QnA/else_q/add.html');
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
    return render(request, 'QnA/else_q/page.html', content);

def addreply(request, else_qId):
    reply = Reply()
    reply.작성자 = request.user.username;
    reply.작성일 = datetime.now()
    reply.else_q_id = else_qId
    reply.내용 = request.GET['reply']
    reply.save()
    Else_q.objects.filter(id=else_qId).update(댓글수 = Reply.objects.filter(else_q_id=else_qId).count())
    return redirect('EQ:D', else_qId)

def delreply(request, else_qId, replyId):
    Reply.objects.get(id=replyId).delete()
    Else_q.objects.filter(id=else_qId).update(댓글수 = Reply.objects.filter(else_q_id=else_qId).count())
    return redirect('EQ:D', else_qId)


def file_upload(request, else_qId):
    # 각 else_q.id 의 이름으로 폴더 생성
    dirName = str(else_qId)
    path = settings.ELSE_Q_MEDIA_ROOT + "/" + dirName + "/"

    if not os.path.isdir(path):
        os.mkdir(path)

    for x in request.FILES.getlist("files"):
        upload_file = open(path + str(x), 'wb')
        for chunk in x.chunks():
            upload_file.write(chunk)

def good(request, else_qId):
    else_q = Else_q.objects.get(id=else_qId)
    else_q.좋아요 = else_q.좋아요 + 1
    else_q.save()

    return redirect('EQ:D', else_qId)

def hate(request, else_qId):
    else_q = Else_q.objects.get(id=else_qId)
    else_q.싫어요 = else_q.싫어요 + 1
    else_q.save()
    return redirect('EQ:D', else_qId)