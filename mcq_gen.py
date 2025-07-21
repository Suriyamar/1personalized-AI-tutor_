import ollama

def generate_mcq(module_content, retrieved_context, num_questions=10):
    """
    Generate multiple-choice questions (MCQs) using gemma:2b based on module content.
    Incorporates additional retrieved context for a RAG approach.
    The prompt below explicitly requests exactly num_questions, using the proper format.
    """
    prompt = f"""
You are an expert educator. Based on the module content and additional context below, generate exactly {num_questions} multiple-choice questions.
IMPORTANT:
1. You MUST produce exactly {num_questions} questions, numbered sequentially from 1 to {num_questions}.
2. For each question, use this exact format (no extra text or punctuation):
   
   **Question 1:** <Question text>
   A) <Option A>
   B) <Option B>
   C) <Option C>
   D) <Option D>
   **Answer:** <Correct Option Letter>
   
   **Question 2:** <Question text>
   A) <Option A>
   B) <Option B>
   C) <Option C>
   D) <Option D>
   **Answer:** <Correct Option Letter>
   
   ... and so on.

Module Content:
--------------------
{module_content}
--------------------
Retrieved Context:
--------------------
{retrieved_context}
--------------------
If the module content is limited, create relevant questions anyway.
"""
    response = ollama.chat(
        model="gemma:2b",
        messages=[{"role": "user", "content": prompt}],
        stream=False
    )
    
    # Return the raw output for further parsing by the UI module.
    return response["message"]["content"]