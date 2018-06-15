import json

from django_celery_beat.models import CrontabSchedule, PeriodicTask

from party_calculator.common.service import Service
from party_calculator.exceptions import TemplatePartyScheduleIsNotSet
from party_calculator.models import TemplateParty


class ScheduleService(Service):
    model = CrontabSchedule

    CRONTAB_FIELDS = ('minute', 'hour', 'day_of_week', 'day_of_month', 'month_of_year')

    SCHEDULE_PREFIX = 'create-'

    def create(self, pattern=None, **kwargs) -> model:
        if pattern:
            splitted = self.split_pattern(pattern)
            dict_to_pass = dict(zip(self.CRONTAB_FIELDS, splitted))
            return self.model.objects.create(**dict_to_pass)

        return self.model.objects.create(**kwargs)

    def update(self, schedule: model, pattern: str):
        splitted = self.split_pattern(pattern)
        schedule.minute = splitted[0]
        schedule.hour = splitted[1]
        schedule.day_of_week = splitted[2]
        schedule.day_of_month = splitted[3]
        schedule.month_of_year = splitted[4]
        schedule.save()

    def split_pattern(self, pattern: str):
        return pattern.split(sep=' ')

    def set_periodic_task_enabled(self, template: TemplateParty, enabled):
        try:
            schedule_name = self.get_schedule_name(template)
            task = PeriodicTask.objects.get(name=schedule_name)
        except PeriodicTask.DoesNotExist:
            schedule = template.schedule

            if not schedule:
                raise TemplatePartyScheduleIsNotSet()

            task = PeriodicTask.objects.create(name=self.get_schedule_name(template),
                                               crontab=schedule,
                                               task='party_calculator.tasks.create_party',
                                               args=json.dumps([template.pk]))
        task.enabled = enabled
        task.save()

    def get_schedule_name(self, template: TemplateParty):
        return '{0}{1}'.format(self.SCHEDULE_PREFIX, template.name)