from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def notification(request):
    return HttpResponse(status=200)
