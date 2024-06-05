from django.shortcuts import render, redirect, HttpResponse
from picture_member.models import Picture_member, Reply
from datetime import datetime
from django.core.paginator import Paginator
from django.db.models import Max, Min, Avg, Sum, Q
import os
from django.conf import settings
import shutil
from django.contrib import messages
from urllib import parse

# 파일 다운로드, 삭제
def download(request, picture_memberId, filename):
    file_path = os.path.join(settings.PICTURE_MEMBER_MEDIA_ROOT, picture_memberId + "/" + filename)
    
    # exists() : 파일이 있으면 True 없으면 False
    if os.path.exists(file_path):
        readFile = open(file_path, 'rb')
        response = HttpResponse(readFile.read())
        response['Content-Disposition']='attachment;filename='+parse.quote(filename)
        return response

def deleteFile(request, picture_memberId, filename):
    path = picture_memberId + "/" + filename
    file_path = os.path.join(settings.PICTURE_MEMBER_MEDIA_ROOT, path)
    os.remove(file_path)

    msg = "<script>"
    msg += f"alert('{filename} 파일을 삭제했습니다.');"
    msg += f"location.href='/picture_member/{picture_memberId}/update/';";
    msg += "</script>"

    return HttpResponse(msg)

# 동영상
def get_queryset(request, self):
    search_keyword = self.request.GET.get('q', '')
    search_type = self.request.GET.get('type', '')
    notice_list = Picture_member.objects.order_by('-id') 
    
    if search_keyword :
        if len(search_keyword) > 1 :
            if search_type == 'all':
                search_notice_list = notice_list.filter(Q (title__icontains=search_keyword) | Q (content__icontains=search_keyword) | Q (writer__user_id__icontains=search_keyword))
            elif search_type == 'title_content':
                search_notice_list = notice_list.filter(Q (title__icontains=search_keyword) | Q (content__icontains=search_keyword))
            elif search_type == 'title':
                search_notice_list = notice_list.filter(title__icontains=search_keyword)    
            elif search_type == 'content':
                search_notice_list = notice_list.filter(content__icontains=search_keyword)    
            elif search_type == 'writer':
                search_notice_list = notice_list.filter(writer__user_id__icontains=search_keyword)

            return search_notice_list
        else:
            messages.error(self.request, '검색어는 2글자 이상 입력해주세요.')
    return notice_list
    


# Create your views here.
def index(request, page):
    query = request.GET.get('query', '')
    search_by = request.GET.get('search_by', 'title')
    post_by = request.GET.get('post_by', 'present')

    if search_by == 'title':
        picture_member = Picture_member.objects.filter(제목__icontains=query)
    elif search_by == 'author':
        picture_member = Picture_member.objects.filter(작성자__icontains=query)
    elif search_by == 'content':
        picture_member = Picture_member.objects.filter(내용__icontains=query)
    else:
        picture_member = Picture_member.objects.all()

    if post_by == 'present' :
        picture_member = picture_member.order_by('-id')
    elif post_by == 'like' :
        picture_member = picture_member.order_by('-좋아요','-id')

    best_border = Picture_member.objects.order_by("-좋아요")
    
    # Paginator(데이터, 분할할 데이터 수)
    paging = Paginator(picture_member, 8)
    
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
            'picture_member':paging.page(page),
            'page_num':page_num,
            'best_border':best_border,
        }
    except:
        content = {
            'picture_member':paging.page(paging.num_pages),
            'page_num':page_num,
            'best_border':best_border,
        }
    return render(request, 'community/picture_member/index.html', content);

def detail(request, picture_memberId):
    # picture_member.obejcts.get() : picture_member의 class 객체
    # picture_member = picture_member.objects.get(id=picture_memberId);
    # picture_member.조회수 = picture_member.조회수 + 1;
    # picture_member.save()
    # picture_member.obejcts.values().get() : dict 형태
    if request.user.is_active :
        picture_member = Picture_member.objects.values().get(id=picture_memberId);
        Picture_member.objects.filter(id=picture_memberId).update(조회수 = picture_member['조회수'] + 1)
        # get(id=고유번호)
        # filter(컬럼명 = 값)
        reply = Reply.objects.filter(picture_member_id=picture_memberId).values()
        
        try:
            dirList = os.listdir(settings.PICTURE_MEMBER_MEDIA_ROOT + "/" + str(picture_memberId))

            content = {
                'picture_member':picture_member,
                'reply':reply,
                'dirList':dirList,
            }
        except:
            content = {
                'picture_member':picture_member,
                'reply':reply,
            }
        return render(request, 'community/picture_member/detail.html', content);
    else:
        msg = "<script>";
        msg += "alert('로그인 후 사용 가능합니다.');"
        msg += "location.href='/account/login/';"
        msg += "</script>"
        return HttpResponse(msg);

