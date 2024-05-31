from django.contrib import admin
from workout_diary.models import Workout_diary

# Register your models here.
class Workout_diaryAdmin(admin.ModelAdmin):
    list_display = ['id', '제목', '작성자', '조회수']



admin.site.register(Workout_diary, Workout_diaryAdmin)
