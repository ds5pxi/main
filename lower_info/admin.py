from django.contrib import admin
from lower_info.models import Lower_info

# Register your models here.
class Lower_infoAdmin(admin.ModelAdmin):
    list_display = ['id', '제목', '작성자', '조회수']



admin.site.register(Lower_info, Lower_infoAdmin)

