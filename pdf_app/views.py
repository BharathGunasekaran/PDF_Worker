import os
import PyPDF2
import google.generativeai as genai
from django.shortcuts import render, redirect
from django.views import View
from django.conf import settings
from django.http import FileResponse, HttpResponseNotFound, HttpResponseServerError
import time
from google.api_core import exceptions as google_exceptions
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from io import BytesIO
from gtts import gTTS
import pygame
import time


genai.configure(api_key=settings.GEMINI_API_KEY)
model = genai.GenerativeModel('models/gemini-1.5-flash')

class UploadPDFView(View):
    def get(self, request):
        return render(request, 'upload_pdf.html')

    def post(self, request):
        pdf_file = request.FILES.get('pdf_file')
        if pdf_file and pdf_file.name.endswith('.pdf'):
            try:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                text = ""
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text()

                if text:
                    request.session['pdf_text'] = text  # Store text in session for other views
                    return redirect('process_pdf')
                else:
                    error_message = "Could not extract text from the PDF."
                    return render(request, 'upload_pdf.html', {'error': error_message})

            except Exception as e:
                error_message = f"Error processing PDF: {e}"
                return render(request, 'upload_pdf.html', {'error': error_message})
        else:
            error_message = "Please upload a valid PDF file."
            return render(request, 'upload_pdf.html', {'error': error_message})

class ProcessPDFView(View):
    def get(self, request):
        pdf_text = request.session.get('pdf_text')
        if not pdf_text:
            return redirect('upload_pdf')
        return render(request, 'process_pdf.html')

    def post(self, request):
        pdf_text = request.session.get('pdf_text')
        if not pdf_text:
            return redirect('upload_pdf')

        action = request.POST.get('action')

        if action == 'summarize':
            prompt = f"Summarize: {pdf_text}"
            retries = 3
            wait_time = 1  # Initial wait time in seconds
            for i in range(retries):
                try:
                    response = model.generate_content(prompt)
                    summary = response.text
                    return render(request, 'summary.html', {'result': summary, 'type': 'summary'})
                except google_exceptions.ResourceExhausted as e:
                    if i < retries - 1:
                        wait_time *= 2  # Exponential backoff
                        time.sleep(wait_time)
                        print(f"Rate limit exceeded. Retrying in {wait_time} seconds...")
                    else:
                        error_message = f"Rate limit exceeded after multiple retries: {e}"
                        return render(request, 'process_pdf.html', {'error': error_message})
                except Exception as e:
                    error_message = f"Error during summarization: {e}"
                    return render(request, 'process_pdf.html', {'error': error_message})
            return render(request, 'process_pdf.html', {'error': "Summarization failed."})

        elif action == 'translate':
            target_language = request.POST.get('language', 'en') # Default to English
            prompt = f"Translate the following text to {target_language}:\n\n{pdf_text}"
            retries = 3
            wait_time = 1
            for i in range(retries):
                try:
                    response = model.generate_content(prompt)
                    translation = response.text
                    return render(request, 'summary.html', {'result': translation, 'type': 'translation', 'language': target_language})
                except google_exceptions.ResourceExhausted as e:
                    if i < retries - 1:
                        wait_time *= 2
                        time.sleep(wait_time)
                        print(f"Rate limit exceeded. Retrying translation in {wait_time} seconds...")
                    else:
                        error_message = f"Rate limit exceeded after multiple retries during translation: {e}"
                        return render(request, 'process_pdf.html', {'error': error_message})
                except Exception as e:
                    error_message = f"Error during translation: {e}"
                    return render(request, 'process_pdf.html', {'error': error_message})
            return render(request, 'process_pdf.html', {'error': "Translation failed."})

        elif action == 'ask':
            question = request.POST.get('question')
            if question:
                prompt = f"Answer the following question based on the text provided:\n\nText:\n{pdf_text}\n\nQuestion: {question}\n\nAnswer:"
                retries = 3
                wait_time = 1
                for i in range(retries):
                    try:
                        response = model.generate_content(prompt)
                        answer = response.text
                        return render(request, 'summary.html', {'result': answer, 'type': 'answer', 'question': question})
                    except google_exceptions.ResourceExhausted as e:
                        if i < retries - 1:
                            wait_time *= 2
                            time.sleep(wait_time)
                            print(f"Rate limit exceeded. Retrying question in {wait_time} seconds...")
                        else:
                            error_message = f"Rate limit exceeded after multiple retries during question answering: {e}"
                            return render(request, 'process_pdf.html', {'error': error_message})
                    except Exception as e:
                        error_message = f"Error during question answering: {e}"
                        return render(request, 'process_pdf.html', {'error': error_message})
                return render(request, 'process_pdf.html', {'error': "Question answering failed."})
            else:
                return render(request, 'process_pdf.html', {'error': 'Please enter a question.'})

        return render(request, 'process_pdf.html')

# For simplicity, we'll handle voice output separately (you'd likely integrate with a TTS service)
class VoiceOutputView(View):
    def post(self, request):
        text_to_speak = request.POST.get('text_to_speak')
        if text_to_speak:
            time.sleep(200)  # Keep the delay for rate limiting
            tts = gTTS(text=text_to_speak, lang='en', tld='com')
            filename = "voice_output.mp3"
            try:
                tts.save(filename)
                print(f"Audio file saved as: {filename}")  # Debugging
                return render(request, 'play_voice.html', {'audio_file': filename})
            except Exception as e:
                error_message = f"Error generating audio: {e}"
                print(f"Error during audio generation: {error_message}")  # Debugging
                return render(request, 'play_voice.html', {'error': error_message, 'text': text_to_speak}) # Pass error to template
        return redirect('process_pdf')
    

class DownloadPDFView(View):
    def post(self, request):
        content = request.POST.get('content')
        filename = request.POST.get('filename', 'download.pdf')
        buffer = BytesIO()
        p = canvas.Canvas(buffer)
        p.drawString(100, 750, content)
        p.showPage()
        p.save()
        buffer.seek(0)
        response = FileResponse(buffer, as_attachment=True, filename=filename)
        return response
    
class DownloadTextView(View):
    def post(self, request):
        content = request.POST.get('content')
        filename = request.POST.get('filename', 'output.txt')
        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    
def serve_audio(request, audio_file):
    file_path = os.path.join(os.getcwd(), audio_file) # Adjust path if needed
    if os.path.exists(file_path):
        return FileResponse(open(file_path, 'rb'), content_type='audio/mpeg')
    else:
        return HttpResponseNotFound("Audio file not found")

def delete_audio(request, filename):
    file_path = os.path.join(os.getcwd(), filename) # Adjust path if needed
    try:
        os.remove(file_path)
        return HttpResponse("Audio file deleted", status=200)
    except FileNotFoundError:
        return HttpResponseNotFound("Audio file not found")
    except Exception as e:
        return HttpResponseServerError(f"Error deleting audio file: {e}")