from django.urls import path
from . import views

app_name = 'expression'
urlpatterns = [
    path('', views.summary, name='main'),
    path('summary/', views.summary, name= 'summary'),
    path('transcript/', views.transcript_identify, name= 'transcript')
]

if settings.DEBUG:
    urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)