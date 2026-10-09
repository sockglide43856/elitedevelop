from django.contrib import admin
from .models import AIMessage, AIRoom, AIUserMemory, AIJob

admin.site.register(AIMessage)
admin.site.register(AIRoom)
admin.site.register(AIUserMemory)
admin.site.register(AIJob)