from django.contrib import admin
from center_q.models import Center_q

# Register your models here.
class Center_qAdmin(admin.ModelAdmin):
    list_display = ['id', '제목', '작성자', '조회수']



admin.site.register(Center_q, Center_qAdmin)
