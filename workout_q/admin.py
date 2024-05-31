from django.contrib import admin
from workout_q.models import Workout_q

# Register your models here.
class Workout_qAdmin(admin.ModelAdmin):
    list_display = ['id', '제목', '작성자', '조회수']



admin.site.register(Workout_q, Workout_qAdmin)
