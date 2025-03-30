from django import forms
from .models import FeeTransaction, FeeItem, FeeCategory

class FeeTransactionForm(forms.ModelForm):
    class Meta:
        model = FeeTransaction
        fields = ['payment_mode']

class FeeItemForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        categories = FeeCategory.objects.filter(is_active=True)
        
        for category in categories:
            self.fields[f'category_{category.id}'] = forms.BooleanField(
                required=False,
                label=category.name
            )
            self.fields[f'amount_{category.id}'] = forms.DecimalField(
                required=False,
                min_value=0,
                decimal_places=2
            )
        
        # Add Other Fee field
        self.fields['other_fee_description'] = forms.CharField(
            required=False,
            widget=forms.TextInput(attrs={'placeholder': 'Other Fee Description'})
        )
        self.fields['other_fee_amount'] = forms.DecimalField(
            required=False,
            min_value=0,
            decimal_places=2
        ) 