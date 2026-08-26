from django.shortcuts import render, get_object_or_404, redirect  # ← добавили redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Sport, Match
from bets.forms import BetForm

def match_list(request):
    """Список всех матчей"""
    sports = Sport.objects.filter(is_active=True)
    selected_sport = request.GET.get('sport')
    
    if selected_sport:
        matches = Match.objects.filter(sport_id=selected_sport, is_active=True).order_by('start_time')
    else:
        matches = Match.objects.filter(is_active=True).order_by('start_time')
    
    context = {
        'sports': sports,
        'matches': matches,
        'selected_sport': selected_sport,
        'title': 'Все матчи',
    }
    return render(request, 'matches/match_list.html', context)

def match_list_by_sport(request, sport_id):
    """Матчи по конкретному виду спорта"""
    sport = get_object_or_404(Sport, id=sport_id, is_active=True)
    matches = Match.objects.filter(sport=sport, is_active=True).order_by('start_time')
    
    context = {
        'sport': sport,
        'matches': matches,
        'title': f'Матчи - {sport.name}',
    }
    return render(request, 'matches/match_list_by_sport.html', context)

def match_detail(request, match_id):
    """Детальная информация о матче"""
    match = get_object_or_404(Match, id=match_id, is_active=True)
    
    # Если это простой POST запрос со списка матчей, просто показываем форму
    if request.method == 'POST' and request.user.is_authenticated:
        # Проверяем, есть ли данные формы
        if 'amount' in request.POST:
            # Это реальная отправка ставки
            form = BetForm(request.POST)
            if form.is_valid():
                bet = form.save(commit=False)
                bet.user = request.user
                bet.match = match
                bet.save()
                return redirect('bets:bet_success', bet_id=bet.id)
        else:
            # Это просто переход со списка - показываем форму
            form = BetForm()
    else:
        form = BetForm()
    
    context = {
        'match': match,
        'form': form,
        'title': f'{match.team1} vs {match.team2}',
    }
    return render(request, 'matches/match_detail.html', context)

def live_matches(request):
    """Live матчи"""
    live_matches = Match.objects.filter(status='live', is_active=True).order_by('start_time')
    
    context = {
        'live_matches': live_matches,
        'title': 'Live матчи',
    }
    return render(request, 'matches/live_matches.html', context)

@login_required
def api_match_list(request):
    """API для получения списка матчей (JSON)"""
    sport_id = request.GET.get('sport_id')
    
    if sport_id:
        matches = Match.objects.filter(sport_id=sport_id, is_active=True)
    else:
        matches = Match.objects.filter(is_active=True)
    
    matches_data = []
    for match in matches:
        matches_data.append({
            'id': match.id,
            'team1': match.team1,
            'team2': match.team2,
            'start_time': match.start_time.isoformat(),
            'league': match.league,
            'coefficient_team1': float(match.coefficient_team1),
            'coefficient_team2': float(match.coefficient_team2),
            'coefficient_draw': float(match.coefficient_draw) if match.coefficient_draw else None,
            'status': match.status,
        })
    
    return JsonResponse({'matches': matches_data})