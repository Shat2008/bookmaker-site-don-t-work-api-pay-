from django.urls import path
from . import views

app_name = 'matches'

urlpatterns = [
    path('', views.match_list, name='match_list'),
    path('sport/<int:sport_id>/', views.match_list_by_sport, name='match_list_by_sport'),
    path('<int:match_id>/', views.match_detail, name='match_detail'),
    path('live/', views.live_matches, name='live_matches'),
    path('api/matches/', views.api_match_list, name='api_match_list'),
]