def update(request, picture_memberId):
    picture_member = Picture_member.objects.get(id=picture_memberId)
    if request.method == 'GET':
        if request.user.is_active:
            if request.user.username == picture_member.작성자:
                try:
                    dirList = os.listdir(settings.PICTURE_MEMBER_MEDIA_ROOT + "/" + str(picture_memberId))
                    content = {
                        'picture_member':picture_member,
                        'dirList':dirList,
                    }
                except:
                    content = {
                        'picture_member':picture_member,
                    }
                return render(request, 'community/picture_member/update.html', content);
            else :
                msg = "<script>"
                msg += "alert('접근할 수 없는 URL 입니다.');"
                msg += "location.href='/picture_member/page/1';"
                msg += "</script>"
                return HttpResponse(msg);
        else :
            return render(request, 'error/errorAccess.html');
    elif request.method == "POST":
        picture_member.제목 = request.POST.get('title');
        picture_member.내용 = request.POST.get('content');
        picture_member.수정일 = datetime.now();
        picture_member.save()

        file_upload(request, picture_member.id);

        msg = "<script>"
        msg += f"alert('{ picture_member.id }번 게시글이 수정되었습니다.');"
        msg += f"location.href='/picture_member/{ picture_member.id }/';"
        msg += "</script>"
        return HttpResponse(msg);

def delete(request, picture_memberId):
    print('aaa')
    # os.remove(파일삭제)
    # os.rmdir(폴더삭제 - 빈폴더만 삭제가능)
    path = settings.PICTURE_MEMBER_MEDIA_ROOT + "/" + str(picture_memberId) + "/"
    if os.path.isdir(path):
        # dirList = os.listdir(path)
        # for f in dirList:
        #     os.remove(path + "/" + f)
        # os.rmdir(path)
        shutil.rmtree(path)

    Picture_member.objects.get(id=picture_memberId).delete()
    Reply.objects.filter(picture_member_id=picture_memberId).delete()
    content = {
        'picture_memberId':picture_memberId
    }
    return render(request, 'community/picture_member/delete.html', content);

def add(request):
    if request.method == 'POST':
        now = datetime.now()
        picture_member = Picture_member()
        picture_member.제목 = request.POST['title']
        picture_member.내용 = request.POST.get("context");
        picture_member.작성자 = request.user.username;
        picture_member.작성일 = now
        picture_member.수정일 = now
        picture_member.조회수 = request.POST['vcount']
        picture_member.save()

        file_upload(request, picture_member.id);

        msg = "<script>";
        msg += "alert('게시글이 저장되었습니다.');";
        msg += f"location.href='/picture_member/{picture_member.id}/';";
        msg += "</script>";
        return HttpResponse(msg);
        # return redirect('PM', picture_member.id)
        # return render(request, 'community/picture_member/detail.html')
    else: # GET 방식
        if request.user.is_active:
            return render(request, 'community/picture_member/add.html');
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
    return render(request, 'community/picture_member/page.html', content);

def addreply(request, picture_memberId):
    reply = Reply()
    reply.작성자 = request.user.username;
    reply.작성일 = datetime.now()
    reply.picture_member_id = picture_memberId
    reply.내용 = request.GET['reply']
    reply.save()
    Picture_member.objects.filter(id=picture_memberId).update(댓글수 = Reply.objects.filter(picture_member_id=picture_memberId).count())
    return redirect('PD:D', picture_memberId)

def delreply(request, picture_memberId, replyId):
    Reply.objects.get(id=replyId).delete()
    Picture_member.objects.filter(id=picture_memberId).update(댓글수 = Reply.objects.filter(picture_member_id=picture_memberId).count())
    return redirect('PD:D', picture_memberId)


def file_upload(request, picture_memberId):
    # 각 picture_member.id 의 이름으로 폴더 생성
    dirName = str(picture_memberId)
    path = settings.PICTURE_MEMBER_MEDIA_ROOT + "/" + dirName + "/"

    if not os.path.isdir(path):
        os.mkdir(path)

    for x in request.FILES.getlist("files"):
        upload_file = open(path + str(x), 'wb')
        for chunk in x.chunks():
            upload_file.write(chunk)

def good(request, picture_memberId):
    picture_member = Picture_member.objects.get(id=picture_memberId)
    picture_member.좋아요 = picture_member.좋아요 + 1
    picture_member.save()

    return redirect('PD:D', picture_memberId)

def hate(request, picture_memberId):
    picture_member = Picture_member.objects.get(id=picture_memberId)
    picture_member.싫어요 = picture_member.싫어요 + 1
    picture_member.save()
    return redirect('PD:D', picture_memberId)