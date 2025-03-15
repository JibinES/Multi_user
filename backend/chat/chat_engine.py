# backend/chat/chat_engine.py
import os
import json
from langchain_community.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from langchain.chains import ConversationalRetrievalChain
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import CharacterTextSplitter
import openai
# Replace with your chosen LLM API key and configuration
openai.api_key = os.environ.get("OPENAI_API_KEY", "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")

def get_chat_response(query, conversation_history=None, document_context=None):
    """
    Generate a response using the chat model
    """
    if conversation_history is None:
        conversation_history = []
    
    try:
        if document_context:
            # Create a vector store from the document context for retrieval
            text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
            texts = text_splitter.split_text(document_context)
            
            # Create embeddings and vector store
            embeddings = OpenAIEmbeddings()
            vectorstore = FAISS.from_texts(texts=texts, embedding=embeddings)
            
            # Create a conversational chain that can reference the document
            chat = ChatOpenAI(temperature=0)
            qa_chain = ConversationalRetrievalChain.from_llm(
                llm=chat,
                retriever=vectorstore.as_retriever(),
                return_source_documents=True
            )
            
            # Format history for the chain
            formatted_history = []
            for message in conversation_history:
                if message['role'] == 'user':
                    formatted_history.append(f"Human: {message['content']}")
                else:
                    formatted_history.append(f"AI: {message['content']}")
                    
            # Get response from the chain
            result = qa_chain({"question": query, "chat_history": formatted_history})
            return result['answer']
        else:
            # For general queries without document context
            messages = [SystemMessage(content="You are a helpful assistant.")]
            
            # Add conversation history
            for message in conversation_history:
                if message['role'] == 'user':
                    messages.append(HumanMessage(content=message['content']))
                else:
                    messages.append(AIMessage(content=message['content']))
            
            # Add the current query
            messages.append(HumanMessage(content=query))
            
            # Get response from OpenAI
            chat = ChatOpenAI(temperature=0.7)
            response = chat(messages)
            return response.content
    
    except Exception as e:
        print(f"Error in chat engine: {e}")
        return "I'm sorry, I encountered an error processing your request."
