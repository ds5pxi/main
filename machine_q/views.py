from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.urls import reverse
from machine_q.models import Machine_q, Reply
from datetime import datetime
from django.core.paginator import Paginator
from django.db.models import Max, Min, Avg, Sum
import os
from django.conf import settings
import shutil
from urllib import parse

# 파일 다운로드, 삭제
def download(request, machine_qId, filename):
    file_path = os.path.join(settings.MACHINE_Q_MEDIA_ROOT, machine_qId + "/" + filename)
    
    # exists() : 파일이 있으면 True 없으면 False
    if os.path.exists(file_path):
        readFile = open(file_path, 'rb')
        response = HttpResponse(readFile.read())
        response['Content-Disposition']='attachment;filename='+parse.quote(filename)
        return response

def deleteFile(request, machine_qId, filename):
    path = machine_qId + "/" + filename
    file_path = os.path.join(settings.MACHINE_Q_MEDIA_ROOT, path)
    os.remove(file_path)

    msg = "<script>"
    msg += f"alert('{filename} 파일을 삭제했습니다.');"
    msg += f"location.href='/machine_q/{machine_qId}/update/';";
    msg += "</script>"

    return HttpResponse(msg)

# Create your views here.
def index(request, page):
    query = request.GET.get('query', '')
    search_by = request.GET.get('search_by', 'title')
    post_by = request.GET.get('post_by', 'present')

    if search_by == 'title':
        machine_q = Machine_q.objects.filter(제목__icontains=query)
    elif search_by == 'author':
        machine_q = Machine_q.objects.filter(작성자__icontains=query)
    elif search_by == 'content':
        machine_q = Machine_q.objects.filter(내용__icontains=query)
    else:
        machine_q = Machine_q.objects.all()

    if post_by == 'present' :
        machine_q = machine_q.order_by('-id')
    elif post_by == 'like' :
        machine_q = machine_q.order_by('-좋아요','-id')

    best_border = Machine_q.objects.order_by("-좋아요")
    
    # Paginator(데이터, 분할할 데이터 수)
    paging = Paginator(machine_q, 8)
    
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
            'machine_q':paging.page(page),
            'page_num':page_num,
            'query': query,
            'search_by': search_by,
            'best_border':best_border,
        }
    except:
        content = {
            'machine_q':paging.page(paging.num_pages),
            'page_num':page_num,
            'query': query,
            'search_by': search_by,
            'best_border':best_border,
        }
    return render(request, 'QnA/machine_q/index.html', content);

def detail(request, machine_qId):
    if request.user.is_active :
        video = get_object_or_404(Machine_q, pk=machine_qId)
        machine_q = Machine_q.objects.values().get(id=machine_qId);
        Machine_q.objects.filter(id=machine_qId).update(조회수 = machine_q['조회수'] + 1)
        reply = Reply.objects.filter(machine_q_id=machine_qId).values()
        
        try:
            dirList = os.listdir(settings.MACHINE_Q_MEDIA_ROOT + "/" + str(machine_qId))

            content = {
                'machine_q':machine_q,
                'reply':reply,
                'dirList':dirList,
                'video': video,
            }
        except:
            content = {
                'machine_q':machine_q,
                'reply':reply,
            }
        return render(request, 'QnA/machine_q/detail.html', content);
    else:
        msg = "<script>";
        msg += "alert('로그인 후 사용 가능합니다.');"
        msg += "location.href='/account/login/';"
        msg += "</script>"
        return HttpResponse(msg);

