import importlib

from PartyCalculator.celery import app


@app.task
def create_object(module_name, model_name, **kwargs):
  cls = class_for_name(module_name, model_name)
  obj = cls(**kwargs)

def class_for_name(module_name, class_name):
  module = importlib.import_module(module_name)
  cls = getattr(module, class_name)
  return cls