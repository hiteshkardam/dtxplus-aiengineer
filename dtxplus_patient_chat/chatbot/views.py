from django.shortcuts import render
from django.http import JsonResponse
from django.utils import timezone
import random

# Test Responses
responses = [
    "Hello!",
    "How can I help you?",
    "Hi!",
    "How are you?"
]

# TO-DO: ADD LOGIC TO STORE ALL THE CHATS WITH CHAT IDS TO POSTGRES IN JSON AND DISPLAY THE LIST HERE 
def allchats_view(request):
    pass

def chatbot_view(request):
    return render(request, 'chatbot.html')

def send_message(request):
    if request.method == 'POST':
        user_message = request.POST.get('message')
        bot_response = random.choice(responses)
        current_time = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
        return JsonResponse({
            'response': bot_response,
            'timestamp': current_time
        })
    return JsonResponse({'response': 'Invalid request'}, status=400)

