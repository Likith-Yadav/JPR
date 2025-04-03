from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
from django.templatetags.static import static
from django.utils import timezone
from .models import UserProfile, Transactions, PaymentCategory
from datetime import datetime, timedelta
import json
import hashlib
from hashlib import sha256
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from random import randint
import smtplib
from cashfree_pg.models.create_order_request import CreateOrderRequest
from cashfree_pg.api_client import Cashfree
from cashfree_pg.models.customer_details import CustomerDetails
from cashfree_pg.models.order_meta import OrderMeta
from urllib3.exceptions import InsecureRequestWarning
import warnings
from django.db.models import F
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import requests
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Image
import os
from django.conf import settings

warnings.filterwarnings("ignore", category=InsecureRequestWarning)
# Create your views here.
def home(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        
        # SMTP Configuration
        sender_email = "proxybroproxy@gmail.com"  # Use your Gmail account
        password = "Abcd@1234#"  # Add your app password or email password here
        # To get an app password for Gmail:
        # 1. Enable 2-Step Verification on your Google account
        # 2. Go to https://myaccount.google.com/apppasswords
        # 3. Select "Mail" and your device, then generate
        # 4. Use the 16-character password generated here
        recipient_email = "yushaoffline@gmail.com"
        # recipient_email = "info.jpreducation@gmail.com"  # Where you want to receive messages
        
        # Create email
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = f"Contact Form Submission from {name}"
        
        # Email body
        body = f"""
        You have received a new message from the contact form:
        
        Name: {name}
        Email: {email}
        
        Message:
        {message}
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        try:
            # Connect to Gmail SMTP server
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(sender_email, password)
            
            # Send email
            server.send_message(msg)
            server.quit()
            
            messages.success(request, 'Thank you for your message! We will get back to you soon.')
        except Exception as e:
            messages.error(request, f'Sorry, there was an error sending your message. Please try again later.')
            
        return redirect('/#Contact-Us')
        
    return render(request,'index.html',{"user":str(request.user)})

def loginUser(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request,username=username, password=password)
        if user is not None:
            login(request,user)
            messages.success(request, str(request.user)+'Login successful.')
            return redirect('/dashboard/'+str(request.user))
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request,'student_dash/login.html')


def registerUser(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        name = request.POST.get('name')
        user_class = request.POST.get('class')
        father_name = request.POST.get('father_name')
        phone_number = request.POST.get('phone_number')
        alt_number = request.POST.get('alt_number')
        address = request.POST.get('address')
        otp = request.POST.get('otp')
        if str(otp) != str(request.session['otp']):
            messages.error(request, 'Invalid OTP. Please try again.')
            return redirect('register')
        otp_created_time = datetime.fromisoformat(request.session['otp_created_at'])
        if datetime.now() - otp_created_time > timedelta(minutes=10):
            del request.session['otp']
            del request.session['otp_created_at']
            request.session.modified = True
            return JsonResponse({"error": "OTP has expired."}, status=400)
        # Validate input (add your own validation logic)
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return redirect('register')
        
        if UserProfile.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return redirect('register')

        # Create the User object
        user = User.objects.create(
            username=username,
            password=make_password(password)  # Hash the password
        )
        UserProfile.objects.create(
            user=user,
            Name=name,
            Class=user_class,
            Father_name=father_name,
            phone_number=phone_number,
            alt_number=alt_number,
            address=address,
            email=email
        )

        messages.success(request, 'Registration successful! You can now log in.')
        return redirect('login')

    return render(request,'student_dash/register.html')


def dashboard(request,username):
    if request.user.is_superuser==False:
        if str(request.user) != username:
            return redirect('login')
    user = User.objects.get(username=username)
    user_profile = UserProfile.objects.get(user=user)
    user_data = {
        'username': user.username,
        'email': user_profile.email,
        'name': user_profile.Name,
        'class': user_profile.Class,
        'father_name': user_profile.Father_name,
        'phone_number': user_profile.phone_number,
        'alt_number': user_profile.alt_number,
        'address': user_profile.address,
        'fee_due': user_profile.Fee_Due,
        'registration_number': user_profile.registration_number,
        'profile_image': user_profile.profile_image.url if user_profile.profile_image else None,
    }
    transactions = Transactions.objects.filter(user=user).order_by('-date')
    return render(request,'student_dash/dashboard.html',{"student":user_data,'transactions': transactions})

def gallery(request):
    return render(request, 'gallery.html')

def otp_api(request):
    if request.method == "POST":
        data = json.loads(request.body)
        to_email = data.get('email')
        action = data.get('action')
        if action == 'forgot':
            if UserProfile.objects.filter(email=to_email).exists():
                pass
            else:
                return JsonResponse({'message': 'Email not found!'}, status=400)
        my_email = "rishi71213@gmail.com"
        password = ""
        gmail_server = "smtp.gmail.com"
        gmail_port = 587
        my_server = smtplib.SMTP(gmail_server,gmail_port)
        my_server.ehlo()
        my_server.starttls()
        my_server.login(my_email,password)
        otp = randint(100000,999999)
        request.session['otp'] = otp
        request.session['otp_created_at'] = datetime.now().isoformat()
        request.session.modified = True
        if action == 'forgot':
            m = "Your OTP for password change is "+str(otp)+" This OTP is valid for 10 minutes.Don't share this OTP with anyone."
        else:
            m = "Hello, Welcome to School! Your OTP is "+str(otp)+" This OTP is valid for 10 minutes.Don't share this OTP with anyone."
        msg1 = MIMEText(m, "plain", "utf-8")
        my_server.sendmail(from_addr=my_email,to_addrs=to_email, msg=msg1.as_string())
        print("Email sent!")
        return JsonResponse({'message': 'OTP sent!'}, status=201)
    else:
        print("Problem sending email")
    return JsonResponse({'message': 'OTP not sent!'}, status=400)

def logoutUser(request):
    logout(request)
    return redirect('home')

def change_password(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        otp = data.get('otp')
        email = data.get('email')
        new_password = data.get('newPassword')
        if str(otp) != str(request.session['otp']):
            messages.error(request, 'Invalid OTP. Please try again.')
            return redirect('change_password')
        otp_created_time = datetime.fromisoformat(request.session['otp_created_at'])
        if datetime.now() - otp_created_time > timedelta(minutes=10):
            del request.session['otp']
            del request.session['otp_created_at']
            request.session.modified = True
            return JsonResponse({"error": "OTP has expired."}, status=400)
        user = UserProfile.objects.get(email=email).user
        if user is not None:
            user.set_password(new_password)
            user.save()
            messages.success(request, 'Password changed successfully.')
            return redirect('login')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request,'student_dash/forgot_pass.html')

def serialize_order_entity(order_entity):
    return {
    "cart_details": order_entity.cart_details,
    "cf_order_id": order_entity.order_id,
    "created_at": order_entity.created_at,
    "customer_details": {
        "customer_id": order_entity.customer_details.customer_id,    
        "customer_name": order_entity.customer_details.customer_name,
        "customer_email": order_entity.customer_details.customer_email,
        "customer_phone": order_entity.customer_details.customer_phone,
        "customer_uid": order_entity.customer_details.customer_uid
    },
    "entity": order_entity.entity,
    "order_amount": order_entity.order_amount,
    "order_currency": order_entity.order_currency,
    "order_expiry_time": order_entity.order_expiry_time,
    "order_id": order_entity.order_id,  
    "order_meta": {
        "return_url": order_entity.order_meta.return_url,
        "notify_url": order_entity.order_meta.notify_url,
        "payment_methods": order_entity.order_meta.payment_methods
    },
    "order_note": order_entity.order_note,
    "order_splits": order_entity.order_splits,
    "order_status": order_entity.order_status,
    "order_tags": order_entity.order_tags,
    "payment_session_id": order_entity.payment_session_id,
    "terminal_data": "",
}

def serialize_payment_method(payment_method):
    return {
        "oneof_schema_1_validator": payment_method.oneof_schema_1_validator,
        "oneof_schema_2_validator": payment_method.oneof_schema_2_validator,
        "oneof_schema_3_validator": payment_method.oneof_schema_3_validator,
        "oneof_schema_4_validator": payment_method.oneof_schema_4_validator,
        "oneof_schema_5_validator": payment_method.oneof_schema_5_validator,
        "oneof_schema_6_validator": payment_method.oneof_schema_6_validator,
        "oneof_schema_7_validator": payment_method.oneof_schema_7_validator,
        "oneof_schema_8_validator": payment_method.oneof_schema_8_validator,
        "actual_instance": {
            "upi": {
                "channel": payment_method.actual_instance.upi.channel,
                "upi_id": payment_method.actual_instance.upi.upi_id
            }
        },
        "one_of_schemas": payment_method.one_of_schemas,
    }

def serialize_payment_entity(payment_entity):
    return {
        "cf_payment_id": payment_entity.cf_payment_id,
        "order_id": payment_entity.order_id,
        "entity": payment_entity.entity,
        "error_details": payment_entity.error_details,
        "is_captured": payment_entity.is_captured,
        "order_amount": payment_entity.order_amount,
        "payment_group": payment_entity.payment_group,
        "payment_currency": payment_entity.payment_currency,
        "payment_amount": payment_entity.payment_amount,
        "payment_time": payment_entity.payment_time,
        "payment_completion_time": payment_entity.payment_completion_time,
        "payment_status": payment_entity.payment_status,
        "payment_message": payment_entity.payment_message,
        "bank_reference": payment_entity.bank_reference,
        "auth_id": payment_entity.auth_id,
        "authorization": payment_entity.authorization,
        "payment_method": serialize_payment_method(payment_entity.payment_method),
    }



def create_order(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        amount = data.get('amount')

        Cashfree.XClientId = "TEST430329ae80e0f32e41a393d78b923034"
        Cashfree.XClientSecret = "TESTaf195616268bd6202eeb3bf8dc458956e7192a85"
        Cashfree.XEnvironment = Cashfree.SANDBOX
        x_api_version = "2023-08-01"

        customerDetails = CustomerDetails(customer_id=str(request.user), customer_phone="9999999999")    
        customerDetails.customer_name = UserProfile.objects.get(user=request.user).Name 
        customerDetails.customer_email = UserProfile.objects.get(user=request.user).email
        order_id = str(request.user)+str(datetime.now()).replace(" ","").replace(":","").replace(".","")
        createOrderRequest = CreateOrderRequest(order_id=order_id, order_amount=float(amount), order_currency="INR", customer_details=customerDetails)
        orderMeta = OrderMeta()
        orderMeta.return_url = "https://www.cashfree.com/devstudio/preview/pg/web/popupCheckout?order_id={order_id}"
        orderMeta.notify_url = "https://www.cashfree.com/devstudio/preview/pg/webhooks/8020517"
        orderMeta.payment_methods = "cc,dc,upi"
        createOrderRequest.order_meta = orderMeta

        try:
            api_response = Cashfree().PGCreateOrder(x_api_version, createOrderRequest, None, None)
            #print(api_response.data)
            return JsonResponse(serialize_order_entity(api_response.data), status=201)
        except Exception as e:
            print(e)
        return JsonResponse({"error": "Error creating order."}, status=400)
    
def verify_payment(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        order_id = data.get('order_id')
        Cashfree.XClientId = "TEST430329ae80e0f32e41a393d78b923034"
        Cashfree.XClientSecret = "TESTaf195616268bd6202eeb3bf8dc458956e7192a85"
        Cashfree.XEnvironment = Cashfree.SANDBOX
        x_api_version = "2023-08-01"
        try:
            api_response = Cashfree().PGOrderFetchPayments(x_api_version, str(order_id), None)
            res = serialize_payment_entity(api_response.data[0])
            print(res)
            Transactions.objects.create(
            user=request.user,
            amount=res['payment_amount'],
            transaction_id=res['cf_payment_id'],
            status=True if res['payment_status'] == 'SUCCESS' else False,
            payment_mode = "Online-"+str(list(res['payment_method']['actual_instance'].keys())[0]),
            date = res['payment_time']
            )
            if res['payment_status'] == 'SUCCESS':
                UserProfile.objects.filter(user=request.user).update(Fee_Due=UserProfile.objects.get(user=request.user).Fee_Due - res['payment_amount'])
            return JsonResponse(res, status=200)
        except Exception as e:
            print(e)
        return JsonResponse({"error": "Error fetching order status."}, status=400)
    

def update_fee(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        amount = data.get('fee')
        users = data.get('queryset')
        for user in users:
            UserProfile.objects.filter(user=User.objects.get(username=user)).update(Fee_Due=F("Fee_Due")+amount)
        messages.success(request, 'Fee updated successfully.')
        return JsonResponse({"message": "Fee updated successfully."}, status=200)
    return JsonResponse({"error": "Error updating fee."}, status=400)





def download_receipt(request, transaction_id):
    """
    Generate and download the receipt as a PDF using reportlab.
    """
    # Fetch transaction and user details from the database
    transaction = get_object_or_404(Transactions, transaction_id=transaction_id)
    user_profile = get_object_or_404(UserProfile, user=transaction.user)

    # Create the PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="Receipt_{transaction_id}.pdf"'
    
    # Create the PDF document with adjusted margins for border
    doc = SimpleDocTemplate(
        response,
        pagesize=letter,
        rightMargin=50,
        leftMargin=50,
        topMargin=50,
        bottomMargin=50
    )
    styles = getSampleStyleSheet()
    elements = []

    # Create a frame with rounded corners
    frame_data = [['']]
    main_table = Table(frame_data, colWidths=[450])
    main_table.setStyle(TableStyle([
        ('ROUNDEDCORNERS', (0, 0), (-1, -1), 10),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (-1, -1), colors.white),
    ]))

    # Content elements list
    content = []

    # Add logo centered at the top with larger dimensions
    try:
        # Get the absolute path to the logo file
        logo_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'logo.png')
        if os.path.exists(logo_path):
            # Increased size for better visibility
            logo = Image(logo_path, width=4*inch, height=1.2*inch)
            logo.hAlign = 'CENTER'
            content.append(logo)
            content.append(Spacer(1, 10))
    except Exception as e:
        print(f"Error loading logo: {e}")
        pass

    # Add school name
    school_name = ParagraphStyle(
        'SchoolName',
        parent=styles['Heading1'],
        fontSize=16,
        alignment=TA_CENTER,
        spaceAfter=5
    )
    content.append(Paragraph("JPR Public School", school_name))
    content.append(Paragraph("Educating for a Brighter Future", ParagraphStyle(
        'Tagline',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_CENTER,
        spaceAfter=15
    )))

    # Add horizontal line
    line = Table([['']], colWidths=[450])
    line.setStyle(TableStyle([
        ('LINEABOVE', (0, 0), (-1, 0), 1, colors.black),
    ]))
    content.append(line)
    content.append(Spacer(1, 10))

    # Rest of your existing code for receipt content
    receipt_header = ParagraphStyle(
        'ReceiptHeader',
        parent=styles['Heading2'],
        fontSize=14,
        alignment=TA_CENTER,
        spaceAfter=10
    )
    content.append(Paragraph("Transaction Receipt", receipt_header))
    content.append(Spacer(1, 10))

    # Student Details
    detail_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
    ])

    student_data = [
        ['Student Name', user_profile.Name],
        ['Registration Number', user_profile.registration_number],
        ['Class', user_profile.Class],
        ['Date', transaction.date.strftime('%d %b %Y %H:%M')],
        ['Payment Mode', transaction.payment_mode],
        ['Transaction ID', transaction.transaction_id],
        ['Received By', transaction.received_by if transaction.received_by else '']
    ]
    
    student_table = Table(student_data, colWidths=[150, 300])
    student_table.setStyle(detail_style)
    content.append(student_table)
    content.append(Spacer(1, 10))

    # Payment Details
    content.append(Paragraph("Payment Details", receipt_header))
    content.append(Spacer(1, 5))

    payment_data = [['Category', 'Amount', 'Description']]
    for category in transaction.categories.all():
        payment_data.append([
            category.get_category_display(),
            "Rs. " + str(category.amount),
            category.description if category.description else ''
        ])
    
    payment_data.append(['Total Amount', "Rs. " + str(transaction.total_amount), ''])
    payment_data.append(['Fee Due', "Rs. " + str(user_profile.Fee_Due), ''])

    payment_table = Table(payment_data, colWidths=[150, 150, 150])
    payment_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
        ('FONTNAME', (-2, -2), (-2, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
    ]))
    content.append(payment_table)

    # Footer
    content.append(Spacer(1, 15))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.gray,
        alignment=TA_CENTER,
        spaceBefore=0
    )
    if transaction.status:
        content.append(Paragraph("Digitally Signed by Public School", footer_style))
        hash_data = f"{transaction.transaction_id}{transaction.date}{transaction.total_amount}".encode()
        digital_signature = sha256(hash_data).hexdigest()
        content.append(Paragraph(digital_signature, footer_style))
    
    content.append(Spacer(1, 10))
    content.append(Paragraph("Thank you for your payment!", footer_style))
    content.append(Paragraph("For queries, contact support@publicschool.com", footer_style))

    # Create the main table with rounded corners and add all content
    main_table._cellvalues[0][0] = content
    elements.append(main_table)

    # Build the PDF
    doc.build(elements)
    return response

def gallery(request):
    return render(request, 'gallery.html')