def update(request, machine_qId):
    machine_q = Machine_q.objects.get(id=machine_qId)
    if request.method == 'GET':
        if request.user.is_active:
            if request.user.username == machine_q.작성자:
                try:
                    dirList = os.listdir(settings.MACHINE_Q_MEDIA_ROOT + "/" + str(machine_qId))
                    content = {
                        'machine_q':machine_q,
                        'dirList':dirList,
                    }
                except:
                    content = {
                        'machine_q':machine_q,
                    }
                return render(request, 'QnA/machine_q/update.html', content);
            else :
                msg = "<script>"
                msg += "alert('접근할 수 없는 URL 입니다.');"
                msg += "location.href='/machine_q/page/1';"
                msg += "</script>"
                return HttpResponse(msg);
        else :
            return render(request, 'error/errorAccess.html');
    elif request.method == "POST":
        machine_q.제목 = request.POST.get('title');
        machine_q.내용 = request.POST.get('content');
        machine_q.video_url = request.POST.get('video_url');
        machine_q.수정일 = datetime.now();
        machine_q.save()

        file_upload(request, machine_q.id);

        msg = "<script>"
        msg += f"alert('{ machine_q.id }번 게시글이 수정되었습니다.');"
        msg += f"location.href='/machine_q/{ machine_q.id }/';"
        msg += "</script>"
        return HttpResponse(msg);

def delete(request, machine_qId):
    # os.remove(파일삭제)
    # os.rmdir(폴더삭제 - 빈폴더만 삭제가능)
    path = settings.MACHINE_Q_MEDIA_ROOT + "/" + str(machine_qId) + "/"
    if os.path.isdir(path):
        # dirList = os.listdir(path)
        # for f in dirList:
        #     os.remove(path + "/" + f)
        # os.rmdir(path)
        shutil.rmtree(path)

    Machine_q.objects.get(id=machine_qId).delete()
    Reply.objects.filter(machine_q_id=machine_qId).delete()
    content = {
        'machine_qId':machine_qId
    }
    return render(request, 'QnA/machine_q/delete.html', content);

def add(request):
    if request.method == 'POST':
        now = datetime.now()
        machine_q = Machine_q()
        machine_q.제목 = request.POST['title']
        machine_q.video_url = request.POST.get('video_url')
        machine_q.내용 = request.POST.get("context");
        machine_q.작성자 = request.user.username;
        machine_q.작성일 = now
        machine_q.수정일 = now
        machine_q.조회수 = 0
        machine_q.save()

        file_upload(request, machine_q.id);

        msg = "<script>";
        msg += "alert('게시글이 저장되었습니다.');";
        msg += f"location.href='/machine_q/{machine_q.id}/';";
        msg += "</script>";
        return HttpResponse(msg);
        # return redirect('MQ', machine_q.id)
        # return render(request, 'QnA/machine_q/detail.html')
    else: # GET 방식
        if request.user.is_active:
            return render(request, 'QnA/machine_q/add.html');
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
    return render(request, 'QnA/machine_q/page.html', content);

def addreply(request, machine_qId):
    reply = Reply()
    reply.작성자 = request.user.username;
    reply.작성일 = datetime.now()
    reply.machine_q_id = machine_qId
    reply.내용 = request.GET['reply']
    reply.save()
    Machine_q.objects.filter(id=machine_qId).update(댓글수 = Reply.objects.filter(machine_q_id=machine_qId).count())
    return redirect('MQ:D', machine_qId)

def delreply(request, machine_qId, replyId):
    Reply.objects.get(id=replyId).delete()
    Machine_q.objects.filter(id=machine_qId).update(댓글수 = Reply.objects.filter(machine_q_id=machine_qId).count())
    return redirect('MQ:D', machine_qId)


def file_upload(request, machine_qId):
    # 각 machine_q.id 의 이름으로 폴더 생성
    dirName = str(machine_qId)
    path = settings.MACHINE_Q_MEDIA_ROOT + "/" + dirName + "/"

    if not os.path.isdir(path):
        os.mkdir(path)

    for x in request.FILES.getlist("files"):
        upload_file = open(path + str(x), 'wb')
        for chunk in x.chunks():
            upload_file.write(chunk)

def good(request, machine_qId):
    machine_q = Machine_q.objects.get(id=machine_qId)
    machine_q.좋아요 = machine_q.좋아요 + 1
    machine_q.save()

    return redirect('MQ:D', machine_qId)

def hate(request, machine_qId):
    machine_q = Machine_q.objects.get(id=machine_qId)
    machine_q.싫어요 = machine_q.싫어요 + 1
    machine_q.save()
    return redirect('MQ:D', machine_qId)