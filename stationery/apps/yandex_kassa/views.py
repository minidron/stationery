from django.http import HttpResponse


def notification(request):
    return HttpResponse(status=200)
