from django.shortcuts import get_object_or_404

from party_calculator.models import Food


def get_food_by_id(id: int) -> Food:
  return get_object_or_404(Food, id=id)