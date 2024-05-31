from django.contrib import admin
from upper_info.models import Upper_info

# Register your models here.
class Upper_infoAdmin(admin.ModelAdmin):
    list_display = ['id', '제목', '작성자', '조회수']



admin.site.register(Upper_info, Upper_infoAdmin)
