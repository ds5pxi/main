DATABASES = {
    'default':{
        'ENGINE' : 'django.db.backends.mysql', # mysql orm engine
        'NAME' : 'mydatabase', # DB 이름
        'USER' : 'root', # 사용자 이름
        'PASSWORD' : '1234', # 암호
        'HOST' : 'localhost', # 127.0.0.1, 서버 아이피 또는 도메인이름
        'PORT' : '3306', # DB 연결 포트
    }
}