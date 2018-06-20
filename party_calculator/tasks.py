from celery.utils.log import get_task_logger
from django.core.mail import send_mail as django_send_mail

from PartyCalculator.celery import app
from party_calculator.exceptions import TemplatePartyHasActiveRelatedPartyException
from party_calculator.services.party import PartyService
from party_calculator.services.template_party import TemplatePartyService
from party_calculator.utils import create_object

logger = get_task_logger(__name__)

@app.task(name='party_calculator.tasks.create_user')
def create_user(module_name, model_name, **kwargs):
    create_object(module_name, model_name, **kwargs)


@app.task(name='party_calculator.tasks.create_party')
def create_party(template_id):
    template = TemplatePartyService().get(id=template_id)

    if TemplatePartyService().has_active_parties(template):
        logger.error('Task can`t be run because this template(id={0}) has active parties'
                    .format(template_id))
        raise TemplatePartyHasActiveRelatedPartyException()

    PartyService().create_from_template(template)


@app.task(name='party_calculator.tasks.send_mail')
def send_mail(*args, **kwargs):
    django_send_mail(*args, **kwargs)