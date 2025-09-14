from django.contrib import admin
from .models import Cattle, HealthCheck, Treatment, Vaccination, Notification, Report


@admin.register(Cattle)
class CattleAdmin(admin.ModelAdmin):
    list_display = ('tag_no', 'name', 'breed', 'gender')
    search_fields = ('tag_no', 'name')


admin.site.register(HealthCheck)
admin.site.register(Treatment)
admin.site.register(Vaccination)
admin.site.register(Notification)
admin.site.register(Report)
