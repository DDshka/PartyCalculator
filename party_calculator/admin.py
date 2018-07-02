# Register your models here.
from django.contrib import admin

from party_calculator.models import Schedule


class ScheduleAdmin(admin.ModelAdmin):
    pass


admin.site.register(Schedule, ScheduleAdmin)