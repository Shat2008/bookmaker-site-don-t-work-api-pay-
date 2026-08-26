from django import forms
from .models import Transaction

class StripeDepositForm(forms.Form):
    """Форма для пополнения счета через Stripe"""
    
    amount = forms.DecimalField(
        min_value=1,
        max_value=999999,
        label='Сумма пополнения (USD)',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите сумму',
            'step': '0.01',
            'id': 'id_amount'
        })
    )
    
    email = forms.EmailField(
        required=False,
        label='Email для квитанции',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'your@email.com'
        })
    )

class DepositForm(forms.Form):
    PAYMENT_CHOICES = [
        ('stripe', '💳 Stripe (Карта)'),
        ('qiwi', '🥝 QIWI кошелек'),
        ('yoomoney', '💎 ЮMoney'),
        ('webmoney', 'W WebMoney'),
        ('crypto', '₿ Криптовалюта'),
    ]
    
    amount = forms.DecimalField(
        min_value=100,
        max_value=100000,
        label='Сумма пополнения (₽)',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите сумму от 100 до 100,000 ₽',
            'step': '10'
        })
    )
    
    payment_method = forms.ChoiceField(
        choices=PAYMENT_CHOICES,
        label='Способ оплаты',
        widget=forms.RadioSelect
    )
    
    card_number = forms.CharField(
        required=False,
        max_length=19,
        label='Номер карты',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '0000 0000 0000 0000',
            'data-mask': '0000 0000 0000 0000'
        })
    )
    
    phone = forms.CharField(
        required=False,
        max_length=20,
        label='Номер телефона',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+7 (999) 999-99-99',
            'data-mask': '+7 (999) 999-99-99'
        })
    )
    
    wallet = forms.CharField(
        required=False,
        max_length=100,
        label='Номер кошелька',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите номер кошелька'
        })
    )
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    
    def clean(self):
        cleaned_data = super().clean()
        payment_method = cleaned_data.get('payment_method')
        
        # Валидация в зависимости от способа оплаты
        if payment_method == 'card' and not cleaned_data.get('card_number'):
            self.add_error('card_number', 'Введите номер карты')
        elif payment_method == 'qiwi' and not cleaned_data.get('phone'):
            self.add_error('phone', 'Введите номер телефона QIWI')
        elif payment_method in ['yoomoney', 'webmoney'] and not cleaned_data.get('wallet'):
            self.add_error('wallet', 'Введите номер кошелька')
        
        return cleaned_data

class WithdrawalForm(forms.Form):
    PAYMENT_CHOICES = [
        ('card', '💳 На банковскую карту'),
        ('qiwi', '🥝 На QIWI кошелек'),
        ('yoomoney', '💎 На ЮMoney'),
    ]
    
    amount = forms.DecimalField(
        min_value=100,
        max_value=50000,
        label='Сумма вывода (₽)',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите сумму от 100 до 50,000 ₽',
            'step': '10'
        })
    )
    
    payment_method = forms.ChoiceField(
        choices=PAYMENT_CHOICES,
        label='Способ вывода',
        widget=forms.RadioSelect
    )
    
    card_number = forms.CharField(
        required=False,
        max_length=19,
        label='Номер карты',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '0000 0000 0000 0000',
            'data-mask': '0000 0000 0000 0000'
        })
    )
    
    phone = forms.CharField(
        required=False,
        max_length=20,
        label='Номер телефона',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+7 (999) 999-99-99',
            'data-mask': '+7 (999) 999-99-99'
        })
    )
    
    wallet = forms.CharField(
        required=False,
        max_length=100,
        label='Номер кошелька',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите номер кошелька'
        })
    )
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    
    def clean_amount(self):
        amount = self.cleaned_data['amount']
        
        if self.user and amount > self.user.balance:
            raise forms.ValidationError('Недостаточно средств на балансе')
        
        return amount
    
    def clean(self):
        cleaned_data = super().clean()
        payment_method = cleaned_data.get('payment_method')
        
        # Валидация в зависимости от способа вывода
        if payment_method == 'card' and not cleaned_data.get('card_number'):
            self.add_error('card_number', 'Введите номер карты')
        elif payment_method == 'qiwi' and not cleaned_data.get('phone'):
            self.add_error('phone', 'Введите номер телефона QIWI')
        elif payment_method == 'yoomoney' and not cleaned_data.get('wallet'):
            self.add_error('wallet', 'Введите номер кошелька ЮMoney')
        
        return cleaned_data
