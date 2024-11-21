import json
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from application.models import Chat, ChatMessages, QueryHistory, Feedback
from django.utils import timezone
from llama.model.llama_inference import generate_response
from django.http import JsonResponse


def home(request):
    return render(request, "home.html")


# Considerações
# @csrf_exempt: Usei esse decorador para simplificar as requisições POST sem autenticação de CSRF,
# mas é recomendável usar autenticação e proteger as views de CSRF em produção.

@csrf_exempt
def create_chat(request):
    if request.method == "POST":
        user_id = request.POST.get("user_id")
        user = get_object_or_404(User, id=user_id)
        chat = Chat.objects.create(user_id=user)
        return chat
    
@csrf_exempt
def add_message(request):
    """ 
        Adiciona uma mensagem ao chat, recebendo o chat_id e a message do usuário.
        Usa o modelo Llama 3.2 para gerar uma resposta à mensagem do usuário.
        Calcula o tempo de resposta e salva o histórico da consulta no modelo QueryHistory.
        Retorna a mensagem do usuário, a resposta do bot e o tempo de resposta.
        Tempo de Resposta: A view add_message calcula o tempo de resposta do modelo para registro no QueryHistory.        
        JSON Parsing: As views usam json.loads(request.body) para lidar com JSON ou request.POST.get() para lidar com formulários.
    """
    
    if request.method == "POST":
        data = json.loads(request.body)
        chat_id = data.get("chat_id")
        message = data.get("message")
        
        chat = get_object_or_404(Chat, chat_id=chat_id)
        chat_message = ChatMessages.objects.create(chat=chat, message=message, sender="user")#pode quebrar pelo chat id - testar
        
        # Gera uma resposta com o Llama
        start_time = timezone.now()
        response = generate_response(message)
        end_time = timezone.now()
        response_time = end_time - start_time

        # Salva a resposta do chatbot
        bot_message = ChatMessages.objects.create(chat=chat, message=response, sender="bot")

        # Registra o histórico de consultas
        QueryHistory.objects.create(
            chat_id=chat,
            chat_message=chat_message,
            query_type="general",  # Você pode modificar para identificar o tipo da consulta
            response_time=response_time
        )

        return JsonResponse({
            "user_message": chat_message.message,
            "bot_response": bot_message.message,
            "response_time": response_time.total_seconds()
        })
        
@csrf_exempt
def submit_feedback(request):
    """ 
        Coleta o feedback do usuário sobre a resposta do chatbot.
        Recebe o chat_message_id, rating e um comment opcional.
        Salva o feedback no modelo Feedback e retorna uma confirmação de sucesso.
    """
    
    if request.method == "POST":
        data = json.loads(request.body)
        chat_message_id = data.get("chat_message_id")
        rating = data.get("rating")
        comment = data.get("comment", "")

        chat_message = get_object_or_404(ChatMessages, id=chat_message_id)
        Feedback.objects.create(
            chat_message=chat_message,
            rating=rating,
            comment=comment
        )

        return JsonResponse({"status": "success", "message": "Feedback submitted successfully."})

