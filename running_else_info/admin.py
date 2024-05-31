from django.contrib import admin
from running_else_info.models import Running_else_info

# Register your models here.
class Running_else_infoAdmin(admin.ModelAdmin):
    list_display = ['id', '제목', '작성자', '조회수']



admin.site.register(Running_else_info, Running_else_infoAdmin)