from django.shortcuts import render, get_object_or_404, redirect
from matches.models import Sport, Match
from bets.models import Bet
from django.contrib.auth.decorators import login_required
from django.utils import timezone

# ... остальные функции ...

def rules(request):
    """Страница правил и условий"""
    context = {
        'title': 'Правила и условия - VIP BET',
        'current_date': timezone.now(),
    }
    return render(request, 'core/rules.html', context)


# ... остальной код

def home(request):
    """Главная страница"""
    sports = Sport.objects.filter(is_active=True)[:8]
    featured_matches = Match.objects.filter(is_active=True, status='upcoming').order_by('start_time')[:10]
    live_matches = Match.objects.filter(is_active=True, status='live').order_by('start_time')[:5]
    
    # Популярные ставки
    popular_bets = []
    if request.user.is_authenticated:
        popular_bets = Bet.objects.all().order_by('-created_at')[:5]
    
    context = {
        'sports': sports,
        'featured_matches': featured_matches,
        'live_matches': live_matches,
        'popular_bets': popular_bets,
        'title': 'Главная - VIP BET',
    }
    return render(request, 'core/home.html', context)

def sport_detail(request, sport_id):
    """Детальная страница вида спорта"""
    sport = get_object_or_404(Sport, id=sport_id, is_active=True)
    matches = Match.objects.filter(sport=sport, is_active=True).order_by('start_time')
    
    context = {
        'sport': sport,
        'matches': matches,
        'title': f'{sport.name} - VIP BET',
    }
    return render(request, 'core/sport_detail.html', context)

def live_matches(request):
    """Live матчи"""
    live_matches = Match.objects.filter(status='live', is_active=True).order_by('start_time')
    upcoming_matches = Match.objects.filter(status='upcoming', is_active=True).order_by('start_time')[:10]
    
    context = {
        'live_matches': live_matches,
        'upcoming_matches': upcoming_matches,
        'title': 'Live ставки - VIP BET',
    }
    return render(request, 'core/live_matches.html', context)

@login_required
def support(request):
    """Техническая поддержка"""
    context = {
        'title': 'Техническая поддержка - VIP BET',
    }
    return render(request, 'core/support.html', context)

def rules(request):
    """Правила сайта"""
    context = {
        'title': 'Правила - VIP BET',
    }
    return render(request, 'core/rules.html', context)