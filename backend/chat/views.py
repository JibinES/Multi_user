import PyPDF2
from io import BytesIO
from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from .models import Conversation, Message, Document
from .serializers import ConversationSerializer, MessageSerializer, DocumentSerializer
from django.shortcuts import get_object_or_404
from .chat_engine import get_chat_response  # We'll implement this later

class DocumentViewSet(viewsets.ModelViewSet):
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Document.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        document = serializer.save(user=self.request.user)
        
        # Extract text from PDF
        pdf_file = document.file
        pdf_text = ""
        
        try:
            pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_file.read()))
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                pdf_text += page.extract_text()
            
            document.content = pdf_text
            document.save()
        except Exception as e:
            print(f"Error extracting PDF text: {e}")
        
        return document

class ConversationViewSet(viewsets.ModelViewSet):
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Conversation.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)

class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        conversation_id = self.kwargs.get('conversation_pk')
        return Message.objects.filter(
            conversation__user=self.request.user,
            conversation_id=conversation_id
        ).order_by('timestamp')
    
    def perform_create(self, serializer):
        conversation_id = self.kwargs.get('conversation_pk')
        conversation = get_object_or_404(Conversation, id=conversation_id, user=self.request.user)
        
        # Save user message
        user_message = serializer.save(conversation=conversation, sender='user')
        
        # Get document context if provided
        document_id = self.request.data.get('document')
        document_context = None
        if document_id:
            try:
                document = Document.objects.get(id=document_id, user=self.request.user)
                document_context = document.content
            except Document.DoesNotExist:
                pass
        
        # Get conversation history
        conversation_history = Message.objects.filter(
            conversation=conversation
        ).order_by('timestamp')[:10]  # Limit to last 10 messages for context
        
        history_formatted = []
        for msg in conversation_history:
            history_formatted.append({
                'role': 'user' if msg.sender == 'user' else 'assistant',
                'content': msg.content
            })
        
        # Get response from chatbot
        bot_response = get_chat_response(
            user_message.content, 
            history_formatted, 
            document_context
        )
        
        # Save bot response
        Message.objects.create(
            conversation=conversation,
            content=bot_response,
            sender='bot'
        )
        
        return user_message
