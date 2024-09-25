from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
import requests
import json
from environs import Env
from langchain_ollama import ChatOllama
from .rag import with_message_history#, print_messages_from_history
from chatbot.models import Patient
import uuid

env = Env()
env.read_env()

# FIX WITH A RANDOM UUID
session_id = "f7da912b-f285-40e8-90c4-ac1e49f08dd5" # str(uuid.uuid4())

# TO-DO: ADD LOGIC TO DISPLAY ALL THE CHATS WITH CHAT IDS TO POSTGRES AND DISPLAY THE LIST HERE 
def allchats_view(request):
    pass

def chatbot_view(request):
    return render(request, 'chatbot.html')

def send_message(request):
    if request.method == 'POST':
        request_data = json.loads(request.body)
        user_message = request_data.get('message', '')
        current_time = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
        # HARD CODED FOR JUST ONE USER
        patient = get_object_or_404(Patient, id=1)
        patient_info = f"First Name: {patient.first_name},\
            Last Name: {patient.last_name},\
            Date of Birth: {patient.date_of_birth},\
            Medical Condition: {patient.medical_condition},\
            Medication Regimen: {patient.medication_regimen},\
            Last Appointment: {patient.last_appointment},\
            Next Appointment: {patient.next_appointment},\
            Doctor Name: {patient.doctor_name}"
        try:
            response = with_message_history.invoke(
            {"question": user_message, "user_info": patient_info},
            # TO-DO: LOAD USER AND CONVERSATION IDS FROM DB
            # config={"configurable": {"user_id": 1, "session_id": session_id}}
            config={"configurable": {"session_id": session_id}},
            )
            # print_history_messages(conversation_id)
            return JsonResponse({
            'response': response.content,
            'timestamp': current_time
        }, safe=False)

        except requests.exceptions.RequestException as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({'response': 'Invalid request'}, status=400)

