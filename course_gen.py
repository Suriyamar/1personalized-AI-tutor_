# course_generator/course_gen.py

import ollama

def generate_outline_stream(prompt):
    """
    Yields streamed responses from Ollama (Gemma 2B).
    """
    response = ollama.chat(
        model="llama3:8b",
        messages=[{"role": "user", "content": prompt}],
        stream=True
    )

    full_output = ""
    for chunk in response:
        full_output += chunk['message']['content']
        yield full_output