from django.contrib import admin
from picture_member.models import Picture_member

# Register your models here.
class Picture_memberAdmin(admin.ModelAdmin):
    list_display = ['id', '제목', '작성자', '조회수']



admin.site.register(Picture_member, Picture_memberAdmin)
