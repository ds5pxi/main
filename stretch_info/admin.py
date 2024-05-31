from django.contrib import admin
from stretch_info.models import Stretch_info

# Register your models here.
class Stretch_infoAdmin(admin.ModelAdmin):
    list_display = ['id', '제목', '작성자', '조회수']



admin.site.register(Stretch_info, Stretch_infoAdmin)