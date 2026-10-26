import os

import google.generativeai as genai
from dotenv import load_dotenv

# Reads GEMINI_API_KEY from pdf_project/.env (never hardcode API keys)
load_dotenv("pdf_project/.env")
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

for model in genai.list_models():
    print(f"Model: {model.name}")
    for method in model.supported_generation_methods:
        print(f"- Supports: {method}")
