from django.shortcuts import render, redirect, HttpResponse
from workout_q.models import Workout_q, Reply
from datetime import datetime
from django.core.paginator import Paginator
from django.db.models import Max, Min, Avg, Sum
import os
from django.conf import settings
import shutil

# Create your views here.
def index(request, page):
    query = request.GET.get('query', '')
    search_by = request.GET.get('search_by', 'title')

    if search_by == 'title':
        workout_q = Workout_q.objects.filter(제목__icontains=query)
    elif search_by == 'author':
        workout_q = Workout_q.objects.filter(작성자__icontains=query)
    elif search_by == 'content':
        workout_q = Workout_q.objects.filter(내용__icontains=query)
    else:
        workout_q = Workout_q.objects.all()

    workout_q = workout_q.order_by('-id')

    # Paginator(데이터, 분할할 데이터 수)
    paging = Paginator(workout_q, 10)
    
    str_page = str(page)
    # 맨 마지막 숫자
    last = int(str_page[-1])
    first = int(str_page[:-1] + '1')

    if last == 0:
        max = first
        first = max - 10
    elif first + 10 > paging.num_pages:
        max = paging.num_pages + 1
    else:
        max = first + 10
    page_num = range(first, max)

    try:
        content = {
            'workout_q': paging.page(page),
            'page_num': page_num,
            'query': query,
            'search_by': search_by,
        }
    except:
        content = {
            'workout_q': paging.page(paging.num_pages),
            'page_num': page_num,
            'query': query,
            'search_by': search_by,
        }
    return render(request, 'QnA/workout_q/index.html', content)

def detail(request, workout_qId):
    if request.user.is_active:
        workout_q = Workout_q.objects.values().get(id=workout_qId)
        Workout_q.objects.filter(id=workout_qId).update(조회수=workout_q['조회수'] + 1)
        reply = Reply.objects.filter(workout_q_id=workout_qId).values()

        try:
            dirList = os.listdir(settings.WORKOUT_Q_MEDIA_ROOT + "/" + str(workout_qId))

            content = {
                'workout_q': workout_q,
                'reply': reply,
                'dirList': dirList,
            }
        except:
            content = {
                'workout_q': workout_q,
                'reply': reply,
            }
        return render(request, 'QnA/workout_q/detail.html', content)
    else:
        msg = "<script>"
        msg += "alert('로그인 후 사용 가능합니다.');"
        msg += "location.href='/account/login/';"
        msg += "</script>"
        return HttpResponse(msg)

def update(request, workout_qId):
    workout_q = Workout_q.objects.get(id=workout_qId)
    if request.method == 'GET':
        if request.user.is_active:
            if request.user.username == workout_q.작성자:
                try:
                    dirList = os.listdir(settings.WORKOUT_Q_MEDIA_ROOT + "/" + str(workout_qId))
                    content = {
                        'workout_q': workout_q,
                        'dirList': dirList,
                    }
                except:
                    content = {
                        'workout_q': workout_q,
                    }
                return render(request, 'QnA/workout_q/update.html', content)
            else:
                msg = "<script>"
                msg += "alert('접근할 수 없는 URL 입니다.');"
                msg += "location.href='/workout_q/page/1';"
                msg += "</script>"
                return HttpResponse(msg)
        else:
            return render(request, 'error/errorAccess.html')
    elif request.method == "POST":
        workout_q.제목 = request.POST.get('title')
        workout_q.내용 = request.POST.get('content')
        workout_q.수정일 = datetime.now()
        workout_q.save()

        file_upload(request, workout_q.id)

        msg = "<script>"
        msg += f"alert('{ workout_q.id }번 게시글이 수정되었습니다.');"
        msg += f"location.href='/workout_q/{ workout_q.id }/';"
        msg += "</script>"
        return HttpResponse(msg)

def delete(request, workout_qId):
    path = settings.WORKOUT_Q_MEDIA_ROOT + "/" + str(workout_qId) + "/"
    if os.path.isdir(path):
        shutil.rmtree(path)

    Workout_q.objects.get(id=workout_qId).delete()
    Reply.objects.filter(workout_q_id=workout_qId).delete()
    content = {
        'workout_qId': workout_qId
    }
    return render(request, 'QnA/workout_q/delete.html', content)

def add(request):
    if request.method == 'POST':
        now = datetime.now()
        workout_q = Workout_q()
        workout_q.제목 = request.POST['title']
        workout_q.내용 = request.POST.get("context")
        workout_q.작성자 = request.user.username
        workout_q.작성일 = now
        workout_q.수정일 = now
        workout_q.조회수 = request.POST['vcount']
        workout_q.save()

        file_upload(request, workout_q.id)

        msg = "<script>"
        msg += "alert('게시글이 저장되었습니다.');"
        msg += f"location.href='/workout_q/{workout_q.id}/';"
        msg += "</script>"
        return HttpResponse(msg)
    else:
        if request.user.is_active:
            return render(request, 'QnA/workout_q/add.html')
        else:
            msg = "<script>"
            msg += "alert('로그인 후 이용이 가능합니다.');"
            msg += "location.href='/account/login/';"
            msg += "</script>"
            return HttpResponse(msg)

def page(request, page):
    content = {
        'page': page,
    }
    return render(request, 'QnA/workout_q/page.html', content)

def addreply(request, workout_qId):
    reply = Reply()
    reply.작성자 = request.user.username
    reply.작성일 = datetime.now()
    reply.workout_q_id = workout_qId
    reply.내용 = request.GET['reply']
    reply.save()
    Workout_q.objects.filter(id=workout_qId).update(댓글수=Reply.objects.filter(workout_q_id=workout_qId).count())
    return redirect('WQ:D', workout_qId)

def delreply(request, workout_qId, replyId):
    Reply.objects.get(id=replyId).delete()
    Workout_q.objects.filter(id=workout_qId).update(댓글수=Reply.objects.filter(workout_q_id=workout_qId).count())
    return redirect('WQ:D', workout_qId)

def file_upload(request, workout_qId):
    dirName = str(workout_qId)
    path = settings.WORKOUT_Q_MEDIA_ROOT + "/" + dirName + "/"

    if not os.path.isdir(path):
        os.mkdir(path)

    for x in request.FILES.getlist("files"):
        upload_file = open(path + str(x), 'wb')
        for chunk in x.chunks():
            upload_file.write(chunk)

def good(request, workout_qId):
    workout_q = Workout_q.objects.get(id=workout_qId)
    workout_q.좋아요 = workout_q.좋아요 + 1
    workout_q.save()
    return redirect('WQ:D', workout_qId)

def hate(request, workout_qId):
    workout_q = Workout_q.objects.get(id=workout_qId)
    workout_q.싫어요 = workout_q.싫어요 + 1
    workout_q.save()
    return redirect('WQ:D', workout_qId)