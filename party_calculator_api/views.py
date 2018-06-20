from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from party_calculator_api.serializers import ProfileSerializer
from party_calculator_auth.models import Profile


@csrf_exempt
def profile_list(request):
    if request.method == 'GET':
        profiles = Profile.objects.all()
        serializer = ProfileSerializer(profiles, many=True)
        return JsonResponse(serializer.data, safe=False)