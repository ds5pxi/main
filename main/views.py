from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import auth
from django.contrib.auth.hashers import check_password
from django.urls import reverse

def index(request):
    return render(request, 'index.html');

def createAccount(request):
    if request.method == 'GET':
        return render(request, "registration/register.html")
    elif request.method == 'POST':
        username = request.POST.get("username");
        password = request.POST.get("password");
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")

        try:
            User.objects.create_user(username, email, password, 
            first_name=first_name, last_name=last_name)

            return redirect('login')
        except:
            msg = "<script>";
            msg += "alert('같은 아이디가 존재합니다. 다시 가입하세요.');";
            msg += "location.href='/account/register';";
            msg += "</script>";
            return HttpResponse(msg);

def login(request):
    if request.method == 'GET':
        return render(request, 'registration/login.html')
    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(request, username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect("/")  # 로그인 성공 후에 "/"로 리디렉션
        else:
            msg = "<script>"
            msg += "alert('로그인 아이디/비밀번호가 틀립니다. 다시 로그인 하세요.');"
            msg += "location.href='/account/login';"
            msg += "</script>"
            return HttpResponse(msg)
        
        
def logout(request):
    auth.logout(request);
    return render(request, "registration/logged_out.html");


def myinfo(request):
    user = request.user;
    userInfo = User.objects.get(username=user.username);
    content = {
        'userInfo':userInfo
    }
    if user.is_active :
        if request.method == 'GET':
            return render(request, 'registration/myinfo.html', content)
        else: # POST 로 접근
            origin = request.POST['origin']

            # check_password(평문, 해쉬된암호)
            if check_password(origin, user.password):
                password = request.POST.get('password')
                first_name = request.POST['first_name']
                last_name = request.POST.get("last_name")
                email = request.POST.get("email")

                if password != None :
                    userInfo.set_password(password)
                else :
                    userInfo.set_password(origin)
                userInfo.first_name = first_name
                userInfo.last_name = last_name
                userInfo.email = email
                userInfo.save()
                
                msg = "<script>";
                msg += "alert('회원정보 수정이 완료되었습니다. 다시 로그인 하세요.');";
                msg += "location.href='/account/login';";
                msg += "</script>";
                return HttpResponse(msg);
            else:
                msg = "<script>";
                msg += "alert('비밀번호가 틀려 회원정보를 수정 할 수 없습니다.');";
                msg += "location.href='/account/login';";
                msg += "</script>";
                return HttpResponse(msg);
    else:
        msg = "<script>";
        msg += "alert('로그인이 되어 있지 않습니다. 로그인 후 사용하세요.');";
        msg += "location.href='/account/login';";
        msg += "</script>";
        return HttpResponse(msg);
    
def myinfoDel(request):
    # request.user.delete();
    User.objects.get(username = request.user.username).delete();
    
    msg = "<script>";
    msg += "alert('회원정보를 삭제했습니다.');";
    msg += 'location.href="/";';
    msg += "</script>";
    return HttpResponse(msg);

def page_not_found(request, exception):
    return render(request, 'error/404.html')

def custom_500(request):
    return render(request, 'error/500.html', status=500)