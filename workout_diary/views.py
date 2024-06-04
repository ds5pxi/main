from django.shortcuts import render, redirect, HttpResponse
from workout_diary.models import Workout_diary, Reply
from datetime import datetime
from django.core.paginator import Paginator
from django.db.models import Max, Min, Avg, Sum, Q
import os
from django.conf import settings
import shutil
from django.contrib import messages
from urllib import parse

# 파일 다운로드, 삭제
def download(request, workout_diaryId, filename):
    file_path = os.path.join(settings.WORKOUT_DIARY_MEDIA_ROOT, workout_diaryId + "/" + filename)
    
    # exists() : 파일이 있으면 True 없으면 False
    if os.path.exists(file_path):
        readFile = open(file_path, 'rb')
        response = HttpResponse(readFile.read())
        response['Content-Disposition']='attachment;filename='+parse.quote(filename)
        return response

def deleteFile(request, workout_diaryId, filename):
    path = workout_diaryId + "/" + filename
    file_path = os.path.join(settings.WORKOUT_DIARY_MEDIA_ROOT, path)
    os.remove(file_path)

    msg = "<script>"
    msg += f"alert('{filename} 파일을 삭제했습니다.');"
    msg += f"location.href='/workout_diary/{workout_diaryId}/update/';";
    msg += "</script>"

    return HttpResponse(msg)

# Create your views here.
def index(request, page):
    query = request.GET.get('query', '')
    search_by = request.GET.get('search_by', 'title')

    if search_by == 'title':
        workout_diary = Workout_diary.objects.filter(제목__icontains=query)
    elif search_by == 'author':
        workout_diary = Workout_diary.objects.filter(작성자__icontains=query)
    elif search_by == 'content':
        workout_diary = Workout_diary.objects.filter(내용__icontains=query)
    else:
        workout_diary = Workout_diary.objects.all()

    workout_diary = workout_diary.order_by('-id')
    
    # Paginator(데이터, 분할할 데이터 수)
    paging = Paginator(workout_diary, 8)
    
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
            'workout_diary':paging.page(page),
            'page_num':page_num,
        }
    except:
        content = {
            'workout_diary':paging.page(paging.num_pages),
            'page_num':page_num,
        }
    return render(request, 'community/workout_diary/index.html', content);

def detail(request, workout_diaryId):
    # workout_diary.obejcts.get() : workout_diary의 class 객체
    # workout_diary = workout_diary.objects.get(id=workout_diaryId);
    # workout_diary.조회수 = workout_diary.조회수 + 1;
    # workout_diary.save()
    # workout_diary.obejcts.values().get() : dict 형태
    if request.user.is_active :
        workout_diary = Workout_diary.objects.values().get(id=workout_diaryId);
        Workout_diary.objects.filter(id=workout_diaryId).update(조회수 = workout_diary['조회수'] + 1)
        # get(id=고유번호)
        # filter(컬럼명 = 값)
        reply = Reply.objects.filter(workout_diary_id=workout_diaryId).values()
        
        try:
            dirList = os.listdir(settings.WORKOUT_DIARY_MEDIA_ROOT + "/" + str(workout_diaryId))

            content = {
                'workout_diary':workout_diary,
                'reply':reply,
                'dirList':dirList,
            }
        except:
            content = {
                'workout_diary':workout_diary,
                'reply':reply,
            }
        return render(request, 'community/workout_diary/detail.html', content);
    else:
        msg = "<script>";
        msg += "alert('로그인 후 사용 가능합니다.');"
        msg += "location.href='/account/login/';"
        msg += "</script>"
        return HttpResponse(msg);

