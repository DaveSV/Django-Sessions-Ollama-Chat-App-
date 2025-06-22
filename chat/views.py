# chat/views.py

import json
from django.shortcuts import render
from django.http import StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from .ollama_api import generate_response

SYSTEM_PROMPT = {
    'role': 'system',
    'content': (
        'Responde exclusivamente en una oración corta y clara. '
        'Evita adornos o explicaciones largas. '
        'Recuerda las preguntas anteriores y responde de forma coherente con el contexto.'
    )
}

MAX_HISTORY = 12

@csrf_exempt
def chat_view(request):
    print("\n--- INICIO DE CHAT_VIEW ---")
    print(f"Método de la solicitud: {request.method}")
    print(f"Session Key inicial: {request.session.session_key}")
    print(f"Cookies recibidas: {request.COOKIES}")

    if request.method == "POST":
        user_input = request.POST.get("user_input", "").strip()
        if not user_input:
            return StreamingHttpResponse("Entrada vacía.", content_type='text/plain')

        # Obtener historial desde sesión.
        chat_history = list(request.session.get('chat_history', []))
        
        # --- DEBUG: Después de cargar de la sesión ---
        print(f"DEBUG: chat_history *después de cargar de la sesión*: {json.dumps(chat_history, indent=2, ensure_ascii=False)}")

        # Asegúrate de que el SYSTEM_PROMPT esté al inicio si el historial está vacío o no lo tiene
        if not chat_history or (chat_history and chat_history[0]['role'] != 'system'):
            chat_history.insert(0, SYSTEM_PROMPT)

        # Agregar mensaje del usuario
        chat_history.append({'role': 'user', 'content': user_input})

        # Limitar historial (asegurando el SYSTEM_PROMPT se mantiene)
        if len(chat_history) > MAX_HISTORY + 1:
            chat_history = [chat_history[0]] + chat_history[1:][-(MAX_HISTORY):]

        print("\n=== Historial enviado a Ollama ===")
        print(json.dumps(chat_history, indent=2, ensure_ascii=False))
        print("=== Fin del historial ===\n")

        response_generator = generate_response(chat_history)

        def stream_and_save_response(current_chat_history, current_request):
            full_assistant_response = ''
            for chunk in response_generator:
                content = chunk['message']['content']
                full_assistant_response += content
                yield content

            current_chat_history.append({'role': 'assistant', 'content': full_assistant_response})
            
            # Limitar historial nuevamente antes de guardar (mantiene SYSTEM_PROMPT)
            if len(current_chat_history) > MAX_HISTORY + 1:
                current_chat_history = [current_chat_history[0]] + current_chat_history[1:][-(MAX_HISTORY):]

            current_request.session['chat_history'] = current_chat_history
            current_request.session.modified = True
            current_request.session.save() # <-- ¡NUEVA LÍNEA CLAVE!
            
            print(f"\n--- DEBUG: Sesión guardada con historial final. Modified: {current_request.session.modified} ---")
            print(f"DEBUG: Historial guardado en request.session['chat_history'] es: {json.dumps(current_request.session.get('chat_history'), indent=2, ensure_ascii=False)}")
            print("--- FIN stream_and_save_response ---")

        return StreamingHttpResponse(stream_and_save_response(chat_history, request), content_type='text/plain')

    # GET: renderizar plantilla de chat
    return render(request, "chat.html")
