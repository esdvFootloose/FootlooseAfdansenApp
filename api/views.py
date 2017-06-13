from django.http.response import JsonResponse
from afdansen.models import Dance
from index.decorators import superuser_required
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

@superuser_required
def GetCurrentDances(request, pk):
    jury = get_object_or_404(User, pk=pk)
    return JsonResponse([d.id for d in Dance.objects.filter(Jury=jury)], safe=False)