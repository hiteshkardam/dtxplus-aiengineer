from django.contrib import admin
from chatbot.models import Patient, MessageStore

admin.site.register(Patient)
admin.site.register(MessageStore)