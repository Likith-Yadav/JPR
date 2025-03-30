from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
import io
from reportlab.pdfgen import canvas
# Import other necessary modules

def download_receipt(request, transaction_id):
    # Check if user is either admin or the student who made the transaction
    transaction = get_object_or_404(Transaction, transaction_id=transaction_id)
    
    if not (request.user.is_staff or request.user == transaction.student.user):
        return HttpResponse("Unauthorized", status=403)

    # Create the PDF
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)

    # Add receipt content
    p.drawString(100, 800, f"Receipt #{transaction.transaction_id}")
    p.drawString(100, 780, f"Date: {transaction.date}")
    p.drawString(100, 760, f"Student: {transaction.student.name}")
    p.drawString(100, 740, f"Amount: ₹{transaction.amount}")
    p.drawString(100, 720, f"Payment Mode: {transaction.payment_mode}")
    p.drawString(100, 700, f"Status: {transaction.status}")
    
    # Add more receipt details as needed

    p.showPage()
    p.save()
    
    # FileResponse sets the Content-Disposition header
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=receipt_{transaction_id}.pdf'
    
    return response

# If you want a separate view for admin
@staff_member_required
def admin_download_receipt(request, transaction_id):
    return download_receipt(request, transaction_id) 