from django.urls import path,include
from . import views
urlpatterns = [
    path('',views.pay_fee,name='pay_fee'),
]