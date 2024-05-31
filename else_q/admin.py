from django.contrib import admin
from else_q.models import Else_q

# Register your models here.
class Else_qAdmin(admin.ModelAdmin):
    list_display = ['id', '제목', '작성자', '조회수']



admin.site.register(Else_q, Else_qAdmin)
