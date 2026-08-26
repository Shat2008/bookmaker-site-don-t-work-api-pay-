from django import forms
from .models import Bet

class BetForm(forms.ModelForm):
    bet_type = forms.ChoiceField(
        choices=Bet.BET_TYPES,
        widget=forms.RadioSelect,
        label='Тип ставки'
    )
    amount = forms.DecimalField(
        max_digits=10, 
        decimal_places=2,
        min_value=10,
        label='Сумма ставки (₽)',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите сумму',
            'step': '10'
        })
    )
    
    class Meta:
        model = Bet
        fields = ['bet_type', 'amount']
    
    def __init__(self, *args, **kwargs):
        self.match = kwargs.pop('match', None)
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.match:
            # Динамически обновляем коэффициенты
            self.fields['bet_type'].choices = [
                ('team1', f'Победа {self.match.team1} ({self.match.coefficient_team1})'),
                ('team2', f'Победа {self.match.team2} ({self.match.coefficient_team2})'),
            ]
            
            if self.match.coefficient_draw:
                self.fields['bet_type'].choices.append(
                    ('draw', f'Ничья ({self.match.coefficient_draw})')
                )
            
            if self.match.total_over:
                self.fields['bet_type'].choices.append(
                    ('total_over', f'Тотал больше ({self.match.total_over})')
                )
            
            if self.match.total_under:
                self.fields['bet_type'].choices.append(
                    ('total_under', f'Тотал меньше ({self.match.total_under})')
                )
    
    def clean_amount(self):
        amount = self.cleaned_data['amount']
        
        if self.user and amount > self.user.balance:
            raise forms.ValidationError('Недостаточно средств на балансе')
        
        if amount < 10:
            raise forms.ValidationError('Минимальная сумма ставки - 10 ₽')
        
        if amount > 100000:
            raise forms.ValidationError('Максимальная сумма ставки - 100,000 ₽')
        
        return amount
    
    def clean(self):
        cleaned_data = super().clean()
        
        if self.match and self.match.status != 'upcoming':
            raise forms.ValidationError('Ставки принимаются только на предстоящие матчи')
        
        if self.match and not self.match.is_active:
            raise forms.ValidationError('Ставки на этот матч не принимаются')
        
        return cleaned_data
    
    def save(self, commit=True):
        bet = super().save(commit=False)
        
        if self.match:
            bet.match = self.match
            bet.user = self.user
            
            # Устанавливаем коэффициент в зависимости от типа ставки
            bet_type = self.cleaned_data['bet_type']
            if bet_type == 'team1':
                bet.coefficient = self.match.coefficient_team1
            elif bet_type == 'team2':
                bet.coefficient = self.match.coefficient_team2
            elif bet_type == 'draw':
                bet.coefficient = self.match.coefficient_draw
            elif bet_type == 'total_over':
                bet.coefficient = self.match.total_over
            elif bet_type == 'total_under':
                bet.coefficient = self.match.total_under
        
        if commit:
            # Списание средств с баланса пользователя
            if self.user:
                self.user.balance -= bet.amount
                self.user.save()
            
            bet.save()
        
        return bet