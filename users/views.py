from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from .forms import CustomUserCreationForm, CustomUserChangeForm, LoginForm
from .models import CustomUser
from bets.models import Bet

def register(request):
    """Регистрация нового пользователя"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)  # Не сохраняем сразу
            
            # Устанавливаем баланс ДО сохранения
            user.balance = 100.00
            
            # Теперь сохраняем
            user.save()
            
            # Обязательно сохраняем ManyToMany связи
            form.save_m2m()
            
            messages.success(
                request, 
                f'Регистрация успешна! Добро пожаловать, {user.username}! '
                f'Вам начислен приветственный бонус 100 рублей. '
                f'Теперь войдите в свой аккаунт.'
            )
            # Перенаправляем на страницу входа
            return redirect('users:login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = CustomUserCreationForm()
    
    context = {
        'form': form,
        'title': 'Регистрация - VIP BET',
    }
    return render(request, 'users/register.html', context)

def user_login(request):
    """Вход пользователя"""
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Добро пожаловать, {username}!')
                return redirect('core:home')
            else:
                messages.error(request, 'Неверное имя пользователя или пароль.')
    else:
        form = LoginForm()
    
    context = {
        'form': form,
        'title': 'Вход - VIP BET',
    }
    return render(request, 'users/login.html', context)

@login_required
def profile(request):
    """Профиль пользователя"""
    user_bets = Bet.objects.filter(user=request.user).order_by('-created_at')[:10]
    total_bets = Bet.objects.filter(user=request.user).count()
    won_bets = Bet.objects.filter(user=request.user, status='won').count()
    
    win_rate = 0
    if total_bets > 0:
        win_rate = (won_bets / total_bets * 100)
    
    context = {
        'user': request.user,
        'user_bets': user_bets,
        'total_bets': total_bets,
        'won_bets': won_bets,
        'win_rate': win_rate,
        'title': 'Мой профиль',
    }
    return render(request, 'users/profile.html', context)

@login_required
def edit_profile(request):
    """Редактирование профиля"""
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлен!')
            return redirect('users:profile')
    else:
        form = CustomUserChangeForm(instance=request.user)
    
    context = {
        'form': form,
        'title': 'Редактирование профиля',
    }
    return render(request, 'users/edit_profile.html', context)

@login_required
@login_required
def user_bets(request):
    """История ставок пользователя"""
    bets = Bet.objects.filter(user=request.user).order_by('-created_at')
    
    # Статистика
    total_bets = bets.count()
    won_bets = bets.filter(status='won').count()
    lost_bets = bets.filter(status='lost').count()
    pending_bets = bets.filter(status='pending').count()
    
    context = {
        'bets': bets,
        'total_bets': total_bets,
        'won_bets': won_bets,
        'lost_bets': lost_bets,
        'pending_bets': pending_bets,
        'title': 'Мои ставки',
    }
    return render(request, 'users/bets_history.html', context)

@login_required
def balance(request):
    """Управление балансом"""
    context = {
        'title': 'Мой баланс',
    }
    return render(request, 'users/balance.html', context)

@require_POST
def logout_view(request):
    logout(request)
    return redirect('core:home')