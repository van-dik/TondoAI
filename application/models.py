import uuid
from django.db import models
from django.contrib.auth.models import User

class Chat(models.Model):
    """
        Classe para informações do chat iniciada pelo usuário.
    Args:
        chat_id (UUIDField): Chave primária da classe.
        user_id (ForeignKey): ID do usuário que iniciou o chat. 
        user_ip_address(GenericIPAddressField): IP do usuário
        active (BooleanField):  Indica se o chat está ativo ou não.
        created_at(DateTimeField):  Data e hora de criação do chat.
    """
    chat_id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False
    )
    user_id = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name="id_usuario"
    )
    user_ip_address = models.GenericIPAddressField(null=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

class ChatMessages(models.Model):
    """
        Classe para armazenar mensagens de cada chat. CHAT(1, N)MENSAGENS 
    Args:
        chat_id (ForeignKey): Chave estrangeira da classe 'Chat'
        sender (CharFied):  Nome do remetente da mensagem
        message (TextField): Mensagem enviada
        timestamp (DateTimeField):  Data e hora da mensagem auto gravável.
    """
    chat_id = models.ForeignKey(
        Chat, 
        on_delete=models.CASCADE, 
        related_name="messages"
    )
    sender = models.CharField(
        max_length=20, 
        choices=[("user", "User"), 
                 ("bot", "Bot")]
    )
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
class QueryHistory(models.Model):
    """
        O modelo QueryHistory armazena o histórico de consultas realizadas no chat. 
        Cada registro refere-se a uma consulta específica feita em um chat e armazena 
        informações sobre o tipo de consulta e o tempo de resposta.
        
    Args:
        chat_id (ForeignKey para Chat): Identifica o chat ao qual esta consulta pertence, 
            com um relacionamento de muitos-para-um, ou seja, um Chat pode ter múltiplos 
            registros de QueryHistory.
            
        chat_message (OneToOneField para ChatMessages): Identifica a mensagem de chat 
            associada a esta consulta específica, garantindo que cada mensagem do chat 
            tenha apenas um registro de histórico de consulta.
            
        query_type (CharField): Descreve o tipo de consulta realizada, por exemplo, 
            "consulta financeira" ou "informação de cliente".
            
        response_time (DurationField): Armazena a duração da resposta gerada pelo chatbot, 
            útil para monitoramento de performance.
    """
    chat_id = models.ForeignKey(
        Chat, 
        on_delete=models.CASCADE, 
        related_name="query_history"
    )
    chat_message = models.OneToOneField(ChatMessages, on_delete=models.CASCADE)
    query_type = models.CharField(max_length=100)
    response_time = models.DurationField()
    
class Feedback(models.Model):
    """
        O modelo Feedback armazena o feedback de cada mensagem de chat, 
        incluindo uma avaliação (rating) e um comentário opcional. 
        Isso ajuda a avaliar a qualidade das respostas fornecidas pelo chatbot.

    Args:
        chat_message (ForeignKey para ChatMessages): Identifica a mensagem de chat para a 
            qual este feedback é fornecido, com um relacionamento de muitos-para-um.
            
        rating (IntegerField com choices): Classificação numérica do feedback, 
            permitindo que o usuário avalie a resposta do chatbot com uma escala de 1 a 5.
            Opções de classificação:
            1: Péssimo
            2: Ruim
            3: Bom
            4: Muito bom
            5: Excelente
            
        comment (TextField, opcional): Comentário adicional do usuário, 
            permitindo feedback descritivo sobre a resposta.
            
        created_at (DateTimeField): Registra automaticamente a data e hora em que o feedback
            foi criado, útil para análise de histórico.
    """
    chat_message = models.ForeignKey(
        ChatMessages, 
        on_delete=models.CASCADE, 
        related_name="feedback"
    )
    rating = models.IntegerField(
        choices=[(1, "Péssimo"), 
                 (2, "Ruim"), 
                 (3, "Bom"), 
                 (4, "Muito bom"), 
                 (5, "Excelente")]
    )
    comment = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    