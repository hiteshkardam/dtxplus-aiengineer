from django.urls import path
from . import views

urlpatterns = [
    path('', views.chatbot_view, name='chatbot'),
    # path('chatbot/', views.chatbot_view, name='chatbot'),
    path('send-message/', views.send_message, name='send_message'),
]