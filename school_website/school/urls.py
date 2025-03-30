from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('',views.home,name='home'),
    path('login/',views.loginUser,name='login'),
    path('logout/',views.logoutUser,name='logout'),
    path('register/',views.registerUser,name='register'),
    path('otp_api/',views.otp_api,name='otp_api'),
    path('change_password/',views.change_password,name='change_password'),
    path('create_order/',views.create_order,name='create_order'),
    path('verify_payment/',views.verify_payment,name='verify_payment'),
    path('update_fee/',views.update_fee,name='update_fee'),
    path('download_receipt/<str:transaction_id>/', views.download_receipt, name='download_receipt'),
    path('dashboard/<str:username>/',views.dashboard,name='dashboard'),
    path('gallery/', views.gallery, name='gallery'),
]