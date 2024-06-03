from django.urls import path, re_path
from . import views

app_name = "EQ"

urlpatterns= [
    re_path(r'page/(?P<page>\d+)/$', views.index, name='I'),
    re_path(r'(?P<else_qId>\d+)/$', views.detail, name='D'),
    re_path(r'(?P<else_qId>\d+)/update/$', views.update, name='U'),
    re_path(r'(?P<else_qId>\d+)/delete/$', views.delete, name='L'),
    path('add/', views.add, name='A'),
    re_path(r'addreply/(?P<else_qId>\d+)/', views.addreply),
    re_path(r'delreply/(?P<else_qId>\d+)/(?P<replyId>\d+)/$', views.delreply),
    path('good/<int:else_qId>/', views.good),
    path('hate/<int:else_qId>/', views.hate),
]