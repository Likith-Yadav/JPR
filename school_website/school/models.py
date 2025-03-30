from django.contrib.auth.models import User
from django.db import models
from datetime import datetime

# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    Name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    Fee_Due = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    Class = models.CharField(max_length=3) 
    Father_name = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    alt_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    registration_number = models.CharField(max_length=20, unique=True, null=True, blank=True, help_text="Student's unique registration number")
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)

    def __str__(self):
        return self.Name

class PaymentCategory(models.Model):
    CATEGORY_CHOICES = [
        ('tuition', 'Tuition'),
        ('transport', 'Transport'),
        ('book', 'Book'),
        ('uniform', 'Uniform'),
        ('competitive', 'Competitive'),
        ('celebrations', 'Celebrations'),
        ('admission', 'Admission'),
        ('application', 'Application'),
        ('others', 'Others'),
    ]
    
    transaction = models.ForeignKey('Transactions', on_delete=models.CASCADE, related_name='categories')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True, help_text='Required for Others category')

    def __str__(self):
        return f"{self.get_category_display()} - ₹{self.amount}"

    class Meta:
        verbose_name_plural = "Payment Categories"

class Transactions(models.Model):
    PAYMENT_MODES = (
        ('Online', 'Online'),
        ('Cash', 'Cash'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(null=True, blank=True)
    time = models.TimeField(null=True, blank=True)
    transaction_id = models.CharField(max_length=100, unique=True)
    status = models.BooleanField(default=False)
    payment_mode = models.CharField(max_length=10, choices=PAYMENT_MODES)
    received_by = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Transactions"

    def __str__(self):
        return f"{self.user.username} - {self.total_amount} - {self.date} {self.time}"

    def save(self, *args, **kwargs):
        if not self.date:
            self.date = datetime.now().date()
        if not self.time:
            self.time = datetime.now().time()
        super().save(*args, **kwargs)
    
