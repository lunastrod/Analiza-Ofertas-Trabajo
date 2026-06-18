import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client()
prompt = "Buscamos programador Python y SQL. ¿Qué tecnologías piden?"

response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=prompt,
)

print(response.text)