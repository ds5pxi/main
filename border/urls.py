from django.urls import path, re_path
from . import views

app_name="BD"

urlpatterns= [
    # path('', views.index, name='I'),
    re_path(r'page/(\d+)/$', views.index, name='I'),
    re_path(r'(\d+)/$', views.detail, name='D'),
    re_path(r'(\d+)/update/$', views.update, name='U'),
    re_path(r'(\d+)/delete/$', views.delete, name='L'),
    path('add/', views.add, name='A'),
    re_path(r'addreply/(\d+)/', views.addreply),
    re_path(r'delreply/(\d+)/(\d+)/$', views.delreply),
    path('good/<borderId>/', views.good),
    path('hate/<borderId>/', views.hate),
]