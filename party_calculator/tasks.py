from PartyCalculator.celery import app
from party_calculator.services.party import PartyService
from party_calculator.services.template_party import TemplatePartyService
from party_calculator.utils import create_object


@app.task(name='party_calculator.tasks.create_user')
def create_user(module_name, model_name, **kwargs):
    create_object(module_name, model_name, **kwargs)


@app.task(name='party_calculator.tasks.create_party')
def create_party(template_id):
    template = TemplatePartyService().get(id=template_id)

    PartyService().create_from_template(template)