from django.shortcuts import render, redirect, HttpResponse
from advice.models import Advice, Reply
from datetime import datetime
from django.core.paginator import Paginator
from django.db.models import Max, Min, Avg, Sum, Q
import os
from django.conf import settings
import shutil
from django.contrib import messages
from urllib import parse

# 파일 다운로드, 삭제
def download(request, adviceId, filename):
    file_path = os.path.join(settings.ADVICE_MEDIA_ROOT, adviceId + "/" + filename)
    
    # exists() : 파일이 있으면 True 없으면 False
    if os.path.exists(file_path):
        readFile = open(file_path, 'rb')
        response = HttpResponse(readFile.read())
        response['Content-Disposition']='attachment;filename='+parse.quote(filename)
        return response

def deleteFile(request, adviceId, filename):
    path = adviceId + "/" + filename
    file_path = os.path.join(settings.ADVICE_MEDIA_ROOT, path)
    os.remove(file_path)

    msg = "<script>"
    msg += f"alert('{filename} 파일을 삭제했습니다.');"
    msg += f"location.href='/advice/{adviceId}/update/';";
    msg += "</script>"

    return HttpResponse(msg)


# Create your views here.
def index(request, page):
    query = request.GET.get('query', '')
    search_by = request.GET.get('search_by', 'title')

    if search_by == 'title':
        advice = Advice.objects.filter(제목__icontains=query)
    elif search_by == 'author':
        advice = Advice.objects.filter(작성자__icontains=query)
    elif search_by == 'content':
        advice = Advice.objects.filter(내용__icontains=query)
    else:
        advice = Advice.objects.all()

    advice = advice.order_by('-id')

    
    # Paginator(데이터, 분할할 데이터 수)
    paging = Paginator(advice, 10)
    
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
            'advice':paging.page(page),
            'page_num':page_num,
        }
    except:
        content = {
            'advice':paging.page(paging.num_pages),
            'page_num':page_num,
        }
    return render(request, 'community/advice/index.html', content);

def detail(request, adviceId):
    # advice.obejcts.get() : advice의 class 객체
    # advice = advice.objects.get(id=adviceId);
    # advice.조회수 = advice.조회수 + 1;
    # advice.save()
    # advice.obejcts.values().get() : dict 형태
    if request.user.is_active :
        advice = Advice.objects.values().get(id=adviceId);
        Advice.objects.filter(id=adviceId).update(조회수 = advice['조회수'] + 1)
        # get(id=고유번호)
        # filter(컬럼명 = 값)
        reply = Reply.objects.filter(advice_id=adviceId).values()
        
        try:
            dirList = os.listdir(settings.ADVICE_MEDIA_ROOT + "/" + str(adviceId))

            content = {
                'advice':advice,
                'reply':reply,
                'dirList':dirList,
            }
        except:
            content = {
                'advice':advice,
                'reply':reply,
            }
        return render(request, 'community/advice/detail.html', content);
    else:
        msg = "<script>";
        msg += "alert('로그인 후 사용 가능합니다.');"
        msg += "location.href='/account/login/';"
        msg += "</script>"
        return HttpResponse(msg);

def update(request, adviceId):
    advice = Advice.objects.get(id=adviceId)
    if request.method == 'GET':
        if request.user.is_active:
            if request.user.username == advice.작성자:
                try:
                    dirList = os.listdir(settings.ADVICE_MEDIA_ROOT + "/" + str(adviceId))
                    content = {
                        'advice':advice,
                        'dirList':dirList,
                    }
                except:
                    content = {
                        'advice':advice,
                    }
                return render(request, 'community/advice/update.html', content);
            else :
                msg = "<script>"
                msg += "alert('접근할 수 없는 URL 입니다.');"
                msg += "location.href='/advice/page/1';"
                msg += "</script>"
                return HttpResponse(msg);
        else :
            return render(request, 'error/errorAccess.html');
    elif request.method == "POST":
        advice.제목 = request.POST.get('title');
        advice.내용 = request.POST.get('content');
        advice.수정일 = datetime.now();
        advice.save()

        file_upload(request, advice.id);

        msg = "<script>"
        msg += f"alert('{ advice.id }번 게시글이 수정되었습니다.');"
        msg += f"location.href='/advice/{ advice.id }/';"
        msg += "</script>"
        return HttpResponse(msg);

def delete(request, adviceId):
    # os.remove(파일삭제)
    # os.rmdir(폴더삭제 - 빈폴더만 삭제가능)
    path = settings.ADVICE_MEDIA_ROOT + "/" + str(adviceId) + "/"
    if os.path.isdir(path):
        # dirList = os.listdir(path)
        # for f in dirList:
        #     os.remove(path + "/" + f)
        # os.rmdir(path)
        shutil.rmtree(path)

    Advice.objects.get(id=adviceId).delete()
    Reply.objects.filter(advice_id=adviceId).delete()
    content = {
        'adviceId':adviceId
    }
    return render(request, 'community/advice/delete.html', content);

def add(request):
    if request.method == 'POST':
        now = datetime.now()
        advice = Advice()
        advice.제목 = request.POST['title']
        advice.내용 = request.POST.get("context");
        advice.작성자 = request.user.username;
        advice.작성일 = now
        advice.수정일 = now
        advice.조회수 = request.POST['vcount']
        advice.save()

        file_upload(request, advice.id);

        msg = "<script>";
        msg += "alert('게시글이 저장되었습니다.');";
        msg += f"location.href='/advice/{advice.id}/';";
        msg += "</script>";
        return HttpResponse(msg);
        # return redirect('AD', advice.id)
        # return render(request, 'community/advice/detail.html')
    else: # GET 방식
        if request.user.is_active:
            return render(request, 'community/advice/add.html');
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
    return render(request, 'community/advice/page.html', content);

def addreply(request, adviceId):
    reply = Reply()
    reply.작성자 = request.user.username;
    reply.작성일 = datetime.now()
    reply.advice_id = adviceId
    reply.내용 = request.GET['reply']
    reply.save()
    Advice.objects.filter(id=adviceId).update(댓글수 = Reply.objects.filter(advice_id=adviceId).count())
    return redirect('AD:D', adviceId)

def delreply(request, adviceId, replyId):
    Reply.objects.get(id=replyId).delete()
    Advice.objects.filter(id=adviceId).update(댓글수 = Reply.objects.filter(advice_id=adviceId).count())
    return redirect('AD:D', adviceId)


def file_upload(request, adviceId):
    # 각 advice.id 의 이름으로 폴더 생성
    dirName = str(adviceId)
    path = settings.ADVICE_MEDIA_ROOT + "/" + dirName + "/"

    if not os.path.isdir(path):
        os.mkdir(path)

    for x in request.FILES.getlist("files"):
        upload_file = open(path + str(x), 'wb')
        for chunk in x.chunks():
            upload_file.write(chunk)

def good(request, adviceId):
    advice = Advice.objects.get(id=adviceId)
    advice.좋아요 = advice.좋아요 + 1
    advice.save()

    return redirect('AD:D', adviceId)

def hate(request, adviceId):
    advice = Advice.objects.get(id=adviceId)
    advice.싫어요 = advice.싫어요 + 1
    advice.save()
    return redirect('AD:D', adviceId)