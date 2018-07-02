import json

from django_celery_beat.models import CrontabSchedule, PeriodicTask

from party_calculator.common.service import Service
from party_calculator.exceptions import TemplatePartyScheduleIsNotSetException
from party_calculator.models import TemplateParty


class ScheduleService(Service):
    model = CrontabSchedule     # in fact there is no specific model at all

    CRONTAB_FIELDS = ('minute', 'hour', 'day_of_week', 'day_of_month', 'month_of_year')

    SCHEDULE_PREFIX = 'create-'

    def set_periodic_task_enabled(self, template: TemplateParty, enabled):
        try:
            schedule_name = self.get_schedule_name(template)
            task = PeriodicTask.objects.get(name=schedule_name)
        except PeriodicTask.DoesNotExist:
            schedule = template.schedule

            if not schedule:
                raise TemplatePartyScheduleIsNotSetException()

            crontab_schedule = CrontabSchedule.objects.get(minute=schedule.minute,
                                                           hour=schedule.hour,
                                                           day_of_week=schedule.day_of_week,
                                                           day_of_month=schedule.day_of_month,
                                                           month_of_year=schedule.month_of_year)

            task = PeriodicTask.objects.create(name=self.get_schedule_name(template),
                                               crontab=crontab_schedule,
                                               task='party_calculator.tasks.create_party',
                                               args=json.dumps([template.pk]))
        task.enabled = enabled
        task.save()

    def get_or_create_dcbcs(self, **kwargs) -> tuple:
        """
        This method gets or creates a django_celery_beat.CrontabSchedule instance.
        Use it, because django_celery_beat.PeriodicTask depends on this model, not ours.
        """
        return CrontabSchedule.objects.get_or_create(**kwargs)

    def get_schedule_name(self, template: TemplateParty):
        return '{0}{1}'.format(self.SCHEDULE_PREFIX, template.name)