# 📄 PDF Worker

A Django web app that makes PDFs easier to work with using **Google Gemini**. Upload a PDF,
then summarise it, translate it, ask questions about it, or listen to it as audio.

## Features

- 📤 Upload any text-based PDF
- 📝 **Summarise** the whole document
- 🌐 **Translate** the content into another language
- ❓ **Ask questions** and get answers based on the document
- 🔊 **Listen** to the text with text-to-speech (gTTS)
- ⬇️ Download the results as PDF, text or audio

## Tech stack

| Area | Technology |
|---|---|
| Web framework | Django |
| AI | Google Gemini (`google-generativeai`) |
| PDF parsing | PyPDF2 |
| Text-to-speech | gTTS |
| Config | python-dotenv |

## Getting started

### Prerequisites
- Python 3.10+
- A Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey)

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Add your API key
Create `pdf_project/.env`:
```env
GEMINI_API_KEY=your_gemini_api_key
```
Keep this file out of version control.

### 3. Run the app
```bash
python manage.py migrate
python manage.py runserver
```
Open http://127.0.0.1:8000/upload/ and upload a PDF.

## Project structure

```text
PDF_Worker/
├── pdf_project/          # Django settings and URLs
├── pdf_app/
│   ├── views.py          # Upload, summarise, translate, Q&A, voice and download views
│   ├── urls.py
│   └── templates/        # Upload, process, summary and voice pages
├── list_models.py        # Helper that lists the Gemini models available to your key
└── requirements.txt
```
