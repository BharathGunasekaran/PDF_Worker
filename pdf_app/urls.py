from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.UploadPDFView.as_view(), name='upload_pdf'),
    path('process/', views.ProcessPDFView.as_view(), name='process_pdf'),
    path('voice/', views.VoiceOutputView.as_view(), name='voice_output'),
    path('download/pdf/', views.DownloadPDFView.as_view(), name='download_pdf'),
    path('download/text/', views.DownloadTextView.as_view(), name='download_text'),
    path('<str:audio_file>/', views.serve_audio, name='serve_audio'), # To serve the audio file
    path('delete_audio/<str:filename>/', views.delete_audio, name='delete_audio'), # Optional: for cleanup
    path('download/audio/<str:audio_file>/', views.serve_audio, name='download_audio'),
]