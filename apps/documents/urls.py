"""
URL patterns for document endpoints.
"""
from django.urls import path
from . import views

app_name = 'documents'

urlpatterns = [
    # Document operations
    path('', views.list_documents_view, name='list_documents'),
    path('upload/', views.upload_document_view, name='upload_document'),
    path('<int:document_id>/', views.get_document_view, name='get_document'),
    path('<int:document_id>/download/', views.download_document_view, name='download_document'),
    path('<int:document_id>/update/', views.update_document_view, name='update_document'),
    path('<int:document_id>/delete/', views.delete_document_view, name='delete_document'),
]

