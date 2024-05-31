from django.contrib import admin
from diet_info.models import Diet_info

# Register your models here.
class Diet_infoAdmin(admin.ModelAdmin):
    list_display = ['id', '제목', '작성자', '조회수']



admin.site.register(Diet_info, Diet_infoAdmin)