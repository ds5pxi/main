from django.shortcuts import render, redirect, HttpResponse
from diet_q.models import Diet_q, Reply
from datetime import datetime
from django.core.paginator import Paginator
from django.db.models import Max, Min, Avg, Sum
import os
from django.conf import settings
import shutil

# Create your views here.
def index(request, page):
    diet_q = Diet_q.objects.all().order_by('-id')
    
    # Paginator(데이터, 분할할 데이터 수)
    paging = Paginator(diet_q, 10)
    
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
            'diet_q':paging.page(page),
            'page_num':page_num,
        }
    except:
        content = {
            'diet_q':paging.page(paging.num_pages),
            'page_num':page_num,
        }
    return render(request, 'QnA/diet_q/index.html', content);

def detail(request, diet_qId):
    # Diet_q.obejcts.get() : Diet_q의 class 객체
    # diet_q = Diet_q.objects.get(id=diet_qId);
    # diet_q.조회수 = diet_q.조회수 + 1;
    # diet_q.save()
    # diet_q.obejcts.values().get() : dict 형태
    if request.user.is_active :
        diet_q = Diet_q.objects.values().get(id=diet_qId);
        Diet_q.objects.filter(id=diet_qId).update(조회수 = diet_q['조회수'] + 1)
        # get(id=고유번호)
        # filter(컬럼명 = 값)
        reply = Reply.objects.filter(diet_q_id=diet_qId).values()
        
        try:
            dirList = os.listdir(settings.DIET_Q_MEDIA_ROOT + "/" + str(diet_qId))

            content = {
                'diet_q':diet_q,
                'reply':reply,
                'dirList':dirList,
            }
        except:
            content = {
                'diet_q':diet_q,
                'reply':reply,
            }
        return render(request, 'QnA/diet_q/detail.html', content);
    else:
        msg = "<script>";
        msg += "alert('로그인 후 사용 가능합니다.');"
        msg += "location.href='/account/login/';"
        msg += "</script>"
        return HttpResponse(msg);

def update(request, diet_qId):
    diet_q = Diet_q.objects.get(id=diet_qId)
    if request.method == 'GET':
        if request.user.is_active:
            if request.user.username == diet_q.작성자:
                try:
                    dirList = os.listdir(settings.DIET_Q_MEDIA_ROOT + "/" + str(diet_qId))
                    content = {
                        'diet_q':diet_q,
                        'dirList':dirList,
                    }
                except:
                    content = {
                        'diet_q':diet_q,
                    }
                return render(request, 'QnA/diet_q/update.html', content);
            else :
                msg = "<script>"
                msg += "alert('접근할 수 없는 URL 입니다.');"
                msg += "location.href='/diet_q/page/1';"
                msg += "</script>"
                return HttpResponse(msg);
        else :
            return render(request, 'error/errorAccess.html');
    elif request.method == "POST":
        diet_q.제목 = request.POST.get('title');
        diet_q.내용 = request.POST.get('content');
        diet_q.수정일 = datetime.now();
        diet_q.save()

        file_upload(request, diet_q.id);

        msg = "<script>"
        msg += f"alert('{ diet_q.id }번 게시글이 수정되었습니다.');"
        msg += f"location.href='/diet_q/{ diet_q.id }/';"
        msg += "</script>"
        return HttpResponse(msg);

def delete(request, diet_qId):
    # os.remove(파일삭제)
    # os.rmdir(폴더삭제 - 빈폴더만 삭제가능)
    path = settings.DIET_Q_MEDIA_ROOT + "/" + str(diet_qId) + "/"
    if os.path.isdir(path):
        # dirList = os.listdir(path)
        # for f in dirList:
        #     os.remove(path + "/" + f)
        # os.rmdir(path)
        shutil.rmtree(path)

    Diet_q.objects.get(id=diet_qId).delete()
    Reply.objects.filter(diet_q_id=diet_qId).delete()
    content = {
        'diet_qId':diet_qId
    }
    return render(request, 'QnA/diet_q/delete.html', content);

def add(request):
    if request.method == 'POST':
        now = datetime.now()
        diet_q = Diet_q()
        diet_q.제목 = request.POST['title']
        diet_q.내용 = request.POST.get("context");
        diet_q.작성자 = request.user.username;
        diet_q.작성일 = now
        diet_q.수정일 = now
        diet_q.조회수 = request.POST['vcount']
        diet_q.save()

        file_upload(request, diet_q.id);

        msg = "<script>";
        msg += "alert('게시글이 저장되었습니다.');";
        msg += f"location.href='/diet_q/{diet_q.id}/';";
        msg += "</script>";
        return HttpResponse(msg);
        # return redirect('DQ', diet_q.id)
        # return render(request, 'QnA/diet_q/detail.html')
    else: # GET 방식
        if request.user.is_active:
            return render(request, 'QnA/diet_q/add.html');
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
    return render(request, 'QnA/diet_q/page.html', content);

def addreply(request, diet_qId):
    reply = Reply()
    reply.작성자 = request.user.username;
    reply.작성일 = datetime.now()
    reply.diet_q_id = diet_qId
    reply.내용 = request.GET['reply']
    reply.save()
    Diet_q.objects.filter(id=diet_qId).update(댓글수 = Reply.objects.filter(diet_q_id=diet_qId).count())
    return redirect('DQ:D', diet_qId)

def delreply(request, diet_qId, replyId):
    Reply.objects.get(id=replyId).delete()
    Diet_q.objects.filter(id=diet_qId).update(댓글수 = Reply.objects.filter(diet_q_id=diet_qId).count())
    return redirect('DQ:D', diet_qId)


def file_upload(request, diet_qId):
    # 각 diet_q.id 의 이름으로 폴더 생성
    dirName = str(diet_qId)
    path = settings.DIET_Q_MEDIA_ROOT + "/" + dirName + "/"

    if not os.path.isdir(path):
        os.mkdir(path)

    for x in request.FILES.getlist("files"):
        upload_file = open(path + str(x), 'wb')
        for chunk in x.chunks():
            upload_file.write(chunk)

def good(request, diet_qId):
    diet_q = Diet_q.objects.get(id=diet_qId)
    diet_q.좋아요 = diet_q.좋아요 + 1
    diet_q.save()

    return redirect('DQ:D', diet_qId)

def hate(request, diet_qId):
    diet_q = Diet_q.objects.get(id=diet_qId)
    diet_q.싫어요 = diet_q.싫어요 + 1
    diet_q.save()
    return redirect('DQ:D', diet_qId)