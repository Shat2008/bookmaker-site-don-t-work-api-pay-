from django.shortcuts import render, redirect, get_object_or_404  # ← добавить redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Bet
from .forms import BetForm
from matches.models import Match

@login_required
def place_bet(request, match_id):
    """Размещение ставки"""
    match = get_object_or_404(Match, id=match_id, is_active=True)
    
    if request.method == 'POST':
        form = BetForm(request.POST, match=match, user=request.user)
        if form.is_valid():
            bet = form.save()
            messages.success(
                request, 
                f'Ставка размещена успешно! Потенциальный выигрыш: {bet.potential_win} ₽'
            )
            return redirect('bets:bet_success', bet_id=bet.id)  # ← будет работать
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = BetForm(match=match, user=request.user)
    
    context = {
        'match': match,
        'form': form,
        'title': f'Ставка на {match.team1} vs {match.team2}',
    }
    return render(request, 'bets/place_bet.html', context)

# ... остальной код


@login_required
def bet_success(request, bet_id):
    """Страница успешного размещения ставки"""
    bet = get_object_or_404(Bet, id=bet_id, user=request.user)
    
    context = {
        'bet': bet,
        'title': 'Ставка размещена!',
    }
    return render(request, 'bets/bet_success.html', context)

@login_required
def bet_history(request):
    """История ставок"""
    bets = Bet.objects.filter(user=request.user).order_by('-created_at')
    
    # Статистика
    total_bets = bets.count()
    won_bets = bets.filter(status='won').count()
    lost_bets = bets.filter(status='lost').count()
    pending_bets = bets.filter(status='pending').count()
    
    total_won = sum(bet.result_amount for bet in bets.filter(status='won') if bet.result_amount)
    total_bet = sum(bet.amount for bet in bets)
    
    context = {
        'bets': bets,
        'total_bets': total_bets,
        'won_bets': won_bets,
        'lost_bets': lost_bets,
        'pending_bets': pending_bets,
        'total_won': total_won,
        'total_bet': total_bet,
        'profit': total_won - total_bet,
        'title': 'История ставок',
    }
    return render(request, 'bets/bet_history.html', context)

@login_required
def active_bets(request):
    """Активные ставки"""
    bets = Bet.objects.filter(user=request.user, status='pending').order_by('-created_at')
    
    context = {
        'bets': bets,
        'title': 'Активные ставки',
    }
    return render(request, 'bets/active_bets.html', context)

@login_required
def cancel_bet(request, bet_id):
    """Отмена ставки"""
    bet = get_object_or_404(Bet, id=bet_id, user=request.user)
    
    if bet.can_cancel():
        bet.status = 'cancelled'
        bet.save()
        
        # Возврат средств
        request.user.balance += bet.amount
        request.user.save()
        
        messages.success(request, 'Ставка отменена. Средства возвращены на баланс.')
    else:
        messages.error(request, 'Невозможно отменить эту ставку.')
    
    return redirect('bets:bet_history')

@login_required
def api_place_bet(request):
    """API для размещения ставки (AJAX)"""
    if request.method == 'POST':
        match_id = request.POST.get('match_id')
        bet_type = request.POST.get('bet_type')
        amount = request.POST.get('amount')
        
        try:
            match = Match.objects.get(id=match_id, is_active=True)
            
            # Проверка баланса
            if float(amount) > request.user.balance:
                return JsonResponse({
                    'success': False,
                    'error': 'Недостаточно средств на балансе'
                })
            
            # Создание ставки
            bet = Bet.objects.create(
                user=request.user,
                match=match,
                bet_type=bet_type,
                amount=amount,
                coefficient=getattr(match, f'coefficient_{bet_type}', 1.0)
            )
            
            # Списание средств
            request.user.balance -= bet.amount
            request.user.save()
            
            return JsonResponse({
                'success': True,
                'bet_id': bet.id,
                'potential_win': float(bet.potential_win),
                'new_balance': float(request.user.balance)
            })
            
        except Match.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Матч не найден'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Неверный метод запроса'})
