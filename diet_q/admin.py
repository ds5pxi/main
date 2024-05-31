from django.contrib import admin
from diet_q.models import Diet_q

# Register your models here.
class Diet_qAdmin(admin.ModelAdmin):
    list_display = ['id', '제목', '작성자', '조회수']



admin.site.register(Diet_q, Diet_qAdmin)
