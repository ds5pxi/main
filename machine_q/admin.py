from django.contrib import admin
from machine_q.models import Machine_q

# Register your models here.
class Machine_qAdmin(admin.ModelAdmin):
    list_display = ['id', '제목', '작성자', '조회수']



admin.site.register(Machine_q, Machine_qAdmin)
