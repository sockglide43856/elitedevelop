from django.db import OperationalError, InterfaceError
from . import models


def indev(request):
    try:
        idobj = models.inDevelopment.objects.filter(pk=1).first()

        if idobj is None:
            return {"indev": False, "reason": ""}

        return {
            "indev": idobj.indev,
            "reason": idobj.reason,
        }

    except (OperationalError, InterfaceError):
        return {"indev": False, "reason": ""}