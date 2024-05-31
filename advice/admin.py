from django.contrib import admin
from advice.models import Advice

# Register your models here.
class AdviceAdmin(admin.ModelAdmin):
    list_display = ['id', '제목', '작성자', '조회수']



admin.site.register(Advice, AdviceAdmin)
