import ollama

def generate_response(messages):
    stream = ollama.chat(
        model='llama3.2:1b',
        messages=messages,
        stream=True,
    )
    for chunk in stream:
        yield chunk

