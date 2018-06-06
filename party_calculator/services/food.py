from django.shortcuts import get_object_or_404

from party_calculator.models import Food


class FoodService:
  def get_by_id(self, food_id: int) -> Food:
    return get_object_or_404(Food, id=food_id)