from django.shortcuts import render

# Create your views here.
def pay_fee(request):
    return render(request,'payment.html')
