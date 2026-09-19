from . import models
def indev(request):
    idobj, created = models.inDevelopment.objects.get_or_create(pk=1)
    return {
        'indev': idobj.indev,
        'reason': idobj.reason,
    }