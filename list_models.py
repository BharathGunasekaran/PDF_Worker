
import google.generativeai as genai

genai.configure(api_key="AIzaSyCi0liYJES68qTMg-8RwbYPVaZFdD1uKo4")  # Replace with your actual key

for model in genai.list_models():
    print(f"Model: {model.name}")
    for method in model.supported_generation_methods:
        print(f"- Supports: {method}")