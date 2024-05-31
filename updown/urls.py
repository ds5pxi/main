from django.urls import path, re_path
from . import views

urlpatterns= [
    path("", views.index, name='index'),
    path('upload/', views.upload, name='upload'),
    re_path(r'download/(\d+)/([0-9a-zA-Zㄱ-힣 ()_.-]+)', views.download, name='download'),
    path(r'delete/<borderId>/<filename>/', views.delete, name='delete'),
]