from django.contrib import admin
from diet_diary.models import Diet_diary

# Register your models here.
class Diet_diaryAdmin(admin.ModelAdmin):
    list_display = ['id', '제목', '작성자', '조회수']



admin.site.register(Diet_diary, Diet_diaryAdmin)
