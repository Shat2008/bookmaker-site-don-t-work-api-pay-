from django.urls import path
from . import views

app_name = 'bets'

urlpatterns = [
    path('place/<int:match_id>/', views.place_bet, name='place_bet'),
    path('success/<int:bet_id>/', views.bet_success, name='bet_success'),
    path('history/', views.bet_history, name='bet_history'),
    path('active/', views.active_bets, name='active_bets'),
    path('cancel/<int:bet_id>/', views.cancel_bet, name='cancel_bet'),
    path('api/place/', views.api_place_bet, name='api_place_bet'),
]