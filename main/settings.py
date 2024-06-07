"""
Django settings for main project.

Generated by 'django-admin startproject' using Django 5.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from pathlib import Path
import os
from .my_settings import DATABASES

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-q2c+nl83t(kh5gsy=q97ia-nu8$2ha67ejtssb7x+_rf!1xk3t'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost','*']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'main', 'border', 'diet_info', 'routine_info', 'stretch_info', 'upper_info',
    'lower_info',  'diet_diary', 'advice', 'running_else_info', 'workout_diary',
    'picture_member', 'workout_q', 'center_q', 'diet_q', 'machine_q', 'else_q',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'main.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR), 'template'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'main.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

# sqlite3 DB 사용
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

# mysql DB 사용
# DATABASES = {
#     'default':{
#         'ENGINE' : 'django.db.backends.mysql', # mysql orm engine
#         'NAME' : 'mydatabase', # DB 이름
#         'USER' : 'root', # 사용자 이름
#         'PASSWORD' : '1234', # 암호
#         'HOST' : 'localhost', # 127.0.0.1, 서버 아이피 또는 도메인이름
#         'PORT' : '3306', # DB 연결 포트
#     }
# }

# oracle DB 사용
# DATABASES = {
#     'default':{
#         'ENGINE' : 'django.db.backends.oracle', # mysql orm engine
#         'NAME' : 'XE', # DB 이름
#         'USER' : 'system', # 사용자 이름
#         'PASSWORD' : 'oracle', # 암호
#         'HOST' : 'localhost', # 127.0.0.1, 서버 아이피 또는 도메인이름
#         'PORT' : '1521', # DB 연결 포트
#     }
# }

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'ko-kr'

TIME_ZONE = 'Asia/Seoul'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

# 정적파일의 URL 
STATIC_URL = 'static/'

# 정적파일의 폴더 지정
# 수정한 부분 BY 대근
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
# STATICFILES_DIRS = [
#     os.path.join(BASE_DIR, 'static'),
# ]
# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# 로그인 후에 이동할 페이지 url
LOGIN_REDIRECT_URL = "/"

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
WORKOUT_DIARY_MEDIA_ROOT = os.path.join(BASE_DIR, 'media_workout_diary')
DIET_DIARY_MEDIA_ROOT = os.path.join(BASE_DIR, 'media_diet_diary')
ADVICE_MEDIA_ROOT = os.path.join(BASE_DIR, 'media_advice')
PICTURE_MEMBER_MEDIA_ROOT = os.path.join(BASE_DIR, 'media_picture_member')
DIET_INFO_MEDIA_ROOT = os.path.join(BASE_DIR, 'media_diet_info')
ROUTINE_INFO_MEDIA_ROOT = os.path.join(BASE_DIR, 'media_routine_info')
STRETCH_INFO_MEDIA_ROOT = os.path.join(BASE_DIR, 'media_stretch_info')
UPPER_INFO_MEDIA_ROOT = os.path.join(BASE_DIR, 'media_upper_info')
LOWER_INFO_MEDIA_ROOT = os.path.join(BASE_DIR, 'media_lower_info')
RUNNING_ELSE_INFO_MEDIA_ROOT = os.path.join(BASE_DIR, 'media_running_else_info')
WORKOUT_Q_MEDIA_ROOT = os.path.join(BASE_DIR, 'media_workout_q')
CENTER_Q_MEDIA_ROOT = os.path.join(BASE_DIR, 'media_center_q')
DIET_Q_MEDIA_ROOT = os.path.join(BASE_DIR, 'media_diet_q')
MACHINE_Q_MEDIA_ROOT = os.path.join(BASE_DIR, 'media_machine_q')
ELSE_Q_MEDIA_ROOT = os.path.join(BASE_DIR, 'media_else_q')
DIET_MEDIA_ROOT = os.path.join(BASE_DIR, 'media_diet')
MEDIA_URL = '/media/'