def update(request, workout_diaryId):
    workout_diary = Workout_diary.objects.get(id=workout_diaryId)
    if request.method == 'GET':
        if request.user.is_active:
            if request.user.username == workout_diary.작성자:
                try:
                    dirList = os.listdir(settings.WORKOUT_DIARY_MEDIA_ROOT + "/" + str(workout_diaryId))
                    content = {
                        'workout_diary':workout_diary,
                        'dirList':dirList,
                    }
                except:
                    content = {
                        'workout_diary':workout_diary,
                    }
                return render(request, 'community/workout_diary/update.html', content);
            else :
                msg = "<script>"
                msg += "alert('접근할 수 없는 URL 입니다.');"
                msg += "location.href='/workout_diary/page/1';"
                msg += "</script>"
                return HttpResponse(msg);
        else :
            return render(request, 'error/errorAccess.html');
    elif request.method == "POST":
        workout_diary.제목 = request.POST.get('title');
        workout_diary.내용 = request.POST.get('content');
        workout_diary.수정일 = datetime.now();
        workout_diary.save()

        file_upload(request, workout_diary.id);

        msg = "<script>"
        msg += f"alert('{ workout_diary.id }번 게시글이 수정되었습니다.');"
        msg += f"location.href='/workout_diary/{ workout_diary.id }/';"
        msg += "</script>"
        return HttpResponse(msg);

def delete(request, workout_diaryId):
    # os.remove(파일삭제)
    # os.rmdir(폴더삭제 - 빈폴더만 삭제가능)
    path = settings.WORKOUT_DIARY_MEDIA_ROOT + "/" + str(workout_diaryId) + "/"
    if os.path.isdir(path):
        # dirList = os.listdir(path)
        # for f in dirList:
        #     os.remove(path + "/" + f)
        # os.rmdir(path)
        shutil.rmtree(path)

    Workout_diary.objects.get(id=workout_diaryId).delete()
    Reply.objects.filter(workout_diary_id=workout_diaryId).delete()
    content = {
        'workout_diaryId':workout_diaryId
    }
    return render(request, 'community/workout_diary/delete.html', content);

def add(request):
    if request.method == 'POST':
        now = datetime.now()
        workout_diary = Workout_diary()
        workout_diary.제목 = request.POST['title']
        workout_diary.내용 = request.POST.get("context");
        workout_diary.작성자 = request.user.username;
        workout_diary.작성일 = now
        workout_diary.수정일 = now
        workout_diary.조회수 = request.POST['vcount']
        workout_diary.save()

        file_upload(request, workout_diary.id);

        msg = "<script>";
        msg += "alert('게시글이 저장되었습니다.');";
        msg += f"location.href='/workout_diary/{workout_diary.id}/';";
        msg += "</script>";
        return HttpResponse(msg);
        # return redirect('WD', workout_diary.id)
        # return render(request, 'community/workout_diary/detail.html')
    else: # GET 방식
        if request.user.is_active:
            return render(request, 'community/workout_diary/add.html');
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
    return render(request, 'community/workout_diary/page.html', content);

def addreply(request, workout_diaryId):
    reply = Reply()
    reply.작성자 = request.user.username;
    reply.작성일 = datetime.now()
    reply.workout_diary_id = workout_diaryId
    reply.내용 = request.GET['reply']
    reply.save()
    Workout_diary.objects.filter(id=workout_diaryId).update(댓글수 = Reply.objects.filter(workout_diary_id=workout_diaryId).count())
    return redirect('WD:D', workout_diaryId)

def delreply(request, workout_diaryId, replyId):
    Reply.objects.get(id=replyId).delete()
    Workout_diary.objects.filter(id=workout_diaryId).update(댓글수 = Reply.objects.filter(workout_diary_id=workout_diaryId).count())
    return redirect('WD:D', workout_diaryId)


def file_upload(request, workout_diaryId):
    # 각 workout_diary.id 의 이름으로 폴더 생성
    dirName = str(workout_diaryId)
    path = settings.WORKOUT_DIARY_MEDIA_ROOT + "/" + dirName + "/"

    if not os.path.isdir(path):
        os.mkdir(path)

    for x in request.FILES.getlist("files"):
        upload_file = open(path + str(x), 'wb')
        for chunk in x.chunks():
            upload_file.write(chunk)

def good(request, workout_diaryId):
    workout_diary = Workout_diary.objects.get(id=workout_diaryId)
    workout_diary.좋아요 = workout_diary.좋아요 + 1
    workout_diary.save()

    return redirect('WD:D', workout_diaryId)

def hate(request, workout_diaryId):
    workout_diary = Workout_diary.objects.get(id=workout_diaryId)
    workout_diary.싫어요 = workout_diary.싫어요 + 1
    workout_diary.save()
    return redirect('WD:D', workout_diaryId)