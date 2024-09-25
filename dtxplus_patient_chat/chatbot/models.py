from django.db import models
from django.db import connection
from langchain_postgres import PostgresChatMessageHistory

class Patient(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    date_of_birth = models.DateField()
    phone_number = models.CharField(max_length=15)
    email = models.EmailField()
    medical_condition = models.TextField()
    medication_regimen = models.TextField()
    last_appointment = models.DateTimeField()
    next_appointment = models.DateTimeField()
    doctor_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class MessageStore(models.Model):
    session_id = models.UUIDField()
    message = models.JSONField()
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'message_store'
