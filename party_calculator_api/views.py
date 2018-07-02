import json

from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from party_calculator_api.serializers import ProfileSerializer
from party_calculator_auth.models import Profile


@csrf_exempt
def profile_list(request):
    if request.method == 'GET':
        profiles = Profile.objects.all()
        serializer = ProfileSerializer(profiles, many=True)
        return JsonResponse(serializer.data, safe=False)


def profile_list_by_term(request):
    if request.is_ajax() :
        q = request.GET.get('term', '')
        profiles = Profile.objects.filter(username__icontains=q)[:20]
        results = []
        for profile in profiles:
            profile_json = {}
            profile_json['label'] = '{0} ({1})'.format(profile.username, profile.email)
            profile_json['value'] = profile.username
            results.append(profile_json)
        data = json.dumps(results)
    else:
        data = 'fail'

    return HttpResponse(data, 'application/json')