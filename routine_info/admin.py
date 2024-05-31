from django.contrib import admin
from routine_info.models import Routine_info

# Register your models here.
class Routine_infoAdmin(admin.ModelAdmin):
    list_display = ['id', '제목', '작성자', '조회수']



admin.site.register(Routine_info, Routine_infoAdmin)
