from django.contrib import admin
from django.shortcuts import render
from .models import UserProfile, Transactions, PaymentCategory
from django.contrib.admin import SimpleListFilter
from django.contrib import messages
from django.urls import path
from django.http import HttpResponse
from django.utils.html import format_html
from django import forms
from django.db.models import Q
from datetime import datetime, timedelta
from django.utils.safestring import mark_safe

admin.site.site_header = "\n"
admin.site.site_title = "Admin Portal"
admin.site.index_title = "Welcome to the School Admin"

class AmountRangeFilter(SimpleListFilter):
    title = 'Amount Range'
    parameter_name = 'amount_range'

    def lookups(self, request, model_admin):
        return (
            ('0-100', '0 - 100'),
            ('100-500', '100 - 500'),
            ('500-1000', '500 - 1000'),
            ('1000+', '1000+'),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            if value == '0-100':
                return queryset.filter(Fee_Due__gte=0, Fee_Due__lte=100)
            elif value == '100-500':
                return queryset.filter(Fee_Due__gte=100, Fee_Due__lte=500)
            elif value == '500-1000':
                return queryset.filter(Fee_Due__gte=500, Fee_Due__lte=1000)
            elif value == '1000+':
                return queryset.filter(Fee_Due__gte=1000)
        return queryset

def add_fee_due(modeladmin, request, queryset):
    usrs = []
    for q in queryset:
        usrs.append(q.user)
    return render(request, 'admin/fee_due_form.html', {'users': usrs})

add_fee_due.short_description = "Set Fee Due for selected users"

class FeeDueRangeFilter(SimpleListFilter):
    title = 'Fee Due Range'
    parameter_name = 'fee_due_range'

    def lookups(self, request, model_admin):
        return (
            ('0_5000', 'Less than ₹5,000'),
            ('5000_10000', '₹5,000 - ₹10,000'),
            ('10000_20000', '₹10,000 - ₹20,000'),
            ('20000_plus', 'More than ₹20,000'),
            ('no_dues', 'No Dues'),
        )

    def queryset(self, request, queryset):
        if self.value() == '0_5000':
            return queryset.filter(Fee_Due__lt=5000)
        if self.value() == '5000_10000':
            return queryset.filter(Fee_Due__gte=5000, Fee_Due__lt=10000)
        if self.value() == '10000_20000':
            return queryset.filter(Fee_Due__gte=10000, Fee_Due__lt=20000)
        if self.value() == '20000_plus':
            return queryset.filter(Fee_Due__gte=20000)
        if self.value() == 'no_dues':
            return queryset.filter(Fee_Due=0)

class PhoneVerifiedFilter(SimpleListFilter):
    title = 'Phone Verification'
    parameter_name = 'phone_verified'

    def lookups(self, request, model_admin):
        return (
            ('verified', 'Verified'),
            ('unverified', 'Unverified'),
            ('invalid', 'Invalid Number'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'verified':
            return queryset.filter(phone_number__regex=r'^\d{10}$')
        if self.value() == 'unverified':
            return queryset.filter(phone_number__isnull=True)
        if self.value() == 'invalid':
            return queryset.exclude(phone_number__regex=r'^\d{10}$').exclude(phone_number__isnull=True)

class UserProfileAdmin(admin.ModelAdmin):
    search_fields = ('Name', 'registration_number', 'Class', 'phone_number', 'email')
    list_display = ('get_profile_image', 'Name', 'registration_number', 'Class', 'phone_number', 'email', 'Fee_Due', 'view_transactions')
    list_filter = (
        'Class',
        FeeDueRangeFilter,
        PhoneVerifiedFilter,
        ('email', admin.EmptyFieldListFilter),  # Filter for empty/non-empty email
        'registration_number',
    )
    ordering = ('Name',)
    actions = [add_fee_due]
    readonly_fields = ('profile_image_preview',)

    def get_profile_image(self, obj):
        if obj.profile_image:
            return format_html('<img src="{}" width="80" height="80" style="border-radius: 50%; object-fit: cover; box-shadow: 0 2px 4px rgba(0,0,0,0.1);" />', obj.profile_image.url)
        return format_html('<img src="/static/images/default-profile.png" width="80" height="80" style="border-radius: 50%; object-fit: cover; box-shadow: 0 2px 4px rgba(0,0,0,0.1);" />')
    get_profile_image.short_description = ''

    def profile_image_preview(self, obj):
        if obj.profile_image:
            return mark_safe(f'<img src="{obj.profile_image.url}" style="max-height: 100px;"/>')
        return "No image"
    profile_image_preview.short_description = 'Profile Image Preview'

    fieldsets = (
        ('Personal Information', {
            'fields': ('Name', 'Class', 'Father_name', 'phone_number', 'alt_number', 'address', 'email', 'registration_number')
        }),
        ('Financial Information', {
            'fields': ('Fee_Due',)
        }),
        ('Profile Image', {
            'fields': ('profile_image', 'profile_image_preview'),
            'classes': ('collapse',)
        }),
    )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('transactions/<int:user_id>/', self.admin_site.admin_view(self.view_transaction_history), name='user-transactions'),
        ]
        return custom_urls + urls

    def view_transactions(self, obj):
        return format_html(
            '<a class="button" href="{}">View Transactions</a>',
            f'/admin/school/userprofile/transactions/{obj.user.id}/'
        )
    view_transactions.short_description = 'Transactions'

    def view_transaction_history(self, request, user_id):
        user_profile = UserProfile.objects.get(user_id=user_id)
        
        # Get all transactions for this user
        all_transactions = Transactions.objects.filter(user_id=user_id)
        
        # Get one-time fees (all non-tuition fees)
        one_time_fees = all_transactions.filter(
            ~Q(categories__category='tuition')
        ).distinct().order_by('-date')

        # Get all monthly fees (tuition)
        monthly_fees = all_transactions.filter(
            categories__category='tuition'
        ).order_by('date')

        # Create a list of months with payment status
        current_date = datetime.now().date()
        months = []
        
        # Get the earliest transaction date
        earliest_transaction = all_transactions.order_by('date').first()
        if earliest_transaction:
            start_date = earliest_transaction.date
        else:
            start_date = current_date - timedelta(days=365)
            
        # Generate months from earliest to current
        current_month = start_date.replace(day=1)
        while current_month <= current_date:
            month_str = current_month.strftime('%B %Y')
            
            # Get all transactions for this month (both tuition and one-time)
            month_transactions = all_transactions.filter(
                date__year=current_month.year,
                date__month=current_month.month,
                status=True  # Only count successful transactions
            )
            
            # Calculate total amount for this month including both tuition and one-time fees
            total_amount = sum(trans.total_amount for trans in month_transactions)
            
            # Get the latest transaction for this month
            latest_transaction = month_transactions.order_by('-date').first()
            
            # Get all categories for this month's transactions
            month_categories = []
            for trans in month_transactions:
                for category in trans.categories.all():
                    month_categories.append({
                        'category': category.get_category_display(),
                        'amount': category.amount
                    })
            
            months.append({
                'month': month_str,
                'paid': bool(latest_transaction),
                'transaction': latest_transaction,
                'total_amount': total_amount,
                'categories': month_categories
            })
            
            # Move to next month
            if current_month.month == 12:
                current_month = current_month.replace(year=current_month.year + 1, month=1)
            else:
                current_month = current_month.replace(month=current_month.month + 1)

        context = {
            'user_profile': user_profile,
            'one_time_fees': one_time_fees,
            'months': months,
            'opts': self.model._meta,
            'all_transactions': all_transactions,
        }
        return render(request, 'admin/transaction_history.html', context)

    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }
        js = ('admin/js/custom_admin.js',)

class PaymentCategoryInline(admin.TabularInline):
    model = PaymentCategory
    extra = 1
    fields = ('category', 'amount', 'description')

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        form = formset.form
        form.base_fields['description'].widget = forms.Textarea(attrs={'rows': 1})
        return formset

class TransactionsAdminForm(forms.ModelForm):
    class Meta:
        model = Transactions
        fields = '__all__'
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        # Ensure time is set
        if not cleaned_data.get('time'):
            cleaned_data['time'] = datetime.now().time()
        return cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:  # If this is a new transaction
            from datetime import datetime
            self.initial['time'] = datetime.now().time()
            self.initial['date'] = datetime.now().date()

class TransactionsAdmin(admin.ModelAdmin):
    form = TransactionsAdminForm
    inlines = [PaymentCategoryInline]
    search_fields = ['transaction_id', 'user__username', 'date']
    list_display = ['get_student_name', 'total_amount', 'date', 'time', 'transaction_id', 'status', 'payment_mode', 'received_by', 'download_receipt']
    list_filter = ['status', 'payment_mode', 'date']
    raw_id_fields = ['user']
    
    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }
        js = ('admin/js/transaction_admin.js',)

    def get_fields(self, request, obj=None):
        fields = list(super().get_fields(request, obj))
        if obj is None:  # This is an add form
            if 'payment_mode' in fields:
                if 'transaction_id' in fields and request.POST.get('payment_mode') == 'Cash':
                    fields.remove('transaction_id')
            if 'total_amount' in fields:
                fields.remove('total_amount')
        return fields

    def save_model(self, request, obj, form, change):
        if not change:  # New transaction
            obj.received_by = request.user.username
            obj.total_amount = 0
            
            if obj.payment_mode == 'Cash':
                from datetime import datetime
                cash_trans_id = f"CASH-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                obj.transaction_id = cash_trans_id
            elif not obj.transaction_id:
                from datetime import datetime
                obj.transaction_id = f"ONLINE-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Always ensure time is set
        if not obj.time:
            from datetime import datetime
            obj.time = datetime.now().time()
        
        super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        obj = form.instance
        total = sum(category.amount for category in obj.categories.all())
        obj.total_amount = total
        obj.save()

        # Update fee due when transaction is successful
        if obj.status:
            user_profile = UserProfile.objects.filter(user=obj.user).first()
            if user_profile:
                # Calculate new fee due
                new_fee_due = user_profile.Fee_Due - total
                user_profile.Fee_Due = max(0, new_fee_due)  # Ensure fee due doesn't go below 0
                user_profile.save()
                messages.success(
                    request,
                    f"User {user_profile.Name}'s fee has been updated successfully. New fee due: ₹{user_profile.Fee_Due}"
                )

    def download_receipt(self, obj):
        if obj.status:
            return format_html(
                '<a class="button" href="/download_receipt/{transaction_id}/" target="_blank">Download Receipt</a>',
                transaction_id=obj.transaction_id
            )
        return "N/A"
    download_receipt.short_description = 'Receipt'

    def get_student_name(self, obj):
        return obj.user.profile.Name
    get_student_name.short_description = 'Student Name'
    get_student_name.admin_order_field = 'user__profile__Name'

admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Transactions, TransactionsAdmin)
