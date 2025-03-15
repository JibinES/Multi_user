from rest_framework import serializers
from .models import Conversation, Message, Document

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ('id', 'title', 'file', 'uploaded_at', 'user')
        read_only_fields = ('user', 'content')

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ('id', 'content', 'sender', 'timestamp', 'document')
        read_only_fields = ('timestamp',)

class ConversationSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Conversation
        fields = ('id', 'title', 'created_at', 'messages', 'user')
        read_only_fields = ('user',)
