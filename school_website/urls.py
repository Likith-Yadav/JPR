from django.urls import path
from . import views

urlpatterns = [
    # Existing URLs
    path('download-receipt/<str:transaction_id>/', views.download_receipt, name='download_receipt'),
    path('admin/download-receipt/<str:transaction_id>/', views.admin_download_receipt, name='admin_download_receipt'),
] 