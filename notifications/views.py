from django.http import HttpResponse

def ws_connect(request):
    return HttpResponse(status=204)
